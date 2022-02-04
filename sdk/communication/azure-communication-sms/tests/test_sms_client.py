# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest

from azure.core.credentials import AccessToken
from azure.communication.sms import SmsClient
from unittest_helpers import mock_response

from unittest.mock import Mock, patch

class FakeTokenCredential(object):
    def __init__(self):
        self.token = AccessToken("Fake Token", 0)

    def get_token(self, *args):
        return self.token

class TestSMSClient(unittest.TestCase):
    def test_send_message(self):
        phone_number = "+14255550123"
        raised = False

        def mock_send(*_, **__):
            return mock_response(status_code=202, json_payload={
                "value": [
                    {
                        "to": phone_number,
                        "messageId": "id",
                        "httpStatusCode": "202",
                        "errorMessage": "null",
                        "repeatabilityResult": "accepted",
                        "successful": "true"
                    }
                ]
            })
            
        sms_client = SmsClient("https://endpoint", FakeTokenCredential(), transport=Mock(send=mock_send))

        sms_response = None
        try:
            sms_responses = sms_client.send(
                from_=phone_number,
                to=[phone_number],
                message="Hello World via SMS",
                enable_delivery_report=True,
                tag="custom-tag")
            sms_response = sms_responses[0]
        except:
            raised = True
            raise

        self.assertFalse(raised, 'Expected is no excpetion raised')
        self.assertEqual(phone_number, sms_response.to)
        self.assertIsNotNone(sms_response.message_id)
        self.assertEqual(202, sms_response.http_status_code)
        self.assertIsNotNone(sms_response.error_message)
        self.assertTrue(sms_response.successful)

    @patch(
        "azure.communication.sms._generated.operations._sms_operations.SmsOperations.send"
    )
    def test_send_message_parameters(self, mock_send):
        phone_number = "+14255550123"
        msg = "Hello World via SMS"
        tag = "custom-tag"

        sms_client = SmsClient("https://endpoint", FakeTokenCredential())
        sms_client.send(
            from_=phone_number,
            to=[phone_number],
            message=msg,
            enable_delivery_report=True,
            tag=tag)
        
        send_message_request = mock_send.call_args[0][0]
        self.assertEqual(phone_number, send_message_request.from_property)
        self.assertEqual(phone_number, send_message_request.sms_recipients[0].to)
        self.assertIsNotNone(send_message_request.sms_recipients[0].repeatability_request_id)
        self.assertIsNotNone(send_message_request.sms_recipients[0].repeatability_first_sent)
        self.assertTrue(send_message_request.sms_send_options.enable_delivery_report)
        self.assertEqual(tag, send_message_request.sms_send_options.tag)
