from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Modify existing fields
    delivery_status = fields.Selection([
        ('delivered', 'Delivered'),
        ('partially_delivered', 'Partially delivered'),
        ('none_delivered', 'Delivery not done')
        ], string='Delivery Status', compute='_get_invoiced', store=True, readonly=True)

    @api.depends('state', 'order_line.invoice_status')
    def _get_invoiced(self):
        super(SaleOrder,self)._get_invoiced()
        for order in self:
            # Ignore the status of the deposit product
            deposit_product_id = self.env['sale.advance.payment.inv']._default_product_id()
            line_invoice_status = [line.invoice_status for line in order.order_line if line.product_id != deposit_product_id]

            if order.state not in ('sale', 'done'):
                invoice_status = 'no'
                delivery_status = 'none_delivered'
            elif any(invoice_status == 'to invoice' for invoice_status in line_invoice_status):
                invoice_status = 'to invoice'
                if all(invoice_status == 'to invoice' for invoice_status in line_invoice_status):
                    delivery_status = 'delivered'
                elif any(invoice_status == 'no' for invoice_status in line_invoice_status):
                    delivery_status = 'partially_delivered'
                elif not any(invoice_status == 'no' for invoice_status in line_invoice_status):
                    delivery_status = 'delivered'
            elif not any(invoice_status == 'to invoice' for invoice_status in line_invoice_status) and not all(invoice_status == 'invoiced' for invoice_status in line_invoice_status):
                invoice_status = 'no'
                if not any(invoice_status == 'invoiced' for invoice_status in line_invoice_status):
                    delivery_status = 'none_delivered'
                else:
                    delivery_status = 'partially_delivered'
            elif all(invoice_status == 'invoiced' for invoice_status in line_invoice_status):
                invoice_status = 'invoiced'
                delivery_status = 'delivered'
            elif all(invoice_status in ['invoiced', 'upselling'] for invoice_status in line_invoice_status):
                invoice_status = 'upselling'
                delivery_status = 'delivered'
            else:
                invoice_status = 'no'
                delivery_status = 'none_delivered'

            order.update({
                'invoice_status': invoice_status,
                'delivery_status': delivery_status
            })
