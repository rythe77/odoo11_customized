# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Product(models.Model):
    _inherit = 'product.template'

    sale_priority = fields.Selection([
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')],
        string='Sale Priority', default='medium',
        help="Product with higher priority should be prioritized in sales")
    sale_type = fields.Selection([
        ('order', 'Order'),
        ('normal', 'Normal'),
        ('clearance', 'Clearance'),
        ('archive', 'Archive')],
        string='Sale Type', default='normal',
        help='An order product is product that is ordered after sale quotation.\n'
             'A normal product is a ready stock product.\n'
             'A clearance product is product must be cleared as soon as possible.\n'
             'An archive product is product which will be archived soon.')
