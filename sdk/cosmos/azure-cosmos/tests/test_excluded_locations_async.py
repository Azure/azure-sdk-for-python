# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import logging
import unittest
import uuid
import test_config
import pytest
import pytest_asyncio

from azure.cosmos.aio import CosmosClient
from azure.cosmos.partition_key import PartitionKey
from test_excluded_locations import _verify_endpoint, MockHandler, read_item_test_data, write_item_test_data, L1

MOCK_HANDLER = MockHandler()
CONFIG = test_config.TestConfig()
HOST = CONFIG.host
KEY = CONFIG.masterKey
DATABASE_ID = CONFIG.TEST_DATABASE_ID
CONTAINER_ID = CONFIG.TEST_SINGLE_PARTITION_CONTAINER_ID
PARTITION_KEY = CONFIG.TEST_CONTAINER_PARTITION_KEY
ITEM_ID = 'doc1'
ITEM_PK_VALUE = 'pk'
TEST_ITEM = {'id': ITEM_ID, PARTITION_KEY: ITEM_PK_VALUE}

async def _create_item_with_excluded_locations(container, body, excluded_locations):
    if excluded_locations is None:
        await container.create_item(body=body)
    else:
        await container.create_item(body=body, excluded_locations=excluded_locations)

@pytest_asyncio.fixture(scope="class", autouse=True)
async def setup_and_teardown():
    print("Setup: This runs before any tests")
    logger = logging.getLogger("azure")
    logger.addHandler(MOCK_HANDLER)
    logger.setLevel(logging.DEBUG)

    test_client = CosmosClient(HOST, KEY)
    container = test_client.get_database_client(DATABASE_ID).get_container_client(CONTAINER_ID)
    await container.upsert_item(body=TEST_ITEM)

    yield
    await test_client.close()

async def _init_container(preferred_locations, client_excluded_locations, multiple_write_locations = True):
    client = CosmosClient(HOST, KEY,
                          preferred_locations=preferred_locations,
                          excluded_locations=client_excluded_locations,
                          multiple_write_locations=multiple_write_locations)
    db = await client.create_database_if_not_exists(DATABASE_ID)
    container = await db.create_container_if_not_exists(CONTAINER_ID, PartitionKey(path='/' + PARTITION_KEY, kind='Hash'))
    MOCK_HANDLER.reset()

    return client, db, container

@pytest.mark.cosmosMultiRegion
@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_and_teardown")
class TestExcludedLocationsAsync:
    @pytest.mark.parametrize('test_data', read_item_test_data())
    async def test_read_item_async(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        # Client setup
        client, db, container = await _init_container(preferred_locations, client_excluded_locations)

        # API call: read_item
        if request_excluded_locations is None:
            await container.read_item(ITEM_ID, ITEM_PK_VALUE)
        else:
            await container.read_item(ITEM_ID, ITEM_PK_VALUE, excluded_locations=request_excluded_locations)

        # Verify endpoint locations
        _verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)

    @pytest.mark.parametrize('test_data', read_item_test_data())
    async def test_read_all_items_async(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        # Client setup
        client, db, container = await _init_container(preferred_locations, client_excluded_locations)

        # API call: read_all_items
        if request_excluded_locations is None:
            all_items = [item async for item in container.read_all_items()]
        else:
            all_items = [item async for item in container.read_all_items(excluded_locations=request_excluded_locations)]

        # Verify endpoint locations
        _verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)

    @pytest.mark.parametrize('test_data', read_item_test_data())
    async def test_query_items_async(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        # Client setup and create an item
        client, db, container = await _init_container(preferred_locations, client_excluded_locations)

        # API call: query_items
        if request_excluded_locations is None:
            all_items = [item async for item in container.query_items(None)]
        else:
            all_items = [item async for item in container.query_items(None, excluded_locations=request_excluded_locations)]

        # Verify endpoint locations
        _verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)

    @pytest.mark.parametrize('test_data', read_item_test_data())
    async def test_query_items_change_feed_async(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data


        # Client setup and create an item
        client, db, container = await _init_container(preferred_locations, client_excluded_locations)

        # API call: query_items_change_feed
        if request_excluded_locations is None:
            all_items = [item async for item in container.query_items_change_feed(start_time="Beginning")]
        else:
            all_items = [item async for item in container.query_items_change_feed(start_time="Beginning", excluded_locations=request_excluded_locations)]

        # Verify endpoint locations
        _verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)


    @pytest.mark.parametrize('test_data', write_item_test_data())
    async def test_replace_item_async(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in [True, False]:
            # Client setup and create an item
            client, db, container = await _init_container(preferred_locations, client_excluded_locations, multiple_write_locations)

            # API call: replace_item
            if request_excluded_locations is None:
                await container.replace_item(ITEM_ID, body=TEST_ITEM)
            else:
                await container.replace_item(ITEM_ID, body=TEST_ITEM, excluded_locations=request_excluded_locations)

            # Verify endpoint locations
            if multiple_write_locations:
                _verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)
            else:
                _verify_endpoint(MOCK_HANDLER.messages, client, [L1])

    @pytest.mark.parametrize('test_data', write_item_test_data())
    async def test_upsert_item_async(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in [True, False]:
            # Client setup and create an item
            client, db, container = await _init_container(preferred_locations, client_excluded_locations, multiple_write_locations)

            # API call: upsert_item
            body = {'pk': 'pk', 'id': f'doc2-{str(uuid.uuid4())}'}
            if request_excluded_locations is None:
                await container.upsert_item(body=body)
            else:
                await container.upsert_item(body=body, excluded_locations=request_excluded_locations)

            # get location from mock_handler
            if multiple_write_locations:
                _verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)
            else:
                _verify_endpoint(MOCK_HANDLER.messages, client, [L1])

    @pytest.mark.parametrize('test_data', write_item_test_data())
    async def test_create_item_async(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in [True, False]:
            # Client setup and create an item
            client, db, container = await _init_container(preferred_locations, client_excluded_locations, multiple_write_locations)

            # API call: create_item
            body = {'pk': 'pk', 'id': f'doc2-{str(uuid.uuid4())}'}
            await _create_item_with_excluded_locations(container, body, request_excluded_locations)

            # get location from mock_handler
            if multiple_write_locations:
                _verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)
            else:
                _verify_endpoint(MOCK_HANDLER.messages, client, [L1])

    @pytest.mark.parametrize('test_data', write_item_test_data())
    async def test_patch_item_async(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in [True, False]:
            # Client setup and create an item
            client, db, container = await _init_container(preferred_locations, client_excluded_locations,
                                                         multiple_write_locations)

            # API call: patch_item
            operations = [
                {"op": "add", "path": "/test_data", "value": f'Data-{str(uuid.uuid4())}'},
            ]
            if request_excluded_locations is None:
                await container.patch_item(item=ITEM_ID, partition_key=ITEM_PK_VALUE,
                                     patch_operations=operations)
            else:
                await container.patch_item(item=ITEM_ID, partition_key=ITEM_PK_VALUE,
                                     patch_operations=operations,
                                     excluded_locations=request_excluded_locations)

            # get location from mock_handler
            if multiple_write_locations:
                _verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)
            else:
                _verify_endpoint(MOCK_HANDLER.messages, client, [L1])

    @pytest.mark.parametrize('test_data', write_item_test_data())
    async def test_execute_item_batch_async(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in [True, False]:
            # Client setup and create an item
            client, db, container = await _init_container(preferred_locations, client_excluded_locations,
                                                         multiple_write_locations)

            # API call: execute_item_batch
            batch_operations = []
            for i in range(3):
                batch_operations.append(("create", ({"id": f'Doc-{str(uuid.uuid4())}', PARTITION_KEY: ITEM_PK_VALUE},)))

            if request_excluded_locations is None:
                await container.execute_item_batch(batch_operations=batch_operations,
                                            partition_key=ITEM_PK_VALUE,)
            else:
                await container.execute_item_batch(batch_operations=batch_operations,
                                            partition_key=ITEM_PK_VALUE,
                                     excluded_locations=request_excluded_locations)

            # get location from mock_handler
            if multiple_write_locations:
                _verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)
            else:
                _verify_endpoint(MOCK_HANDLER.messages, client, [L1])

    @pytest.mark.parametrize('test_data', write_item_test_data())
    async def test_delete_item_async(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in [True, False]:
            # Client setup
            client, db, container = await _init_container(preferred_locations, client_excluded_locations, multiple_write_locations)

            # create before delete
            item_id = f'doc2-{str(uuid.uuid4())}'
            body = {PARTITION_KEY: ITEM_PK_VALUE, 'id': item_id}
            await _create_item_with_excluded_locations(container, body, request_excluded_locations)
            MOCK_HANDLER.reset()

            # API call: delete_item
            if request_excluded_locations is None:
                await container.delete_item(item_id, ITEM_PK_VALUE)
            else:
                await container.delete_item(item_id, ITEM_PK_VALUE, excluded_locations=request_excluded_locations)

            # Verify endpoint locations
            if multiple_write_locations:
                _verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)
            else:
                _verify_endpoint(MOCK_HANDLER.messages, client, [L1])

if __name__ == "__main__":
    unittest.main()
