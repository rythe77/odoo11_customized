# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('waiting_validation', 'Tunggu Validasi'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, track_visibility='onchange',
        help=" * Draft: not confirmed yet and will not be scheduled until confirmed.\n"
             " * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows).\n"
             " * Waiting: if it is not ready to be sent because the required products could not be reserved.\n"
             " * Ready: products are reserved and ready to be sent. If the shipping policy is 'As soon as possible' this happens as soon as anything is reserved.\n"
             " * Waiting Validation: transfer confirmed, waiting for validation.\n"
             " * Done: has been processed, can't be modified or cancelled anymore.\n"
             " * Cancelled: has been cancelled, can't be confirmed anymore.")
    move_type = fields.Selection([
        ('direct', 'As soon as possible'), ('one', 'When all products are ready')], 'Shipping Policy',
        default='direct', required=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)], 'waiting_validation': [('readonly', True)]},
        help="It specifies goods to be deliver partially or all at once")
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        required=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)], 'waiting_validation': [('readonly', True)], 'assigned': [('readonly', True)]})
    partner_id = fields.Many2one(
        'res.partner', 'Partner',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)], 'waiting_validation': [('readonly', True)], 'assigned': [('readonly', True)]})
    scheduled_date = fields.Datetime(
        'Scheduled Date', compute='_compute_scheduled_date', inverse='_set_scheduled_date', store=True,
        index=True, track_visibility='onchange',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)], 'waiting_validation': [('readonly', True)]},
        help="Scheduled time for the first part of the shipment to be processed. Setting manually a value here would set it as expected date for all the stock moves.")
    origin = fields.Char(
        'Source Document', index=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)], 'waiting_validation': [('readonly', True)]},
        help="Reference of the document")
    
    #Create new field
    show_do_transfer = fields.Boolean(
        compute='_compute_show_do_transfer',
        help='Technical field used to compute whether the do transfer should be shown.')
    show_redo_transfer = fields.Boolean(
        compute='_compute_show_redo_transfer',
        help='Technical field used to compute whether the redo transfer should be shown.')

    @api.multi
    @api.depends('state', 'is_locked')
    def _compute_show_validate(self):
        for picking in self:
            if self._context.get('planned_picking') and picking.state == 'draft':
                picking.show_validate = False
            elif picking.state != 'waiting_validation' or not picking.is_locked:
                picking.show_validate = False
            else:
                picking.show_validate = True

    @api.multi
    @api.depends('state', 'is_locked')
    def _compute_show_do_transfer(self):
        for picking in self:
            if self._context.get('planned_picking') and picking.state == 'draft':
                picking.show_do_transfer = False
            elif picking.state != 'assigned' or not picking.is_locked:
                picking.show_do_transfer = False
            else:
                picking.show_do_transfer = True

    @api.multi
    @api.depends('state', 'is_locked')
    def _compute_show_redo_transfer(self):
        for picking in self:
            if self._context.get('planned_picking') and picking.state == 'draft':
                picking.show_redo_transfer = False
            elif picking.state != 'waiting_validation' or not picking.is_locked:
                picking.show_redo_transfer = False
            else:
                picking.show_redo_transfer = True

    @api.multi
    def action_transfer(self):
        for picking in self:
            if picking.state == 'assigned':
                picking.state = 'waiting_validation'
        return True

    @api.multi
    def redo_transfer(self):
        for picking in self:
            if picking.state == 'waiting_validation':
                picking.state = 'assigned'
        return True


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    count_picking_waiting_validation = fields.Integer(compute='_compute_picking_count')

    def _compute_picking_count(self):
        super(StockPickingType,self)._compute_picking_count()
        domains = {
            'count_picking_waiting_validation': [('state', '=', 'waiting_validation')],
            'count_picking': [('state', 'in', ('assigned', 'waiting', 'waiting_validation', 'confirmed'))],
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
        for record in self:
            record.rate_picking_late = record.count_picking and record.count_picking_late * 100 / record.count_picking or 0
            record.rate_picking_backorders = record.count_picking and record.count_picking_backorders * 100 / record.count_picking or 0

    def get_action_picking_tree_waiting_validation(self):
        return self._get_action('stock_picking_validation.action_picking_tree_waiting_validation')