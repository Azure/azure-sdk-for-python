# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
from unittest.mock import Mock

from azure.core.credentials import AccessToken
from azure.communication.sms import (
    TelcoMessagingClient,
    SmsClient,
    DeliveryReportsClient,
    OptOutsClient
)
from unittest_helpers import mock_response


class FakeTokenCredential(object):
    def __init__(self):
        self.token = AccessToken("Fake Token", 0)

    def get_token(self, *args, **kwargs):
        return self.token


class TestTelcoMessagingClient(unittest.TestCase):
    def test_invalid_url(self):
        with self.assertRaises(ValueError) as context:
            TelcoMessagingClient(None, FakeTokenCredential(), transport=Mock())

        self.assertTrue("Account URL must be a string." in str(context.exception))

    def test_invalid_credential(self):
        with self.assertRaises(ValueError) as context:
            TelcoMessagingClient("endpoint", None, transport=Mock())

        self.assertTrue("invalid credential from connection string." in str(context.exception))

    def test_initialization_and_sub_clients(self):
        """Test that TelcoMessagingClient properly initializes and exposes sub-clients"""
        endpoint = "https://test.communication.azure.com"
        credential = FakeTokenCredential()
        
        client = TelcoMessagingClient(endpoint, credential, transport=Mock())
        
        # Verify sub-clients are initialized
        self.assertIsNotNone(client.sms)
        self.assertIsNotNone(client.delivery_reports)
        self.assertIsNotNone(client.opt_outs)
        
        # Verify sub-clients are of correct types
        self.assertIsInstance(client.sms, SmsClient)
        self.assertIsInstance(client.delivery_reports, DeliveryReportsClient)
        self.assertIsInstance(client.opt_outs, OptOutsClient)

    def test_from_connection_string(self):
        """Test TelcoMessagingClient factory method from connection string"""
        conn_str = "endpoint=https://test.communication.azure.com;accessKey=test_key"
        
        client = TelcoMessagingClient.from_connection_string(conn_str, transport=Mock())
        
        # Verify sub-clients are initialized
        self.assertIsNotNone(client.sms)
        self.assertIsNotNone(client.delivery_reports)
        self.assertIsNotNone(client.opt_outs)


if __name__ == "__main__":
    unittest.main()
