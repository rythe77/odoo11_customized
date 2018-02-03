# -*- coding: utf-8 -*-

from odoo import models, fields, api

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