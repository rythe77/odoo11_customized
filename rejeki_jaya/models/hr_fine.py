# -*- coding: utf-8 -*-

from datetime import datetime, time

from odoo import models, fields, api, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz

class HrFineCategory(models.Model):
    _name = 'hr.fine_category'
    _description = 'Kategori Catatan Denda'

    name = fields.Char(string='Keterangan', required=True)
    hr_fine_id = fields.One2many('hr.fine', 'category_id', store=True)
    amount = fields.Float(string='Jumlah Denda')

class HrFine(models.Model):
    _name = 'hr.fine'
    _description = 'Catatan Denda Karyawan'

#    name = fields.Char(string='Keterangan', required=True)
    category_id = fields.Many2one('hr.fine_category', string='Kategori Denda', required=True, ondelete='cascade', index=True)
    amount = fields.Float(string='Jumlah', store=True)
    date_input = fields.Date(string='Tanggal Pencatatan', required=True, index=True, copy=False, default=fields.Datetime.now)
    employee_id = fields.Many2one('hr.employee', string='Nama Karyawan', required=True, index=True)
    
    @api.onchange('category_id')
    def category_id_change(self):
        for fine in self:
            fine.amount = fine.category_id.amount

    @api.multi
    def get_total_fines(self, employee_id, date_from, date_to):
        """ Compute total fines between two dates on the input.
        """
        # get current logged in user's timezone
        local = pytz.timezone(self.env['res.users'].browse(self._uid).tz) or pytz.utc

        amount_fines = 0
        fines = self.env['hr.fine'].search([
                 ('employee_id', '=', employee_id.id),
                 ('date_input', '>=', date_from),
                 ('date_input', '<=', date_to)
             ])
        for data in fines:
            amount_fines+=data['amount']
        return [len(fines),amount_fines]

class HrEmployeeInherited(models.Model):
    _inherit = 'hr.employee'

    hr_fine_id = fields.One2many('hr.fine', 'employee_id', store=True, index=True)