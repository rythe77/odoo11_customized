# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
import pytz

from odoo.addons import decimal_precision as dp

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    
    #Create new fields
    x_vehicle_notes = fields.Char(
        'Vehicle Notes', index=False,
        states={'sale': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    x_notes = fields.Char(
        'Other Notes', index=False,
        states={'sale': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    
    def _prepare_invoice(self):
        vals = super(SaleOrderInherit, self)._prepare_invoice()
        # get current logged in user's timezone
        local = pytz.timezone(self.env['res.users'].browse(self._uid).tz) or pytz.utc
        vals.update({
            'date_invoice':pytz.utc.localize(datetime.datetime.now()).astimezone(local).strftime('%Y-%m-%d'),
        })
        return vals

    @api.multi
    def action_status(self):
        for item in self:
            item.invoice_status = 'invoiced'
            item.delivery_status = 'delivered'

    @api.multi
    def action_check_product_qty(self):
        rel_view_id = self.env.ref(
            'toserba23.sale_order_line_tree_view_custom')
        if self.partner_id.id:
            sale_lines = self.env['sale.order.line'].search([('order_id', '=', self.id)]).mapped('id')
        else:
            sale_lines = []
        if not sale_lines:
            raise Warning("Tidak ada baris order penjualan.!")
        else:
            return {
                'domain': [('id', 'in', sale_lines)],
                'views': [(rel_view_id.id, 'tree')],
                'name': 'Cek Qty Produk',
                'res_model': 'sale.order.line',
                'view_id': False,
                'type': 'ir.actions.act_window',
            }

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    #Computed fields for checking order qty availability
    x_qty_on_draft = fields.Float(
        compute='_get_draft_qty', string='Qty Total Penawaran', store=False, readonly=True,
        digits=dp.get_precision('Product Unit of Measure'))
    x_qty_ckl = fields.Float(
        compute='_get_inventory', string='Qty CKL', store=False, readonly=True,
        digits=dp.get_precision('Product Unit of Measure'))
    x_qty2_ckl = fields.Float(
        compute='_get_inventory', string='Qty* CKL', store=False, readonly=True,
        digits=dp.get_precision('Product Unit of Measure'))
    x_qty_prl = fields.Float(
        compute='_get_inventory', string='Qty PRL', store=False, readonly=True,
        digits=dp.get_precision('Product Unit of Measure'))
    x_qty2_prl = fields.Float(
        compute='_get_inventory', string='Qty* PRL', store=False, readonly=True,
        digits=dp.get_precision('Product Unit of Measure'))

    def _get_draft_qty(self):
        for line in self:
            draft_qty = 0;
            if line.order_partner_id.id:
                sale_lines = self.env['sale.order.line'].search([('product_id', '=', line.product_id.id),('state', 'in', ['draft','sent'])])
            else:
                sale_lines = []
            for sale_line in sale_lines:
                draft_qty += sale_line.product_uom_qty
            line.x_qty_on_draft = draft_qty

    def _get_inventory(self):
        for line in self:
            if line.product_id.id:
                line.x_qty_ckl = line.product_id.x_qty_available_0
                line.x_qty2_ckl = line.product_id.x_virtual_available_0
                line.x_qty_prl = line.product_id.x_qty_available_1
                line.x_qty2_prl = line.product_id.x_virtual_available_1