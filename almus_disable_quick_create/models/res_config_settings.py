# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # Configuraciones para Partners (Clientes/Proveedores)
    almus_disable_partner_quick_create = fields.Boolean(
        string='Desactivar "Crear" para Contactos',
        help='Evita crear contactos rápidamente desde los formularios de ventas y compras',
        config_parameter='almus_disable_quick_create.disable_partner_quick_create',
    )
    
    almus_disable_partner_create_edit = fields.Boolean(
        string='Desactivar "Crear y editar" para Contactos',
        help='Evita crear y editar contactos desde los formularios de ventas y compras',
        config_parameter='almus_disable_quick_create.disable_partner_create_edit',
    )
    
    # Configuraciones para Productos
    almus_disable_product_quick_create = fields.Boolean(
        string='Desactivar "Crear" para Productos',
        help='Evita crear productos rápidamente desde los formularios de ventas y compras',
        config_parameter='almus_disable_quick_create.disable_product_quick_create',
    )
    
    almus_disable_product_create_edit = fields.Boolean(
        string='Desactivar "Crear y editar" para Productos',
        help='Evita crear y editar productos desde los formularios de ventas y compras',
        config_parameter='almus_disable_quick_create.disable_product_create_edit',
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
            disable_partner_create = ICP.get_param('almus_disable_quick_create.disable_partner_quick_create', 'False') == 'True'
            disable_partner_create_edit = ICP.get_param('almus_disable_quick_create.disable_partner_create_edit', 'False') == 'True'
            disable_product_create = ICP.get_param('almus_disable_quick_create.disable_product_quick_create', 'False') == 'True'
            disable_product_create_edit = ICP.get_param('almus_disable_quick_create.disable_product_create_edit', 'False') == 'True'
            
            # Aplicar opciones a campos en la vista
            from lxml import etree
            doc = etree.XML(res['arch'])
            
            # Campos de partner
            for field in doc.xpath("//field[@name='partner_id'] | //field[@name='partner_invoice_id'] | //field[@name='partner_shipping_id']"):
                options = {}
                if disable_partner_create:
                    options['no_create'] = True
                    options['no_quick_create'] = True
                if disable_partner_create_edit:
                    options['no_create_edit'] = True
                if options:
                    field.set('options', str(options))
            
            # Campos de producto en líneas
            for field in doc.xpath("//field[@name='order_line']//field[@name='product_id'] | //field[@name='order_line']//field[@name='product_template_id']"):
                options = {}
                if disable_product_create:
                    options['no_create'] = True
                    options['no_quick_create'] = True
                if disable_product_create_edit:
                    options['no_create_edit'] = True
                if options:
                    field.set('options', str(options))
            
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
            disable_partner_create = ICP.get_param('almus_disable_quick_create.disable_partner_quick_create', 'False') == 'True'
            disable_partner_create_edit = ICP.get_param('almus_disable_quick_create.disable_partner_create_edit', 'False') == 'True'
            disable_product_create = ICP.get_param('almus_disable_quick_create.disable_product_quick_create', 'False') == 'True'
            disable_product_create_edit = ICP.get_param('almus_disable_quick_create.disable_product_create_edit', 'False') == 'True'
            
            # Aplicar opciones a campos en la vista
            from lxml import etree
            doc = etree.XML(res['arch'])
            
            # Campo de partner
            for field in doc.xpath("//field[@name='partner_id']"):
                options = {}
                if disable_partner_create:
                    options['no_create'] = True
                    options['no_quick_create'] = True
                if disable_partner_create_edit:
                    options['no_create_edit'] = True
                if options:
                    field.set('options', str(options))
            
            # Campos de producto en líneas
            for field in doc.xpath("//field[@name='order_line']//field[@name='product_id']"):
                options = {}
                if disable_product_create:
                    options['no_create'] = True
                    options['no_quick_create'] = True
                if disable_product_create_edit:
                    options['no_create_edit'] = True
                if options:
                    field.set('options', str(options))
            
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
            disable_partner_create = ICP.get_param('almus_disable_quick_create.disable_partner_quick_create', 'False') == 'True'
            disable_partner_create_edit = ICP.get_param('almus_disable_quick_create.disable_partner_create_edit', 'False') == 'True'
            disable_product_create = ICP.get_param('almus_disable_quick_create.disable_product_quick_create', 'False') == 'True'
            disable_product_create_edit = ICP.get_param('almus_disable_quick_create.disable_product_create_edit', 'False') == 'True'
            
            # Aplicar opciones a campos en la vista
            from lxml import etree
            doc = etree.XML(res['arch'])
            
            # Campos de partner
            for field in doc.xpath("//field[@name='partner_id'] | //field[@name='partner_shipping_id']"):
                options = {}
                if disable_partner_create:
                    options['no_create'] = True
                    options['no_quick_create'] = True
                if disable_partner_create_edit:
                    options['no_create_edit'] = True
                if options:
                    field.set('options', str(options))
            
            # Campos de producto en líneas
            for field in doc.xpath("//field[@name='invoice_line_ids']//field[@name='product_id']"):
                options = {}
                if disable_product_create:
                    options['no_create'] = True
                    options['no_quick_create'] = True
                if disable_product_create_edit:
                    options['no_create_edit'] = True
                if options:
                    field.set('options', str(options))
            
            res['arch'] = etree.tostring(doc, encoding='unicode')
        
        return res