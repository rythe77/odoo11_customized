# -*- coding: utf-8 -*-

from datetime import date

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm_limited(self):
        for sale in self:
            # Check cash payment
            cash_payment = False
            if any(line_id.value == 'balance' and line_id.days == 0 for line_id in sale.payment_term_id.line_ids):
                cash_payment = True

            # Get total credit and current sale total
            credit = sale.partner_id.credit
            current_total = sale.amount_total
            if sale.partner_id.parent_id:
                credit_limit = sale.partner_id.parent_id.credit_limit
            else:
                credit_limit = sale.partner_id.credit_limit

            # Check whether payment due invoice exists for this partner
            invoices_due = False
            today = fields.Date.context_today(self)
            due_invoices = self.env['account.invoice'].search([
                ('partner_id', '=', sale.partner_id.id),
                ('state', '=', 'open'),
                ('type', '=', 'out_invoice'),
                ('date_due', '<', today)
            ])
            if due_invoices:
                invoices_due = True

            # Block confirmation if credit criteria is not met
            if credit_limit == 0 or cash_payment:
                sale.action_confirm()
            elif credit + current_total > credit_limit:
                raise UserError(_('''Cannot confirm the quotation because the customer exceed the credit limit!\n
                                        This customer current credit is Rp %d, including the current quotation, the total is Rp %d.
                                        The credit limit is Rp %d.''') % (credit, current_total + credit, credit_limit))
            elif invoices_due:
                raise UserError(_('''Cannot confirm the quotation because the customer has due invoices!'''))
            else:
                sale.action_confirm()
        return True
