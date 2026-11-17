# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Row 1 × Path C — ``(store=true, bg=true, resilient_bg=True)`` × ``stream=F/T``.

Path C: SIGKILL mid-handler — no in-process action runs. On the next
process lifetime, the resilient-task primitive's recovery re-invokes the
handler with ``entry_mode="recovered"`` and reaches terminal.

For ``stream=False`` (polled): the reconnecting client GETs the
response and observes the recovered terminal.

For ``stream=True`` (the divergence-1 closure side): a reconnecting
client at ``GET /responses/{id}?stream=true&starting_after=N`` MUST
see a ``response.in_progress`` reset event followed by continuation
and a coherent terminal.

EXPECTED today:

- ``stream=False``: GREEN — Spec 013's cross-process reconstruction
  delivers row-1 polled recovery.
- ``stream=True``: **RED — divergence 1.** Same root cause as Path B:
  no resilient record exists for the streamed POST. Phase 3 closes this.

Contract source: ``resilience-contract.md`` § Per-row contracts → Row 1.
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
@pytest.mark.parametrize("stream", [False, True], ids=["stream=False", "stream=True"])
async def test_row_1_path_c(make_harness: Callable[..., CrashHarness], stream: bool) -> None:
    """Row 1 Path C: SIGKILL mid-handler, restart, handler re-invoked, terminal reached."""
    harness = make_harness(
        resilient_background=True,
        handler_sleep_ms=int(LONG_TIME_SECS * 1000),
        # Long grace just to make clear the SIGKILL is what ends things,
        # not grace exhaustion.
        shutdown_grace_seconds=LONG_GRACE_S,
    )
    await harness.start()
    try:
        response_id = await post_and_get_response_id(
            harness.client,
            store=True,
            background=True,
            stream=stream,
        )
        # Give the handler a beat to start its sleep before SIGKILL.
        await asyncio.sleep(0.5)

        await harness.kill()
        await harness.restart()

        terminal = await poll_until_terminal(
            harness.client,
            response_id,
            timeout_seconds=30.0,
        )
        # Recovered terminal must be a real completion (Path C for row 1
        # = recovery, NOT marked-failed).
        assert terminal["status"] == "completed", terminal
    finally:
        await harness.close()
