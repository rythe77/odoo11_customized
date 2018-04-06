# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class StockMove(models.Model):
    """Inheriting stock move is only for transferring fields value from SO to DO"""
    _inherit = 'stock.move'

    def _get_new_picking_values(self):
        vals = super(StockMove, self)._get_new_picking_values()
        for line in self:
            if line.sale_line_id and line.sale_line_id.order_id:
                sale_obj = line.sale_line_id.order_id
                vals.update({
                    'use_transporter': sale_obj.use_transporter,
                    'transporter_id': sale_obj.transporter_id.id,
                    'int_transporter_id': sale_obj.int_transporter_id.id,
                    })
        return vals