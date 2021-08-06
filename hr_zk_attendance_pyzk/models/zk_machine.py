# -*- coding: utf-8 -*-
###################################################################################
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################
import pytz
from datetime import datetime, timedelta
import logging
import os
import platform
import subprocess

from odoo import api, fields, models
from odoo import _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
try:
    from zk import ZK, const
except ImportError:
    raise ImportError("Unable to import pyzk library. Try 'pip3 install pyzk'.")


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    device_id = fields.Char(string='Biometric Device ID')


class ZkMachine(models.Model):
    _name = 'zk.machine'

    name = fields.Char(string='Machine IP', required=True)
    port_no = fields.Integer(string='Port No', required=True, default="4370")
    address_id = fields.Many2one('res.partner', string='Working Address')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)
    zk_timeout = fields.Integer(string='ZK Timeout', required=True, default="120")
    zk_after_date = fields.Datetime(string='Attend Start Date',
                                    help='If provided, Attendance module will ignore records before this date.')
    zk_delete_after = fields.Integer(string='Delete After (days)', required=True, default="60",
                                     help='Delete attendance data that is more than X days old. put 0 for never delete')

    @api.multi
    def device_connect(self, zkobj):
        try:
            conn = zkobj.connect()
            return conn
        except Exception as e:
            _logger.info("zk.exception.ZKNetworkError: can't reach device.")
            #raise UserError(_("Connection To Device cannot be established."))
            return False

    @api.model
    def cron_set_time(self):
        machines = self.env['zk.machine'].search([])
        for machine in machines:
            machine.set_time()

    @api.multi
    def set_time(self):
        for info in self:
            zk = ZK(info.name, port=info.port_no, timeout=info.zk_timeout, password=0,
                    force_udp=False, ommit_ping=False)
            conn = self.device_connect(zk)
            if conn:
                local_tz = pytz.timezone(self.env.user.partner_id.tz or 'GMT')
                utc_dt = pytz.utc.localize(datetime.today(), is_dst=None)
                local_dt = utc_dt.astimezone(local_tz)
                conn.set_time(local_dt)
            else:
                _logger.info(
                    "zk.exception.ZKNetworkError: Unable to connect to Attendance Device. Please use Test Connection button to verify.")

    @api.multi
    def try_connection(self):
        for r in self:
            machine_ip = r.name
            if platform.system() == 'Linux':
                response = os.system("ping -c 1 " + machine_ip)
                if response == 0:
                    raise UserError(_("Biometric Device is Up/Reachable."))
                else:
                    raise UserError(_("Biometric Device is Down/Unreachable."))
            else:
                prog = subprocess.run(["ping", machine_ip], stdout=subprocess.PIPE)
                if 'unreachable' in str(prog):
                    raise UserError(_("Biometric Device is Down/Unreachable."))
                else:
                    raise UserError(_("Biometric Device is Up/Reachable."))

    @api.model
    def cron_clear_attendance(self):
        machines = self.env['zk.machine'].search([])
        for machine in machines:
            machine.clear_attendance()

    @api.multi
    def clear_attendance(self):
        # delete zk_machine_attendance record older than X days
        for info in self:
            if info.zk_delete_after <= 0:
                continue
            else:
                threshold_date = (datetime.now() - timedelta(days=info.zk_delete_after)). \
                    strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                to_delete = self.env['zk.machine.attendance'].search([
                    ('punching_time', '<', threshold_date)
                ])
                to_delete.unlink()

    @api.model
    def cron_download(self):
        machines = self.env['zk.machine'].search([])
        for machine in machines:
            machine.download_attendance()

    @api.multi
    def download_attendance(self):
        zk_attendance = self.env['zk.machine.attendance']
        att_obj = self.env['hr.attendance']
        for info in self:
            zk = ZK(info.name, port=info.port_no, timeout=info.zk_timeout, password=0,
                    force_udp=False, ommit_ping=False)
            conn = self.device_connect(zk)
            if conn:
                conn.disable_device()  # Device Cannot be used during this time.
                try:
                    attendance = conn.get_attendance()
                except Exception as e:
                    _logger.info("zk.exception.ZKNetworkError: can't get attendance from device." + e)
                    attendance = False
                if attendance:
                    for each in attendance:
                        atten_time = each.timestamp
                        atten_time = datetime.strptime(atten_time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
                        if atten_time is not False and atten_time > datetime.strptime(info.zk_after_date,
                                                                                      '%Y-%m-%d %H:%M:%S'):
                            local_tz = pytz.timezone(self.env.user.partner_id.tz or 'GMT')
                            local_dt = local_tz.localize(atten_time, is_dst=None)
                            utc_dt = local_dt.astimezone(pytz.utc)
                            utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
                            atten_time = datetime.strptime(utc_dt, "%Y-%m-%d %H:%M:%S")
                            tmp_utc = local_dt.astimezone(pytz.utc)
                            tmp_attend = tmp_utc.strftime("%m-%d-%Y %H:%M:%S")
                            tmp_local = local_dt.replace(hour=0, minute=0). \
                                astimezone(pytz.utc).strftime("%m-%d-%Y %H:%M:%S")
                            atten_time = fields.Datetime.to_string(atten_time)

                            get_user_id = self.env['hr.employee'].search([('device_id', '=', each.user_id)])
                            if get_user_id:
                                duplicate_atten_ids = zk_attendance.search(
                                    [('device_id', '=', each.user_id), ('punching_time', '=', atten_time)])
                                if duplicate_atten_ids:
                                    continue
                                else:
                                    zk_attendance.create({'employee_id': get_user_id.id,
                                                          'device_id': each.user_id,
                                                          'attendance_type': str(each.status),
                                                          'punch_type': str(each.punch),
                                                          'punching_time': atten_time,
                                                          'address_id': info.address_id.id})
                                    att_var = att_obj.search([('employee_id', '=', get_user_id.id),
                                                              ('check_out', '=', False)])

                                    if each.punch == 0:  # check-in
                                        if not att_var:
                                            attend_rec_tmp = att_obj.search(
                                                [('employee_id', '=', get_user_id.id), '|',
                                                 ('check_out', '>', tmp_attend),
                                                 ('check_in', '>', tmp_local)])
                                            if not attend_rec_tmp:
                                                att_obj.create({'employee_id': get_user_id.id,
                                                                'check_in': atten_time})
                                    if each.punch == 1:  # check-out
                                        if len(att_var) == 1:
                                            att_var.write({'check_out': atten_time})
                                        elif len(att_var) == 0:
                                            continue
                                        else:
                                            att_var1 = att_obj.search(
                                                [('employee_id', '=', get_user_id.id)])
                                            if att_var1:
                                                att_var1[-1].write({'check_out': atten_time})
                    conn.clear_attendance()
                    conn.test_voice()
                else:
                    _logger.info("zk.exception.ZKNetworkError: no attendance found in Attendance Device to Download.")
                conn.enable_device()
                conn.disconnect()
                return True
            else:
                _logger.info("zk.exception.ZKNetworkError: Unable to connect to Attendance Device. Please use Test Connection button to verify.")