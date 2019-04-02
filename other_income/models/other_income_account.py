# -*- coding: utf-8 -*-

from odoo import models, fields, api


class OtherIncomeAccount(models.Model):
    _name = 'other.income.account'

    name = fields.Char(string='Name', required=True)
    default_credit_account_id = fields.Many2one('account.account', string='Default Credit Account', required=True,
        domain=[('deprecated', '=', False)], help="It acts as a default account for credit amount")