# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.indonesia_template import amount_to_text_id

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    x_collector = fields.Char(
        'Collector', index=False,
        states={'paid': [('readonly', True)], 'cancel': [('readonly', True)]})

    def _prepare_invoice_line_from_po_line(self, line):
        data=super(AccountInvoice,self)._prepare_invoice_line_from_po_line(line)
        if line.x_discount:
            data.update({
                'discount':line.x_discount,
            })
        return data

    @api.multi
    def amount_to_text(self, amount):
        convert_amount_in_words = amount_to_text_id.amount_to_text(amount)
        return convert_amount_in_words

class AccountPayment(models.Model):
    _inherit = "account.payment"

    x_collector = fields.Char(
        'Collector', index=False,
        states={'posted': [('readonly', True)]})


class account_register_payments_inherited(models.TransientModel):
    _inherit = 'account.register.payments'

    x_collector = fields.Char('Collector')

    def get_payment_vals(self):
        res=super(account_register_payments_inherited,self).get_payment_vals()
        res.update({
            'x_collector':self.x_collector,
        })
        return res