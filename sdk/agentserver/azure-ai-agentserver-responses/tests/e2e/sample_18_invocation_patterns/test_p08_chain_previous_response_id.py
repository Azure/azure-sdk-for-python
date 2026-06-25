# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 18 invocation pattern p08 — multi-turn chain via previous_response_id.

Pattern: multi-turn conversation chained via ``previous_response_id``.
Each turn references the prior turn's id; the framework derives a stable
``context.conversation_chain_id`` from the chain so sample 18's Copilot
session id is the same across all turns. Crash recovery during turn 2
must preserve the chain — turn 3 still chains correctly post-recovery.

Exercised under Row 1 (resilient+bg+stream=True) to confirm the resilient
streaming path preserves chain semantics through recovery.

Coverage:

- Turn 1: fresh POST, capture response_id (R1).
- Turn 2: POST with previous_response_id=R1, capture R2.
- Crash mid-turn-2 (SIGKILL Path C), restart, poll R2 to terminal.
- Turn 3: POST with previous_response_id=R2 (which is now the recovered
  terminal). Confirm the chain still resolves to the same upstream
  Copilot session.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable

import pytest

from tests.e2e._crash_harness import CrashHarness
from tests.e2e.sample_18_invocation_patterns.conftest import (
    LONG_GRACE_S,
    TERMINAL_POLL_BUDGET_S,
    payload,
    poll_until_terminal,
    post_and_get_response_id,
)

pytestmark = pytest.mark.live


@pytest.mark.asyncio
async def test_p08_chain_preserves_across_recovery(
    make_harness: Callable[..., CrashHarness],
) -> None:
    """Three-turn chain with a crash mid-turn-2; the chain survives."""
    harness = make_harness(
        shutdown_grace_seconds=LONG_GRACE_S,
    )
    await harness.start()
    try:
        # ── Turn 1: fresh chain head ─────────────────────────────────
        r1 = await post_and_get_response_id(
            harness.client,
            store=True,
            background=True,
            stream=True,
            model="copilot",
            input_text="Pick a colour. Just one word.",
        )
        t1 = await poll_until_terminal(
            harness.client,
            r1,
            timeout_seconds=TERMINAL_POLL_BUDGET_S,
        )
        assert t1["status"] == "completed", t1

        # ── Turn 2: chain via previous_response_id; crash mid-handler ─
        body2 = payload(
            "What colour did I pick?",
            background=True,
            store=True,
            stream=True,
            previous_response_id=r1,
        )
        r2 = await post_and_get_response_id(
            harness.client,
            store=True,
            background=True,
            stream=True,
            model="copilot",
            input_text="What colour did I pick?",
            extra={"previous_response_id": r1},
        )
        _ = body2  # body shape doc-check; actual POST uses helper above

        await asyncio.sleep(0.5)
        await harness.kill()
        await harness.restart()

        t2 = await poll_until_terminal(
            harness.client,
            r2,
            timeout_seconds=TERMINAL_POLL_BUDGET_S,
        )
        assert t2["status"] == "completed", t2

        # ── Turn 3: chain via R2 (recovered) ──────────────────────────
        r3 = await post_and_get_response_id(
            harness.client,
            store=True,
            background=True,
            stream=True,
            model="copilot",
            input_text="Confirm you remember.",
            extra={"previous_response_id": r2},
        )
        t3 = await poll_until_terminal(
            harness.client,
            r3,
            timeout_seconds=TERMINAL_POLL_BUDGET_S,
        )
        assert t3["status"] == "completed", t3

        # Sanity: all three responses share the same conversation chain.
        # The framework derives conversation_chain_id from the chain;
        # if turn 3 successfully resolves and reaches Copilot through
        # the same upstream session, the chain is intact. We can only
        # check the contract surface (response objects), not the
        # upstream session id directly — the conformance side
        # ``test_conversation_chain_id.py`` covers the derivation rule.
        assert str(t1["id"]) == r1
        assert str(t2["id"]) == r2
        assert str(t3["id"]) == r3
    finally:
        await harness.close()
