# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

class HrPayslipInherit(models.Model):
    _inherit = 'hr.payslip'
    
    # override default logic to compute working days count
    @api.model
    def get_worked_day_lines(self, contract_ids, date_from, date_to):
        res=super(HrPayslipInherit,self).get_worked_day_lines(contract_ids, date_from, date_to)
        workedDays_overtime = self.employee_id.attendance_ids.get_working_days(self.employee_id, date_from, date_to)
        amount_fines = self.employee_id.hr_fine_id.get_total_fines(self.employee_id, date_from, date_to)
        for data in res:
            data.update({
                'number_of_days':workedDays_overtime[0],
                'overtime_hours':workedDays_overtime[1],
                'rule_violation':amount_fines[0],
                'fine_amount':amount_fines[1]*(-1),
            })
        return res

class HrPayslipWorkedDaysInherit(models.Model):
    _inherit = 'hr.payslip.worked_days'
    
    overtime_hours = fields.Float(string='Overtime (hours)', store=True)
    rule_violation = fields.Float(string='Rule Violation', store=True)
    fine_amount = fields.Float(string='Fine Amount', store=True)