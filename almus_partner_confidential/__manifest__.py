{
    'name': 'Almus Partner Confidential Information',
    'summary': 'Gestión de información confidencial de proveedores con control de acceso',
    'description': """
        Este módulo agrega una pestaña de información confidencial en el formulario de contactos
        que solo es visible para usuarios con permisos específicos.
        
        Características principales:
        - Nueva pestaña "Información Confidencial" en contactos
        - Campos específicos para proveedores internacionales
        - Control de acceso mediante permisos de usuario
        - Configuración desde el panel Almus
        - Registro de auditoría de cambios
    """,
    'author': 'Almus Dev',
    'website': 'https://www.almus.dev',
    'category': 'Sales/Purchase',
    'version': '18.0.1.0.0',
    'license': 'LGPL-3',
    'depends': [
        'almus_base',
        'base',
        'contacts',
    ],
    'data': [
        'security/partner_confidential_security.xml',
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}