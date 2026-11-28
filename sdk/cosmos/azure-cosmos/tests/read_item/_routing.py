# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Main's twelve read-exclusion cases, checked against native attempt regions."""
import time
from urllib.parse import urlsplit
import uuid

import pytest

from azure.cosmos import PartitionKey, _rust
from common.throughput_fixtures import owned_database
from config import clients
from create_item._routing import normalize_region
from fault_injection._regional_routing import native_records

# Indices replace the original account-dependent L1/L2/L3 names.
READ_ITEM_TEST_DATA = [
    ([0, 1], [], None, [0]),
    ([0, 1], [0], None, [1]),
    ([0, 1], [0, 1], None, [0]),
    ([0, 1], [2], None, [0]),
    ([0, 1], [], [0], [1]),
    ([0, 1], [0], [0], [1]),
    ([0, 1], [0, 1], [0], [1]),
    ([0, 1], [0], [0, 1], [0]),
    ([0, 1], [0, 1], [0, 1], [0]),
    ([0, 1], [0], [1], [0]),
    ([0, 1], [0, 1], [2], [0]),
    ([0, 1], [0, 1], [], [0]),
]


@pytest.fixture(scope="module")
def routing_order():
    with clients.create_setup_client(_backend="rust") as setup:
        topology = _rust._debug_cached_account_regions(setup._adapter._ensure_driver_handle())
        assert topology is not None, "Excluded-location tests require native account topology"
        writes, reads = topology
        assert writes, "The account has no writable region"
        primary = writes[0]
        secondary = next((region for region in reads if normalize_region(region) != normalize_region(primary)), None)
        assert secondary is not None, "Excluded-location tests require an account with at least two readable regions"
        # L3 represents a location outside the two preferred locations.
        other = next(region for region in ("East US 2", "North Europe", "Japan East")
                     if normalize_region(region) not in {normalize_region(primary), normalize_region(secondary)})
        with owned_database(setup, "read-routing-" + uuid.uuid4().hex) as database:
            database.create_container("orders", partition_key=PartitionKey(path=["/pk1", "/pk2"]))
            with clients.create_data_client(_backend="rust") as writer:
                container = writer.get_database_client(database.id).get_container_client("orders")
                container.create_item({"id": "doc1", "pk1": "value1", "pk2": "value2"})
            time.sleep(3)  # Preserve the original cross-region replication allowance.
            yield database.id, (primary, secondary, other)


def resolve_case(test_data, regions):
    return tuple(None if group is None else [regions[index] for index in group] for group in test_data)


class ReadRoutingCapture:
    def __init__(self, monkeypatch, *, asynchronous=False):
        if asynchronous:
            from azure.cosmos.aio._backend import binding_adapter as module
        else:
            from azure.cosmos._backend import binding_adapter as module
        self.calls = []
        original = module._binding_function_for_op

        def select(operation):
            function = original(operation)
            if operation != "read_item":
                return function

            def capture(handle, prepared, **kwargs):
                assert not kwargs.get("include_attempts"), "Disable attempt telemetry for routing capture"
                response, payload = function(handle, prepared, **kwargs, include_fault_diagnostics=True)
                self.calls.append((prepared, payload))
                return response

            async def capture_async(handle, prepared, **kwargs):
                assert not kwargs.get("include_attempts"), "Disable attempt telemetry for routing capture"
                response, payload = await function(handle, prepared, **kwargs, include_fault_diagnostics=True)
                self.calls.append((prepared, payload))
                return response

            return capture_async if asynchronous else capture

        monkeypatch.setattr(module, "_binding_function_for_op", select)

    def assert_destination(self, database_id, request_exclusions, expected_locations):
        assert len(self.calls) == 1, "Expected exactly one native read result"
        prepared, payload = self.calls[0]
        assert (prepared.container_link, prepared.item_id) == (f"dbs/{database_id}/colls/orders", "doc1")
        expected_exclusions = None if request_exclusions is None else tuple(request_exclusions)
        assert prepared.settings.excluded_locations == expected_exclusions
        assert payload["result_status"] == 200
        records = native_records(payload)
        for record in records:
            endpoint = urlsplit(record["endpoint"])
            assert endpoint.scheme == "https" and endpoint.hostname, "Missing native read destination"
        assert {normalize_region(record["region"]) for record in records} == {
            normalize_region(region) for region in expected_locations
        }
        assert records[-1]["status"] == 200
