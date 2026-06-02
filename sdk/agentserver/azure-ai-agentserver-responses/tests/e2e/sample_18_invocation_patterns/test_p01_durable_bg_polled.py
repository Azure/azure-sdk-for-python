# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 18 invocation pattern p01 — durable_bg + bg + polled.

Pattern: ``(store=true, background=true, durable_background=True, stream=False)``.

The user POSTs a background request without streaming and polls
``GET /responses/{id}`` until terminal. The framework wraps the handler
in a durable task, so server crashes mid-handler trigger re-invoke.

Paths covered:

- **Path A** — natural completion within grace. Server stays up; handler
  finishes a real Copilot turn; ``GET`` polls until ``completed``.
- **Path B** — SIGTERM with short grace while the handler is awaiting
  Copilot's response (the prompt is written to take longer than the
  grace). The framework leaves the durable task ``in_progress`` so
  the next process lifetime re-invokes it. After ``restart()`` the
  polled response reaches ``completed``.
- **Path C** — SIGKILL mid-flight. Same recovery shape as Path B but
  with no opportunity for graceful cleanup.
"""

from __future__ import annotations

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
)


pytestmark = pytest.mark.live


@pytest.mark.asyncio
async def test_p01_path_a_natural_completion(
    make_harness: Callable[..., CrashHarness],
) -> None:
    """p01 Path A: handler completes naturally, polled GET sees completed."""
    harness = make_harness(
        shutdown_grace_seconds=LONG_GRACE_S,
    )
    await harness.start()
    try:
        body = payload("say hi briefly", background=True, store=True, stream=False)
        r = await harness.client.post("/responses", json=body)
        assert r.status_code == 200, r.text
        response_id = r.json()["id"]

        terminal = await poll_until_terminal(
            harness.client,
            response_id,
            timeout_seconds=TERMINAL_POLL_BUDGET_S,
        )
        assert terminal["status"] == "completed", terminal
    finally:
        await harness.close()


@pytest.mark.asyncio
async def test_p01_path_b_graceful_recovery(
    make_harness: Callable[..., CrashHarness],
) -> None:
    """p01 Path B: graceful-shutdown grace exhausted → recovered terminal."""
    harness = make_harness(
        shutdown_grace_seconds=SHORT_GRACE_S,
    )
    await harness.start()
    try:
        body = payload(SLOW_PROMPT, background=True, store=True, stream=False)
        r = await harness.client.post("/responses", json=body)
        assert r.status_code == 200, r.text
        response_id = r.json()["id"]

        await harness.terminate(wait_seconds=SHORT_GRACE_S + 2.0)
        await harness.restart()

        terminal = await poll_until_terminal(
            harness.client,
            response_id,
            timeout_seconds=TERMINAL_POLL_BUDGET_S,
        )
        assert terminal["status"] == "completed", terminal
    finally:
        await harness.close()


@pytest.mark.asyncio
async def test_p01_path_c_sigkill_recovery(
    make_harness: Callable[..., CrashHarness],
) -> None:
    """p01 Path C: SIGKILL mid-handler → recovered terminal."""
    import asyncio  # pylint: disable=import-outside-toplevel

    harness = make_harness(
        shutdown_grace_seconds=LONG_GRACE_S,
    )
    await harness.start()
    try:
        body = payload(SLOW_PROMPT, background=True, store=True, stream=False)
        r = await harness.client.post("/responses", json=body)
        assert r.status_code == 200, r.text
        response_id = r.json()["id"]

        # Give the handler a beat to enter the injected sleep.
        await asyncio.sleep(0.5)

        await harness.kill()
        await harness.restart()

        terminal = await poll_until_terminal(
            harness.client,
            response_id,
            timeout_seconds=TERMINAL_POLL_BUDGET_S,
        )
        assert terminal["status"] == "completed", terminal
    finally:
        await harness.close()
