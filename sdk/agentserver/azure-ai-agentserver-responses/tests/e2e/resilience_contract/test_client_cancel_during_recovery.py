# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Spec 032 / B3 — client cancel DURING a recovered invocation (real signals).

The responses cancellation contract (``responses-resilience-spec.md`` §10)
distinguishes a real client cancel (``context.client_cancelled=True`` →
terminal ``cancelled``) from in-process shutdown (``context.shutdown`` → recovery
/ failed marker, NOT ``cancelled``). The conformance cause-boolean test
(``tests/conformance/test_cancellation_cause_booleans.py``) drives the cause
states by directly mutating ``ResponseContext`` — a mocked signal, not the real
one — and never covers a client cancel that arrives while a RECOVERED handler is
running.

This module closes that gap with real signals only: a resilient background
response is crashed (SIGKILL) and restarted so the resilient-task primitive
re-invokes the handler; while that recovered handler is running, the real
``POST /responses/{id}/cancel`` endpoint is invoked. The response MUST settle to
``cancelled`` (the terminal reserved for ``client_cancelled=True``), proving the
client-cancel cause is honored on the recovered lifetime.

Real signal only: SIGKILL via ``_crash_harness`` + the real cancel endpoint. No
mocked crash, no ``ResponseContext`` mutation.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable

import pytest

from tests.e2e._crash_harness import CrashHarness
from tests.e2e.resilience_contract.conftest import (
    LONG_GRACE_S,
    LONG_TIME_SECS,
    poll_until_terminal,
    post_and_get_response_id,
)


@pytest.mark.asyncio
async def test_client_cancel_during_recovery_settles_cancelled(
    make_harness: Callable[..., CrashHarness],
) -> None:
    """A real client cancel arriving during a recovered invocation settles the
    response to ``cancelled`` (client_cancelled cause), not failed/completed."""
    harness = make_harness(
        resilient_background=True,
        # Long handler sleep so the recovered invocation is still running (in
        # its interruptible sleep) when the cancel lands.
        handler_sleep_ms=int(LONG_TIME_SECS * 1000),
        shutdown_grace_seconds=LONG_GRACE_S,
    )
    await harness.start()
    try:
        response_id = await post_and_get_response_id(
            harness.client,
            store=True,
            background=True,
            stream=False,
        )
        # Let the fresh handler start, then SIGKILL + restart so recovery
        # re-invokes the handler.
        await asyncio.sleep(0.5)
        await harness.kill()
        await harness.restart()

        # Give the recovered handler a beat to re-enter and reach its
        # interruptible sleep, then issue the REAL client cancel.
        await asyncio.sleep(1.0)
        cancel_resp = await harness.client.post(f"/responses/{response_id}/cancel")
        assert cancel_resp.status_code in (
            200,
            202,
        ), f"cancel endpoint returned {cancel_resp.status_code}: {cancel_resp.text}"

        terminal = await poll_until_terminal(harness.client, response_id, timeout_seconds=30.0)
        assert terminal["status"] == "cancelled", (
            "a real client cancel during a recovered invocation MUST settle the "
            f"response to 'cancelled' (client_cancelled cause). Got: {terminal!r}"
        )
    finally:
        await harness.close()
