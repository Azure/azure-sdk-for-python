# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Async copy of the delete exclusion matrix, observing the real Rust delete call.

Uses the shared test database and prefix-key container, like the create copy.
"""

import asyncio
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


async def create_item_with_excluded_locations_async(container, body, excluded_locations):
    if excluded_locations is None:
        await container.create_item(body=body)
    else:
        await container.create_item(body=body, excluded_locations=excluded_locations)


@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosMultiRegion
@pytest.mark.cosmosAADCircuitBreaker
@pytest.mark.asyncio(loop_scope="class")
class TestExcludedLocationsAsync:
    @pytest.mark.parametrize("test_data", DELETE_ITEM_TEST_DATA)
    async def test_delete_item_async_rust(self, test_data, monkeypatch):
        # Source: tests/test_excluded_locations_async.py::TestExcludedLocationsAsync.test_delete_item_async
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = test_data

        # The original repeated this for multiple_write_locations in [True, False]. Rust-backed
        # clients reject that switch ("Closed by design: Rust owns endpoint discovery and
        # multi-write routing", docs/V5/api-review/RUST_PARITY_PUSHBACKS.md), so one pass runs
        # and the account's write topology decides the expected region.
        capture = DeleteRoutingCapture(monkeypatch, asynchronous=True)
        async with clients.create_data_client_async(
            _backend="rust",
            preferred_locations=preferred_locations,
            excluded_locations=client_excluded_locations,
        ) as client:
            container = client.get_database_client(DATABASE_ID).get_container_client(CONTAINER_ID)

            # create before delete
            item_id = f"doc2-{str(uuid.uuid4())}"
            body = {"id": item_id}
            body.update(PARTITION_KEY_ITEMS)
            await create_item_with_excluded_locations_async(container, body, request_excluded_locations)
            capture.reset()

            # API call: delete_item
            if request_excluded_locations is None:
                await container.delete_item(item_id, PARTITION_KEY_VALUES)
            else:
                await container.delete_item(item_id, PARTITION_KEY_VALUES, excluded_locations=request_excluded_locations)

            # Verify endpoint locations: Rust attempt regions replace the legacy logged request URLs.
            handle = await client._adapter._ensure_driver_handle()
            regions = await asyncio.to_thread(_rust._debug_cached_account_regions, handle)
            capture.assert_destination(
                f"dbs/{DATABASE_ID}/colls/{CONTAINER_ID}",
                item_id,
                request_excluded_locations,
                regions,
                expected_locations[-1],
            )
