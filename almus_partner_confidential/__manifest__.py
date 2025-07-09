{
    'name': 'Almus Partner Confidential Information',
    'summary': 'Gestión de información confidencial de proveedores con control de acceso',
    'description': """
        Este módulo agrega una pestaña de información confidencial en el formulario de contactos
        que solo es visible para usuarios con permisos específicos.
        
        Características principales:
        - Nueva pestaña "Información Confidencial" en contactos
        - Control de visibilidad mediante configuración en panel Almus
        - Campos específicos para proveedores internacionales
        - Control de acceso mediante permisos de usuario
        - Los administradores NO tienen acceso automático
        - Registro de auditoría de cambios
        - Estadísticas de uso en el panel de configuración
        
        Seguridad:
        - La pestaña solo es visible si la funcionalidad está activada Y el usuario tiene permisos
        - Permisos separados para lectura y escritura
        - Los administradores del sistema deben recibir permisos explícitamente
    """,
    'author': 'Almus Dev',
    'website': 'https://www.almus.dev',
    'category': 'Sales/Purchase',
    'version': '18.0.1.0.1',
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