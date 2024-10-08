# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest

import azure.cosmos.cosmos_client as cosmos_client
import test_config

@pytest.fixture(scope="class")
def setup():
    if (TestRequestContext.masterKey == '[YOUR_KEY_HERE]' or
            TestRequestContext.host == '[YOUR_ENDPOINT_HERE]'):
        raise Exception(
            "You must specify your Azure Cosmos account values for "
            "'masterKey' and 'host' at the top of this class to run the "
            "tests.")
    test_client = cosmos_client.CosmosClient(TestRequestContext.host, test_config.TestConfig.masterKey),
    created_db = test_client[0].get_database_client(TestRequestContext.TEST_DATABASE_ID)
    return {
        "created_db": created_db,
        "created_collection": created_db.get_container_client(TestRequestContext.TEST_CONTAINER_ID)
    }

def validate_request_context(collection, with_partition_key=True):
    request_context = collection.client_connection.last_response_headers["request_context"]
    keys_expected = ["session_token"]
    if with_partition_key:
        keys_expected.append("feed_range")
    assert request_context is not None
    for key in keys_expected:
        assert request_context[key] is not None

def createItem(id = 'item' + str(uuid.uuid4()), pk='A', name='sample'):
    item = {
        'id': id,
        'name': name,
        'pk': pk
    }
    return item

@pytest.mark.cosmosEmulator
@pytest.mark.unittest
@pytest.mark.usefixtures("setup")
class TestRequestContext:
    """Tests to verify request context gets populated correctly
    """

    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_ID = test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID

    # test out all operations
    def test_crud_request_context(self, setup):
        item = createItem()
        setup["created_collection"].create_item(item)
        validate_request_context(setup["created_collection"])

        setup["created_collection"].read_item(item['id'], item['pk'])
        validate_request_context(setup["created_collection"])

        new_item = createItem(item['id'], name='sample_replaced')
        setup["created_collection"].replace_item(item['id'], new_item)
        validate_request_context(setup["created_collection"])
        operations = [
            {"op": "add", "path": "/favorite_color", "value": "red"},
            {"op": "replace", "path": "/name", "value": 14},
        ]
        setup["created_collection"].patch_item(item['id'], item['pk'], operations)
        validate_request_context(setup["created_collection"], False)

        setup["created_collection"].read_all_items()
        validate_request_context(setup["created_collection"], False)

        setup["created_collection"].upsert_item(createItem())
        validate_request_context(setup["created_collection"])

        setup["created_collection"].query_items_change_feed()
        validate_request_context(setup["created_collection"], False)

        # with partition key
        setup["created_collection"].query_items("SELECT * FROM c WHERE c.id = @id", parameters=[dict(name="@id", value=item['id'])], partition_key=item['pk'])
        validate_request_context(setup["created_collection"])

        # without partition key
        setup["created_collection"].query_items("SELECT * FROM c WHERE c.id = @id", parameters=[dict(name="@id", value=item['id'])])
        validate_request_context(setup["created_collection"], False)

        setup["created_collection"].read_all_items()
        validate_request_context(setup["created_collection"], False)

        setup["created_collection"].delete_item(item['id'], item['pk'])
        validate_request_context(setup["created_collection"])

if __name__ == '__main__':
    unittest.main()
