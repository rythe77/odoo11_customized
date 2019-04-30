# -*- coding: utf-8 -*-
import logging
_logger = logging.getLogger(__name__)

from odoo import api, fields, models

class ResPartnerSms(models.Model):
    _inherit = "res.partner"

    
    @api.onchange('country_id','mobile')
    def _onchange_mobile(self):
        """Tries to convert a local number to e.164 format based on the partners country, don't change if already in e164 format"""
        if self.mobile:                    
            
            if self.country_id and self.country_id.phone_code:
                if self.mobile.startswith("0"):
                    self.mobile = "+" + str(self.country_id.phone_code) + self.mobile[1:].replace(" ","")
                elif self.mobile.startswith("+"):
                    self.mobile = self.mobile.replace(" ","")
                else:
                    self.mobile = "+" + str(self.country_id.phone_code) + self.mobile.replace(" ","")
            else:
                self.mobile = self.mobile.replace(" ","")