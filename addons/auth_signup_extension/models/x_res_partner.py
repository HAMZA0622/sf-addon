from odoo import fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Custom fields for additional user information
    x_dscape_sales_rep = fields.Char(string='Sales Representative')
    x_dscape_occupation = fields.Char(string='Occupation')
    x_dscape_subscribe = fields.Boolean(string="Subscribe to Newsletter", default=True)
    x_dscape_privacy_policy = fields.Boolean(string='Privacy Policy Accepted')