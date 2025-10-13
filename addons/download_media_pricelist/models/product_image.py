# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductImage(models.Model):
    _inherit = "product.image"

    related_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Related Attachment",
        copy=False,
        compute="_compute_related_attachment_id",
        store=True,
    )

    @api.depends("image_1920")
    def _compute_related_attachment_id(self):
        for image in self:
            if image.image_1920:
                attachment = self.env["ir.attachment"].search(
                    [
                        ("res_model", "=", "product.image"),
                        ("res_id", "=", image.id),
                        ("res_field", "=", "image_1920"),
                    ],
                    limit=1,
                )
                image.related_attachment_id = attachment
            else:
                image.related_attachment_id = False
