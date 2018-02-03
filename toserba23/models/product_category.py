# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductCategory(models.Model):
    _inherit = 'product.category'
    
    # Create new fields
    is_warranty = fields.Boolean(string='Barang Garansi', index=False, default=True)