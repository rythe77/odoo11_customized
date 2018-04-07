# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    #Create new fields
    credit_limit = fields.Monetary(string='Receivable Limit',
                                   help="Maximum credit that this customer is allowed for. If the current credit exceeds the limit, sale quotation confirmation is blocked. Zero limit means no limit")