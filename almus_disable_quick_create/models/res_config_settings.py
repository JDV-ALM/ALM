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
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        
        res.update({
            'almus_disable_partner_quick_create': params.get_param(
                'almus_disable_quick_create.disable_partner_quick_create', 
                default=False
            ),
            'almus_disable_partner_create_edit': params.get_param(
                'almus_disable_quick_create.disable_partner_create_edit', 
                default=False
            ),
            'almus_disable_product_quick_create': params.get_param(
                'almus_disable_quick_create.disable_product_quick_create', 
                default=False
            ),
            'almus_disable_product_create_edit': params.get_param(
                'almus_disable_quick_create.disable_product_create_edit', 
                default=False
            ),
        })
        
        return res
    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        _logger.info('Actualizando configuración de Almus Disable Quick Create por usuario %s', self.env.user.name)