# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Row 1 × Path C with SSE keep-alive ENABLED — resilience must not depend on
whether the platform enables keep-alive.

Background: on hosted, the platform enables SSE keep-alive by injecting the
``SSE_KEEPALIVE_INTERVAL`` environment variable. The streaming orchestrator
(:meth:`_ResponseOrchestrator._live_stream`) used to create the resilient task
ONLY on its non-keep-alive code path; with keep-alive enabled it ran the
handler inline and never created a resilient task. Stored background responses
therefore ran connection-scoped: they hung ``in_progress`` when the client /
proxy dropped the SSE connection and the recovery scan found no task to
reclaim. The default-off keep-alive in the rest of the conformance suite hid
the bug.

This module pins the contract: Row 1 (``store=true, bg=true,
resilient_bg=True``) MUST create a resilient task and recover after a crash
(Path C) **regardless of keep-alive**. It mirrors ``test_row_1_path_c`` but
runs with keep-alive on.

Expected on the BUGGED orchestrator: RED — no resilient task is created under
keep-alive, so recovery never happens and ``poll_until_terminal`` times out.
Expected on the FIXED orchestrator: GREEN — the resilient task is created, the
recovered lifetime (``L1``) completes, and keep-alive comments are interleaved
into the wire stream.

Contract source: ``resilience-contract.md`` § Per-row contracts → Row 1.
Constitution: Principle X (Resilience Contract Conformance), Principle XI
(Contract-Surface Test Depth).
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


def _final_text_from_snapshot(snapshot: dict) -> str:
    """Extract the assembled ``output[0].content[0].text`` from a response snapshot."""
    output = snapshot.get("output") or []
    assert output, f"snapshot has empty output: {snapshot!r}"
    contents = output[0].get("content") or []
    assert contents, f"output item has no content: {output[0]!r}"
    return contents[0].get("text", "")


@pytest.mark.asyncio
@pytest.mark.parametrize("stream", [False, True], ids=["stream=False", "stream=True"])
async def test_row_1_keep_alive_path_c(make_harness: Callable[..., CrashHarness], stream: bool) -> None:
    """Row 1 Path C with keep-alive ON: SIGKILL mid-handler, restart, recover, completed.

    The recovered lifetime (``L1``) MUST produce the terminal content — a
    status-only assertion would pass for any path that reaches ``completed``;
    asserting ``L1_done`` proves the resilient task was created and recovered
    under keep-alive (Principle XI depth).
    """
    harness = make_harness(
        resilient_background=True,
        handler_sleep_ms=int(LONG_TIME_SECS * 1000),
        shutdown_grace_seconds=LONG_GRACE_S,
        keep_alive_seconds=1,  # <-- the hosted condition the suite otherwise never exercises
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
        # Path C for Row 1 is recovery (NOT marked-failed): a resilient task was
        # created under keep-alive and the recovered handler reached terminal.
        assert terminal["status"] == "completed", terminal
        # Depth (Principle XI): the recovered lifetime produced the content.
        final_text = _final_text_from_snapshot(terminal)
        assert final_text.startswith("L1_done"), final_text
    finally:
        await harness.close()
