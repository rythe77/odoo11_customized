from odoo import models, fields, api

class Holidays(models.Model):
    _inherit = 'hr.holidays'

    @api.model
    def create(self, values):
        """ Override to call onchange method on number of days """
        holiday = super(Holidays, self).create(values)
        holiday._onchange_date_to()
        return holiday

    @api.multi
    def write(self, values):
        """ Override to call onchange method on number of days """
        result = super(Holidays, self).write(values)
        if 'date_from' in values or 'date_to' in values:
            self._onchange_date_to()
        return result
