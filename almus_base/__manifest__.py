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
        - Registro de cambios de configuración
    """,
    "license": "LGPL-3",
    "author": "Almus Dev",
    "website": "https://www.almus.dev",
    "category": "Technical",
    "version": "18.0.1.0.0",
    "depends": ["base", "web"],
    "auto_install": False,
    "application": True,
    "data": [
        "security/almus_base_security.xml",
        "security/ir.model.access.csv",
        "data/almus_app_config_data.xml",
        "views/almus_app_config_views.xml",
        "views/res_config_settings_views.xml",
        "views/menu_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "almus_base/static/src/scss/almus_base.scss",
        ],
    },
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
}