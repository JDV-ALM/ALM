# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    almus_sale_price_control_enabled = fields.Boolean(
        string='Activar Control de Precios',
        config_parameter='almus_sale_price_control.enabled',
        default=True,
        help='Activa las restricciones de control de precios en ventas'
    )
    
    almus_sale_restrict_pricelist_access = fields.Boolean(
        string='Restringir Acceso a Listas de Precios',
        config_parameter='almus_sale_price_control.restrict_pricelist_access',
        default=True,
        help='Solo los administradores podrán ver y modificar las listas de precios'
    )
    
    almus_sale_restrict_price_edit = fields.Boolean(
        string='Restringir Edición de Precios en Ventas',
        config_parameter='almus_sale_price_control.restrict_price_edit',
        default=True,
        help='Los vendedores no podrán modificar precios en líneas de venta'
    )
    
    almus_sale_enable_line_pricelist = fields.Boolean(
        string='Habilitar Lista de Precios por Línea',
        config_parameter='almus_sale_price_control.enable_line_pricelist',
        default=True,
        help='Permite seleccionar una lista de precios diferente para cada línea de venta'
    )
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICP = self.env['ir.config_parameter'].sudo()
        
        res.update(
            almus_sale_price_control_enabled=ICP.get_param(
                'almus_sale_price_control.enabled', default=True
            ),
            almus_sale_restrict_pricelist_access=ICP.get_param(
                'almus_sale_price_control.restrict_pricelist_access', default=True
            ),
            almus_sale_restrict_price_edit=ICP.get_param(
                'almus_sale_price_control.restrict_price_edit', default=True
            ),
            almus_sale_enable_line_pricelist=ICP.get_param(
                'almus_sale_price_control.enable_line_pricelist', default=True
            ),
        )
        return res
    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICP = self.env['ir.config_parameter'].sudo()
        
        ICP.set_param('almus_sale_price_control.enabled', self.almus_sale_price_control_enabled)
        ICP.set_param('almus_sale_price_control.restrict_pricelist_access', self.almus_sale_restrict_pricelist_access)
        ICP.set_param('almus_sale_price_control.restrict_price_edit', self.almus_sale_restrict_price_edit)
        ICP.set_param('almus_sale_price_control.enable_line_pricelist', self.almus_sale_enable_line_pricelist)
        
        # Limpiar caché cuando se cambien las configuraciones
        self.env.registry.clear_cache()
        
        _logger.info('Configuración de Almus Sale Price Control actualizada por usuario %s', self.env.user.name)