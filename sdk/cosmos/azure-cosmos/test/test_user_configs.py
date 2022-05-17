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
from azure.cosmos import http_constants, exceptions, PartitionKey
import pytest
import uuid
from test_config import _test_config

# This test class serves to test user-configurable options and verify they are
# properly set and saved into the different object instances that use these
# user-configurable settings.

pytestmark = pytest.mark.cosmosEmulator

DATABASE_ID = "PythonSDKUserConfigTesters"
CONTAINER_ID = "PythonSDKTestContainer"


def get_test_item():
    item = {
        'id': 'Async_' + str(uuid.uuid4()),
        'test_object': True,
        'lastName': 'Smith'
    }
    return item


@pytest.mark.usefixtures("teardown")
class TestUserConfigs(unittest.TestCase):

    def test_invalid_connection_retry_configuration(self):
        try:
            cosmos_client.CosmosClient(url=_test_config.host, credential=_test_config.masterKey,
                                       consistency_level="Session", connection_retry_policy="Invalid Policy")
        except TypeError as e:
            self.assertTrue(str(e).startswith('Unsupported retry policy'))

    def test_enable_endpoint_discovery(self):
        client_false = cosmos_client.CosmosClient(url=_test_config.host, credential=_test_config.masterKey,
                                                  consistency_level="Session", enable_endpoint_discovery=False)
        client_default = cosmos_client.CosmosClient(url=_test_config.host, credential=_test_config.masterKey,
                                                    consistency_level="Session")
        client_true = cosmos_client.CosmosClient(url=_test_config.host, credential=_test_config.masterKey,
                                                 consistency_level="Session", enable_endpoint_discovery=True)

        self.assertFalse(client_false.client_connection.connection_policy.EnableEndpointDiscovery)
        self.assertTrue(client_default.client_connection.connection_policy.EnableEndpointDiscovery)
        self.assertTrue(client_true.client_connection.connection_policy.EnableEndpointDiscovery)

    def test_default_account_consistency(self):
        # These tests use the emulator, which has a default consistency of "Session".
        # If your account has a different level of consistency, make sure it's not the same as the custom_level below.

        # Seems like our live tests are unable to fetch _GetDatabaseAccount method on client initialization, so this
        # test will be disabled if not being ran with the emulator or live.
        # TODO: Look into the configuration running the tests in the pipeline - this is the reason we specify
        #  consistency levels on most test clients.
        if _test_config.host != "https://localhost:8081/":
            return

        client = cosmos_client.CosmosClient(url=_test_config.host, credential=_test_config.masterKey)
        database_account = client.get_database_account()
        account_consistency_level = database_account.ConsistencyPolicy["defaultConsistencyLevel"]
        self.assertEqual(account_consistency_level, "Session")

        # Testing the session token logic works without user passing in Session explicitly
        database = client.create_database(DATABASE_ID)
        container = database.create_container(id=CONTAINER_ID, partition_key=PartitionKey(path="/id"))
        container.create_item(body=get_test_item())
        session_token = client.client_connection.last_response_headers[http_constants.CookieHeaders.SessionToken]
        item2 = get_test_item()
        container.create_item(body=item2)
        session_token2 = client.client_connection.last_response_headers[http_constants.CookieHeaders.SessionToken]

        # Check Session token is being updated to reflect new item created
        self.assertNotEqual(session_token, session_token2)

        container.read_item(item=item2.get("id"), partition_key=item2.get("id"))
        read_session_token = client.client_connection.last_response_headers[http_constants.CookieHeaders.SessionToken]

        # Check Session token remains the same for read operation as with previous create item operation
        self.assertEqual(session_token2, read_session_token)
        client.delete_database(DATABASE_ID)

        # Now testing a user-defined consistency level as opposed to using the account one
        custom_level = "Eventual"
        client = cosmos_client.CosmosClient(url=_test_config.host, credential=_test_config.masterKey,
                                            consistency_level=custom_level)
        database_account = client.get_database_account()
        account_consistency_level = database_account.ConsistencyPolicy["defaultConsistencyLevel"]
        # Here they're not equal, since the headers being used make the client use a different level of consistency
        self.assertNotEqual(
            client.client_connection.default_headers[http_constants.HttpHeaders.ConsistencyLevel],
            account_consistency_level)

        # Test for failure when trying to set consistency to higher level than account level
        custom_level = "Strong"
        client = cosmos_client.CosmosClient(url=_test_config.host, credential=_test_config.masterKey,
                                            consistency_level=custom_level)
        try:
            client.create_database(DATABASE_ID)
        except exceptions.CosmosHttpResponseError as e:
            self.assertEqual(e.status_code, http_constants.StatusCodes.BAD_REQUEST)


if __name__ == "__main__":
    unittest.main()
