# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import aiounittest
from unittest.mock import Mock, patch, AsyncMock

from azure.core.credentials import AccessToken
from azure.communication.sms.aio import DeliveryReportsClient
from unittest_helpers import mock_response


class FakeTokenCredential(object):
    def __init__(self):
        self.token = AccessToken("Fake Token", 0)

    async def get_token(self, *args, **kwargs):
        return self.token


class TestDeliveryReportsClientAsync(aiounittest.AsyncTestCase):
    def test_invalid_url(self):
        with self.assertRaises(ValueError) as context:
            DeliveryReportsClient(None, FakeTokenCredential(), transport=Mock())

        self.assertTrue("Account URL must be a string." in str(context.exception))

    def test_invalid_credential(self):
        with self.assertRaises(ValueError) as context:
            DeliveryReportsClient("endpoint", None, transport=Mock())

        self.assertTrue("invalid credential from connection string." in str(context.exception))

    async def test_get_status_success(self):
        """Test successful delivery report retrieval"""
        mock_response_data = {
            "deliveryStatus": "Delivered",
            "deliveryStatusDetails": "Message delivered successfully",
            "messageId": "test-message-id",
            "from": "+1234567890",
            "to": "+0987654321",
            "receivedTimestamp": "2025-09-12T10:30:00Z"
        }
        
        with patch("azure.communication.sms._generated.aio.operations._operations.DeliveryReportsOperations.get") as mock_get:
            mock_get.return_value = mock_response_data
            
            client = DeliveryReportsClient("https://endpoint", FakeTokenCredential())
            result = await client.get_status("test-message-id")
            
            self.assertIsNotNone(result)
            self.assertEqual(result.delivery_status, "Delivered")
            self.assertEqual(result.message_id, "test-message-id")
            self.assertEqual(result.from_property, "+1234567890")
            self.assertEqual(result.to, "+0987654321")
            mock_get.assert_called_once()

    async def test_get_status_with_delivery_attempts(self):
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
        
        with patch("azure.communication.sms._generated.aio.operations._operations.DeliveryReportsOperations.get") as mock_get:
            mock_get.return_value = mock_response_data
            
            client = DeliveryReportsClient("https://endpoint", FakeTokenCredential())
            result = await client.get_status("test-message-id-2")
            
            self.assertIsNotNone(result)
            self.assertEqual(result.delivery_status, "Failed")
            self.assertEqual(result.message_id, "test-message-id-2")
            self.assertIsNotNone(result.delivery_attempts)
            self.assertEqual(len(result.delivery_attempts), 1)

    async def test_context_manager(self):
        """Test async context manager functionality"""
        with patch("azure.communication.sms._generated.aio._azure_communication_sms_service.AzureCommunicationSMSService.__aenter__") as mock_enter:
            with patch("azure.communication.sms._generated.aio._azure_communication_sms_service.AzureCommunicationSMSService.__aexit__") as mock_exit:
                mock_enter.return_value = AsyncMock()
                mock_exit.return_value = AsyncMock()
                
                client = DeliveryReportsClient("https://endpoint", FakeTokenCredential())
                
                async with client:
                    # Just test that context manager works
                    pass
                
                mock_enter.assert_called_once()
                mock_exit.assert_called_once()

    async def test_close_method(self):
        """Test that close method works"""
        with patch("azure.communication.sms._generated.aio._azure_communication_sms_service.AzureCommunicationSMSService.close") as mock_close:
            mock_close.return_value = AsyncMock()
            
            client = DeliveryReportsClient("https://endpoint", FakeTokenCredential())
            await client.close()
            
            mock_close.assert_called_once()


if __name__ == "__main__":
    import unittest
    unittest.main()
