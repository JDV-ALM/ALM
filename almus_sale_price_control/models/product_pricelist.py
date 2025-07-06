# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval
import logging

_logger = logging.getLogger(__name__)


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'
    
    @api.model
    def _is_price_control_enabled(self):
        """Verifica si el control de precios está habilitado"""
        ICP = self.env['ir.config_parameter'].sudo()
        return safe_eval(ICP.get_param('almus_sale_price_control.enabled', 'True'))
    
    @api.model
    def _check_write_access(self):
        """Verifica si el usuario puede escribir en listas de precios"""
        if not self._is_price_control_enabled():
            return True
            
        ICP = self.env['ir.config_parameter'].sudo()
        restrict_access = safe_eval(ICP.get_param('almus_sale_price_control.restrict_pricelist_access', 'True'))
        
        if restrict_access and not self.env.user.has_group('sales_team.group_sale_manager'):
            return False
        return True
    
    def write(self, vals):
        """Override write para verificar permisos"""
        if not self._check_write_access():
            raise UserError('Solo los administradores pueden modificar listas de precios.')
        return super().write(vals)
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create para verificar permisos"""
        if not self._check_write_access():
            raise UserError('Solo los administradores pueden crear listas de precios.')
        return super().create(vals_list)
    
    def unlink(self):
        """Override unlink para verificar permisos"""
        if not self._check_write_access():
            raise UserError('Solo los administradores pueden eliminar listas de precios.')
        return super().unlink()


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'
    
    def write(self, vals):
        """Override write para verificar permisos"""
        if not self.pricelist_id._check_write_access():
            raise UserError('Solo los administradores pueden modificar elementos de listas de precios.')
        return super().write(vals)
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create para verificar permisos"""
        # Verificar acceso usando el método del modelo padre
        if not self.env['product.pricelist']._check_write_access():
            raise UserError('Solo los administradores pueden crear elementos de listas de precios.')
        return super().create(vals_list)
    
    def unlink(self):
        """Override unlink para verificar permisos"""
        if not self.pricelist_id._check_write_access():
            raise UserError('Solo los administradores pueden eliminar elementos de listas de precios.')
        return super().unlink()