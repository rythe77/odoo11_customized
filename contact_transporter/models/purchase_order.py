# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    #Create new fields
    use_transporter = fields.Boolean(string='Use Transporter?', index=True,
        states={'purchase': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    transporter_id = fields.Many2one("res.partner",
        states={'purchase': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    @api.multi
    def _prepare_picking(self):
        res=super(PurchaseOrder,self)._prepare_picking()
        if self.use_transporter:
            res.update({
                'use_transporter':self.use_transporter,
            })
            if self.transporter_id:
                res.update({
                    'transporter_id':self.transporter_id.id,
                })
        return res
