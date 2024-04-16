from odoo import fields, models, api


class BundleWizard(models.TransientModel):
    _name = "bundle.wizard"

    ni_pack_name = fields.Many2one('product.template', string="Pack", required=True,)
    ni_quantity = fields.Integer(string="Quantity", default=1)

    def add_pack(self):
        active_id = self.env.context.get('active_id')
        order_id = self.env['sale.order'].browse(active_id)
        bundling_price = order_id.pricelist_id.get_product_price(self.ni_pack_name, self.ni_quantity, order_id.partner_id)
        individual_price = 0

        if self.env.context.get('active_model') == 'sale.order':
            for bundle_product_id in self.ni_pack_name.ni_bundle_product_ids:
                product_id = self.env['product.product'].search([('product_tmpl_id', '=', bundle_product_id.name.id)])
                sale_order_line_obj = self.env['sale.order.line']
                sol = sale_order_line_obj.create({
                    'order_id': active_id,
                    'product_id': product_id.id,
                    'product_uom_qty': bundle_product_id.ni_quantity*self.ni_quantity,
                })
                sol.product_uom_change()
                # Get individual item total price
                individual_price += order_id.pricelist_id.get_product_price(
                    product_id, bundle_product_id.ni_quantity, order_id.partner_id)* \
                                    bundle_product_id.ni_quantity

            # Add discount item to adjust for price difference
            price_difference = bundling_price - individual_price
            if not price_difference == 0:
                discount_product_id = self.env['product.product'].browse(
                    int(self.env['ir.config_parameter'].sudo().get_param('ni_bundle_pack_product.discount_product')))
                sale_order_line_obj = self.env['sale.order.line']
                sale_order_line_obj.create({
                    'order_id': active_id,
                    'product_id': discount_product_id.id,
                    'product_uom_qty': self.ni_quantity,
                    'price_unit': price_difference
                })

        if self.env.context.get('active_model') == 'purchase.order':
            for bundle_product_id in self.ni_pack_name.ni_bundle_product_ids:
                product_id = self.env['product.product'].search([('product_tmpl_id', '=', bundle_product_id.name.id)])
                purchase_order_line_obj = self.env['purchase.order.line']
                pol = purchase_order_line_obj.create({
                    'order_id': active_id,
                    'name': bundle_product_id.name.name,
                    'display_type': '',
                    'date_planned': fields.Datetime.now(),
                    'product_id': product_id.id,
                    'price_unit': product_id.list_price,
                    'product_qty': bundle_product_id.ni_quantity*self.ni_quantity,
                    'product_uom': bundle_product_id.ni_uom_id.id,
                })
                pol._onchange_quantity()
