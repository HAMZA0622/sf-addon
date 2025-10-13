# controllers/auth_signup.py
from odoo import http, _
from odoo.http import request
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.exceptions import UserError
import werkzeug
import logging
from markupsafe import Markup
from werkzeug.urls import url_encode

_logger = logging.getLogger(__name__)

class AuthSignupHomeInherit(AuthSignupHome):

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                if not request.env['ir.http']._verify_request_recaptcha_token('signup'):
                    raise UserError(_("Suspicious activity detected by Google reCaptcha."))

                self.do_signup(qcontext)

                # Set user to public if they were not signed in by do_signup
                # (mfa enabled)
                if request.session.uid is None:
                    public_user = request.env.ref('base.public_user')
                    request.update_env(user=public_user)

                # Send an account creation confirmation email
                User = request.env['res.users']
                user_sudo = User.sudo().search(
                    User._get_login_domain(qcontext.get('login')), order=User._get_login_order(), limit=1
                )
                template_signup = request.env.ref('auth_signup_extension.mail_template_decoscape_user_signup', raise_if_not_found=False)
                template_approval = request.env.ref('auth_signup_extension.mail_template_decoscape_approval', raise_if_not_found=False)

                if user_sudo and template_signup:
                    template_signup.sudo().send_mail(user_sudo.id, force_send=True)

                    admin_group = request.env.ref('auth_signup_extension.group_user_account_approval', raise_if_not_found=False)
                    if not admin_group:
                        _logger.error("Admin group not found!")
                    else:
                        admin_users = request.env['res.users'].sudo().search([
                            ('groups_id', 'in', [admin_group.id]),
                            ('email', '!=', False)
                        ])

                        if not admin_users:
                            _logger.warning("No admin users found in the User Account Approval group!")
                        elif not template_approval:
                            _logger.error("Approval email template not found!")
                        else:
                            for admin in admin_users:
                                base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                                activation_link = f"{base_url}/odoo/users/{user_sudo.id}"
                                theme_color = request.env['ir.config_parameter'].sudo().get_param('web.color.primary', '#875A7B')
                                _logger.info("New User Context: ID=%s, Name=%s, Email=%s", user_sudo.id, user_sudo.name, user_sudo.email)
                                _logger.info("New User Activation Link: %s", activation_link)

                                template_approval.with_context(
                                    new_user_email=user_sudo.email,
                                    first_name=qcontext.get('first_name', ''),
                                    last_name=qcontext.get('last_name', ''),
                                    city=qcontext.get('city', ''),
                                    phone=qcontext.get('phone', ''),
                                    sales_rep=qcontext.get('x_dscape_sales_rep', ''),
                                    occupation=qcontext.get('x_dscape_occupation', ''),
                                    other_occupation=qcontext.get('x_dscape_other_occupation', ''),
                                    company_name=qcontext.get('company_name', ''),
                                    street=qcontext.get('street', ''),
                                    street2=qcontext.get('street2', ''),
                                    zip=qcontext.get('zip', ''),
                                    subscribe="Yes" if qcontext.get('x_dscape_subscribe') == 'on' else "No",
                                    privacy_policy="Accepted" if qcontext.get('x_dscape_privacy_policy') == 'on' else "Not Accepted",
                                    country_name=qcontext.get('country_name', ''),
                                    state_name=qcontext.get('state_name', ''),
                                    activation_link=activation_link,
                                    theme_color=theme_color
                                ).sudo().send_mail(admin.id, force_send=True)

                user_rec = request.env['res.users'].sudo().search([('login', '=', qcontext.get('login'))], limit=1)
                if user_rec:
                    user_rec.write({'active': False})

                msg = _("Thank you for signing up. Your account is under review and will be approved within 24 hours.")
                return request.redirect('/web/login?' + url_encode({'message': msg}))
            except UserError as e:
                qcontext['error'] = e.args[0]
            except (Exception, AssertionError) as e:
                _logger.warning("%s", e)
                qcontext['error'] = _("Could not create a new account.") + Markup('<br/>') + str(e)

        elif 'signup_email' in qcontext:
            user = request.env['res.users'].sudo().search([('email', '=', qcontext.get('signup_email')), ('state', '!=', 'new')], limit=1)
            if user:
                return request.redirect('/web/login?%s' % url_encode({'login': user.login, 'redirect': '/web'}))

        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response

    def do_signup(self, qcontext):
        """
        Override do_signup to create the user with active=False
        and avoid auto-login.
        """
        values = self._prepare_signup_values(qcontext)


        # Ensure a 'name' value is provided.
        if not values.get('name'):
            values['name'] = qcontext.get('name') or qcontext.get('company_name') or "New User"

        # Create the user and partner record without logging the user in.
        self._signup_with_values_no_login(qcontext.get('token'), values)
        request.env.cr.commit()

    def _signup_with_values_no_login(self, token, values):
        
        login, password = request.env['res.users'].sudo().signup(values, token) 
        request.env.cr.commit()
        # Force the created user to be inactive.
        """  """

    def get_auth_signup_qcontext(self):
        qcontext = super(AuthSignupHomeInherit, self).get_auth_signup_qcontext()

        # Fetch countries and states for form dropdowns.
        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])

        # Define allowed fields, including custom fields.
        allowed_fields = [
            'phone', 'street', 'street2', 'city', 'zip',
            'country_id', 'state_id', 'company_name',
            'x_dscape_sales_rep', 'x_dscape_occupation',
            'x_dscape_subscribe', 'x_dscape_privacy_policy',
            'x_dscape_other_occupation'
        ]

        qcontext.update({
            k: v for k, v in request.params.items() if k in allowed_fields
        })

        qcontext.update({
            'countries': countries,
            'states': states
        })

        # Fetch first_name and last_name
        qcontext['first_name'] = request.params.get('first_name', '')
        qcontext['last_name'] = request.params.get('last_name', '')

        # Fetch country and state names if IDs are provided
        country_id = request.params.get('country_id')
        state_id = request.params.get('state_id')

        qcontext['country_name'] = request.env['res.country'].sudo().browse(int(country_id)).name if country_id and country_id.isdigit() else ''
        qcontext['state_name'] = request.env['res.country.state'].sudo().browse(int(state_id)).name if state_id and state_id.isdigit() else ''

        return qcontext

    def _prepare_signup_values(self, qcontext):
        values = super(AuthSignupHomeInherit, self)._prepare_signup_values(qcontext)

        allowed_fields = [
            'phone', 'street', 'street2', 'city', 'zip',
            'country_id', 'state_id', 'company_name',
            'x_dscape_sales_rep', 'x_dscape_occupation',
            'x_dscape_other_occupation'
        ]

        partner_fields = request.env['res.partner']._fields

        values.update({
            key: qcontext.get(key)
            for key in allowed_fields
            if key in qcontext and key in partner_fields
        })

        # If the user selected "other" for occupation, override with the provided value.
        if qcontext.get('x_dscape_occupation') == 'other':
            values['x_dscape_occupation'] = qcontext.get('x_dscape_other_occupation') or ''

        # Handle custom checkbox values.
        if 'x_dscape_subscribe' in partner_fields:
            values['x_dscape_subscribe'] = qcontext.get('x_dscape_subscribe') == 'on'
        if 'x_dscape_privacy_policy' in partner_fields:
            values['x_dscape_privacy_policy'] = qcontext.get('x_dscape_privacy_policy') == 'on'

        # Convert country and state IDs to integers if provided.
        if 'country_id' in values and values['country_id']:
            try:
                values['country_id'] = int(values['country_id'])
            except ValueError:
                values['country_id'] = False
        if 'state_id' in values and values['state_id']:
            try:
                values['state_id'] = int(values['state_id'])
            except ValueError:
                values['state_id'] = False

        return values
    

    def send_account_approval_email_to_admins(self, user_sudo):
        """Send account approval request email to all members of the admin group."""
        admin_group = request.env.ref('auth_signup_extension.group_user_account_approval', raise_if_not_found=False)
        
        if not admin_group:
            _logger.error("Admin group not found!")
            return
        
        admin_users = request.env['res.users'].sudo().search([('groups_id', 'in', [admin_group.id]), ('email', '!=', False)])
        if not admin_users:
            _logger.warning("No admin users found in the User Account Approval group!")
            return
        
        template = request.env.ref('auth_signup_extension.mail_template_account_approval', raise_if_not_found=False)
        if not template:
            _logger.error("Approval email template not found!")
            return

        for admin in admin_users:
            _logger.info(f"Sending approval email to: {admin.email}")
            template.sudo().send_mail(admin.id, force_send=True)
            _logger.info(f"Sent approval email to: {admin.email}")
