# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Row 2 × Path B — ``(store=true, bg=true, resilient_bg=False)`` × ``stream=F/T``.

Path B: SIGTERM with short grace; handler still running at grace
expiry. The in-process shutdown loop at
``_endpoint_handler.py:1614-1630`` marks the response ``failed`` (with
``code=server_error``) BEFORE the subprocess exits. The reconnecting
client (in the same lifetime, before the subprocess actually exits)
sees the failed terminal.

EXPECTED today: GREEN — the in-process marker already covers this
row. Regression guard.

Contract source: ``resilience-contract.md`` § Per-row contracts → Row 2.
"""

from __future__ import annotations

from collections.abc import Callable

import pytest

from tests.e2e._crash_harness import CrashHarness
from tests.e2e.resilience_contract.conftest import (
    LONG_TIME_SECS,
    SHORT_GRACE_S,
    poll_until_terminal,
    post_and_get_response_id,
)


@pytest.mark.asyncio
@pytest.mark.parametrize("stream", [False, True], ids=["stream=False", "stream=True"])
async def test_row_2_path_b(make_harness: Callable[..., CrashHarness], stream: bool) -> None:
    """Row 2 Path B: graceful shutdown, grace exhausted, in-process marker fires."""
    harness = make_harness(
        resilient_background=False,
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
        # SIGTERM short-grace forces the in-process shutdown loop to mark
        # this row's response failed before the subprocess exits. The
        # harness's terminate() falls back to SIGKILL only if the
        # subprocess hangs past wait_seconds — that would be a framework
        # bug for row 2 Path B (shutdown loop should exit cleanly within
        # the grace window).
        await harness.terminate(wait_seconds=SHORT_GRACE_S + 5.0)

        # Subprocess has exited. Restart so the GET endpoint is available.
        await harness.restart()

        terminal = await poll_until_terminal(harness.client, response_id)
        # Row 2 Path B contract: response is ``failed`` with ``code=server_error``.
        # The error.code may currently be `server_crashed` pre-Phase-3 (the
        # rename happens in T-045); accept either to keep this test green
        # today and let Phase 3's CHANGELOG-flagged rename be the trigger
        # for tightening this assertion.
        assert terminal["status"] == "failed", terminal
        error = terminal.get("error") or {}
        assert error.get("code") in ("server_error", "server_crashed"), error
    finally:
        await harness.close()
