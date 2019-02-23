# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
import pytz

from odoo.addons import decimal_precision as dp

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    
    #Create new fields
    x_vehicle_notes = fields.Char(
        'Vehicle Notes', index=False,
        states={'sale': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    x_notes = fields.Char(
        'Other Notes', index=False,
        states={'sale': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    def _prepare_invoice(self):
        vals = super(SaleOrderInherit, self)._prepare_invoice()
        # get current logged in user's timezone
        local = pytz.timezone(self.env['res.users'].browse(self._uid).tz) or pytz.utc
        vals.update({
            'date_invoice':pytz.utc.localize(datetime.datetime.now()).astimezone(local).strftime('%Y-%m-%d'),
        })
        return vals

    @api.multi
    def action_status(self):
        for item in self:
            item.invoice_status = 'invoiced'
            item.delivery_status = 'delivered'