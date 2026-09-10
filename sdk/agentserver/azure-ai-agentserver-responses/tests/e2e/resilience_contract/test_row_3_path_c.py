# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Row 3 × Path C — ``(store=true, bg=false)`` × ``stream=F/T``.

Path C: SIGKILL mid-handler — no in-process marker runs. On the next
process lifetime, the framework MUST mark the response ``failed``
(``code=server_error``) so a subsequent ``GET /responses/{saved_id}``
returns the failed terminal — NOT ``in_progress`` indefinitely.

EXPECTED today: **RED — divergence 3.** ``run_sync`` never calls
``_start_resilient_background``; no resilient record is created for
foreground responses; SIGKILL leaves the response ``in_progress`` with
nothing on the restart side to mark it failed.

Phase 4 closes this by creating a bookkeeping resilient record for every
``store=true`` response (per RD-1) with disposition ``mark-failed``.

Contract source: ``resilience-contract.md`` § Per-row contracts → Row 3.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from pathlib import Path

import pytest

from tests.e2e._crash_harness import CrashHarness
from tests.e2e.resilience_contract.conftest import (
    LONG_GRACE_S,
    LONG_TIME_SECS,
    poll_until_terminal,
    post_foreground_and_discover_id,
)


@pytest.mark.asyncio
@pytest.mark.parametrize("stream", [False, True], ids=["stream=False", "stream=True"])
async def test_row_3_path_c(
    make_harness: Callable[..., CrashHarness],
    tmp_path: Path,
    stream: bool,
) -> None:
    """Row 3 Path C: SIGKILL mid-foreground-handler, restart, marked failed."""
    harness = make_harness(
        resilient_background=True,
        handler_sleep_ms=int(LONG_TIME_SECS * 1000),
        shutdown_grace_seconds=LONG_GRACE_S,
    )
    await harness.start()
    bg_task = None
    try:
        response_id, bg_task = await post_foreground_and_discover_id(harness.client, tmp_path, stream=stream)
        await asyncio.sleep(0.5)
        await harness.kill()
        await harness.restart()

        terminal = await poll_until_terminal(harness.client, response_id)
        assert terminal["status"] == "failed", terminal
        error = terminal.get("error") or {}
        assert error.get("code") in ("server_error", "server_crashed"), error
    finally:
        if bg_task is not None:
            bg_task.cancel()
            try:
                await bg_task
            except (asyncio.CancelledError, Exception):  # noqa: BLE001
                pass
        await harness.close()
