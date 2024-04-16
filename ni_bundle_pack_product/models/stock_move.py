from odoo import fields, models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def create(self, vals):
        res = super(StockMove, self).create(vals)
        data = []

        if vals.get('product_id'):
            product_id = self.env['product.product'].browse(vals.get('product_id'))
            if product_id.ni_is_product_pack:
                for bundle_product_id in product_id.ni_bundle_product_ids:
                    product_obj = self.env['product.product'].search(
                        [('product_tmpl_id', '=', bundle_product_id.name.id)])
                    bundle_qty = vals.get('product_uom_qty')
                    quantity = int(bundle_qty) * bundle_product_id.ni_quantity
                    data.append(res.copy({
                        'product_id': product_obj.id,
                        'product_uom_qty': quantity,
                        'product_uom': bundle_product_id.name.uom_id.id
                    }).id)

                return self.browse(data)
        return res
