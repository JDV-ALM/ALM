{
    'name': 'Almus Información Confidencial de Contactos',
    'summary': 'Gestiona información confidencial de proveedores y contactos con control de acceso',
    'description': """
        Este módulo agrega una pestaña de información confidencial en los contactos que solo
        es visible para usuarios con permisos específicos. Permite proteger datos sensibles como:
        - Información de contacto internacional (WeChat, WhatsApp)
        - Condiciones comerciales y términos de pago especiales
        - Información bancaria y de crédito
        - Notas internas confidenciales
        
        La funcionalidad puede ser activada/desactivada desde la configuración de Almus.
    """,
    'author': 'Almus Dev',
    'website': 'https://www.almus.dev',
    'category': 'Sales/CRM',
    'version': '18.0.1.0.0',
    'license': 'LGPL-3',
    'depends': [
        'almus_base',
        'base',
        'contacts',
    ],
    'data': [
        # Seguridad
        'security/almus_partner_confidential_security.xml',
        'security/ir.model.access.csv',
        
        # Vistas
        'views/res_config_settings_views.xml',
        'views/res_partner_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}