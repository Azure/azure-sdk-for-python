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
        # Test phone numbers for opt-out operations
        self.from_phone = "+1234567890"
        self.to_phone = "+0987654321"
        self.to_phones = ["+0987654321", "+0987654322"]

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
        with patch("azure.communication.sms._generated.operations.OptOutsOperations.add") as mock_add:
            mock_add.return_value = {"value": [{"to": self.to_phone, "httpStatusCode": 202}]}
            
            client = OptOutsClient(self.endpoint, self.credential)
            result = client.add_opt_out(from_=self.from_phone, to=self.to_phone)
            
            self.assertIsNotNone(result)
            self.assertEqual(len(result), 1)
            mock_add.assert_called_once()

    def test_remove_opt_out_success(self):
        """Test successful opt-out removal"""
        with patch("azure.communication.sms._generated.operations.OptOutsOperations.remove") as mock_remove:
            mock_remove.return_value = {"value": [{"to": self.to_phone, "httpStatusCode": 202}]}
            
            client = OptOutsClient(self.endpoint, self.credential)
            result = client.remove_opt_out(from_=self.from_phone, to=self.to_phone)
            
            self.assertIsNotNone(result)
            self.assertEqual(len(result), 1)
            mock_remove.assert_called_once()

    def test_check_opt_out_success(self):
        """Test successful opt-out status check"""
        with patch("azure.communication.sms._generated.operations.OptOutsOperations.check") as mock_check:
            mock_check.return_value = {"value": [{"to": self.to_phone, "httpStatusCode": 200, "isOptedOut": True}]}
            
            client = OptOutsClient(self.endpoint, self.credential)
            result = client.check_opt_out(from_=self.from_phone, to=self.to_phone)
            
            self.assertIsNotNone(result)
            self.assertEqual(len(result), 1)
            self.assertTrue(result[0].is_opted_out)
            self.assertEqual(result[0].http_status_code, 200)
            mock_check.assert_called_once()

    @patch("azure.communication.sms._generated.operations.OptOutsOperations.add")
    def test_add_opt_out_parameters(self, mock_add):
        """Test that add_opt_out passes correct parameters to generated operations"""
        mock_add.return_value = {"value": [{"to": self.to_phone, "httpStatusCode": 202}]}
        
        client = OptOutsClient(self.endpoint, self.credential)
        client.add_opt_out(from_=self.from_phone, to=self.to_phone)
        
        # Verify the generated operation was called with correct parameters
        mock_add.assert_called_once()
        call_args = mock_add.call_args
        # Check that the request was created with correct from_ and recipients
        request_dict = call_args.kwargs['body']
        self.assertEqual(request_dict["from"], self.from_phone)
        self.assertEqual(len(request_dict["recipients"]), 1)
        self.assertEqual(request_dict["recipients"][0]["to"], self.to_phone)

    @patch("azure.communication.sms._generated.operations.OptOutsOperations.remove")
    def test_remove_opt_out_parameters(self, mock_remove):
        """Test that remove_opt_out passes correct parameters to generated operations"""
        mock_remove.return_value = {"value": [{"to": self.to_phone, "httpStatusCode": 202}]}
        
        client = OptOutsClient(self.endpoint, self.credential)
        client.remove_opt_out(from_=self.from_phone, to=self.to_phone)
        
        # Verify the generated operation was called with correct parameters
        mock_remove.assert_called_once()
        call_args = mock_remove.call_args
        # Check that the request was created with correct from_ and recipients
        request_dict = call_args.kwargs['body']
        self.assertEqual(request_dict["from"], self.from_phone)
        self.assertEqual(len(request_dict["recipients"]), 1)
        self.assertEqual(request_dict["recipients"][0]["to"], self.to_phone)

    @patch("azure.communication.sms._generated.operations.OptOutsOperations.check")
    def test_check_opt_out_parameters(self, mock_check):
        """Test that check_opt_out passes correct parameters to generated operations"""
        mock_check.return_value = {"value": [{"to": self.to_phone, "httpStatusCode": 200, "isOptedOut": True}]}
        
        client = OptOutsClient(self.endpoint, self.credential)
        client.check_opt_out(from_=self.from_phone, to=self.to_phone)
        
        # Verify the generated operation was called with correct parameters
        mock_check.assert_called_once()
        call_args = mock_check.call_args
        # Check that the request was created with correct from_ and recipients
        request_dict = call_args.kwargs['body']
        self.assertEqual(request_dict["from"], self.from_phone)
        self.assertEqual(len(request_dict["recipients"]), 1)
        self.assertEqual(request_dict["recipients"][0]["to"], self.to_phone)

    def test_opt_out_error_response(self):
        """Test opt-out operation with error response"""
        with patch("azure.communication.sms._generated.operations.OptOutsOperations.add") as mock_add:
            mock_add.return_value = {"value": [{"to": self.to_phone, "httpStatusCode": 400}]}
            
            client = OptOutsClient(self.endpoint, self.credential)
            result = client.add_opt_out(from_=self.from_phone, to=self.to_phone)
            
            self.assertIsNotNone(result)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].http_status_code, 400)
            mock_add.assert_called_once()

    def test_from_connection_string(self):
        """Test OptOutsClient factory method from connection string"""
        conn_str = "endpoint=https://test.communication.azure.com;accessKey=test_key"
        
        client = OptOutsClient.from_connection_string(conn_str, transport=Mock())
        
        self.assertIsNotNone(client)
        self.assertIsInstance(client, OptOutsClient)


if __name__ == "__main__":
    unittest.main()
