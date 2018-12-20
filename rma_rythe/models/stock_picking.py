# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    rmain_id = fields.Many2one('rma.rma', 'RMA-IN')
    rmain_count = fields.Integer(string='# of RMA-IN', compute='_compute_rmain', readonly=True)
    rmaout_id = fields.Many2one('rma.rmaout', 'RMA-OUT')
    rmaout_count = fields.Integer(string='# of RMA-OUT', compute='_compute_rmaout', readonly=True)

    @api.depends('rmain_id')
    @api.one
    def _compute_rmain(self):
        for picking in self:
            rmain = picking.rmain_id
            picking.rmain_count = len(rmain)

    @api.multi
    def action_done(self):
        """
            On transfer validation, auto create invoice
        """
        return_val = super(StockPicking, self).action_done()
        for rec in self:
            rmain_ids = []
            invoice_ids = []
            if rec.rmain_id and rec.rmain_id.show_button_create_invoice:
                rmain_ids.append(rec.rmain_id.id)
            if rmain_ids and not self.picking_type_id.code == 'internal':
                rmain = self.env['rma.rma'].browse(rmain_ids)
                invoice_ids = rmain.sudo().action_invoice_create()
            if len(invoice_ids) == 1:
                rec.invoice_id = invoice_ids[0]
        return return_val

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
        for picking in self:
            rmaout = picking.rmaout_id
            picking.rmaout_count = len(rmaout)

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


class StockMove(models.Model):
    _inherit = "stock.move"

    rmain_line_id = fields.Many2one('rma.rma.line', 'RMA-IN Line')
    rmaout_line_id = fields.Many2one('rma.rmaout.line', 'RMA-OUT Line')
