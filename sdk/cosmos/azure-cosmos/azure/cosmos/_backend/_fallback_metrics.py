# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Process-wide count of Rust attempts that were retried on the legacy path.

When a Rust request hits a narrow compatibility gap, the backend retries it
through the equivalent core-python call. The request still succeeds and nothing
surfaces to the caller, so this counter is how a test or a diagnostic finds out
that it happened at all.

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
    """Return Rust attempts retried through a legacy compatibility operation."""
    with _RUST_COMPATIBILITY_FALLBACK_COUNT_LOCK:
        return _RUST_COMPATIBILITY_FALLBACK_COUNT


def record_rust_compatibility_fallback() -> None:
    """Record a request retried with the Python implementation."""
    global _RUST_COMPATIBILITY_FALLBACK_COUNT  # pylint: disable=global-statement
    with _RUST_COMPATIBILITY_FALLBACK_COUNT_LOCK:
        _RUST_COMPATIBILITY_FALLBACK_COUNT += 1
