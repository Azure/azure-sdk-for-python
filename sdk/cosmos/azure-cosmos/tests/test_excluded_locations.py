# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import logging
import re
import unittest
import uuid
import test_config
import pytest
import time

from azure.cosmos import CosmosClient
from azure.cosmos.documents import _OperationType as OperationType
from azure.cosmos.http_constants import ResourceType


class MockHandler(logging.Handler):
    def __init__(self):
        super(MockHandler, self).__init__()
        self.messages = []

    def reset(self):
        self.messages = []

    def emit(self, record):
        self.messages.append(record.msg)

# Test configurations
class TestDataType:
    CLIENT_ONLY_TESTS = 'clientOnlyTests'
    CLIENT_AND_REQUEST_TESTS = 'clientAndRequestTests'
    ALL_TESTS = 'allTests'

TEST_DATA_TYPE = TestDataType.ALL_TESTS

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

L0 = "Default"
L1 = test_config.TestConfig.WRITE_LOCATION
L2 = test_config.TestConfig.READ_LOCATION
L3 = "East US 2"

CLIENT_ONLY_TEST_DATA = [
    # preferred_locations, client_excluded_locations, excluded_locations_request
    # 0. No excluded location
    [[L1, L2], [], None],
    # 1. Single excluded location
    [[L1, L2], [L1], None],
    # 2. Exclude all locations
    [[L1, L2], [L1, L2], None],
    # 3. Exclude a location not in preferred locations
    [[L1, L2], [L3], None],
]

CLIENT_AND_REQUEST_TEST_DATA = [
    # preferred_locations, client_excluded_locations, excluded_locations_request
    # 0. No client excluded locations + a request excluded location
    [[L1, L2], [], [L1]],
    # 1. The same client and request excluded location
    [[L1, L2], [L1], [L1]],
    # 2. Less request excluded locations
    [[L1, L2], [L1, L2], [L1]],
    # 3. More request excluded locations
    [[L1, L2], [L1], [L1, L2]],
    # 4. All locations were excluded
    [[L1, L2], [L1, L2], [L1, L2]],
    # 5. No common excluded locations
    [[L1, L2], [L1], [L2]],
    # 6. Request excluded location not in preferred locations
    [[L1, L2], [L1, L2], [L3]],
    # 7. Empty excluded locations, remove all client level excluded locations
    [[L1, L2], [L1, L2], []],
]

def set_test_data_type(test_data_type):
    global TEST_DATA_TYPE
    TEST_DATA_TYPE = test_data_type

def get_test_data_with_expected_output(_client_only_output_data, _client_and_request_output_data):
    if TEST_DATA_TYPE == TestDataType.CLIENT_ONLY_TESTS:
        all_input_test_data = CLIENT_ONLY_TEST_DATA
        all_output_data = _client_only_output_data
    elif TEST_DATA_TYPE == TestDataType.CLIENT_AND_REQUEST_TESTS:
        all_input_test_data = CLIENT_AND_REQUEST_TEST_DATA
        all_output_data = _client_and_request_output_data
    else:
        all_input_test_data = CLIENT_ONLY_TEST_DATA + CLIENT_AND_REQUEST_TEST_DATA
        all_output_data = _client_only_output_data + _client_and_request_output_data

    all_test_data = [input_data + [output_data] for input_data, output_data in
                     zip(all_input_test_data, all_output_data)]
    return all_test_data

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


def write_item_test_data():
    client_only_output_data = [
        [L1],  # 0
        [L2],  # 1
        [L0],  # 2
        [L1],  # 3
    ]
    client_and_request_output_data = [
        [L2],  # 0
        [L2],  # 1
        [L2],  # 2
        [L0],  # 3
        [L0],  # 4
        [L1],  # 5
        [L1],  # 6
        [L1],  # 7
    ]
    return get_test_data_with_expected_output(client_only_output_data, client_and_request_output_data)

def read_and_write_item_test_data():
    read_item = read_item_test_data()
    write_item = write_item_test_data()

    # Combine the expected_locations of read and write item
    for i in range(len(read_item)):
        read_item[i][-1] += write_item[i][-1]
    return read_item

def create_item_with_excluded_locations(container, body, excluded_locations):
    if excluded_locations is None:
        container.create_item(body=body)
    else:
        container.create_item(body=body, excluded_locations=excluded_locations)

def init_container(preferred_locations, client_excluded_locations, multiple_write_locations=True):
    client = CosmosClient(HOST, KEY,
                          preferred_locations=preferred_locations,
                          excluded_locations=client_excluded_locations,
                          multiple_write_locations=multiple_write_locations)
    db = client.get_database_client(DATABASE_ID)
    container = db.get_container_client(CONTAINER_ID)
    MOCK_HANDLER.reset()

    return client, db, container

def verify_endpoint(messages, client, expected_locations, multiple_write_locations=True,
                    operation_type=None, resource_type=None):
    if not multiple_write_locations:
        expected_locations[-1] = L1

    # get mapping for locations
    location_mapping = (client.client_connection._global_endpoint_manager.
                        location_cache.account_locations_by_write_endpoints)
    default_endpoint = (client.client_connection._global_endpoint_manager.
                        location_cache.default_regional_routing_context.get_primary())

    # get Request URL
    req_urls = [url.replace("Request URL: '", "") for url in messages if 'Request URL:' in url]

    # get location
    actual_locations = set()
    for req_url in req_urls:
        # Requests that require session tokens to be set can now potentially have a request made to fetch partition key ranges beforehand.
        # We only care about the request that is made to the actual item endpoint.
        req_resource_type = re.search(r"'x-ms-thinclient-proxy-resource-type':\s*'([^']+)'", req_url)
        resource_value = req_resource_type.group(1)
        # ignore health check requests
        if resource_value == ResourceType.DatabaseAccount:
            continue
        if operation_type and resource_type:
            req_operation_type = re.search(r"'x-ms-thinclient-proxy-operation-type':\s*'([^']+)'", req_url)
            operation_value = req_operation_type.group(1)
            if resource_type != resource_value or operation_type != operation_value:
                continue
        if req_url.startswith(default_endpoint):
            actual_locations.add(L0)
        else:
            for endpoint in location_mapping:
                if req_url.startswith(endpoint):
                    location = location_mapping[endpoint]
                    actual_locations.add(location)
                    break

    assert actual_locations == set(expected_locations)

@pytest.fixture(scope="class", autouse=True)
def setup_and_teardown():
    print("Setup: This runs before any tests")
    logger = logging.getLogger("azure")
    logger.addHandler(MOCK_HANDLER)
    logger.setLevel(logging.DEBUG)

    container = CosmosClient(HOST, KEY).get_database_client(DATABASE_ID).get_container_client(CONTAINER_ID)
    container.upsert_item(body=TEST_ITEM)
    # Waiting some time for the new items to be replicated to other regions
    time.sleep(3)
    yield
    # Code to run after tests
    print("Teardown: This runs after all tests")

@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosMultiRegion
class TestExcludedLocations:
    @pytest.mark.parametrize('test_data', read_item_test_data())
    def test_read_item(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        # Client setup
        client, db, container = init_container(preferred_locations, client_excluded_locations)

        # API call: read_item
        if request_excluded_locations is None:
            container.read_item(item=ITEM_ID, partition_key=PARTITION_KEY_VALUES)
        else:
            container.read_item(item=ITEM_ID, partition_key=PARTITION_KEY_VALUES, excluded_locations=request_excluded_locations)

        # Verify endpoint locations
        verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)

    @pytest.mark.parametrize('test_data', read_item_test_data())
    def test_read_all_items(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        # Client setup
        client, db, container = init_container(preferred_locations, client_excluded_locations)

        # API call: read_all_items
        if request_excluded_locations is None:
            list(container.read_all_items())
        else:
            list(container.read_all_items(excluded_locations=request_excluded_locations))

        # Verify endpoint locations
        verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)

    @pytest.mark.parametrize('test_data', read_item_test_data())
    def test_query_items_with_partition_key(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        # Client setup and create an item
        client, db, container = init_container(preferred_locations, client_excluded_locations)

        # API call: query_items
        query = 'select * from c'
        if request_excluded_locations is None:
            list(container.query_items(query, partition_key=PREFIX_PARTITION_KEY))
        else:
            list(container.query_items(query, partition_key=PREFIX_PARTITION_KEY, excluded_locations=request_excluded_locations))

        # Verify endpoint locations
        verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)

    @pytest.mark.parametrize('test_data', read_item_test_data())
    def test_query_items_with_query_plan(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        # Client setup and create an item
        client, db, container = init_container(preferred_locations, client_excluded_locations)

        # API call: query_items
        query = 'Select top 10 value count(c.id) from c'
        if request_excluded_locations is None:
            list(container.query_items(query, enable_cross_partition_query=True))
            # list(container.query_items(query))
        else:
            list(container.query_items(query, enable_cross_partition_query=True, excluded_locations=request_excluded_locations))

        # Verify endpoint locations
        verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)

    @pytest.mark.parametrize('test_data', read_item_test_data())
    def test_query_items_change_feed(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        # Client setup and create an item
        client, db, container = init_container(preferred_locations, client_excluded_locations)

        # API call: query_items_change_feed
        if request_excluded_locations is None:
            items = list(container.query_items_change_feed(start_time="Beginning", partition_key=PREFIX_PARTITION_KEY))
        else:
            items = list(container.query_items_change_feed(start_time="Beginning", partition_key=PREFIX_PARTITION_KEY, excluded_locations=request_excluded_locations))

        # Verify endpoint locations
        verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)

    @pytest.mark.parametrize('test_data', read_and_write_item_test_data())
    def test_replace_item(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in [True, False]:
            # Client setup and create an item
            client, db, container = init_container(preferred_locations, client_excluded_locations, multiple_write_locations)

            # API call: replace_item
            if request_excluded_locations is None:
                container.replace_item(ITEM_ID, body=TEST_ITEM)
            else:
                container.replace_item(ITEM_ID, body=TEST_ITEM, excluded_locations=request_excluded_locations)

            # Verify endpoint locations
            verify_endpoint(MOCK_HANDLER.messages, client, expected_locations, multiple_write_locations)

    @pytest.mark.parametrize('test_data', read_and_write_item_test_data())
    def test_upsert_item(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in [True, False]:
            # Client setup and create an item
            client, db, container = init_container(preferred_locations, client_excluded_locations, multiple_write_locations)

            # API call: upsert_item
            body = {'id': f'doc2-{str(uuid.uuid4())}'}
            body.update(PARTITION_KEY_ITEMS)
            if request_excluded_locations is None:
                container.upsert_item(body=body)
            else:
                container.upsert_item(body=body, excluded_locations=request_excluded_locations)

            # get location from mock_handler
            verify_endpoint(MOCK_HANDLER.messages, client, expected_locations, multiple_write_locations)

    @pytest.mark.parametrize('test_data', read_and_write_item_test_data())
    def test_create_item(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in [True, False]:
            # Client setup and create an item
            client, db, container = init_container(preferred_locations, client_excluded_locations, multiple_write_locations)

            # API call: create_item
            body = {'id': f'doc2-{str(uuid.uuid4())}'}
            body.update(PARTITION_KEY_ITEMS)
            create_item_with_excluded_locations(container, body, request_excluded_locations)

            # Single write
            verify_endpoint(MOCK_HANDLER.messages, client, expected_locations, multiple_write_locations)

    @pytest.mark.parametrize('test_data', read_and_write_item_test_data())
    def test_patch_item(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in [True, False]:
            # Client setup and create an item
            client, db, container = init_container(preferred_locations, client_excluded_locations,
                                                   multiple_write_locations)

            # API call: patch_item
            operations = [
                {"op": "add", "path": "/test_data", "value": f'Data-{str(uuid.uuid4())}'},
            ]
            if request_excluded_locations is None:
                container.patch_item(item=ITEM_ID, partition_key=PARTITION_KEY_VALUES,
                                     patch_operations=operations)
            else:
                container.patch_item(item=ITEM_ID, partition_key=PARTITION_KEY_VALUES,
                                     patch_operations=operations,
                                     excluded_locations=request_excluded_locations)

            # get location from mock_handler
            verify_endpoint(MOCK_HANDLER.messages, client, expected_locations, multiple_write_locations)

    @pytest.mark.parametrize('test_data', read_and_write_item_test_data())
    def test_execute_item_batch(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in [True, False]:
            # Client setup and create an item
            client, db, container = init_container(preferred_locations, client_excluded_locations,
                                                   multiple_write_locations)

            # API call: execute_item_batch
            batch_operations = []
            for i in range(3):
                body = {'id': f'doc2-{str(uuid.uuid4())}'}
                body.update(PARTITION_KEY_ITEMS)
                batch_operations.append(("create", (
                    body,
                )))

            if request_excluded_locations is None:
                container.execute_item_batch(batch_operations=batch_operations,
                                            partition_key=PARTITION_KEY_VALUES,)
            else:
                container.execute_item_batch(batch_operations=batch_operations,
                                            partition_key=PARTITION_KEY_VALUES,
                                     excluded_locations=request_excluded_locations)

            # get location from mock_handler
            verify_endpoint(MOCK_HANDLER.messages, client, expected_locations, multiple_write_locations)

    @pytest.mark.parametrize('test_data', write_item_test_data())
    def test_delete_item(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in [True, False]:
            # Client setup
            client, db, container = init_container(preferred_locations, client_excluded_locations, multiple_write_locations)

            # create before delete
            item_id = f'doc2-{str(uuid.uuid4())}'
            body = {'id': item_id}
            body.update(PARTITION_KEY_ITEMS)
            create_item_with_excluded_locations(container, body, request_excluded_locations)
            MOCK_HANDLER.reset()

            # API call: delete_item
            container.upsert_item(body)
            if request_excluded_locations is None:
                container.delete_item(item_id, PARTITION_KEY_VALUES)
            else:
                container.delete_item(item_id, PARTITION_KEY_VALUES, excluded_locations=request_excluded_locations)

            # Verify endpoint locations
            verify_endpoint(MOCK_HANDLER.messages, client, expected_locations, multiple_write_locations,
                            operation_type=OperationType.Delete, resource_type=ResourceType.Document)

if __name__ == "__main__":
    unittest.main()
