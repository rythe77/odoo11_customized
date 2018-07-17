# -*- encoding: utf-8 -*-

from odoo import models, api, fields, _
from odoo.exceptions import Warning


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def action_view_past_price(self):
        rel_view_id = self.env.ref(
            'sale_purchase_previous_price.last_sale_product_prices_view')
        if self.partner_id.id:
            sale_lines = self.env['sale.order.line'].search([('order_partner_id', '=', self.partner_id.id)],
                                 order='create_date DESC').mapped('id')
        else:
            sale_lines = []
        if not sale_lines:
            raise Warning("No sales history found.!")
        else:
            return {
                'domain': [('id', 'in', sale_lines)],
                'views': [(rel_view_id.id, 'tree')],
                'name': _('Sales History'),
                'res_model': 'sale.order.line',
                'view_id': False,
                'type': 'ir.actions.act_window',
            }

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def action_view_past_price(self):
        rel_view_id = self.env.ref(
            'sale_purchase_previous_price.last_sale_product_purchase_prices_view')
        if self.partner_id.id:
            purchase_lines = self.env['purchase.order.line'].search([('partner_id', '=', self.partner_id.id)],
                                                                order='create_date DESC').mapped('id')
        else:
            purchase_lines = []
        if not purchase_lines:
            raise Warning("No purchase history found.!")
        else:
            return {
                'domain': [('id', 'in', purchase_lines)],
                'views': [(rel_view_id.id, 'tree')],
                'name': _('Purchase History'),
                'res_model': 'purchase.order.line',
                'view_id': False,
                'type': 'ir.actions.act_window',
            }