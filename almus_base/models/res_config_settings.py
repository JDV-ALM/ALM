from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # Campos computados para estadísticas
    almus_installed_apps = fields.Integer(
        string='Aplicaciones Almus Instaladas',
        compute='_compute_almus_stats',
        help='Número total de módulos Almus instalados'
    )
    
    almus_app_list = fields.Html(
        string='Lista de Aplicaciones',
        compute='_compute_almus_stats',
        sanitize=False,
        help='Lista de aplicaciones Almus instaladas'
    )
    
    def _compute_almus_stats(self):
        """Calcular estadísticas de aplicaciones Almus instaladas"""
        for settings in self:
            # Buscar módulos instalados con prefijo almus_ o autor Almus Dev
            domain = [
                ('state', '=', 'installed'),
                '|', '|',
                ('name', '=like', 'almus_%'),
                ('name', '=like', 'l10n_ve_almus_%'),
                ('author', 'ilike', 'Almus Dev')
            ]
            
            # Excluir almus_base del conteo
            domain.append(('name', '!=', 'almus_base'))
            
            almus_modules = self.env['ir.module.module'].search(domain)
            
            settings.almus_installed_apps = len(almus_modules)
            
            # Crear lista HTML de aplicaciones
            if almus_modules:
                app_html = '<div class="row">'
                for module in almus_modules.sorted('name'):
                    # Formatear nombre para mostrar
                    display_name = module.shortdesc or module.name
                    version = module.installed_version or '1.0.0'
                    icon = module.icon or '/base/static/description/icon.png'
                    
                    app_html += f'''
                    <div class="col-md-6 mb-3">
                        <div class="d-flex align-items-center">
                            <img src="{icon}" alt="{display_name}" 
                                 style="width: 32px; height: 32px; margin-right: 12px;"
                                 onerror="this.src='/base/static/description/icon.png'"/>
                            <div>
                                <strong>{display_name}</strong>
                                <span class="text-muted ms-2">v{version}</span>
                            </div>
                        </div>
                    </div>
                    '''
                app_html += '</div>'
                settings.almus_app_list = app_html
            else:
                settings.almus_app_list = '<p class="text-muted">No hay aplicaciones Almus instaladas actualmente.</p>'