from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # Campo para activar/desactivar la funcionalidad
    almus_partner_confidential_enabled = fields.Boolean(
        string='Activar Información Confidencial de Contactos',
        config_parameter='almus_partner_confidential.enabled',
        help='Activa la pestaña de información confidencial en los contactos'
    )
    
    @api.model
    def set_values(self):
        """Sobrescribir para manejar la activación/desactivación"""
        # Obtener el valor anterior
        was_enabled = self.env['ir.config_parameter'].sudo().get_param(
            'almus_partner_confidential.enabled', 'False'
        ).lower() == 'true'
        
        # Llamar al método padre
        super().set_values()
        
        # Obtener el valor nuevo
        is_enabled = self.almus_partner_confidential_enabled
        
        # Log del cambio
        if was_enabled != is_enabled:
            _logger.info(
                'Información Confidencial de Contactos %s por el usuario %s',
                'activada' if is_enabled else 'desactivada',
                self.env.user.name
            )