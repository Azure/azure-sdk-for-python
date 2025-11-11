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
        
        # Mock the response from the generated operation using proper model
        from azure.communication.sms._generated.models import SmsSendResponse, SmsSendResponseItem
        mock_response = SmsSendResponse(
            value=[
                SmsSendResponseItem(
                    to=phone_number,
                    message_id="id",
                    http_status_code=202,
                    successful=True,
                    error_message=None
                )
            ]
        )
        mock_send.return_value = mock_response

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
        self.assertEqual(phone_number, send_message_request.from_property)
        self.assertEqual(phone_number, send_message_request.sms_recipients[0].to)
        self.assertIsNotNone(send_message_request.sms_recipients[0].repeatability_request_id)
        self.assertIsNotNone(send_message_request.sms_recipients[0].repeatability_first_sent)
        self.assertTrue(send_message_request.sms_send_options.enable_delivery_report)
        self.assertEqual(tag, send_message_request.sms_send_options.tag)

    async def test_get_delivery_report_success_async(self):
        """Test successful delivery report retrieval"""
        mock_response_data = {
            "deliveryStatus": "Delivered",
            "deliveryStatusDetails": "Message delivered successfully",
            "messageId": "test-message-id",
            "from": "+1234567890",
            "to": "+0987654321",
            "receivedTimestamp": "2025-09-12T10:30:00Z"
        }

        with patch("azure.communication.sms._generated.aio.operations.DeliveryReportsOperations.get") as mock_get:
            mock_get.return_value = mock_response_data

            client = SmsClient("https://endpoint", FakeTokenCredential())
            result = await client.get_delivery_report("test-message-id")

            self.assertIsNotNone(result)
            self.assertEqual(result.delivery_status, "Delivered")
            self.assertEqual(result.message_id, "test-message-id")
            self.assertEqual(result.from_property, "+1234567890")
            self.assertEqual(result.to, "+0987654321")
            mock_get.assert_called_once()

    async def test_get_delivery_report_with_delivery_attempts_async(self):
        """Test delivery report with delivery attempts"""
        mock_response_data = {
            "deliveryStatus": "Failed",
            "deliveryStatusDetails": "Message delivery failed",
            "messageId": "test-message-id-2",
            "from": "+1234567890",
            "to": "+0987654321",
            "deliveryAttempts": [
                {
                    "timestamp": "2025-09-12T10:30:00Z",
                    "segmentsSucceeded": 0,
                    "segmentsFailed": 1
                }
            ],
            "receivedTimestamp": "2025-09-12T10:30:00Z"
        }

        with patch("azure.communication.sms._generated.aio.operations.DeliveryReportsOperations.get") as mock_get:
            mock_get.return_value = mock_response_data

            client = SmsClient("https://endpoint", FakeTokenCredential())
            result = await client.get_delivery_report("test-message-id-2")

            self.assertIsNotNone(result)
            self.assertEqual(result.delivery_status, "Failed")
            self.assertEqual(result.message_id, "test-message-id-2")
            self.assertIsNotNone(result.delivery_attempts)
            if result.delivery_attempts:
                self.assertEqual(len(result.delivery_attempts), 1)

    def test_hierarchical_client_pattern_async(self):
        """Test that async SmsClient provides get_opt_outs_client method following Azure SDK Design Guidelines"""
        sms_client = SmsClient("https://endpoint", FakeTokenCredential())
        
        # Test that the method exists and follows naming convention
        self.assertTrue(hasattr(sms_client, 'get_opt_outs_client'))
        self.assertTrue(callable(getattr(sms_client, 'get_opt_outs_client')))
        
        # Test that method follows Azure SDK Design Guidelines naming pattern
        method_name = 'get_opt_outs_client'
        self.assertTrue(method_name.startswith('get_'))
        self.assertTrue(method_name.endswith('_client'))
        
        # Test that the method returns the correct type
        opt_outs_client = sms_client.get_opt_outs_client()
        self.assertIsNotNone(opt_outs_client)
        self.assertEqual(opt_outs_client.__class__.__name__, 'OptOutsClient')
        
        # Test that the sub-client has required methods
        self.assertTrue(hasattr(opt_outs_client, 'add_opt_out'))
        self.assertTrue(hasattr(opt_outs_client, 'remove_opt_out'))
        self.assertTrue(hasattr(opt_outs_client, 'check_opt_out'))
        
        # Test that async methods exist
        self.assertTrue(hasattr(opt_outs_client, '__aenter__'))
        self.assertTrue(hasattr(opt_outs_client, '__aexit__'))
        self.assertTrue(hasattr(opt_outs_client, 'close'))
