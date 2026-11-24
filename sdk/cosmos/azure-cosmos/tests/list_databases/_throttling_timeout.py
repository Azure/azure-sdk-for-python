# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Driver faults replacing the legacy transport's five-second 429 responses."""

import time
import uuid

from azure.cosmos import _rust
from fault_injection._delayed_create import emit


def delayed_throttling_rule():
    return {
        "id": "listing-throttle-" + uuid.uuid4().hex,
        "operation_type": "All",
        "status_code": 429,
        "delay_ms": 5000,
        "enabled": False,
        "probability": 1.0,
        "hit_limit": None,
    }


def snapshot(handle, rule_id):
    return (
        time.monotonic(),
        _rust._debug_fault_injection_rule_hit_count(handle, rule_id),
    )


def assert_throttled_timeout(before, after, timeout):
    elapsed = after[0] - before[0]
    emit(
        "listing_throttle_timeout",
        timeout=timeout,
        elapsed=elapsed,
        hits=after[1] - before[1],
    )
    assert timeout - 0.5 <= elapsed < timeout + 5, "The operation did not exhaust its own timeout budget"
    assert after[1] - before[1] >= 2, "The driver did not retry the injected 429"
