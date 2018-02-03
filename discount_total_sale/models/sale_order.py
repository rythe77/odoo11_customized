# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp

class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string='Discount type',
                                     readonly=True,states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                     default='percent')
    discount_rate = fields.Float('Discount Rate', digits=dp.get_precision('Account'),
                                 readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    amount_discount = fields.Monetary(string='Discount', store=True, readonly=True, compute='_amount_all',
                                      digits=dp.get_precision('Account'), track_visibility='always')
    amount_undiscounted = fields.Monetary(string='Undiscounted Amout', store=True, readonly=True, compute='_amount_all',
                                      digits=dp.get_precision('Account'))

    @api.onchange('discount_type', 'discount_rate', 'order_line')
    def supply_rate(self):
        for order in self:
            if order.discount_type == 'percent':
                for line in order.order_line:
                    line.discount = order.discount_rate
            else:
                total = discount = 0.0
                for line in order.order_line:
                    total += round((line.product_uom_qty * line.price_unit))
                if order.discount_rate != 0:
                    discount = (order.discount_rate / total) * 100
                else:
                    discount = order.discount_rate
                for line in order.order_line:
                    line.discount = discount

    @api.multi
    def button_dummy(self):
        self.supply_rate()
        return True

    @api.depends('order_line.price_total')
    def _amount_all(self):
        super(SaleOrderInherit,self)._amount_all()
        for order in self:
            amount_discount = 0.0
            for line in order.order_line:
                amount_discount += (line.product_uom_qty * line.price_unit * line.discount)/100
            amount_undiscounted = order.amount_untaxed + amount_discount
            order.update({
                'amount_discount': order.pricelist_id.currency_id.round(amount_discount),
                'amount_undiscounted': order.pricelist_id.currency_id.round(amount_undiscounted),
            })

    @api.multi
    def _prepare_invoice(self):
        res = super(SaleOrderInherit,self)._prepare_invoice()
        res.update({
            'discount_type': self.discount_type,
            'discount_rate': self.discount_rate
        })
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    #Create new fields
    price_subtotal_nodiscount = fields.Monetary(compute='_compute_amount_nodiscount', string='Subtotal', readonly=True, store=True)

    @api.depends('product_uom_qty', 'price_unit')
    def _compute_amount_nodiscount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            subtotal = line.price_unit * line.product_uom_qty
            line.update({
                'price_subtotal_nodiscount': subtotal,
            })