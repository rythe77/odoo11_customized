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
    def action_status(self):
        for item in self:
            item.invoice_status = 'invoiced'
            item.delivery_status = 'delivered'