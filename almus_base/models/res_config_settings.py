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
        
        # Sincronizar registro si está vacío o desactualizado
        if not AlmusRegistry.search_count([]) or self._context.get('force_almus_sync'):
            AlmusRegistry.sync_almus_apps()
        
        for settings in self:
            # Usar el registro persistente
            settings.almus_installed_apps = AlmusRegistry.get_installed_count()
            settings.almus_app_list = AlmusRegistry.get_installed_list()
    
    def action_refresh_almus_apps(self):
        """Refrescar manualmente el registro de apps Almus"""
        self.env['almus.app.registry'].sync_almus_apps()
        
        # Forzar el recálculo de los campos
        self._compute_almus_stats()
        
        # Mostrar notificación sin recargar la vista
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Sincronización Completada'),
                'message': _('El registro de aplicaciones Almus ha sido actualizado.'),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.client', 'tag': 'soft_reload'},
            }
        }