{
    'name': 'Almus Product Category per Company',
    'summary': 'Restringe categorías de producto por empresa',
    'description': '''
        Modifica el comportamiento estándar de Odoo para que las categorías
        de producto sean específicas por empresa en lugar de globales.
        
        Características:
        - Agrega campo company_id a product.category
        - Aplica reglas de seguridad multi-company
        - Migración automática de categorías existentes
        - Se puede activar/desactivar desde Configuración → Almus Dev
        
        Activar si necesitas que cada empresa tenga sus propias categorías
        de productos independientes.
    ''',
    'author': 'Almus Dev',
    'website': 'https://www.almus.dev',
    'category': 'Inventory',
    'version': '18.0.1.0.0',
    'license': 'LGPL-3',
    'depends': ['almus_base', 'product'],
    'application': True,
    'auto_install': False,
    'data': [
        'security/product_category_security.xml',
        'views/res_config_settings_views.xml',
        'views/product_category_views.xml',
    ],
}