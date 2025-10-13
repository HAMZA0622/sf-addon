from odoo import models, fields, api

class ProductTemplateAttributeValue(models.Model):
    _inherit = 'product.template.attribute.value'

    image_1024 = fields.Image(related='product_attribute_value_id.image_1024')
    image_512 = fields.Image(related='product_attribute_value_id.image_512')
    image_256 = fields.Image(related='product_attribute_value_id.image_256')