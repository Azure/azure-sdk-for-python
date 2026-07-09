# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Async ``test_create_item`` excluded-locations routing test against
the ``_backend="rust"`` path. Async mirror of the sync sibling.

The 12-row test data table is duplicated between sync and aio copies on
purpose: a cross-folder import would couple two independent migration
units together. The class name and method name match the source at
``tests/test_excluded_locations_async.py`` so test IDs differ only by
path.

This test runs against a live multi-region account; it is gated by
``cosmosMultiRegion`` / ``cosmosCircuitBreaker`` markers.
"""
import asyncio
import logging
import os
import re
import uuid

import pytest
import pytest_asyncio

from azure.cosmos.aio import CosmosClient
from azure.cosmos.http_constants import ResourceType


# ---------------------------------------------------------------------------
# Account configuration (overridable via environment).
# ---------------------------------------------------------------------------
HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)
DATABASE_ID = os.environ.get("LEGACY_EXCLUDED_LOCATIONS_DATABASE_ID", "PythonSDKTestDatabase")
CONTAINER_ID = os.environ.get("LEGACY_EXCLUDED_LOCATIONS_CONTAINER_ID", "MultiPartitionPrefixPKTestContainer")

PARTITION_KEY = ["state", "city", "zipcode"]
PARTITION_KEY_VALUES = [f"value{i+1}" for i in range(len(PARTITION_KEY))]
PARTITION_KEY_ITEMS = dict(zip(PARTITION_KEY, PARTITION_KEY_VALUES))
ITEM_ID = "doc1"
TEST_ITEM = {"id": ITEM_ID, **PARTITION_KEY_ITEMS}

# Region labels used by the test data table.
DEFAULT_LOCATION = "Default"
WRITE_LOCATION = os.environ.get("LEGACY_WRITE_LOCATION", "West US")
READ_LOCATION = os.environ.get("LEGACY_READ_LOCATION", "East US")
THIRD_LOCATION = "East US 2"


# Same shape as the sync sibling -- see its docstring for the column
# meaning and the row-by-row commentary.
CREATE_ITEM_TEST_DATA = [
    ([WRITE_LOCATION, READ_LOCATION], [],                              None,                              [WRITE_LOCATION, WRITE_LOCATION]),    # 0
    ([WRITE_LOCATION, READ_LOCATION], [WRITE_LOCATION],                None,                              [READ_LOCATION, READ_LOCATION]),      # 1
    ([WRITE_LOCATION, READ_LOCATION], [WRITE_LOCATION, READ_LOCATION], None,                              [WRITE_LOCATION, DEFAULT_LOCATION]),  # 2
    ([WRITE_LOCATION, READ_LOCATION], [THIRD_LOCATION],                None,                              [WRITE_LOCATION, WRITE_LOCATION]),    # 3
    ([WRITE_LOCATION, READ_LOCATION], [],                              [WRITE_LOCATION],                  [READ_LOCATION, READ_LOCATION]),      # 4
    ([WRITE_LOCATION, READ_LOCATION], [WRITE_LOCATION],                [WRITE_LOCATION],                  [READ_LOCATION, READ_LOCATION]),      # 5
    ([WRITE_LOCATION, READ_LOCATION], [WRITE_LOCATION, READ_LOCATION], [WRITE_LOCATION],                  [READ_LOCATION, READ_LOCATION]),      # 6
    ([WRITE_LOCATION, READ_LOCATION], [WRITE_LOCATION],                [WRITE_LOCATION, READ_LOCATION],   [WRITE_LOCATION, DEFAULT_LOCATION]),  # 7
    ([WRITE_LOCATION, READ_LOCATION], [WRITE_LOCATION, READ_LOCATION], [WRITE_LOCATION, READ_LOCATION],   [WRITE_LOCATION, DEFAULT_LOCATION]),  # 8
    ([WRITE_LOCATION, READ_LOCATION], [WRITE_LOCATION],                [READ_LOCATION],                   [WRITE_LOCATION, WRITE_LOCATION]),    # 9
    ([WRITE_LOCATION, READ_LOCATION], [WRITE_LOCATION, READ_LOCATION], [THIRD_LOCATION],                  [WRITE_LOCATION, WRITE_LOCATION]),    # 10
    ([WRITE_LOCATION, READ_LOCATION], [WRITE_LOCATION, READ_LOCATION], [],                                [WRITE_LOCATION, WRITE_LOCATION]),    # 11
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
class _LogCaptureHandler(logging.Handler):
    """A logging.Handler that buffers every record so the test can scan
    for ``Request URL: ...`` lines after the SDK has run.
    """

    def __init__(self):
        super().__init__()
        self.messages = []

    def reset(self):
        self.messages = []

    def emit(self, record):
        self.messages.append(record.msg)


LOG_CAPTURE = _LogCaptureHandler()


async def _create_item_with_excluded_locations(container, body, excluded_locations):
    if excluded_locations is None:
        await container.create_item(body=body)
    else:
        await container.create_item(body=body, excluded_locations=excluded_locations)


def _verify_endpoint(messages, client, expected_locations, multiple_write_locations):
    if not multiple_write_locations:
        expected_locations[-1] = WRITE_LOCATION

    # pylint: disable=protected-access
    endpoint_manager = client.client_connection._global_endpoint_manager
    location_mapping = endpoint_manager.location_cache.account_locations_by_write_endpoints
    default_endpoint = endpoint_manager.location_cache.default_regional_routing_context.get_primary()

    request_urls = [m.replace("Request URL: '", "") for m in messages if "Request URL:" in m]

    actual_locations = set()
    for request_url in request_urls:
        resource_type_match = re.search(r"'x-ms-thinclient-proxy-resource-type':\s*'([^']+)'", request_url)
        if resource_type_match is None:
            continue
        if resource_type_match.group(1) == ResourceType.DatabaseAccount:
            continue
        if request_url.startswith(default_endpoint):
            actual_locations.add(DEFAULT_LOCATION)
            continue
        for endpoint, location_name in location_mapping.items():
            if request_url.startswith(endpoint):
                actual_locations.add(location_name)
                break

    assert actual_locations == set(expected_locations), (
        "expected {} got {}".format(set(expected_locations), actual_locations)
    )


# ---------------------------------------------------------------------------
# Fixture: install the log capture and warm up the test item.
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture(scope="class", autouse=True)
async def setup_and_teardown_async():
    logger = logging.getLogger("azure")
    logger.addHandler(LOG_CAPTURE)
    logger.setLevel(logging.DEBUG)

    client = CosmosClient(HOST, KEY, _backend="rust")
    try:
        container = client.get_database_client(DATABASE_ID).get_container_client(CONTAINER_ID)
        await container.upsert_item(body=TEST_ITEM)
        # Give the service a few seconds to replicate the warm-up item
        # across regions before the tests start asserting on routing.
        await asyncio.sleep(3)
        yield
    finally:
        logger.removeHandler(LOG_CAPTURE)
        await client.close()


# ---------------------------------------------------------------------------
# Test class
# ---------------------------------------------------------------------------
@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosMultiRegion
@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_and_teardown_async")
class TestExcludedLocationsAsync:
    @pytest.mark.parametrize("test_data", CREATE_ITEM_TEST_DATA)
    async def test_create_item(self, test_data):
        # Source: tests/test_excluded_locations_async.py::TestExcludedLocationsAsync.test_create_item
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in (True, False):
            async with CosmosClient(
                HOST, KEY,
                preferred_locations=preferred_locations,
                excluded_locations=client_excluded_locations,
                multiple_write_locations=multiple_write_locations,
                _backend="rust",
            ) as client:
                container = client.get_database_client(DATABASE_ID).get_container_client(CONTAINER_ID)
                LOG_CAPTURE.reset()

                body = {"id": f"doc2-{uuid.uuid4()}"}
                body.update(PARTITION_KEY_ITEMS)
                await _create_item_with_excluded_locations(container, body, request_excluded_locations)

                _verify_endpoint(LOG_CAPTURE.messages, client, list(expected_locations), multiple_write_locations)

