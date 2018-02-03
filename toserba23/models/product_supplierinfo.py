# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'
    
    #Create new fields
    x_notes = fields.Char(
        'Other Notes', index=False)