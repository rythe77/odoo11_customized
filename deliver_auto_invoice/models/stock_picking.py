# -*- encoding: utf-8 -*-

import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = "stock.picking"

    invoice_id = fields.Many2one(
        'account.invoice', 'Related Invoice',
        copy=False, help="Invoice related to this picking")

    @api.multi
    def action_done(self):
        """
            On transfer validation, auto create invoice
        """
        return_val = super(StockPicking, self).action_done()
        sale_ids = []
        purchase_ids = []
        invoice_ids = []
        for rec in self:
            _logger.debug("Stock Picking Code: %s", rec.picking_type_id.code)
            if rec.sale_id:
                if rec.sale_id.invoice_status == 'to invoice':
                    sale_ids.append(rec.sale_id.id)
            elif rec.purchase_id:
                if rec.purchase_id.invoice_status == 'to invoice':
                    purchase_ids.append(rec.purchase_id.id)

        if sale_ids:
            sales_order = self.env['sale.order'].browse(sale_ids)
            if rec.picking_type_id.code == 'outgoing':
                invoice_ids = sales_order.sudo().action_invoice_create()
            elif rec.picking_type_id.code == 'incoming':
                invoice_ids = sales_order.sudo().action_invoice_create(final=True)
        elif purchase_ids:
            purchase_order = self.env['purchase.order'].browse(purchase_ids)
            if rec.picking_type_id.code == 'incoming':
                invoice_ids = purchase_order.sudo().action_invoice_create()
            elif rec.picking_type_id.code == 'outgoing':
                invoice_ids = purchase_order.sudo().action_invoice_create(final=True)

        #link created invoice to this picking
        for rec in self:
            if len(invoice_ids) == 1:
                rec.invoice_id = invoice_ids[0]

        # validate those invoices if setting is enabled
        invoices = self.env['account.invoice'].browse(invoice_ids)
        for invoice in invoices:
            if self.env['ir.config_parameter'].sudo().get_param('auto_validate_invoice.auto_validate_invoice', default=False):
                invoice.sudo().action_invoice_open()
        return return_val