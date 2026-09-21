# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Count requests switched from Rust to Python before execution.

Some operations still allow the existing Python implementation when Rust
cannot handle the request. Count those choices, not retries of failed Rust
calls or explicit core-python selection.

All clients in this process, synchronous and asynchronous, share this counter.
Both reading and updating it take the same lock.
"""
from __future__ import annotations

from threading import Lock


_RUST_COMPATIBILITY_FALLBACK_COUNT = 0
_RUST_COMPATIBILITY_FALLBACK_COUNT_LOCK = Lock()


def rust_compatibility_fallback_count() -> int:
    """Return the number of requests switched to Python before execution."""
    with _RUST_COMPATIBILITY_FALLBACK_COUNT_LOCK:
        return _RUST_COMPATIBILITY_FALLBACK_COUNT


def record_rust_compatibility_fallback() -> None:
    """Count one request switched to Python before execution."""
    global _RUST_COMPATIBILITY_FALLBACK_COUNT  # pylint: disable=global-statement
    with _RUST_COMPATIBILITY_FALLBACK_COUNT_LOCK:
        _RUST_COMPATIBILITY_FALLBACK_COUNT += 1
