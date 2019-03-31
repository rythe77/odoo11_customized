# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError

class RmaInIntTransferWizardLine(models.TransientModel):
    _name = "rma.int.transfer.wizard.line"
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product', string="Product", domain="[('id', '=', product_id)]")
    name = fields.Char('Description', help="More precise description of the problem")
    quantity = fields.Float("Quantity", digits=dp.get_precision('Product Unit of Measure'))
    uom_id = fields.Many2one('product.uom', string='Unit of Measure')
    wizard_id = fields.Many2one('rma.int.transfer.wizard', string="Wizard")
    rmain_line_id = fields.Many2one('rma.rma.line', "RMA-IN Line")

    @api.multi
    def _prepare_stock_moves(self, picking):
        self.ensure_one()
        res = []
        if self.rmain_line_id.product_id.type not in ['product', 'consu']:
            return res
        template = {
            'name': self.rmain_line_id.display_name or '',
            'date': self.rmain_line_id.date,
            'date_expected': datetime.now(),
            'rmain_line_id': self.rmain_line_id.id,
            'location_id': picking.location_id.id,
            'location_dest_id': picking.location_dest_id.id,
            'picking_id': picking.id,
            'partner_id': picking.partner_id.id,
            'product_id': self.product_id.id,
            'product_uom': self.uom_id.id,
            'state': 'draft',
            'company_id': self.rmain_line_id.rma_id.company_id.id,
            'picking_type_id': picking.picking_type_id.id,
            'origin': self.rmain_line_id.rma_id.name,
            'route_ids': self.wizard_id.src_warehouse_id and [(6, 0, [x.id for x in self.wizard_id.src_warehouse_id.route_ids])] or [],
            'warehouse_id': self.wizard_id.src_warehouse_id.id,
            'product_desc':self.name,
        }
        if self.quantity < 0 or self.quantity > self.rmain_line_id.received_qty:
            raise UserError(_("You either input negative qty or qty greater than the quantity you should send"))
        else:
            template['product_uom_qty'] = self.quantity
            res.append(template)
        return res

    @api.multi
    def _create_stock_moves(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self:
            for val in line._prepare_stock_moves(picking):
                done += moves.create(val)
        return done


class RmaInIntTransferWizard(models.TransientModel):
    _name = "rma.int.transfer.wizard"
    _description = "RMA-IN Internal Transfer Wizard"

    rmain_id = fields.Many2one('rma.rma')
    src_warehouse_id = fields.Many2one('stock.warehouse', string='Source Warehouse')
    dst_warehouse_id = fields.Many2one('stock.warehouse', string='Destination Warehouse')
    rmain_transfer_line = fields.One2many('rma.int.transfer.wizard.line', 'wizard_id', 'Lines')

    @api.model
    def default_get(self, fields):
        if len(self.env.context.get('active_ids', list())) > 1:
            raise UserError(_("You may only create transfer for a single RMA-IN at a time!"))
        res = super(RmaInIntTransferWizard, self).default_get(fields)

        rmain_transfer_line = []
        rmain = self.env['rma.rma'].browse(self.env.context.get('active_id'))
        if rmain:
            res.update({
                    'rmain_id': rmain.id,
                    'src_warehouse_id': rmain.warehouse_id.id,
                    'dst_warehouse_id': rmain.warehouse_id.id,
                    })
            if rmain.state not in ['processing', 'closed']:
                raise UserError(_("You may only create transfer for processing lines"))
            for rma_line in rmain.rma_line:
                line_vals = {
                    'product_id': rma_line.product_id.id,
                    'name': rma_line.name,
                    'quantity': rma_line.received_qty,
                    'uom_id': rma_line.product_uom.id,
                    'rmain_line_id': rma_line.id}
                rmain_transfer_line.append((0, 0, line_vals))
            res.update({'rmain_transfer_line': rmain_transfer_line})
        return res

    @api.model
    def _prepare_picking(self):
        return {
            'picking_type_id': self.src_warehouse_id.int_type_id.id,
            'partner_id': self.rmain_id.partner_id.id,
            'date': fields.Datetime.now(),
            'origin': self.rmain_id.code,
            'rmain_id': self.rmain_id.id,
            'location_dest_id': self.dst_warehouse_id.int_type_id.default_location_dest_id.id,
            'location_id': self.src_warehouse_id.int_type_id.default_location_src_id.id,
            'company_id': self.rmain_id.company_id.id,
        }

    def create_picking(self):
        self.ensure_one()
        stock_picking = self.env['stock.picking']
        if any([ptype in ['product', 'consu'] for ptype in self.rmain_transfer_line.mapped('rmain_line_id.product_id.type')]):
            res = self._prepare_picking()
            picking = stock_picking.create(res)
            moves = self.rmain_transfer_line._create_stock_moves(picking)
            moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm(merge=False)
            seq = 0
            for move in sorted(moves, key=lambda move: move.date_expected):
                seq += 5
                move.sequence = seq
            moves._action_assign()
            picking.message_post_with_view('mail.message_origin_link',
                values={'self': picking, 'origin': self.rmain_id},
                subtype_id=self.env.ref('mail.mt_note').id)
        return {}