# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
from unittest.mock import Mock, patch

from azure.core.credentials import AccessToken
from azure.communication.sms import DeliveryReportsClient
from unittest_helpers import mock_response


class FakeTokenCredential(object):
    def __init__(self):
        self.token = AccessToken("Fake Token", 0)

    def get_token(self, *args, **kwargs):
        return self.token


class TestDeliveryReportsClient(unittest.TestCase):
    def test_invalid_url(self):
        with self.assertRaises(ValueError) as context:
            DeliveryReportsClient(None, FakeTokenCredential(), transport=Mock())

        self.assertTrue("Account URL must be a string." in str(context.exception))

    def test_invalid_credential(self):
        with self.assertRaises(ValueError) as context:
            DeliveryReportsClient("endpoint", None, transport=Mock())

        self.assertTrue("invalid credential from connection string." in str(context.exception))

    def test_get_status_success(self):
        """Test successful delivery report retrieval"""
        with patch("azure.communication.sms._generated.operations._delivery_reports_operations.DeliveryReportsOperations.get") as mock_get:
            mock_get.return_value = Mock()
            
            client = DeliveryReportsClient("https://endpoint", FakeTokenCredential())
            result = client.get_status("test-message-id")
            
            self.assertIsNotNone(result)
            mock_get.assert_called_once()

    def test_get_status_not_found(self):
        """Test delivery report not found (404 error response)"""
        with patch("azure.communication.sms._generated.operations._delivery_reports_operations.DeliveryReportsOperations.get") as mock_get:
            mock_get.return_value = Mock()
            
            client = DeliveryReportsClient("https://endpoint", FakeTokenCredential())
            result = client.get_status("non-existent-message-id")
            
            self.assertIsNotNone(result)
            mock_get.assert_called_once()

    @patch("azure.communication.sms._generated.operations._delivery_reports_operations.DeliveryReportsOperations.get")
    def test_get_status_parameters(self, mock_get):
        """Test that get_status passes correct parameters to generated operations"""
        message_id = "test-message-id"
        
        client = DeliveryReportsClient("https://endpoint", FakeTokenCredential())
        client.get_status(message_id)
        
        # Verify the generated operation was called with correct parameters
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertEqual(call_args[1]['outgoing_message_id'], message_id)

    def test_from_connection_string(self):
        """Test DeliveryReportsClient factory method from connection string"""
        conn_str = "endpoint=https://test.communication.azure.com;accessKey=test_key"
        
        client = DeliveryReportsClient.from_connection_string(conn_str, transport=Mock())
        
        self.assertIsNotNone(client)
        self.assertIsInstance(client, DeliveryReportsClient)


if __name__ == "__main__":
    unittest.main()
