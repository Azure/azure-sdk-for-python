# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Count permitted fallback to the legacy path before execution.

Some unmigrated operations still use the legacy path for unsupported requests.
Count those temporary cases, not retries of failed binding calls or runs using
the private legacy test control. These are migration measurements, not
evidence of a second supported execution path.

All clients in this process, synchronous and asynchronous, share this counter.
Both reading and updating it take the same lock.
"""
from __future__ import annotations

from threading import Lock


_RUST_COMPATIBILITY_FALLBACK_COUNT = 0
_RUST_COMPATIBILITY_FALLBACK_COUNT_LOCK = Lock()


def rust_compatibility_fallback_count() -> int:
    """Return the count of fallback choices made before request execution."""
    with _RUST_COMPATIBILITY_FALLBACK_COUNT_LOCK:
        return _RUST_COMPATIBILITY_FALLBACK_COUNT


def record_rust_compatibility_fallback() -> None:
    """Count one permitted fallback to the legacy path before execution."""
    global _RUST_COMPATIBILITY_FALLBACK_COUNT  # pylint: disable=global-statement
    with _RUST_COMPATIBILITY_FALLBACK_COUNT_LOCK:
        _RUST_COMPATIBILITY_FALLBACK_COUNT += 1
