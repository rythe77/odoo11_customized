# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError

class RmaOutCreateWizardLine(models.TransientModel):
    _name = "rmaout.create.wizard.line"
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product', string="Product", domain="[('id', '=', product_id)]")
    name = fields.Char('Description', help="More precise description of the problem")
    quantity = fields.Float("Quantity", digits=dp.get_precision('Product Unit of Measure'))
    uom_id = fields.Many2one('product.uom', string='Unit of Measure', related='rmain_line_id.product_uom')
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True)
    wizard_id = fields.Many2one('rmaout.create.wizard', string="Wizard")
    rmain_line_id = fields.Many2one('rma.rma.line', "RMA-IN Line")


class RmaOutCreateWizard(models.TransientModel):
    _name = "rmaout.create.wizard"
    _description = "RMA-OUT Create Wizard"

    rmain_id = fields.Many2one('rma.rma')
    rmaout_create_line = fields.One2many('rmaout.create.wizard.line', 'wizard_id', 'Lines')

    @api.model
    def default_get(self, fields):
        if len(self.env.context.get('active_ids', list())) > 1:
            raise UserError(_("You may only create RMA-OUT for one RMA-IN at a time!"))
        res = super(RmaOutCreateWizard, self).default_get(fields)

        rmaout_create_line = []
        rmain = self.env['rma.rma'].browse(self.env.context.get('active_id'))
        if rmain:
            res.update({'rmain_id': rmain.id})
            if rmain.state not in ['processing', 'closed']:
                raise UserError(_("You may only create RMA-OUT for already received goods"))
            for rma_line in rmain.rma_line:
                if len(rma_line.rmaout_line_ids) == 0:
                    line_vals = {
                        'name': rma_line.name,
                        'product_id': rma_line.product_id.id,
                        'quantity': rma_line.received_qty,
                        'uom_id': rma_line.product_id.uom_id.id,
                        'rmain_line_id': rma_line.id}
                    partners = rma_line.product_id.seller_ids.mapped('name')
                    if len(partners) > 0:
                        line_vals['partner_id'] = partners[0].id
                    rmaout_create_line.append((0, 0, line_vals))
            res.update({'rmaout_create_line': rmaout_create_line})
        return res

    @api.model
    def _prepare_rmaout(self, rmaout_line):
        return {
            'partner_id': rmaout_line.partner_id.id,
            'name': rmaout_line.partner_id.name,
            'warehouse_id': self.rmain_id.warehouse_id.id,
            'responsible': self._context.get('uid'),
        }

    def _prepare_rmaout_line_default_values(self, rmaout_create_line, rmaout):
        vals = {
            'rmaout_id': rmaout.id,
            'rmain_line_id': rmaout_create_line.rmain_line_id.id,
            'product_id': rmaout_create_line.product_id.id,
            'name': rmaout_create_line.name,
            'product_returned_qty': rmaout_create_line.quantity,
            'product_uom': rmaout_create_line.uom_id.id,
        }
        return vals

    def create_rmaout(self):
        self.ensure_one()
        draft_rmaout = self.env['rma.rmaout'].search([('state', '=', 'draft'), ('warehouse_id', '=', self.rmain_id.warehouse_id.id)])
        exist_partner = draft_rmaout.mapped('partner_id')
        for line in self.rmaout_create_line:
            if len(line.rmain_line_id.rmaout_line_ids) == 0:
                if line.partner_id not in exist_partner:
                    # create new rma-out if no existing rma-out in draft state with matching partner_id
                    res = self._prepare_rmaout(line)
                    new_rmaout = self.env['rma.rmaout'].create(res)
                    new_rmaout.message_post_with_view('mail.message_origin_link',
                        values={'self': new_rmaout, 'origin': self.rmain_id},
                        subtype_id=self.env.ref('mail.mt_note').id)
                    draft_rmaout = self.env['rma.rmaout'].search([('state', '=', 'draft'), ('warehouse_id', '=', self.rmain_id.warehouse_id.id)])
                    exist_partner = draft_rmaout.mapped('partner_id')
                    vals = self._prepare_rmaout_line_default_values(line, new_rmaout)
                    created_lines = self.env['rma.rmaout.line'].create(vals)
                    created_lines.product_id_change()
                else:
                    # Just add new lines to existing rmaout in draft
                    vals = self._prepare_rmaout_line_default_values(line, draft_rmaout.filtered(lambda x: x.partner_id == line.partner_id)[0])
                    created_lines = self.env['rma.rmaout.line'].create(vals)
                    created_lines.product_id_change()
            else:
                raise UserError(_("The line (%s) already has associated rma-out line") % line.rmain_line_id.display_name)
        return {}