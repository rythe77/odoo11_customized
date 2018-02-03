# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountPayment(models.Model):
    _inherit = "account.payment"

    sale_id = fields.Many2one('sale.order', "Sale", readonly=True,
                              states={'draft': [('readonly', False)]})