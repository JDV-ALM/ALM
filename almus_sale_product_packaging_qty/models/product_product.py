from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    packaging_qty = fields.Integer(
        string='Cantidad por Empaque',
        default=1,
        help='Cantidad de unidades que contiene cada empaque del producto',
        tracking=True,
    )


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    packaging_qty = fields.Integer(
        string='Cantidad por Empaque',
        default=1,
        help='Cantidad de unidades que contiene cada empaque del producto',
        tracking=True,
        related='product_variant_ids.packaging_qty',
        readonly=False,
    )