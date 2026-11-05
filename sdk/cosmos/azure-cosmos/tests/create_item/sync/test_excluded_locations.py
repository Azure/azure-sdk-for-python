# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Legacy create exclusion matrix, observing real Rust data-plane attempts.

Run on single- and multi-write accounts; V5 does not accept a client-level
multi-write switch. Native binding tests separately observe cold metadata.
"""

import uuid

import pytest
from config import clients, settings
from create_item._routing import (
    CREATE_ITEM_TEST_DATA,
    PREFERRED_LOCATIONS,
    CreateRoutingCapture,
    expected_write_region,
)

from azure.cosmos import _rust

CONFIG = settings.TestSettings()
DATABASE_ID = CONFIG.TEST_DATABASE_ID
CONTAINER_ID = CONFIG.TEST_MULTI_PARTITION_PREFIX_PK_CONTAINER_ID
PARTITION_KEY_ITEMS = {
    name: f"value{index + 1}" for index, name in enumerate(CONFIG.TEST_CONTAINER_PREFIX_PARTITION_KEY)
}


@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosMultiRegion
@pytest.mark.cosmosAADCircuitBreaker
class TestExcludedLocations:
    @pytest.mark.parametrize("test_data", CREATE_ITEM_TEST_DATA)
    def test_create_item_rust(self, test_data, monkeypatch):
        # Source: tests/test_excluded_locations.py::TestExcludedLocations.test_create_item
        client_exclusions, request_exclusions, expected_region = test_data
        capture = CreateRoutingCapture(monkeypatch)
        with clients.create_data_client(
            _backend="rust",
            preferred_locations=PREFERRED_LOCATIONS,
            excluded_locations=client_exclusions,
        ) as client:
            container = client.get_database_client(DATABASE_ID).get_container_client(CONTAINER_ID)
            body = {"id": f"doc2-{uuid.uuid4()}", **PARTITION_KEY_ITEMS}
            options = {} if request_exclusions is None else {"excluded_locations": request_exclusions}
            created = container.create_item(body, tracing_enable=False, **options)

            assert all(created[key] == value for key, value in body.items())
            regions = _rust._debug_cached_account_regions(client._adapter._ensure_driver_handle())
            capture.assert_destination(
                f"dbs/{DATABASE_ID}/colls/{CONTAINER_ID}",
                body["id"],
                expected_write_region(regions, expected_region),
            )
