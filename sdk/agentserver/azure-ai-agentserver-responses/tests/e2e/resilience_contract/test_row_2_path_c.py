# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Row 2 × Path C — ``(store=true, bg=true, resilient_bg=False)`` × ``stream=F/T``.

Path C: SIGKILL mid-handler — the in-process marker doesn't run. On
the next process lifetime, the framework MUST mark the response
``failed`` (with ``code=server_error``) via the resilient-task primitive's
next-lifetime recovery. The reconnecting client sees the failed
terminal — NOT ``in_progress`` indefinitely.

EXPECTED today: **RED — divergence 2.** ``_orchestrator.py:2273`` gates
``_start_resilient_background`` on ``resilient_background AND store``. With
``resilient_background=False`` no resilient record is created; next-lifetime
recovery finds nothing for the response; nothing marks it failed.
The response stays ``in_progress`` indefinitely.

Phase 4 closes this by creating a bookkeeping resilient record for every
``store=true`` response (per RD-1) with disposition ``mark-failed``.

Contract source: ``resilience-contract.md`` § Per-row contracts → Row 2.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable

import pytest

from tests.e2e._crash_harness import CrashHarness
from tests.e2e.resilience_contract.conftest import (
    LONG_GRACE_S,
    LONG_TIME_SECS,
    poll_until_output_count,
    poll_until_terminal,
    post_and_get_response_id,
)


@pytest.mark.asyncio
@pytest.mark.parametrize("stream", [False, True], ids=["stream=False", "stream=True"])
async def test_row_2_path_c(make_harness: Callable[..., CrashHarness], stream: bool) -> None:
    """Row 2 Path C: SIGKILL mid-handler, restart, response marked failed."""
    harness = make_harness(
        resilient_background=False,
        handler_sleep_ms=int(LONG_TIME_SECS * 1000),
        pre_sleep_deltas=1 if stream else 0,
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
        if stream:
            await poll_until_output_count(harness.client, response_id, 1)
        else:
            await asyncio.sleep(0.5)
        await harness.kill()
        await harness.restart()

        terminal = await poll_until_terminal(harness.client, response_id)
        assert terminal["status"] == "failed", terminal
        error = terminal.get("error") or {}
        assert error.get("code") in ("server_error", "server_crashed"), error
    finally:
        await harness.close()
