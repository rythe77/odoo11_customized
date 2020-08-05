# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
import pytz

from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    
    @api.multi
    def action_status(self):
        for item in self:
            item.invoice_status = 'invoiced'
            item.delivery_status = 'delivered'