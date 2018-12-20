# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError

class RmaInSendWizardLine(models.TransientModel):
    _name = "rma.send.wizard.line"
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product', string="Product", domain="[('id', '=', product_id)]")
    name = fields.Char('Description', help="More precise description of the problem")
    quantity = fields.Float("Quantity", digits=dp.get_precision('Product Unit of Measure'))
    uom_id = fields.Many2one('product.uom', string='Unit of Measure')
    wizard_id = fields.Many2one('rma.send.wizard', string="Wizard")
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
            'route_ids': self.wizard_id.warehouse_id and [(6, 0, [x.id for x in self.wizard_id.warehouse_id.route_ids])] or [],
            'warehouse_id': self.wizard_id.warehouse_id.id,
            'product_desc':self.name,
        }
        diff_product = True if self.rmain_line_id.action == 'replace'\
                        and self.rmain_line_id.product_id != self.rmain_line_id.replace_product_id else False
        if not diff_product:
            if self.quantity < 0 or\
                    self.quantity > self.rmain_line_id.received_qty - self.rmain_line_id.refund_qty -\
                    self.rmain_line_id.replaced_qty - self.rmain_line_id.qty_to_send:
                raise UserError(_("You either input negative qty or qty greater than the quantity you should send"))
            else:
                template['product_uom_qty'] = self.quantity
                res.append(template)
        else:
            if self.quantity < 0 or self.quantity != self.rmain_line_id.replace_product_qty:
                raise UserError(_("You either input negative qty or qty different than the replacement plan"))
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


class RmaInSendWizard(models.TransientModel):
    _name = "rma.send.wizard"
    _description = "RMA-IN Send Wizard"

    rmain_id = fields.Many2one('rma.rma')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    rmain_send_line = fields.One2many('rma.send.wizard.line', 'wizard_id', 'Lines')

    @api.model
    def default_get(self, fields):
        if len(self.env.context.get('active_ids', list())) > 1:
            raise UserError(_("You may only create transfer for a single RMA-IN at a time!"))
        res = super(RmaInSendWizard, self).default_get(fields)

        rmain_send_line = []
        rmain = self.env['rma.rma'].browse(self.env.context.get('active_id'))
        if rmain:
            res.update({'rmain_id': rmain.id, 'warehouse_id': rmain.warehouse_id.id})
            if rmain.state not in ['processing']:
                raise UserError(_("You may only create transfer for processing lines"))
            for rma_line in rmain.rma_line.filtered(lambda x: x.action in ['replace', 'replace_part', 'repair']):
                diff_product = True if rma_line.action == 'replace' and rma_line.product_id != rma_line.replace_product_id else False
                if not diff_product and rma_line.received_qty - rma_line.refund_qty - rma_line.replaced_qty - rma_line.qty_to_send > 0:
                    quantity = rma_line.received_qty - rma_line.refund_qty - rma_line.replaced_qty - rma_line.qty_to_send
                    line_vals = {
                        'product_id': rma_line.product_id.id,
                        'name': rma_line.name,
                        'quantity': quantity,
                        'uom_id': rma_line.product_id.uom_id.id,
                        'rmain_line_id': rma_line.id}
                    rmain_send_line.append((0, 0, line_vals))
                elif diff_product and rma_line.replace_product_qty - rma_line.replaced_qty > 0:
                    quantity = rma_line.replace_product_qty - rma_line.replaced_qty
                    line_vals = {
                        'product_id': rma_line.replace_product_id.id,
                        'name': rma_line.name,
                        'quantity': quantity,
                        'uom_id': rma_line.replace_product_uom.id,
                        'rmain_line_id': rma_line.id}
                    rmain_send_line.append((0, 0, line_vals))
            res.update({'rmain_send_line': rmain_send_line})
        return res

    @api.model
    def _prepare_pickingout(self):
        return {
            'picking_type_id': self.warehouse_id.out_type_id.id,
            'partner_id': self.rmain_id.partner_id.id,
            'date': fields.Datetime.now(),
            'origin': self.rmain_id.code,
            'rmain_id': self.rmain_id.id,
            'location_dest_id': self.rmain_id.partner_id.property_stock_customer.id,
            'location_id': self.warehouse_id.out_type_id.default_location_src_id.id,
            'company_id': self.rmain_id.company_id.id,
        }

    def create_pickingout(self):
        self.ensure_one()
        stock_picking = self.env['stock.picking']
        if any([ptype in ['product', 'consu'] for ptype in self.rmain_send_line.mapped('rmain_line_id.product_id.type')]):
            res = self._prepare_pickingout()
            picking = stock_picking.create(res)
            moves = self.rmain_send_line._create_stock_moves(picking)
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