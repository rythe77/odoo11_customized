# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from openerp.tools import float_compare

class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.multi
    @api.depends('invoice_ids','move_line_ids.matched_debit_ids','move_line_ids.matched_credit_ids')
    def _compute_payment_balance(self):
        for payment in self:
            ids = []
            total_amount = 0.0
            no_reconcile_line = True
            for aml in payment.move_line_ids:
                if aml.account_id.reconcile:
                    no_reconcile_line = False
                    ids.extend([r.debit_move_id for r in aml.matched_debit_ids] if aml.credit > 0 else [r.credit_move_id for r in aml.matched_credit_ids])
            for ml in ids:
                if payment.payment_type == 'inbound':
                    total_amount += ml.debit - ml.amount_residual
                else:
                    total_amount += ml.credit - ml.amount_residual
            set_amount = payment.amount - total_amount
            if set_amount > 0.0 and not no_reconcile_line:
                payment.payment_balance = set_amount
            else:
                payment.payment_balance = 0.0

    payment_balance = fields.Monetary(compute='_compute_payment_balance', string="Unapplied Balance",store="True",
                                      help="What remains after deducting amounts already applied to close or reduce invoice balances, or reconciled with other payments.")

