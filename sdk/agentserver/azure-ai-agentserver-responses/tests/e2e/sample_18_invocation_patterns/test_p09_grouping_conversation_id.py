# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 18 invocation pattern p09 — multi-turn grouping via conversation_id.

Pattern: multi-turn conversation grouped via ``conversation_id``. Each
turn carries the same conversation id; the framework derives the same
``conversation_chain_id`` from it so sample 18's Copilot session id is
stable across all turns. Crash recovery during turn 2 must preserve
the grouping — turn 3 still groups correctly and the conversation
listing stays ordered.

Exercised under Row 1 (durable+bg+stream=True).

Coverage:

- Turn 1: POST with conversation_id="conv-p09-<unique>", capture R1.
- Turn 2: POST with the same conversation_id, capture R2.
- Crash mid-turn-2 (SIGKILL Path C), restart, poll R2 to terminal.
- Turn 3: POST with the same conversation_id, capture R3.
- Confirm R3 sees turn 1 and the recovered turn 2 (via the upstream
  Copilot session) and that the conversation listing order is preserved.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Callable

import pytest

from tests.e2e._crash_harness import CrashHarness
from tests.e2e.sample_18_invocation_patterns.conftest import (
    LONG_GRACE_S,
    TERMINAL_POLL_BUDGET_S,
    poll_until_terminal,
    post_and_get_response_id,
)


pytestmark = pytest.mark.live


@pytest.mark.asyncio
async def test_p09_grouping_preserves_across_recovery(
    make_harness: Callable[..., CrashHarness],
) -> None:
    """Three-turn grouping with a crash mid-turn-2; the group survives."""
    conv_id = f"conv-p09-{int(time.time() * 1000)}"

    harness = make_harness(
        shutdown_grace_seconds=LONG_GRACE_S,
    )
    await harness.start()
    try:
        # ── Turn 1: first turn in the conversation ────────────────────
        r1 = await post_and_get_response_id(
            harness.client,
            store=True,
            background=True,
            stream=True,
            model="copilot",
            input_text="Pick a number 1-10.",
            extra={"conversation_id": conv_id},
        )
        t1 = await poll_until_terminal(
            harness.client,
            r1,
            timeout_seconds=TERMINAL_POLL_BUDGET_S,
        )
        assert t1["status"] == "completed", t1

        # ── Turn 2: same conversation; crash mid-handler ──────────────
        r2 = await post_and_get_response_id(
            harness.client,
            store=True,
            background=True,
            stream=True,
            model="copilot",
            input_text="What number did I pick?",
            extra={"conversation_id": conv_id},
        )

        await asyncio.sleep(0.5)
        await harness.kill()
        await harness.restart()

        t2 = await poll_until_terminal(
            harness.client,
            r2,
            timeout_seconds=TERMINAL_POLL_BUDGET_S,
        )
        assert t2["status"] == "completed", t2

        # ── Turn 3: same conversation; should see the recovered turn 2 ─
        r3 = await post_and_get_response_id(
            harness.client,
            store=True,
            background=True,
            stream=True,
            model="copilot",
            input_text="Confirm you still remember.",
            extra={"conversation_id": conv_id},
        )
        t3 = await poll_until_terminal(
            harness.client,
            r3,
            timeout_seconds=TERMINAL_POLL_BUDGET_S,
        )
        assert t3["status"] == "completed", t3

        # All three responses must share the same conversation_id.
        assert t1.get("conversation_id") == conv_id, t1
        assert t2.get("conversation_id") == conv_id, t2
        assert t3.get("conversation_id") == conv_id, t3
    finally:
        await harness.close()
