# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Row 3 × Path C — ``(store=true, bg=false)`` × switch state × ``stream=F/T``.

Path C: SIGKILL mid-handler — no in-process marker runs.

- Switch enabled: foreground execution has a durable ``mark-failed`` record;
  restart persists ``failed`` with ``code=server_error``.
- Switch disabled: no manager or scanner exists; restart leaves the persisted
  response ``in_progress``.

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
        resilient_tasks_enabled=True,
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


@pytest.mark.asyncio
@pytest.mark.parametrize("stream", [False, True], ids=["stream=False", "stream=True"])
async def test_row_3_path_c_switch_disabled_remains_in_progress(
    make_harness: Callable[..., CrashHarness],
    tmp_path: Path,
    stream: bool,
) -> None:
    """SIGKILL with the switch disabled leaves stored foreground state in progress."""
    harness = make_harness(
        resilient_tasks_enabled=False,
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

        # Startup recovery is immediate when a manager exists. Waiting longer
        # than the original handler duration proves no delayed scanner changes
        # the persisted switch-disabled state.
        await asyncio.sleep(LONG_TIME_SECS + 1.0)
        response = await harness.client.get(f"/responses/{response_id}")
        assert response.status_code == 200, response.text
        assert response.json()["status"] == "in_progress", response.json()
    finally:
        if bg_task is not None:
            bg_task.cancel()
            try:
                await bg_task
            except (asyncio.CancelledError, Exception):  # noqa: BLE001
                pass
        await harness.close()
