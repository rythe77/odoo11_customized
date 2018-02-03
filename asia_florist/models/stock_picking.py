# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class StockPicking(models.Model):
    """Add several fields as requested by Asia Florist"""
    _inherit = 'stock.picking'

    #Create new fields
    x_event_notes = fields.Char(
        'Event Name', index=False,
        states={'sale': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Input name of the event here")
    x_delivery_name = fields.Char(
        'Receiver Name', index=False,
        states={'sale': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Input the name of the package receiver here")
    x_delivery_address = fields.Char(
        'Delivery Address', index=False,
        states={'sale': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Input delivery address here")
    x_delivery_city = fields.Char(
        'City', index=False, default="Kendari",
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Input delivery city here")
    x_worker = fields.Char('Worker', index=False)
    x_driver = fields.Char('Driver', index=False)