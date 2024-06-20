# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    #Create new fields
    contact_person = fields.Text(help="Info kontak ini akan tampil pada kop dokumen dan template email")