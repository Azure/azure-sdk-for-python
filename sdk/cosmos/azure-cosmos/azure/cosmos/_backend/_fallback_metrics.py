# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Process-wide count of permitted pre-dispatch legacy compatibility routes.

When a Rust-selected request is ineligible or static preflight detects an
allowed capability gap, the coordinator invokes its legacy callable instead.
No Rust execution is retried. Explicit core-python selection is not counted.

The count is shared by every client in the process and can be incremented from
any thread, so both functions take a lock. The async backends record through
this same counter, which is why :func:`record_rust_compatibility_fallback` is
public to the package rather than private to one module.
"""
from __future__ import annotations

from threading import Lock


_RUST_COMPATIBILITY_FALLBACK_COUNT = 0
_RUST_COMPATIBILITY_FALLBACK_COUNT_LOCK = Lock()


def rust_compatibility_fallback_count() -> int:
    """Return the number of permitted pre-dispatch compatibility routes."""
    with _RUST_COMPATIBILITY_FALLBACK_COUNT_LOCK:
        return _RUST_COMPATIBILITY_FALLBACK_COUNT


def record_rust_compatibility_fallback() -> None:
    """Record pre-dispatch routing to the Python implementation."""
    global _RUST_COMPATIBILITY_FALLBACK_COUNT  # pylint: disable=global-statement
    with _RUST_COMPATIBILITY_FALLBACK_COUNT_LOCK:
        _RUST_COMPATIBILITY_FALLBACK_COUNT += 1
