{
    'name': "Product List Extension",
    'summary': "Extend Product Model with Additional Name Field and Show It in Product Grid",
    'description': """
        This module adds an extended name field to the product model.

        The extended name is displayed alongside the main product name in the product grid on the e-commerce website.
    """,
    'author': "Meer Zaman Khattak",
    'website': "https://www.decoscape.com",
    'category': 'Website',
    'version': '1.0',
    'depends': ['website_sale','custom_product_detail'],
    'data': [
        'views/templates.xml',
        'views/product_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}