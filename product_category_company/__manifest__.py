{
    'name': 'Product Category Company Filter',
    'version': '18.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Filter product categories by company',
    'description': """
        This module adds company filtering to product categories.
        Each category will belong to a specific company and users
        will only see categories from their current company.
    """,
    'author': 'JDV-ALM',
    'website': 'https://www.almus.dev',
    'depends': ['product', 'base'],
    'data': [
        'security/product_category_security.xml',
        'views/product_category_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}