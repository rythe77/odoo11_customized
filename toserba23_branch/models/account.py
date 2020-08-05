# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.indonesia_template import amount_to_text_id

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def amount_to_text(self, amount):
        convert_amount_in_words = amount_to_text_id.amount_to_text(amount)
        return convert_amount_in_words