{
    'name': "Auth Signup Extension",
    'version': "1.1",
    'summary': "Add Custom Fields to Signup Form",
    'description': "Extend the signup form to capture additional details and save them on the contact (res.partner) record.",
    'author': "Meer Zaman Khattak",
    'category': "Custom",
    'depends': ['auth_signup', 'web', 'website', 'portal'],
    'data': [
        'data/groups.xml',
        'data/mail_template_signup.xml',
        'views/auth_signup_template.xml',
        'views/res_partner_custom_fields.xml'
    ],
    'installable': True,
    'application': True,
}