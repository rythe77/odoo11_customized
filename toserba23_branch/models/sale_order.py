# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    
    @api.multi
    def action_status(self):
        for item in self:
            item.invoice_status = 'invoiced'
            item.delivery_status = 'delivered'