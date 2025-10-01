from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_product_name_extended = fields.Html("Product Name (Extended)")