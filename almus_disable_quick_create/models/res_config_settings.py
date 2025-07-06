# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # Configuraciones para Partners/Contactos
    almus_disable_partner_quick_create = fields.Boolean(
        string='Deshabilitar creación rápida de contactos',
        help='Si está activado, no se permitirá crear contactos directamente desde los campos de cliente/proveedor',
        config_parameter='almus_disable_quick_create.disable_partner_quick_create',
    )
    
    almus_disable_partner_create_edit = fields.Boolean(
        string='Deshabilitar "Crear y editar" para contactos',
        help='Si está activado, no se permitirá usar la opción "Crear y editar" para contactos',
        config_parameter='almus_disable_quick_create.disable_partner_create_edit',
    )
    
    # Configuraciones para Productos
    almus_disable_product_quick_create = fields.Boolean(
        string='Deshabilitar creación rápida de productos',
        help='Si está activado, no se permitirá crear productos directamente desde las líneas de pedido',
        config_parameter='almus_disable_quick_create.disable_product_quick_create',
    )
    
    almus_disable_product_create_edit = fields.Boolean(
        string='Deshabilitar "Crear y editar" para productos',
        help='Si está activado, no se permitirá usar la opción "Crear y editar" para productos',
        config_parameter='almus_disable_quick_create.disable_product_create_edit',
    )
    
    @api.model
    def get_values(self):
        """Obtener valores de configuración"""
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        
        res.update(
            almus_disable_partner_quick_create=params.get_param(
                'almus_disable_quick_create.disable_partner_quick_create', 
                default=False
            ),
            almus_disable_partner_create_edit=params.get_param(
                'almus_disable_quick_create.disable_partner_create_edit', 
                default=False
            ),
            almus_disable_product_quick_create=params.get_param(
                'almus_disable_quick_create.disable_product_quick_create', 
                default=False
            ),
            almus_disable_product_create_edit=params.get_param(
                'almus_disable_quick_create.disable_product_create_edit', 
                default=False
            ),
        )
        
        _logger.info('Configuración Almus Disable Quick Create cargada: %s', res)
        return res
    
    def set_values(self):
        """Guardar valores de configuración"""
        super(ResConfigSettings, self).set_values()
        
        _logger.info('Guardando configuración Almus Disable Quick Create para la compañía %s', 
                     self.env.company.name)