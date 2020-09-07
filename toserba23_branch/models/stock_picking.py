# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
import time

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    #Create new fields
    x_notes = fields.Char(
        'Keterangan', index=False,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)], 'waiting_validation': [('readonly', True)]})
