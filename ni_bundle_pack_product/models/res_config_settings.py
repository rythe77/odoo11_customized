from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    discount_product = fields.Many2one("product.product", "Discount Product",
                                       domain="[('type', '=', 'service')]",
                                       help='This product will be added to adjust pricing of bundling product')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            discount_product=int(params.get_param('ni_bundle_pack_product.discount_product', default=False))
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("ni_bundle_pack_product.discount_product", self.discount_product.id)
