# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # Configuración simplificada para Partners
    almus_disable_partner_creation = fields.Boolean(
        string='Desactivar creación rápida de contactos',
        help='Obliga a crear contactos solo desde el módulo de Contactos',
        config_parameter='almus_disable_quick_create.disable_partner_creation',
    )
    
    # Configuración simplificada para Productos
    almus_disable_product_creation = fields.Boolean(
        string='Desactivar creación rápida de productos',
        help='Obliga a crear productos solo desde el módulo de Inventario',
        config_parameter='almus_disable_quick_create.disable_product_creation',
    )
    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        _logger.info('Actualizando configuración de Almus Disable Quick Create por usuario %s', self.env.user.name)


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        res = super().get_view(view_id, view_type, **options)
        
        if view_type == 'form':
            ICP = self.env['ir.config_parameter'].sudo()
            
            # Obtener configuraciones
            disable_partner = ICP.get_param('almus_disable_quick_create.disable_partner_creation', 'False') == 'True'
            disable_product = ICP.get_param('almus_disable_quick_create.disable_product_creation', 'False') == 'True'
            
            # Aplicar opciones a campos en la vista
            from lxml import etree
            doc = etree.XML(res['arch'])
            
            # Campos de partner
            if disable_partner:
                for field in doc.xpath("//field[@name='partner_id'] | //field[@name='partner_invoice_id'] | //field[@name='partner_shipping_id']"):
                    field.set('options', "{'no_create': True, 'no_create_edit': True, 'no_quick_create': True}")
            
            # Campos de producto en líneas
            if disable_product:
                for field in doc.xpath("//field[@name='order_line']//field[@name='product_id'] | //field[@name='order_line']//field[@name='product_template_id']"):
                    field.set('options', "{'no_create': True, 'no_create_edit': True, 'no_quick_create': True}")
            
            res['arch'] = etree.tostring(doc, encoding='unicode')
        
        return res


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        res = super().get_view(view_id, view_type, **options)
        
        if view_type == 'form':
            ICP = self.env['ir.config_parameter'].sudo()
            
            # Obtener configuraciones
            disable_partner = ICP.get_param('almus_disable_quick_create.disable_partner_creation', 'False') == 'True'
            disable_product = ICP.get_param('almus_disable_quick_create.disable_product_creation', 'False') == 'True'
            
            # Aplicar opciones a campos en la vista
            from lxml import etree
            doc = etree.XML(res['arch'])
            
            # Campo de partner
            if disable_partner:
                for field in doc.xpath("//field[@name='partner_id']"):
                    field.set('options', "{'no_create': True, 'no_create_edit': True, 'no_quick_create': True}")
            
            # Campos de producto en líneas
            if disable_product:
                for field in doc.xpath("//field[@name='order_line']//field[@name='product_id']"):
                    field.set('options', "{'no_create': True, 'no_create_edit': True, 'no_quick_create': True}")
            
            res['arch'] = etree.tostring(doc, encoding='unicode')
        
        return res


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        res = super().get_view(view_id, view_type, **options)
        
        if view_type == 'form':
            ICP = self.env['ir.config_parameter'].sudo()
            
            # Obtener configuraciones
            disable_partner = ICP.get_param('almus_disable_quick_create.disable_partner_creation', 'False') == 'True'
            disable_product = ICP.get_param('almus_disable_quick_create.disable_product_creation', 'False') == 'True'
            
            # Aplicar opciones a campos en la vista
            from lxml import etree
            doc = etree.XML(res['arch'])
            
            # Campos de partner
            if disable_partner:
                for field in doc.xpath("//field[@name='partner_id'] | //field[@name='partner_shipping_id']"):
                    field.set('options', "{'no_create': True, 'no_create_edit': True, 'no_quick_create': True}")
            
            # Campos de producto en líneas
            if disable_product:
                for field in doc.xpath("//field[@name='invoice_line_ids']//field[@name='product_id']"):
                    field.set('options', "{'no_create': True, 'no_create_edit': True, 'no_quick_create': True}")
            
            res['arch'] = etree.tostring(doc, encoding='unicode')
        
        return res