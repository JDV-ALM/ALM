from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    almus_show_packaging_qty = fields.Boolean(
        string='Mostrar Cantidad por Empaque',
        config_parameter='almus_sale_product_packaging_qty.show_packaging_qty',
        default=True,
        help='Muestra la cantidad por empaque en el catálogo de productos de ventas'
    )