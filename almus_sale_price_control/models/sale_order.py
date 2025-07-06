# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    @api.model
    def _is_price_control_enabled(self):
        """Verifica si el control de precios está habilitado"""
        ICP = self.env['ir.config_parameter'].sudo()
        return safe_eval(ICP.get_param('almus_sale_price_control.enabled', 'True'))
    
    @api.model
    def _check_pricelist_access(self):
        """Verifica si el usuario tiene acceso a modificar listas de precios"""
        if not self._is_price_control_enabled():
            return True
            
        ICP = self.env['ir.config_parameter'].sudo()
        restrict_access = safe_eval(ICP.get_param('almus_sale_price_control.restrict_pricelist_access', 'True'))
        
        if restrict_access and not self.env.user.has_group('sales_team.group_sale_manager'):
            return False
        return True
    
    @api.onchange('pricelist_id')
    def _onchange_pricelist_id(self):
        """Override para verificar permisos al cambiar lista de precios"""
        if self.pricelist_id and not self._check_pricelist_access():
            raise UserError('No tiene permisos para cambiar la lista de precios de la orden.')
        return super()._onchange_pricelist_id()
    
    def write(self, vals):
        """Override write para controlar cambios en pricelist_id"""
        if 'pricelist_id' in vals and not self._check_pricelist_access():
            raise UserError('No tiene permisos para cambiar la lista de precios de la orden.')
        return super().write(vals)