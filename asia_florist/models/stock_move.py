# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class StockMove(models.Model):
    """Add several fields as requested by Asia Florist
        Inheriting stock move is only for transferring fields value from SO to DO"""
    _inherit = 'stock.move'

    #Modify new fields
    product_desc = fields.Text(
        'Specific Request', index=False, store=True,
        help="Special request from customer regarding the purchase of this product")

    def _get_new_picking_values(self):
        vals = super(StockMove, self)._get_new_picking_values()
        for line in self:
            if line.sale_line_id and line.sale_line_id.order_id:
                sale_obj = line.sale_line_id.order_id
                vals.update({
                    'x_event_notes': sale_obj.x_event_notes,
                    'x_delivery_name': sale_obj.x_delivery_name,
                    'x_delivery_address': sale_obj.x_delivery_address,
                    'x_delivery_city': sale_obj.x_delivery_city,
                    })
        return vals