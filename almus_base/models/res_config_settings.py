from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import base64


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # Campo relacional para apps
    almus_app_ids = fields.Many2many(
        'almus.app.config',
        string='Aplicaciones Almus',
        compute='_compute_almus_app_ids',
    )
    
    # Campos computados para estadísticas
    almus_total_apps = fields.Integer(
        string='Total de Aplicaciones',
        compute='_compute_almus_stats',
    )
    
    almus_enabled_apps = fields.Integer(
        string='Aplicaciones Habilitadas',
        compute='_compute_almus_stats',
    )
    
    @api.depends('company_id')
    def _compute_almus_app_ids(self):
        """Obtener todas las aplicaciones Almus"""
        for settings in self:
            apps = self.env['almus.app.config'].search([
                ('active', '=', True),
                '|',
                ('company_ids', '=', False),
                ('company_ids', 'in', [settings.company_id.id] if settings.company_id else [])
            ])
            settings.almus_app_ids = apps
    
    @api.depends('almus_app_ids', 'almus_app_ids.is_enabled')
    def _compute_almus_stats(self):
        """Calcular estadísticas de aplicaciones"""
        for settings in self:
            settings.almus_total_apps = len(settings.almus_app_ids)
            settings.almus_enabled_apps = len(settings.almus_app_ids.filtered('is_enabled'))
    
    def action_toggle_app(self):
        """Activar/desactivar una aplicación Almus"""
        self.ensure_one()
        app_id = self._context.get('app_id')
        enable = self._context.get('enable', False)
        
        if not app_id:
            return
            
        app = self.env['almus.app.config'].browse(app_id)
        if app.exists():
            if enable:
                app.action_enable()
            else:
                app.action_disable()
        
        # Recargar la vista
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
    
    def action_almus_refresh_apps(self):
        """Refrescar la lista de aplicaciones Almus"""
        # Detectar nuevos módulos Almus instalados
        self.env['ir.module.module'].sudo()._update_almus_dependencies()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
    
    def action_export_almus_config(self):
        """Exportar configuración actual de aplicaciones Almus"""
        self.ensure_one()
        
        apps = self.almus_app_ids
        
        config_data = {
            'company': self.env.company.name,
            'date': fields.Datetime.now().isoformat(),
            'user': self.env.user.name,
            'apps': []
        }
        
        for app in apps:
            config_data['apps'].append({
                'name': app.name,
                'display_name': app.display_name,
                'enabled': app.is_enabled,
                'module': app.module_id.name,
                'category': app.category,
                'description': app.description or '',
            })
        
        # Crear adjunto con la configuración
        json_data = json.dumps(config_data, indent=2, ensure_ascii=False)
        attachment = self.env['ir.attachment'].create({
            'name': f'almus_config_{fields.Date.today()}.json',
            'type': 'binary',
            'datas': base64.b64encode(json_data.encode('utf-8')),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/json',
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }