# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class StockMove(models.Model):
    """Add several fields as requested by Asia Florist
        Inheriting stock move is only for transferring fields value from SO to DO"""
    _inherit = 'stock.move'
    
    #Create new fields
    product_desc = fields.Char(
        'Specific Request', index=False, store=True,
        help="Special request from customer regarding the purchase of this product")
