# -*- coding: utf-8 -*-
import base64
import logging
from odoo import http, tools, _
from odoo.addons.website_sale.controllers.main import WebsiteSale, TableCompute
from werkzeug.exceptions import Forbidden, NotFound
from odoo.http import request, content_disposition
from werkzeug.exceptions import NotFound
from odoo.addons.website.controllers.main import QueryURL
from datetime import datetime
from openpyxl.styles import Alignment
from odoo.tools import lazy
# from odoo.addons.http_routing.models.ir_http import slug
import zipfile
import io
from io import BytesIO
import math
import re

_logger = logging.getLogger(__name__)

EXCEL_MIMETYPE = {
    'application/vnd.ms-excel': 'xls',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx'
}


class DownloadMediaWebsite(WebsiteSale):

    @http.route([
        '/download/pricelist/attachment-zip/<model("product.pricelist"):pricelist>',
    ], type='http', auth="user")
    def download_attachment_zip(self, pricelist, **kw):
        excel_file = pricelist.sudo().related_pricelist_excel_attachment_id
        pdf_file = pricelist.sudo().related_pricelist_pdf_attachment_id
        zip_data = io.BytesIO()
        with zipfile.ZipFile(zip_data, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if excel_file:
                file_type = EXCEL_MIMETYPE.get(excel_file.sudo().mimetype, 'xlsx')
                excel_file_name = f"{pricelist.name}.{file_type}"
                zipf.writestr(f"{excel_file_name}", base64.b64decode(excel_file.datas))
            if pdf_file:
                pdf_file_name = f"{pricelist.name}.pdf"
                zipf.writestr(f"{pdf_file_name}", base64.b64decode(pdf_file.datas))
        file_name = f"{pricelist.name}.zip"
        response = request.make_response(
            zip_data.getvalue(),
            headers=[
                ('Content-Type', 'application/zip'),
                ('Content-Disposition', content_disposition(file_name))
            ]
        )
        zip_data.close()
        return response

    def _create_zip_response(self, products, file_name):
        zip_data = io.BytesIO()
        with zipfile.ZipFile(zip_data, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for product in products:
                model_no = product.default_code
                product_name = product.name
                model_no = model_no if model_no else product_name
                text_file_name = str(model_no) +'_'+ "video"
                folder_name = f"{model_no}"
                
                product_imgs = [img for img in product._get_images() if not (hasattr(img, 'video_url') and img.video_url)]
                product_with_video_url = [img for img in product._get_images() if (hasattr(img, 'video_url') and img.video_url)]
                
                video_urls = []
                for img in product_with_video_url:
                    if hasattr(img, 'video_url') and img.video_url:
                        video_urls.append(img.video_url)
                if video_urls:
                    video_content = "\n".join(video_urls)
                    text_file_name = re.sub(r'/', '-', text_file_name)
                    folder_name = re.sub(r'/', '-', folder_name)
                    zipf.writestr(f"{folder_name}/{text_file_name}.txt", video_content)
                        
                if product_imgs:
                    extra_image_serial = 0
                    image_name_list = []
                    for index, record in enumerate(product_imgs, start=1):
                        image_data = record.with_context({'bin_size':False}).image_1920
                        if record._table == 'product_template':
                            if record.related_image_attachment_id:
                                m_type = record.related_image_attachment_id.sudo().mimetype.split("/")
                                image_name = record.default_code or record.name
                        elif record._table == 'product_image':
                            if record.related_attachment_id:
                                extra_image_serial += 1
                                m_type = record.related_attachment_id.sudo().mimetype.split("/")
                                image_name = str(model_no) + '_' +  str(extra_image_serial)
                        if image_data and m_type:
                            image_name = f"{image_name}.{m_type[1]}"
                            if image_name in image_name_list:
                                image_name = f"{image_name}_{index}.{m_type[1]}"
                            image_name_list.append(image_name)
                            folder_name = re.sub(r'/', '-', folder_name)
                            image_name = re.sub(r'/', '-', image_name)
                            zipf.writestr(f"{folder_name}/{image_name}", base64.b64decode(image_data))
        response = request.make_response(
            zip_data.getvalue(),
            headers=[
                ('Content-Type', 'application/zip'),
                ('Content-Disposition', content_disposition(file_name))
            ]
        )
        zip_data.close()
        return response
    
    @http.route([
        '/download/all/media/category/<model("product.public.category"):category>',
    ], type='http', auth="public", website=True)
    def download_all_media(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, ppg=False, **post):
        try:
            min_price = float(min_price)
        except ValueError:
            min_price = 0
        try:
            max_price = float(max_price)
        except ValueError:
            max_price = 0

        Category = request.env['product.public.category']
        if category:
            category = Category.search([('id', '=', int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category

        website = request.env['website'].get_current_website()
        website_domain = website.website_domain()

        request_args = request.httprequest.args
        attrib_list = request_args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        conversion_rate = 1
        if search:
            post['search'] = search
        if attrib_list:
            post['attrib'] = attrib_list

        options = self._get_search_options(
            category=category,
            attrib_values=attrib_values,
            min_price=min_price,
            max_price=max_price,
            conversion_rate=conversion_rate,
            display_currency=website.currency_id,
            **post
        )
        options.update({
            'displayImage':False,
            'displayDescription': False,
            'displayDetail': False,
            
        })
        fuzzy_search_term, product_count, search_product = self._shop_lookup_products(attrib_set, options, post, search, website)
        
        file_name = category.display_name
        file_name = file_name + '.zip'
        
        if post.get('part'):
            part  = int(post.get('part'))
            max_media_count = request.env['website'].get_current_website().maximum_media_count
            if max_media_count:
                start_index = (part - 1) * max_media_count
                end_index = start_index + max_media_count
                search_product = search_product[start_index:end_index]
                file_name = f"{category.display_name}_part_{part}.zip"
        
        return self._create_zip_response(search_product, file_name)

    @http.route([
        '/download/media',
        '/download/media/page/<int:page>',
        '/download/media/category/<model("product.public.category"):category>',
        '/download/media/category/<model("product.public.category"):category>/page/<int:page>',
    ], type='http', auth="public", website=True)
    def download_media(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, ppg=False, **post):
        
        if post.get('order',''):
            post['order'] = ''
        context = request.env.context.copy()
        context['from_shop'] = False
        request.env.context = context

        add_qty = int(post.get('add_qty', 1))
        try:
            min_price = float(min_price)
        except ValueError:
            min_price = 0
        try:
            max_price = float(max_price)
        except ValueError:
            max_price = 0

        Category = request.env['product.public.category']
        if category:
            category = Category.search([('id', '=', int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category

        website = request.env['website'].get_current_website()
        website_domain = website.website_domain()
        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = 60

        ppr = 6

        request_args = request.httprequest.args
        attrib_list = request_args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        # filter_by_tags_enabled = website.is_view_active('website_sale.filter_products_tags')
        # if filter_by_tags_enabled:
        #     tags = request_args.getlist('tags')
        #     # Allow only numeric tag values to avoid internal error.
        #     if tags and all(tag.isnumeric() for tag in tags):
        #         post['tags'] = tags
        #         tags = {int(tag) for tag in tags}
        #     else:
        #         post['tags'] = None
        #         tags = {}

        keep = QueryURL('/download/media', **self._shop_get_query_url_kwargs(category and int(category), search, min_price, max_price, **post))

        now = datetime.timestamp(datetime.now())
        pricelist = website.pricelist_id
        if 'website_sale_pricelist_time' in request.session:
            # Check if we need to refresh the cached pricelist
            pricelist_save_time = request.session['website_sale_pricelist_time']
            if pricelist_save_time < now - 60*60:
                request.session.pop('website_sale_current_pl', None)
                website.invalidate_recordset(['pricelist_id'])
                pricelist = website.pricelist_id
                request.session['website_sale_pricelist_time'] = now
                request.session['website_sale_current_pl'] = pricelist.id
        else:
            request.session['website_sale_pricelist_time'] = now
            request.session['website_sale_current_pl'] = pricelist.id

        # filter_by_price_enabled = website.is_view_active('website_sale.filter_products_price')
        # if filter_by_price_enabled:
        #     company_currency = website.company_id.sudo().currency_id
        #     conversion_rate = request.env['res.currency']._get_conversion_rate(
        #         company_currency, website.currency_id, request.website.company_id, fields.Date.today())
        # else:
        #     conversion_rate = 1
        conversion_rate = 1
        url = '/download/media'
        if search:
            post['search'] = search
        if attrib_list:
            post['attrib'] = attrib_list

        options = self._get_search_options(
            category=category,
            attrib_values=attrib_values,
            min_price=min_price,
            max_price=max_price,
            conversion_rate=conversion_rate,
            display_currency=website.currency_id,
            **post
        )

        fuzzy_search_term, product_count, search_product = self._shop_lookup_products(attrib_set, options, post, search, website)

        categs_domain = [('parent_id', '=', False)] + website_domain
        if search:
            search_categories = Category.search(
                [('product_tmpl_ids', 'in', search_product.ids)] + website_domain
            ).parents_and_self
            categs_domain.append(('id', 'in', search_categories.ids))
        else:
            search_categories = Category
        categs = lazy(lambda: Category.search(categs_domain))

        if category:
            url = "/download/media/category/%s" % request.env['ir.http']._slug(category)

        pager = website.pager(url=url, total=product_count, page=page, step=ppg, scope=5, url_args=post)
        offset = pager['offset']
        products = search_product[offset:offset + ppg]

        ProductAttribute = request.env['product.attribute']
        if products:
            # get all products without limit
            attributes = lazy(lambda: ProductAttribute.search([
                ('product_tmpl_ids', 'in', search_product.ids),
                ('visibility', '=', 'visible'),
            ]))
        else:
            attributes = lazy(lambda: ProductAttribute.browse(attributes_ids))

        layout_mode = request.session.get('website_sale_shop_layout_mode')
        if not layout_mode:
            if website.viewref('website_sale.products_list_view').active:
                layout_mode = 'list'
            else:
                layout_mode = 'grid'
            request.session['website_sale_shop_layout_mode'] = layout_mode

        # Try to fetch geoip based fpos or fallback on partner one
        fiscal_position_sudo = website.fiscal_position_id.sudo()
        products_prices = lazy(lambda: products._get_sales_prices(pricelist, fiscal_position_sudo))

        values = {
            'search': fuzzy_search_term or search,
            'original_search': fuzzy_search_term and search,
            'order': post.get('order', ''),
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'fiscal_position': fiscal_position_sudo,
            'add_qty': add_qty,
            'products': products,
            'search_product': search_product,
            'search_count': product_count,  # common for all searchbox
            'bins': lazy(lambda: TableCompute().process(products, ppg, ppr)),
            'ppg': ppg,
            'ppr': ppr,
            'categories': categs,
            'attributes': attributes,
            'keep': keep,
            'search_categories_ids': search_categories.ids,
            'layout_mode': layout_mode,
            'products_prices': products_prices,
            'get_product_prices': lambda product: lazy(lambda: products_prices[product.id]),
            'float_round': tools.float_round,
            'current_website': request.env['website'].get_current_website(),
        }
        # if filter_by_price_enabled:
        #     values['min_price'] = min_price or available_min_price
        #     values['max_price'] = max_price or available_max_price
        #     values['available_min_price'] = tools.float_round(available_min_price, 2)
        #     values['available_max_price'] = tools.float_round(available_max_price, 2)
        # if filter_by_tags_enabled:
        #     values.update({'all_tags': all_tags, 'tags': tags})
        if category:
            values['main_object'] = category
        values.update(self._get_additional_shop_values(values))

        if not category and not search:
            url = '/download/media'
            products_of_specific_cat = request.env['product.template'].sudo()
            bins = TableCompute().process(products_of_specific_cat, ppg, ppr)
            product_count = len(products_of_specific_cat)
            pager = website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=None)
            values['bins'] = bins
            values['pager'] = pager
            values['search_count'] = product_count

        return request.render("download_media_pricelist.AGT_products", values)
    

    @http.route(['/download/product/images/zip/<model("product.template"):product>'], type='http', auth="public", website=True, sitemap=False)
    def download_product_images(self, product):
        product = request.env['product.template'].sudo().browse(int(product))
        model_no = product.default_code
        product_name = product.name
        model_no = model_no if model_no else product_name
        extra_image_serial = 0
        file_name = model_no + ".zip" if model_no else "model_no.zip"
        if product:
            zip_data = io.BytesIO()
            with zipfile.ZipFile(zip_data, 'w', zipfile.ZIP_DEFLATED) as zipf:
                folder_name = f"{model_no}"
                text_file_name = str(model_no) +'_'+ "video"
                product_imgs = [img for img in product._get_images() if not (hasattr(img, 'video_url') and img.video_url)]
                product_with_video_url = [img for img in product._get_images() if (hasattr(img, 'video_url') and img.video_url)]
                video_urls = []
                for img in product_with_video_url:
                    if hasattr(img, 'video_url') and img.video_url:
                        video_urls.append(img.video_url)
                if video_urls:
                    video_content = "\n".join(video_urls)
                    text_file_name = re.sub(r'/', '-', text_file_name)
                    folder_name = re.sub(r'/', '-', folder_name)
                    zipf.writestr(f"{folder_name}/{text_file_name}.txt", video_content)
                if product_imgs:
                    image_name_list = []
                    for index, record in enumerate(product_imgs, start=1):
                        image_data = record.image_1920
                        if record._table == 'product_template':
                            if record.related_image_attachment_id:
                                m_type = record.related_image_attachment_id.sudo().mimetype.split("/")
                                image_name = record.default_code or record.name
                        elif record._table == 'product_image':
                            if record.related_attachment_id:
                                extra_image_serial += 1
                                m_type = record.related_attachment_id.sudo().mimetype.split("/")
                                image_name = str(model_no) + '_' + str(extra_image_serial) 
                        if image_data and m_type:
                            image_name = f"{image_name}.{m_type[1]}"
                            if image_name in image_name_list:
                                image_name = f"{image_name}_{index}.{m_type[1]}"
                            image_name_list.append(image_name)
                            folder_name = re.sub(r'/', '-', folder_name)
                            image_name = re.sub(r'/', '-', image_name)
                            zipf.writestr(f"{folder_name}/{image_name}", base64.b64decode(image_data))

            response = request.make_response(
                zip_data.getvalue(),
                headers=[
                    ('Content-Type', 'application/zip'),
                    ('Content-Disposition', content_disposition(file_name))
                ]
            )
            zip_data.close()
            return response
        
    
    @http.route(['/download'], type='http', auth="user", website=True, sitemap=False)
    def download_page(self):
        return request.render("download_media_pricelist.AGT_download")
    
    @http.route(['/download/latest/pricelist'], type='http', auth="user", website=True, sitemap=False)
    def download_latest_pricelist(self):
        current_website = request.website.get_current_website()
        partner = request.env.user.partner_id
        available_pricelists = current_website.get_pricelist_available(show_visible=True)
        assigned_pricelist = False
        price_lists = request.env['product.pricelist']
        if len(available_pricelists) > 1:
            if partner.property_product_pricelist:
                assigned_pricelist = available_pricelists.filtered(lambda x: x.id == partner.property_product_pricelist.id)
                for pricelist in available_pricelists:
                    if pricelist.id == partner.property_product_pricelist.id:
                        assigned_pricelist = pricelist
                    else:
                        price_lists += pricelist 
            else:
                assigned_pricelist = available_pricelists[0]
        else:
            pricelist = available_pricelists
            assigned_pricelist = available_pricelists

        values = {
            'price_lists': price_lists.filtered(lambda x: x.is_default_fallback),
            'assigned_pricelist': assigned_pricelist,
        }
        return request.render("download_media_pricelist.AGT_download_pricelist", values)
    
    def _get_pricelist_data(self, pricelist):
        """Get the pricelist data for the given pricelist."""
        # product name, model, uom, qunatity_1_price, quantity_2_price, quantity_3_price
        # TODO: need to check pricelist item computation rule and apply on product or variant or all product
        item_ids = pricelist.non_default_item_ids
        quantities = item_ids.mapped('min_quantity')
        quantities = sorted(list(set(quantities)))
        product_products = item_ids.mapped('product_tmpl_id').sudo().filtered(lambda x: x.is_published)
        sorted_products = sorted(product_products, key=lambda x: x.default_code)
        current_currency = pricelist.currency_id

        def get_product_price_with_symbol(price, currency_id):
            symbol = currency_id.symbol
            symbol_position = currency_id.position
            if symbol_position == 'before':
                return f"{symbol}{price}"
            else:
                return f"{price}{symbol}"

        data = {}
        _logger.info(f"Total products: {len(sorted_products)} of {pricelist.name}")
        for product in sorted_products:
            data[product.id] = {
                'Model No': product.default_code,
            }
            for qty in quantities:
                price = pricelist._get_product_price(product, qty)
                price = get_product_price_with_symbol(price, current_currency)
                column_name = f"{qty}+"
                data[product.id][column_name] = price
            # list_price = product.list_price
            # list_price = get_product_price_with_symbol(list_price, current_currency)
            # data[product.id]['Retail Price'] = list_price
        _logger.info(f"Done pricelist file generate for {pricelist.name}")
        return data
    
    def convert_file_size(self, size_bytes):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])
    

    @http.route([
        '/download/media/product/images/<int:product>'
    ], type='http', auth="user", website=True)
    def detail_product_media(self, product, **kw):
        keep = QueryURL('/download/media/category/')
        search = None
        product = request.env['product.template'].sudo().browse(int(product))
        category = None
        if kw.get('category', None):
            category_id = int(kw.get('category', None))
            category = request.env['product.public.category'].sudo().browse(category_id)
        if kw.get('search',None):
            search = kw.get('search',None)
        if product:
            # folder_name = f"{product.default_code}"
            file_model = product.default_code
            product_imgs = product._get_images()
            directory_detail = [] 
            video_url = False
            if product_imgs:
                extra_image_serial = 0
                for index, record in enumerate(product_imgs, start=1):
                    image_data = record.image_1920
                    # file_model = record.default_code
                    if record._table == 'product_template':
                        file_name = record.default_code
                        if record.related_image_attachment_id:
                            attachment_id = record.related_image_attachment_id
                            m_type = record.related_image_attachment_id.mimetype.split("/")
                            file_size = record.related_image_attachment_id.file_size
                            image_src = record.related_image_attachment_id.image_src
                            local_url = record.related_image_attachment_id.local_url
                    elif record._table == 'product_image':
                        extra_image_serial +=1
                        file_name = file_model+ '_' + str(extra_image_serial)
                        if record.related_attachment_id:
                            attachment_id = record.related_attachment_id
                            m_type = record.related_attachment_id.mimetype.split("/")
                            file_size = record.related_attachment_id.file_size
                            image_src = record.related_attachment_id.image_src
                            local_url = record.related_attachment_id.local_url
                            if record.video_url:
                                video_url = record.video_url
                    if image_data:
                        directory_detail.append({
                            'file_name': file_name,
                            'type': m_type[1],
                            'size': self.convert_file_size(file_size),
                            'date': record.create_date.strftime('%Y/%m/%d'),
                            'image_src': image_src,
                            'local_url': local_url,
                            'video_url': video_url,
                            'attachment_id': attachment_id,
                        })

            values = {
                'directory_details': directory_detail,
                'product': product,
                'category': category,
                'search': search,
                'keep': keep,
            }
            return request.render("download_media_pricelist.directory_content", values)
    
    @http.route(['/download/single/product/image/<int:attachment_id>/<string:download_file_name>'], type='http', auth="user", website=True, sitemap=False)
    def download_single_product_image_media(self, attachment_id, download_file_name):
        # Get the attachment data
        attachment_id = request.env['ir.attachment'].sudo().browse(int(attachment_id)).exists()
        if not attachment_id.public:
            _logger.error(f"Attachment with ID {attachment_id.id} is not public.")
            raise Forbidden()
        if not attachment_id:
            # not found
            raise NotFound()
        attachment_data = attachment_id.datas
        
        # Get the filename and mimetype
        # filename = attachment_id.res_name
        mimetype = attachment_id.mimetype.split("/")[1]
        image_file_name = download_file_name+'.'+mimetype

        # Create headers for the response
        headers = {
            'Content-Type': mimetype,
            'Content-Disposition': f'attachment; filename="{image_file_name}"'
        }
        response = request.make_response(base64.b64decode(attachment_data), headers=headers)
        return response
    

    
    
    


    