# -*- coding: utf-8 -*-
{
    'name': 'Almus Bank Tesote',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'Integración bancaria Tesote para importación automática de transacciones',
    'description': """
Almus Bank Tesote - Integración 
===============================

Módulo de integración con Tesote API v2.0.0:

Características principales:
----------------------------
* Sincronización automática de cuentas bancarias desde Tesote
* Mapeo simple de cuentas a diarios contables
* Importación incremental de transacciones con protección anti-bucles
* Generación automática de extractos bancarios
* Configuración independiente por compañía
* Soporte para webhooks

Protecciones de seguridad:
--------------------------
* Timeouts cortos (10 segundos máximo)
* Límite de reintentos (máximo 2)
* Rate limiting interno
* Límite de transacciones por sincronización
* Validación de datos antes de procesar

Desarrollado por: Almus Dev (JDV-ALM)
Sitio web: www.almus.dev
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
        
        # Data
        'data/ir_cron.xml',
        
        # Views
        'views/tesote_config_views.xml',
        'views/tesote_account_views.xml',
        'views/menu_views.xml',
    ],
    
    'external_dependencies': {
        'python': ['requests'],
    },
    
    'installable': True,
    'application': False,
    'auto_install': False,
    
    
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}