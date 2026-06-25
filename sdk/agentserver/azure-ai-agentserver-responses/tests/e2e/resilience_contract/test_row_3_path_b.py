# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Row 3 × Path B — ``(store=true, bg=false)`` × ``stream=F/T``.

Path B: SIGTERM with short grace; foreground handler still running at
grace expiry.

EXPECTED today: RED — divergence 3. The in-process shutdown loop only
covers responses currently in ``runtime_state``. Foreground responses
are not added to ``runtime_state`` until ``_finalize_stream`` runs at
terminal, so a foreground handler still mid-sleep at grace expiry has
no in-memory record for the shutdown loop to mark failed. The
``server_error`` terminal is never persisted. Phase 4 (T-060 onwards)
closes this gap by creating a bookkeeping resilient record at request
accept time for every ``store=true`` row, with a next-lifetime
recovery dispatch that marks orphan records ``failed``.

Contract source: ``resilience-contract.md`` § Per-row contracts → Row 3.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from pathlib import Path

import pytest

from tests.e2e._crash_harness import CrashHarness
from tests.e2e.resilience_contract.conftest import (
    LONG_TIME_SECS,
    SHORT_GRACE_S,
    poll_until_terminal,
    post_foreground_and_discover_id,
)


@pytest.mark.asyncio
@pytest.mark.parametrize("stream", [False, True], ids=["stream=False", "stream=True"])
async def test_row_3_path_b(
    make_harness: Callable[..., CrashHarness],
    tmp_path: Path,
    stream: bool,
) -> None:
    """Row 3 Path B: foreground graceful shutdown, in-process marked failed."""
    harness = make_harness(
        resilient_background=True,
        handler_sleep_ms=int(LONG_TIME_SECS * 1000),
        shutdown_grace_seconds=SHORT_GRACE_S,
    )
    await harness.start()
    bg_task = None
    try:
        response_id, bg_task = await post_foreground_and_discover_id(harness.client, tmp_path, stream=stream)
        # Give the handler a tick to be mid-sleep, then SIGTERM-short-grace.
        await asyncio.sleep(0.3)
        await harness.terminate(wait_seconds=SHORT_GRACE_S + 5.0)
        # Restart to get the GET endpoint up.
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
