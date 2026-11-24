# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Rust-path evidence without importing the legacy comparison harness."""

import json


def _fault_rule_counter():
    try:
        from azure.cosmos import _rust
    except ImportError as error:
        raise NotImplementedError(
            "Rust fault injection requires the compiled azure.cosmos._rust module."
        ) from error
    if _rust is None:
        raise NotImplementedError("Rust fault injection requires the compiled azure.cosmos._rust module.")
    counter = getattr(_rust, "_debug_fault_injection_rule_hit_count", None)
    if not callable(counter):
        raise NotImplementedError("Rust fault-rule inspection requires a wheel built with --features test-probes.")
    return counter


def fault_rule_hit_count(adapter, rule_id: str) -> int:
    """Read fault hits through the test client's own driver handle."""
    counter = _fault_rule_counter()
    return int(counter(adapter._ensure_driver_handle(), rule_id))


async def fault_rule_hit_count_async(adapter, rule_id: str) -> int:
    """Await the test client's driver acquisition before reading fault hits."""
    counter = _fault_rule_counter()
    driver_handle = await adapter._ensure_driver_handle()
    return int(counter(driver_handle, rule_id))


def _binding_operation_count() -> int:
    """Read the process-wide counter at instrumented Rust binding entry points."""
    try:
        from azure.cosmos import _rust
        counter = getattr(_rust, "_debug_operation_count", None)
        if callable(counter):
            return int(counter())
    except (ImportError, TypeError, ValueError):
        pass
    raise AssertionError("Rust binding operation counter requires a wheel built with --features test-probes")


def emit(kind, **fields):
    print("FAULT_EVIDENCE " + json.dumps({"kind": kind, **fields}, sort_keys=True), flush=True)
