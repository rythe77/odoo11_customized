# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductCategory(models.Model):
    _inherit = 'product.category'
    
    # Create new fields
    is_warranty = fields.Boolean(string='Barang Garansi', index=False, default=True)
    responsible_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.uid, required=True)
