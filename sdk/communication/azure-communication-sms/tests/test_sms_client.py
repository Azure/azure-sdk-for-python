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

    def get_token(self, *args, **kwargs):
        return self.token


class TestSMSClient(unittest.TestCase):
    def test_invalid_url(self):
        with self.assertRaises(ValueError) as context:
            SmsClient(None, FakeTokenCredential(), transport=Mock())

        self.assertTrue("Account URL must be a string." in str(context.exception))

    def test_invalid_credential(self):
        with self.assertRaises(ValueError) as context:
            SmsClient("endpoint", None, transport=Mock())

        self.assertTrue("invalid credential from connection string." in str(context.exception))

    def test_send_message(self):
        phone_number = "+14255550123"
        raised = False

        def mock_send(*_, **__):
            return mock_response(
                status_code=202,
                json_payload={
                    "value": [
                        {
                            "to": phone_number,
                            "messageId": "id",
                            "httpStatusCode": "202",
                            "errorMessage": "null",
                            "repeatabilityResult": "accepted",
                            "successful": "true",
                        }
                    ]
                },
            )

        sms_client = SmsClient("https://endpoint", FakeTokenCredential(), transport=Mock(send=mock_send))

        sms_response = None
        try:
            sms_responses = sms_client.send(
                from_=phone_number,
                to=[phone_number],
                message="Hello World via SMS",
                enable_delivery_report=True,
                tag="custom-tag",
            )
            sms_response = sms_responses[0]
        except:
            raised = True
            raise

        self.assertFalse(raised, "Expected is no excpetion raised")
        self.assertEqual(phone_number, sms_response.to)
        self.assertIsNotNone(sms_response.message_id)
        self.assertEqual(202, sms_response.http_status_code)
        self.assertIsNotNone(sms_response.error_message)
        self.assertTrue(sms_response.successful)

    @patch("azure.communication.sms._generated.operations._sms_operations.SmsOperations.send")
    def test_send_message_parameters(self, mock_send):
        phone_number = "+14255550123"
        msg = "Hello World via SMS"
        tag = "custom-tag"

        sms_client = SmsClient("https://endpoint", FakeTokenCredential())
        sms_client.send(from_=phone_number, to=[phone_number], message=msg, enable_delivery_report=True, tag=tag)

        send_message_request = mock_send.call_args[0][0]
        self.assertEqual(phone_number, send_message_request.from_property)
        self.assertEqual(phone_number, send_message_request.sms_recipients[0].to)
        self.assertIsNotNone(send_message_request.sms_recipients[0].repeatability_request_id)
        self.assertIsNotNone(send_message_request.sms_recipients[0].repeatability_first_sent)
        self.assertTrue(send_message_request.sms_send_options.enable_delivery_report)
        self.assertEqual(tag, send_message_request.sms_send_options.tag)

    @patch("azure.communication.sms._generated.operations._sms_operations.SmsOperations.send")
    def test_send_message_with_delivery_timeout(self, mock_send):
        """Test sending SMS with delivery report timeout parameter"""
        phone_number = "+14255550123"
        msg = "Hello World via SMS"
        timeout_seconds = 300

        sms_client = SmsClient("https://endpoint", FakeTokenCredential())
        sms_client.send(
            from_=phone_number, 
            to=[phone_number], 
            message=msg, 
            enable_delivery_report=True,
            delivery_report_timeout_in_seconds=timeout_seconds
        )

        send_message_request = mock_send.call_args[0][0]
        self.assertEqual(phone_number, send_message_request.from_property)
        self.assertEqual(phone_number, send_message_request.sms_recipients[0].to)
        self.assertTrue(send_message_request.sms_send_options.enable_delivery_report)
        self.assertEqual(timeout_seconds, send_message_request.sms_send_options.delivery_report_timeout_in_seconds)

    @patch("azure.communication.sms._generated.operations._sms_operations.SmsOperations.send")
    def test_send_message_with_messaging_connect(self, mock_send):
        """Test sending SMS with messaging connect parameters"""
        phone_number = "+14255550123"
        msg = "Hello World via SMS"
        api_key = "test-api-key"
        partner_name = "test-partner"

        sms_client = SmsClient("https://endpoint", FakeTokenCredential())
        sms_client.send(
            from_=phone_number, 
            to=[phone_number], 
            message=msg, 
            enable_delivery_report=True,
            messaging_connect_api_key=api_key,
            messaging_connect_partner_name=partner_name
        )

        send_message_request = mock_send.call_args[0][0]
        self.assertEqual(phone_number, send_message_request.from_property)
        self.assertEqual(phone_number, send_message_request.sms_recipients[0].to)
        self.assertTrue(send_message_request.sms_send_options.enable_delivery_report)
        
        # Check MessagingConnect options
        messaging_connect = send_message_request.sms_send_options.messaging_connect
        self.assertIsNotNone(messaging_connect)
        self.assertEqual(api_key, messaging_connect.api_key)
        self.assertEqual(partner_name, messaging_connect.partner)

    @patch("azure.communication.sms._generated.operations._sms_operations.SmsOperations.send")
    def test_send_message_with_all_new_parameters(self, mock_send):
        """Test sending SMS with all new parameters combined"""
        phone_number = "+14255550123"
        msg = "Hello World via SMS"
        timeout_seconds = 600
        api_key = "comprehensive-api-key"
        partner_name = "comprehensive-partner"
        tag = "comprehensive-tag"

        sms_client = SmsClient("https://endpoint", FakeTokenCredential())
        sms_client.send(
            from_=phone_number, 
            to=[phone_number], 
            message=msg, 
            enable_delivery_report=True,
            tag=tag,
            delivery_report_timeout_in_seconds=timeout_seconds,
            messaging_connect_api_key=api_key,
            messaging_connect_partner_name=partner_name
        )

        send_message_request = mock_send.call_args[0][0]
        self.assertEqual(phone_number, send_message_request.from_property)
        self.assertEqual(phone_number, send_message_request.sms_recipients[0].to)
        self.assertTrue(send_message_request.sms_send_options.enable_delivery_report)
        self.assertEqual(tag, send_message_request.sms_send_options.tag)
        self.assertEqual(timeout_seconds, send_message_request.sms_send_options.delivery_report_timeout_in_seconds)
        
        # Check MessagingConnect options
        messaging_connect = send_message_request.sms_send_options.messaging_connect
        self.assertIsNotNone(messaging_connect)
        self.assertEqual(api_key, messaging_connect.api_key)
        self.assertEqual(partner_name, messaging_connect.partner)

    def test_messaging_connect_validation_missing_api_key(self):
        """Test that providing only partner name raises ValueError"""
        phone_number = "+14255550123"
        sms_client = SmsClient("https://endpoint", FakeTokenCredential())
        
        with self.assertRaises(ValueError) as context:
            sms_client.send(
                from_=phone_number,
                to=[phone_number],
                message="Test message",
                messaging_connect_partner_name="test-partner"
                # Missing messaging_connect_api_key
            )
        
        self.assertIn("Both messaging_connect_api_key and messaging_connect_partner_name must be provided together", 
                      str(context.exception))

    def test_messaging_connect_validation_missing_partner_name(self):
        """Test that providing only API key raises ValueError"""
        phone_number = "+14255550123"
        sms_client = SmsClient("https://endpoint", FakeTokenCredential())
        
        with self.assertRaises(ValueError) as context:
            sms_client.send(
                from_=phone_number,
                to=[phone_number],
                message="Test message",
                messaging_connect_api_key="test-api-key"
                # Missing messaging_connect_partner_name
            )
        
        self.assertIn("Both messaging_connect_api_key and messaging_connect_partner_name must be provided together", 
                      str(context.exception))
