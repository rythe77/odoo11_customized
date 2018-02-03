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
                    'x_transporter_note':sale_obj.x_transporter_note,
                    'x_salesperson_id':sale_obj.user_id.name,
                })
        return vals