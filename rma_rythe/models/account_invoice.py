# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models
from odoo.tools.float_utils import float_is_zero, float_compare


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    rmain_id = fields.Many2one('rma.rma', string='RMA-IN')
    rmain_count = fields.Integer(string='# of RMA-IN', compute='_compute_rmain', readonly=True)
    rmaout_id = fields.Many2one('rma.rmaout', string='RMA-OUT')
    rmaout_count = fields.Integer(string='# of RMA-OUT', compute='_compute_rmaout', readonly=True)

    @api.depends('rmain_id')
    @api.one
    def _compute_rmain(self):
        for invoice in self:
            rmain = invoice.rmain_id
            invoice.rmain_count = len(rmain)

    def _prepare_invoice_line_from_rma_line(self, line, is_refund=True):
        data = {
            'rmain_line_id': line.id,
            'origin': line.rma_id.code,
            'discount': 0.0,
        }
        qty = 0.0
        if is_refund:
            data['name'] = line.product_id.name
            data['uom_id'] = line.product_uom.id
            data['product_id'] = line.product_id.id
            data['price_unit'] = line.unit_sale_price
            data['account_id'] = self.env['account.invoice.line'].with_context({'journal_id': self.journal_id.id, 'type': 'out_refund'})._default_account()
            qty = line.received_qty - line.refund_qty
        else:
            data['name'] = line.replace_product_id.name
            data['uom_id'] = line.replace_product_uom.id
            data['product_id'] = line.replace_product_id.id
            data['price_unit'] = line.replace_unit_sale_price
            data['account_id'] = self.env['account.invoice.line'].with_context({'journal_id': self.journal_id.id, 'type': 'out_invoice'})._default_account()
            qty = line.replaced_qty - line.replace_invoiced_qty
        if float_compare(qty, 0.0,  precision_rounding=line.replace_product_uom.rounding) > 0:
            data['quantity'] = qty
        return data

    @api.onchange('rmain_id')
    def rmain_change(self, rma_line_to_do, is_refund=True):
        if not self.rmain_id:
            return {}
        if not self.partner_id:
            self.partner_id = self.rmain_id.partner_id.id

        new_lines = self.env['account.invoice.line']
        if is_refund:
            for line in rma_line_to_do - self.invoice_line_ids.mapped('rmain_line_id'):
                data = self._prepare_invoice_line_from_rma_line(line, is_refund=True)
                new_line = new_lines.new(data)
                new_line._set_additional_fields(self)
                new_lines += new_line
        else:
            for line in rma_line_to_do - self.invoice_line_ids.mapped('rmain_line_id'):
                data = self._prepare_invoice_line_from_rma_line(line, is_refund=False)
                new_line = new_lines.new(data)
                new_line._set_additional_fields(self)
                new_lines += new_line

        self.invoice_line_ids += new_lines
        return {}

    @api.multi
    def action_view_rmain(self):
        rmain = self.mapped('rmain_id')
        action = self.env.ref('rma_rythe.rma_rma_view_act').read()[0]
        if len(rmain) > 1:
            action['domain'] = [('id', 'in', rmain.ids)]
        elif len(rmain) == 1:
            action['views'] = [(self.env.ref('rma_rythe.rma_rma_form_view').id, 'form')]
            action['res_id'] = rmain.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.depends('rmaout_id')
    @api.one
    def _compute_rmaout(self):
        for invoice in self:
            rmaout = invoice.rmaout_id
            invoice.rmaout_count = len(rmaout)

    @api.multi
    def action_view_rmaout(self):
        rmaout = self.mapped('rmaout_id')
        action = self.env.ref('rma_rythe.rma_rmaout_view_act').read()[0]
        if len(rmaout) > 1:
            action['domain'] = [('id', 'in', rmaout.ids)]
        elif len(rmaout) == 1:
            action['views'] = [(self.env.ref('rma_rythe.rma_rmaout_form_view').id, 'form')]
            action['res_id'] = rmaout.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    rmain_line_id = fields.Many2one('rma.rma.line', string='RMA-IN Line')
    rmaout_line_id = fields.Many2one('rma.rmaout.line', string='RMA-OUT Line')
