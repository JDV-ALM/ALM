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
    
    def _compute_almus_stats(self):
        """Calcular estadísticas de aplicaciones Almus instaladas"""
        AlmusRegistry = self.env['almus.app.registry']
        
        for settings in self:
            # Siempre usar el registro persistente
            settings.almus_installed_apps = AlmusRegistry.get_installed_count()
            settings.almus_app_list = AlmusRegistry.get_installed_list()
    
    def action_refresh_almus_apps(self):
        """Refrescar manualmente el registro de apps Almus"""
        # Sincronizar el registro
        self.env['almus.app.registry'].sync_almus_apps()
        
        # Mostrar notificación sin recargar
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Sincronización Completada'),
                'message': _('El registro de aplicaciones Almus ha sido actualizado.'),
                'type': 'success',
                'sticky': False,
            }
        }