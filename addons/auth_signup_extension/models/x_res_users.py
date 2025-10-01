from odoo import models

class ResUsers(models.Model):
    _inherit = 'res.users'

    def write(self, vals):
        # Cache previous active status
        users_with_status = [(user, user.active) for user in self]

        # Call super first
        result = super().write(vals)

        for user, was_active in users_with_status:
            is_active = vals.get('active', user.active)

            # Skip if not being activated
            if was_active or not is_active:
                continue

            # Check if partner has the tag 'ds_imported_user'
            tag = self.env['res.partner.category'].sudo().search([('name', '=', 'ds_imported_user')], limit=1)
            if tag and tag in user.partner_id.category_id:
                continue 

            # Send activation email
            template = self.env.ref('auth_signup_extension.mail_template_decoscape_user_activation', raise_if_not_found=False)
            if template:
                template.send_mail(user.id, force_send=True)

        return result
