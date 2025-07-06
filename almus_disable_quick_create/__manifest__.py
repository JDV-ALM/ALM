# -*- coding: utf-8 -*-
{
    'name': 'Almus Disable Quick Create',
    'summary': 'Controla la creación rápida de contactos y productos en ventas y compras',
    'description': """
        Este módulo permite deshabilitar la creación rápida de contactos y productos
        desde los formularios de órdenes de venta y compra, obligando a los usuarios
        a crear estos registros desde sus respectivos menús.
    """,
    'author': 'Almus Dev',
    'website': 'https://www.almus.dev',
    'category': 'Sales/Sales',
    'version': '18.0.1.0.0',
    'license': 'LGPL-3',
    'depends': [
        'almus_base',
        'sale',
        'purchase',
    ],
    'data': [
        'views/res_config_settings_views.xml',
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}