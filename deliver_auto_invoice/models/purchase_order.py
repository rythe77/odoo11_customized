# -*- encoding: utf-8 -*-

import logging
from odoo import api, fields, models, _
from odoo.tools import float_is_zero
import datetime
import pytz
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a purchase order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        # get current logged in user's timezone
        local = pytz.timezone(self.env['res.users'].browse(self._uid).tz) or pytz.utc

        self.ensure_one()
        journal_id = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1).id
        if not journal_id:
            raise UserError(_('Please define an accounting purchase journal for this company.'))
        invoice_vals = {
            'name': self.partner_ref or '',
            'origin': self.name,
            'type': 'in_invoice',
            'account_id': self.partner_id.property_account_payable_id.id,
            'partner_id': self.partner_id.id,
            'journal_id': journal_id,
            'currency_id': self.currency_id.id,
            'comment': self.notes,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_id.property_account_position_id.id,
            'company_id': self.company_id.id,
            'purchase_id': self.id,
            'date_invoice':pytz.utc.localize(datetime.datetime.now()).astimezone(local).strftime('%Y-%m-%d'),
        }
        return invoice_vals

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        """
        Create the invoice associated to the PO.
        :param grouped: if True, invoices are grouped by PO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        inv_obj = self.env['account.invoice']
        invoices = {}
        references = {}
        for order in self:
            group_key = order.id if grouped else (order.partner_id.id, order.currency_id.id)
            if any(line.qty_received - line.qty_invoiced > 0 for line in order.order_line):
                inv_data = order._prepare_invoice()
                invoice = inv_obj.create(inv_data)
                #create invoice line using account.invoice method
                invoice.purchase_order_change()
                references[invoice] = order
                invoices[group_key] = invoice

            if references.get(invoices.get(group_key)):
                if order not in references[invoices[group_key]]:
                    references[invoice] = references[invoice] | order

        if not invoices:
            raise UserError(_('There is no invoicable line.'))

        for invoice in invoices.values():
            if not invoice.invoice_line_ids:
                raise UserError(_('There is no invoicable line.'))
            # If invoice is negative, do a refund invoice instead
            if invoice.amount_untaxed < 0:
                invoice.type = 'in_refund'
                for line in invoice.invoice_line_ids:
                    line.quantity = -line.quantity
            # Necessary to force computation of taxes. In account_invoice, they are triggered
            # by onchanges, which are not triggered when doing a create.
            invoice.compute_taxes()
            invoice.message_post_with_view('mail.message_origin_link',
                values={'self': invoice, 'origin': references[invoice]},
                subtype_id=self.env.ref('mail.mt_note').id)
        return [inv.id for inv in invoices.values()]
