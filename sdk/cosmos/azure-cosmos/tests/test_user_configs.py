# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest

import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos import http_constants, exceptions, PartitionKey
from test_config import TestConfig


# This test class serves to test user-configurable options and verify they are
# properly set and saved into the different object instances that use these
# user-configurable settings.


def get_test_item():
    item = {
        'id': 'Async_' + str(uuid.uuid4()),
        'test_object': True,
        'lastName': 'Smith'
    }
    return item


@pytest.mark.cosmosLong
class TestUserConfigs(unittest.TestCase):

    def test_invalid_connection_retry_configuration(self):
        try:
            cosmos_client.CosmosClient(url=TestConfig.host, credential=TestConfig.masterKey,
                                       consistency_level="Session", connection_retry_policy="Invalid Policy")
        except TypeError as e:
            self.assertTrue(str(e).startswith('Unsupported retry policy'))

    def test_enable_endpoint_discovery(self):
        client_false = cosmos_client.CosmosClient(url=TestConfig.host, credential=TestConfig.masterKey,
                                                  consistency_level="Session", enable_endpoint_discovery=False)
        client_default = cosmos_client.CosmosClient(url=TestConfig.host, credential=TestConfig.masterKey,
                                                    consistency_level="Session")
        client_true = cosmos_client.CosmosClient(url=TestConfig.host, credential=TestConfig.masterKey,
                                                 consistency_level="Session", enable_endpoint_discovery=True)

        self.assertFalse(client_false.client_connection.connection_policy.EnableEndpointDiscovery)
        self.assertTrue(client_default.client_connection.connection_policy.EnableEndpointDiscovery)
        self.assertTrue(client_true.client_connection.connection_policy.EnableEndpointDiscovery)

    def test_authentication_error(self):
        try:
            cosmos_client.CosmosClient(url=TestConfig.host, credential="wrong_key")
        except exceptions.CosmosHttpResponseError as e:
            self.assertEqual(e.status_code, http_constants.StatusCodes.UNAUTHORIZED)

    def test_default_account_consistency(self):
        database_id = "PythonSDKUserConfigTesters-" + str(uuid.uuid4())
        container_id = "PythonSDKTestContainer-" + str(uuid.uuid4())
        client = cosmos_client.CosmosClient(url=TestConfig.host, credential=TestConfig.masterKey)
        database_account = client.get_database_account()
        account_consistency_level = database_account.ConsistencyPolicy["defaultConsistencyLevel"]
        self.assertEqual(account_consistency_level, "Session")

        # Testing the session token logic works without user passing in Session explicitly
        database = client.create_database(database_id)
        container = database.create_container(id=container_id, partition_key=PartitionKey(path="/id"))
        create_response = container.create_item(body=get_test_item())
        session_token = create_response.get_response_headers()[http_constants.CookieHeaders.SessionToken]
        item2 = get_test_item()
        create_response = container.create_item(body=item2)
        session_token2 = create_response.get_response_headers()[http_constants.CookieHeaders.SessionToken]

        # Check Session token is being updated to reflect new item created
        self.assertNotEqual(session_token, session_token2)

        read_response = container.read_item(item=item2.get("id"), partition_key=item2.get("id"))
        read_session_token = read_response.get_response_headers()[http_constants.CookieHeaders.SessionToken]

        # Check Session token remains the same for read operation as with previous create item operation
        self.assertEqual(session_token2, read_session_token)
        client.delete_database(database_id)

        # Now testing a user-defined consistency level as opposed to using the account one
        custom_level = "Eventual"
        eventual_consistency_client = cosmos_client.CosmosClient(url=TestConfig.host,
                                                                 credential=TestConfig.masterKey,
                                                                 consistency_level=custom_level)
        database_account = eventual_consistency_client.get_database_account()
        account_consistency_level = database_account.ConsistencyPolicy["defaultConsistencyLevel"]
        # Here they're not equal, since the headers being used make the client use a different level of consistency
        self.assertNotEqual(
            eventual_consistency_client
            .client_connection.default_headers[http_constants.HttpHeaders.ConsistencyLevel],
            account_consistency_level)

        # Test for failure when trying to set consistency to higher level than account level
        custom_level = "Strong"
        strong_consistency_client = cosmos_client.CosmosClient(url=TestConfig.host,
                                                               credential=TestConfig.masterKey,
                                                               consistency_level=custom_level)
        try:
            strong_consistency_client.create_database(database_id)
        except exceptions.CosmosHttpResponseError as e:
            self.assertEqual(e.status_code, http_constants.StatusCodes.BAD_REQUEST)


if __name__ == "__main__":
    unittest.main()
