from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = 'product.template'

    ni_is_product_pack = fields.Boolean(string="Is Product Pack")
    ni_bundle_product_ids = fields.One2many('bundle.product', 'ni_product_id', string="Bundle Products")

    @api.model
    def create(self, vals):
        res = super(ProductProduct, self).create(vals)
        if vals.get('ni_is_product_pack'):
            if vals.get('attribute_line_ids'):
                raise ValidationError(
                    _('You cannot create the variant of the Product which is Pack!!!'))

        return res

    # @api.model
    def write(self, vals):
        res = super(ProductProduct, self).write(vals)
        if self.ni_is_product_pack:
            if self.attribute_line_ids:
                raise ValidationError(
                    _('You cannot create the variant of the Product which is Pack!!!'))

        return res
