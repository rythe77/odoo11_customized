# -*- coding: utf-8 -*-

from datetime import datetime, time, timedelta

from odoo import models, fields, api, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'
    
    overtime_hours = fields.Float(string='Overtime (hours)', compute='_compute_overtime_hours', store=True, readonly=True)
    overtime_hours_late = fields.Float(string='Late Overtime (hours)', compute='_compute_overtime_hours', store=True, readonly=True)

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
                if check_in.hour < 7 or check_in.hour >= 15:
                    raise exceptions.ValidationError(_('Absen masuk hanya bisa dilakukan antara pukul 07:00-15:00'))
                if attendance.check_out:
                    # convert check in/out time to local timezone
                    check_out = pytz.utc.localize(datetime.strptime(attendance.check_out, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local)
                    if check_out.hour < 15 and check_out.hour >= 7:
                        raise exceptions.ValidationError(_('Absen pulang hanya bisa dilakukan setelah pukul 15:00'))

    @api.depends('check_out')
    def _compute_overtime_hours(self):
        """ Compute overtime working hours for each attendance record.
        Check-out over the working hours will be considered overtime in 1 hour increment.
        Overtime is divided into two tiers, with two models of payslip calculation.
        The first model is overtime for less than 4 hours. The second model is for 4 hours or more.
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
                    if str((int(check_in.strftime("%w")) + 6) % 7) == work_hours.dayofweek:
                        if (check_out.day - check_in.day) == 0 and check_out.hour >= work_hours.hour_to:
                            delta = check_out.hour + check_out.minute/float(60) - work_hours.hour_to
                        elif (check_out.day - check_in.day) == 1 and check_out.hour < (work_hours.hour_from - 1):
                            delta = check_out.hour + check_out.minute/float(60) + 24 - work_hours.hour_to
                        else:
                            delta = 0
                        if round(delta) < 4:
                            attendance.overtime_hours = round(delta)
                            attendance.overtime_hours_late = 0
                        else:
                            attendance.overtime_hours = 3
                            attendance.overtime_hours_late = round(delta) - 3

    @api.multi
    def get_working_days(self, employee_id, date_from, date_to):
        """ Compute working days between two dates on the input.
        Also return aggregated overtime work hours in each attendance record.
        Attendance records count between input dates are considered valid working days.
        Return a list with 3 data, number of attendance records and aggregated overtime work hours & late overtime
        """
        # get current logged in user's timezone
        local = pytz.timezone(self.env['res.users'].browse(self._uid).tz) or pytz.utc

        overtime_hours = 0
        overtime_hours_late = 0
        date_from_utc = local.localize(datetime.combine(datetime.strptime(date_from, '%Y-%m-%d'),time.min)).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        date_to_utc = local.localize(datetime.combine(datetime.strptime(date_to, '%Y-%m-%d'),time.max)).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        attendances = self.env['hr.attendance'].search([
                ('employee_id', '=', employee_id.id),
                ('check_in', '>=', date_from_utc),
                ('check_in', '<=', date_to_utc)
            ])
        for attendance in attendances:
            overtime_hours+=attendance['overtime_hours']
            overtime_hours_late+=attendance['overtime_hours_late']
        return [len(attendances),overtime_hours, overtime_hours_late]
    
    @api.multi
    def auto_check_out(self):
        """ Automatically check out attendances without checkout.
        Should be used with scheduled action.
        """
        no_check_out_attendances = self.env['hr.attendance'].search([
            ('check_out', '=', False),
        ])
        for attendance in no_check_out_attendances:
            local = pytz.timezone(self.env['res.users'].browse(self._uid).tz) or pytz.utc
            check_in = pytz.utc.localize(
                datetime.strptime(attendance.check_in, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local)
            today = pytz.utc.localize(datetime.today()).astimezone(local)
            if check_in.date() < today.date():
                attendance.check_out = check_in.replace(hour=17, minute=30, second=00).astimezone(pytz.utc)

    @api.multi
    def auto_create_leaves(self, check_days, leave_type):
        """ Automatically create leaves if no attendance and existing leave on working days. Check attendance for the last 'check_days' day(s)
        Should be used with scheduled action.
        """
        # get current logged in user's timezone
        local = pytz.timezone(self.env['res.users'].browse(self._uid).tz) or pytz.utc
        date_from_utc = local.localize(datetime.combine(datetime.strptime(fields.Date.context_today(self), '%Y-%m-%d')-timedelta(days=check_days), time.min))\
            .astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        active_employees = self.env['hr.employee'].search([
            ('active', '=', True),
        ])
        attendances = self.env['hr.attendance'].search([
                ('check_in', '>=', date_from_utc)
            ])
        leaves = self.env['hr.holidays'].search([
                '|',
                ('date_from', '>=', date_from_utc),
                ('date_to', '>=', date_from_utc)
            ])
        leave_type = self.env['hr.holidays.status'].search([
            ('name', 'ilike', leave_type)
        ], limit=1)
        for employee in active_employees:
            # Get this employee attendances and leaves record
            attendances_leaves = attendances.filtered(lambda emp: emp.employee_id == employee).mapped(
                            lambda r: [
                                pytz.utc.localize(datetime.strptime(r.check_in, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local).date(),
                                pytz.utc.localize(datetime.strptime(r.check_in, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local).date()
                            ] if r else []) + \
                        leaves.filtered(lambda emp: emp.employee_id == employee).mapped(
                             lambda r: [
                                 pytz.utc.localize(datetime.strptime(r.date_from, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local).date(),
                                 pytz.utc.localize(datetime.strptime(r.date_to, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local).date()
                             ]if r else [])
            work_days = employee.resource_calendar_id.mapped('attendance_ids')
            for i in range(check_days):
                date_check = (datetime.strptime(fields.Date.context_today(self), '%Y-%m-%d') - timedelta(days=i+1)).date()
                # Check whether the date already has attendance or leave record
                if str((int(date_check.strftime("%w")) + 6) % 7) in [week.dayofweek for week in work_days] and len(leave_type) == 1 and \
                        not (any(attendance_leave[0] <= date_check <= attendance_leave[1] for attendance_leave in attendances_leaves)):
                    # Create leave record
                    work_day = work_days.filtered(lambda r: r.dayofweek == str((int(date_check.strftime("%w")) + 6) % 7))
                    date_from = local.localize(datetime.combine(
                        date_check, time(hour=int(work_day.hour_from), minute=int((work_day.hour_from-int(work_day.hour_from))*60)))).astimezone(pytz.utc)
                    date_to = local.localize(datetime.combine(
                        date_check, time(hour=int(work_day.hour_to), minute=int((work_day.hour_to-int(work_day.hour_to))*60)))).astimezone(pytz.utc)
                    vals = {
                        'employee_id': employee.id,
                        'holiday_status_id': leave_type.id,
                        'date_from': date_from,
                        'date_to': date_to,
                        'name': 'Cuti Otomatis',
                        'number_of_days_temp': 1
                    }
                    self.env['hr.holidays'].create(vals)
