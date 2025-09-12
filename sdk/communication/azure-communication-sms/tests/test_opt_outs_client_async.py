# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import aiounittest
from unittest.mock import Mock, patch, AsyncMock

from azure.core.credentials import AccessToken
from azure.communication.sms.aio import OptOutsClient
from unittest_helpers import mock_response


class FakeTokenCredential(object):
    def __init__(self):
        self.token = AccessToken("Fake Token", 0)

    async def get_token(self, *args, **kwargs):
        return self.token


class TestOptOutsClientAsync(aiounittest.AsyncTestCase):
    def setUp(self):
        self.endpoint = "https://endpoint"
        self.credential = FakeTokenCredential()

    def test_invalid_url(self):
        with self.assertRaises(ValueError) as context:
            OptOutsClient(None, self.credential, transport=Mock())

        self.assertTrue("Account URL must be a string." in str(context.exception))

    def test_invalid_credential(self):
        with self.assertRaises(ValueError) as context:
            OptOutsClient("endpoint", None, transport=Mock())

        self.assertTrue("invalid credential from connection string." in str(context.exception))

    async def test_add_opt_out_success(self):
        """Test successful opt-out addition"""
        mock_response_data = {
            "value": [
                {
                    "to": "+0987654321",
                    "httpStatusCode": 200,
                    "errorMessage": None
                }
            ]
        }

        with patch("azure.communication.sms._generated.aio.operations.OptOutsOperations.add") as mock_add:
            mock_add.return_value = mock_response_data
            
            client = OptOutsClient(self.endpoint, self.credential)
            result = await client.add_opt_out(from_="+1234567890", to="+0987654321")
            
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].to, "+0987654321")
            self.assertEqual(result[0].http_status_code, 200)
            self.assertIsNone(result[0].error_message)

    async def test_add_opt_out_multiple_recipients(self):
        """Test adding multiple recipients to opt-out"""
        mock_response_data = {
            "value": [
                {
                    "to": "+0987654321",
                    "httpStatusCode": 200,
                    "errorMessage": None
                },
                {
                    "to": "+1234567890", 
                    "httpStatusCode": 200,
                    "errorMessage": None
                }
            ]
        }
        
        with patch("azure.communication.sms._generated.aio.operations.OptOutsOperations.add") as mock_add:
            mock_add.return_value = mock_response_data
            
            client = OptOutsClient(self.endpoint, self.credential)
            result = await client.add_opt_out(from_="+5555555555", to=["+0987654321", "+1234567890"])
            
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0].to, "+0987654321")
            self.assertEqual(result[1].to, "+1234567890")

    async def test_remove_opt_out_success(self):
        """Test successful opt-out removal"""
        mock_response_data = {
            "value": [
                {
                    "to": "+0987654321",
                    "httpStatusCode": 200,
                    "errorMessage": None
                }
            ]
        }
        
        with patch("azure.communication.sms._generated.aio.operations.OptOutsOperations.remove") as mock_remove:
            mock_remove.return_value = mock_response_data
            
            client = OptOutsClient(self.endpoint, self.credential)
            result = await client.remove_opt_out(from_="+1234567890", to="+0987654321")
            
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].to, "+0987654321")
            self.assertEqual(result[0].http_status_code, 200)

    async def test_check_opt_out_success(self):
        """Test successful opt-out status check"""
        mock_response_data = {
            "value": [
                {
                    "to": "+0987654321",
                    "httpStatusCode": 200,
                    "isOptedOut": True,
                    "errorMessage": None
                }
            ]
        }
        
        with patch("azure.communication.sms._generated.aio.operations.OptOutsOperations.check") as mock_check:
            mock_check.return_value = mock_response_data
            
            client = OptOutsClient(self.endpoint, self.credential)
            result = await client.check_opt_out(from_="+1234567890", to="+0987654321")
            
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].to, "+0987654321")
            self.assertEqual(result[0].http_status_code, 200)
            self.assertTrue(result[0].is_opted_out)

    async def test_context_manager(self):
        """Test async context manager functionality"""
        with patch("azure.communication.sms._generated.aio._azure_communication_sms_service.AzureCommunicationSMSService.__aenter__") as mock_enter:
            with patch("azure.communication.sms._generated.aio._azure_communication_sms_service.AzureCommunicationSMSService.__aexit__") as mock_exit:
                mock_enter.return_value = AsyncMock()
                mock_exit.return_value = AsyncMock()
                
                client = OptOutsClient(self.endpoint, self.credential)
                
                async with client:
                    # Just test that context manager works
                    pass
                
                mock_enter.assert_called_once()
                mock_exit.assert_called_once()


if __name__ == "__main__":
    import unittest
    unittest.main()
