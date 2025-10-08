# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import logging
import time
import unittest
import uuid
import test_config
import pytest
import pytest_asyncio

from azure.cosmos.aio import CosmosClient
from azure.cosmos.documents import _OperationType as OperationType
from azure.cosmos.http_constants import ResourceType
from test_excluded_locations import (TestDataType, set_test_data_type,
                                     read_item_test_data, write_item_test_data, read_and_write_item_test_data,
                                     verify_endpoint)


class MockHandler(logging.Handler):
    def __init__(self):
        super(MockHandler, self).__init__()
        self.messages = []

    def reset(self):
        self.messages = []

    def emit(self, record):
        self.messages.append(record.msg)

# Test configurations
MOCK_HANDLER = MockHandler()
CONFIG = test_config.TestConfig()
HOST = CONFIG.host
KEY = CONFIG.masterKey
DATABASE_ID = CONFIG.TEST_DATABASE_ID
CONTAINER_ID = CONFIG.TEST_MULTI_PARTITION_PREFIX_PK_CONTAINER_ID
PARTITION_KEY = CONFIG.TEST_CONTAINER_PREFIX_PARTITION_KEY
ITEM_ID = 'doc1'
PARTITION_KEY_VALUES = [f'value{i+1}' for i in range(len(PARTITION_KEY))]
PREFIX_PARTITION_KEY = [PARTITION_KEY_VALUES[0]]
PARTITION_KEY_ITEMS = dict(zip(PARTITION_KEY, PARTITION_KEY_VALUES))
TEST_ITEM = {'id': ITEM_ID}
TEST_ITEM.update(PARTITION_KEY_ITEMS)

set_test_data_type(TestDataType.ALL_TESTS)

async def create_item_with_excluded_locations_async(container, body, excluded_locations):
    if excluded_locations is None:
        await container.create_item(body=body)
    else:
        await container.create_item(body=body, excluded_locations=excluded_locations)

async def init_container_async(client):
    db = client.get_database_client(DATABASE_ID)
    container = db.get_container_client(CONTAINER_ID)
    MOCK_HANDLER.reset()

    return db, container

@pytest_asyncio.fixture(scope="class", autouse=True)
async def setup_and_teardown_async():
    print("Setup: This runs before any tests")
    logger = logging.getLogger("azure")
    logger.addHandler(MOCK_HANDLER)
    logger.setLevel(logging.DEBUG)

    test_client = CosmosClient(HOST, KEY)
    container = test_client.get_database_client(DATABASE_ID).get_container_client(CONTAINER_ID)
    await container.upsert_item(body=TEST_ITEM)
    # Waiting some time for the new items to be replicated to other regions
    time.sleep(3)
    yield
    # Code to run after tests
    print("Teardown: This runs after all tests")

@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosMultiRegion
@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_and_teardown_async")
class TestExcludedLocationsAsync:
    @pytest.mark.parametrize('test_data', read_item_test_data())
    async def test_read_item_async(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        # Client setup
        async with CosmosClient(HOST, KEY,
                              preferred_locations=preferred_locations,
                              excluded_locations=client_excluded_locations,
                              multiple_write_locations=True) as client:
            db, container = await init_container_async(client)

            # API call: read_item
            if request_excluded_locations is None:
                await container.read_item(ITEM_ID, PARTITION_KEY_VALUES)
            else:
                await container.read_item(ITEM_ID, PARTITION_KEY_VALUES, excluded_locations=request_excluded_locations)

            # Verify endpoint locations
            verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)

    @pytest.mark.parametrize('test_data', read_item_test_data())
    async def test_read_all_items_async(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        # Client setup
        async with CosmosClient(HOST, KEY,
                                preferred_locations=preferred_locations,
                                excluded_locations=client_excluded_locations,
                                multiple_write_locations=True) as client:
            db, container = await init_container_async(client)

            # API call: read_all_items
            if request_excluded_locations is None:
                all_items = [item async for item in container.read_all_items()]
            else:
                all_items = [item async for item in container.read_all_items(excluded_locations=request_excluded_locations)]

            # Verify endpoint locations
            verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)

    @pytest.mark.parametrize('test_data', read_item_test_data())
    async def test_query_items_with_partition_key_async(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        # Client setup
        async with CosmosClient(HOST, KEY,
                                preferred_locations=preferred_locations,
                                excluded_locations=client_excluded_locations,
                                multiple_write_locations=True) as client:
            db, container = await init_container_async(client)

            # API call: query_items
            query = 'select * from c'
            if request_excluded_locations is None:
                all_items = [item async for item in container.query_items(query, partition_key=PREFIX_PARTITION_KEY)]
            else:
                all_items = [item async for item in container.query_items(query, partition_key=PREFIX_PARTITION_KEY, excluded_locations=request_excluded_locations)]

            # Verify endpoint locations
            verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)

    @pytest.mark.parametrize('test_data', read_item_test_data())
    async def test_query_items_with_query_plan_async(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        # Client setup
        async with CosmosClient(HOST, KEY,
                                preferred_locations=preferred_locations,
                                excluded_locations=client_excluded_locations,
                                multiple_write_locations=True) as client:
            db, container = await init_container_async(client)

            # API call: query_items
            query = 'Select top 10 value count(c.id) from c'
            if request_excluded_locations is None:
                all_items = [item async for item in container.query_items(query)]
            else:
                all_items = [item async for item in container.query_items(query, excluded_locations=request_excluded_locations)]

            # Verify endpoint locations
            verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)

    @pytest.mark.parametrize('test_data', read_item_test_data())
    async def test_query_items_change_feed_async(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data


        # Client setup
        async with CosmosClient(HOST, KEY,
                                preferred_locations=preferred_locations,
                                excluded_locations=client_excluded_locations,
                                multiple_write_locations=True) as client:
            db, container = await init_container_async(client)
            # API call: query_items_change_feed
            if request_excluded_locations is None:
                all_items = [item async for item in container.query_items_change_feed(start_time="Beginning", partition_key=PREFIX_PARTITION_KEY)]
            else:
                all_items = [item async for item in container.query_items_change_feed(start_time="Beginning", partition_key=PREFIX_PARTITION_KEY, excluded_locations=request_excluded_locations)]

            # Verify endpoint locations
            verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)


    @pytest.mark.parametrize('test_data', read_and_write_item_test_data())
    async def test_replace_item(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in [True, False]:
            # Client setup
            async with CosmosClient(HOST, KEY,
                                    preferred_locations=preferred_locations,
                                    excluded_locations=client_excluded_locations,
                                    multiple_write_locations=multiple_write_locations) as client:
                db, container = await init_container_async(client)

                # API call: replace_item
                if request_excluded_locations is None:
                    await container.replace_item(ITEM_ID, body=TEST_ITEM)
                else:
                    await container.replace_item(ITEM_ID, body=TEST_ITEM, excluded_locations=request_excluded_locations)

                # Verify endpoint locations
                verify_endpoint(MOCK_HANDLER.messages, client, expected_locations, multiple_write_locations)

    @pytest.mark.parametrize('test_data', read_and_write_item_test_data())
    async def test_upsert_item(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in [True, False]:
            # Client setup
            async with CosmosClient(HOST, KEY,
                                    preferred_locations=preferred_locations,
                                    excluded_locations=client_excluded_locations,
                                    multiple_write_locations=multiple_write_locations) as client:
                db, container = await init_container_async(client)

                # API call: upsert_item
                body = {'id': f'doc2-{str(uuid.uuid4())}'}
                body.update(PARTITION_KEY_ITEMS)
                if request_excluded_locations is None:
                    await container.upsert_item(body=body)
                else:
                    await container.upsert_item(body=body, excluded_locations=request_excluded_locations)

                # get location from mock_handler
                verify_endpoint(MOCK_HANDLER.messages, client, expected_locations, multiple_write_locations)

    @pytest.mark.parametrize('test_data', read_and_write_item_test_data())
    async def test_create_item(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in [True, False]:
            # Client setup
            async with CosmosClient(HOST, KEY,
                                    preferred_locations=preferred_locations,
                                    excluded_locations=client_excluded_locations,
                                    multiple_write_locations=multiple_write_locations) as client:
                db, container = await init_container_async(client)

                # API call: create_item
                body = {'id': f'doc2-{str(uuid.uuid4())}'}
                body.update(PARTITION_KEY_ITEMS)
                await create_item_with_excluded_locations_async(container, body, request_excluded_locations)

                # get location from mock_handler
                verify_endpoint(MOCK_HANDLER.messages, client, expected_locations, multiple_write_locations)

    @pytest.mark.parametrize('test_data', read_and_write_item_test_data())
    async def test_patch_item_async(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in [True, False]:
            # Client setup
            async with CosmosClient(HOST, KEY,
                                    preferred_locations=preferred_locations,
                                    excluded_locations=client_excluded_locations,
                                    multiple_write_locations=multiple_write_locations) as client:
                db, container = await init_container_async(client)

                # API call: patch_item
                operations = [
                    {"op": "add", "path": "/test_data", "value": f'Data-{str(uuid.uuid4())}'},
                ]
                if request_excluded_locations is None:
                    await container.patch_item(item=ITEM_ID, partition_key=PARTITION_KEY_VALUES,
                                         patch_operations=operations)
                else:
                    await container.patch_item(item=ITEM_ID, partition_key=PARTITION_KEY_VALUES,
                                         patch_operations=operations,
                                         excluded_locations=request_excluded_locations)

                # get location from mock_handler
                verify_endpoint(MOCK_HANDLER.messages, client, expected_locations, multiple_write_locations)

    @pytest.mark.parametrize('test_data', read_and_write_item_test_data())
    async def test_execute_item_batch_async(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in [True, False]:
            # Client setup
            async with CosmosClient(HOST, KEY,
                                    preferred_locations=preferred_locations,
                                    excluded_locations=client_excluded_locations,
                                    multiple_write_locations=multiple_write_locations) as client:
                db, container = await init_container_async(client)

                # API call: execute_item_batch
                batch_operations = []
                for i in range(3):
                    body = {'id': f'doc2-{str(uuid.uuid4())}'}
                    body.update(PARTITION_KEY_ITEMS)
                    batch_operations.append(("create", (
                        body,
                    )))

                if request_excluded_locations is None:
                    await container.execute_item_batch(batch_operations=batch_operations,
                                                partition_key=PARTITION_KEY_VALUES,)
                else:
                    await container.execute_item_batch(batch_operations=batch_operations,
                                                partition_key=PARTITION_KEY_VALUES,
                                         excluded_locations=request_excluded_locations)

                # get location from mock_handler
                verify_endpoint(MOCK_HANDLER.messages, client, expected_locations, multiple_write_locations)

    @pytest.mark.parametrize('test_data', write_item_test_data())
    async def test_delete_item_async(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in [True, False]:
            # Client setup
            async with CosmosClient(HOST, KEY,
                                    preferred_locations=preferred_locations,
                                    excluded_locations=client_excluded_locations,
                                    multiple_write_locations=multiple_write_locations) as client:
                db, container = await init_container_async(client)

                # create before delete
                item_id = f'doc2-{str(uuid.uuid4())}'
                body = {'id': item_id}
                body.update(PARTITION_KEY_ITEMS)
                await create_item_with_excluded_locations_async(container, body, request_excluded_locations)
                MOCK_HANDLER.reset()

                # API call: delete_item
                if request_excluded_locations is None:
                    await container.delete_item(item_id, PARTITION_KEY_VALUES)
                else:
                    await container.delete_item(item_id, PARTITION_KEY_VALUES, excluded_locations=request_excluded_locations)

                # Verify endpoint locations
                verify_endpoint(MOCK_HANDLER.messages, client, expected_locations, multiple_write_locations,
                                operation_type=OperationType.Delete, resource_type=ResourceType.Document)

if __name__ == "__main__":
    unittest.main()
