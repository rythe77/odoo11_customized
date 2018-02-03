# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'
    
    #Create new fields
    x_notes = fields.Char(
        'Other Notes', index=False)