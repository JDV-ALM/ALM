# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import AccessError
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
    def check_access_rights(self, operation, raise_exception=True):
        """Override para controlar acceso a listas de precios"""
        result = super().check_access_rights(operation, raise_exception=False)
        
        if not self._is_price_control_enabled():
            return result or super().check_access_rights(operation, raise_exception=raise_exception)
        
        ICP = self.env['ir.config_parameter'].sudo()
        restrict_access = safe_eval(ICP.get_param('almus_sale_price_control.restrict_pricelist_access', 'True'))
        
        if restrict_access and operation in ['write', 'create', 'unlink']:
            if not self.env.user.has_group('sales_team.group_sale_manager'):
                if raise_exception:
                    raise AccessError('Solo los administradores pueden %s listas de precios.' % operation)
                return False
        
        return result or super().check_access_rights(operation, raise_exception=raise_exception)
    
    def write(self, vals):
        """Override write para verificar permisos"""
        self.check_access_rights('write')
        return super().write(vals)
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create para verificar permisos"""
        self.check_access_rights('create')
        return super().create(vals_list)
    
    def unlink(self):
        """Override unlink para verificar permisos"""
        self.check_access_rights('unlink')
        return super().unlink()