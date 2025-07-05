from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import base64


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # Campos computados para mostrar información
    almus_apps_summary = fields.Html(
        string='Resumen de Aplicaciones',
        compute='_compute_almus_apps_summary',
        readonly=True
    )
    
    almus_total_apps = fields.Integer(
        string='Total de Aplicaciones',
        compute='_compute_almus_stats',
        readonly=True
    )
    
    almus_enabled_apps = fields.Integer(
        string='Aplicaciones Habilitadas',
        compute='_compute_almus_stats',
        readonly=True
    )
    
    def _compute_almus_apps_summary(self):
        """Generar resumen HTML de aplicaciones con controles"""
        for settings in self:
            apps = self.env['almus.app.config'].search([('active', '=', True)])
            
            if not apps:
                settings.almus_apps_summary = '<p class="text-muted">No hay aplicaciones Almus configuradas.</p>'
                continue
            
            html_parts = ['<div class="almus-apps-config">']
            
            # Agrupar por categoría
            categories = {}
            for app in apps:
                if app.category not in categories:
                    categories[app.category] = []
                categories[app.category].append(app)
            
            for category, cat_apps in categories.items():
                cat_name = dict(apps._fields['category'].selection).get(category, category)
                html_parts.append(f'<div class="mt-4">')
                html_parts.append(f'<h5>{cat_name}</h5>')
                
                for app in sorted(cat_apps, key=lambda a: a.sequence):
                    app_id = app.id
                    checked = 'checked' if app.is_enabled else ''
                    disabled = '' if app.can_disable or not app.is_enabled else 'disabled'
                    
                    html_parts.append(f'''
                        <div class="o_setting_box mb-2">
                            <div class="o_setting_left_pane">
                                <div class="form-check">
                                    <input type="checkbox" 
                                           class="form-check-input almus-app-toggle" 
                                           id="almus_app_{app_id}"
                                           data-app-id="{app_id}"
                                           {checked} {disabled}/>
                                </div>
                            </div>
                            <div class="o_setting_right_pane">
                                <label for="almus_app_{app_id}" class="o_form_label">
                                    {app.display_name}
                                </label>
                                <div class="text-muted small">{app.description or ''}</div>
                            </div>
                        </div>
                    ''')
                
                html_parts.append('</div>')
            
            html_parts.append('</div>')
            
            # JavaScript para manejar los cambios
            html_parts.append('''
                <script>
                    $(document).ready(function() {
                        $('.almus-app-toggle').on('change', function() {
                            var $checkbox = $(this);
                            var appId = $checkbox.data('app-id');
                            var isEnabled = $checkbox.is(':checked');
                            
                            // Llamar al método Python para cambiar el estado
                            self._rpc({
                                model: 'almus.app.config',
                                method: isEnabled ? 'action_enable' : 'action_disable',
                                args: [[appId]],
                            }).then(function(result) {
                                // Recargar la vista si es necesario
                                if (result && result.type === 'ir.actions.client') {
                                    self.do_action(result);
                                }
                            }).catch(function(error) {
                                // Revertir el cambio si hay error
                                $checkbox.prop('checked', !isEnabled);
                            });
                        });
                    });
                </script>
            ''')
            
            settings.almus_apps_summary = ''.join(html_parts)
    
    def _compute_almus_stats(self):
        """Calcular estadísticas de aplicaciones"""
        for settings in self:
            apps = self.env['almus.app.config'].search([('active', '=', True)])
            settings.almus_total_apps = len(apps)
            settings.almus_enabled_apps = len(apps.filtered('is_enabled'))
    
    def action_open_almus_apps(self):
        """Abrir vista simple de aplicaciones Almus"""
        # Crear una vista tree simple si no existe
        tree_view = self.env.ref('almus_base.view_almus_app_config_simple_tree', raise_if_not_found=False)
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Aplicaciones Almus'),
            'res_model': 'almus.app.config',
            'view_mode': 'tree',
            'view_id': tree_view.id if tree_view else False,
            'target': 'new',
            'context': {
                'search_default_active': 1,
                'create': False,
                'delete': False,
            }
        }
    
    def action_export_almus_config(self):
        """Exportar configuración actual de aplicaciones Almus"""
        self.ensure_one()
        
        apps = self.env['almus.app.config'].search([('active', '=', True)])
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
    
    def action_toggle_almus_app(self, app_id, enable):
        """Método auxiliar para cambiar estado de aplicación desde la vista"""
        app = self.env['almus.app.config'].browse(app_id)
        if app.exists():
            if enable:
                return app.action_enable()
            else:
                return app.action_disable()
        return False