# -*- coding: utf-8 -*-

from datetime import datetime, time

from odoo import models, fields, api, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'
    
    overtime_hours = fields.Float(string='Overtime (hours)', compute='_compute_overtime_hours', store=True, readonly=True)

    @api.constrains('check_in', 'check_out')
    def _check_validity_check_in_check_out(self):
        """ verifies if check_in is earlier than check_out. """
        super(HrAttendance,self)._check_validity_check_in_check_out()
        
        """ verifies if check_in is on the same day as check_out. """
        # get current logged in user's timezone
        local = pytz.timezone(self.env['res.users'].browse(self._uid).tz) or pytz.utc
        
        for attendance in self:
            if attendance.check_in:
                # convert check in/out time to local timezone
                check_in = pytz.utc.localize(datetime.strptime(attendance.check_in, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local)
                if check_in.hour < 7 or check_in.hour >= 12:
                    raise exceptions.ValidationError(_('Absen masuk hanya bisa dilakukan antara pukul 07:00-12:00'))
                if attendance.check_out:
                    # convert check in/out time to local timezone
                    check_out = pytz.utc.localize(datetime.strptime(attendance.check_out, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local)
                    if check_out.hour < 13 and check_out.hour >= 7:
                        raise exceptions.ValidationError(_('Absen pulang hanya bisa dilakukan setelah pukul 13:00'))

    @api.depends('check_out')
    def _compute_overtime_hours(self):
        """ Compute overtime working hours for each attendance record.
        Check-out over the working hours will be considered overtime in 1 hour increment.
        """
        # get current logged in user's timezone
        local = pytz.timezone(self.env['res.users'].browse(self._uid).tz) or pytz.utc
        
        for attendance in self:
            if attendance.check_in and attendance.check_out:
                # convert check in/out time to local timezone
                check_in = pytz.utc.localize(datetime.strptime(attendance.check_in, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local)
                check_out = pytz.utc.localize(datetime.strptime(attendance.check_out, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local)
                # calculate overtime by iterating over employee weekly working schedule
                for work_hours in attendance.employee_id.resource_calendar_id.attendance_ids:
                    if check_in.strftime("%w") == work_hours.dayofweek:
                        if (check_out.day - check_in.day) == 0 and check_out.hour >= work_hours.hour_to:
                            delta = check_out.hour + check_out.minute/float(60) - work_hours.hour_to
                        elif (check_out.day - check_in.day) == 1 and check_out.hour < (work_hours.hour_from - 1):
                            delta = check_out.hour + check_out.minute/float(60) + 24 - work_hours.hour_to
                        else:
                            delta = 0
                        attendance.overtime_hours = round(delta)

    @api.multi
    def get_working_days(self, employee_id, date_from, date_to):
        """ Compute working days between two dates on the input.
        Also return aggregated overtime work hours in each attendance record.
        Attendance records count between input dates are considered valid working days.
        Return a list with 2 data, number of attendance records and aggregated overtime work hours
        """
        # get current logged in user's timezone
        local = pytz.timezone(self.env['res.users'].browse(self._uid).tz) or pytz.utc

        overtime_hours = 0
        date_from_utc = local.localize(datetime.combine(datetime.strptime(date_from, '%Y-%m-%d'),time.min)).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        date_to_utc = local.localize(datetime.combine(datetime.strptime(date_to, '%Y-%m-%d'),time.max)).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        attendances = self.env['hr.attendance'].search([
                ('employee_id', '=', employee_id.id),
                ('check_in', '>=', date_from_utc),
                ('check_in', '<=', date_to_utc)
            ])
        for attendance in attendances:
            overtime_hours+=attendance['overtime_hours']
        return [len(attendances),overtime_hours]
    
    @api.multi
    def auto_check_out(self):
        """ Automatically check out attendaces without checkout.
        Should be used with scheduled action.
        """
        no_check_out_attendances = self.env['hr.attendance'].search([
            ('check_out', '=', False),
        ])
        for attendance in no_check_out_attendances:
            #attendance.check_out=datetime.combine(date.today(), time(9,30,00))
            attendance.check_out=datetime.now()