from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    #Create new fields
    product_desc = fields.Char(
        'Specific Request', index=False, store=True,
        states={'purchase': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Special request regarding the purchase of this product")

    @api.multi
    def _prepare_stock_moves(self, picking):
        vals = super(PurchaseOrderLine, self)._prepare_stock_moves(picking=picking)
        if self.product_desc and vals:
            vals[0].update({
                'product_desc':self.product_desc,
            })
        return vals