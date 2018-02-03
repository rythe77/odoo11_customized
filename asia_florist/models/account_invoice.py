# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.indonesia_template import amount_to_text_id

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    x_delivery_name = fields.Char(
        'Receiver Name', index=False,
        states={'paid': [('readonly', True)], 'cancel': [('readonly', True)]})

    x_invoicing_name = fields.Char(
        'Name', index=False,
        states={'sale': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Input the name to put on invoice here")
    x_invoicing_address = fields.Char(
        'Address', index=False,
        states={'sale': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Input invoice address here")
    x_invoicing_city = fields.Char(
        'City', index=False,
        states={'sale': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Input the city name to put on invoice here")

class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.multi
    def amount_to_text(self, amount):
        convert_amount_in_words = amount_to_text_id.amount_to_text(amount)
        return convert_amount_in_words