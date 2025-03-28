from odoo import models, fields, api


class BannerMessage(models.Model):
    _name = "banner.message"
    _description = "Banner message to display in android app"
    _order = "message"

    message = fields.Text('Banner Message')
    app_companion_id = fields.Many2one('app.companion')
