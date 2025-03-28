from odoo import models, fields, api

class AppCompanion(models.Model):
    _name = "app.companion"
    _description = "Android app companion for app versioning control"
    _order = "name"

    name = fields.Char('App Name', help="Name of the app")
    app_version = fields.Char('App Version', help="Required minimum app version")
    app_link = fields.Text('App Link', help="Link to app apk file for update purpose")
    banner_messages = fields.One2many('banner.message', 'app_companion_id', string='Banner Messages')
