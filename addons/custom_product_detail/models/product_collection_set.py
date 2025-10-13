from odoo import _, api, fields, models

class ProductCollectionSet(models.Model):
    _name = 'product.collection.set'
    _inherit = ['mail.thread']
    _description = "Product Collection Set"
    _rec_name = 'name'

    name = fields.Char()
    description = fields.Text()
    sequence = fields.Integer(string="Sequence", help="Determine the display order", index=True, default=20)
    image = fields.Image(string="Image",max_width=1024, max_height=1024)
    website_link = fields.Char(compute="_compute_website_link", store=True)
    hide_image = fields.Boolean(default=True)
    collection_pdf = fields.Binary(attachment=True, string='Collection Attachment')
    related_collection_pdf_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Related Collection PDF Attachment",
        copy=False,
        compute="_compute_related_collection_pdf_attachment_id",
        store=True,
    )
    product_template_ids = fields.One2many('product.template','product_collection_id')

    # New: Parent Collection (self-referencing)
    parent_id = fields.Many2one(
        'product.collection.set',
        string='Parent Collection',
        help='The parent collection this collection belongs to.'
    )
    child_ids = fields.One2many(
        'product.collection.set',
        'parent_id',
        string='Sub Collections'
    )


    @api.depends('name')
    def _compute_website_link(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for rec in self:
            rec.website_link = f"/collections/{rec.id}"


    @api.depends("collection_pdf")
    def _compute_related_collection_pdf_attachment_id(self):
        for record in self:
            if record.collection_pdf:
                attachment = self.env["ir.attachment"].search(
                    [
                        ("res_model", "=", "product.collection.set"),
                        ("res_id", "=", record.id),
                        ("res_field", "=", "collection_pdf"),
                    ],
                    limit=1,
                )
                if attachment and not attachment.public:
                    attachment.sudo().write({"public": True})
                record.related_collection_pdf_attachment_id = attachment
            else:
                record.related_collection_pdf_attachment_id = False

    def action_go_to_website(self):
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return {
            'type': 'ir.actions.act_url',
            'url': f"{base_url}/collections/{self.id}",
            'target': 'self',
        }

