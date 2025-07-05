from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import base64


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # Campos computados para estadísticas
    almus_total_apps = fields.Integer(
        string='Total de Aplicaciones',
        compute='_compute_almus_stats',
    )
    
    almus_enabled_apps = fields.Integer(
        string='Aplicaciones Habilitadas',
        compute='_compute_almus_stats',
    )
    
    def _compute_almus_stats(self):
        """Calcular estadísticas de aplicaciones"""
        for settings in self:
            current_company = self.env.company
            apps = self.env['almus.app.config'].search([
                ('active', '=', True),
                '|',
                ('company_ids', '=', False),
                ('company_ids', 'in', [current_company.id])
            ])
            settings.almus_total_apps = len(apps)
            settings.almus_enabled_apps = len(apps.filtered('is_enabled'))
    
    def action_almus_manage_apps(self):
        """Abrir vista de gestión de aplicaciones Almus"""
        action = self.env.ref('almus_base.action_almus_app_config_simple').read()[0]
        return action
    
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
        
        current_company = self.env.company
        apps = self.env['almus.app.config'].search([
            ('active', '=', True),
            '|',
            ('company_ids', '=', False),
            ('company_ids', 'in', [current_company.id])
        ])
        
        config_data = {
            'company': current_company.name,
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