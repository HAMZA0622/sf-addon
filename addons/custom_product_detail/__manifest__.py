{
    'name': 'Custom Product Detail',
    'version': '19.0.1.0',
    'summary': 'Custom Product Detail for Odoo 18 website sale',
    'description': 'This module provides a custom product detail for Odoo 18',
    'category': 'Website',
    'author': 'Saidul Islam Tuhin',
    'website': 'https://www.odoo.com/',

    'depends': ['base', "product", 'website', 'website_sale', 'stock', 'download_media_pricelist'],

    'data': [
        'security/ir.model.access.csv',
        'templates/custom_variant_template.xml',
        'templates/product_detail_template.xml',
        'templates/product_finishes_page_template.xml',
        'templates/attribute_detail_page_template.xml',
        'templates/headers_footers/header.xml',
        # 'templates/headers_footers/options.xml',
        'templates/templates.xml',
        'templates/collection_page_template.xml',
        'templates/category_page_template.xml',
        'templates/products_by_category_template.xml',
        'templates/quick_ship_products_template.xml',
        'templates/shop_page_template.xml',
        'views/product_template_views.xml',
        'views/product_attribute_views.xml',
        'views/website_menu_views.xml',
	    'views/product_collection_set_views.xml',
	    'views/dimension_type_views.xml',

    ],
    'assets': {
        'web.assets_frontend': [
            'custom_product_detail/static/lib/photoswipe/*.css',
            'custom_product_detail/static/lib/photoswipe/photoswipe.umd.min.js',
            'custom_product_detail/static/lib/photoswipe/photoswipe-lightbox.umd.min.js',

            'custom_product_detail/static/src/js/*.js',
            'custom_product_detail/static/src/scss/*.scss',
        ],
        'website.assets_wysiwyg': [
        'custom_product_detail/static/src/builder/plugins/options/header/custom_header_option.js',
        'custom_product_detail/static/src/builder/plugins/options/header/custom_header_option.xml',
        ],
    },
    'installable': True,
    'application': True,

}
