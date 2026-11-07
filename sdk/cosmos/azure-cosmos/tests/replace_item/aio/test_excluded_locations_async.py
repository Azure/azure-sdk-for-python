# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Async legacy replace exclusion matrix, run through the real Rust replace call.

Uses the shared test database and prefix-key container, like the original.
The original verified each request's region from Python request logs, which
Rust requests never reach, so that final check is skipped after the replace.
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
PARTITION_KEY_ITEMS = dict(zip(PARTITION_KEY, PARTITION_KEY_VALUES))
TEST_ITEM = {'id': ITEM_ID}
TEST_ITEM.update(PARTITION_KEY_ITEMS)

# Same values the original imported from tests/test_excluded_locations.py.
L0 = "Default"
L1 = settings.TestSettings.WRITE_LOCATION
L2 = settings.TestSettings.READ_LOCATION


@pytest.fixture(scope="class", autouse=True)
def _require_configured_regions():
    # Known gap 24: Account information is internal and cannot be returned to Python (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-24). The original discovers regions from the account; this copy needs them configured.
    if not L1 or not L2:
        pytest.skip("environment-gap: excluded-locations tests need WRITE_LOCATION and READ_LOCATION set to account "
                    "regions; Rust cannot discover account regions (known gap 24).")
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
    "driver-gap: the Rust replace_item binding does not report the region of each attempt; "
    "the original read request URLs from a Python logging handler that Rust requests never "
    "reach, and client.client_connection._global_endpoint_manager does not exist on Rust. "
    "The replace call above ran with these exclusions and succeeded. See RUST_PARITY_PUSHBACKS.md#client-serving-region-gap."
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
    @pytest.mark.parametrize('test_data', read_and_write_item_test_data())
    async def test_replace_item_rust(self, test_data):
        # Source: tests/test_excluded_locations_async.py::TestExcludedLocationsAsync.test_replace_item
        # Init test variables
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        # The original repeated this for multiple_write_locations in [True, False]. Rust-backed
        # clients reject that switch ("Closed by design: Rust owns endpoint discovery and
        # multi-write routing", docs/V5/api-review/RUST_PARITY_PUSHBACKS.md), so one pass runs.
        # Client setup
        async with clients.create_data_client_async(
                _backend="rust",
                preferred_locations=preferred_locations,
                excluded_locations=client_excluded_locations) as client:
            db, container = await init_container_async(client)

            # API call: replace_item
            if request_excluded_locations is None:
                await container.replace_item(ITEM_ID, body=TEST_ITEM)
            else:
                await container.replace_item(ITEM_ID, body=TEST_ITEM, excluded_locations=request_excluded_locations)

            # Verify endpoint locations
            pytest.skip(REGION_NOT_OBSERVABLE)
