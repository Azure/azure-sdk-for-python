# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Row 1 × Path B — ``(store=true, bg=true, durable_bg=True)`` × ``stream=F/T``.

Path B: SIGTERM is delivered with a deliberately-short shutdown grace
period (``SHORT_GRACE_S``). The handler is still running at grace
expiry. The framework MUST hand the handler off to the durable-task
primitive's recovery (it MUST NOT mark the response failed); on the
next process lifetime, the handler is re-invoked with
``entry_mode="recovered"`` and reaches terminal.

For ``stream=False`` (polled): the reconnecting client GETs the
response and observes the recovered terminal.

For ``stream=True`` (the divergence-1 closure side): a reconnecting
client at ``GET /responses/{id}?stream=true&starting_after=N`` MUST
see a ``response.in_progress`` reset event followed by continuation
and a coherent terminal.

EXPECTED today:

- ``stream=False``: GREEN — Spec 013's cross-process reconstruction
  already covers the polled case for row 1.
- ``stream=True``: **RED — divergence 1.** ``run_stream`` never engages
  ``_start_durable_background``; no durable record exists for the
  streamed POST; restart has nothing to re-invoke. Phase 3 closes this.

Contract source: ``durability-contract.md`` § Per-row contracts → Row 1.
"""

from __future__ import annotations

from collections.abc import Callable

import pytest

from tests.e2e._crash_harness import CrashHarness
from tests.e2e.durability_contract.conftest import (
    LONG_TIME_SECS,
    SHORT_GRACE_S,
    poll_until_terminal,
    post_and_get_response_id,
)


@pytest.mark.asyncio
@pytest.mark.parametrize("stream", [False, True], ids=["stream=False", "stream=True"])
async def test_row_1_path_b(make_harness: Callable[..., CrashHarness], stream: bool) -> None:
    """Row 1 Path B: graceful shutdown, grace exhausted, framework hand-off + recovery."""
    harness = make_harness(
        durable_background=True,
        handler_sleep_ms=int(LONG_TIME_SECS * 1000),
        shutdown_grace_seconds=SHORT_GRACE_S,
    )
    await harness.start()
    try:
        response_id = await post_and_get_response_id(
            harness.client,
            store=True,
            background=True,
            stream=stream,
        )
        # Subprocess is now mid-handler. SIGTERM with short grace forces
        # Path B. The harness's terminate() waits for clean exit; if the
        # subprocess doesn't exit within wait_seconds, it falls back to
        # SIGKILL (which is fine — Path C is the documented fallback for
        # Path B failure).
        await harness.terminate(wait_seconds=SHORT_GRACE_S + 2.0)

        # Restart. Next-lifetime recovery re-invokes the durable handler.
        await harness.restart()

        terminal = await poll_until_terminal(
            harness.client,
            response_id,
            timeout_seconds=30.0,
        )
        # Recovered terminal must be a real completion (Path B for row 1
        # = recovery, NOT marked-failed).
        assert terminal["status"] == "completed", terminal
    finally:
        await harness.close()
