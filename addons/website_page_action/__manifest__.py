{
    'name': 'Website Page Action',
    'version': '1.1',
    'category': 'Website',
    'summary': 'Add Custom `Edit` Action to Website Pages List page',
    'description': """
        This module adds a custom "Edit Page" action to the Website Pages list view in the Odoo backend.
        Unlike the default behavior, which uses the configured website domain for navigation,
        this module generates the edit link using the current browser host URL,
        ensuring users are always directed to the correct edit page regardless of multi-website domain configurations.
        The "Edit Page" link appears as the first column and opens the page editor directly in the current tab.
    """,
    'author': "Meer Zaman Khattak",
    'depends': ['website'],
    'data': [
        'views/website_page_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}