# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    #Create new fields
    x_vehicle_notes = fields.Char(
        'Vehicle Notes', index=False,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)], 'waiting_validation': [('readonly', True)]})
    x_notes = fields.Char(
        'Other Notes', index=False,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)], 'waiting_validation': [('readonly', True)]})


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    count_picking_not_done = fields.Integer(compute='_compute_picking_count')
    count_picking_urgent = fields.Integer(compute='_compute_picking_count')
    count_picking_very_urgent = fields.Integer(compute='_compute_picking_count')

    def _compute_picking_count(self):
        super(StockPickingType,self)._compute_picking_count()
        domains = {
            'count_picking_not_done': [('state', 'not in', ('done', 'cancel'))],
            'count_picking_urgent': [('priority', '=', 2)],
            'count_picking_very_urgent': [('priority', '=', 3)],
        }
        for field in domains:
            data = self.env['stock.picking'].read_group(domains[field] +
                [('state', 'not in', ('done', 'cancel')), ('picking_type_id', 'in', self.ids)],
                ['picking_type_id'], ['picking_type_id'])
            count = {
                x['picking_type_id'][0]: x['picking_type_id_count']
                for x in data if x['picking_type_id']
            }
            for record in self:
                record[field] = count.get(record.id, 0)

    def get_action_picking_tree_not_done(self):
        return self._get_action('toserba23.action_picking_tree_not_done')

    def get_action_picking_tree_urgent(self):
        return self._get_action('toserba23.action_picking_tree_urgent')

    def get_action_picking_tree_very_urgent(self):
        return self._get_action('toserba23.action_picking_tree_very_urgent')