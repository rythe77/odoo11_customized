# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError

class RmaServiceProductWizard(models.TransientModel):
    _name = "rma.service.product.wizard"
    _description = "RMA Service Product Wizard"

    rma_line_id = fields.Many2one('rma.rma.line', string='RMA Lines', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True, help="Product to be Serviced")
    service_qty = fields.Float('Service Quantity', default = 0.0, digits=dp.get_precision('Product Unit of Measure'),
                                        help="Quantity of product serviced")

    @api.one
    def service_product(self):
        rma_line_id = self.env['rma.rma.line'].browse(self.rma_line_id.id)
        if self.service_qty < 0:
            raise UserError(_('Quantity must be positive!'))
        elif self.service_qty + rma_line_id.serviced_qty > rma_line_id.received_qty:
            raise UserError(_('Total service quantity will be larger than the received quantity. Please check that you serviced the correct quantities!'))
        else:
            rma_line_id.serviced_qty += self.service_qty