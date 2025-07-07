# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    # Campo para lista de precios por línea
    line_pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Lista de Precios',
        help='Lista de precios específica para esta línea'
    )
    
    # Campo computado para verificar si mostrar el selector de lista
    show_line_pricelist = fields.Boolean(
        compute='_compute_show_line_pricelist',
        store=False
    )
    
    # Campo para determinar si el precio es editable
    is_price_editable = fields.Boolean(
        compute='_compute_is_price_editable',
        store=False
    )
    
    @api.depends('order_id')
    def _compute_show_line_pricelist(self):
        """Determina si mostrar el campo de lista de precios por línea"""
        enabled = self.env['ir.config_parameter'].sudo().get_param(
            'almus_sale_pricelist_control.enabled', 'True'
        ) == 'True'
        pricelist_per_line = self.env['ir.config_parameter'].sudo().get_param(
            'almus_sale_pricelist_control.pricelist_per_line', 'True'
        ) == 'True'
        
        show = enabled and pricelist_per_line
        for line in self:
            line.show_line_pricelist = show
    
    @api.depends('order_id')
    def _compute_is_price_editable(self):
        """Determina si el precio unitario es editable"""
        is_admin = self.env.user.has_group('sales_team.group_sale_manager')
        hide_price = self.env['ir.config_parameter'].sudo().get_param(
            'almus_sale_pricelist_control.hide_unit_price', 'True'
        ) == 'True'
        enabled = self.env['ir.config_parameter'].sudo().get_param(
            'almus_sale_pricelist_control.enabled', 'True'
        ) == 'True'
        
        for line in self:
            line.is_price_editable = is_admin or not (enabled and hide_price)
    
    @api.onchange('line_pricelist_id', 'product_id', 'product_uom_qty')
    def _onchange_line_pricelist_id(self):
        """Recalcula el precio cuando cambia la lista de precios de la línea"""
        if not self.line_pricelist_id or not self.product_id:
            return
        
        # Usar la lista de precios de la línea para calcular el precio
        pricelist = self.line_pricelist_id
        
        # Obtener el precio del producto según la lista seleccionada
        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id,
            quantity=self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=pricelist.id,
            uom=self.product_uom.id
        )
        
        price_unit = pricelist._get_product_price(
            product,
            self.product_uom_qty or 1.0,
            partner=self.order_id.partner_id,
            date=self.order_id.date_order,
            uom_id=self.product_uom.id
        )
        
        self.price_unit = price_unit
        
        # Log del cambio de precio
        _logger.info(
            'Precio actualizado para producto %s en orden %s: Lista %s, Precio: %s',
            self.product_id.name,
            self.order_id.name,
            pricelist.name,
            price_unit
        )
    
    @api.model_create_multi
    def create(self, vals_list):
        """Sobrescribe create para aplicar lista de precios por defecto"""
        for vals in vals_list:
            if 'line_pricelist_id' not in vals and 'order_id' in vals:
                order = self.env['sale.order'].browse(vals['order_id'])
                if order.pricelist_id:
                    vals['line_pricelist_id'] = order.pricelist_id.id
        
        return super(SaleOrderLine, self).create(vals_list)
    
    def _compute_price_unit(self):
        """Extiende el cálculo del precio para considerar la lista de la línea"""
        for line in self:
            if line.line_pricelist_id and line.product_id:
                # Usar la lista de precios de la línea si está definida
                pricelist = line.line_pricelist_id
                price_unit = pricelist._get_product_price(
                    line.product_id,
                    line.product_uom_qty or 1.0,
                    partner=line.order_id.partner_id,
                    date=line.order_id.date_order,
                    uom_id=line.product_uom.id
                )
                line.price_unit = price_unit
            else:
                # Comportamiento estándar
                super(SaleOrderLine, line)._compute_price_unit()