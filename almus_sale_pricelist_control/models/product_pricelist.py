# -*- coding: utf-8 -*-
import logging
from odoo import models, api, fields
from odoo.exceptions import UserError, AccessError

_logger = logging.getLogger(__name__)


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'
    
    is_admin_user = fields.Boolean(
        compute='_compute_is_admin_user',
        store=False
    )
    
    @api.depends_context('uid')
    def _compute_is_admin_user(self):
        is_admin = self.env.user.has_group('sales_team.group_sale_manager')
        for record in self:
            record.is_admin_user = is_admin
    
    @api.model
    def check_access_rights(self, operation, raise_exception=True):
        """Verifica permisos de acceso según configuración del módulo"""
        res = super(ProductPricelist, self).check_access_rights(operation, raise_exception=False)
        
        # Verificar si el control está habilitado
        enabled = self.env['ir.config_parameter'].sudo().get_param(
            'almus_sale_pricelist_control.enabled', 'True'
        ) == 'True'
        restrict_edit = self.env['ir.config_parameter'].sudo().get_param(
            'almus_sale_pricelist_control.restrict_pricelist_edit', 'True'
        ) == 'True'
        
        if enabled and restrict_edit and operation in ('write', 'create', 'unlink'):
            # Verificar si es administrador de ventas
            if not self.env.user.has_group('sales_team.group_sale_manager'):
                _logger.warning(
                    'Usuario %s intentó %s en product.pricelist sin permisos de administrador',
                    self.env.user.name, operation
                )
                if raise_exception:
                    raise AccessError(
                        'Solo los administradores de ventas pueden modificar las listas de precios'
                    )
                return False
        
        return res
    
    def write(self, vals):
        """Sobrescribe write para validar permisos"""
        self.check_access_rights('write')
        
        # Log de cambios
        for record in self:
            _logger.info(
                'Lista de precios %s modificada por usuario %s',
                record.name, self.env.user.name
            )
        
        return super(ProductPricelist, self).write(vals)
    
    @api.model_create_multi
    def create(self, vals_list):
        """Sobrescribe create para validar permisos"""
        self.check_access_rights('create')
        
        records = super(ProductPricelist, self).create(vals_list)
        
        # Log de creación
        for record in records:
            _logger.info(
                'Lista de precios %s creada por usuario %s',
                record.name, self.env.user.name
            )
        
        return records
    
    def unlink(self):
        """Sobrescribe unlink para validar permisos"""
        self.check_access_rights('unlink')
        
        # Log antes de eliminar
        for record in self:
            _logger.info(
                'Lista de precios %s eliminada por usuario %s',
                record.name, self.env.user.name
            )
        
        return super(ProductPricelist, self).unlink()