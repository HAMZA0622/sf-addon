import csv
import logging
from odoo import http, _
from odoo.http import request

_logger = logging.getLogger(__name__)

class UserImportController(http.Controller):

    @http.route('/user/import/form', type='http', auth='user', methods=['GET'], website=True)
    def user_import_form(self, **kwargs):
        """
        Render CSV upload form (Admin only).
        """
        if not request.env.user.has_group('base.group_system'):
            return request.redirect('/web?error=' + _("Access Denied."))
        
        return request.render('user_import_module.user_import_form_template')

    @http.route('/user/import', type='http', auth='user', methods=['POST'], website=True)
    def import_users(self, csv_file, **kwargs):
        """
        Handle CSV upload and bulk-create users and partners (admin access only).
        Optimized to pre-fetch existing records and use bulk creation to minimize database calls.
        """
        if not request.env.user.has_group('base.group_system'):
            return request.redirect('/web?error=' + _("Access Denied."))

        try:
            # Read CSV file content and parse rows
            csv_content = csv_file.read().decode('utf-8')
            csv_reader = csv.DictReader(csv_content.splitlines())
            rows = list(csv_reader)

            if not rows:
                return request.redirect('/web?error=' + _("Empty CSV file."))

            Users = request.env['res.users'].sudo()
            Partners = request.env['res.partner'].sudo()

            # Ensure the 'ds_imported_user' category exists
            category = request.env['res.partner.category'].sudo().search(
                [('name', '=', 'ds_imported_user')], limit=1)
            if not category:
                category = request.env['res.partner.category'].sudo().create({'name': 'ds_imported_user'})

            # Cache countries and states to avoid repeated searches
            countries = {c.name: c.id for c in request.env['res.country'].sudo().search([])}
            states = {s.name: s.id for s in request.env['res.country.state'].sudo().search([])}
            portal_group = request.env.ref('base.group_portal')

            # Pre-fetch existing users and partners in bulk using CSV emails
            emails = [row['email'] for row in rows]
            existing_users = Users.search([('login', 'in', emails)])
            existing_users_map = {user.login: user for user in existing_users}
            existing_partners = Partners.search([('email', 'in', emails)])
            existing_partners_map = {partner.email: partner for partner in existing_partners}

            # To track CSV emails that are already queued for user creation
            queued_user_emails = set()
            user_vals_list = []

            for row in rows:
                email = row['email']
                # Skip if the user already exists or already queued
                if email in existing_users_map or email in queued_user_emails:
                    _logger.info("User already exists or is duplicated in CSV, skipping: %s", email)
                    continue

                # Prepare partner values
                partner_vals = {
                    'name': f"{row['firstname']} {row['lastname']}",
                    'email': email,
                    'phone': row.get('telephone'),
                    'street': row.get('address_1', ''),
                    'street2': row.get('address_2', ''),
                    'city': row.get('city', ''),
                    'zip': row.get('postcode', ''),
                    'country_id': countries.get(row.get('country')),
                    'state_id': states.get(row.get('zone')),
                    'company_type': 'person',
                    'category_id': [(4, category.id)],
                    'x_dscape_sales_rep': row.get('sales_representative'),
                    'x_dscape_occupation': row.get('occupation'),
                    'x_dscape_subscribe': bool(int(row.get('newsletter', 0))),
                    'x_dscape_privacy_policy': bool(int(row.get('approved', 0))),
                    'company_name': row.get('company', ''),
                }

                # Check if a partner exists. If yes, update it; if not, create it.
                partner = existing_partners_map.get(email)
                if partner:
                    partner.sudo().write(partner_vals)
                    _logger.info("Updated partner: %s", partner.name)
                else:
                    partner = Partners.create(partner_vals)
                    _logger.info("Created new partner: %s", partner.name)
                    # Update the partner lookup map for later use
                    existing_partners_map[email] = partner

                # Prepare user values for bulk creation
                user_vals = {
                    'login': email,
                    'name': partner.name,
                    'partner_id': partner.id,
                    'password': row.get('password', 'changeme'),
                    'active': True,
                    'groups_id': [(6, 0, [portal_group.id])],
                }
                user_vals_list.append(user_vals)
                queued_user_emails.add(email)

            # Bulk create users if there are new ones queued
            if user_vals_list:
                Users.create(user_vals_list)
                new_users_count = len(user_vals_list)
                _logger.info("Created %d new users.", new_users_count)
            else:
                new_users_count = 0

            skipped_count = len(emails) - new_users_count
            message = _("Successfully imported %d new users. Skipped %d existing/duplicate users.") % (new_users_count, skipped_count)
            return request.redirect('/web?message=' + message)

        except Exception as e:
            _logger.exception("Error during CSV import")
            return request.redirect('/web?error=' + str(e))

    def create_user_from_csv(self, row):
        """
        This helper is retained for compatibility but is not used in the optimized bulk import.
        It creates a res.users and res.partner from a CSV row.
        """
        Users = request.env['res.users'].sudo()
        Partners = request.env['res.partner'].sudo()

        # Ensure the 'ds_imported_user' category exists (create if not found)
        category = request.env['res.partner.category'].sudo().search(
            [('name', '=', 'ds_imported_user')], limit=1)
        if not category:
            category = request.env['res.partner.category'].sudo().create({'name': 'ds_imported_user'})

        # Check if a user already exists (do NOT update if found)
        existing_user = Users.search([('login', '=', row['email'])], limit=1)

        # Map boolean fields for newsletter and privacy policy
        subscribe = bool(int(row.get('newsletter', 0)))
        privacy_policy = bool(int(row.get('approved', 0)))

        # Prepare partner values
        partner_vals = {
            'name': f"{row['firstname']} {row['lastname']}",
            'email': row['email'],
            'phone': row.get('telephone'),
            'street': row.get('address_1', ''),
            'street2': row.get('address_2', ''),
            'city': row.get('city', ''),
            'zip': row.get('postcode', ''),
            'country_id': self.get_country_id(row.get('country')),
            'state_id': self.get_state_id(row.get('zone'), row.get('country')),
            'company_type': 'person',
            'category_id': [(4, category.id)],
            'x_dscape_sales_rep': row.get('sales_representative'),
            'x_dscape_occupation': row.get('occupation'),
            'x_dscape_subscribe': subscribe,
            'x_dscape_privacy_policy': privacy_policy,
            'company_name': row.get('company', ''),
        }

        # Update or create partner
        partner = Partners.search([('email', '=', row['email'])], limit=1)
        if partner:
            partner.sudo().write(partner_vals)
            _logger.info("Updated partner: %s", partner.name)
        else:
            partner = Partners.create(partner_vals)
            _logger.info("Created new partner: %s", partner.name)

        # If user already exists, do not create a new user
        if existing_user:
            _logger.info("User already exists: %s", existing_user.login)
            return None

        # Create new portal user
        portal_group = request.env.ref('base.group_portal')
        user_vals = {
            'login': row['email'],
            'name': partner_vals['name'],
            'partner_id': partner.id,
            'password': row.get('password', 'changeme'),
            'active': True,
            'groups_id': [(6, 0, [portal_group.id])]
        }
        new_user = Users.create(user_vals)
        _logger.info("Portal user created: %s", new_user.login)
        return new_user

    def get_country_id(self, country_name):
        """
        Get country ID by name or return None.
        """
        if not country_name:
            return None
        country = request.env['res.country'].sudo().search([('name', '=', country_name)], limit=1)
        return country.id if country else None

    def get_state_id(self, state_name, country_name):
        """
        Get state ID by name and country or return None.
        """
        if not state_name or not country_name:
            return None
        country_id = self.get_country_id(country_name)
        if not country_id:
            return None
        state = request.env['res.country.state'].sudo().search([
            ('name', '=', state_name),
            ('country_id', '=', country_id)
        ], limit=1)
        return state.id if state else None
