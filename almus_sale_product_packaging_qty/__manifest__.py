{
    "name": "Almus Sale Product Packaging Quantity",
    "summary": """
        Muestra la cantidad por empaque en el catálogo de productos de ventas
    """,
    "description": """
        Este módulo agrega un campo informativo en la vista de catálogo de productos
        dentro del formulario de ventas para mostrar la cantidad de unidades por empaque.
        
        Características:
        - Campo de solo lectura tipo entero
        - Visible en la vista kanban del catálogo de productos
        - Configurable desde el panel de Almus Dev
    """,
    "license": "LGPL-3",
    "author": "Almus Dev",
    "website": "https://www.almus.dev",
    "category": "Sales",
    "version": "18.0.1.0.0",
    "depends": ["almus_base", "sale", "product", "account"],
    "installable": True,
    "auto_install": False,
    "application": True,
    "data": [
        "security/ir.model.access.csv",
        "views/product_views.xml",
        "views/res_config_settings_views.xml",
    ],
}