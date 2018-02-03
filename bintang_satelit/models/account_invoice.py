# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    x_transporter_note = fields.Char(
        'Transporter Name', index=False,
        states={'paid': [('readonly', True)], 'cancel': [('readonly', True)]})