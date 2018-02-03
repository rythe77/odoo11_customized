from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    auto_validate_invoice = fields.Boolean("Auto validate invoice",
                                       help='Otherwise created invoice will remain in draft state')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            auto_validate_invoice=params.get_param('auto_validate_invoice.auto_validate_invoice', default=False)
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("auto_validate_invoice.auto_validate_invoice", self.auto_validate_invoice)