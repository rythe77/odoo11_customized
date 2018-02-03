# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class ProductProduct(models.Model):
    _inherit = 'product.product'

    #Modify existing fields
    standard_price = fields.Float(
        'Cost', compute='_compute_standard_price',
        inverse='_set_standard_price', search='_search_standard_price',
        digits=dp.get_precision('Product Price'), groups="hide_confidential_info.view_cost_price",
        help = "Cost used for stock valuation in standard price and as a first price to set in average/fifo. "
               "Also used as a base price for pricelists. "
               "Expressed in the default unit of measure of the product. ")
    stock_value = fields.Float(
        'Value', compute='_compute_stock_value', groups="hide_confidential_info.view_cost_price")