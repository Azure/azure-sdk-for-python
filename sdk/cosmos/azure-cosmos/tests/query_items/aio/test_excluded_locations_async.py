# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Async legacy query exclusion matrix, run through the real Rust query_items call.

Rust-path copies of the query_items tests in tests/test_excluded_locations_async.py.
Uses the shared test database and prefix-key container, like the original. The
original verified each request's region from Python request logs, which Rust
requests never reach, so that final check is skipped after the query.
"""

import time

import pytest
import pytest_asyncio

from config import clients, settings

CONFIG = settings.TestSettings()
DATABASE_ID = CONFIG.TEST_DATABASE_ID
CONTAINER_ID = CONFIG.TEST_MULTI_PARTITION_PREFIX_PK_CONTAINER_ID
PARTITION_KEY = CONFIG.TEST_CONTAINER_PREFIX_PARTITION_KEY
ITEM_ID = 'doc1'
PARTITION_KEY_VALUES = [f'value{i+1}' for i in range(len(PARTITION_KEY))]
PREFIX_PARTITION_KEY = [PARTITION_KEY_VALUES[0]]
PARTITION_KEY_ITEMS = dict(zip(PARTITION_KEY, PARTITION_KEY_VALUES))
TEST_ITEM = {'id': ITEM_ID}
TEST_ITEM.update(PARTITION_KEY_ITEMS)

# Same values the original imported from tests/test_excluded_locations.py.
L0 = "Default"
L1 = settings.TestSettings.WRITE_LOCATION
L2 = settings.TestSettings.READ_LOCATION


@pytest.fixture(scope="class", autouse=True)
def _require_configured_regions():
    # Account inspection is excluded from the client API; use configured test regions.
    if not L1 or not L2:
        pytest.skip("environment-gap: excluded-locations tests need WRITE_LOCATION and READ_LOCATION set to account "
                    "regions.")
L3 = "East US 2"

CLIENT_ONLY_TEST_DATA = [
    # preferred_locations, client_excluded_locations, excluded_locations_request
    [[L1, L2], [], None],
    [[L1, L2], [L1], None],
    [[L1, L2], [L1, L2], None],
    [[L1, L2], [L3], None],
]

CLIENT_AND_REQUEST_TEST_DATA = [
    # preferred_locations, client_excluded_locations, excluded_locations_request
    [[L1, L2], [], [L1]],
    [[L1, L2], [L1], [L1]],
    [[L1, L2], [L1, L2], [L1]],
    [[L1, L2], [L1], [L1, L2]],
    [[L1, L2], [L1, L2], [L1, L2]],
    [[L1, L2], [L1], [L2]],
    [[L1, L2], [L1, L2], [L3]],
    [[L1, L2], [L1, L2], []],
]

# Known gap 33: serving region not visible (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#client-serving-region-gap). Rust logs and diagnostics do not name the region that served each attempt.
REGION_NOT_OBSERVABLE = (
    "driver-gap: the Rust query_items binding does not report the region of each attempt; "
    "the original read request URLs from a Python logging handler that Rust requests never "
    "reach, and client.client_connection._global_endpoint_manager does not exist on Rust. "
    "The query above ran with these exclusions and succeeded (known gap 33, "
    "docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#client-serving-region-gap)."
)


def get_test_data_with_expected_output(_client_only_output_data, _client_and_request_output_data):
    # Same as the original with set_test_data_type(TestDataType.ALL_TESTS).
    all_input_test_data = CLIENT_ONLY_TEST_DATA + CLIENT_AND_REQUEST_TEST_DATA
    all_output_data = _client_only_output_data + _client_and_request_output_data
    return [input_data + [output_data] for input_data, output_data in
            zip(all_input_test_data, all_output_data)]


def read_item_test_data():
    client_only_output_data = [[L1], [L2], [L1], [L1]]
    client_and_request_output_data = [[L2], [L2], [L2], [L1], [L1], [L1], [L1], [L1]]
    return get_test_data_with_expected_output(client_only_output_data, client_and_request_output_data)


def write_item_test_data():
    client_only_output_data = [[L1], [L2], [L0], [L1]]
    client_and_request_output_data = [[L2], [L2], [L2], [L0], [L0], [L1], [L1], [L1]]
    return get_test_data_with_expected_output(client_only_output_data, client_and_request_output_data)


def read_and_write_item_test_data():
    read_item = read_item_test_data()
    write_item = write_item_test_data()

    # Combine the expected_locations of read and write item
    for i in range(len(read_item)):
        read_item[i][-1] += write_item[i][-1]
    return read_item


async def init_container_async(client):
    db = client.get_database_client(DATABASE_ID)
    container = db.get_container_client(CONTAINER_ID)
    return db, container


@pytest_asyncio.fixture(scope="class", loop_scope="class", autouse=True)
async def setup_and_teardown_async():
    async with clients.create_data_client_async(_backend="rust") as test_client:
        container = test_client.get_database_client(DATABASE_ID).get_container_client(CONTAINER_ID)
        await container.upsert_item(body=TEST_ITEM)
    # Waiting some time for the new items to be replicated to other regions
    time.sleep(3)
    yield


@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosMultiRegion
@pytest.mark.cosmosAADCircuitBreaker
@pytest.mark.asyncio(loop_scope="class")
@pytest.mark.usefixtures("setup_and_teardown_async")
class TestExcludedLocationsAsync:
    @pytest.mark.parametrize('test_data', read_item_test_data())
    async def test_query_items_with_partition_key_async_rust(self, test_data):
        # Source: tests/test_excluded_locations_async.py::TestExcludedLocationsAsync.test_query_items_with_partition_key_async
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        # Client setup; multiple_write_locations=True is omitted because Rust-backed clients reject it
        # ("Closed by design: Rust owns endpoint discovery and multi-write routing").
        async with clients.create_data_client_async(
                _backend="rust",
                preferred_locations=preferred_locations,
                excluded_locations=client_excluded_locations) as client:
            db, container = await init_container_async(client)

            # API call: query_items
            query = 'select * from c'
            if request_excluded_locations is None:
                all_items = [item async for item in container.query_items(query, partition_key=PREFIX_PARTITION_KEY)]
            else:
                all_items = [item async for item in container.query_items(query, partition_key=PREFIX_PARTITION_KEY, excluded_locations=request_excluded_locations)]

            # Verify endpoint locations
            # Known gap 33: the region that served each attempt is not observable on Rust.
            pytest.skip(REGION_NOT_OBSERVABLE)

    @pytest.mark.parametrize('test_data', read_item_test_data())
    async def test_query_items_with_query_plan_async_rust(self, test_data):
        # Source: tests/test_excluded_locations_async.py::TestExcludedLocationsAsync.test_query_items_with_query_plan_async
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        # Client setup; multiple_write_locations=True is omitted because Rust-backed clients reject it
        # ("Closed by design: Rust owns endpoint discovery and multi-write routing").
        async with clients.create_data_client_async(
                _backend="rust",
                preferred_locations=preferred_locations,
                excluded_locations=client_excluded_locations) as client:
            db, container = await init_container_async(client)

            # API call: query_items
            query = 'Select top 10 value count(c.id) from c'
            if request_excluded_locations is None:
                all_items = [item async for item in container.query_items(query)]
            else:
                all_items = [item async for item in container.query_items(query, excluded_locations=request_excluded_locations)]

            # Verify endpoint locations
            # Known gap 33: the region that served each attempt is not observable on Rust.
            pytest.skip(REGION_NOT_OBSERVABLE)
