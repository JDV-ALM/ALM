# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
import logging

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    line_pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Lista de Precios de Línea',
        help='Lista de precios específica para esta línea'
    )
    
    @api.model
    def _is_price_control_enabled(self):
        """Verifica si el control de precios está habilitado"""
        ICP = self.env['ir.config_parameter'].sudo()
        return safe_eval(ICP.get_param('almus_sale_price_control.enabled', 'True'))
    
    @api.model
    def _is_line_pricelist_enabled(self):
        """Verifica si está habilitada la lista de precios por línea"""
        ICP = self.env['ir.config_parameter'].sudo()
        return safe_eval(ICP.get_param('almus_sale_price_control.enable_line_pricelist', 'True'))
    
    @api.model
    def _can_edit_price(self):
        """Verifica si el usuario puede editar precios"""
        if not self._is_price_control_enabled():
            return True
            
        ICP = self.env['ir.config_parameter'].sudo()
        restrict_price = safe_eval(ICP.get_param('almus_sale_price_control.restrict_price_edit', 'True'))
        
        if restrict_price and not self.env.user.has_group('sales_team.group_sale_manager'):
            return False
        return True
    
    @api.onchange('line_pricelist_id')
    def _onchange_line_pricelist_id(self):
        """Recalcula el precio cuando cambia la lista de precios de la línea"""
        if self.line_pricelist_id and self.product_id and self._is_line_pricelist_enabled():
            # Obtener el precio de la lista de precios seleccionada
            price = self.line_pricelist_id._get_product_price(
                self.product_id,
                self.product_uom_qty or 1.0,
                currency=self.order_id.currency_id,
                date=self.order_id.date_order,
                uom=self.product_uom
            )
            
            # Aplicar el precio
            self.price_unit = price
            
            # Recalcular descuentos si aplica
            if self.order_id.pricelist_id.discount_policy == 'with_discount':
                discount = 0.0
                pricelist_price = self.order_id.pricelist_id._get_product_price(
                    self.product_id,
                    self.product_uom_qty or 1.0,
                    currency=self.order_id.currency_id,
                    date=self.order_id.date_order,
                    uom=self.product_uom
                )
                if pricelist_price != 0:
                    discount = max(0, (pricelist_price - price) / pricelist_price * 100)
                self.discount = discount
            
            _logger.info('Precio actualizado para línea %s usando lista de precios %s', 
                        self.product_id.name, self.line_pricelist_id.name)
    
    @api.onchange('product_id', 'product_uom_qty', 'product_uom')
    def product_id_change(self):
        """Override para usar la lista de precios de la línea si está configurada"""
        result = super().product_id_change()
        
        if self._is_line_pricelist_enabled() and self.line_pricelist_id and self.product_id:
            self._onchange_line_pricelist_id()
            
        return result
    
    @api.onchange('price_unit')
    def _onchange_price_unit(self):
        """Valida si el usuario puede cambiar el precio"""
        if not self._can_edit_price() and self._origin.price_unit != self.price_unit:
            raise UserError(_('No tiene permisos para modificar el precio unitario.'))
    
    def write(self, vals):
        """Override write para controlar cambios en price_unit"""
        if 'price_unit' in vals and not self._can_edit_price():
            # Verificar si realmente está cambiando el precio
            for line in self:
                if line.price_unit != vals['price_unit']:
                    raise UserError(_('No tiene permisos para modificar el precio unitario.'))
        
        return super().write(vals)
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create para validar permisos al crear líneas"""
        if not self._can_edit_price():
            for vals in vals_list:
                if 'price_unit' in vals:
                    # Si se está especificando un precio, verificar que sea correcto
                    # según la lista de precios
                    product = self.env['product.product'].browse(vals.get('product_id'))
                    order = self.env['sale.order'].browse(vals.get('order_id'))
                    if product and order:
                        expected_price = order.pricelist_id._get_product_price(
                            product,
                            vals.get('product_uom_qty', 1.0),
                            currency=order.currency_id,
                            date=order.date_order
                        )
                        if abs(vals['price_unit'] - expected_price) > 0.01:
                            raise UserError(_('No tiene permisos para crear líneas con precios personalizados.'))
        
        return super().create(vals_list)