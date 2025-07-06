from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install')
class TestAlmusProductCategoryCompany(TransactionCase):
    
    def setUp(self):
        super().setUp()
        
        # Crear empresas de prueba
        self.company_1 = self.env.company
        self.company_2 = self.env['res.company'].create({
            'name': 'Test Company 2',
            'currency_id': self.env.ref('base.USD').id,
        })
        self.company_3 = self.env['res.company'].create({
            'name': 'Test Company 3',
            'currency_id': self.env.ref('base.USD').id,
        })
        
        # Usuario multi-empresa
        self.multi_company_user = self.env['res.users'].create({
            'name': 'Multi Company User',
            'login': 'multi_company_user',
            'company_id': self.company_1.id,
            'company_ids': [(6, 0, [self.company_1.id, self.company_2.id])],
            'groups_id': [(6, 0, [
                self.env.ref('base.group_user').id,
                self.env.ref('base.group_multi_company').id
            ])]
        })
        
        # Configuración
        self.config_param = self.env['ir.config_parameter'].sudo()
        
    def _enable_feature(self):
        """Activar la funcionalidad"""
        settings = self.env['res.config.settings'].create({
            'almus_product_category_company_enabled': True
        })
        settings.set_values()
        
    def _disable_feature(self):
        """Desactivar la funcionalidad"""
        settings = self.env['res.config.settings'].create({
            'almus_product_category_company_enabled': False
        })
        settings.set_values()
    
    def test_01_feature_disabled_by_default(self):
        """Verificar que la funcionalidad está deshabilitada por defecto"""
        param_value = self.config_param.get_param('almus_product_category_company.enabled', 'False')
        self.assertEqual(param_value, 'False')
        
        # Crear categoría sin la funcionalidad habilitada
        category = self.env['product.category'].create({
            'name': 'Test Category Disabled'
        })
        
        # No debería tener company_id asignado
        self.assertFalse(category.company_id)
    
    def test_02_enable_feature(self):
        """Probar activación de la funcionalidad"""
        # Activar la funcionalidad
        self._enable_feature()
        
        # Verificar parámetro
        param_value = self.config_param.get_param('almus_product_category_company.enabled')
        self.assertEqual(param_value, 'True')
        
        # Verificar que las reglas de seguridad se activaron
        rule1 = self.env.ref('almus_product_category_company.product_category_company_rule')
        rule2 = self.env.ref('almus_product_category_company.product_category_multi_company_rule')
        self.assertTrue(rule1.active)
        self.assertTrue(rule2.active)
    
    def test_03_category_with_company_auto_assign(self):
        """Verificar que las categorías se crean con empresa automáticamente"""
        self._enable_feature()
        
        # Crear categoría sin especificar company_id
        category = self.env['product.category'].create({
            'name': 'Test Category Auto Company'
        })
        
        # Debe tener la empresa actual asignada
        self.assertEqual(category.company_id, self.company_1)
    
    def test_04_category_with_specific_company(self):
        """Verificar creación con empresa específica"""
        self._enable_feature()
        
        # Crear categoría con empresa específica
        category = self.env['product.category'].create({
            'name': 'Test Category Company 2',
            'company_id': self.company_2.id
        })
        
        self.assertEqual(category.company_id, self.company_2)
    
    def test_05_multi_company_isolation(self):
        """Verificar aislamiento entre empresas"""
        self._enable_feature()
        
        # Crear categorías en diferentes empresas
        cat_company1 = self.env['product.category'].create({
            'name': 'Category Company 1',
            'company_id': self.company_1.id
        })
        
        cat_company2 = self.env['product.category'].create({
            'name': 'Category Company 2',
            'company_id': self.company_2.id
        })
        
        cat_shared = self.env['product.category'].create({
            'name': 'Shared Category',
            'company_id': False
        })
        
        # Cambiar a usuario de company_1
        categories = self.env['product.category'].with_user(self.multi_company_user).search([])
        
        # Debe ver categorías de company_1, company_2 (multi-empresa) y compartidas
        self.assertIn(cat_company1, categories)
        self.assertIn(cat_company2, categories)
        self.assertIn(cat_shared, categories)
        
        # Usuario de una sola empresa (company_3)
        single_company_user = self.env['res.users'].create({
            'name': 'Single Company User',
            'login': 'single_company_user',
            'company_id': self.company_3.id,
            'company_ids': [(6, 0, [self.company_3.id])],
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])]
        })
        
        # No debe ver categorías de otras empresas cuando las reglas están activas
        categories_single = self.env['product.category'].with_user(single_company_user).search([])
        self.assertNotIn(cat_company1, categories_single)
        self.assertNotIn(cat_company2, categories_single)
        self.assertIn(cat_shared, categories_single)  # Pero sí las compartidas
    
    def test_06_parent_category_validation(self):
        """Verificar validación de categoría padre en la misma empresa"""
        self._enable_feature()
        
        # Crear categoría padre
        parent_cat = self.env['product.category'].create({
            'name': 'Parent Category',
            'company_id': self.company_1.id
        })
        
        # Crear categoría hija en la misma empresa - debe funcionar
        child_cat = self.env['product.category'].create({
            'name': 'Child Category',
            'parent_id': parent_cat.id,
            'company_id': self.company_1.id
        })
        self.assertEqual(child_cat.parent_id, parent_cat)
        
        # Intentar crear categoría hija en diferente empresa - debe fallar
        with self.assertRaises(ValidationError):
            self.env['product.category'].create({
                'name': 'Child Different Company',
                'parent_id': parent_cat.id,
                'company_id': self.company_2.id
            })
    
    def test_07_migration_existing_categories(self):
        """Verificar migración de categorías existentes"""
        # Crear categorías sin empresa (simulando datos existentes)
        cat1 = self.env['product.category'].create({'name': 'Existing Cat 1'})
        cat2 = self.env['product.category'].create({'name': 'Existing Cat 2'})
        
        self.assertFalse(cat1.company_id)
        self.assertFalse(cat2.company_id)
        
        # Activar la funcionalidad (esto ejecuta la migración)
        self._enable_feature()
        
        # Verificar que se asignó la empresa actual
        cat1.invalidate_recordset()
        cat2.invalidate_recordset()
        self.assertEqual(cat1.company_id, self.company_1)
        self.assertEqual(cat2.company_id, self.company_1)
    
    def test_08_disable_feature(self):
        """Probar desactivación de la funcionalidad"""
        # Primero activar
        self._enable_feature()
        
        # Desactivar
        self._disable_feature()
        
        # Verificar parámetro
        param_value = self.config_param.get_param('almus_product_category_company.enabled')
        self.assertEqual(param_value, 'False')
        
        # Verificar que las reglas se desactivaron
        rule1 = self.env.ref('almus_product_category_company.product_category_company_rule')
        rule2 = self.env.ref('almus_product_category_company.product_category_multi_company_rule')
        self.assertFalse(rule1.active)
        self.assertFalse(rule2.active)
    
    def test_09_search_method_filtering(self):
        """Verificar que el método _search filtra correctamente"""
        self._enable_feature()
        
        # Crear categorías para diferentes empresas
        cat1 = self.env['product.category'].create({
            'name': 'Search Test Cat 1',
            'company_id': self.company_1.id
        })
        cat2 = self.env['product.category'].create({
            'name': 'Search Test Cat 2',
            'company_id': self.company_2.id
        })
        
        # Buscar con contexto de empresa específica
        ProductCategory = self.env['product.category']
        
        # Como company_1
        self.env.company = self.company_1
        search_results = ProductCategory.search([])
        self.assertIn(cat1, search_results)
        
        # Como company_2
        self.env.company = self.company_2
        search_results = ProductCategory.search([])
        self.assertIn(cat2, search_results)
    
    def test_10_display_name_multi_company(self):
        """Verificar que el display_name muestra la empresa en contexto multi-empresa"""
        self._enable_feature()
        
        category = self.env['product.category'].create({
            'name': 'Display Name Test',
            'company_id': self.company_1.id
        })
        
        # Usuario multi-empresa debe ver el nombre con la empresa
        category_multi = category.with_user(self.multi_company_user)
        display_name = category_multi.display_name
        self.assertIn(self.company_1.name, display_name)
        self.assertIn('Display Name Test', display_name)