# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Row 1 × Path B — ``(store=true, bg=true, resilient_bg=True)`` × ``stream=F/T``.

Path B: SIGTERM is delivered with a deliberately-short shutdown grace
period (``SHORT_GRACE_S``). The handler is still running at grace
expiry. The framework MUST hand the handler off to the resilient-task
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
  ``_start_resilient_background``; no resilient record exists for the
  streamed POST; restart has nothing to re-invoke. Phase 3 closes this.

Contract source: ``resilience-contract.md`` § Per-row contracts → Row 1.
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
async def test_row_1_path_b(make_harness: Callable[..., CrashHarness], stream: bool) -> None:
    """Row 1 Path B: graceful shutdown, grace exhausted, framework hand-off + recovery."""
    harness = make_harness(
        resilient_background=True,
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

        # Restart. Next-lifetime recovery re-invokes the resilient handler.
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


@pytest.mark.asyncio
async def test_row_1_path_b_graceful_exit_not_sigkill(
    make_harness: Callable[..., CrashHarness],
) -> None:
    """Spec 032 / B6 — Path B proves the GRACEFUL shutdown path ran, distinct
    from a Path-C SIGKILL.

    The plain Row 1 Path B test (above) accepts a SIGKILL fallback "which is
    fine — Path C is the documented fallback", and asserts only that the
    recovered terminal is ``completed`` — an assertion Path C also satisfies.
    So it does not prove the Path-B-specific in-process graceful grace-
    exhaustion handoff actually executed.

    This test gives the runtime a generous wait window (>> the short grace)
    and asserts the subprocess exited GRACEFULLY ON ITS OWN — the harness did
    NOT have to fall back to SIGKILL (``-signal.SIGKILL``). A clean exit within
    grace+margin proves the framework's shutdown loop ran the resilient handoff
    and exited, rather than being force-killed. Recovery is then verified to
    still complete (the response was NOT marked failed at grace exhaustion).
    """
    import signal as _signal

    harness = make_harness(
        resilient_background=True,
        handler_sleep_ms=int(LONG_TIME_SECS * 1000),
        shutdown_grace_seconds=SHORT_GRACE_S,
    )
    await harness.start()
    try:
        response_id = await post_and_get_response_id(
            harness.client,
            store=True,
            background=True,
            stream=False,
        )
        # Generous wait window so a graceful shutdown completes on its own;
        # only a genuine hang would trip the SIGKILL fallback.
        exit_code = await harness.terminate(wait_seconds=SHORT_GRACE_S + 8.0)
        assert exit_code is not None, "subprocess did not report an exit code"
        assert exit_code != -_signal.SIGKILL, (
            "Path B MUST shut down gracefully (resilient handoff) within grace+margin; "
            "the harness had to fall back to SIGKILL, so the graceful path did not "
            f"run (degraded to Path C). exit_code={exit_code}"
        )

        await harness.restart()
        terminal = await poll_until_terminal(harness.client, response_id, timeout_seconds=30.0)
        # Graceful Path B hands off to recovery (MUST NOT mark failed).
        assert terminal["status"] == "completed", terminal
    finally:
        await harness.close()
