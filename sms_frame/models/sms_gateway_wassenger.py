# -*- coding: utf-8 -*-
import requests
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

class SmsGatewayWassenger(models.Model):

    _name = "sms.gateway.wassenger"
    _description = "Wassenger WA Gateway"

    def send_message(self, sms_gateway_id, from_number, to_number, sms_content, my_model_name='', my_record_id=0, media=None, queued_sms_message=None, media_filename=False):
        """Actual Sending of the sms"""
        sms_account = self.env['sms.account'].browse(sms_gateway_id)

        #format the from number before sending
        format_from = from_number
        if " " in format_from: format_from.replace(" ", "")

        #format the to number before sending
        format_to = to_number
        if " " in format_to: format_to.replace(" ", "")

        #send the wa message and/or media
        # TDE: TODO test code against wassenger server
        if media:
            # First upload the media data to Gdrive via wassenger api
            headers = {
                'content-type': "image/jpeg",
                'token': sms_account.wassenger_api_token
            }

            upload_response = requests.request(
                "POST",
                sms_account.wassenger_api_url + "/files",
                data=media,
                headers=headers
            )

            # If upload successfull, send the message with media file, else return upload error message
            if upload_response and upload_response.status_code == 201:
                media_vals = {
                    'file': upload_response.json()["id"],
                    'message': sms_content
                }
                payload = "{\"phone\": \"" + format_to + "\". \"media\": \"" + media_vals + "\". \"device\": \"" + sms_account.device_id + "\"}"
                headers = {
                    'content-type': "application/json",
                    'token': sms_account.wassenger_api_token
                }
                response = requests.request(
                    "POST",
                    sms_account.wassenger_api_url + "/messages",
                    data=payload,
                    headers=headers
                )
            else:
                response = upload_response
        else:
            payload = "{\"phone\": \"" + format_to + "\". \"message\": \"" + sms_content + "\". \"device\": \"" + sms_account.device_id + "\"}"
            headers = {
                'content-type': "application/json",
                'token': sms_account.wassenger_api_token
            }

            response = requests.request(
                "POST",
                sms_account.wassenger_api_url + "/messages",
                data=payload,
                headers=headers
            )

        #Analyse the response string and determine if it sent successfully other wise return a human readable error message
        human_read_error = ""
        sms_gateway_message_id = ""
        delivary_state = "failed"
        if response:
            root = response.json()
            if response.status_code == 201:
                sms_gateway_message_id = root["id"]
                delivary_state = "successful"
            else:
                human_read_error = root["message"]

        #send a response back saying how the sending went
        my_sms_response = sms_response()
        my_sms_response.delivary_state = delivary_state
        my_sms_response.response_string = response.text
        my_sms_response.human_read_error = human_read_error
        my_sms_response.message_id = sms_gateway_message_id
        return my_sms_response

    def check_messages(self, account_id, message_id=""):
        """Checks for any new messages or if the message id is specified get only that message"""
        # TDE: FIXME implement getting messages from wassenger api
        # sms_account = self.env['sms.account'].browse(account_id)
        pass


    def _add_message(self, sms_message, account_id):
        """Adds the new sms to the system"""       
        # TDE: FIXME waiting for check_messages implementation
        pass

    def delivary_receipt(self, account_id, message_id):
        """Updates the sms message when it is successfully received by the mobile phone"""
        # TDE: TODO test code against wassenger server
        sms_account = self.env['sms.account'].browse(account_id)
        headers = {'token': sms_account.wassenger_api_token}
        response = requests.request(
            "GET",
            sms_account.wassenger_api_url + "/messages/" + message_id,
            headers=headers
        )
        delivary_state = ""
        if response:
            root = response.json()
            if response.status_code == 200:
                #map the Wassenger delivary code to the sms delivary states
                if root["deliveryStatus"] == "failed":
                    delivary_state = "failed"
                elif root["deliveryStatus"] == "sent":
                    delivary_state = "successful"
                elif root["deliveryStatus"] == "queued":
                    delivary_state = "successful"
                elif root["deliveryStatus"] == "readed":
                    delivary_state = "DELIVRD"
                elif root["deliveryStatus"] == "played":
                    delivary_state = "DELIVRD"
                elif root["deliveryStatus"] == "delivered":
                    delivary_state = "DELIVRD"
                elif root["deliveryStatus"] == "cancelled":
                    delivary_state = "UNDELIV"
                elif root["deliveryStatus"] == "processing":
                    delivary_state = "successful"
            else:
                human_read_error = root["message"]
        else:
            human_read_error = ""
        my_message = self.env['sms.message'].search([('sms_gateway_message_id', '=', message_id)])
        if len(my_message) > 0:
            my_message[0].status_code = delivary_state
            my_message[0].delivary_error_string = human_read_error


class SmsAccountWassenger(models.Model):

    _inherit = "sms.account"
    _description = "Adds the Wassenger specfic gateway settings to the sms gateway accounts"

    wassenger_api_url = fields.Char(string='API URL', default="https://api.wassenger.com/v1")
    wassenger_api_token = fields.Char(string='Auth Token')
    wassenger_last_check_date = fields.Datetime(string="Last Check Date")
    device_id = fields.Char(string="Device ID")