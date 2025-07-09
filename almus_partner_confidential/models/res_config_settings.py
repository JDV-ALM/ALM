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
    
    # Campo computado para mostrar estadísticas
    almus_confidential_partners_count = fields.Integer(
        string='Contactos con Información Confidencial',
        compute='_compute_confidential_partners_count'
    )
    
    # Campo para mostrar usuarios con acceso
    almus_confidential_users_count = fields.Integer(
        string='Usuarios con Acceso',
        compute='_compute_confidential_users_count'
    )
    
    @api.depends('almus_partner_confidential_enabled')
    def _compute_confidential_partners_count(self):
        """Cuenta cuántos partners tienen información confidencial"""
        for record in self:
            if record.almus_partner_confidential_enabled:
                # Contar partners con al menos un campo confidencial
                domain = ['|'] * 9 + [
                    ('almus_confidential_name', '!=', False),
                    ('almus_confidential_email', '!=', False),
                    ('almus_wechat_id', '!=', False),
                    ('almus_whatsapp_number', '!=', False),
                    ('almus_contact_person', '!=', False),
                    ('almus_payment_terms_notes', '!=', False),
                    ('almus_price_conditions', '!=', False),
                    ('almus_bank_info', '!=', False),
                    ('almus_internal_notes', '!=', False),
                    ('almus_credit_info', '!=', False)
                ]
                record.almus_confidential_partners_count = self.env['res.partner'].sudo().search_count(domain)
            else:
                record.almus_confidential_partners_count = 0
    
    @api.depends('almus_partner_confidential_enabled')
    def _compute_confidential_users_count(self):
        """Cuenta cuántos usuarios tienen acceso a información confidencial"""
        for record in self:
            group_user = self.env.ref('almus_partner_confidential.group_partner_confidential_user', False)
            if group_user:
                record.almus_confidential_users_count = len(group_user.users)
            else:
                record.almus_confidential_users_count = 0
    
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
            
            # Si se está desactivando, limpiar caché para actualizar vistas
            if not is_enabled:
                self.env['res.partner'].invalidate_model(['almus_show_confidential_tab'])
    
    def action_open_confidential_users(self):
        """Abre la vista de usuarios con acceso a información confidencial"""
        group = self.env.ref('almus_partner_confidential.group_partner_confidential_user')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Usuarios con Acceso a Información Confidencial',
            'res_model': 'res.users',
            'view_mode': 'tree,form',
            'domain': [('groups_id', 'in', group.id)],
            'context': {'create': False}
        }
    
    def action_open_confidential_partners(self):
        """Abre la vista de contactos con información confidencial"""
        domain = ['|'] * 9 + [
            ('almus_confidential_name', '!=', False),
            ('almus_confidential_email', '!=', False),
            ('almus_wechat_id', '!=', False),
            ('almus_whatsapp_number', '!=', False),
            ('almus_contact_person', '!=', False),
            ('almus_payment_terms_notes', '!=', False),
            ('almus_price_conditions', '!=', False),
            ('almus_bank_info', '!=', False),
            ('almus_internal_notes', '!=', False),
            ('almus_credit_info', '!=', False)
        ]
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contactos con Información Confidencial',
            'res_model': 'res.partner',
            'view_mode': 'tree,form',
            'domain': domain,
            'context': {'search_default_has_confidential': 1}
        }