from odoo import models, fields, api
from odoo.exceptions import AccessError
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    # Campos de información confidencial
    almus_confidential_name = fields.Char(
        string='Nombre Internacional',
        help='Nombre del proveedor en su idioma original o nombre comercial internacional'
    )
    
    almus_confidential_email = fields.Char(
        string='Correo Confidencial',
        help='Correo electrónico privado para comunicaciones sensibles'
    )
    
    almus_wechat_id = fields.Char(
        string='WeChat ID',
        help='Identificador de WeChat para comunicaciones'
    )
    
    almus_whatsapp_number = fields.Char(
        string='WhatsApp',
        help='Número de WhatsApp para comunicaciones directas'
    )
    
    almus_contact_person = fields.Char(
        string='Persona de Contacto Clave',
        help='Nombre de la persona de contacto principal para asuntos importantes'
    )
    
    almus_payment_terms_notes = fields.Text(
        string='Términos de Pago Especiales',
        help='Notas sobre condiciones de pago negociadas o especiales'
    )
    
    almus_price_conditions = fields.Text(
        string='Condiciones de Precios',
        help='Información sobre descuentos, precios especiales o condiciones comerciales'
    )
    
    almus_bank_info = fields.Text(
        string='Información Bancaria',
        help='Datos bancarios para transferencias internacionales'
    )
    
    almus_internal_notes = fields.Text(
        string='Notas Internas Confidenciales',
        help='Notas privadas sobre el proveedor que no deben ser compartidas'
    )
    
    almus_credit_info = fields.Text(
        string='Información de Crédito',
        help='Límites de crédito, historial de pagos y otra información financiera'
    )
    
    # Campo para búsquedas rápidas
    almus_has_confidential = fields.Boolean(
        string='Tiene información confidencial',
        store=True,
        index=True,
        help='Indica si el contacto tiene información confidencial'
    )
    
    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        """Modificar la vista para ocultar la pestaña cuando la funcionalidad está desactivada"""
        res = super().get_view(view_id, view_type, **options)
        
        if view_type == 'form' and res.get('arch'):
            # Agregar una clave de caché basada en el estado de configuración
            cache_key = f"partner_view_{view_id}_{self._is_confidential_enabled()}"
            
            # Si ya procesamos esta vista con este estado, devolver directamente
            if hasattr(self.env, '_view_cache') and cache_key in self.env._view_cache:
                res['arch'] = self.env._view_cache[cache_key]
                return res
                
            # Verificar si la funcionalidad está activada
            is_enabled = self._is_confidential_enabled()
            
            if not is_enabled:
                # Si no está activada, modificar el XML para agregar invisible="1"
                from lxml import etree
                doc = etree.XML(res['arch'])
                
                # Buscar la pestaña de información confidencial
                pages = doc.xpath("//page[@name='almus_confidential_info']")
                for page in pages:
                    page.set('invisible', '1')
                
                res['arch'] = etree.tostring(doc, encoding='unicode')
                
            # Guardar en caché temporal
            if not hasattr(self.env, '_view_cache'):
                self.env._view_cache = {}
            self.env._view_cache[cache_key] = res['arch']
        
        return res
    
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
            
        if self._has_confidential_data(vals):
            # Solo registrar en log
            _logger.info('Información confidencial creada para partner por usuario %s', self.env.user.name)
            # Marcar que tiene información confidencial
            vals['almus_has_confidential'] = True
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
            
        if self._has_confidential_data(vals):
            # Solo registrar en log
            _logger.info('Información confidencial modificada para partner %s por usuario %s', 
                        ', '.join([str(p.id) for p in self]), self.env.user.name)
            # Marcar que tiene información confidencial
            vals['almus_has_confidential'] = True
            
        # Verificar si necesitamos actualizar almus_has_confidential a False
        if not self._has_confidential_data(vals) and 'almus_has_confidential' not in vals:
            for partner in self:
                # Verificar si todos los campos confidenciales están vacíos
                has_any_data = any([
                    partner.almus_confidential_name,
                    partner.almus_confidential_email,
                    partner.almus_wechat_id,
                    partner.almus_whatsapp_number,
                    partner.almus_contact_person,
                    partner.almus_payment_terms_notes,
                    partner.almus_price_conditions,
                    partner.almus_bank_info,
                    partner.almus_internal_notes,
                    partner.almus_credit_info
                ])
                if not has_any_data:
                    vals['almus_has_confidential'] = False
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