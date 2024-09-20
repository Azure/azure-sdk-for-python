# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest
from requests import session

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.partition_key as partition_key
import test_config
from azure.cosmos._change_feed.feed_range import FeedRangeEpk, FeedRangePartitionKey
from azure.cosmos._routing.routing_range import Range
from test.test_config import TestConfig



@pytest.fixture(scope="class")
def setup():
    if (TestRequestContext.masterKey == '[YOUR_KEY_HERE]' or
            TestRequestContext.host == '[YOUR_ENDPOINT_HERE]'):
        raise Exception(
            "You must specify your Azure Cosmos account values for "
            "'masterKey' and 'host' at the top of this class to run the "
            "tests.")
    test_client = cosmos_client.CosmosClient(TestRequestContext.host, TestConfig.credential),
    created_db = test_client[0].get_database_client(TestRequestContext.TEST_DATABASE_ID)
    return {
        "created_db": created_db,
        "created_collection": created_db.get_container_client(TestRequestContext.TEST_CONTAINER_ID)
    }

@pytest.mark.cosmosEmulator
@pytest.mark.unittest
@pytest.mark.usefixtures("setup")
class TestRequestContext:
    """Tests to verify methods for operations on feed ranges
    """

    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_ID = test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID

    test_operations = []

    #@pytest.mark.parametrize("operation", test_operations)
    # test out all operations and using response hook
    def test_crud_request_context(self, setup):
        keys_expected = ["session_token", "feed_range", "partitionKey"]
        item = {
            'id': 'item' + str(uuid.uuid4()),
            'name': 'sample',
            'key': 'A'
        }
        setup["created_collection"].create_item(item)
        request_context = setup["created_collection"].client_connection.last_response_headers["request_context"]
        for key in keys_expected:
            assert request_context is not None
            assert request_context[key] is not None


if __name__ == '__main__':
    unittest.main()
