from odoo import models, api

class AlmusAppConfig(models.Model):
    _inherit = 'almus.app.config'
    
    def _post_enable_actions(self):
        """Acciones específicas al activar el módulo"""
        super()._post_enable_actions()
        
        if self.name == 'product_category_company':
            # Migrar categorías existentes
            self._migrate_existing_categories()
            # Activar reglas de seguridad
            self._enable_security_rules()
            # Actualizar contexto de vistas
            self._update_view_context()
    
    def _post_disable_actions(self):
        """Acciones específicas al desactivar el módulo"""
        super()._post_disable_actions()
        
        if self.name == 'product_category_company':
            # Desactivar reglas de seguridad
            self._disable_security_rules()
            # Limpiar datos si está en contexto
            if self.env.context.get('almus_cleanup_on_disable'):
                self._cleanup_category_companies()
    
    def _migrate_existing_categories(self):
        """Asignar empresa actual a categorías sin empresa"""
        categories_without_company = self.env['product.category'].search([
            ('company_id', '=', False)
        ])
        
        if categories_without_company:
            # Asignar la empresa actual a todas las categorías sin empresa
            categories_without_company.write({
                'company_id': self.env.company.id
            })
            
            # Log de migración
            self.env['ir.logging'].create({
                'name': 'almus.product_category_company',
                'type': 'info',
                'message': f'Migradas {len(categories_without_company)} categorías a la empresa {self.env.company.name}',
                'path': 'almus_product_category_company',
                'func': '_migrate_existing_categories',
                'line': 0,
            })
    
    def _enable_security_rules(self):
        """Activar reglas de seguridad del módulo"""
        rules_to_enable = [
            'almus_product_category_company.product_category_company_rule',
            'almus_product_category_company.product_category_multi_company_rule'
        ]
        
        for rule_ref in rules_to_enable:
            rule = self.env.ref(rule_ref, False)
            if rule and not rule.active:
                rule.active = True
    
    def _disable_security_rules(self):
        """Desactivar reglas de seguridad del módulo"""
        rules_to_disable = [
            'almus_product_category_company.product_category_company_rule',
            'almus_product_category_company.product_category_multi_company_rule'
        ]
        
        for rule_ref in rules_to_disable:
            rule = self.env.ref(rule_ref, False)
            if rule and rule.active:
                rule.active = False
    
    def _cleanup_category_companies(self):
        """Opcional: Limpiar company_id de las categorías al desactivar"""
        # Solo ejecutar si explícitamente se solicita
        if self.env.context.get('almus_force_cleanup'):
            categories_with_company = self.env['product.category'].search([
                ('company_id', '!=', False)
            ])
            categories_with_company.write({'company_id': False})
    
    def _update_view_context(self):
        """Actualizar contexto en las vistas para indicar que está activo"""
        # Esto permite que las vistas sepan si mostrar campos relacionados
        self.env['ir.config_parameter'].sudo().set_param(
            'almus_product_category_company.enabled', 
            'True'
        )