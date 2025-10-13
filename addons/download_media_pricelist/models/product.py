# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    related_image_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Related Attachment",
        copy=False,
        compute="_compute_related_image_attachment_id",
        store=True,
    )

    @api.depends("image_1920")
    def _compute_related_image_attachment_id(self):
        for template in self:
            if template.image_1920:
                attachment = self.env["ir.attachment"].search(
                    [
                        ("res_model", "=", "product.template"),
                        ("res_id", "=", template.id),
                        ("res_field", "=", "image_1920")
                    ],
                    limit=1,
                )
                template.related_image_attachment_id = attachment
            else:
                template.related_image_attachment_id = False
