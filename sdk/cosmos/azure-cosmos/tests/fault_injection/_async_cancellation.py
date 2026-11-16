# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Cancel a real Python/Rust read; observe its future, not service rollback."""
import asyncio
import math
import time

DELAY_MS = 5000
OPERATION_TIMEOUT = 30.0
CANCELLATION_ALLOWANCE = 1.0


def cancellation_rule(rule_id, container_id, inject):
    return {
        "id": rule_id,
        "operation_type": "ReadItem",
        "container_id": container_id,
        "status_code": 503,
        "delay_ms": DELAY_MS,
        "probability": 1.0 if inject else 0.0,
        "hit_limit": 1,  # Consume once so the same client can subsequently recover.
    }


async def wait_for_evidence(predicate, timeout, description):
    deadline = time.monotonic() + timeout
    while not await predicate():
        assert time.monotonic() < deadline, description
        await asyncio.sleep(0.01)


def assert_cancelled(error, status, elapsed):
    assert isinstance(error, asyncio.CancelledError), "Caller cancellation must remain CancelledError"
    assert status == "dropped", "The native operation future must drop, not merely its Python waiter"
    assert math.isfinite(elapsed) and 0 <= elapsed < CANCELLATION_ALLOWANCE, "Cancellation was not prompt"


def capture_read_lifecycle(monkeypatch):
    from azure.cosmos import _rust

    original = _rust.read_item_async
    probes = []

    def observed(*args, **kwargs):
        probe = _rust._AsyncOperationProbe()
        probes.append(probe)
        return original(*args, **kwargs, _debug_lifecycle=probe)

    monkeypatch.setattr(_rust, "read_item_async", observed)
    return probes
