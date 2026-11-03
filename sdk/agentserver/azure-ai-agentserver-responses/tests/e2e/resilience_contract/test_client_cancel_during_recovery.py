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

import httpx
import pytest

from tests.e2e._crash_harness import CrashHarness
from tests.e2e.resilience_contract.conftest import (
    LONG_GRACE_S,
    LONG_TIME_SECS,
    poll_until_terminal,
    post_and_get_response_id,
)


async def _cancel_with_retry(
    client: httpx.AsyncClient,
    response_id: str,
    *,
    timeout_seconds: float = 15.0,
    poll_interval_seconds: float = 0.2,
) -> httpx.Response:
    """POST ``/responses/{id}/cancel``, retrying while the recovery scanner
    catches up.

    Immediately after ``CrashHarness.restart()``, ``/health/live`` reports
    ready as soon as the HTTP server binds — before the recovery scanner has
    necessarily re-registered this response in the new process's in-memory
    runtime state. A cancel that lands in that window gets a transient 404
    (no live record yet), which a real client would retry rather than treat
    as a permanent failure. Returns the first non-404 response, or the last
    404 response if *timeout_seconds* elapses.
    """
    deadline = asyncio.get_event_loop().time() + timeout_seconds
    last_response: httpx.Response | None = None
    while asyncio.get_event_loop().time() < deadline:
        last_response = await client.post(f"/responses/{response_id}/cancel")
        if last_response.status_code != 404:
            return last_response
        await asyncio.sleep(poll_interval_seconds)
    assert last_response is not None  # loop always runs at least once
    return last_response


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
        # interruptible sleep. The recovery scanner re-registers the
        # response in the new process's in-memory runtime state
        # asynchronously after ``/health/live`` already reports ready, so a
        # fixed sleep here is inherently racy under CI load (e.g. the
        # coverage-instrumented job): if the real cancel lands before the
        # scanner has re-registered this response, the endpoint can't find
        # a live record yet and returns 404. A real client hitting that
        # transient window would retry, so do the same here with the real
        # cancel endpoint (no mocking) instead of widening a guessed sleep.
        await asyncio.sleep(1.0)
        cancel_resp = await _cancel_with_retry(harness.client, response_id, timeout_seconds=15.0)
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
