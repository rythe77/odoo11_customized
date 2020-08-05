# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime

from odoo import _, api, exceptions, fields, models
from odoo.tools import (DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT)
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero, float_compare
import pytz


class RmaRma(models.Model):
    _name = "rma.rmaout"
    _description = "RMA-OUT"
    _order = "date desc"
    _inherit = ['mail.thread']

    @api.depends('rmaout_line.state', 'rmaout_line.process_status')
    @api.one
    def _compute_state(self):
        ''' State of a rma depends on the state of its related rma.line
        - Draft: only used for "planned rma"
        - Confirmed: if the rma is confirmed and product is ready to be send
        - Processing: if the product is sent and ready to be processed
        - Closed: if the rma is done.
        - Rejected: if the rma is rejected
        '''
        if not self.rmaout_line:
            self.state = 'draft'
        elif all(rma_line.state == 'draft' for rma_line in self.rmaout_line):
            self.state = 'draft'
        elif all(rma_line.state == 'rejected' for rma_line in self.rmaout_line):
            self.state = 'rejected'
        elif all(rma_line.state == 'confirmed' and rma_line.process_status == 'to_process' for rma_line in self.rmaout_line):
            self.state = 'confirmed'
        elif all(rma_line.state == 'confirmed' and rma_line.process_status == 'done' for rma_line in self.rmaout_line):
            self.state = 'closed'
        else:
            self.state = 'processing'

    code = fields.Char(string='RMA Number', required=True, default="/", readonly=True, copy=False)
    _sql_constraints = [
        ('rma_unique_code', 'UNIQUE (code)',
         'The code must be unique!'),
    ]

    @api.depends('rmain_ids')
    @api.one
    def _compute_rmain(self):
        for rma in self:
            rma.rmain_count = len(rma.rmain_ids)

    @api.depends('rmaout_line.rmain_line_id')
    @api.one
    def _compute_rmain_ids(self):
        for rma in self:
            rmain_id_to_append = []
            for rma_line in rma.rmaout_line:
                if rma_line.rmain_line_id and rma_line.rmain_line_id.rma_id.mapped('id')[0] not in rmain_id_to_append:
                    rmain_id_to_append.append(rma_line.rmain_line_id.rma_id.mapped('id')[0])
            self.update({
                'rmain_ids': [(6,0,rmain_id_to_append)]
                })

    @api.multi
    def action_view_rmain(self):
        rmains = self.mapped('rmain_ids')
        action = self.env.ref('rma_rythe.rma_rma_view_act').read()[0]
        if len(rmains) > 1:
            action['domain'] = [('id', 'in', rmains.ids)]
        elif len(rmains) == 1:
            action['views'] = [(self.env.ref('rma_rythe.rma_rma_form_view').id, 'form')]
            action['res_id'] = rmains.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    rmain_count = fields.Integer(string='RMA-IN', compute='_compute_rmain', readonly=True, copy=False)
    rmain_ids = fields.Many2many('rma.rma', compute='_compute_rmain_ids', store=True, string='Related RMA-IN')
    name = fields.Char('Subject', required=True, readonly=True, states={'draft': [('readonly', False)]})
    user_id = fields.Many2one('res.users', 'Responsible', required=True, track_visibility='always',default=lambda self: self.env.user)
    date = fields.Datetime('RMA Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)]}, copy=False, default=fields.Datetime.now)
    date_closed = fields.Datetime('Closed', compute='_compute_date_closed', store=True, readonly=True)
    partner_id = fields.Many2one('res.partner', 'Partner', required=True, readonly=True, states={'draft': [('readonly', False)]})
    partner_email = fields.Char('Email', size=128, help="Partner email", states={'rejected': [('readonly', True)], 'closed': [('readonly', True)]})
    partner_phone = fields.Char('Phone', states={'rejected': [('readonly', True)], 'closed': [('readonly', True)]})
    state = fields.Selection([
        ('rejected', 'Rejected'),
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('closed', 'Closed'),
        ], string='Status', compute='_compute_state', store=True, readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    note = fields.Text('RMA Note', states={'rejected': [('readonly', True)], 'closed': [('readonly', True)]})

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self, email=False):
        if not self.partner_id:
            return {'value': {'partner_email': False, 'partner_phone': False, 'name': False}}
        address = self.env['res.partner'].browse(self.partner_id.id)
        return {'value': {'partner_email': address.email, 'partner_phone': address.mobile, 'name': self.partner_id.name}}

    @api.model
    def create(self, vals):
        if vals.get('code', '/') == '/':
            vals['code'] = self.env['ir.sequence'].next_by_code('rma.rma.supplier')
        return super(RmaRma, self).create(vals)

    @api.multi
    def unlink(self):
        for rma in self:
            if not rma.state == 'rejected':
                raise UserError(_('In order to delete a RMA, you must cancel it first.'))
        return super(RmaRma, self).unlink()

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        if 'code' not in default:
            default['code'] = self.env['ir.sequence'].next_by_code('rma.rma.supplier')
        raise UserError(_('Copying document disabled.'))
        return super(RmaRma, self).copy(default)

    def _get_default_warehouse(self):
        company_id = self.env.user.company_id.id
        wh_obj = self.env['stock.warehouse']
        wh = wh_obj.search([('company_id', '=', company_id)], limit=1)
        if not wh:
            raise exceptions.UserError(
                _('There is no warehouse for the current user\'s company.')
            )
        return wh

    @api.depends('state')
    @api.one
    def _compute_date_closed(self):
        for rma in self:
            if rma.state == 'closed':
                rma.update({
                    'date_closed': fields.Datetime.now()
                    })

    @api.depends('picking_ids')
    @api.one
    def _compute_picking(self):
        for rma in self:
            pickings = rma.picking_ids
            rma.picking_count = len(pickings)

    @api.depends('invoice_ids')
    @api.one
    def _compute_invoice(self):
        for rma in self:
            invoices = rma.invoice_ids
            rma.invoice_count = len(invoices)

    @api.multi
    def name_get(self):
        res = []
        for rma in self:
            code = rma.code and str(rma.code) or ''
            res.append((rma.id, '[' + code + '] ' + rma.name))
        return res

    @api.depends('rmaout_line.sent_qty', 'rmaout_line.received_qty', 'rmaout_line.refund_qty')
    def _compute_show_button_receive_refund(self):
        for rma in self:
            if rma.state == 'processing':
                if any([line.sent_qty > line.received_qty + line.refund_qty + line.qty_to_receive\
                        for line in rma.rmaout_line]):
                    self.show_button_receive_refund = True
                else:
                    self.show_button_receive_refund = False
            else:
                self.show_button_receive_refund = False

    company_id = fields.Many2one('res.company', change_default=True, default=lambda self: self.env['res.company']._company_default_get('rma_rythe'))
    rmaout_line = fields.One2many('rma.rmaout.line', 'rmaout_id', string='RMA Lines', readonly=True, states={'draft': [('readonly', False)]}, copy=True, auto_join=True)
    rmaout_line_follow = fields.One2many(related='rmaout_line', string='RMA Lines Follow Up', readonly=True, copy=True, auto_join=True)
    invoice_count = fields.Integer(string='# of Invoices', compute='_compute_invoice', readonly=True, copy=False)
    invoice_ids = fields.One2many('account.invoice', 'rmaout_id', 'Refunds', copy=False)
    picking_count = fields.Integer(compute='_compute_picking', string='Receptions', default=0, store=True, copy=False)
    picking_ids = fields.One2many('stock.picking', 'rmaout_id', string='Related Stock Picking', copy=False)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', required=True, default=_get_default_warehouse)
    group_id = fields.Many2one('procurement.group', string="Procurement Group", copy=False)
    show_button_receive_refund = fields.Boolean(compute="_compute_show_button_receive_refund", default=False)

    @api.multi
    def action_status(self):
        for item in self:
            item.state = 'closed'

    @api.multi
    def button_draft(self):
        for rma in self:
            rma.rmaout_line.action_set_draft()

    @api.multi
    def button_cancel(self):
        for rma in self:
            for pick in rma.picking_ids:
                if pick.state == 'done':
                    raise UserError(_('Unable to cancel RMA %s as some receptions have already been done.') % (rma.name))
            for inv in rma.invoice_ids:
                if inv and inv.state not in ('cancel', 'draft'):
                    raise UserError(_("Unable to cancel this RMA. You must first cancel related invoice."))
            for pick in rma.picking_ids.filtered(lambda r: r.state != 'cancel'):
                pick.action_cancel()
            rma.rmaout_line.action_reject()

    @api.multi
    def button_confirm(self):
        self.create_picking_out()
        return {}

    @api.multi
    def create_picking_out(self):
        for rma in self:
            if rma.rmaout_line:
                rma._create_picking(self.warehouse_id.rma_out_type_id, rma.rmaout_line)

    @api.model
    def _prepare_picking(self, picking_type_id):
        if not self.group_id:
            self.group_id = self.group_id.create({
                'name': self.code,
                'partner_id': self.partner_id.id
            })
        if not self.partner_id.property_stock_supplier.id:
            raise UserError(_("You must set a Supplier Location for this partner %s") % self.partner_id.name)
        # Set corresponding location based on picking type
        if picking_type_id.code == 'incoming':
            loc_dest_id = picking_type_id.default_location_dest_id
            loc_src_id = self.partner_id.property_stock_supplier
        elif picking_type_id.code == 'internal':
            raise UserError(_("Picking type can not be internal"))
        else:
            loc_dest_id = self.partner_id.property_stock_supplier
            loc_src_id = picking_type_id.default_location_src_id
        return {
            'picking_type_id': picking_type_id.id,
            'partner_id': self.partner_id.id,
            'date': self.date,
            'origin': self.code,
            'rmaout_id': self.id,
            'location_dest_id': loc_dest_id.id,
            'location_id': loc_src_id.id,
            'company_id': self.company_id.id,
        }

    @api.multi
    def _create_picking(self, picking_type_id, rma_lines):
        StockPicking = self.env['stock.picking']
        for rma in self:
            if any([ptype in ['product', 'consu'] for ptype in rma.rmaout_line.mapped('product_id.type')]):
                res = rma._prepare_picking(picking_type_id)
                picking = StockPicking.create(res)
                rma_lines.action_confirm()
                moves = rma_lines._create_stock_moves(picking)
                moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm(merge=False)
                seq = 0
                for move in sorted(moves, key=lambda move: move.date_expected):
                    seq += 5
                    move.sequence = seq
                moves._action_assign()
                picking.message_post_with_view('mail.message_origin_link',
                    values={'self': picking, 'origin': rma},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return True

    @api.multi
    def action_view_picking(self):
        '''
        This function returns an action that display existing picking orders of given rma ids.
        When only one found, show the picking immediately.
        '''
        action = self.env.ref('stock.action_picking_tree')
        result = action.read()[0]

        #override the context to get rid of the default filtering on operation type
        result['context'] = {}
        pick_ids = self.mapped('picking_ids')
        #choose the view_mode accordingly
        if len(pick_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (pick_ids.ids)
        elif len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids.id
        return result

    @api.multi
    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_supplier_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action


class RmaLine(models.Model):
    _name = "rma.rmaout.line"
    _inherit = 'mail.thread'
    _description = "List of product to return"
    _rec_name = "display_name"
    _order = "date desc"
    
    @api.depends('sent_qty', 'refund_qty', 'received_qty')
    @api.one
    def _compute_process_status(self):
        ''' Process state of an rma line depends on the state of its handling process.
        Each rma line has different done requirements, depending on its action.
        Below is the requirement for each action
        '''
        qty_sent = self.sent_qty
        qty_refund = self.refund_qty
        qty_received = self.received_qty
        vals = {}
        if qty_sent == 0:
            vals['process_status'] = 'to_process'
        elif qty_sent == qty_received + qty_refund:
            vals['process_status'] = 'done'
        else:
            vals['process_status'] = 'processing'
        self.update(vals)

    @api.depends('state', 'move_ids.state', 'move_ids.product_uom_qty')
    def _compute_qty_sent_received(self):
        for line in self:
            if line.state != 'confirmed':
                line.sent_qty = 0.0
                line.received_qty = 0.0
                continue
            if line.product_id.type not in ['consu', 'product']:
                line.sent_qty = line.product_returned_qty
                line.received_qty = line.product_returned_qty
                continue
            total = 0.0
            for move in line.move_ids.filtered(lambda x: x.state != 'cancel' and x.location_dest_id.usage == "supplier"):
                if move.state == 'done':
                    total += move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom)
            line.sent_qty = total
            total_received = 0.0
            for move in line.move_ids.filtered(lambda x: x.state != 'cancel' and x.location_id.usage == "supplier"):
                if move.state == 'done':
                    total_received += move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom)
            line.received_qty = total_received

    @api.depends('refund_line_ids.invoice_id.state', 'refund_line_ids.quantity')
    def _compute_qty_refund(self):
        for line in self:
            qty = 0.0
            for inv_line in line.refund_line_ids.filtered(lambda x: x.invoice_id.type == 'in_refund'):
                if inv_line.invoice_id.state not in ['cancel']:
                    qty += inv_line.uom_id._compute_quantity(inv_line.quantity, line.product_uom)
            line.refund_qty = qty

    @api.depends('move_ids.state', 'move_ids.product_uom_qty')
    def _compute_qty_to_receive(self):
        for line in self:
            qty = 0.0
            for move in line.move_ids.filtered(lambda x: x.state not in ['cancel','done'] and x.location_id.usage == "supplier"):
                qty += move.product_qty
            line.qty_to_receive = qty

    rmaout_id = fields.Many2one('rma.rmaout', string='RMA-OUT Reference', required=True, ondelete='cascade',
                             index=True, copy=True)
    company_id = fields.Many2one(related='rmaout_id.company_id', string='Company', store=True, readonly=True)
    rma_partner_id = fields.Many2one(related='rmaout_id.partner_id', store=True, string='Customer')
    date = fields.Datetime('RMA-OUT Line Date', default=fields.Datetime.now)
    rmain_line_id = fields.Many2one('rma.rma.line', string='RMA-IN Line',
                                    index=True, copy=True)
    product_id = fields.Many2one('product.product', string='Product', required=True, help="Returned product")
    product_returned_qty = fields.Float('Quantity', required=True, digits=dp.get_precision('Product Unit of Measure'),
                                        help="Quantity of product returned")
    product_uom = fields.Many2one('product.uom', string='Unit of Measure', required=True)
    name = fields.Char('Description', required=True, help="More precise description of the problem")
    unit_purchase_price = fields.Float(digits=dp.get_precision('Product Price'), compute='_compute_purchase_price', store=True, help="Unit purchase price of the product")
    display_name = fields.Char('Name', compute='_get_display_name')
    state = fields.Selection([('draft', 'Draft'),
                              ('rejected', 'Rejected'),
                              ('confirmed', 'Confirmed')],
                              string='State', default='draft')
    process_status = fields.Selection([
                                ('to_process', 'To Process'),
                                ('processing', 'Processing'),
                                ('done', 'Processed')],
                                compute='_compute_process_status', store=True, string='Process Status', default='to_process')
    
    #Moves and invoice lines related to RMA handling process
    move_ids = fields.One2many('stock.move', 'rmaout_line_id', string='Reservation', readonly=True, ondelete='set null', copy=False)
    refund_line_ids = fields.One2many('account.invoice.line', 'rmaout_line_id', string='Refund Line', readonly=True, ondelete='set null', copy=False)
    sent_qty = fields.Float(compute='_compute_qty_sent_received', string="Sent Qty", digits=dp.get_precision('Product Unit of Measure'), store=True)
    refund_qty = fields.Float(compute='_compute_qty_refund', string="Refund Qty", digits=dp.get_precision('Product Unit of Measure'), store=True)
    received_qty = fields.Float(compute='_compute_qty_sent_received', string="Received Qty", digits=dp.get_precision('Product Unit of Measure'), store=True)
    qty_to_receive = fields.Integer(compute='_compute_qty_to_receive', string='Quantity to Receive', default=0, store=True)

    @api.onchange('rmain_line_id')
    def rmain_line_id_change(self):
        vals = {}
        domain_domain = {'domain': {'product_id':[]}}
        if not self.rmain_line_id:
            vals['product_id'] = False
            self.update(vals)
            return domain_domain
        if self.rmain_line_id.product_id:
            vals['product_id'] = self.rmain_line_id.product_id
        self.update(vals)
        return domain_domain

    @api.onchange('product_id')
    def product_id_change(self):
        vals = {}
        if not self.product_id:
            vals['product_uom'] = False
            vals['product_returned_qty'] = 0
            self.update(vals)
            return {'domain': {'product_uom':[]}}
        product_id = self.product_id
        domain = {'product_uom': [('category_id', '=', product_id.uom_id.category_id.id)]}
        if not self.product_uom or (product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = product_id.uom_id
            vals['product_returned_qty'] = 1.0
        result = {'domain': domain}
        self.update(vals)
        return result

    @api.depends('product_id')
    def _compute_purchase_price(self):
        for line in self:
            if not line.product_id:
                line.unit_purchase_price = 0
            else:
                # Get product purchase price from supplierinfo if exists, else use standard price
                product_supplierinfo = line.product_id.seller_ids.filtered(lambda x: x.name == line.rmaout_id.partner_id and\
                                               (not x.date_start or x.date_start < fields.Datetime.now()) and\
                                               (not x.date_end or x.date_end > fields.Datetime.now())\
                                               )
                purchase_price = product_supplierinfo[0].price if len(product_supplierinfo) > 0 else\
                                    line.product_id.standard_price
                line.unit_purchase_price = purchase_price

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = default or {}
        std_default = {
            'move_ids': False,
            'refund_line_ids': False,
        }
        std_default.update(default)
        return super(RmaLine, self).copy(default=std_default)

    @api.multi
    def _get_display_name(self):
        for line_id in self:
            line_id.display_name = "%s - %s" % (line_id.rmaout_id.code, line_id.product_id.name)

    @api.multi
    def action_confirm(self):
        for line in self:
            line.update({'state': 'confirmed'})
        return {}

    @api.multi
    def action_reject(self):
        for line in self:
            line.update({'state': 'rejected'})
        return {}

    @api.multi
    def action_set_draft(self):
        for line in self:
            line.update({'state': 'draft'})
        return {}

    @api.multi
    def _prepare_stock_moves(self, picking):
        """ Prepare the stock moves data for one rma line. This function returns a list of
        dictionary ready to be used in stock.move's create()
        """
        self.ensure_one()
        res = []
        if self.product_id.type not in ['product', 'consu']:
            return res
        template = {
            'name': self.display_name or '',
            'date': self.date,
            'date_expected': self.date,
            'rmaout_line_id': self.id,
            'location_id': picking.location_id.id,
            'location_dest_id': picking.location_dest_id.id,
            'picking_id': picking.id,
            'partner_id': picking.partner_id.id,
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id,
            'state': 'draft',
            'company_id': self.rmaout_id.company_id.id,
            'picking_type_id': picking.picking_type_id.id,
            'group_id': self.rmaout_id.group_id.id,
            'origin': self.rmaout_id.name,
            'route_ids': self.rmaout_id.warehouse_id and [(6, 0, [x.id for x in self.rmaout_id.warehouse_id.route_ids])] or [],
            'warehouse_id': self.rmaout_id.warehouse_id.id,
            'product_desc':self.name,
        }
        qty = 0.0
        if picking.picking_type_id.code == 'incoming':
            for move in self.move_ids.filtered(lambda x: x.state != 'cancel' and x.location_id.usage == "supplier"):
                qty += move.product_qty
            diff_quantity = self.sent_qty - self.refund_qty - qty
        else:
            for move in self.move_ids.filtered(lambda x: x.state != 'cancel' and x.location_dest_id.usage == "supplier"):
                qty += move.product_qty
            diff_quantity = self.product_returned_qty - qty
        if float_compare(diff_quantity, 0.0,  precision_rounding=self.product_uom.rounding) > 0:
            template['product_uom_qty'] = diff_quantity
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