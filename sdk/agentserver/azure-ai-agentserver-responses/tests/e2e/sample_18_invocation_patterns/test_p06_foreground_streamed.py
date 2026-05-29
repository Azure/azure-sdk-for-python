# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 18 invocation pattern p06 — foreground + streamed.

Pattern: ``(store=true, background=false, stream=True)``.

Foreground streaming: the client receives SSE events over the live HTTP
connection. The connection dies with the server, but per-event
persistence to ``_durable_stream_provider`` continues; on restart a
reconnecting client at ``GET ?stream=true&starting_after=N`` sees the
events that landed plus the recovery-failed terminal.

Paths covered:

- **Path A** — natural completion through the live stream.
- **Path B** — SIGTERM short grace; in-process marker writes failed
  terminal; GET-reconnect sees ``response.failed``.
- **Path C** — SIGKILL; next-lifetime recovery marks failed;
  GET-reconnect sees ``response.failed``.
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
async def test_p06_path_a_natural_completion(
    make_harness: Callable[..., CrashHarness],
) -> None:
    """p06 Path A: foreground streamed POST completes via live stream."""
    harness = make_harness(
        shutdown_grace_seconds=LONG_GRACE_S,
    )
    await harness.start()
    try:
        response_id = await post_and_get_response_id(
            harness.client,
            store=True,
            background=False,
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
async def test_p06_path_b_graceful_marks_failed(
    make_harness: Callable[..., CrashHarness],
) -> None:
    """p06 Path B: graceful shutdown → failed terminal; GET-reconnect sees it."""
    harness = make_harness(
        shutdown_grace_seconds=SHORT_GRACE_S,
    )
    await harness.start()
    try:
        response_id = await post_and_get_response_id(
            harness.client,
            store=True,
            background=False,
            stream=True,
            model="copilot",
            input_text=SLOW_PROMPT,
        )

        await harness.terminate(wait_seconds=SHORT_GRACE_S + 2.0)
        await harness.restart()

        terminal = await poll_until_terminal(
            harness.client,
            response_id,
            timeout_seconds=TERMINAL_POLL_BUDGET_S,
        )
        assert terminal["status"] == "failed", terminal

        events = await reconnect_stream_and_collect_events(
            harness.client,
            response_id,
            starting_after=0,
            timeout_seconds=30.0,
        )
        term = _terminal_in(events)
        assert term is not None, [e.get("type") for e in events]
        assert term.get("type") == "response.failed", term
    finally:
        await harness.close()


@pytest.mark.asyncio
async def test_p06_path_c_sigkill_marks_failed(
    make_harness: Callable[..., CrashHarness],
) -> None:
    """p06 Path C: SIGKILL → next-lifetime marks failed."""
    harness = make_harness(
        shutdown_grace_seconds=LONG_GRACE_S,
    )
    await harness.start()
    try:
        response_id = await post_and_get_response_id(
            harness.client,
            store=True,
            background=False,
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
        assert terminal["status"] == "failed", terminal
        error = terminal.get("error") or {}
        assert error.get("code") == "server_error", terminal
        additional = error.get("additionalInfo") or {}
        assert additional.get("shutdown_reason") == "crash_recovery", terminal
    finally:
        await harness.close()
