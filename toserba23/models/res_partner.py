# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    #Create new fields
    x_call_freq = fields.Selection([
        ('urgent', 'Urgent'),
        ('less_urgent', 'Less Urgent'),
        ('common', 'common'),
        ('not_urgent', 'Not Urgent')],
        string='To Call', default='not_urgent',
       help="Show how urgent it is to call the customer")