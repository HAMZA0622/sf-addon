from odoo import models, fields, api
from odoo.http import request

class WebsitePage(models.Model):
    _inherit = 'website.page'

    ds_edit_link = fields.Html(string="Edit", compute='_compute_ds_edit_link', sanitize=False)

    @api.depends('website_url')
    def _compute_ds_edit_link(self):
        base_url = request.httprequest.host_url.rstrip('/') if request and request.httprequest else ''
        
        for record in self:
            if record.website_url:
                url = f'{base_url}/odoo/action-website.website_preview?path={record.website_url}'
                # Open in same window — no target attribute
                record.ds_edit_link = f'<a href="{url}" onclick="event.stopPropagation();">Edit</a>'
            else:
                record.ds_edit_link = ''
