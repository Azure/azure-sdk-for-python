# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Spec 024 Phase 1 RED test: no race window on fast-handler completion.

Today the pre-registration race in ``_BOOKKEEPING_EVENTS`` is a documented
hazard in SOT §6.5 — the orchestrator calls ``ensure_bookkeeping_event``
to pre-register the event BEFORE the external handler runs, so that
``complete_bookkeeping_task`` can find the event when the handler
finishes. If the handler is fast enough, it could (in theory) call
``complete_bookkeeping_task`` before the event is registered.

Under spec 024 Phase 2 the bookkeeping pattern is gone — the handler
runs inside the resilient task body, so the race is architecturally
impossible.

This test fires many fast Row 2 (``resilient_background=False``,
``background=True``, ``store=true``) handlers in parallel and asserts
that EVERY response reaches a terminal status within a bounded time.
A regression that re-introduces the race would manifest as some
responses stuck in ``in_progress`` forever.

Note: today this test is GREEN-by-mitigation (the pre-registration in
``_start_resilient_background`` runs before the handler can call
``complete_bookkeeping_task``). Post-Phase-2 the test is GREEN by
construction. The value is preventing regressions in either direction.

Contract source: spec 024 Phase 1 step 7 + SOT §6.5 (the section that
documents the race and that Phase 6 deletes).
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable

import pytest

from tests.e2e._crash_harness import CrashHarness
from tests.e2e.resilience_contract.conftest import (
    LONG_GRACE_S,
    poll_until_terminal,
    post_and_get_response_id,
)

# How many fast-handler invocations to fire in parallel.
# Larger N increases race-detection sensitivity but also CI time. 30
# is enough to surface a race with high probability while keeping
# wall-clock under the per-test 60s budget.
FAN_OUT: int = 30

# Per-response terminal polling timeout. Each handler sleeps only
# ``HANDLER_SLEEP_MS`` so terminal should arrive within seconds.
POLL_TIMEOUT_SECONDS: float = 30.0

# Handler sleep — small enough to be "deliberately fast" but non-zero
# so the handler yields the event loop. Zero would also work but might
# elide async scheduling.
HANDLER_SLEEP_MS: int = 5


@pytest.mark.asyncio
async def test_no_fast_handler_race_row_2(
    make_harness: Callable[..., CrashHarness],
) -> None:
    """Fire FAN_OUT parallel Row 2 fast handlers; none stuck in_progress."""
    harness = make_harness(
        resilient_background=False,
        handler_sleep_ms=HANDLER_SLEEP_MS,
        shutdown_grace_seconds=LONG_GRACE_S,
    )
    await harness.start()
    try:
        # Fire FAN_OUT POSTs concurrently.
        async def _create_one() -> str:
            return await post_and_get_response_id(
                harness.client,
                store=True,
                background=True,
                stream=False,
            )

        response_ids = await asyncio.gather(*(_create_one() for _ in range(FAN_OUT)))
        assert len(response_ids) == FAN_OUT
        assert len(set(response_ids)) == FAN_OUT, "duplicate response IDs"

        # Now poll each to terminal in parallel.
        terminals = await asyncio.gather(
            *(poll_until_terminal(harness.client, rid, timeout_seconds=POLL_TIMEOUT_SECONDS) for rid in response_ids)
        )

        # Every one must have reached a terminal status.
        for rid, t in zip(response_ids, terminals):
            assert t["status"] in (
                "completed",
                "failed",
                "cancelled",
            ), f"response {rid} did not reach terminal; got status={t.get('status')}"
        # And for fast happy-path handlers, all should be completed.
        completed = sum(1 for t in terminals if t["status"] == "completed")
        assert completed == FAN_OUT, (
            f"expected all {FAN_OUT} fast Row 2 handlers to complete; "
            f"got {completed} completed (others: "
            f"{[t['status'] for t in terminals if t['status'] != 'completed']})"
        )
    finally:
        await harness.close()


@pytest.mark.asyncio
async def test_no_fast_handler_race_row_3(
    make_harness: Callable[..., CrashHarness],
) -> None:
    """Same shape for Row 3 (foreground): FAN_OUT parallel POSTs all reach terminal."""
    harness = make_harness(
        resilient_background=True,  # row 3 is resilient_background-agnostic
        handler_sleep_ms=HANDLER_SLEEP_MS,
        shutdown_grace_seconds=LONG_GRACE_S,
    )
    await harness.start()
    try:
        body = {
            "model": "conformance-test",
            "input": "hello",
            "store": True,
            "background": False,
            "stream": False,
        }

        async def _post_one() -> dict:
            r = await harness.client.post("/responses", json=body, timeout=30.0)
            assert r.status_code == 200, r.text
            return r.json()

        results = await asyncio.gather(*(_post_one() for _ in range(FAN_OUT)))

        # Row 3 foreground returns the terminal body directly — every
        # one must be completed.
        for r in results:
            assert r["status"] == "completed", (
                f"row 3 foreground response did not complete; got status={r.get('status')}, " f"id={r.get('id')}"
            )
    finally:
        await harness.close()
