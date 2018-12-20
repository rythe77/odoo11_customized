# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class EquityChangePaymentWizard(models.TransientModel):

    _name = "equity.change.payment.wizard"
    _description = "Equity Change Payment wizard"

    payment_type = fields.Selection([('outbound', 'Send Money to Equity Holder'), ('inbound', 'Receive Money from Equity Holder')], string='Payment Type', required=True)
    equity_holder_id = fields.Many2one('equity.holder_account', string='Equity Holder', required=True)
    partner_id = fields.Many2one('res.partner', related='equity_holder_id.partner_id', string='Partner')
    journal_id = fields.Many2one('account.journal', string='Payment Method', required=True, domain=[('type', 'in', ('bank', 'cash'))])
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True, required=True)
    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, readonly=True)
    label = fields.Char(string='Label', default=_('Pengambilan Prive'), required=True)

    @api.one
    @api.constrains('amount')
    def _check_amount(self):
        if not self.amount > 0.0:
            raise ValidationError('The payment amount must be strictly positive.')

    @api.multi
    def equity_change_create(self, post=False):
        self.ensure_one()
        for rec in self:
            if rec.payment_type == 'outbound':
                debit_account = rec.equity_holder_id.default_debit_account_id
                credit_account = rec.journal_id.default_credit_account_id
            else:
                debit_account = rec.journal_id.default_debit_account_id
                credit_account = rec.equity_holder_id.default_credit_account_id
            
            move = {
                'name': '/',
                'journal_id': rec.journal_id.id,
                'date': rec.payment_date,
                'ref': rec.label,
                
                'line_ids': [(0, 0, {
                        'name': rec.label,
                        'debit': rec.amount,
                        'account_id': debit_account.id,
                        'partner_id': rec.partner_id.id,
                    }), (0, 0, {
                        'name': rec.label,
                        'credit': rec.amount,
                        'account_id': credit_account.id,
                        'partner_id': rec.partner_id.id,
                    })]
            }
            move_id = self.env['account.move'].create(move)
            if post == True:
                move_id.post()
            return move_id.id

    def equity_change_create_post(self):
        self.ensure_one()
        self.equity_change_create(True)