# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class OtherIncomePaymentWizard(models.TransientModel):

    _name = "other.income.payment.wizard"
    _description = "Other Income Payment Wizard"

    other_income_id = fields.Many2one('other.income.account', string='Other Income Type', required=True)
    journal_id = fields.Many2one('account.journal', string='Payment Method', required=True, domain=[('type', 'in', ('bank', 'cash'))])
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True, required=True)
    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, readonly=True)
    label = fields.Char(string='Label', required=True)

    @api.one
    @api.constrains('amount')
    def _check_amount(self):
        if not self.amount > 0.0:
            raise ValidationError('The payment amount must be strictly positive.')

    @api.multi
    def other_income_create(self, post=False):
        self.ensure_one()
        for rec in self:
            debit_account = rec.journal_id.default_debit_account_id
            credit_account = rec.other_income_id.default_credit_account_id
            
            move = {
                'name': '/',
                'journal_id': rec.journal_id.id,
                'date': rec.payment_date,
                'ref': rec.label,
                
                'line_ids': [(0, 0, {
                        'name': rec.label,
                        'debit': rec.amount,
                        'account_id': debit_account.id,
                    }), (0, 0, {
                        'name': rec.label,
                        'credit': rec.amount,
                        'account_id': credit_account.id,
                    })]
            }
            move_id = self.env['account.move'].create(move)
            if post == True:
                move_id.post()
            return move_id.id

    def other_income_create_post(self):
        self.ensure_one()
        self.other_income_create(True)