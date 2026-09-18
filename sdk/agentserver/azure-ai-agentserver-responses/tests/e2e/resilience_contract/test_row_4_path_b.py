# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Row 4 × Path B — ``(store=false, ...)`` × ``stream=F/T`` × ``background=F/T``.

Path B: SIGTERM with short grace. Best-effort marker fires on the open
connection (if any). The contract is "best-effort during shutdown grace
period." Test asserts the subprocess exits cleanly within the grace
window and does NOT hang past it.

EXPECTED: GREEN today; regression guard.

Contract source: ``resilience-contract.md`` § Per-row contracts → Row 4.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable

import pytest

from tests.e2e._crash_harness import CrashHarness
from tests.e2e.resilience_contract.conftest import (
    LONG_TIME_SECS,
    SHORT_GRACE_S,
)


@pytest.mark.asyncio
@pytest.mark.parametrize("stream", [False, True], ids=["stream=False", "stream=True"])
async def test_row_4_path_b(
    make_harness: Callable[..., CrashHarness],
    stream: bool,
) -> None:
    """Row 4 Path B: store=false best-effort shutdown marker; clean exit within grace.

    ``background`` parametrize dropped: ``(store=false, background=true)``
    is rejected with HTTP 400. Row 4 is exercised with ``background=False``
    only.
    """
    harness = make_harness(
        resilient_background=False,
        handler_sleep_ms=int(LONG_TIME_SECS * 1000),
        shutdown_grace_seconds=SHORT_GRACE_S,
    )
    await harness.start()
    bg_task = None
    try:
        body = {
            "model": "conformance-test",
            "input": "hello",
            "store": False,
            "background": False,
            "stream": stream,
        }

        # Fire the POST in the background — for bg=False the POST blocks
        # until terminal (which won't happen because we're going to
        # SIGTERM). For bg=True the POST returns quickly and the
        # connection closes; the handler keeps running in-process.
        async def _fire() -> None:
            try:
                if stream:
                    async with harness.client.stream("POST", "/responses", json=body, timeout=15.0) as resp:
                        async for _ in resp.aiter_lines():
                            pass
                else:
                    await harness.client.post("/responses", json=body, timeout=15.0)
            except Exception:  # pylint: disable=broad-exception-caught
                # Connection severed by SIGTERM is expected.
                pass

        bg_task = asyncio.create_task(_fire())
        await asyncio.sleep(0.3)

        # SIGTERM-short-grace. The framework's best-effort marker runs
        # in-process; the subprocess MUST exit within a reasonable
        # window (SHORT_GRACE_S + small slack) — if it hangs past
        # wait_seconds, the harness falls back to SIGKILL and the test
        # has surfaced a bug.
        exit_code = await harness.terminate(wait_seconds=SHORT_GRACE_S + 3.0)
        # If exit_code is None, the SIGKILL fallback ran — the subprocess
        # hung past grace. That's a regression for row 4.
        assert exit_code is not None, (
            "Row 4 Path B: subprocess hung past SHORT_GRACE_S + slack; "
            "best-effort shutdown loop did not exit cleanly within grace"
        )
    finally:
        if bg_task is not None:
            bg_task.cancel()
            try:
                await bg_task
            except (asyncio.CancelledError, Exception):  # noqa: BLE001
                pass
        await harness.close()
