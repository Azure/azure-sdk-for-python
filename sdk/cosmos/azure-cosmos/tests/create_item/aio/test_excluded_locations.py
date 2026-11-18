# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Async copy of the create exclusion matrix using Rust attempt diagnostics."""

import asyncio
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
@pytest.mark.asyncio
@pytest.mark.cosmosAADCircuitBreaker
class TestExcludedLocationsAsync:
    @pytest.mark.parametrize("test_data", CREATE_ITEM_TEST_DATA)
    async def test_create_item_rust(self, test_data, monkeypatch):
        # Source: tests/test_excluded_locations_async.py::TestExcludedLocationsAsync.test_create_item
        client_exclusions, request_exclusions, expected_region = test_data
        capture = CreateRoutingCapture(monkeypatch, asynchronous=True)
        async with clients.create_data_client_async(
            _backend="rust",
            preferred_locations=PREFERRED_LOCATIONS,
            excluded_locations=client_exclusions,
        ) as client:
            container = client.get_database_client(DATABASE_ID).get_container_client(CONTAINER_ID)
            body = {"id": f"doc2-{uuid.uuid4()}", **PARTITION_KEY_ITEMS}
            options = {} if request_exclusions is None else {"excluded_locations": request_exclusions}
            created = await container.create_item(body, tracing_enable=False, **options)

            assert all(created[key] == value for key, value in body.items())
            handle = await client._adapter._ensure_driver_handle()
            regions = await asyncio.to_thread(_rust._debug_cached_account_regions, handle)
            capture.assert_destination(
                f"dbs/{DATABASE_ID}/colls/{CONTAINER_ID}",
                body["id"],
                expected_write_region(regions, expected_region),
            )
