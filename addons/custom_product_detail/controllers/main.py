from odoo import http
from odoo.http import request

class ProductFinishes(http.Controller):

    @http.route(['/finishes'], type='http', auth="public", website=True)
    def render_finishes_page_template(self):
        product_attributes = request.env['product.attribute'].search([('display_type', '=', 'color'),('show_in_finishes','=',True)])
        context = {'product_attributes':product_attributes}
        return request.render('custom_product_detail.product_finishes_page_template', context)

    @http.route(['/finishes/<model("product.attribute"):attribute>'], type='http', auth="public", website=True)
    def render_attribute_detail(self, attribute):
        if not attribute:
            return request.not_found()
        context = {'attribute': attribute}
        return request.render('custom_product_detail.attribute_detail_page_template', context)

class ProductCollections(http.Controller):
    @http.route(['/collections/<model("product.collection.set"):collection>'], type='http', auth="public", website=True)
    def render_collection_template(self, collection):
        if not collection:
            return request.not_found()
        context = {'collection': collection}
        return request.render('custom_product_detail.collection_page_template', context)

class WebsiteProductCategory(http.Controller):
    @http.route(['/products'], type='http', auth="public", website=True)
    def render_category_template(self):
        ecommerce_categories = request.env['product.public.category'].search([])
        context = {'ecommerce_categories': ecommerce_categories}
        return request.render('custom_product_detail.category_page_template', context)

class WebsiteProductsByCategory(http.Controller):
    @http.route(['/products/<model("product.public.category"):category>'], type='http', auth="public", website=True)
    def render_products_by_category_template(self, category):
        if not category:
            return request.not_found()
        current_website = request.env['website'].get_current_website()

        # Filter product templates which are published and associated with the current website
        product_templates = category.product_tmpl_ids.filtered(
            lambda template: template.website_published and
                             (not template.website_id or template.website_id == current_website))

        context = {'category': category, 'product_templates': product_templates}
        return request.render('custom_product_detail.products_by_category_template', context)

class QuickShipProducts(http.Controller):
    @http.route(['/quick-ship'], type='http', auth="public", website=True)
    def render_quick_ship_template(self):
        quick_ship_products = request.env['product.template'].search([('is_quick_ship','=',True)])
        current_website = request.env['website'].get_current_website()
        quick_ship_products = quick_ship_products.filtered(
            lambda template: template.website_published and
                             (not template.website_id or template.website_id == current_website))
        context = {'quick_ship_products': quick_ship_products}
        return request.render('custom_product_detail.quick_ship_products_template', context)

