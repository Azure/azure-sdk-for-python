# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Spec 025 §A.4 — explicit ``await context.exit_for_recovery()`` recovery.

The unified recovery primitive raises ``ResponseExitForRecovery``
(a ``BaseException``) inside the handler. The resilient orchestrator catches
it at the task boundary and translates it to next-lifetime recovery — the
SAME disposition as the implicit bare-``return``-on-shutdown fallback, but
via the explicit developer-facing idiom that works in every handler shape.

This is the Row-1 Path-B flow (grace exhausted mid-handler) with the
handler's shutdown branch set to call ``await context.exit_for_recovery()``
explicitly (``CONFORMANCE_EXPLICIT_EXIT_FOR_RECOVERY=true``). The response
MUST recover to a real ``completed`` terminal after restart — proving the
``BaseException`` propagates cleanly (is NOT swallowed by the orchestrator's
``except Exception`` guards) and the translation leaves the response
``in_progress`` for the recovery scanner rather than marking it failed.

Contract source: ``resilience-contract.md`` § Per-row contracts → Row 1
(Path B), unified-recovery clause (Spec 025 §A.4).
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
async def test_explicit_exit_for_recovery_recovers(make_harness: Callable[..., CrashHarness], stream: bool) -> None:
    """Explicit ``await context.exit_for_recovery()`` → next-lifetime recovery."""
    harness = make_harness(
        resilient_background=True,
        handler_sleep_ms=int(LONG_TIME_SECS * 1000),
        shutdown_grace_seconds=SHORT_GRACE_S,
        explicit_exit_for_recovery=True,
    )
    await harness.start()
    try:
        response_id = await post_and_get_response_id(
            harness.client,
            store=True,
            background=True,
            stream=stream,
        )
        # SIGTERM with short grace: handler is mid-sleep, its shutdown
        # branch fires `await context.exit_for_recovery()`.
        await harness.terminate(wait_seconds=SHORT_GRACE_S + 2.0)

        # Restart: next-lifetime recovery re-invokes the resilient handler.
        await harness.restart()

        terminal = await poll_until_terminal(
            harness.client,
            response_id,
            timeout_seconds=30.0,
        )
        # The recovery signal must NOT mark the response failed: it must
        # recover to a real completion.
        assert terminal["status"] == "completed", terminal
    finally:
        await harness.close()
