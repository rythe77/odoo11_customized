from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class BundleProduct(models.Model):
    _name = "bundle.product"

    name = fields.Many2one('product.template', string="Product",
                           domain=[('ni_is_product_pack', '=', False)])
    ni_quantity = fields.Integer(string="Quantity", default=1)
    ni_product_id = fields.Many2one('product.template', string="Product Id")
    ni_uom_id = fields.Many2one('uom.uom', 'Unit of Measure ')

    @api.model
    def create(self, vals):

        if vals.get('name'):
            product_id = self.env['product.template'].browse(vals.get('name'))
            vals.update({'ni_uom_id': product_id.uom_id.id})
        return super(BundleProduct, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('name'):
            product_id = self.env['product.template'].browse(vals.get('name'))
            vals = dict(vals, ni_uom_id=product_id.uom_id.id)
        return super(BundleProduct, self).write(vals)

    @api.constrains('name')
    def _check_product_is_not_bundle(self):
        for record in self:
            if record.name and record.name.ni_is_product_pack:
                raise ValidationError(
                    _('Product "%s" is a bundle product and cannot be used as '
                      'an item of another bundle product.')
                    % record.name.display_name)
