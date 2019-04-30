# -*- coding: utf-8 -*
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)
from odoo import api, fields, models

class SmsCompose(models.TransientModel):
    """Composing SMS wizard."""
    _name = "sms.compose.wizard"
    _description = 'Composing SMS wizard'

    record_id = fields.Integer()
    model = fields.Char()
    sms_template_id = fields.Many2one('sms.template', string="Template")
    from_mobile_id = fields.Many2one('sms.number', required=True, string="From Mobile") 
    to_number = fields.Char(required=True, string='To Mobile Number', readonly=True)
    sms_content = fields.Text(string='SMS Content')
    media_id = fields.Binary(string="Media (MMS)")      
    media_filename = fields.Char(string="Media Filename")
    delivery_time = fields.Datetime(string="Delivery Time")

    @api.onchange('sms_template_id')
    def _onchange_sms_template_id(self):
        """Prefills from mobile, sms_account and sms_content but allow them to manually change the content after"""
        if self.sms_template_id.id != False:

            sms_rendered_content = self.env['sms.template'].render_template(self.sms_template_id.template_body, self.sms_template_id.model_id.model, self.record_id)

            self.from_mobile_id = self.sms_template_id.from_mobile_verified_id.id
            self.media_id = self.sms_template_id.media_id
            self.media_filename = self.sms_template_id.media_filename
            self.sms_content = sms_rendered_content

    @api.multi
    def send_entity(self):
        """Send the sms by creating queued sms"""
        self.ensure_one()

        my_model = self.env['ir.model'].search([('model', '=', self.model)])
        vals = {
            'record_id': self.record_id,
            'model_id': my_model[0].id,
            'account_id': self.from_mobile_id.account_id.id,
            'from_mobile': self.from_mobile_id.mobile_number,
            'to_mobile': self.to_number,
            'sms_content': self.sms_content,
            'status_string': '-',
            'direction': 'O',
            'message_date': datetime.utcnow(),
            'status_code': 'queued',
            'by_partner_id': self.env.user.partner_id.id
        }

        if self.delivery_time:
            vals.update({
                'message_date': self.delivery_time
            })
        if self.media_id:
            vals.update({
                'media_id': self.media_id
            })

        # Create the queued sms
        self.env['sms.message'].create(vals)
        return True