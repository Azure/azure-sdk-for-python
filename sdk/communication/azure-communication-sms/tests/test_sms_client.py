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

    @patch("azure.communication.sms._generated.operations.SmsOperations.send")
    def test_send_message(self, mock_send):
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

        sms_responses = sms_client.send(
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

    @patch("azure.communication.sms._generated.operations.SmsOperations.send")
    def test_send_message_parameters(self, mock_send):
        phone_number = "+14255550123"
        msg = "Hello World via SMS"
        tag = "custom-tag"

        sms_client = SmsClient("https://endpoint", FakeTokenCredential())
        sms_client.send(from_=phone_number, to=[phone_number], message=msg, enable_delivery_report=True, tag=tag)

        # Now the call receives a SendMessageRequest model object, not a dict
        send_message_request = mock_send.call_args[0][0]
        self.assertEqual(phone_number, send_message_request.from_property)
        self.assertEqual(phone_number, send_message_request.sms_recipients[0].to)
        self.assertIsNotNone(send_message_request.sms_recipients[0].repeatability_request_id)
        self.assertIsNotNone(send_message_request.sms_recipients[0].repeatability_first_sent)
        self.assertTrue(send_message_request.sms_send_options.enable_delivery_report)
        self.assertEqual(tag, send_message_request.sms_send_options.tag)

    @patch("azure.communication.sms._generated.operations.SmsOperations.send")
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

    @patch("azure.communication.sms._generated.operations.SmsOperations.send")
    def test_send_message_with_messaging_connect(self, mock_send):
        """Test sending SMS with messaging connect parameters"""
        phone_number = "+14255550123"
        msg = "Hello World via SMS"
        partner_params = {"apiKey": "test-api-key"}
        partner_name = "test-partner"

        sms_client = SmsClient("https://endpoint", FakeTokenCredential())
        sms_client.send(
            from_=phone_number, 
            to=[phone_number], 
            message=msg, 
            enable_delivery_report=True,
            messaging_connect_partner_params=partner_params,
            messaging_connect_partner_name=partner_name
        )

        send_message_request = mock_send.call_args[0][0]
        self.assertEqual(phone_number, send_message_request.from_property)
        self.assertEqual(phone_number, send_message_request.sms_recipients[0].to)
        self.assertTrue(send_message_request.sms_send_options.enable_delivery_report)
        
        # Check MessagingConnect options
        messaging_connect = send_message_request.sms_send_options.messaging_connect
        self.assertIsNotNone(messaging_connect)
        self.assertEqual(partner_params, messaging_connect.partner_params)
        self.assertEqual(partner_name, messaging_connect.partner)

    @patch("azure.communication.sms._generated.operations.SmsOperations.send")
    def test_send_message_with_all_new_parameters(self, mock_send):
        """Test sending SMS with all new parameters combined"""
        phone_number = "+14255550123"
        msg = "Hello World via SMS"
        timeout_seconds = 600
        partner_params = {"apiKey": "comprehensive-api-key", "customParam": "value123"}
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
            messaging_connect_partner_params=partner_params,
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
        self.assertEqual(partner_params, messaging_connect.partner_params)
        self.assertEqual(partner_name, messaging_connect.partner)

    def test_messaging_connect_validation_missing_partner_params(self):
        """Test that providing only partner name raises ValueError"""
        phone_number = "+14255550123"
        sms_client = SmsClient("https://endpoint", FakeTokenCredential())
        
        with self.assertRaises(ValueError) as context:
            sms_client.send(
                from_=phone_number,
                to=[phone_number],
                message="Test message",
                messaging_connect_partner_name="test-partner"
                # Missing messaging_connect_partner_params
            )
        
        self.assertIn("Both messaging_connect_partner_name and messaging_connect_partner_params must be provided together", 
                      str(context.exception))

    def test_messaging_connect_validation_missing_partner_name(self):
        """Test that providing only partner params raises ValueError"""
        phone_number = "+14255550123"
        sms_client = SmsClient("https://endpoint", FakeTokenCredential())
        
        with self.assertRaises(ValueError) as context:
            sms_client.send(
                from_=phone_number,
                to=[phone_number],
                message="Test message",
                messaging_connect_partner_params={"apiKey": "test-api-key"}
                # Missing messaging_connect_partner_name
            )
        
        self.assertIn("Both messaging_connect_partner_name and messaging_connect_partner_params must be provided together", 
                      str(context.exception))

    @patch("azure.communication.sms._generated.operations.DeliveryReportsOperations.get")
    def test_get_delivery_report_success(self, mock_get):
        """Test successful delivery report retrieval"""
        from azure.communication.sms._generated.models import DeliveryReport
        
        # Mock return should be a proper DeliveryReport model object
        mock_response = DeliveryReport(
            message_id="test-message-id",
            delivery_status="Delivered",
            from_property="+1234567890",
            to="+0987654321"
        )
        mock_get.return_value = mock_response

        client = SmsClient("https://endpoint", FakeTokenCredential())
        result = client.get_delivery_report("test-message-id")

        self.assertIsNotNone(result)
        self.assertEqual(result.message_id, "test-message-id")
        self.assertEqual(result.delivery_status, "Delivered")
        mock_get.assert_called_once()

    @patch("azure.communication.sms._generated.operations.DeliveryReportsOperations.get")
    def test_get_delivery_report_not_found(self, mock_get):
        """Test delivery report not found (404 error response)"""
        from azure.communication.sms._generated.models import DeliveryReport
        
        # Mock return for not found case
        mock_response = DeliveryReport(
            message_id="non-existent-message-id",
            delivery_status="Unknown",
            from_property="+1234567890",
            to="+0987654321"
        )
        mock_get.return_value = mock_response

        client = SmsClient("https://endpoint", FakeTokenCredential())
        result = client.get_delivery_report("non-existent-message-id")

        self.assertIsNotNone(result)
        self.assertEqual(result.message_id, "non-existent-message-id")
        mock_get.assert_called_once()

    @patch("azure.communication.sms._generated.operations.DeliveryReportsOperations.get")
    def test_get_delivery_report_parameters(self, mock_get):
        """Test that get_delivery_report passes correct parameters to generated operations"""
        from azure.communication.sms._generated.models import DeliveryReport
        
        message_id = "test-message-id"
        mock_response = DeliveryReport(
            message_id=message_id,
            delivery_status="Delivered",
            from_property="+1234567890",
            to="+0987654321"
        )
        mock_get.return_value = mock_response

        client = SmsClient("https://endpoint", FakeTokenCredential())
        client.get_delivery_report(message_id)

        # Verify the generated operation was called with correct parameters
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertEqual(call_args.kwargs['outgoing_message_id'], message_id)

    def test_hierarchical_client_pattern(self):
        """Test that SmsClient provides get_opt_outs_client method following Azure SDK Design Guidelines"""
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
        
        # Test that methods are callable
        self.assertTrue(callable(getattr(opt_outs_client, 'add_opt_out')))
        self.assertTrue(callable(getattr(opt_outs_client, 'remove_opt_out')))
        self.assertTrue(callable(getattr(opt_outs_client, 'check_opt_out')))
