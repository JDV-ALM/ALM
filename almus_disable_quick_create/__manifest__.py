# -*- coding: utf-8 -*-
{
    'name': 'Almus Disable Quick Create',
    'summary': 'Desactiva la creación rápida de contactos y productos en ventas y compras',
    'description': """
        Este módulo permite controlar la creación rápida de registros en los campos Many2one
        de contactos y productos en las aplicaciones de ventas y compras.
        
        Funcionalidades:
        - Desactivar "Crear" para contactos
        - Desactivar "Crear y editar" para contactos
        - Desactivar "Crear" para productos
        - Desactivar "Crear y editar" para productos
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
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
    ],
    'application': True,
    'auto_install': False,
    'installable': True,
}