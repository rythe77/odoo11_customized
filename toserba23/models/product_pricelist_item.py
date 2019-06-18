# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'
    
    #Create new fields
    x_notes = fields.Char(
        'Other Notes', index=False)
    x_formula_price = fields.Float('Hasil', compute='_calculate_formula', readonly=True, store=False, digits=dp.get_precision('Product Price'))

    @api.multi
    def _calculate_formula(self):
        for item in self:
            formula_price = 0.0
            # check that pricelist item is applied on product, and check that the product is not on onchange status
            if item.applied_on == "1_product" and item.product_tmpl_id and not isinstance(item.product_tmpl_id.id, models.NewId):
                formula_price = item.pricelist_id.get_product_price(item.product_tmpl_id, item.min_quantity, '')
            item.update({
                'x_formula_price': formula_price
            })
