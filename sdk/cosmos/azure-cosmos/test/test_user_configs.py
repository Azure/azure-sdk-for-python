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

if __name__ == "__main__":
    unittest.main()
