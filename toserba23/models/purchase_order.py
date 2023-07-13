# -*- coding: utf-8 -*-

from odoo import models, fields, api, SUPERUSER_ID
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, AccessError
import datetime
import pytz

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

    # When "Confirm PO" button is pressed, automatically update product purchasing price for the particular supplier
    @api.multi
    def _add_supplier_to_product(self):
        # Add the partner in the supplier list of the product if the supplier is not registered for
        # this product. We limit to 10 the number of suppliers for a product to avoid the mess that
        # could be caused for some generic products ("Miscellaneous").
        res=super(PurchaseOrder,self)._add_supplier_to_product()
        # get current logged in user's timezone
        local = pytz.timezone(self.env['res.users'].browse(self._uid).tz) or pytz.utc
        today = pytz.utc.localize(datetime.datetime.now()).astimezone(local).strftime('%Y-%m-%d')

        for line in self.order_line:
            # Do not add a contact as a supplier
            partner = self.partner_id if not self.partner_id.parent_id else self.partner_id.parent_id
            if partner in line.product_id.seller_ids.mapped('name'):
                for seller_id in line.product_id.seller_ids.filtered(lambda r: r.name == partner).sorted(key=lambda r: r.min_qty, reverse=True):
                    if seller_id.date_start and seller_id.date_start <= today and not seller_id.date_end and line.product_qty >= seller_id.min_qty:
                        seller_id.price = line.price_unit
                        seller_id.date_start = today
                        break


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

    @api.multi
    def _prepare_invoice_line(self, qty):
        res=super(PurchaseOrderLine,self)._prepare_invoice_line(qty=qty)
        res.update({
            'discount': self.x_discount,
        })
        return res
