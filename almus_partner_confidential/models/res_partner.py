from odoo import models, fields, api
from odoo.exceptions import AccessError
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    # Campos de información confidencial
    almus_confidential_name = fields.Char(
        string='Nombre Internacional',
        help='Nombre del proveedor en su idioma original o nombre comercial internacional',
        groups='almus_partner_confidential.group_partner_confidential_user'
    )
    
    almus_confidential_email = fields.Char(
        string='Correo Confidencial',
        help='Correo electrónico privado para comunicaciones sensibles',
        groups='almus_partner_confidential.group_partner_confidential_user'
    )
    
    almus_wechat_id = fields.Char(
        string='WeChat ID',
        help='Identificador de WeChat para comunicaciones',
        groups='almus_partner_confidential.group_partner_confidential_user'
    )
    
    almus_whatsapp_number = fields.Char(
        string='WhatsApp',
        help='Número de WhatsApp para comunicaciones directas',
        groups='almus_partner_confidential.group_partner_confidential_user'
    )
    
    almus_contact_person = fields.Char(
        string='Persona de Contacto Clave',
        help='Nombre de la persona de contacto principal para asuntos importantes',
        groups='almus_partner_confidential.group_partner_confidential_user'
    )
    
    almus_payment_terms_notes = fields.Text(
        string='Términos de Pago Especiales',
        help='Notas sobre condiciones de pago negociadas o especiales',
        groups='almus_partner_confidential.group_partner_confidential_user'
    )
    
    almus_price_conditions = fields.Text(
        string='Condiciones de Precios',
        help='Información sobre descuentos, precios especiales o condiciones comerciales',
        groups='almus_partner_confidential.group_partner_confidential_user'
    )
    
    almus_bank_info = fields.Text(
        string='Información Bancaria',
        help='Datos bancarios para transferencias internacionales',
        groups='almus_partner_confidential.group_partner_confidential_user'
    )
    
    almus_internal_notes = fields.Text(
        string='Notas Internas Confidenciales',
        help='Notas privadas sobre el proveedor que no deben ser compartidas',
        groups='almus_partner_confidential.group_partner_confidential_user'
    )
    
    almus_credit_info = fields.Text(
        string='Información de Crédito',
        help='Límites de crédito, historial de pagos y otra información financiera',
        groups='almus_partner_confidential.group_partner_confidential_user'
    )
    
    # Tracking de última modificación de información confidencial
    almus_confidential_last_update = fields.Datetime(
        string='Última Actualización Confidencial',
        readonly=True,
        groups='almus_partner_confidential.group_partner_confidential_user'
    )
    
    almus_confidential_last_user = fields.Many2one(
        'res.users',
        string='Último Usuario que Modificó',
        readonly=True,
        groups='almus_partner_confidential.group_partner_confidential_user'
    )
    
    # Campo computado para verificar si la funcionalidad está activa
    almus_show_confidential_tab = fields.Boolean(
        compute='_compute_show_confidential_tab',
        string='Mostrar Pestaña Confidencial'
    )
    
    @api.depends_context('uid')
    def _compute_show_confidential_tab(self):
        """Determina si mostrar la pestaña confidencial basado en:
        1. Si la funcionalidad está activada en configuración
        2. Si el usuario tiene permisos para ver información confidencial
        """
        is_enabled = self.env['ir.config_parameter'].sudo().get_param(
            'almus_partner_confidential.enabled', 'False'
        ).lower() == 'true'
        
        has_permission = self.env.user.has_group(
            'almus_partner_confidential.group_partner_confidential_user'
        )
        
        for record in self:
            record.almus_show_confidential_tab = is_enabled and has_permission
            
        _logger.debug(
            'Verificación pestaña confidencial - Activado: %s, Permisos: %s, Usuario: %s',
            is_enabled, has_permission, self.env.user.name
        )
    
    @api.model
    def create(self, vals):
        """Registrar creación de información confidencial"""
        # Verificar si la funcionalidad está activa
        if not self._is_confidential_enabled():
            # Si no está activa, eliminar campos confidenciales de vals
            vals = self._remove_confidential_fields(vals)
            return super().create(vals)
            
        # Verificar permisos si hay datos confidenciales
        if self._has_confidential_data(vals) and not self.env.user.has_group(
            'almus_partner_confidential.group_partner_confidential_manager'
        ):
            raise AccessError('No tiene permisos para crear información confidencial.')
            
        if self._has_confidential_data(vals) and self.env.user.has_group(
            'almus_partner_confidential.group_partner_confidential_manager'
        ):
            vals.update({
                'almus_confidential_last_update': fields.Datetime.now(),
                'almus_confidential_last_user': self.env.user.id,
            })
        return super().create(vals)
    
    def write(self, vals):
        """Registrar modificación de información confidencial"""
        # Verificar si la funcionalidad está activa
        if not self._is_confidential_enabled():
            # Si no está activa, eliminar campos confidenciales de vals
            vals = self._remove_confidential_fields(vals)
            return super().write(vals)
            
        # Verificar permisos si hay datos confidenciales
        if self._has_confidential_data(vals) and not self.env.user.has_group(
            'almus_partner_confidential.group_partner_confidential_manager'
        ):
            raise AccessError('No tiene permisos para modificar información confidencial.')
            
        if self._has_confidential_data(vals) and self.env.user.has_group(
            'almus_partner_confidential.group_partner_confidential_manager'
        ):
            vals.update({
                'almus_confidential_last_update': fields.Datetime.now(),
                'almus_confidential_last_user': self.env.user.id,
            })
        return super().write(vals)
    
    def _has_confidential_data(self, vals):
        """Verifica si los valores contienen campos confidenciales"""
        confidential_fields = self._get_confidential_fields()
        return bool(confidential_fields.intersection(vals.keys()))
    
    def _get_confidential_fields(self):
        """Retorna el conjunto de campos confidenciales"""
        return {
            'almus_confidential_name', 'almus_confidential_email',
            'almus_wechat_id', 'almus_whatsapp_number',
            'almus_contact_person', 'almus_payment_terms_notes',
            'almus_price_conditions', 'almus_bank_info',
            'almus_internal_notes', 'almus_credit_info'
        }
    
    def _is_confidential_enabled(self):
        """Verifica si la funcionalidad de información confidencial está activada"""
        return self.env['ir.config_parameter'].sudo().get_param(
            'almus_partner_confidential.enabled', 'False'
        ).lower() == 'true'
    
    def _remove_confidential_fields(self, vals):
        """Elimina campos confidenciales del diccionario de valores"""
        confidential_fields = self._get_confidential_fields()
        return {k: v for k, v in vals.items() if k not in confidential_fields}