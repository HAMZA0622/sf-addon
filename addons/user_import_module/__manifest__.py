{
    'name': 'User CSV Import',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Import users and partners from CSV',
    'author': 'Meer Zaman Khattak',
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'auth_signup'],
    'data': [
        'views/user_import_template.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
