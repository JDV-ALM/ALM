# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # Configuración general del módulo
    almus_sale_pricelist_control_enabled = fields.Boolean(
        string='Activar Control de Listas de Precios',
        config_parameter='almus_sale_pricelist_control.enabled',
        default=True,
        help='Activa el control de edición de listas de precios y precios en órdenes de venta'
    )
    
    # Control de edición de listas de precios
    almus_restrict_pricelist_edit = fields.Boolean(
        string='Restringir Edición de Listas',
        config_parameter='almus_sale_pricelist_control.restrict_pricelist_edit',
        default=True,
        help='Solo los administradores de ventas pueden editar listas de precios'
    )
    
    # Control de precios en líneas de venta
    almus_hide_unit_price = fields.Boolean(
        string='Ocultar Precio Unitario',
        config_parameter='almus_sale_pricelist_control.hide_unit_price',
        default=True,
        help='Oculta el campo de precio unitario para usuarios no administradores'
    )
    
    # Lista de precios por línea
    almus_pricelist_per_line = fields.Boolean(
        string='Lista de Precios por Línea',
        config_parameter='almus_sale_pricelist_control.pricelist_per_line',
        default=True,
        help='Permite seleccionar una lista de precios diferente para cada línea de la orden'
    )
    
    # Configuración por compañía
    almus_apply_per_company = fields.Boolean(
        string='Aplicar por Compañía',
        config_parameter='almus_sale_pricelist_control.apply_per_company',
        company_dependent=True,
        help='Aplicar estas configuraciones solo a la compañía actual'
    )
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        
        res.update(
            almus_sale_pricelist_control_enabled=params.get_param(
                'almus_sale_pricelist_control.enabled', default=True
            ),
            almus_restrict_pricelist_edit=params.get_param(
                'almus_sale_pricelist_control.restrict_pricelist_edit', default=True
            ),
            almus_hide_unit_price=params.get_param(
                'almus_sale_pricelist_control.hide_unit_price', default=True
            ),
            almus_pricelist_per_line=params.get_param(
                'almus_sale_pricelist_control.pricelist_per_line', default=True
            ),
        )
        
        _logger.info('Configuración de Almus Sale Pricelist Control cargada')
        return res
    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        
        params.set_param('almus_sale_pricelist_control.enabled', self.almus_sale_pricelist_control_enabled)
        params.set_param('almus_sale_pricelist_control.restrict_pricelist_edit', self.almus_restrict_pricelist_edit)
        params.set_param('almus_sale_pricelist_control.hide_unit_price', self.almus_hide_unit_price)
        params.set_param('almus_sale_pricelist_control.pricelist_per_line', self.almus_pricelist_per_line)
        
        _logger.info('Configuración de Almus Sale Pricelist Control guardada por usuario %s', self.env.user.name)