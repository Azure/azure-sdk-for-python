# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Legacy delete exclusion matrix, observing the real Rust delete call.

Uses the shared test database and prefix-key container, like the create copy.
Run on single- and multi-write accounts; V5 does not accept a client-level
multi-write switch, so the expected write region comes from Rust's account
topology instead of the removed ``multiple_write_locations`` loop.
"""

import uuid

import pytest
from config import clients, settings
from delete_item._routing import DELETE_ITEM_TEST_DATA, DeleteRoutingCapture

from azure.cosmos import _rust

CONFIG = settings.TestSettings()
DATABASE_ID = CONFIG.TEST_DATABASE_ID
CONTAINER_ID = CONFIG.TEST_MULTI_PARTITION_PREFIX_PK_CONTAINER_ID
PARTITION_KEY = CONFIG.TEST_CONTAINER_PREFIX_PARTITION_KEY
PARTITION_KEY_VALUES = [f"value{i + 1}" for i in range(len(PARTITION_KEY))]
PARTITION_KEY_ITEMS = dict(zip(PARTITION_KEY, PARTITION_KEY_VALUES))


def create_item_with_excluded_locations(container, body, excluded_locations):
    if excluded_locations is None:
        container.create_item(body=body)
    else:
        container.create_item(body=body, excluded_locations=excluded_locations)


@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosMultiRegion
@pytest.mark.cosmosAADCircuitBreaker
class TestExcludedLocations:
    @pytest.mark.parametrize("test_data", DELETE_ITEM_TEST_DATA)
    def test_delete_item_rust(self, test_data, monkeypatch):
        # Source: tests/test_excluded_locations.py::TestExcludedLocations.test_delete_item
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        # The original repeated this for multiple_write_locations in [True, False]. Rust-backed
        # clients reject that switch ("Closed by design: Rust owns endpoint discovery and
        # multi-write routing", docs/V5/api-review/RUST_PARITY_PUSHBACKS.md), so one pass runs
        # and the account's write topology decides the expected region.
        capture = DeleteRoutingCapture(monkeypatch)
        with clients.create_data_client(
            _backend="rust",
            preferred_locations=preferred_locations,
            excluded_locations=client_excluded_locations,
        ) as client:
            container = client.get_database_client(DATABASE_ID).get_container_client(CONTAINER_ID)

            # create before delete
            item_id = f"doc2-{str(uuid.uuid4())}"
            body = {"id": item_id}
            body.update(PARTITION_KEY_ITEMS)
            create_item_with_excluded_locations(container, body, request_excluded_locations)
            capture.reset()

            # API call: delete_item
            container.upsert_item(body)
            if request_excluded_locations is None:
                container.delete_item(item_id, PARTITION_KEY_VALUES)
            else:
                container.delete_item(item_id, PARTITION_KEY_VALUES, excluded_locations=request_excluded_locations)

            # Verify endpoint locations: Rust attempt regions replace the legacy logged request URLs.
            regions = _rust._debug_cached_account_regions(client._adapter._ensure_driver_handle())
            capture.assert_destination(
                f"dbs/{DATABASE_ID}/colls/{CONTAINER_ID}",
                item_id,
                request_excluded_locations,
                regions,
                expected_locations[-1],
            )
