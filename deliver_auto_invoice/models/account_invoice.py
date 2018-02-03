# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    picking_id = fields.One2many(
        'stock.picking', 'invoice_id', 'Related Picking',
        help="Picking related to this invoice")