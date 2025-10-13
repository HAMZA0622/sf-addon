from odoo import models, fields, api

class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    image = fields.Image(
        string="Image",
        help="You can upload an image that will be used as the color of the attribute value.",
        max_width=1024, max_height=1024
    )
    image_1024 = fields.Image(
        string="Image 1024",
        compute="_compute_resized_images",
        max_width=1024, max_height=1024
    )
    image_512 = fields.Image(
        string="Image 512",
        compute="_compute_resized_images",
        max_width=512, max_height=512
    )
    image_256 = fields.Image(
        string="Image 256",
        compute="_compute_resized_images",
        max_width=256, max_height=256
    )

    @api.depends('image')
    def _compute_resized_images(self):
        for record in self:
            record.image_1024 = record.image
            record.image_512 = record.image
            record.image_256 = record.image
