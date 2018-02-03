# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time
import datetime

class SequenceInherit(models.Model):
    _inherit = 'ir.sequence'
    last_month = fields.Char("last",default="April")    
    
    def _next(self):
        thismonth=datetime.date.today().strftime("%B") 
        if thismonth!=self.last_month:
            self.last_month=thismonth
            self.number_next_actual=1
            self.number_next=1
        result = super(SequenceInherit,self)._next()
        return result