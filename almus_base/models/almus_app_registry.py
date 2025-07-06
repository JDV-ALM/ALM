from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class AlmusAppRegistry(models.Model):
    """Registro persistente de aplicaciones Almus instaladas"""
    _name = 'almus.app.registry'
    _description = 'Registro de Aplicaciones Almus'
    _order = 'sequence, name'
    _rec_name = 'display_name'
    
    name = fields.Char(
        string='Nombre Técnico',
        required=True,
        index=True,
        readonly=True,
    )
    
    display_name = fields.Char(
        string='Nombre',
        required=True,
        readonly=True,
    )
    
    module_id = fields.Many2one(
        'ir.module.module',
        string='Módulo',
        required=True,
        readonly=True,
        ondelete='cascade',
    )
    
    state = fields.Selection(
        related='module_id.state',
        string='Estado',
        readonly=True,
    )
    
    author = fields.Char(
        related='module_id.author',
        string='Autor',
        readonly=True,
    )
    
    summary = fields.Char(
        related='module_id.summary',
        string='Resumen',
        readonly=True,
    )
    
    installed_version = fields.Char(
        related='module_id.installed_version',
        string='Versión',
        readonly=True,
    )
    
    sequence = fields.Integer(
        string='Secuencia',
        default=10,
    )
    
    active = fields.Boolean(
        string='Activo',
        default=True,
    )
    
    @api.model
    def sync_almus_apps(self):
        """Sincronizar el registro con los módulos Almus instalados"""
        # Buscar módulos Almus
        domain = [
            '|', '|',
            ('name', '=like', 'almus_%'),
            ('name', '=like', 'l10n_ve_almus_%'),
            ('author', 'ilike', 'Almus Dev')
        ]
        
        almus_modules = self.env['ir.module.module'].search(domain)
        
        # Excluir almus_base del registro
        almus_modules = almus_modules.filtered(lambda m: m.name != 'almus_base')
        
        # Actualizar o crear registros
        for module in almus_modules:
            existing = self.search([('module_id', '=', module.id)], limit=1)
            
            if not existing and module.state in ['installed', 'to upgrade']:
                # Crear nuevo registro
                self.create({
                    'name': module.name,
                    'display_name': module.shortdesc or module.name,
                    'module_id': module.id,
                })
                _logger.info('Registrada nueva app Almus: %s', module.name)
            
            elif existing and module.state == 'uninstalled':
                # Desactivar si se desinstaló
                existing.active = False
                _logger.info('Desactivada app Almus: %s', module.name)
        
        # Limpiar registros huérfanos
        orphan_apps = self.search([('module_id', '=', False)])
        if orphan_apps:
            orphan_apps.unlink()
            
        return True
    
    @api.model
    def get_installed_count(self):
        """Obtener cantidad de apps instaladas"""
        return self.search_count([
            ('active', '=', True),
            ('state', '=', 'installed')
        ])
    
    @api.model
    def get_installed_list(self):
        """Obtener lista formateada de apps instaladas"""
        apps = self.search([
            ('active', '=', True),
            ('state', '=', 'installed')
        ], order='display_name')
        
        if apps:
            app_list = []
            for app in apps:
                version = f" (v{app.installed_version})" if app.installed_version else ""
                app_list.append(f"• {app.display_name}{version}")
            return '\n'.join(app_list)
        else:
            return _('No hay aplicaciones Almus instaladas')
    
    def action_refresh_registry(self):
        """Acción manual para refrescar el registro"""
        self.sync_almus_apps()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Registro Actualizado'),
                'message': _('El registro de aplicaciones Almus ha sido actualizado.'),
                'type': 'success',
                'sticky': False,
            }
        }