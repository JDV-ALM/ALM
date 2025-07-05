from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import base64
from datetime import datetime


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    almus_apps_summary = fields.Html(
        string='Resumen de Aplicaciones',
        compute='_compute_almus_apps_summary'
    )
    
    almus_total_apps = fields.Integer(
        string='Total de Aplicaciones',
        compute='_compute_almus_stats'
    )
    almus_enabled_apps = fields.Integer(
        string='Aplicaciones Habilitadas',
        compute='_compute_almus_stats'
    )
    
    def _compute_almus_apps_summary(self):
        """Generar resumen HTML de aplicaciones"""
        for settings in self:
            apps = self.env['almus.app.config'].search([('active', '=', True)])
            
            html_parts = ['<div class="almus-apps-summary">']
            
            # Agrupar por categoría
            categories = {}
            for app in apps:
                if app.category not in categories:
                    categories[app.category] = []
                categories[app.category].append(app)
            
            for category, cat_apps in categories.items():
                cat_name = dict(apps._fields['category'].selection).get(category, category)
                html_parts.append(f'<h5 class="mt-3">{cat_name}</h5>')
                html_parts.append('<ul class="list-unstyled">')
                
                for app in sorted(cat_apps, key=lambda a: a.sequence):
                    status_icon = '✓' if app.is_enabled else '○'
                    status_class = 'text-success' if app.is_enabled else 'text-muted'
                    
                    html_parts.append(
                        f'<li><span class="{status_class}">{status_icon}</span> '
                        f'{app.display_name}</li>'
                    )
                
                html_parts.append('</ul>')
            
            html_parts.append('</div>')
            settings.almus_apps_summary = ''.join(html_parts)
    
    def _compute_almus_stats(self):
        """Calcular estadísticas de aplicaciones"""
        for settings in self:
            apps = self.env['almus.app.config'].search([('active', '=', True)])
            settings.almus_total_apps = len(apps)
            settings.almus_enabled_apps = len(apps.filtered('is_enabled'))
    
    def action_open_almus_apps(self):
        """Abrir vista de aplicaciones Almus"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Aplicaciones Almus'),
            'res_model': 'almus.app.config',
            'view_mode': 'tree,form',
            'target': 'current',
            'context': {'search_default_active': 1}
        }
    
    @api.model
    def get_values(self):
        """Obtener valores de configuración incluyendo apps Almus"""
        res = super(ResConfigSettings, self).get_values()
        
        # Obtener estado de cada aplicación
        apps = self.env['almus.app.config'].search([('active', '=', True)])
        for app in apps:
            field_name = f'almus_app_{app.name}'
            res[field_name] = app.is_enabled
            
        return res
    
    def set_values(self):
        """Guardar valores de configuración incluyendo apps Almus"""
        super(ResConfigSettings, self).set_values()
        
        # Procesar cambios en aplicaciones
        apps = self.env['almus.app.config'].search([('active', '=', True)])
        for app in apps:
            field_name = f'almus_app_{app.name}'
            if hasattr(self, field_name):
                new_value = getattr(self, field_name)
                if new_value != app.is_enabled:
                    if new_value:
                        app.action_enable()
                    else:
                        app.action_disable()
    
    @api.model
    def _register_almus_app_fields(self):
        """Registrar dinámicamente campos para cada aplicación Almus"""
        apps = self.env['almus.app.config'].search([('active', '=', True)])
        
        for app in apps:
            field_name = f'almus_app_{app.name}'
            
            # Solo crear el campo si no existe
            if not hasattr(self.__class__, field_name):
                # Crear campo Boolean dinámicamente
                field = fields.Boolean(
                    string=app.display_name,
                    help=app.description or f'Habilitar/Deshabilitar {app.display_name}',
                    default=False
                )
                
                # Añadir el campo a la clase
                setattr(self.__class__, field_name, field)
                
                # Registrar el campo en _fields
                self._add_field(field_name, field)
    
    def _add_field(self, name, field):
        """Método auxiliar para añadir campo al modelo"""
        # Establecer el modelo y nombre del campo
        field.model_name = self._name
        field.name = name
        
        # Añadir a _fields si no existe
        if name not in self._fields:
            self._fields[name] = field
            
            # Setup del campo
            field.setup_base(self, name)
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """Modificar la vista para incluir campos dinámicos de apps Almus"""
        res = super(ResConfigSettings, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        
        if view_type == 'form':
            # Registrar campos dinámicos
            self._register_almus_app_fields()
            
            # TODO: Aquí se podría modificar el XML de la vista para incluir
            # los campos dinámicos en la ubicación correcta
            
        return res
    
    def action_export_almus_config(self):
        """Exportar configuración actual de aplicaciones Almus"""
        self.ensure_one()
        
        apps = self.env['almus.app.config'].search([('active', '=', True)])
        config_data = {
            'company': self.env.company.name,
            'date': fields.Datetime.now().isoformat(),
            'apps': {}
        }
        
        for app in apps:
            config_data['apps'][app.name] = {
                'display_name': app.display_name,
                'enabled': app.is_enabled,
                'module': app.module_id.name,
                'category': app.category,
            }
        
        # Crear adjunto con la configuración
        attachment = self.env['ir.attachment'].create({
            'name': f'almus_config_{fields.Date.today()}.json',
            'type': 'binary',
            'datas': base64.b64encode(json.dumps(config_data, indent=2).encode()),
            'res_model': self._name,
            'res_id': self.id,
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }