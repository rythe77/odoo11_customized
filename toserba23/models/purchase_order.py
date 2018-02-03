# -*- coding: utf-8 -*-

from odoo import models, fields, api, SUPERUSER_ID
import odoo.addons.decimal_precision as dp

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    x_vehicle_notes = fields.Char(
        'Vehicle Notes', index=False,
        states={'purchase': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    x_notes = fields.Char(
        'Other Notes', index=False,
        states={'purchase': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    @api.multi
    def _prepare_picking(self):
        res=super(PurchaseOrder,self)._prepare_picking()
        if self.x_vehicle_notes:
            res.update({
                'x_vehicle_notes':self.x_vehicle_notes,
            })
        if self.x_notes:
            res.update({
                'x_notes':self.x_notes,
            })
        return res

    @api.multi
    def action_status(self):
        for item in self:
            item.invoice_status = 'invoiced'
            item.delivery_status = 'delivered'


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    #Create new fields
    x_discount = fields.Float(string='Discount (%)', digits=dp.get_precision('Discount'), default=0.0)

    @api.depends('product_qty', 'price_unit', 'taxes_id', 'x_discount')
    def _compute_amount(self):
        for line in self:
            taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.product_qty, product=line.product_id, partner=line.order_id.partner_id)
            line.update({
                'price_tax': (1-line.x_discount/100)*(taxes['total_included'] - taxes['total_excluded']),
                'price_total': (1-line.x_discount/100)*taxes['total_included'],
                'price_subtotal': (1-line.x_discount/100)*taxes['total_excluded'],
            })