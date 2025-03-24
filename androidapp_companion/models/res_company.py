from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    app_version = fields.Char('App Version', help="Required minimum app version")