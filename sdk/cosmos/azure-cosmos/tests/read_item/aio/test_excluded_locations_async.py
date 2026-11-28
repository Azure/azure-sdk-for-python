# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original async read exclusions, observing the real native read attempts."""
import pytest

from config import clients
from read_item._routing import READ_ITEM_TEST_DATA, ReadRoutingCapture, resolve_case, routing_order


@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosMultiRegion
@pytest.mark.cosmosAADCircuitBreaker
class TestExcludedLocationsAsync:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("test_data", READ_ITEM_TEST_DATA)
    async def test_read_item_async_rust(self, test_data, routing_order, monkeypatch):
        # Source: tests/test_excluded_locations_async.py::TestExcludedLocationsAsync.test_read_item_async
        database_id, regions = routing_order
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = resolve_case(
            test_data, regions
        )
        capture = ReadRoutingCapture(monkeypatch, asynchronous=True)
        async with clients.create_data_client_async(
            _backend="rust", preferred_locations=preferred_locations, excluded_locations=client_excluded_locations,
        ) as client:
            container = client.get_database_client(database_id).get_container_client("orders")
            if request_excluded_locations is None:
                result = await container.read_item("doc1", ["value1", "value2"])
            else:
                result = await container.read_item(
                    "doc1", ["value1", "value2"], excluded_locations=request_excluded_locations
                )
            assert result["id"] == "doc1"
            capture.assert_destination(database_id, request_excluded_locations, expected_locations)
