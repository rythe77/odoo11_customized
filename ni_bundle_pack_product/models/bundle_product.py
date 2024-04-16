from odoo import fields, models, api


class BundleProduct(models.Model):
    _name = "bundle.product"

    name = fields.Many2one('product.template', string="Product")
    ni_quantity = fields.Integer(string="Quantity", default=1)
    ni_product_id = fields.Many2one('product.template', string="Product Id")
    ni_uom_id = fields.Many2one('uom.uom', 'Unit of Measure ')

    @api.model
    def create(self, vals):

        if vals.get('name'):
            product_id = self.env['product.template'].browse(vals.get('name'))
            vals.update({'ni_uom_id': product_id.uom_id.id})
        return super(BundleProduct, self).create(vals)

