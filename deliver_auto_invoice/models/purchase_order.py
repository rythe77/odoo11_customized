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
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoices = {}
        references = {}
        invoices_origin = {}
        invoices_name = {}
        for order in self:
            group_key = order.id if grouped else (order.partner_id.id, order.currency_id.id)
            for line in order.order_line.sorted(key=lambda l: l.qty_received - l.qty_invoiced < 0):
                if float_is_zero(line.qty_received - line.qty_invoiced, precision_digits=precision):
                    continue
                if group_key not in invoices:
                    inv_data = order._prepare_invoice()
                    invoice = inv_obj.create(inv_data)
                    references[invoice] = order
                    invoices[group_key] = invoice
                    invoices_origin[group_key] = [invoice.origin]
                    invoices_name[group_key] = [invoice.name]
                elif group_key in invoices:
                    if order.name not in invoices_origin[group_key]:
                        invoices_origin[group_key].append(order.name)
                    if order.partner_ref and order.partner_ref not in invoices_name[group_key]:
                        invoices_name[group_key].append(order.partner_ref)

                if line.qty_received - line.qty_invoiced > 0:
                    line.invoice_line_create(invoices[group_key].id, line.qty_received - line.qty_invoiced)
                elif line.qty_received - line.qty_invoiced < 0 and final:
                    line.invoice_line_create(invoices[group_key].id, line.qty_received - line.qty_invoiced)

            if references.get(invoices.get(group_key)):
                if order not in references[invoices[group_key]]:
                    references[invoices[group_key]] |= order

        for group_key in invoices:
            invoices[group_key].write({'name': ', '.join(invoices_name[group_key]),
                                       'origin': ', '.join(invoices_origin[group_key])})

        if not invoices:
            raise UserError(_('There is no invoicable line.'))

        for invoice in invoices.values():
            if not invoice.invoice_line_ids:
                raise UserError(_('There is no invoicable line.'))
            # If invoice is negative, do a refund invoice instead
            if invoice.amount_total < 0:
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


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.multi
    def _prepare_invoice_line(self, qty):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        """
        self.ensure_one()
        res = {
            'name': self.name,
            'sequence': self.sequence,
            'origin': self.order_id.name,
            'account_id': self.product_id.product_tmpl_id._get_product_accounts()['stock_input'].id,
            'price_unit': self.price_unit,
            'quantity': qty,
            'uom_id': self.product_uom.id,
            'product_id': self.product_id.id or False,
            'account_analytic_id': self.account_analytic_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
        }
        return res

    @api.multi
    def invoice_line_create(self, invoice_id, qty):
        """ Create an invoice line. The quantity to invoice can be positive (invoice) or negative (refund).
            :param invoice_id: integer
            :param qty: float quantity to invoice
            :returns recordset of account.invoice.line created
        """
        invoice_lines = self.env['account.invoice.line']
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for line in self:
            if not float_is_zero(qty, precision_digits=precision):
                vals = line._prepare_invoice_line(qty=qty)
                vals.update({'invoice_id': invoice_id, 'purchase_line_id': line.id})
                invoice_lines |= self.env['account.invoice.line'].create(vals)
        return invoice_lines