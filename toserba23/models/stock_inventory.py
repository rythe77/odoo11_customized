# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError

class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    #Create new fields
    x_notes = fields.Text(string='Keterangan')