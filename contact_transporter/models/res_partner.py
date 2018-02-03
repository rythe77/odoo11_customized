from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    # Create new fields
    transporter = fields.Boolean(string='Is a Transporter', index=True,
                               help="Check this box if this contact is a transporter.")