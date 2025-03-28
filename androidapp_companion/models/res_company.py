from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    app_version = fields.Char('App Version', help="Required minimum app version")
    app_link = fields.Text('App Link', help="Link to app apk file for update purpose")
    banner_messages = fields.One2many('banner.message', 'company_id', string='Banner Messages')
