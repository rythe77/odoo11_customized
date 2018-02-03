# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import re


class StockPicking(models.Model):
    """Store sequence number to be used """
    _inherit = 'stock.picking'

    #Create new fields
    sequence_number_copy = fields.Char(
        'Sequence Number', index=False, store=True, compute='_get_sequence_number')

    @api.depends('name')
    def _get_sequence_number(self):
        for picking in self:
            name = picking.name
            extracted_number = re.findall('\d+', name)
            if extracted_number:
                picking.sequence_number_copy = extracted_number[len(extracted_number)-1]

    def action_generate_backorder_wizard(self):
        result = super(StockPicking,self).action_generate_backorder_wizard()
        self.action_done()
        return


class StockReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    @api.multi
    def _create_returns(self):
        new_picking_id, pick_type_id = super(StockReturnPicking, self)._create_returns()
        new_picking = self.env['stock.picking'].browse([new_picking_id])
        for move in new_picking.move_lines:
            return_picking_line = self.product_return_moves.filtered(lambda r: r.move_id == move.origin_returned_move_id)
            if return_picking_line:
                move.to_refund = True
        return new_picking_id, pick_type_id
