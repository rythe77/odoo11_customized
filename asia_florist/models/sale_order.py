from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    #Create new fields regarding delivery
    x_event_notes = fields.Char(
        'Event Name', index=False,
        states={'sale': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Input name of the event here")
    x_delivery_name = fields.Char(
        'Receiver Name', index=False,
        states={'sale': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Input the name of the package receiver here")
    x_delivery_address = fields.Char(
        'Delivery Address', index=False,
        states={'sale': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Input delivery address here")
    x_delivery_city = fields.Char(
        'City', index=False,
        states={'sale': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Input delivery city here")

    #Create new field to instantly show customer address
    x_partner_address = fields.Char(
        'Address', index=False, compute='_get_partner_address')

    #Create new field regarding invoicing
    x_invoicing_name = fields.Char(
        'Name on Invoice', index=False,
        states={'sale': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Input the name to put on invoice here")
    x_invoicing_address = fields.Char(
        'Invoice Address', index=False,
        states={'sale': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Input invoice address here")
    x_invoicing_city = fields.Char(
        index=False,
        states={'sale': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Input the city name to put on invoice here")

    @api.one
    @api.depends('partner_id')
    def _get_partner_address(self):
        address = ""
        if self.partner_id:
            if self.partner_id.name:
                self.x_invoicing_name = self.partner_id.display_name
            if self.partner_id.street:
                address += self.partner_id.street
            if self.partner_id.street2:
                address += ", " + self.partner_id.street2
            self.x_invoicing_address = address
            if self.partner_id.city:
                address += ", " + self.partner_id.city
                self.x_invoicing_city = self.partner_id.city
        self.x_partner_address = address

    @api.multi
    def _prepare_invoice(self):
        res=super(SaleOrder,self)._prepare_invoice()
        if self.x_delivery_name:
            res.update({
                'x_invoicing_name':self.x_invoicing_name,
                'x_invoicing_address':self.x_invoicing_address,
                'x_invoicing_city':self.x_invoicing_city,
                'x_delivery_name':self.x_delivery_name,
            })
        return res

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    #Modify fields
    product_desc = fields.Text(
        'Specific Request', index=False, store=True,
        states={'sale': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Special request from customer regarding the purchase of this product")
