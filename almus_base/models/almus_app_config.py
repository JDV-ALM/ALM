from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class AlmusAppConfig(models.Model):
    _name = 'almus.app.config'
    _description = 'Configuración de Aplicaciones Almus'
    _order = 'sequence, name'
    _rec_name = 'display_name'

    name = fields.Char(
        string='Nombre Técnico',
        required=True,
        index=True,
        help='Nombre técnico único de la aplicación'
    )
    display_name = fields.Char(
        string='Nombre',
        required=True,
        translate=True,
        help='Nombre visible de la aplicación'
    )
    module_id = fields.Many2one(
        'ir.module.module',
        string='Módulo',
        required=True,
        ondelete='cascade',
        domain=[('state', '=', 'installed')]
    )
    description = fields.Text(
        string='Descripción',
        translate=True,
        help='Descripción detallada de la funcionalidad'
    )
    category = fields.Selection([
        ('accounting', 'Contabilidad'),
        ('sales', 'Ventas'),
        ('purchase', 'Compras'),
        ('inventory', 'Inventario'),
        ('hr', 'RRHH'),
        ('project', 'Proyectos'),
        ('manufacturing', 'Manufactura'),
        ('website', 'Sitio Web'),
        ('tools', 'Herramientas'),
        ('other', 'Otros'),
    ], string='Categoría', default='other', required=True)
    
    sequence = fields.Integer(
        string='Secuencia',
        default=10,
        help='Orden de aparición en la configuración'
    )
    
    # Estado y activación
    active = fields.Boolean(
        string='Activo',
        default=True,
        help='Si está activo, aparece en la configuración'
    )
    is_enabled = fields.Boolean(
        string='Habilitado',
        default=False,
        help='Si está habilitado, la funcionalidad está activa'
    )
    
    # Dependencias
    depends_on = fields.Many2many(
        'almus.app.config',
        'almus_app_dependency_rel',
        'app_id',
        'depends_id',
        string='Depende de',
        help='Aplicaciones que deben estar habilitadas para activar esta'
    )
    required_by = fields.Many2many(
        'almus.app.config',
        'almus_app_dependency_rel',
        'depends_id',
        'app_id',
        string='Requerido por',
        help='Aplicaciones que dependen de esta'
    )
    
    # Configuración adicional
    config_action_id = fields.Many2one(
        'ir.actions.act_window',
        string='Acción de Configuración',
        help='Acción a ejecutar para configuración adicional'
    )
    
    # Información de la empresa
    company_ids = fields.Many2many(
        'res.company',
        string='Compañías',
        help='Compañías donde está habilitada. Vacío = todas'
    )
    
    # Metadata
    icon = fields.Char(
        string='Icono',
        default='fa-cog',
        help='Icono FontAwesome para la aplicación'
    )
    color = fields.Integer(
        string='Color',
        default=1,
        help='Color para la tarjeta de la aplicación'
    )
    
    # Campos computados
    enabled_count = fields.Integer(
        string='Habilitado en',
        compute='_compute_enabled_count',
        help='Número de compañías donde está habilitado'
    )
    can_disable = fields.Boolean(
        string='Puede Deshabilitarse',
        compute='_compute_can_disable',
        help='Indica si la aplicación puede ser deshabilitada'
    )
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'El nombre técnico debe ser único!'),
    ]
    
    @api.depends('company_ids', 'is_enabled')
    def _compute_enabled_count(self):
        for app in self:
            if app.company_ids:
                app.enabled_count = len(app.company_ids)
            elif app.is_enabled:
                app.enabled_count = self.env['res.company'].sudo().search_count([])
            else:
                app.enabled_count = 0
    
    @api.depends('required_by', 'required_by.is_enabled')
    def _compute_can_disable(self):
        for app in self:
            # No se puede deshabilitar si otras apps habilitadas dependen de esta
            enabled_deps = app.required_by.filtered('is_enabled')
            app.can_disable = not bool(enabled_deps)
    
    @api.constrains('is_enabled', 'depends_on')
    def _check_dependencies(self):
        for app in self.filtered('is_enabled'):
            disabled_deps = app.depends_on.filtered(lambda d: not d.is_enabled)
            if disabled_deps:
                raise ValidationError(_(
                    'No se puede habilitar "%s" porque depende de: %s'
                ) % (app.display_name, ', '.join(disabled_deps.mapped('display_name'))))
    
    def action_enable(self):
        """Habilitar la aplicación"""
        self.ensure_one()
        if self.is_enabled:
            return {'type': 'ir.actions.act_window_close'}
        
        # Verificar dependencias
        self._check_dependencies()
        
        # Habilitar
        self.is_enabled = True
        
        # Registrar en el log
        self._create_config_log('enable')
        
        # Ejecutar acciones post-habilitación
        self._post_enable_actions()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Aplicación Habilitada'),
                'message': _('%s ha sido habilitada correctamente.') % self.display_name,
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_disable(self):
        """Deshabilitar la aplicación"""
        self.ensure_one()
        if not self.is_enabled:
            return {'type': 'ir.actions.act_window_close'}
        
        if not self.can_disable:
            raise UserError(_(
                'No se puede deshabilitar "%s" porque otras aplicaciones dependen de ella.'
            ) % self.display_name)
        
        # Deshabilitar
        self.is_enabled = False
        
        # Registrar en el log
        self._create_config_log('disable')
        
        # Ejecutar acciones post-deshabilitación
        self._post_disable_actions()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Aplicación Deshabilitada'),
                'message': _('%s ha sido deshabilitada.') % self.display_name,
                'type': 'info',
                'sticky': False,
            }
        }
    
    def action_configure(self):
        """Abrir configuración adicional de la aplicación"""
        self.ensure_one()
        if not self.config_action_id:
            raise UserError(_('No hay configuración adicional disponible para %s') % self.display_name)
        
        action = self.config_action_id.sudo().read()[0]
        return action
    
    def _create_config_log(self, action):
        """Crear registro en el log de configuración"""
        self.env['almus.config.log'].create({
            'app_config_id': self.id,
            'action': action,
            'user_id': self.env.user.id,
            'date': fields.Datetime.now(),
            'company_id': self.env.company.id,
        })
    
    def _post_enable_actions(self):
        """Acciones a ejecutar después de habilitar la aplicación"""
        # Este método puede ser sobrescrito por cada aplicación
        _logger.info('Aplicación %s habilitada por %s', self.name, self.env.user.name)
    
    def _post_disable_actions(self):
        """Acciones a ejecutar después de deshabilitar la aplicación"""
        # Este método puede ser sobrescrito por cada aplicación
        _logger.info('Aplicación %s deshabilitada por %s', self.name, self.env.user.name)
    
    @api.model
    def get_enabled_apps(self, company_id=None):
        """Obtener lista de aplicaciones habilitadas para una compañía"""
        domain = [('is_enabled', '=', True)]
        if company_id:
            domain.append('|')
            domain.append(('company_ids', '=', False))
            domain.append(('company_ids', 'in', [company_id]))
        
        return self.search(domain)
    
    def name_get(self):
        """Mostrar nombre y estado"""
        result = []
        for app in self:
            name = app.display_name
            if app.is_enabled:
                name = f"✓ {name}"
            result.append((app.id, name))
        return result