from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request

class CustomCustomerPortal(CustomerPortal):

    @http.route(['/my'], type='http', auth='user', website=True)
    def custom_account_access(self, **kw):
        custom_url = '/account-access'

        if custom_url:
            return request.redirect(custom_url)

        return super().my_home(**kw)
