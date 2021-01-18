# -*- coding: utf-8 -*-
import requests
import json
import logging
_logger = logging.getLogger(__name__)

from odoo.http import request
from odoo import api, fields, models

class sms_response():
     delivary_state = ""
     response_string = ""
     human_read_error = ""
     mms_url = ""
     message_id = ""

class SmsGatewayZenviva(models.Model):

    _name = "sms.gateway.zenviva"
    _description = "Zenviva SMS Gateway"

    def send_message(self, sms_gateway_id, from_number, to_number, sms_content, my_model_name='', my_record_id=0, media=None, queued_sms_message=None, media_filename=False):
        """Actual Sending of the sms"""
        sms_account = self.env['sms.account'].browse(sms_gateway_id)

        #format the from number before sending
        format_from = from_number
        if " " in format_from: format_from.replace(" ", "")

        #format the to number before sending
        format_to = to_number
        if " " in format_to: format_to.replace(" ", "")

        #send the sms message
        params = {
            'userkey': sms_account.zenviva_userkey,
            'passkey': sms_account.zenviva_passkey,
            'to': format_to,
            'message': sms_content,
        }

        response = requests.post(
            sms_account.zenviva_api_url,
            data=params
        )

        #Analyse the response string and determine if it sent successfully other wise return a human readable error message
        human_read_error = ""
        sms_gateway_message_id = ""
        delivary_state = "failed"
        if response:
            json_response = json.loads(response.text)
            if json_response["status"] == "1":
                delivary_state = "successful"
            elif json_response["status"] == "0":
                delivary_state = "failed"
                human_read_error = json_response["text"]
            else:
                delivary_state = "failed"
                human_read_error = "Kode kesalahan tidak diketahui"

        #send a response back saying how the sending went
        my_sms_response = sms_response()
        my_sms_response.delivary_state = delivary_state
        my_sms_response.response_string = response.text
        my_sms_response.human_read_error = human_read_error
        my_sms_response.message_id = sms_gateway_message_id
        return my_sms_response

    def check_messages(self, account_id, message_id=""):
        """Checks for any new messages or if the message id is specified get only that message"""
        # TDE: FIXME implement getting messages from zenviva api
        # sms_account = self.env['sms.account'].browse(account_id)
        pass

    def _add_message(self, sms_message, account_id):
        """Adds the new sms to the system"""
        # TDE: FIXME waiting for check_messages implementation
        pass


class SmsAccountZenviva(models.Model):

    _inherit = "sms.account"
    _description = "Adds the Zenviva specfic gateway settings to the sms gateway accounts"

    zenviva_api_url = fields.Char(string='API URL', default="https://console.zenziva.net/reguler/api/sendsms/")
    zenviva_userkey = fields.Char(string='User Key')
    zenviva_passkey = fields.Char(string='Pass Key')
    zenviva_last_check_date = fields.Datetime(string="Last Check Date")