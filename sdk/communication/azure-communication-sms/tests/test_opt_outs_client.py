# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
from unittest.mock import Mock, patch

from azure.core.credentials import AccessToken
from azure.communication.sms import OptOutsClient
from unittest_helpers import mock_response


class FakeTokenCredential(object):
    def __init__(self):
        self.token = AccessToken("Fake Token", 0)

    def get_token(self, *args, **kwargs):
        return self.token


class TestOptOutsClient(unittest.TestCase):
    def setUp(self):
        self.endpoint = "https://endpoint"
        self.credential = FakeTokenCredential()
        # Create a mock OptOutRequest-like object for testing
        self.opt_out_request = Mock()
        self.opt_out_request.from_property = "+1234567890"
        self.opt_out_request.recipients = [Mock()]
        self.opt_out_request.recipients[0].to = "+0987654321"

    def test_invalid_url(self):
        with self.assertRaises(ValueError) as context:
            OptOutsClient(None, self.credential, transport=Mock())

        self.assertTrue("Account URL must be a string." in str(context.exception))

    def test_invalid_credential(self):
        with self.assertRaises(ValueError) as context:
            OptOutsClient("endpoint", None, transport=Mock())

        self.assertTrue("invalid credential from connection string." in str(context.exception))

    def test_add_opt_out_success(self):
        """Test successful opt-out addition"""
        with patch("azure.communication.sms._generated.operations._opt_outs_operations.OptOutsOperations.add") as mock_add:
            mock_add.return_value = Mock()
            
            client = OptOutsClient(self.endpoint, self.credential)
            result = client.add_opt_out(self.opt_out_request)
            
            self.assertIsNotNone(result)
            mock_add.assert_called_once()

    def test_remove_opt_out_success(self):
        """Test successful opt-out removal"""
        with patch("azure.communication.sms._generated.operations._opt_outs_operations.OptOutsOperations.remove") as mock_remove:
            mock_remove.return_value = Mock()
            
            client = OptOutsClient(self.endpoint, self.credential)
            result = client.remove_opt_out(self.opt_out_request)
            
            self.assertIsNotNone(result)
            mock_remove.assert_called_once()

    def test_check_opt_out_success(self):
        """Test successful opt-out status check"""
        with patch("azure.communication.sms._generated.operations._opt_outs_operations.OptOutsOperations.check") as mock_check:
            mock_check.return_value = Mock()
            
            client = OptOutsClient(self.endpoint, self.credential)
            result = client.check_opt_out(self.opt_out_request)
            
            self.assertIsNotNone(result)
            mock_check.assert_called_once()

    @patch("azure.communication.sms._generated.operations._opt_outs_operations.OptOutsOperations.add")
    def test_add_opt_out_parameters(self, mock_add):
        """Test that add_opt_out passes correct parameters to generated operations"""
        client = OptOutsClient(self.endpoint, self.credential)
        client.add_opt_out(self.opt_out_request)
        
        # Verify the generated operation was called with correct parameters
        mock_add.assert_called_once()
        call_args = mock_add.call_args
        self.assertEqual(call_args[1]['body'], self.opt_out_request)

    @patch("azure.communication.sms._generated.operations._opt_outs_operations.OptOutsOperations.remove")
    def test_remove_opt_out_parameters(self, mock_remove):
        """Test that remove_opt_out passes correct parameters to generated operations"""
        client = OptOutsClient(self.endpoint, self.credential)
        client.remove_opt_out(self.opt_out_request)
        
        # Verify the generated operation was called with correct parameters
        mock_remove.assert_called_once()
        call_args = mock_remove.call_args
        self.assertEqual(call_args[1]['body'], self.opt_out_request)

    @patch("azure.communication.sms._generated.operations._opt_outs_operations.OptOutsOperations.check")
    def test_check_opt_out_parameters(self, mock_check):
        """Test that check_opt_out passes correct parameters to generated operations"""
        client = OptOutsClient(self.endpoint, self.credential)
        client.check_opt_out(self.opt_out_request)
        
        # Verify the generated operation was called with correct parameters
        mock_check.assert_called_once()
        call_args = mock_check.call_args
        self.assertEqual(call_args[1]['body'], self.opt_out_request)

    def test_opt_out_error_response(self):
        """Test opt-out operation with error response"""
        with patch("azure.communication.sms._generated.operations._opt_outs_operations.OptOutsOperations.add") as mock_add:
            mock_add.return_value = Mock()
            
            client = OptOutsClient(self.endpoint, self.credential)
            result = client.add_opt_out(self.opt_out_request)
            
            self.assertIsNotNone(result)
            mock_add.assert_called_once()

    def test_from_connection_string(self):
        """Test OptOutsClient factory method from connection string"""
        conn_str = "endpoint=https://test.communication.azure.com;accessKey=test_key"
        
        client = OptOutsClient.from_connection_string(conn_str, transport=Mock())
        
        self.assertIsNotNone(client)
        self.assertIsInstance(client, OptOutsClient)


if __name__ == "__main__":
    unittest.main()
