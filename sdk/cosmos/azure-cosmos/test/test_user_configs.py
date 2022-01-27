# The MIT License (MIT)
# Copyright (c) 2021 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import unittest

import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos import http_constants
import pytest
from test_config import _test_config

# This test class serves to test user-configurable options and verify they are
# properly set and saved into the different object instances that use these
# user-configurable settings.

pytestmark = pytest.mark.cosmosEmulator


@pytest.mark.usefixtures("teardown")
class TestUserConfigs(unittest.TestCase):

    def test_enable_endpoint_discovery(self):
        client_false = cosmos_client.CosmosClient(url=_test_config.host, credential=_test_config.masterKey,
                                                  enable_endpoint_discovery=False)
        client_default = cosmos_client.CosmosClient(url=_test_config.host, credential=_test_config.masterKey)
        client_true = cosmos_client.CosmosClient(url=_test_config.host, credential=_test_config.masterKey,
                                                 enable_endpoint_discovery=True)

        self.assertFalse(client_false.client_connection.connection_policy.EnableEndpointDiscovery)
        self.assertTrue(client_default.client_connection.connection_policy.EnableEndpointDiscovery)
        self.assertTrue(client_true.client_connection.connection_policy.EnableEndpointDiscovery)

    def test_default_account_consistency(self):
        # These tests use the emulator, which has a default consistency of "Session"
        # If your account has a different level of consistency, make sure it's not the same as the custom_level below

        client = cosmos_client.CosmosClient(url=_test_config.host, credential=_test_config.masterKey)
        database_account = client.get_database_account()
        account_consistency_level = database_account.ConsistencyPolicy["defaultConsistencyLevel"]
        self.assertEqual(client.client_connection.default_headers[http_constants.HttpHeaders.ConsistencyLevel],
                         account_consistency_level)

        # Now testing a user-defined consistency level as opposed to using the account one
        custom_level = "Strong"
        client = cosmos_client.CosmosClient(url=_test_config.host, credential=_test_config.masterKey,
                                            consistency_level=custom_level)
        database_account = client.get_database_account()
        account_consistency_level = database_account.ConsistencyPolicy["defaultConsistencyLevel"]
        # Here they're not equal, since the headers being used make the client use a different level of consistency
        self.assertNotEqual(
            client.client_connection.default_headers[http_constants.HttpHeaders.ConsistencyLevel],
            account_consistency_level)


if __name__ == "__main__":
    unittest.main()
