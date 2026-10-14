# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Row 2 × Path C — stored background with resilient tasks disabled.

Path C: SIGKILL mid-handler — the in-process marker cannot run. Because the
core switch is disabled, no task manager or next-lifetime recovery scan runs;
the last persisted response remains ``in_progress``.

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
    post_and_get_response_id,
)


@pytest.mark.asyncio
@pytest.mark.parametrize("stream", [False, True], ids=["stream=False", "stream=True"])
async def test_row_2_path_c(make_harness: Callable[..., CrashHarness], stream: bool) -> None:
    """Row 2 Path C: SIGKILL leaves the stored response in progress."""
    harness = make_harness(
        resilient_tasks_enabled=False,
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

        await asyncio.sleep(0.5)
        response = await harness.client.get(f"/responses/{response_id}")
        assert response.status_code == 200, response.text
        assert response.json()["status"] == "in_progress", response.json()
    finally:
        await harness.close()
