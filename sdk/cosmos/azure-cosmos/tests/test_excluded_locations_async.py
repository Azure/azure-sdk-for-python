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
from test_excluded_locations import (CLIENT_ONLY_TEST_DATA, CLIENT_AND_REQUEST_TEST_DATA,
                                     TestDataType, set_test_data_type,
                                     get_test_data_with_expected_output, verify_endpoint)

class MockHandler(logging.Handler):
    def __init__(self):
        super(MockHandler, self).__init__()
        self.messages = []

    def reset(self):
        self.messages = []

    def emit(self, record):
        self.messages.append(record.msg)

# Test configurations
set_test_data_type(TestDataType.ALL_TESTS)
MOCK_HANDLER = MockHandler()
CONFIG = test_config.TestConfig()
HOST = CONFIG.host
KEY = CONFIG.masterKey
DATABASE_ID = CONFIG.TEST_DATABASE_ID
CONTAINER_ID = CONFIG.TEST_SINGLE_PARTITION_PREFIX_PK_CONTAINER_ID
PARTITION_KEY = CONFIG.TEST_CONTAINER_PREFIX_PARTITION_KEY
ITEM_ID = 'doc1'
PARTITION_KEY_VALUES = [f'value{i+1}' for i in range(len(PARTITION_KEY))]
PREFIX_PARTITION_KEY = [PARTITION_KEY_VALUES[0]]
PARTITION_KEY_ITEMS = dict(zip(PARTITION_KEY, PARTITION_KEY_VALUES))
TEST_ITEM = {'id': ITEM_ID}
TEST_ITEM.update(PARTITION_KEY_ITEMS)

L0 = "Default"
L1 = "West US 3"
L2 = "West US"
L3 = "East US 2"

# L0 = "Default"
# L1 = "East US 2"
# L2 = "East US"
# L3 = "West US 2"

ALL_INPUT_TEST_DATA = CLIENT_ONLY_TEST_DATA + CLIENT_AND_REQUEST_TEST_DATA

def read_item_test_data():
    client_only_output_data = [
        [L1],  # 0
        [L2],  # 1
        [L1],  # 2
        [L1],  # 3
    ]
    client_and_request_output_data = [
        [L2],  # 0
        [L2],  # 1
        [L2],  # 2
        [L1],  # 3
        [L1],  # 4
        [L1],  # 5
        [L1],  # 6
        [L1],  # 7
    ]
    return get_test_data_with_expected_output(client_only_output_data, client_and_request_output_data)

def read_all_item_test_data():
    client_only_output_data = [
        [L1, L1],  # 0
        [L2, L2],  # 1
        [L1, L1],  # 2
        [L1, L1],  # 3
    ]
    client_and_request_output_data = [
        [L2, L2],  # 0
        [L2, L2],  # 1
        [L2, L2],  # 2
        [L1, L1],  # 3
        [L1, L1],  # 4
        [L1, L1],  # 5
        [L1, L1],  # 6
        [L1, L1],  # 7
    ]
    return get_test_data_with_expected_output(client_only_output_data, client_and_request_output_data)

def query_items_test_data():
    client_only_output_data = [
        [L1, L1, L1],   #0
        [L2, L2, L2],   #1
        [L1, L1, L1],   #2
        [L1, L1, L1]    #3
    ]
    client_and_request_output_data = [
        [L2, L2, L2],   #0
        [L2, L2, L2],   #1
        [L2, L2, L2],   #2
        [L1, L1, L1],   #3
        [L1, L1, L1],   #4
        [L1, L1, L1],   #5
        [L1, L1, L1],   #6
        [L1, L1, L1],   #7
    ]
    return get_test_data_with_expected_output(client_only_output_data, client_and_request_output_data)

def query_items_change_feed_test_data():
    client_only_output_data = [
        [L1, L1, L1, L1, L1],   #0
        [L2, L2, L2, L2, L2],   #1
        [L1, L1, L1, L1, L1],   #2
        [L1, L1, L1, L1, L1]    #3
    ]
    client_and_request_output_data = [
        [L2, L2, L2, L2, L2],   #0
        [L2, L2, L2, L2, L2],   #1
        [L2, L2, L2, L2, L2],   #2
        [L1, L1, L1, L1, L1],   #3
        [L1, L1, L1, L1, L1],   #4
        [L1, L1, L1, L1, L1],   #5
        [L1, L1, L1, L1, L1],   #6
        [L1, L1, L1, L1, L1],   #7
    ]
    return get_test_data_with_expected_output(client_only_output_data, client_and_request_output_data)

def create_items_test_data():
    client_only_output_data = [
        [L1, L1],   #0
        [L2, L2],   #1
        [L1, L0],   #2
        [L1, L1]    #3
    ]
    client_and_request_output_data = [
        [L2, L2],   #0
        [L2, L2],   #1
        [L2, L2],   #2
        [L1, L0],   #3
        [L1, L0],   #4
        [L1, L1],   #5
        [L1, L1],   #6
        [L1, L1],   #7
    ]
    return get_test_data_with_expected_output(client_only_output_data, client_and_request_output_data)

def patch_item_test_data():
    client_only_output_data = [
        [L1],   #0
        [L2],   #1
        [L0],   #2
        [L1]    #3
    ]
    client_and_request_output_data = [
        [L2],   #0
        [L2],   #1
        [L2],   #2
        [L0],   #3
        [L0],   #4
        [L1],   #5
        [L1],   #6
        [L1],   #7
    ]
    return get_test_data_with_expected_output(client_only_output_data, client_and_request_output_data)

async def create_item_with_excluded_locations(container, body, excluded_locations):
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
    # Waiting some time for the new items to be replicated to other regions
    time.sleep(3)
    yield
    # Code to run after tests
    print("Teardown: This runs after all tests")

async def init_container(client):
    db = client.get_database_client(DATABASE_ID)
    container = db.get_container_client(CONTAINER_ID)
    MOCK_HANDLER.reset()

    return db, container

@pytest.mark.cosmosMultiRegion
@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_and_teardown")
class TestExcludedLocations:
    @pytest.mark.parametrize('test_data', read_item_test_data())
    async def test_read_item(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        # Client setup
        async with CosmosClient(HOST, KEY,
                              preferred_locations=preferred_locations,
                              excluded_locations=client_excluded_locations,
                              multiple_write_locations=True) as client:
            db, container = await init_container(client)

            # API call: read_item
            if request_excluded_locations is None:
                await container.read_item(ITEM_ID, PARTITION_KEY_VALUES)
            else:
                await container.read_item(ITEM_ID, PARTITION_KEY_VALUES, excluded_locations=request_excluded_locations)

            # Verify endpoint locations
            verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)

    @pytest.mark.parametrize('test_data', read_all_item_test_data())
    async def test_read_all_items(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        # Client setup
        async with CosmosClient(HOST, KEY,
                                preferred_locations=preferred_locations,
                                excluded_locations=client_excluded_locations,
                                multiple_write_locations=True) as client:
            db, container = await init_container(client)

            # API call: read_all_items
            if request_excluded_locations is None:
                all_items = [item async for item in container.read_all_items()]
            else:
                all_items = [item async for item in container.read_all_items(excluded_locations=request_excluded_locations)]

            # Verify endpoint locations
            verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)

    @pytest.mark.parametrize('test_data', query_items_test_data())
    async def test_query_items(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        # Client setup
        async with CosmosClient(HOST, KEY,
                                preferred_locations=preferred_locations,
                                excluded_locations=client_excluded_locations,
                                multiple_write_locations=True) as client:
            db, container = await init_container(client)

            # API call: query_items
            query = 'select * from c'
            if request_excluded_locations is None:
                all_items = [item async for item in container.query_items(query, partition_key=PREFIX_PARTITION_KEY)]
            else:
                all_items = [item async for item in container.query_items(query, partition_key=PREFIX_PARTITION_KEY, excluded_locations=request_excluded_locations)]

            # Verify endpoint locations
            verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)

    @pytest.mark.parametrize('test_data', query_items_change_feed_test_data())
    async def test_query_items_change_feed(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data


        # Client setup
        async with CosmosClient(HOST, KEY,
                                preferred_locations=preferred_locations,
                                excluded_locations=client_excluded_locations,
                                multiple_write_locations=True) as client:
            db, container = await init_container(client)
            # API call: query_items_change_feed
            if request_excluded_locations is None:
                all_items = [item async for item in container.query_items_change_feed(start_time="Beginning", partition_key=PREFIX_PARTITION_KEY)]
            else:
                all_items = [item async for item in container.query_items_change_feed(start_time="Beginning", partition_key=PREFIX_PARTITION_KEY, excluded_locations=request_excluded_locations)]

            # Verify endpoint locations
            verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)


    @pytest.mark.parametrize('test_data', create_items_test_data())
    async def test_replace_item(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in [True, False]:
            # Client setup
            async with CosmosClient(HOST, KEY,
                                    preferred_locations=preferred_locations,
                                    excluded_locations=client_excluded_locations,
                                    multiple_write_locations=multiple_write_locations) as client:
                db, container = await init_container(client)

                # API call: replace_item
                if request_excluded_locations is None:
                    await container.replace_item(ITEM_ID, body=TEST_ITEM)
                else:
                    await container.replace_item(ITEM_ID, body=TEST_ITEM, excluded_locations=request_excluded_locations)

                # Verify endpoint locations
                if multiple_write_locations:
                    verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)
                else:
                    verify_endpoint(MOCK_HANDLER.messages, client, expected_locations[:-1] + [L1])

    @pytest.mark.parametrize('test_data', create_items_test_data())
    async def test_upsert_item(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in [True, False]:
            # Client setup
            async with CosmosClient(HOST, KEY,
                                    preferred_locations=preferred_locations,
                                    excluded_locations=client_excluded_locations,
                                    multiple_write_locations=multiple_write_locations) as client:
                db, container = await init_container(client)

                # API call: upsert_item
                body = {'id': f'doc2-{str(uuid.uuid4())}'}
                body.update(PARTITION_KEY_ITEMS)
                if request_excluded_locations is None:
                    await container.upsert_item(body=body)
                else:
                    await container.upsert_item(body=body, excluded_locations=request_excluded_locations)

                # get location from mock_handler
                if multiple_write_locations:
                    verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)
                else:
                    verify_endpoint(MOCK_HANDLER.messages, client, [expected_locations[0], L1])

    @pytest.mark.parametrize('test_data', create_items_test_data())
    async def test_create_item(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in [True, False]:
            # Client setup
            async with CosmosClient(HOST, KEY,
                                    preferred_locations=preferred_locations,
                                    excluded_locations=client_excluded_locations,
                                    multiple_write_locations=multiple_write_locations) as client:
                db, container = await init_container(client)

                # API call: create_item
                body = {'id': f'doc2-{str(uuid.uuid4())}'}
                body.update(PARTITION_KEY_ITEMS)
                await create_item_with_excluded_locations(container, body, request_excluded_locations)

                # get location from mock_handler
                if multiple_write_locations:
                    verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)
                else:
                    verify_endpoint(MOCK_HANDLER.messages, client, [expected_locations[0], L1])

    @pytest.mark.parametrize('test_data', patch_item_test_data())
    async def test_patch_item(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in [True, False]:
            # Client setup
            async with CosmosClient(HOST, KEY,
                                    preferred_locations=preferred_locations,
                                    excluded_locations=client_excluded_locations,
                                    multiple_write_locations=multiple_write_locations) as client:
                db, container = await init_container(client)

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
                if multiple_write_locations:
                    verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)
                else:
                    verify_endpoint(MOCK_HANDLER.messages, client, [L1])

    @pytest.mark.parametrize('test_data', patch_item_test_data())
    async def test_execute_item_batch(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in [True, False]:
            # Client setup
            async with CosmosClient(HOST, KEY,
                                    preferred_locations=preferred_locations,
                                    excluded_locations=client_excluded_locations,
                                    multiple_write_locations=multiple_write_locations) as client:
                db, container = await init_container(client)

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
                if multiple_write_locations:
                    verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)
                else:
                    verify_endpoint(MOCK_HANDLER.messages, client, [L1])

    @pytest.mark.parametrize('test_data', patch_item_test_data())
    async def test_delete_item(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in [True, False]:
            # Client setup
            async with CosmosClient(HOST, KEY,
                                    preferred_locations=preferred_locations,
                                    excluded_locations=client_excluded_locations,
                                    multiple_write_locations=multiple_write_locations) as client:
                db, container = await init_container(client)

                # create before delete
                item_id = f'doc2-{str(uuid.uuid4())}'
                body = {'id': item_id}
                body.update(PARTITION_KEY_ITEMS)
                await create_item_with_excluded_locations(container, body, request_excluded_locations)
                MOCK_HANDLER.reset()

                # API call: delete_item
                if request_excluded_locations is None:
                    await container.delete_item(item_id, PARTITION_KEY_VALUES)
                else:
                    await container.delete_item(item_id, PARTITION_KEY_VALUES, excluded_locations=request_excluded_locations)

                # Verify endpoint locations
                if multiple_write_locations:
                    verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)
                else:
                    verify_endpoint(MOCK_HANDLER.messages, client, [L1])

if __name__ == "__main__":
    unittest.main()
