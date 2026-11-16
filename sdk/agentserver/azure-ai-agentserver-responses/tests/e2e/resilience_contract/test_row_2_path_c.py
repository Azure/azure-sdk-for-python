# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Row 2 × Path C — ``(store=true, bg=true, resilient_bg=False)`` × ``stream=F/T``.

Path C: SIGKILL mid-handler — the in-process marker doesn't run. On
the next process lifetime, the framework MUST mark the response
``failed`` (with ``code=server_error``) via the resilient-task primitive's
next-lifetime recovery. The reconnecting client sees the failed
terminal — NOT ``in_progress`` indefinitely.

With steering enabled this flag-off response has a durable task runtime.
With both Responses features disabled, no recovery scanner runs instead.

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
@pytest.mark.parametrize("steerable", [False, True], ids=["runtime-off", "steering-runtime"])
async def test_row_2_path_c(make_harness: Callable[..., CrashHarness], stream: bool, steerable: bool) -> None:
    """Only a feature-enabled task runtime marks an interrupted response failed."""
    harness = make_harness(
        resilient_background=False,
        steerable_conversations=steerable,
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

        if steerable:
            terminal = await poll_until_terminal(harness.client, response_id)
            assert terminal["status"] == "failed", terminal
            error = terminal.get("error") or {}
            assert error.get("code") in ("server_error", "server_crashed"), error
        else:
            await asyncio.sleep(LONG_TIME_SECS + 1)
            response = await harness.client.get(f"/responses/{response_id}")
            assert response.status_code == 200, response.text
            assert response.json()["status"] == "in_progress", response.text
    finally:
        await harness.close()
