from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    #Create new fields
    product_desc = fields.Char(
        'Specific Request', index=False, store=True,
        states={'sale': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Special request from customer regarding the purchase of this product")

    @api.multi
    def _prepare_procurement_values(self, group_id):
        vals = super(SaleOrderLine, self)._prepare_procurement_values(group_id=group_id)
        if self.product_desc:
            vals.update({
                'product_desc':self.product_desc,
            })
        return vals