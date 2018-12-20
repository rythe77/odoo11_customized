# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EquityHolderAccount(models.Model):
    _name = 'equity.holder_account'

    name = fields.Char(string='Name', compute='_get_name', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True, readonly=False)
    default_credit_account_id = fields.Many2one('account.account', string='Default Credit Account', required=True,
        domain=[('deprecated', '=', False)], help="It acts as a default account for credit amount")
    default_debit_account_id = fields.Many2one('account.account', string='Default Debit Account', required=True,
        domain=[('deprecated', '=', False)], help="It acts as a default account for debit amount")

    @api.multi
    @api.depends('partner_id')
    def _get_name(self):
        for equity_holder in self:
            if equity_holder.partner_id:
                equity_holder.name = equity_holder.partner_id.name