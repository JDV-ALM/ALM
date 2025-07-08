from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # Campo para activar/desactivar la funcionalidad
    almus_partner_confidential_enabled = fields.Boolean(
        string='Activar Información Confidencial de Contactos',
        config_parameter='almus_partner_confidential.enabled',
        help='Activa la pestaña de información confidencial en los contactos'
    )