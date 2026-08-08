# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""End-to-end tests for ``samples/sample_22_resilient_multiturn.py`` (Spec 040).

Spawns the real sample as a subprocess (file-backed storage) via ``CrashHarness``
and exercises the serial multi-turn conversation (``steerable_conversations=False``,
``TextResponse``, no external LLM): each turn references prior context via
``previous_response_id`` and ``"done"`` ends the session.

- **Multi-turn** — turn 1 → turn 2 (via ``previous_response_id``) accumulates
  conversation history; ``"done"`` terminates cleanly.
- **Crash across turns** — after turn 1 completes, SIGKILL + restart; turn 2 on
  the same chain still sees the prior conversation history (the framework history
  store survives the crash).

This sample is near-instantaneous per turn (no artificial delays), so it is not a
good target for *mid-turn* crash injection; the meaningful resilience property is
that cross-turn state survives a process restart, which these tests pin.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

from tests.e2e._crash_harness import CrashHarness
from tests.e2e.resilience_contract.conftest import (
    poll_until_terminal,
    post_and_get_response_id,
)

pytestmark = pytest.mark.skipif(
    sys.platform == "win32",
    reason="CrashHarness uses POSIX process-group signals (os.killpg)",
)

_SAMPLE = Path(__file__).resolve().parents[2] / "samples" / "sample_22_resilient_multiturn.py"


def _reply_text(body: dict[str, Any]) -> str:
    parts: list[str] = []
    for item in body.get("output") or []:
        if isinstance(item, dict) and item.get("type") == "message":
            for part in item.get("content") or []:
                if isinstance(part, dict) and part.get("type") == "output_text":
                    parts.append(part.get("text", ""))
    return " ".join(parts)


async def _run_turn(harness: CrashHarness, text: str, previous: str | None = None) -> dict[str, Any]:
    extra = {"previous_response_id": previous} if previous else None
    rid = await post_and_get_response_id(
        harness.client,
        store=True,
        background=True,
        stream=False,
        model="chat",
        input_text=text,
        extra=extra,
    )
    return await poll_until_terminal(harness.client, rid, timeout_seconds=30.0)


@pytest.fixture
def harness(tmp_path: Path) -> CrashHarness:
    return CrashHarness(sample_module=_SAMPLE, tmp_path=tmp_path, readiness_timeout_seconds=30.0)


@pytest.mark.asyncio
async def test_multiturn_context_accumulates(harness: CrashHarness) -> None:
    """Sequential turns thread conversation context via previous_response_id;
    'done' ends the session cleanly.

    Note: this pins the reliable resilience property — conversation *history*
    accumulates across turns (the sample reports a growing context-item count).
    It intentionally does NOT assert on the ``turn_count`` watermark: cross-turn
    ``conversation_chain_metadata`` propagation for non-steerable serial chains is
    a separate, pre-existing behavior outside this sample's headline guarantee.
    """
    await harness.start()
    try:
        t1 = await _run_turn(harness, "My name is Alice")
        assert t1["status"] == "completed", t1
        assert "my name is alice" in _reply_text(t1).lower(), t1

        t2 = await _run_turn(harness, "What is my name?", previous=t1["id"])
        assert t2["status"] == "completed", t2
        r2 = _reply_text(t2).lower()
        assert "what is my name?" in r2, t2
        # History accumulated → the sample reports a non-zero context item count.
        assert "0 items" not in r2, t2

        done = await _run_turn(harness, "done", previous=t2["id"])
        assert done["status"] == "completed", done
        assert "done" in _reply_text(done).lower(), done
    finally:
        await harness.close()


@pytest.mark.asyncio
async def test_conversation_context_survives_crash(harness: CrashHarness) -> None:
    """After turn 1 completes, SIGKILL + restart → turn 2 on the same chain still
    sees the accumulated conversation history (framework store survives the crash)."""
    await harness.start()
    try:
        t1 = await _run_turn(harness, "My name is Alice")
        assert t1["status"] == "completed", t1

        # Crash AFTER turn 1 is terminal, then restart (cross-lifetime state test).
        await harness.kill()
        await harness.restart()

        t2 = await _run_turn(harness, "What is my name?", previous=t1["id"])
        assert t2["status"] == "completed", t2
        r2 = _reply_text(t2).lower()
        # History is still present after the restart.
        assert "what is my name?" in r2, t2
        assert "0 items" not in r2, t2
    finally:
        await harness.close()
