# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
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

    @api.multi
    def action_done(self):
        """
            Do not allow validation for non-manager if this picking is not related to SO or PO or RMA
        """
        return_val = super(StockPicking, self).action_done()
        for rec in self:
            if not rec.sale_id and not rec.purchase_id  and not rec.rmain_id and not rec.rmaout_id\
            and not self.env['res.users'].browse(self.env.uid).has_group('stock.group_stock_manager'):
                raise UserError('Anda hanya diijinkan untuk memvalidasi transfer yang dibuat dari penjualan/pembelian atau RMA')
            # Send email notification to customer
            if rec.partner_id.customer and rec.partner_id.x_is_notify_do and rec.partner_id.x_notification_method == "email":
                rec.action_send_email()
        return return_val

    @api.multi
    def action_force_status(self):
        self.state = 'done'
        return True

    @api.multi
    def action_send_email(self):
        for item in self:
            # Find the e-mail template
            template = self.env.ref('toserba23.delivery_email_template')
            # Send out the e-mail template to the user
            self.env['mail.template'].browse(template.id).send_mail(item.id)
            # Log a note to the sale order record
            item.message_post(body="Email notifikasi pengiriman sudah dikirimkan ke pelanggan")


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