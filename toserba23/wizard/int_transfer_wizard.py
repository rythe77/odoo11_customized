# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError

class IntTransferWizardLine(models.TransientModel):
    _name = "int.transfer.wizard.line"
    _description = "Internal Transfer Wizard Line"

    product_id = fields.Many2one('product.product', string="Produk", required=True)
    description = fields.Char('Deskripsi', help="Deskripsi produk")
    quantity = fields.Float("Kuantitas", digits=dp.get_precision('Product Unit of Measure'), required=True)
    product_uom = fields.Many2one('product.uom', string='Satuan', required=True)
    wizard_id = fields.Many2one('int.transfer.wizard', string="Wisaya Transfer Internal")

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.product_uom = self.product_id.uom_id.id
        return {'domain': {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}}

    @api.onchange('product_uom')
    def onchange_product_uom(self):
        if self.product_uom != self.product_id.uom_id:
            raise UserError(
                'Anda mengubah satuan standar produk. Sangat tidak disarankan untuk melakukan hal ini')

    @api.multi
    def _prepare_stock_moves(self, picking):
        self.ensure_one()
        res = []
        if self.product_id.type not in ['product', 'consu']:
            return res
        template = {
            'name': self.product_id.name or '',
            'date_expected': picking.scheduled_date,
            'location_id': picking.location_id.id,
            'location_dest_id': picking.location_dest_id.id,
            'picking_id': picking.id,
            'partner_id': picking.partner_id.id,
            'product_id': self.product_id.id,
            'product_uom_qty': self.quantity,
            'product_uom': self.product_uom.id,
            'state': 'draft',
            'picking_type_id': picking.picking_type_id.id,
            'product_desc': self.description,
        }
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


class IntTransferWizard(models.TransientModel):
    _name = "int.transfer.wizard"
    _description = "Internal Transfer Wizard"

    @api.model
    def _get_default_partner(self):
        return self.env['res.partner'].search([('name', '=', 'Toserba 23'), ('customer', '=', True)], limit=1)

    partner_id = fields.Many2one('res.partner', string='Rekanan', default=_get_default_partner, required=True)
    scheduled_date = fields.Datetime('Tanggal Terjadwal', default=fields.Datetime.now)
    source_warehouse_id = fields.Many2one('stock.warehouse', string='Gudang Asal', required=True)
    dest_warehouse_id = fields.Many2one('stock.warehouse', string='Gudang Tujuan', required=True)
    int_transporter = fields.Many2one('int.transporter', string='Pengantaran')
    vehicle = fields.Char('Kendaraan')
    other_notes = fields.Char('Ketarangan Lain', default="Transfer Internal")
    int_transfer_line = fields.One2many('int.transfer.wizard.line', 'wizard_id', 'Baris')

    @api.model
    def _prepare_pickingout(self):
        return {
            'picking_type_id': self.source_warehouse_id.out_type_id.id,
            'partner_id': self.partner_id.id,
            'scheduled_date': self.scheduled_date,
            'location_dest_id': self.partner_id.property_stock_customer.id,
            'location_id': self.source_warehouse_id.out_type_id.default_location_src_id.id,
            'int_transporter_id': self.int_transporter.id,
            'x_vehicle_notes': self.vehicle,
            'x_notes': self.other_notes
        }

    def create_pickingout(self):
        self.ensure_one()
        stock_picking = self.env['stock.picking']
        vals = self._prepare_pickingout()
        picking = stock_picking.create(vals)
        moves = self.int_transfer_line._create_stock_moves(picking)
        moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm(merge=False)
        seq = 0
        for move in sorted(moves, key=lambda move: move.date_expected):
            seq += 5
            move.sequence = seq
        moves._action_assign()
        return picking

    @api.model
    def _prepare_pickingin(self):
        return {
            'picking_type_id': self.dest_warehouse_id.in_type_id.id,
            'partner_id': self.partner_id.id,
            'scheduled_date': self.scheduled_date,
            'location_dest_id': self.dest_warehouse_id.in_type_id.default_location_dest_id.id,
            'location_id': self.partner_id.property_stock_customer.id,
            'int_transporter_id': self.int_transporter.id,
            'x_vehicle_notes': self.vehicle,
            'x_notes': self.other_notes
        }

    def create_pickingin(self):
        self.ensure_one()
        stock_picking = self.env['stock.picking']
        vals = self._prepare_pickingin()
        picking = stock_picking.create(vals)
        moves = self.int_transfer_line._create_stock_moves(picking)
        moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm(merge=False)
        seq = 0
        for move in sorted(moves, key=lambda move: move.date_expected):
            seq += 5
            move.sequence = seq
        moves._action_assign()
        return picking

    @api.multi
    def button_create_picking(self):
        picking_in = self.create_pickingin()
        picking_out = self.create_pickingout()
        if picking_in and picking_out:
            picking_in.x_notes = str(picking_in.x_notes) + '(' + picking_out.name + ')'
            picking_out.x_notes = str(picking_out.x_notes) + '(' + picking_in.name + ')'
