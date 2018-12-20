# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError
import pytz

class RmaOutReceiveWizardLine(models.TransientModel):
    _name = "rmaout.receive.wizard.line"
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product', string="Product", domain="[('id', '=', product_id)]")
    name = fields.Char('Description', help="More precise description of the problem")
    quantity = fields.Float("Quantity", digits=dp.get_precision('Product Unit of Measure'))
    uom_id = fields.Many2one('product.uom', string='Unit of Measure')
    wizard_id = fields.Many2one('rmaout.receive.wizard', string="Wizard")
    rmaout_line_id = fields.Many2one('rma.rmaout.line', "RMA-OUT Line")

    @api.multi
    def _prepare_stock_moves(self, picking):
        self.ensure_one()
        res = []
        if self.rmaout_line_id.product_id.type not in ['product', 'consu']:
            return res
        template = {
            'name': self.rmaout_line_id.display_name or '',
            'date': self.rmaout_line_id.date,
            'date_expected': datetime.now(),
            'rmaout_line_id': self.rmaout_line_id.id,
            'location_id': picking.location_id.id,
            'location_dest_id': picking.location_dest_id.id,
            'picking_id': picking.id,
            'partner_id': picking.partner_id.id,
            'product_id': self.rmaout_line_id.product_id.id,
            'product_uom': self.rmaout_line_id.product_uom.id,
            'state': 'draft',
            'company_id': self.rmaout_line_id.rmaout_id.company_id.id,
            'picking_type_id': picking.picking_type_id.id,
            'origin': self.rmaout_line_id.rmaout_id.name,
            'route_ids': self.wizard_id.warehouse_id and [(6, 0, [x.id for x in self.wizard_id.warehouse_id.route_ids])] or [],
            'warehouse_id': self.wizard_id.warehouse_id.id,
            'product_desc':self.name,
        }
        if self.quantity < 0 or\
            self.quantity > self.rmaout_line_id.sent_qty - self.rmaout_line_id.refund_qty -\
            self.rmaout_line_id.received_qty - self.rmaout_line_id.qty_to_receive:
            raise UserError(_("You either input negative qty or qty greater than the quantity you should receive"))
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

    def _prepare_invoice_line(self, invoice):
        data = {
            'invoice_id': invoice.id,
            'rmaout_line_id': self.rmaout_line_id.id,
            'origin': self.rmaout_line_id.rmaout_id.code,
            'name': self.rmaout_line_id.product_id.name,
            'product_id': self.rmaout_line_id.product_id.id,
            'uom_id': self.rmaout_line_id.product_uom.id,
            'price_unit': self.rmaout_line_id.unit_purchase_price,
            'account_id': self.rmaout_line_id.product_id.product_tmpl_id._get_product_accounts()['stock_input'].id,
            'discount': 0.0,
        }
        if self.quantity < 0 or\
            self.quantity > self.rmaout_line_id.sent_qty - self.rmaout_line_id.refund_qty -\
            self.rmaout_line_id.received_qty - self.rmaout_line_id.qty_to_receive:
            raise UserError(_("You either input negative qty or qty greater than the quantity you should refund"))
        else:
            data['quantity'] = self.quantity
        return data

    @api.multi
    def _create_invoice_lines(self, invoice):
        new_lines = self.env['account.invoice.line']
        created = self.env['account.invoice.line'].browse()
        for line in self:
            data = line._prepare_invoice_line(invoice)
            new_line = new_lines.create(data)
            new_line._set_additional_fields(invoice)
            created += new_line
        return created


class RmaOutReceiveWizard(models.TransientModel):
    _name = "rmaout.receive.wizard"
    _description = "RMA-OUT Receive Wizard"

    rmaout_id = fields.Many2one('rma.rmaout')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    rmaout_receive_line = fields.One2many('rmaout.receive.wizard.line', 'wizard_id', 'Lines')

    @api.model
    def default_get(self, fields):
        if len(self.env.context.get('active_ids', list())) > 1:
            raise UserError(_("You may only create receive for a single RMA-OUT at a time!"))
        res = super(RmaOutReceiveWizard, self).default_get(fields)

        rmaout_receive_line = []
        rmaout = self.env['rma.rmaout'].browse(self.env.context.get('active_id'))
        if rmaout:
            res.update({'rmaout_id': rmaout.id, 'warehouse_id': rmaout.warehouse_id.id})
            if rmaout.state not in ['processing', 'closed']:
                raise UserError(_("You may only create receive for already sent goods"))
            for rma_line in rmaout.rmaout_line.filtered(lambda x: x.sent_qty - x.refund_qty - x.received_qty - x.qty_to_receive > 0):
                quantity = rma_line.sent_qty - rma_line.refund_qty - rma_line.received_qty - rma_line.qty_to_receive
                line_vals = {
                    'product_id': rma_line.product_id.id,
                    'name': rma_line.name,
                    'quantity': quantity,
                    'uom_id': rma_line.product_id.uom_id.id,
                    'rmaout_line_id': rma_line.id}
                rmaout_receive_line.append((0, 0, line_vals))
            res.update({'rmaout_receive_line': rmaout_receive_line})
        return res

    @api.model
    def _prepare_pickingin(self):
        return {
            'picking_type_id': self.warehouse_id.in_type_id.id,
            'partner_id': self.rmaout_id.partner_id.id,
            'date': fields.Datetime.now(),
            'origin': self.rmaout_id.code,
            'rmaout_id': self.rmaout_id.id,
            'location_dest_id': self.warehouse_id.in_type_id.default_location_dest_id.id,
            'location_id': self.rmaout_id.partner_id.property_stock_supplier.id,
            'company_id': self.rmaout_id.company_id.id,
        }

    def create_pickingin(self):
        self.ensure_one()
        stock_picking = self.env['stock.picking']
        if any([ptype in ['product', 'consu'] for ptype in self.rmaout_receive_line.mapped('rmaout_line_id.product_id.type')]):
            res = self._prepare_pickingin()
            picking = stock_picking.create(res)
            moves = self.rmaout_receive_line._create_stock_moves(picking)
            moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm(merge=False)
            seq = 0
            for move in sorted(moves, key=lambda move: move.date_expected):
                seq += 5
                move.sequence = seq
            moves._action_assign()
            picking.message_post_with_view('mail.message_origin_link',
                values={'self': picking, 'origin': self.rmaout_id},
                subtype_id=self.env.ref('mail.mt_note').id)
        return {}

    @api.model
    def _prepare_invoice(self):
        # get current logged in user's timezone
        local = pytz.timezone(self.env['res.users'].browse(self._uid).tz) or pytz.utc
        self.ensure_one()
        journal_id = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1).id
        if not journal_id:
            raise UserError(_('Please define an accounting purchase journal for this company.'))
        invoice_vals = {
            'name': self.rmaout_id.name or '',
            'origin': self.rmaout_id.code,
            'type': 'in_refund',
            'account_id': self.rmaout_id.partner_id.property_account_payable_id.id,
            'partner_id': self.rmaout_id.partner_id.id,
            'journal_id': journal_id,
            'currency_id': self.rmaout_id.company_id.currency_id.id,
            'company_id': self.rmaout_id.company_id.id,
            'rmaout_id': self.rmaout_id.id,
            'date_invoice':pytz.utc.localize(datetime.now()).astimezone(local).strftime('%Y-%m-%d'),
        }
        return invoice_vals

    def create_refund(self):
        self.ensure_one()
        inv_obj = self.env['account.invoice']
        if any(line.sent_qty - line.received_qty - line.refund_qty - line.qty_to_receive > 0\
               for line in self.rmaout_receive_line.mapped('rmaout_line_id')):
            inv_data = self._prepare_invoice()
            invoice = inv_obj.create(inv_data)
            self.rmaout_receive_line._create_invoice_lines(invoice)
        if not invoice:
            raise UserError(_('There is no invoicable line.'))
        else:
            # Necessary to force computation of taxes. In account_invoice, they are triggered
            # by onchanges, which are not triggered when doing a create.
            invoice.compute_taxes()
            invoice.message_post_with_view('mail.message_origin_link',
                values={'self': invoice, 'origin': self.rmaout_id},
                subtype_id=self.env.ref('mail.mt_note').id)
        return {}