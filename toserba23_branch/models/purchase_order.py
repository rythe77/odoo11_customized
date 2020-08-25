from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def action_status(self):
        for item in self:
            item.invoice_status = 'invoiced'
            item.delivery_status = 'delivered'
