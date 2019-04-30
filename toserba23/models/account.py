# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.indonesia_template import amount_to_text_id

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    x_collector = fields.Char(
        'Collector', index=False,
        states={'paid': [('readonly', True)], 'cancel': [('readonly', True)]})

    def _prepare_invoice_line_from_po_line(self, line):
        data=super(AccountInvoice,self)._prepare_invoice_line_from_po_line(line)
        if line.x_discount:
            data.update({
                'discount':line.x_discount,
            })
        return data

    @api.multi
    def amount_to_text(self, amount):
        convert_amount_in_words = amount_to_text_id.amount_to_text(amount)
        return convert_amount_in_words

    @api.multi
    def action_invoice_open(self):
        """
            Send notification to customer according to customer settings
        """
        return_val = super(AccountInvoice, self).action_invoice_open()
        for rec in self:
            if rec.partner_id.customer and rec.partner_id.x_is_notify_inv and rec.partner_id.x_notification_method == "email":
                rec.action_send_email()
            elif rec.partner_id.customer and rec.partner_id.x_is_notify_inv and rec.partner_id.x_notification_method == "wa":
                rec.action_send_wa()
        return return_val


    @api.multi
    def action_send_email(self):
        for item in self:
            # Find the e-mail template
            template = self.env.ref('toserba23.invoice_email_template')
            # Send out the e-mail template to the user
            self.env['mail.template'].browse(template.id).send_mail(item.id)
            # Log a note to the sale order record
            item.message_post(body="Email reminder tagihan sudah dikirimkan ke pelanggan")

    @api.multi
    def action_send_wa(self):
        for item in self:
            # Find the sms template
            template = self.env.ref('toserba23.invoice_wa_template')
            # Send out the sms template to the user
            self.env['sms.template'].browse(template.id).send_sms(template.id, item.id)


class AccountPayment(models.Model):
    _inherit = "account.payment"

    x_collector = fields.Char(
        'Collector', index=False,
        states={'posted': [('readonly', True)]})

    @api.multi
    def post(self):
        """
            Send notification to customer according to customer settings
        """
        return_val = super(AccountPayment, self).post()
        for rec in self:
            # Send email notification to customer
            if rec.partner_id.customer and rec.partner_id.x_is_notify_pay and rec.partner_id.x_notification_method == "email":
                rec.action_send_email()
            if rec.partner_id.customer and rec.partner_id.x_is_notify_pay and rec.partner_id.x_notification_method == "wa":
                rec.action_send_wa()
        return return_val

    @api.multi
    def action_send_email(self):
        for item in self:
            # Find the e-mail template
            template = self.env.ref('toserba23.payment_email_template')
            # Send out the e-mail template to the user
            self.env['mail.template'].browse(template.id).send_mail(item.id)

    @api.multi
    def action_send_wa(self):
        for item in self:
            # Find the sms template
            template = self.env.ref('toserba23.payment_wa_template')
            # Send out the sms template to the user
            self.env['sms.template'].browse(template.id).send_sms(template.id, item.id)


class account_register_payments_inherited(models.TransientModel):
    _inherit = 'account.register.payments'

    x_collector = fields.Char('Collector')

    def get_payment_vals(self):
        res=super(account_register_payments_inherited,self).get_payment_vals()
        res.update({
            'x_collector':self.x_collector,
        })
        return res