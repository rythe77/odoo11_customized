# -*- coding: utf-8 -*-

import base64
from io import BytesIO

import qrcode
from odoo import models, fields, api


class Employee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    @api.depends('employee_qr_code')
    def _generate_qr_code(self):
        for employee in self:
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=20, border=4)
            if employee.employee_qr_code:
                name = employee.employee_qr_code + '_employee.png'
                qr.add_data(employee.employee_qr_code)
                qr.make(fit=True)
                img = qr.make_image()
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                qrcode_img = base64.b64encode(buffer.getvalue())
                employee.update({'qr_code': qrcode_img, 'qr_code_name': name})

    employee_qr_code = fields.Char('QR Code', related='barcode')
    qr_code = fields.Binary('QR Code', compute="_generate_qr_code")
    qr_code_name = fields.Char(default="qr_code.png")