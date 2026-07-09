# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Sync ``test_create_item`` excluded-locations routing test against the
``_backend="rust"`` path.

The original ``TestExcludedLocations`` class in
``tests/test_excluded_locations.py`` covers eleven operations
(create / read / query / replace / upsert / patch / batch / delete /
…). This copy keeps only ``test_create_item`` and the helpers it
needs; everything else belongs in its own operation's ``legacy/``
folder.

The 12-row test data table is the flattening of the source's
``read_and_write_item_test_data()`` -- the expected-locations column
holds the read-route region followed by the write-route region, in
that order.

The class name and method name match the source so test IDs differ
only by path.

This test runs against a live multi-region account; it is gated by
``cosmosMultiRegion`` / ``cosmosCircuitBreaker`` markers.
"""
import logging
import os
import re
import time
import uuid

import pytest

from azure.cosmos import CosmosClient
from azure.cosmos.http_constants import ResourceType


# ---------------------------------------------------------------------------
# Account configuration (overridable via environment).
# ---------------------------------------------------------------------------
HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)
# The multi-region account must have these provisioned in advance.
# create_item routing is observed against a pre-existing container; we
# do not create the database / container per-test.
DATABASE_ID = os.environ.get("LEGACY_EXCLUDED_LOCATIONS_DATABASE_ID", "PythonSDKTestDatabase")
CONTAINER_ID = os.environ.get("LEGACY_EXCLUDED_LOCATIONS_CONTAINER_ID", "MultiPartitionPrefixPKTestContainer")

# The partition-key path for the test container (matches the source).
PARTITION_KEY = ["state", "city", "zipcode"]
PARTITION_KEY_VALUES = [f"value{i+1}" for i in range(len(PARTITION_KEY))]
PARTITION_KEY_ITEMS = dict(zip(PARTITION_KEY, PARTITION_KEY_VALUES))
ITEM_ID = "doc1"
TEST_ITEM = {"id": ITEM_ID, **PARTITION_KEY_ITEMS}

# Region labels used by the test data table. They name the role each
# region plays in the routing tests, not the actual Azure region name
# (override the two preferred-region labels via env vars if your
# multi-region account uses different regions).
DEFAULT_LOCATION = "Default"                                            # the account's default endpoint
WRITE_LOCATION = os.environ.get("LEGACY_WRITE_LOCATION", "West US")     # primary preferred (write) region
READ_LOCATION = os.environ.get("LEGACY_READ_LOCATION", "East US")       # secondary preferred (read) region
THIRD_LOCATION = "East US 2"                                            # a region not in the preferred list


# ---------------------------------------------------------------------------
# Test data: each row is
#     (preferred_locations,
#      client_excluded_locations,
#      request_excluded_locations,
#      [expected_read_region, expected_write_region])
#
# Rows 0-3 exercise client-side excluded_locations only (no per-request
# override). Rows 4-11 exercise client + request-level excluded_locations.
# ---------------------------------------------------------------------------
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
    ([WRITE_LOCATION, READ_LOCATION], [WRITE_LOCATION, READ_LOCATION], [],                                [WRITE_LOCATION, WRITE_LOCATION]),    # 11 (empty request override)
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


def _create_item_with_excluded_locations(container, body, excluded_locations):
    """Call ``create_item`` with or without ``excluded_locations`` set,
    so passing ``None`` is distinguishable from passing an empty list.
    """
    if excluded_locations is None:
        container.create_item(body=body)
    else:
        container.create_item(body=body, excluded_locations=excluded_locations)


def _build_client_and_container(preferred_locations, client_excluded_locations, multiple_write_locations):
    """Build a rust-backed CosmosClient with the given region-routing
    configuration and return ``(client, container)``. Also clears the
    log capture so a fresh test iteration starts with no leftover URLs.
    """
    client = CosmosClient(
        HOST, KEY,
        preferred_locations=preferred_locations,
        excluded_locations=client_excluded_locations,
        multiple_write_locations=multiple_write_locations,
        _backend="rust",
    )
    container = client.get_database_client(DATABASE_ID).get_container_client(CONTAINER_ID)
    LOG_CAPTURE.reset()
    return client, container


def _verify_endpoint(messages, client, expected_locations, multiple_write_locations):
    """Parse ``Request URL: ...`` lines out of ``messages`` and assert
    the set of regions the SDK actually contacted matches
    ``expected_locations``. Skips the database-account health-check
    requests, which carry no operation-level routing signal.
    """
    if not multiple_write_locations:
        # When the account is not configured for multi-write, the
        # write region collapses to the account's primary write region.
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
            # Health-check traffic; not part of the routing under test.
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
@pytest.fixture(scope="class", autouse=True)
def setup_and_teardown():
    logger = logging.getLogger("azure")
    logger.addHandler(LOG_CAPTURE)
    logger.setLevel(logging.DEBUG)

    client = CosmosClient(HOST, KEY, _backend="rust")
    try:
        container = client.get_database_client(DATABASE_ID).get_container_client(CONTAINER_ID)
        container.upsert_item(body=TEST_ITEM)
        # Give the service a few seconds to replicate the warm-up item
        # to the other regions before the tests start asserting on
        # cross-region routing.
        time.sleep(3)
        yield
    finally:
        logger.removeHandler(LOG_CAPTURE)


# ---------------------------------------------------------------------------
# Test class
# ---------------------------------------------------------------------------
@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosMultiRegion
class TestExcludedLocations:
    @pytest.mark.parametrize("test_data", CREATE_ITEM_TEST_DATA)
    def test_create_item(self, test_data):
        # Source: tests/test_excluded_locations.py::TestExcludedLocations.test_create_item
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        for multiple_write_locations in (True, False):
            client, container = _build_client_and_container(
                preferred_locations, client_excluded_locations, multiple_write_locations,
            )

            body = {"id": f"doc2-{uuid.uuid4()}"}
            body.update(PARTITION_KEY_ITEMS)
            _create_item_with_excluded_locations(container, body, request_excluded_locations)

            _verify_endpoint(LOG_CAPTURE.messages, client, list(expected_locations), multiple_write_locations)

