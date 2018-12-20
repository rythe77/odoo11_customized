# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    #Create new fields
    description = fields.Text()