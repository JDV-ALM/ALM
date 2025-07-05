{
    "name": "Almus Base",
    "summary": """
        Módulo base para la gestión centralizada de aplicaciones Almus Dev
    """,
    "description": """
        Este módulo proporciona:
        - Gestión centralizada de aplicaciones Almus
        - Panel de configuración unificado
        - Sistema de activación/desactivación de funcionalidades
    """,
    "license": "LGPL-3",
    "author": "Almus Dev",
    "website": "https://www.almus.dev",
    "category": "Technical",
    "version": "18.0.1.0.0",
    "depends": ["base"],
    "installable": True,
    "auto_install": False,
    "application": False,  # No debe ser aplicación si solo aparece en configuración
    "data": [
        "security/ir.model.access.csv",
        "views/almus_app_config_views.xml",
        "views/res_config_settings_views.xml",
    ],
}