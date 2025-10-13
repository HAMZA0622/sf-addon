from odoo import api, models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    d_img_1 = fields.Image("Image 1")
    d_img_2 = fields.Image("Image 2")
    is_multiple_dimension = fields.Boolean(default=False)
    dimension_value_lines = fields.One2many('dimension.value.line', 'product_template_id', copy=True)
    hide_dimension = fields.Boolean(string="Hide Dimension", default=False)
    dimension_set_ids = fields.One2many(
        'dimension.set', 'product_template_id', string="Dimension Sets", copy=True
    )
    spec_pdf = fields.Binary(attachment=True, string='Spec Sheet Attachment')
    related_spec_pdf_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Related Spec PDF Attachment",
        copy=False,
        compute="_compute_related_spec_pdf_attachment_id",
        store=True,
    )
    atlantic_collection_pdf = fields.Binary(attachment=True, string='Collection Sheet Attachment')
    related_atlantic_collection_pdf_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Related Atlantic Collection PDF Attachment",
        copy=False,
        compute="_compute_related_atlantic_collection_pdf_attachment_id",
        store=True,
    )
    product_collection_id = fields.Many2one('product.collection.set', 'Product Collection')

    # Flags
    is_quick_ship = fields.Boolean(default=False)
    is_ready_to_ship = fields.Boolean(default=False, string="Is Ready to Ship")
    is_made_in_usa = fields.Boolean(default=False, string="Is Made in USA")

    # Dimensions
    # Width, Length, Depth, Height, Thickness, Arm Height, Seat Width, Seat Depth, Seat Height, Diameter, Weight, Seat Diameter and Stackability
    d_width = fields.Char('Width')
    d_length = fields.Char('Length')
    d_depth = fields.Char('Depth')
    d_height = fields.Char('Height')
    d_thickness = fields.Char('Thickness')
    d_arm_height = fields.Char('Arm Height')
    d_seat_width = fields.Char('Seat Width')
    d_seat_depth = fields.Char('Seat Depth')
    d_seat_height = fields.Char('Seat Height')
    d_diameter = fields.Char('Diameter')
    d_weight = fields.Char('Weight')
    d_stackability = fields.Char('Stackability')
    d_seat_diameter = fields.Char('Seat Diameter')
    show_table_sheet = fields.Boolean(string="Show Table Sheet", default=False)
    table_sheet_link = fields.Char(string="Table Sheet Link")

    @api.depends("spec_pdf")
    def _compute_related_spec_pdf_attachment_id(self):
        for record in self:
            if record.spec_pdf:
                attachment = self.env["ir.attachment"].search(
                    [
                        ("res_model", "=", "product.template"),
                        ("res_id", "=", record.id),
                        ("res_field", "=", "spec_pdf"),
                    ],
                    limit=1,
                )
                if attachment and not attachment.public:
                    attachment.sudo().write({"public": True})
                record.related_spec_pdf_attachment_id = attachment
            else:
                record.related_spec_pdf_attachment_id = False

    @api.depends("atlantic_collection_pdf")
    def _compute_related_atlantic_collection_pdf_attachment_id(self):
        for record in self:
            if record.atlantic_collection_pdf:
                attachment = self.env["ir.attachment"].search(
                    [
                        ("res_model", "=", "product.template"),
                        ("res_id", "=", record.id),
                        ("res_field", "=", "atlantic_collection_pdf"),
                    ],
                    limit=1,
                )
                record.related_atlantic_collection_pdf_attachment_id = attachment
            else:
                record.related_atlantic_collection_pdf_attachment_id = False
    
    @api.model
    def _search_get_detail(self, website, order, options):
        if options and 'displayDetail' in options:
            options['displayDetail'] = False
        return super(ProductTemplate, self)._search_get_detail(website, order, options)


class DimensionSet(models.Model):
    _name = "dimension.set"
    _description = "Dimension Set"

    name = fields.Char('Dimension Set', required=True)
    sequence = fields.Integer('Sequence', default=10)
    d_img_1 = fields.Image("Image 1")
    d_img_2 = fields.Image("Image 2")
    product_template_id = fields.Many2one('product.template')
    dimension_value_lines = fields.One2many('dimension.value.line', 'dimension_set_id')
    d_width = fields.Char('Width')
    d_length = fields.Char('Length')
    d_depth = fields.Char('Depth')
    d_height = fields.Char('Height')
    d_thickness = fields.Char('Thickness')
    d_arm_height = fields.Char('Arm Height')
    d_seat_width = fields.Char('Seat Width')
    d_seat_depth = fields.Char('Seat Depth')
    d_seat_height = fields.Char('Seat Height')
    d_diameter = fields.Char('Diameter')
    d_weight = fields.Char('Weight')
    d_stackability = fields.Char('Stackability')
    d_seat_diameter = fields.Char('Seat Diameter')
    show_table_sheet = fields.Boolean(string="Show Table Sheet", default=False)
    table_sheet_link = fields.Char(string="Table Sheet Link")


class DimensionValueLine(models.Model):
    _name = "dimension.value.line"
    _description = "Dimension Value Line"

    dimension_type_id = fields.Many2one('dimension.type','Dimension Type')
    dimension_value = fields.Char('Dimension Value')
    dimension_set_id = fields.Many2one('dimension.set')
    product_template_id = fields.Many2one('product.template')


class DimensionType(models.Model):
    _name = "dimension.type"
    _description = "Dimension Type"
    _rec_name = 'name'

    name = fields.Char('Name', required=True)
