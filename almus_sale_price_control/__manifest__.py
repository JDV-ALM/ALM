# -*- coding: utf-8 -*-
{
    'name': 'Almus Sale Price Control',
    'summary': 'Control de acceso y gestión de precios en ventas',
    'description': """
        Este módulo proporciona:
        - Control de acceso a listas de precios (solo administradores)
        - Restricción de edición de precios en líneas de venta
        - Selector de lista de precios por línea de orden
    """,
    'author': 'Almus Dev',
    'website': 'https://www.almus.dev',
    'category': 'Sales',
    'version': '18.0.1.0.0',
    'license': 'LGPL-3',
    'depends': ['almus_base', 'sale', 'product'],
    'data': [
        'security/sale_security.xml',
        'views/res_config_settings_views.xml',
        'views/sale_order_views.xml',
        'views/product_pricelist_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}