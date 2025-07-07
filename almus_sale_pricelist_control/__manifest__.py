# -*- coding: utf-8 -*-
{
    'name': 'Almus Sale Pricelist Control',
    'summary': 'Control de edición de listas de precios y precios por línea en órdenes de venta',
    'description': """
        Este módulo proporciona:
        - Control de edición de listas de precios solo para administradores de ventas
        - Bloqueo de modificación de precios en líneas de venta
        - Selección de lista de precios por línea de orden de venta
    """,
    'author': 'Almus Dev',
    'website': 'https://www.almus.dev',
    'category': 'Sales',
    'version': '18.0.1.0.0',
    'license': 'LGPL-3',
    'depends': [
        'almus_base',
        'sale_management',
        'product',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/sale_order_views.xml',
        'views/product_pricelist_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}