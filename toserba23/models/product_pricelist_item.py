# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'
    
    #Create new fields
    x_notes = fields.Char(
        'Other Notes', index=False)
    x_formula_price = fields.Float('Hasil', compute='_calculate_formula', readonly=True, store=False, digits=dp.get_precision('Product Price'), groups="sales_team.group_sale_salesman")

    @api.multi
    def _calculate_formula(self):
        for item in self:
            formula_price = 0.0
            if item.applied_on == "1_product" and item.product_tmpl_id:
                formula_price = item.pricelist_id.get_product_price(item.product_tmpl_id, item.min_quantity, '')
            item.update({
                'x_formula_price': formula_price
            })
