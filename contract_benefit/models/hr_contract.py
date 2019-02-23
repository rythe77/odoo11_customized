from odoo import api, fields, models, _

class Contract(models.Model):
    _inherit = 'hr.contract'

    benefit = fields.Monetary('Job Benefits', digits=(16, 2), required=True, track_visibility="onchange", help="Employee's monthly benefits.")