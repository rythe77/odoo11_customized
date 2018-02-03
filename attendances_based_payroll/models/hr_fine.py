# -*- coding: utf-8 -*-

from datetime import datetime, time

from odoo import models, fields, api, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz

class HrFineCategory(models.Model):
    _name = 'hr.fine_category'
    _description = 'Category of Fine Records'

    name = fields.Char(string='Notes', required=True)
    hr_fine_id = fields.One2many('hr.fine', 'category_id', store=True)
    amount = fields.Float(string='Fine Amount')

class HrFine(models.Model):
    _name = 'hr.fine'
    _description = 'Fine Records of Employee'

#    name = fields.Char(string='Keterangan', required=True)
    category_id = fields.Many2one('hr.fine_category', string='Fine Category', required=True, ondelete='cascade', index=True)
    amount = fields.Float(string='Amount', related="category_id.amount", store=True)
    date_input = fields.Date(string='Record Date', required=True, index=True, copy=False, default=fields.Datetime.now)
    employee_id = fields.Many2one('hr.employee', string='Employee Name', required=True, index=True)
    
    @api.multi
    def get_total_fines(self, employee_id, date_from, date_to):
        """ Compute total fines between two dates on the input.
        """
        # get current logged in user's timezone
        local = pytz.timezone(self.env['res.users'].browse(self._uid).tz) or pytz.utc

        amount_fines = 0
        date_from_utc = local.localize(datetime.combine(datetime.strptime(date_from, '%Y-%m-%d'),time.min)).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        date_to_utc = local.localize(datetime.combine(datetime.strptime(date_to, '%Y-%m-%d'),time.max)).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        fines = self.env['hr.fine'].search([
                 ('employee_id', '=', employee_id.id),
                 ('date_input', '>=', date_from_utc),
                 ('date_input', '<=', date_to_utc)
             ])
        for data in fines:
            amount_fines+=data['amount']
        return [len(fines),amount_fines]

class HrEmployeeInherited(models.Model):
    _inherit = 'hr.employee'

    hr_fine_id = fields.One2many('hr.fine', 'employee_id', store=True, index=True)