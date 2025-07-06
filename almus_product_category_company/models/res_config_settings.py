from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    almus_product_category_company_enabled = fields.Boolean(
        string='Categorías de Producto por Empresa',
        config_parameter='almus_product_category_company.enabled',
        help='Cuando está activado, las categorías de producto serán específicas por empresa'
    )
    
    @api.model
    def set_values(self):
        """Override para ejecutar acciones al cambiar la configuración"""
        # Obtener valor anterior
        was_enabled = self.env['ir.config_parameter'].sudo().get_param(
            'almus_product_category_company.enabled', 'False'
        ) == 'True'
        
        # Guardar configuración
        super().set_values()
        
        # Obtener valor actual
        is_enabled = self.almus_product_category_company_enabled
        
        # Si se está activando por primera vez
        if not was_enabled and is_enabled:
            self._enable_product_category_company()
        # Si se está desactivando
        elif was_enabled and not is_enabled:
            self._disable_product_category_company()
    
    def _enable_product_category_company(self):
        """Acciones al activar la funcionalidad"""
        _logger.info('Activando funcionalidad de categorías por empresa')
        
        # Migrar categorías existentes sin empresa
        self._migrate_existing_categories()
        
        # Activar reglas de seguridad
        self._toggle_security_rules(True)
    
    def _disable_product_category_company(self):
        """Acciones al desactivar la funcionalidad"""
        _logger.info('Desactivando funcionalidad de categorías por empresa')
        
        # Desactivar reglas de seguridad
        self._toggle_security_rules(False)
    
    def _migrate_existing_categories(self):
        """Asignar empresa actual a categorías sin empresa"""
        categories_without_company = self.env['product.category'].sudo().search([
            ('company_id', '=', False)
        ])
        
        if categories_without_company:
            # Asignar la empresa actual a todas las categorías sin empresa
            categories_without_company.write({
                'company_id': self.env.company.id
            })
            
            _logger.info(
                'Migradas %d categorías a la empresa %s',
                len(categories_without_company),
                self.env.company.name
            )
    
    def _toggle_security_rules(self, active):
        """Activar o desactivar reglas de seguridad"""
        rules = [
            'almus_product_category_company.product_category_company_rule',
            'almus_product_category_company.product_category_multi_company_rule'
        ]
        
        for rule_ref in rules:
            rule = self.env.ref(rule_ref, False)
            if rule:
                rule.sudo().active = active
                _logger.info(
                    '%s regla %s',
                    'Activada' if active else 'Desactivada',
                    rule.name
                )