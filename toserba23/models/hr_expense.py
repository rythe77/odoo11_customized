# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    @api.multi
    def approve_expense_sheets(self):
        super(HrExpenseSheet,self).approve_expense_sheets()
        for expense in self:
            if expense.total_amount > 1000000 and not expense.user_has_groups('hr_expense.group_hr_expense_manager'):
                raise UserError("Hanya Manajer Pengeluaran yang dapat menyetujui pengeluaran lebih dari Rp 1.000.000")