# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

class HrPayslipInherit(models.Model):
    _inherit = 'hr.payslip'

    # Create new fields
    description = fields.Text()

    # override default logic to compute working days count
    @api.model
    def get_worked_day_lines(self, contract_ids, date_from, date_to):
        res=super(HrPayslipInherit,self).get_worked_day_lines(contract_ids, date_from, date_to)
        workedDays_overtime = self.employee_id.attendance_ids.get_working_days(self.employee_id, date_from, date_to)
        for data in res:
            if data.get('code') == 'WORK100':
                data.update({
                    'number_of_days':workedDays_overtime[0],
                    'overtime_hours':workedDays_overtime[1],
                    'overtime_hours_late':workedDays_overtime[2],
                })
        return res

class HrPayslipWorkedDaysInherit(models.Model):
    _inherit = 'hr.payslip.worked_days'
    
    overtime_hours = fields.Float(string='Overtime (hours)', store=True)
    overtime_hours_late = fields.Float(string='Late Overtime (hours)', store=True)