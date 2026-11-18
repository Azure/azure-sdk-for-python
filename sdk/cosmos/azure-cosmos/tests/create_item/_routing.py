# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Create routing evidence from the real binding, not Python request logs."""

import os
from urllib.parse import urlsplit

from fault_injection._regional_routing import native_records

WRITE_LOCATION = os.environ.get("LEGACY_WRITE_LOCATION", "West US")
READ_LOCATION = os.environ.get("LEGACY_READ_LOCATION", "East US")
THIRD_LOCATION = "East US 2"
DEFAULT_LOCATION = "Default"
PREFERRED_LOCATIONS = [WRITE_LOCATION, READ_LOCATION]

# Original client/request exclusions and multi-write create destinations.
# Cold metadata destinations are checked separately in the native binding test
# create_exclusion_matrix_observes_metadata_and_write_routes.
CREATE_ITEM_TEST_DATA = [
    ([], None, WRITE_LOCATION),
    ([WRITE_LOCATION], None, READ_LOCATION),
    ([WRITE_LOCATION, READ_LOCATION], None, DEFAULT_LOCATION),
    ([THIRD_LOCATION], None, WRITE_LOCATION),
    ([], [WRITE_LOCATION], READ_LOCATION),
    ([WRITE_LOCATION], [WRITE_LOCATION], READ_LOCATION),
    ([WRITE_LOCATION, READ_LOCATION], [WRITE_LOCATION], READ_LOCATION),
    ([WRITE_LOCATION], [WRITE_LOCATION, READ_LOCATION], DEFAULT_LOCATION),
    ([WRITE_LOCATION, READ_LOCATION], [WRITE_LOCATION, READ_LOCATION], DEFAULT_LOCATION),
    ([WRITE_LOCATION], [READ_LOCATION], WRITE_LOCATION),
    ([WRITE_LOCATION, READ_LOCATION], [THIRD_LOCATION], WRITE_LOCATION),
    ([WRITE_LOCATION, READ_LOCATION], [], WRITE_LOCATION),
]


def normalize_region(region):
    assert isinstance(region, str) and region.strip(), "Missing Rust attempt region"
    return region.replace(" ", "").lower()


def expected_write_region(account_regions, expected_multi_write_region):
    """Use Rust's account topology, never the removed client multi-write switch."""
    assert account_regions is not None, "Missing Rust account topology"
    writes, reads = account_regions
    preferred = {normalize_region(region) for region in PREFERRED_LOCATIONS}
    assert preferred.issubset(
        {normalize_region(region) for region in reads}
    ), "Routing matrix requires both configured preferred regions in the account"
    assert writes, "Account has no writable regions"
    if len(writes) == 1 or expected_multi_write_region == DEFAULT_LOCATION:
        return normalize_region(writes[0])
    assert preferred.issubset(
        {normalize_region(region) for region in writes}
    ), "Multi-write matrix requires both preferred regions to be writable"
    return normalize_region(expected_multi_write_region)


class CreateRoutingCapture:
    """Capture one public create's native result without replaying the request."""

    def __init__(self, monkeypatch, *, asynchronous=False):
        if asynchronous:
            from azure.cosmos.aio._backend import binding_adapter as module
        else:
            from azure.cosmos._backend import binding_adapter as module

        self.calls = []
        original = module._binding_function_for_op

        def select(operation):
            function = original(operation)
            if operation != "create_item":
                return function

            def capture(handle, prepared, **kwargs):
                assert not kwargs.get("include_attempts"), "Disable attempt telemetry for routing capture"
                response, payload = function(handle, prepared, **kwargs, include_fault_diagnostics=True)
                self.calls.append((prepared.container_link, prepared.item_id, payload))
                return response

            async def capture_async(handle, prepared, **kwargs):
                assert not kwargs.get("include_attempts"), "Disable attempt telemetry for routing capture"
                response, payload = await function(handle, prepared, **kwargs, include_fault_diagnostics=True)
                self.calls.append((prepared.container_link, prepared.item_id, payload))
                return response

            return capture_async if asynchronous else capture

        monkeypatch.setattr(module, "_binding_function_for_op", select)

    def assert_destination(self, container_link, item_id, expected_region):
        assert len(self.calls) == 1, "Expected exactly one native create result"
        actual_container, actual_id, payload = self.calls[0]
        assert (actual_container, actual_id) == (container_link, item_id), "Evidence belongs to another create"
        records = native_records(payload)
        assert payload["result_status"] == 201, "Native create did not succeed"
        expected = normalize_region(expected_region)
        for record in records:
            endpoint = urlsplit(record["endpoint"])
            assert endpoint.scheme == "https" and endpoint.hostname, "Missing native request destination"
            assert (
                normalize_region(record["region"]) == expected
            ), f"Create attempted {record['region']!r}; expected {expected_region!r}"
        assert records[-1]["status"] == 201, "No successful create attempt"
