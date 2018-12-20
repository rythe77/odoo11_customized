# -*- coding: utf-8 -*-
# © 2018 Ryanto The

from odoo import _, api, fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    lot_rma_id = fields.Many2one('stock.location', 'RMA Location')
    rma_out_type_id = fields.Many2one('stock.picking.type', 'RMA Out Type')
    rma_in_type_id = fields.Many2one('stock.picking.type', 'RMA In Type')
    rma_int_type_id = fields.Many2one('stock.picking.type', 'RMA Internal Type')