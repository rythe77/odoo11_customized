from odoo import models, fields, api

class IntTransporter(models.Model):
    _name = 'int.transporter'
    
    name = fields.Char(string='Name', required=True, index=True)
    reg_number = fields.Char(string='Registration Number', required=True)
    contact = fields.Char(string='Contact Number')
    responsible_id = fields.Many2one('hr.employee', string='Responsible', required=True)