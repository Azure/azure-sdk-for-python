# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import logging
import unittest
import uuid
import test_config
import pytest

import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos.partition_key import PartitionKey
from azure.cosmos.exceptions import CosmosResourceNotFoundError


class MockHandler(logging.Handler):
    def __init__(self):
        super(MockHandler, self).__init__()
        self.messages = []

    def reset(self):
        self.messages = []

    def emit(self, record):
        self.messages.append(record.msg)

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

L0 = "Default"
L1 = "West US 3"
L2 = "West US"
L3 = "East US 2"

# L0 = "Default"
# L1 = "East US 2"
# L2 = "East US"
# L3 = "West US 2"

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
    # 7. Empty excluded locations, remove all client excluded locations
    [[L1, L2], [L1, L2], []],
]

ALL_INPUT_TEST_DATA = CLIENT_ONLY_TEST_DATA + CLIENT_AND_REQUEST_TEST_DATA
# ALL_INPUT_TEST_DATA = CLIENT_ONLY_TEST_DATA
# ALL_INPUT_TEST_DATA = CLIENT_AND_REQUEST_TEST_DATA

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
    all_output_test_data = client_only_output_data + client_and_request_output_data

    all_test_data = [input_data + [output_data] for input_data, output_data in zip(ALL_INPUT_TEST_DATA, all_output_test_data)]
    return all_test_data

def query_items_change_feed_test_data():
    client_only_output_data = [
        [L1, L1, L1, L1],   #0
        [L2, L2, L2, L2],   #1
        [L1, L1, L1, L1],   #2
        [L1, L1, L1, L1]    #3
    ]
    client_and_request_output_data = [
        [L1, L1, L2, L2],   #0
        [L2, L2, L2, L2],   #1
        [L1, L1, L2, L2],   #2
        [L2, L2, L1, L1],   #3
        [L1, L1, L1, L1],   #4
        [L2, L2, L1, L1],   #5
        [L1, L1, L1, L1],   #6
        [L1, L1, L1, L1],   #7
    ]
    all_output_test_data = client_only_output_data + client_and_request_output_data

    all_test_data = [input_data + [output_data] for input_data, output_data in zip(ALL_INPUT_TEST_DATA, all_output_test_data)]
    return all_test_data

def replace_item_test_data():
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
    all_output_test_data = client_only_output_data + client_and_request_output_data

    all_test_data = [input_data + [output_data] for input_data, output_data in zip(ALL_INPUT_TEST_DATA, all_output_test_data)]
    return all_test_data

def patch_item_test_data():
    client_only_output_data = [
        [L1],   #0
        [L2],   #1
        [L0],   #3
        [L1]    #4
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
    all_output_test_data = client_only_output_data + client_and_request_output_data

    all_test_data = [input_data + [output_data] for input_data, output_data in zip(ALL_INPUT_TEST_DATA, all_output_test_data)]
    return all_test_data

def _create_item_with_excluded_locations(container, body, excluded_locations):
    if excluded_locations is None:
        container.create_item(body=body)
    else:
        container.create_item(body=body, excluded_locations=excluded_locations)

@pytest.fixture(scope="class", autouse=True)
def setup_and_teardown():
    print("Setup: This runs before any tests")
    logger = logging.getLogger("azure")
    logger.addHandler(MOCK_HANDLER)
    logger.setLevel(logging.DEBUG)

    container = cosmos_client.CosmosClient(HOST, KEY).get_database_client(DATABASE_ID).get_container_client(CONTAINER_ID)
    container.upsert_item(body=TEST_ITEM)

    yield
    # Code to run after tests
    print("Teardown: This runs after all tests")

def _init_container(preferred_locations, client_excluded_locations, multiple_write_locations = True):
    client = cosmos_client.CosmosClient(HOST, KEY,
                                      preferred_locations=preferred_locations,
                                      excluded_locations=client_excluded_locations,
                                      multiple_write_locations=multiple_write_locations)
    db = client.get_database_client(DATABASE_ID)
    container = db.get_container_client(CONTAINER_ID)
    MOCK_HANDLER.reset()

    return client, db, container

def _verify_endpoint(messages, client, expected_locations):
    # get mapping for locations
    location_mapping = (client.client_connection._global_endpoint_manager.
                        location_cache.account_locations_by_write_regional_routing_context)
    default_endpoint = (client.client_connection._global_endpoint_manager.
                        location_cache.default_regional_routing_context.get_primary())

    # get Request URL
    req_urls = [url.replace("Request URL: '", "") for url in messages if 'Request URL:' in url]

    # get location
    actual_locations = []
    for req_url in req_urls:
        if req_url.startswith(default_endpoint):
            actual_locations.append(L0)
        else:
            for endpoint in location_mapping:
                if req_url.startswith(endpoint):
                    location = location_mapping[endpoint]
                    actual_locations.append(location)
                    break

    assert actual_locations == expected_locations

@pytest.mark.cosmosMultiRegion
class TestExcludedLocations:
    @pytest.mark.parametrize('test_data', read_item_test_data())
    def test_read_item(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        # Client setup
        client, db, container = _init_container(preferred_locations, client_excluded_locations)

        # API call: read_item
        if request_excluded_locations is None:
            container.read_item(ITEM_ID, ITEM_PK_VALUE)
        else:
            container.read_item(ITEM_ID, ITEM_PK_VALUE, excluded_locations=request_excluded_locations)

        # Verify endpoint locations
        _verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)

    @pytest.mark.parametrize('test_data', read_item_test_data())
    def test_read_all_items(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        # Client setup
        client, db, container = _init_container(preferred_locations, client_excluded_locations)

        # API call: read_all_items
        if request_excluded_locations is None:
            list(container.read_all_items())
        else:
            list(container.read_all_items(excluded_locations=request_excluded_locations))

        # Verify endpoint locations
        _verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)

    @pytest.mark.parametrize('test_data', read_item_test_data())
    def test_query_items(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        # Client setup and create an item
        client, db, container = _init_container(preferred_locations, client_excluded_locations)

        # API call: query_items
        if request_excluded_locations is None:
            list(container.query_items(None))
        else:
            list(container.query_items(None, excluded_locations=request_excluded_locations))

        # Verify endpoint locations
        _verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)

    @pytest.mark.parametrize('test_data', query_items_change_feed_test_data())
    def test_query_items_change_feed(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data


        # Client setup and create an item
        client, db, container = _init_container(preferred_locations, client_excluded_locations)

        # API call: query_items_change_feed
        if request_excluded_locations is None:
            items = list(container.query_items_change_feed(start_time="Beginning"))
        else:
            items = list(container.query_items_change_feed(start_time="Beginning", excluded_locations=request_excluded_locations))

        # Verify endpoint locations
        _verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)


    @pytest.mark.parametrize('test_data', replace_item_test_data())
    def test_replace_item(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in [True, False]:
            # Client setup and create an item
            client, db, container = _init_container(preferred_locations, client_excluded_locations, multiple_write_locations)

            # API call: replace_item
            if request_excluded_locations is None:
                container.replace_item(ITEM_ID, body=TEST_ITEM)
            else:
                container.replace_item(ITEM_ID, body=TEST_ITEM, excluded_locations=request_excluded_locations)

            # Verify endpoint locations
            if multiple_write_locations:
                _verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)
            else:
                _verify_endpoint(MOCK_HANDLER.messages, client, [expected_locations[0], L1])

    @pytest.mark.parametrize('test_data', replace_item_test_data())
    def test_upsert_item(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in [True, False]:
            # Client setup and create an item
            client, db, container = _init_container(preferred_locations, client_excluded_locations, multiple_write_locations)

            # API call: upsert_item
            body = {'pk': 'pk', 'id': f'doc2-{str(uuid.uuid4())}'}
            if request_excluded_locations is None:
                container.upsert_item(body=body)
            else:
                container.upsert_item(body=body, excluded_locations=request_excluded_locations)

            # get location from mock_handler
            if multiple_write_locations:
                _verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)
            else:
                _verify_endpoint(MOCK_HANDLER.messages, client, [expected_locations[0], L1])

    @pytest.mark.parametrize('test_data', replace_item_test_data())
    def test_create_item(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in [True, False]:
            # Client setup and create an item
            client, db, container = _init_container(preferred_locations, client_excluded_locations, multiple_write_locations)

            # API call: create_item
            body = {'pk': 'pk', 'id': f'doc2-{str(uuid.uuid4())}'}
            _create_item_with_excluded_locations(container, body, request_excluded_locations)

            # get location from mock_handler
            if multiple_write_locations:
                _verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)
            else:
                _verify_endpoint(MOCK_HANDLER.messages, client, [expected_locations[0], L1])

    @pytest.mark.parametrize('test_data', patch_item_test_data())
    def test_patch_item(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in [True, False]:
            # Client setup and create an item
            client, db, container = _init_container(preferred_locations, client_excluded_locations,
                                                         multiple_write_locations)

            # API call: patch_item
            operations = [
                {"op": "add", "path": "/test_data", "value": f'Data-{str(uuid.uuid4())}'},
            ]
            if request_excluded_locations is None:
                container.patch_item(item=ITEM_ID, partition_key=ITEM_PK_VALUE,
                                     patch_operations=operations)
            else:
                container.patch_item(item=ITEM_ID, partition_key=ITEM_PK_VALUE,
                                     patch_operations=operations,
                                     excluded_locations=request_excluded_locations)

            # get location from mock_handler
            if multiple_write_locations:
                _verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)
            else:
                _verify_endpoint(MOCK_HANDLER.messages, client, [L1])

    @pytest.mark.parametrize('test_data', patch_item_test_data())
    def test_execute_item_batch(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in [True, False]:
            # Client setup and create an item
            client, db, container = _init_container(preferred_locations, client_excluded_locations,
                                                         multiple_write_locations)

            # API call: execute_item_batch
            batch_operations = []
            for i in range(3):
                batch_operations.append(("create", ({"id": f'Doc-{str(uuid.uuid4())}', PARTITION_KEY: ITEM_PK_VALUE},)))

            if request_excluded_locations is None:
                container.execute_item_batch(batch_operations=batch_operations,
                                            partition_key=ITEM_PK_VALUE,)
            else:
                container.execute_item_batch(batch_operations=batch_operations,
                                            partition_key=ITEM_PK_VALUE,
                                     excluded_locations=request_excluded_locations)

            # get location from mock_handler
            if multiple_write_locations:
                _verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)
            else:
                _verify_endpoint(MOCK_HANDLER.messages, client, [L1])

    @pytest.mark.parametrize('test_data', patch_item_test_data())
    def test_delete_item(self, test_data):
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in [True, False]:
            # Client setup
            client, db, container = _init_container(preferred_locations, client_excluded_locations, multiple_write_locations)

            # create before delete
            item_id = f'doc2-{str(uuid.uuid4())}'
            body = {PARTITION_KEY: ITEM_PK_VALUE, 'id': item_id}
            _create_item_with_excluded_locations(container, body, request_excluded_locations)
            MOCK_HANDLER.reset()

            # API call: delete_item
            if request_excluded_locations is None:
                container.delete_item(item_id, ITEM_PK_VALUE)
            else:
                container.delete_item(item_id, ITEM_PK_VALUE, excluded_locations=request_excluded_locations)

            # Verify endpoint locations
            if multiple_write_locations:
                _verify_endpoint(MOCK_HANDLER.messages, client, expected_locations)
            else:
                _verify_endpoint(MOCK_HANDLER.messages, client, [L1])

if __name__ == "__main__":
    unittest.main()
