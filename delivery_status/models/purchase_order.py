from odoo import models, fields, api
from odoo.tools.float_utils import float_compare

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # Modify existing fields
    delivery_status = fields.Selection([
        ('delivered', 'Delivered'),
        ('partially_delivered', 'Partially delivered'),
        ('none_delivered', 'Delivery not done')
        ], string='Delivery Status', compute='_get_invoiced', store=True, readonly=True)

    @api.depends('state', 'order_line.qty_invoiced', 'order_line.qty_received', 'order_line.product_qty')
    def _get_invoiced(self):
        super(PurchaseOrder,self)._get_invoiced()
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for order in self:
            if order.state not in ('purchase', 'done'):
                invoice_status = 'no'
                delivery_status = 'none_delivered'
                continue

            if any(float_compare(line.qty_received, line.product_qty, precision_digits=precision) != 0 and line.qty_received != 0 for line in order.order_line):
                delivery_status = 'partially_delivered'
            elif all(float_compare(line.qty_received, 0 if line.product_id.purchase_method == 'purchase' else line.product_qty, precision_digits=precision) == 0 for line in order.order_line):
                delivery_status = 'delivered'
            else:
                delivery_status = 'none_delivered'

            if any(float_compare(line.qty_invoiced, line.product_qty if line.product_id.purchase_method == 'purchase' else line.qty_received, precision_digits=precision) != 0 for line in order.order_line):
                invoice_status = 'to invoice'
            elif all(float_compare(line.qty_invoiced, line.product_qty if line.product_id.purchase_method == 'purchase' else line.qty_received, precision_digits=precision) == 0 for line in order.order_line) and order.invoice_ids and delivery_status == 'delivered':
                invoice_status = 'invoiced'
            else:
                invoice_status = 'no'

            order.update({
                'invoice_status': invoice_status,
                'delivery_status': delivery_status
            })
