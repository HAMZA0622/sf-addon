from odoo import fields, models


class MenuEcomCategRel(models.Model):
    _name = 'menu.ecom.categ.rel'
    _description = 'Menu E-Commerce Categories'
    _order = 'sequence'

    menu_id = fields.Many2one('website.menu', string="Menu", required=True, ondelete='cascade')
    category_id = fields.Many2one('product.public.category', string="E-Commerce Category", required=True, ondelete='cascade')
    sequence = fields.Integer(string="Sequence", default=10)

class MenuProdRel(models.Model):
    _name = 'menu.prod.rel'
    _description = 'Menu Products'
    _order = 'sequence'

    menu_id = fields.Many2one('website.menu', string="Menu", required=True, ondelete='cascade')
    product_id = fields.Many2one('product.template', string="Product", required=True, ondelete='cascade')
    sequence = fields.Integer(string="Sequence", default=10)

class MenuProdCollectionRel(models.Model):
    _name = 'menu.prod.collection.rel'
    _description = 'Menu Product Collection'
    _order = 'sequence'

    menu_id = fields.Many2one('website.menu', string="Menu", required=True, ondelete='cascade')
    collection_id = fields.Many2one('product.collection.set', string="Product Collection", required=True, ondelete='cascade')
    sequence = fields.Integer(string="Sequence", default=10)


class Menu(models.Model):
    _inherit = "website.menu"

    is_dynamic_submenu = fields.Boolean(string="Is Dynamic SubMenu")
    submenu_model_selection = fields.Selection(
        selection=[
            ('ecom', 'E-Commerce Categories'),
            ('collection', 'Product Collections'),
        ],
        string="Sub Menu Model",
        default="ecom",
        required=True,
    )
    ecom_categ_ids = fields.One2many(
        'menu.ecom.categ.rel',
        'menu_id',
        string='E-Commerce Categories',
    )
    prod_ids = fields.One2many(
        'menu.prod.rel',
        'menu_id',
        string='Products',
    )
    collection_ids = fields.One2many('menu.prod.collection.rel','menu_id',string="Collections")

