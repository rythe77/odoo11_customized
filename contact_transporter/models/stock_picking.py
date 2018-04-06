# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    #Create new fields
    use_transporter = fields.Boolean(string='Use Transporter?', index=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)],
        'waiting_validation': [('readonly', True)]})
    transporter_id = fields.Many2one("res.partner",
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)],
        'waiting_validation': [('readonly', True)]})
    int_transporter_id = fields.Many2one("int.transporter",
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)],
        'waiting_validation': [('readonly', True)]})