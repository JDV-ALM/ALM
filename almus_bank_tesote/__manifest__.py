# -*- coding: utf-8 -*-
{
    'name': 'Almus Bank Tesote',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Tesote Bank Integration for automatic transaction import',
    'description': """
Almus Bank Tesote Integration
==============================

This module integrates Tesote API v2.0.0 for automatic bank transaction import:
- Automatic bank account synchronization from Tesote
- Manual mapping of bank accounts to accounting journals
- Incremental transaction synchronization
- Automatic bank statement generation
- Webhook support for real-time notifications

Developed by Almus Dev (JDV-ALM)
Website: www.almus.dev
    """,
    'author': 'Almus Dev (JDV-ALM)',
    'website': 'https://www.almus.dev',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'account_accountant',
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        'security/tesote_security.xml',
        
        # Data
        'data/ir_cron.xml',
        
        # Views
        'views/tesote_account_views.xml',
        'views/tesote_webhook_views.xml',
        'views/res_config_settings_views.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'almus_bank_tesote/static/src/js/tesote_widget.js',
        ],
    },
    'external_dependencies': {
        'python': ['requests', 'dateutil'],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
