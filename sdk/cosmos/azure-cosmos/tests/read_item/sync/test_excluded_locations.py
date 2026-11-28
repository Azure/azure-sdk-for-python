# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original read exclusions, replacing legacy request logs with native evidence."""
import pytest

from config import clients
from read_item._routing import READ_ITEM_TEST_DATA, ReadRoutingCapture, resolve_case, routing_order


@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosMultiRegion
@pytest.mark.cosmosAADCircuitBreaker
class TestExcludedLocations:
    @pytest.mark.parametrize("test_data", READ_ITEM_TEST_DATA)
    def test_read_item_rust(self, test_data, routing_order, monkeypatch):
        # Source: tests/test_excluded_locations.py::TestExcludedLocations.test_read_item
        database_id, regions = routing_order
        preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations = resolve_case(
            test_data, regions
        )
        capture = ReadRoutingCapture(monkeypatch)
        with clients.create_data_client(
            _backend="rust", preferred_locations=preferred_locations, excluded_locations=client_excluded_locations,
        ) as client:
            container = client.get_database_client(database_id).get_container_client("orders")
            if request_excluded_locations is None:
                result = container.read_item(item="doc1", partition_key=["value1", "value2"])
            else:
                result = container.read_item(
                    item="doc1", partition_key=["value1", "value2"], excluded_locations=request_excluded_locations
                )
            assert result["id"] == "doc1"
            capture.assert_destination(database_id, request_excluded_locations, expected_locations)
