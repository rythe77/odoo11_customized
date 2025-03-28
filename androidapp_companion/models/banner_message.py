from odoo import models, fields, api


class BannerMessage(models.Model):
    _name = "banner.message"
    _description = "Banner message to display in android app"
    _order = "message"

    message = fields.Text('Banner Message')
    company_id = fields.Many2one('res.company',
        change_default=True, default=lambda self: self.env['res.company']._company_default_get('androidapp_companion'))
