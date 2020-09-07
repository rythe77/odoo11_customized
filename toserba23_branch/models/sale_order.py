# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    
    #Create new fields
    x_notes = fields.Char(
        'Keterangan', index=False,
        states={'sale': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    @api.multi
    def action_status(self):
        for item in self:
            item.invoice_status = 'invoiced'
            item.delivery_status = 'delivered'