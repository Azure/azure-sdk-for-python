# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 18 invocation pattern p02 — resilient_bg + bg + streamed.

Pattern: ``(store=true, background=true, resilient_background=True, stream=True)``.

The closure of spec 014 divergence 1. The user POSTs a streaming
background request; the framework runs the handler inside the resilient
task primitive so a server crash mid-stream still produces a recoverable
response. A reconnecting client at
``GET /responses/{id}?stream=true&starting_after=N`` sees a
``response.in_progress`` reset followed by continuation and a coherent
terminal.

Paths covered:

- **Path A** — natural completion. POST returns the SSE stream; client
  consumes events through ``response.completed``.
- **Path B** — SIGTERM with short grace; client disconnects, restart;
  GET-reconnect via ``starting_after=`` returns a reset
  ``response.in_progress`` then continuation and ``response.completed``.
- **Path C** — SIGKILL mid-stream; same recovery shape as Path B.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable

import pytest

from tests.e2e._crash_harness import CrashHarness
from tests.e2e.sample_18_invocation_patterns.conftest import (
    SLOW_PROMPT,
    LONG_GRACE_S,
    SHORT_GRACE_S,
    TERMINAL_POLL_BUDGET_S,
    payload,
    poll_until_terminal,
    post_and_get_response_id,
    reconnect_stream_and_collect_events,
)

pytestmark = pytest.mark.live


def _terminal_in(events: list[dict]) -> dict | None:
    for ev in events:
        t = ev.get("type", "")
        if t in (
            "response.completed",
            "response.failed",
            "response.cancelled",
        ):
            return ev
    return None


@pytest.mark.asyncio
async def test_p02_path_a_natural_completion(
    make_harness: Callable[..., CrashHarness],
) -> None:
    """p02 Path A: streamed POST yields response.created → completed."""
    harness = make_harness(
        shutdown_grace_seconds=LONG_GRACE_S,
    )
    await harness.start()
    try:
        response_id = await post_and_get_response_id(
            harness.client,
            store=True,
            background=True,
            stream=True,
            model="copilot",
            input_text="say hi briefly",
        )
        terminal = await poll_until_terminal(
            harness.client,
            response_id,
            timeout_seconds=TERMINAL_POLL_BUDGET_S,
        )
        assert terminal["status"] == "completed", terminal
    finally:
        await harness.close()


@pytest.mark.asyncio
async def test_p02_path_b_graceful_recovery_with_reconnect(
    make_harness: Callable[..., CrashHarness],
) -> None:
    """p02 Path B: graceful shutdown then GET-reconnect with reset+terminal."""
    harness = make_harness(
        shutdown_grace_seconds=SHORT_GRACE_S,
    )
    await harness.start()
    try:
        response_id = await post_and_get_response_id(
            harness.client,
            store=True,
            background=True,
            stream=True,
            model="copilot",
            input_text=SLOW_PROMPT,
        )

        await harness.terminate(wait_seconds=SHORT_GRACE_S + 2.0)
        await harness.restart()

        # Drive terminal first so the recovered handler has time to
        # reattach to Copilot and produce a real terminal.
        terminal = await poll_until_terminal(
            harness.client,
            response_id,
            timeout_seconds=TERMINAL_POLL_BUDGET_S,
        )
        assert terminal["status"] == "completed", terminal

        # Now reconnect with starting_after=0 and assert the replay
        # includes a reset response.in_progress.
        events = await reconnect_stream_and_collect_events(
            harness.client,
            response_id,
            starting_after=0,
            timeout_seconds=30.0,
        )
        in_progress = [e for e in events if e.get("type") == "response.in_progress"]
        assert in_progress, (
            "Replay must include at least one response.in_progress event "
            "(the reset marker for snapshot reconciliation). Events: "
            f"{[e.get('type') for e in events]}"
        )
        term = _terminal_in(events)
        assert term is not None and term.get("type") == "response.completed", term
    finally:
        await harness.close()


@pytest.mark.asyncio
async def test_p02_path_c_sigkill_recovery_with_reconnect(
    make_harness: Callable[..., CrashHarness],
) -> None:
    """p02 Path C: SIGKILL then GET-reconnect with reset+terminal."""
    harness = make_harness(
        shutdown_grace_seconds=LONG_GRACE_S,
    )
    await harness.start()
    try:
        response_id = await post_and_get_response_id(
            harness.client,
            store=True,
            background=True,
            stream=True,
            model="copilot",
            input_text=SLOW_PROMPT,
        )

        await asyncio.sleep(0.5)
        await harness.kill()
        await harness.restart()

        terminal = await poll_until_terminal(
            harness.client,
            response_id,
            timeout_seconds=TERMINAL_POLL_BUDGET_S,
        )
        assert terminal["status"] == "completed", terminal

        events = await reconnect_stream_and_collect_events(
            harness.client,
            response_id,
            starting_after=0,
            timeout_seconds=30.0,
        )
        in_progress = [e for e in events if e.get("type") == "response.in_progress"]
        assert in_progress, (
            "Replay must include at least one response.in_progress event. " f"Events: {[e.get('type') for e in events]}"
        )
        term = _terminal_in(events)
        assert term is not None and term.get("type") == "response.completed", term
    finally:
        await harness.close()
