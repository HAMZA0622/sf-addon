from odoo import _, api, fields, models

class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    image = fields.Image(
        string="Image",
        max_width=1024, max_height=1024)
    show_in_finishes = fields.Boolean(
        string="Show in Finishes",
        default=False
    )
