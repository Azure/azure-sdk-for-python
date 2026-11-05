# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Rust-path evidence without importing the legacy comparison harness."""

import json


def _binding_operation_count() -> int:
    """Read the process-wide counter at instrumented Rust binding entry points."""
    try:
        from azure.cosmos import _rust
        counter = getattr(_rust, "_debug_operation_count", None)
        if callable(counter):
            return int(counter())
    except (ImportError, TypeError, ValueError):
        pass
    raise AssertionError("Rust binding operation counter is unavailable")


def _rust_fallback_count() -> int:
    """Return the number of Rust calls that continued through Python."""
    from azure.cosmos._backend._fallback_metrics import rust_compatibility_fallback_count
    return rust_compatibility_fallback_count()


def emit(kind, **fields):
    print("FAULT_EVIDENCE " + json.dumps({"kind": kind, **fields}, sort_keys=True), flush=True)
