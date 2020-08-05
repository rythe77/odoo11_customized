from odoo import api, fields, models, _

class HrBenefit(models.Model):
    _name = 'hr.benefit'
    _description = 'Benefit structure of the payroll'

    name = fields.Char(string='Benefit Name', required=True)
    amount = fields.Float(string='Benefit Amount')
    description = fields.Char(string='Description')

class HrLevel(models.Model):
    _name = 'hr.level'
    _description = 'Level structure of the payroll'

    name = fields.Char(string='Level', required=True)
    amount = fields.Float(string='Basic Amount')
    description = fields.Char(string='Description')