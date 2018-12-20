# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError

class RmaProductReplacementWizard(models.TransientModel):
    _name = "rma.product.replacement.wizard"
    _description = "RMA Product Replacement Wizard"

    rma_line_id = fields.Many2one('rma.rma.line', string='RMA Lines', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', required=True, help="Returned product")
    replace_product_qty = fields.Float('Replace Quantity', default = 0.0, digits=dp.get_precision('Product Unit of Measure'),
                                        help="Quantity of product replaced")

    @api.one
    def product_replacement(self):
        if self.product_id:
            rma_line_id = self.env['rma.rma.line'].browse(self.rma_line_id.id)
            rma_line_id.replace_product_id = self.product_id
            rma_line_id.replace_product_qty = self.replace_product_qty