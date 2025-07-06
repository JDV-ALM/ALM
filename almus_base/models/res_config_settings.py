from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # Campos computados para estadísticas
    almus_installed_apps = fields.Integer(
        string='Aplicaciones Almus Instaladas',
        compute='_compute_almus_stats',
        help='Número total de módulos Almus instalados'
    )
    
    almus_app_list = fields.Text(
        string='Lista de Aplicaciones',
        compute='_compute_almus_stats',
        help='Lista de aplicaciones Almus instaladas'
    )
    
    @api.depends('company_id')  # Trigger recompute when form loads
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
            
            # Crear lista formateada de aplicaciones
            if almus_modules:
                app_names = []
                for module in almus_modules.sorted('name'):
                    # Formatear nombre para mostrar
                    display_name = module.shortdesc or module.name
                    app_names.append(f"• {display_name}")
                
                settings.almus_app_list = '\n'.join(app_names)
            else:
                settings.almus_app_list = _('No hay aplicaciones Almus instaladas')