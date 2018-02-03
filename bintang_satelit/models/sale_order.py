from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    #Create new fields regarding delivery
    x_transporter_note = fields.Char(
        'Transporter Name', index=False,
        states={'sale': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Input the name of the package transporter here")

    @api.multi
    def _prepare_invoice(self):
        res=super(SaleOrder,self)._prepare_invoice()
        if self.x_transporter_note:
            res.update({
                'x_transporter_note':self.x_transporter_note,
            })
        return res