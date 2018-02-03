# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class StockPicking(models.Model):
    """Add several fields as requested by Asia Florist"""
    _inherit = 'stock.picking'

    #Create new fields
    x_transporter_note = fields.Char(
        'Transporter Name', index=False,
        states={'sale': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Input the name of the package transporter here")
    x_salesperson_id = fields.Char(
        'Salesperson', index=False,
        states={'sale': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Input the name of the salesperson here")