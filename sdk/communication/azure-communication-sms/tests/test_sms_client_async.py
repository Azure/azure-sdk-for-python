# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import aiounittest

from azure.core.credentials import AccessToken
from azure.communication.sms.aio import SmsClient
from unittest_helpers import mock_response

from unittest.mock import Mock, patch


class FakeTokenCredential(object):
    def __init__(self):
        self.token = AccessToken("Fake Token", 0)

    async def get_token(self, *args, **kwargs):
        return self.token


class TestSMSClientAsync(aiounittest.AsyncTestCase):
    def test_invalid_url(self):
        with self.assertRaises(ValueError) as context:
            SmsClient(None, FakeTokenCredential(), transport=Mock())

        self.assertTrue("Account URL must be a string." in str(context.exception))

    def test_invalid_credential(self):
        with self.assertRaises(ValueError) as context:
            SmsClient("endpoint", None, transport=Mock())

        self.assertTrue("invalid credential from connection string." in str(context.exception))

    @patch("azure.communication.sms._generated.aio.operations.SmsOperations.send")
    async def test_send_message_async(self, mock_send):
        phone_number = "+14255550123"
        
        # Mock the response from the generated operation
        mock_send.return_value = {
            "value": [
                {
                    "to": phone_number,
                    "messageId": "id",
                    "httpStatusCode": 202,
                    "errorMessage": None,
                    "repeatabilityResult": "accepted",
                    "successful": True,
                }
            ]
        }

        sms_client = SmsClient("https://endpoint", FakeTokenCredential())

        sms_responses = await sms_client.send(
            from_=phone_number,
            to=[phone_number],
            message="Hello World via SMS",
            enable_delivery_report=True,
            tag="custom-tag",
        )
        
        sms_response = sms_responses[0]
        
        self.assertEqual(phone_number, sms_response.to)
        self.assertIsNotNone(sms_response.message_id)
        self.assertEqual(202, sms_response.http_status_code)
        self.assertTrue(sms_response.successful)
        mock_send.assert_called_once()

    @patch("azure.communication.sms._generated.aio.operations.SmsOperations.send")
    async def test_send_message_parameters_async(self, mock_send):
        phone_number = "+14255550123"
        msg = "Hello World via SMS"
        tag = "custom-tag"

        sms_client = SmsClient("https://endpoint", FakeTokenCredential())
        await sms_client.send(from_=phone_number, to=[phone_number], message=msg, enable_delivery_report=True, tag=tag)

        send_message_request = mock_send.call_args[0][0]
        self.assertEqual(phone_number, send_message_request["from"])
        self.assertEqual(phone_number, send_message_request["smsRecipients"][0]["to"])
        self.assertIsNotNone(send_message_request["smsRecipients"][0]["repeatabilityRequestId"])
        self.assertIsNotNone(send_message_request["smsRecipients"][0]["repeatabilityFirstSent"])
        self.assertTrue(send_message_request["smsSendOptions"]["enableDeliveryReport"])
        self.assertEqual(tag, send_message_request["smsSendOptions"]["tag"])
