# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Delete routing evidence from the real binding, not Python request logs.

The original delete matrix read request URLs from a Python logging handler.
Rust requests never reach that handler, so this module records the native
delete call itself and, when the binding can report it, the region of each
data-plane attempt.
"""

import inspect
from urllib.parse import urlsplit

import pytest
from create_item._routing import (
    DEFAULT_LOCATION,
    PREFERRED_LOCATIONS,
    READ_LOCATION,
    THIRD_LOCATION,
    WRITE_LOCATION,
    expected_write_region,
    normalize_region,
)
from fault_injection._regional_routing import native_records

L0 = DEFAULT_LOCATION
L1 = WRITE_LOCATION
L2 = READ_LOCATION
L3 = THIRD_LOCATION

# Same inputs and expected write locations as the original
# tests/test_excluded_locations.py::write_item_test_data() with ALL_TESTS:
# [preferred_locations, client_excluded_locations, request_excluded_locations, expected_locations]
DELETE_ITEM_TEST_DATA = [
    # Client-only exclusions
    [[L1, L2], [], None, [L1]],
    [[L1, L2], [L1], None, [L2]],
    [[L1, L2], [L1, L2], None, [L0]],
    [[L1, L2], [L3], None, [L1]],
    # Client and request exclusions
    [[L1, L2], [], [L1], [L2]],
    [[L1, L2], [L1], [L1], [L2]],
    [[L1, L2], [L1, L2], [L1], [L2]],
    [[L1, L2], [L1], [L1, L2], [L0]],
    [[L1, L2], [L1, L2], [L1, L2], [L0]],
    [[L1, L2], [L1], [L2], [L1]],
    [[L1, L2], [L1, L2], [L3], [L1]],
    [[L1, L2], [L1, L2], [], [L1]],
]

DIAGNOSTICS_UNAVAILABLE = (
    "Rust delete_item binding does not accept include_fault_diagnostics, so the "
    "region of each delete attempt cannot be observed; the legacy check read "
    "request URLs from a Python logging handler that Rust requests never reach"
)


def _supports_fault_diagnostics(function):
    signature = getattr(function, "__text_signature__", None) or ""
    if "include_fault_diagnostics" in signature:
        return True
    try:
        return "include_fault_diagnostics" in inspect.signature(function).parameters
    except (TypeError, ValueError):
        return False


class DeleteRoutingCapture:
    """Capture one public delete's native call without replaying the request."""

    def __init__(self, monkeypatch, *, asynchronous=False):
        if asynchronous:
            from azure.cosmos.aio._backend import binding_adapter as module
        else:
            from azure.cosmos._backend import binding_adapter as module

        self.calls = []
        original = module._binding_function_for_op

        def select(operation):
            function = original(operation)
            if operation != "delete_item":
                return function
            diagnostics = _supports_fault_diagnostics(function)

            def capture(handle, prepared, **kwargs):
                if not diagnostics:
                    response = function(handle, prepared, **kwargs)
                    self.calls.append((prepared, None))
                    return response
                assert not kwargs.get("include_attempts"), "Disable attempt telemetry for routing capture"
                response, payload = function(handle, prepared, **kwargs, include_fault_diagnostics=True)
                self.calls.append((prepared, payload))
                return response

            async def capture_async(handle, prepared, **kwargs):
                if not diagnostics:
                    response = await function(handle, prepared, **kwargs)
                    self.calls.append((prepared, None))
                    return response
                assert not kwargs.get("include_attempts"), "Disable attempt telemetry for routing capture"
                response, payload = await function(handle, prepared, **kwargs, include_fault_diagnostics=True)
                self.calls.append((prepared, payload))
                return response

            return capture_async if asynchronous else capture

        monkeypatch.setattr(module, "_binding_function_for_op", select)

    def reset(self):
        self.calls.clear()

    def assert_destination(self, container_link, item_id, request_exclusions, account_regions, expected_location):
        assert len(self.calls) == 1, "Expected exactly one native delete call"
        prepared, payload = self.calls[0]
        assert (prepared.container_link, prepared.item_id) == (container_link, item_id), (
            "Evidence belongs to another delete")
        expected_exclusions = None if request_exclusions is None else tuple(request_exclusions)
        assert prepared.settings.excluded_locations == expected_exclusions, (
            "Request exclusions did not reach the native delete")
        if payload is None:
            pytest.skip(DIAGNOSTICS_UNAVAILABLE)
        expected = expected_write_region(account_regions, expected_location)
        records = native_records(payload)
        assert payload["result_status"] == 204, "Native delete did not succeed"
        for record in records:
            endpoint = urlsplit(record["endpoint"])
            assert endpoint.scheme == "https" and endpoint.hostname, "Missing native request destination"
            assert normalize_region(record["region"]) == expected, (
                f"Delete attempted {record['region']!r}; expected {expected!r}")
        assert records[-1]["status"] == 204, "No successful delete attempt"


__all__ = ["DELETE_ITEM_TEST_DATA", "PREFERRED_LOCATIONS", "DeleteRoutingCapture"]
