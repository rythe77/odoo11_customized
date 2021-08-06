# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime

from odoo import _, api, exceptions, fields, models
from odoo.tools import (DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT)
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero, float_compare
import pytz


class RmaReason(models.Model):
    _name = "rma.reason"
    _description = "RMA Reasons"
    _order = "action"

    name = fields.Char('Reasons Name', required=True, translate=True)
    description = fields.Text('Reasons Description', translate=True)
    action = fields.Selection([
        ('replace','Replace'),
        ('replace_part','Replace Part'),
        ('refund','Refund'),
        ('repair','Repair')],
        'Action',default='replace')

class RmaRma(models.Model):
    _name = "rma.rma"
    _description = "RMA"
    _order = "priority,date desc"
    _inherit = ['mail.thread']

    @api.model
    def _get_default_team(self):
        return self.env['crm.team']._get_default_team_id()
    
    @api.depends('rma_line.state', 'rma_line.process_status')
    @api.one
    def _compute_state(self):
        ''' State of a rma depends on the state of its related rma.line
        - Draft: only used for "planned rma"
        - Approved: if the rma is approved and product is ready to be received
        - Processing: if the product is received and ready to be processed
        - Closed: if the rma is done.
        - Rejected: if the rma is rejected
        '''
        if not self.rma_line:
            self.state = 'draft'
        elif all(rma_line.state == 'draft' for rma_line in self.rma_line):
            self.state = 'draft'
        elif all(rma_line.state == 'rejected' for rma_line in self.rma_line):
            self.state = 'rejected'
        elif all(rma_line.state == 'approved' and rma_line.process_status == 'to_process' for rma_line in self.rma_line):
            self.state = 'approved'
        elif all(rma_line.state == 'approved' and rma_line.process_status == 'done' for rma_line in self.rma_line):
            self.state = 'closed'
        else:
            self.state = 'processing'
    
    code = fields.Char(string='RMA Number', required=True, default="/", readonly=True, copy=False)
    _sql_constraints = [
        ('rma_unique_code', 'UNIQUE (code)',
         'The code must be unique!'),
    ]

    @api.depends('rmaout_ids')
    @api.one
    def _compute_rmaout(self):
        for rma in self:
            rma.rmaout_count = len(rma.rmaout_ids)

    @api.depends('rma_line.rmaout_line_ids')
    @api.one
    def _compute_rmaout_ids(self):
        for rma in self:
            rmaout_id_to_append = []
            for rma_line in rma.rma_line:
                for rmaout_line in rma_line.rmaout_line_ids:
                    if rmaout_line.rmaout_id.mapped('id')[0] not in rmaout_id_to_append:
                        rmaout_id_to_append.append(rmaout_line.rmaout_id.mapped('id')[0])
            self.update({
                'rmaout_ids': [(6,0,rmaout_id_to_append)]
                })

    @api.multi
    def action_view_rmaout(self):
        rmaouts = self.mapped('rmaout_ids')
        action = self.env.ref('rma_rythe.rma_rmaout_view_act').read()[0]
        if len(rmaouts) > 1:
            action['domain'] = [('id', 'in', rmaouts.ids)]
        elif len(rmaouts) == 1:
            action['views'] = [(self.env.ref('rma_rythe.rma_rmaout_form_view').id, 'form')]
            action['res_id'] = rmaouts.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    rmaout_count = fields.Integer(string='RMA-OUT', compute='_compute_rmaout', readonly=True, copy=False)
    rmaout_ids = fields.Many2many('rma.rmaout', compute='_compute_rmaout_ids', store=True, string='Related RMA-OUT')
    name = fields.Char('Subject', required=True, readonly=True, states={'draft': [('readonly', False)]})
    user_id = fields.Many2one('res.users', 'Responsible', required=True, track_visibility='always',default=lambda self: self.env.user)
    team_id = fields.Many2one('crm.team', 'Sales Channel', change_default=True, default=_get_default_team, oldname='section_id', states={'rejected': [('readonly', True)], 'closed': [('readonly', True)]})
    date = fields.Datetime('RMA Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)]}, copy=False, default=fields.Datetime.now)
    priority = fields.Selection([('0','Low'), ('1','Normal'), ('2','High')], 'Priority',default='1', states={'rejected': [('readonly', True)], 'closed': [('readonly', True)]})
    date_deadline = fields.Date('Deadline', states={'rejected': [('readonly', True)], 'closed': [('readonly', True)]})
    date_closed = fields.Datetime('Closed', compute='_compute_date_closed', store=True, readonly=True)
    partner_id = fields.Many2one('res.partner', 'Partner', required=True, readonly=True, states={'draft': [('readonly', False)]})
    partner_email = fields.Char('Email', size=128, help="Partner email", states={'rejected': [('readonly', True)], 'closed': [('readonly', True)]})
    partner_phone = fields.Char('Phone', states={'rejected': [('readonly', True)], 'closed': [('readonly', True)]})
    state = fields.Selection([
        ('rejected', 'Rejected'),
        ('draft', 'Draft'),
        ('approved', 'Approved'),
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
            vals['code'] = self.env['ir.sequence'].next_by_code('rma.rma.customer')
        context = dict(self._context or {})
        if vals.get('team_id') and not self._context.get('default_team_id'):
            context['default_team_id'] = vals.get('team_id')
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
            default['code'] = self.env['ir.sequence'].next_by_code('rma.rma.customer')
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

    @api.depends('rma_line.received_qty', 'rma_line.replaced_qty')
    def _compute_show_button_replace(self):
        for rma in self:
            if rma.state == 'processing':
                if any([line.action in ['replace', 'replace_part']\
                        and line.product_id == line.replace_product_id\
                        and line.received_qty > line.replaced_qty + line.qty_to_send\
                        for line in rma.rma_line]):
                    self.show_button_replace = True
                elif any([line.action in ['replace', 'replace_part']\
                        and not line.product_id == line.replace_product_id\
                        and line.replace_product_qty > line.replaced_qty + line.qty_to_send\
                        for line in rma.rma_line]):
                    self.show_button_replace = True
                elif any([line.action in ['repair']\
                        and line.received_qty > line.replaced_qty + line.qty_to_send\
                        for line in rma.rma_line]):
                    self.show_button_replace = True
                else:
                    self.show_button_replace = False
            else:
                self.show_button_replace = False

    @api.depends('rma_line.received_qty', 'rma_line.refund_qty', 'rma_line.replaced_qty', 'rma_line.replace_invoiced_qty')
    def _compute_show_button_create_invoice(self):
        for rma in self:
            if rma.state == 'processing':
                if any([line.action in ['replace']\
                        and not line.product_id == line.replace_product_id\
                        and (line.received_qty > line.refund_qty\
                        or line.replaced_qty > line.replace_invoiced_qty)\
                        for line in rma.rma_line]):
                    self.show_button_create_invoice = True
                elif any([line.action in ['refund']\
                        and line.received_qty > line.refund_qty\
                        for line in rma.rma_line]):
                    self.show_button_create_invoice = True
                else:
                    self.show_button_create_invoice = False
            else:
                self.show_button_replace = False

    company_id = fields.Many2one('res.company', change_default=True, default=lambda self: self.env['res.company']._company_default_get('rma_rythe'))
    rma_line = fields.One2many('rma.rma.line', 'rma_id', string='RMA Lines', readonly=True, states={'draft': [('readonly', False)]}, copy=True, auto_join=True)
    rma_line_follow = fields.One2many(related='rma_line', string='RMA Lines Follow Up', readonly=True, copy=True, auto_join=True)
    invoice_count = fields.Integer(string='# of Invoices', compute='_compute_invoice', readonly=True, copy=False)
    invoice_ids = fields.One2many('account.invoice', 'rmain_id', 'Refunds', copy=False)
    picking_count = fields.Integer(compute='_compute_picking', string='Receptions', default=0, store=True, copy=False)
    picking_ids = fields.One2many('stock.picking', 'rmain_id', string='Related Stock Picking', copy=False)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', required=True, default=_get_default_warehouse)
    group_id = fields.Many2one('procurement.group', string="Procurement Group", copy=False)
    show_button_replace = fields.Boolean(compute="_compute_show_button_replace", default=False)
    show_button_create_invoice = fields.Boolean(compute="_compute_show_button_create_invoice", default=False)

    @api.multi
    def action_status(self):
        for item in self:
            item.state = 'closed'

    @api.multi
    def button_create_invoice(self):
        self.action_invoice_create()
        return {}

    @api.multi
    def button_approve(self):
        self.create_picking_in()
        return {}

    @api.multi
    def button_draft(self):
        for rma in self:
            rma.rma_line.action_set_draft()

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
            rma.rma_line.action_reject()

    @api.multi
    def create_picking_in(self):
        for rma in self:
            if rma.rma_line:
                rma._create_picking(self.warehouse_id.rma_in_type_id, rma.rma_line)

    @api.model
    def _prepare_picking(self, picking_type_id):
        if not self.group_id:
            self.group_id = self.group_id.create({
                'name': self.code,
                'partner_id': self.partner_id.id
            })
        if not self.partner_id.property_stock_customer.id:
            raise UserError(_("You must set a Customer Location for this partner %s") % self.partner_id.name)
        # Set corresponding location based on picking type
        if picking_type_id.code == 'incoming':
            loc_dest_id = picking_type_id.default_location_dest_id
            loc_src_id = self.partner_id.property_stock_customer
        elif picking_type_id.code == 'internal':
            raise UserError(_("Picking type can not be internal"))
        else:
            loc_dest_id = self.partner_id.property_stock_customer
            loc_src_id = picking_type_id.default_location_src_id
        return {
            'picking_type_id': picking_type_id.id,
            'partner_id': self.partner_id.id,
            'date': self.date,
            'origin': self.code,
            'rmain_id': self.id,
            'location_dest_id': loc_dest_id.id,
            'location_id': loc_src_id.id,
            'company_id': self.company_id.id,
        }

    @api.multi
    def _create_picking(self, picking_type_id, rma_lines):
        StockPicking = self.env['stock.picking']
        for rma in self:
            if any([ptype in ['product', 'consu'] for ptype in rma.rma_line.mapped('product_id.type')]):
                res = rma._prepare_picking(picking_type_id)
                picking = StockPicking.create(res)
                rma_lines.action_approve()
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
    def _prepare_invoice(self, is_refund=True):
        """
        Prepare the dict of values to create the new invoice for a rma.
        """
        # get current logged in user's timezone
        local = pytz.timezone(self.env['res.users'].browse(self._uid).tz) or pytz.utc

        self.ensure_one()
        journal_id = self.env['account.journal'].search([('type', '=', 'sale')], limit=1).id
        if not journal_id:
            raise UserError(_('Please define an accounting purchase journal for this company.'))
        inv_type = 'out_refund' if is_refund else 'out_invoice'
        invoice_vals = {
            'name': self.name or '',
            'origin': self.code,
            'type': inv_type,
            'account_id': self.partner_id.property_account_receivable_id.id,
            'partner_id': self.partner_id.id,
            'journal_id': journal_id,
            'currency_id': self.company_id.currency_id.id,
            'company_id': self.company_id.id,
            'rmain_id': self.id,
            'date_invoice':pytz.utc.localize(datetime.datetime.now()).astimezone(local).strftime('%Y-%m-%d'),
        }
        return invoice_vals

    @api.multi
    def action_invoice_create(self, grouped=False):
        """
        Create the invoice associated to the RMA.
        :param grouped: if True, invoices are grouped by RMA id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        inv_obj = self.env['account.invoice']
        invoices = {}
        references = {}
        for rma in self:
            group_key = rma.id if grouped else (rma.partner_id.id, rma.company_id.currency_id.id)
            rma_line_to_refund = rma.rma_line.filtered(lambda x:\
                        x.action in ['refund'] or (x.action in ['replace']\
                        and not x.product_id == x.replace_product_id)
                        and x.received_qty - x.refund_qty > 0)
            if len(rma_line_to_refund) > 0:
                inv_data = rma._prepare_invoice(is_refund=True)
                invoice = inv_obj.create(inv_data)
                #create invoice line using account.invoice method
                invoice.rmain_change(rma_line_to_refund, is_refund=True)
                references[invoice] = rma
                invoices[group_key] = invoice

            rma_line_to_invoice = rma.rma_line.filtered(lambda x:\
                        x.action in ['replace'] and not x.product_id == x.replace_product_id\
                        and x.replaced_qty - x.replace_invoiced_qty > 0)
            if len(rma_line_to_invoice) > 0:
                inv_data = rma._prepare_invoice(is_refund=False)
                invoice = inv_obj.create(inv_data)
                #create invoice line using account.invoice method
                invoice.rmain_change(rma_line_to_invoice, is_refund=False)
                references[invoice] = rma
                invoices[group_key] = invoice

            if references.get(invoices.get(group_key)):
                if rma not in references[invoices[group_key]]:
                    references[invoice] = references[invoice] | rma

        if not invoices:
            raise UserError(_('There is no invoicable line.'))

        for invoice in invoices.values():
            if not invoice.invoice_line_ids:
                raise UserError(_('There is no invoicable line.'))
            # Necessary to force computation of taxes. In account_invoice, they are triggered
            # by onchanges, which are not triggered when doing a create.
            invoice.compute_taxes()
            invoice.message_post_with_view('mail.message_origin_link',
                values={'self': invoice, 'origin': references[invoice]},
                subtype_id=self.env.ref('mail.mt_note').id)
        return [inv.id for inv in invoices.values()]

    @api.multi
    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.invoice_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action


class RmaLine(models.Model):
    _name = "rma.rma.line"
    _inherit = 'mail.thread'
    _description = "List of product to return"
    _rec_name = "display_name"
    _order = "date desc"
    
    @api.depends('received_qty', 'refund_qty', 'serviced_qty', 'replaced_qty', 'replace_invoiced_qty')
    @api.one
    def _compute_process_status(self):
        ''' Process state of an rma line depends on the state of its handling process.
        Each rma line has different done requirements, depending on its action.
        Below is the requirement for each action
        - Replace and replace part, same product or repair: same return, receive and replace qty
        - Replace and replace part, different product: same return, receive, and replace invoice qty
        - Refund: same return, receive and refund qty
        '''
        action = self.action
        qty_received = self.received_qty
        qty_refund = self.refund_qty
        qty_serviced = self.serviced_qty
        qty_replaced = self.replaced_qty
        qty_invoiced = self.replace_invoiced_qty
        vals = {}
        if qty_received == 0:
            vals['process_status'] = 'to_process'
        elif action in ['replace', 'replace_part'] and self.product_id == self.replace_product_id:
            if qty_received == qty_replaced + qty_refund:
                vals['process_status'] = 'done'
            else:
                vals['process_status'] = 'processing'
        elif action in ['replace'] and self.product_id != self.replace_product_id:
            if qty_received == qty_refund and not qty_replaced == 0 and qty_replaced == qty_invoiced:
                vals['process_status'] = 'done'
            else:
                vals['process_status'] = 'processing'
        elif action == 'repair':
            if qty_received == qty_serviced and qty_replaced == qty_serviced:
                vals['process_status'] = 'done'
            else:
                vals['process_status'] = 'processing'
        elif action == 'refund':
            if qty_received == qty_replaced + qty_refund:
                vals['process_status'] = 'done'
            else:
                vals['process_status'] = 'processing'
        self.update(vals)
    
    @api.depends('state', 'move_ids.state', 'move_ids.product_uom_qty')
    def _compute_qty_received_replaced(self):
        for line in self:
            if line.state != 'approved':
                line.received_qty = 0.0
                line.replaced_qty = 0.0
                continue
            if line.product_id.type not in ['consu', 'product']:
                line.received_qty = line.product_returned_qty
                line.replaced_qty = 0.0
                continue
            total = 0.0
            for move in line.move_ids.filtered(lambda x: x.state != 'cancel' and x.location_id.usage == "customer"):
                if move.state == 'done':
                    total += move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom)
            line.received_qty = total
            total_replaced = 0.0
            for move in line.move_ids.filtered(lambda x: x.state != 'cancel' and x.location_dest_id.usage == "customer"):
                if move.state == 'done':
                    total_replaced += move.product_uom._compute_quantity(move.product_uom_qty, line.replace_product_uom)
            line.replaced_qty = total_replaced

    @api.depends('refund_line_ids.invoice_id.state', 'refund_line_ids.quantity')
    def _compute_qty_refund_invoiced(self):
        for line in self:
            qty = 0.0
            for inv_line in line.refund_line_ids.filtered(lambda x: x.invoice_id.type == 'out_refund'):
                if inv_line.invoice_id.state not in ['cancel']:
                    qty += inv_line.uom_id._compute_quantity(inv_line.quantity, line.product_uom)
            line.refund_qty = qty
            qty_inv = 0.0
            for inv_line in line.refund_line_ids.filtered(lambda x: x.invoice_id.type == 'out_invoice'):
                if inv_line.invoice_id.state not in ['cancel']:
                    qty_inv += inv_line.uom_id._compute_quantity(inv_line.quantity, line.replace_product_uom)
            line.replace_invoiced_qty = qty_inv

    @api.depends('move_ids.state', 'move_ids.product_uom_qty')
    def _compute_qty_to_send(self):
        for line in self:
            qty = 0.0
            for move in line.move_ids.filtered(lambda x: x.state not in ['cancel','done'] and x.location_dest_id.usage == "customer"):
                qty += move.product_qty
            line.qty_to_send = qty

    rma_id = fields.Many2one('rma.rma', string='RMA Reference', required=True, ondelete='cascade',
                             index=True, copy=True)
    company_id = fields.Many2one(related='rma_id.company_id', string='Company', store=True, readonly=True)
    rma_partner_id = fields.Many2one(related='rma_id.partner_id', store=True, string='Customer')
    date = fields.Datetime('RMA Line Date', default=fields.Datetime.now)
    product_id = fields.Many2one('product.product', string='Product', required=True, help="Returned product")
    replace_product_id = fields.Many2one('product.product', string='Replacement Product', compute='_compute_replacement_product',
                                         store=True, help="Replacement product")
    product_invoiced_qty = fields.Float('Invoiced Quantity', compute='_compute_invoice_data',
                                        store=True, digits=dp.get_precision('Product Unit of Measure'),
                                        help="Quantity of product invoiced")
    product_returned_qty = fields.Float('Quantity', required=True, digits=dp.get_precision('Product Unit of Measure'),
                                        help="Quantity of product returned")
    replace_product_qty = fields.Float('Replace Quantity', default=0.0, digits=dp.get_precision('Product Unit of Measure'),
                                        help="Quantity of product replaced")
    product_uom = fields.Many2one('product.uom', string='Unit of Measure', required=True)
    replace_product_uom = fields.Many2one('product.uom', string='Unit of Measure', compute='_compute_replacement_product_uom',
                                         store=True)
    name = fields.Char('Description', required=True, help="More precise description of the problem")
    rma_reason_id = fields.Many2one('rma.reason', string='RMA Reason', index=True)
    action = fields.Selection(related='rma_reason_id.action', string='Action', readonly=True)
    unit_sale_price = fields.Float(digits=dp.get_precision('Product Price'), compute='_compute_invoice_data',
                                   store=True, help="Unit sale price of the product")
    replace_unit_sale_price = fields.Float(digits=dp.get_precision('Product Price'), compute='_compute_replacement_product_uom',
                                   store=True, help="Unit sale price of the product")
    prodlot_id = fields.Many2one('stock.production.lot', string='Serial/Lot number',
                                 help="The serial/lot of the returned product")
    display_name = fields.Char('Name', compute='_get_display_name')
    state = fields.Selection([('draft', 'Draft'),
                              ('rejected', 'Rejected'),
                              ('approved', 'Approved')],
                              string='State', default='draft')
    process_status = fields.Selection([
                                ('to_process', 'To Process'),
                                ('processing', 'Processing'),
                                ('done', 'Processed')],
                                compute='_compute_process_status', store=True, string='Process Status', default='to_process')
    invoice_line_id = fields.Many2one('account.invoice.line', string='Invoice Line', help='The origin invoice line related to the returned product')
    rmaout_line_ids = fields.One2many('rma.rmaout.line', 'rmain_line_id', string='Linked RMA-OUT Line', copy=False)
    
    #Moves and invoice lines related to RMA handling process
    move_ids = fields.One2many('stock.move', 'rmain_line_id', string='Reservation', readonly=True, ondelete='set null', copy=False)
    refund_line_ids = fields.One2many('account.invoice.line', 'rmain_line_id', string='Refund Line', readonly=True, ondelete='set null', copy=False)
    received_qty = fields.Float(compute='_compute_qty_received_replaced', string="Received Qty", digits=dp.get_precision('Product Unit of Measure'), store=True)
    refund_qty = fields.Float(compute='_compute_qty_refund_invoiced', string="Refund Qty", digits=dp.get_precision('Product Unit of Measure'), store=True)
    serviced_qty = fields.Float(string="Serviced Qty", digits=dp.get_precision('Product Unit of Measure'))
    replaced_qty = fields.Float(compute='_compute_qty_received_replaced', string="Replaced Qty", digits=dp.get_precision('Product Unit of Measure'), store=True)
    replace_invoiced_qty = fields.Float(compute='_compute_qty_refund_invoiced', string="Billed Qty", digits=dp.get_precision('Product Unit of Measure'), store=True)
    qty_to_send = fields.Integer(compute='_compute_qty_to_send', string='Quantity to Send', default=0, store=True)

    @api.onchange('invoice_line_id')
    def invoice_line_id_change(self):
        vals = {}
        domain_domain = {'domain': {'product_id':[]}}
        if not self.invoice_line_id:
            vals['product_id'] = False
            self.update(vals)
            return domain_domain
        if self.invoice_line_id.product_id:
            vals['product_id'] = self.invoice_line_id.product_id
        self.update(vals)
        return domain_domain

    @api.onchange('product_id')
    def product_id_change(self):
        vals = {}
        if not self.product_id:
            vals['product_uom'] = False
            vals['product_returned_qty'] = 0
            vals['replace_product_qty'] = 0
            self.update(vals)
            return {'domain': {'product_id':[], 'product_uom':[]}}
        product_id = self.product_id
        domain = {'product_uom': [('category_id', '=', product_id.uom_id.category_id.id)]}
        if not self.product_uom or (product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = product_id.uom_id
            vals['product_returned_qty'] = 1.0
            vals['replace_product_qty'] = 1.0
        result = {'domain': domain}
        self.update(vals)
        return result

    @api.one
    @api.depends('invoice_line_id', 'product_id')
    def _compute_invoice_data(self):
        if self.invoice_line_id:
            self.product_invoiced_qty = self.invoice_line_id.quantity
            self.unit_sale_price = self.invoice_line_id.price_unit
        elif self.product_id:
            self.product_invoiced_qty = 0.0
            if self.rma_partner_id.property_product_pricelist:
                self.unit_sale_price = self.rma_partner_id.property_product_pricelist.\
                                get_product_price(self.product_id, self.product_returned_qty, self.rma_partner_id)
            else:
                self.unit_sale_price = self.product_id.list_price
        else:
            self.product_invoiced_qty = 0.0
            self.unit_sale_price = 0.0

    @api.one
    @api.depends('product_id')
    def _compute_replacement_product(self):
        if self.product_id:
            self.replace_product_id = self.product_id

    @api.one
    @api.depends('replace_product_id')
    def _compute_replacement_product_uom(self):
        if self.replace_product_id:
            self.replace_product_uom = self.replace_product_id.uom_id
            if self.rma_partner_id.property_product_pricelist:
                self.replace_unit_sale_price = self.rma_partner_id.property_product_pricelist.\
                            get_product_price(self.replace_product_id, self.replace_product_qty, self.rma_partner_id)
            else:
                self.replace_unit_sale_price = self.replace_product_id.list_price

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
            line_id.display_name = "%s - %s" % (line_id.rma_id.code, line_id.product_id.name)

    @api.multi
    def get_product_replacement_wizard(self):
        self.ensure_one()
        if self.action != 'replace' and self.action != 'replace_part':
            raise UserError(_("Only a rma line with replace action can have product replacement"))
        return {
            'name': 'Product Replacements',
            'res_model': 'rma.product.replacement.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {'default_rma_line_id':self.id,
                        'default_product_id':self.replace_product_id.id,
                        'default_replace_product_qty':self.product_returned_qty},
        }

    @api.multi
    def get_product_service_wizard(self):
        self.ensure_one()
        if self.action != 'repair':
            raise UserError(_("Only a rma line with repair action can have product service"))
        return {
            'name': 'Product Service',
            'res_model': 'rma.service.product.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {'default_rma_line_id':self.id,
                        'default_product_id':self.replace_product_id.id,
                        'default_service_qty':self.received_qty - self.serviced_qty},
        }

    @api.multi
    def action_approve(self):
        for line in self:
            line.update({'state': 'approved'})
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
    def change_action_to_replace(self):
        for line in self:
            if line.action =='repair':
                replace_reason = self.env['ir.model.data'].get_object_reference('rma_rythe','rma_reason1')
                line.update({'rma_reason_id': replace_reason[1]})
            else:
                raise UserError(_('You can only change repair action to replace action when the service is not done yet!'))
        return {}

    @api.multi
    def change_action_to_refund(self):
        for line in self:
            if (line.action =='replace' or line.action =='replace_part') and line.replaced_qty == 0 and line.qty_to_send == 0:
                refund_reason = self.env['ir.model.data'].get_object_reference('rma_rythe','rma_reason4')
                line.update({'rma_reason_id': refund_reason[1]})
            else:
                raise UserError(_('You can only change replace action to refund action\
                if all related replacement transfer is not yet created or already cancelled'))
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
            #'product_id': self.product_id.id,
            #'product_uom': self.product_uom.id,
            'date': self.date,
            'date_expected': self.date,
            'rmain_line_id': self.id,
            'location_id': picking.location_id.id,
            'location_dest_id': picking.location_dest_id.id,
            'picking_id': picking.id,
            'partner_id': picking.partner_id.id,
            'state': 'draft',
            'company_id': self.rma_id.company_id.id,
            'picking_type_id': picking.picking_type_id.id,
            'group_id': self.rma_id.group_id.id,
            'origin': self.rma_id.name,
            'route_ids': self.rma_id.warehouse_id and [(6, 0, [x.id for x in self.rma_id.warehouse_id.route_ids])] or [],
            'warehouse_id': self.rma_id.warehouse_id.id,
            'product_desc':self.name,
        }
        qty = 0.0
        if picking.picking_type_id.code == 'incoming':
            for move in self.move_ids.filtered(lambda x: x.state != 'cancel' and x.location_id.usage == "customer"):
                qty += move.product_qty
            diff_quantity = self.product_returned_qty - qty
            product_id = self.product_id
            product_uom = self.product_uom
        if float_compare(diff_quantity, 0.0,  precision_rounding=self.product_uom.rounding) > 0:
            template['product_id'] = product_id.id
            template['product_uom'] = product_uom.id
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