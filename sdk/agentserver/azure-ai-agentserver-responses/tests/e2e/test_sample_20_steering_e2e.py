# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""End-to-end tests for ``samples/sample_20_resilient_steering.py`` (Spec 040).

Spawns the real sample as a subprocess (file-backed storage) via ``CrashHarness``
and exercises the steering × cancellation × recovery composition of the
**naive re-run** strategy (steerable, single message item per turn, NO framework
checkpoints — recovery re-runs the turn from scratch):

- **Real-time streaming** — the turn streams tokens → many
  ``response.output_text.delta`` events.
- **Crash recovery (naive re-run)** — SIGKILL mid-turn, restart; because nothing
  was checkpointed, the recovered attempt re-runs the whole turn and reaches
  ``completed`` with a single full message item.
- **Steering** — an overlapping second turn on the same chain is accepted (not
  ``409``); the steered successor completes and its reply reflects the new input.

This is the counterpart to ``test_sample_19_streaming_e2e.py`` (framework
checkpoints) and ``test_sample_21_langgraph_e2e.py`` (external-engine
composition). It has no optional third-party deps, so it is never skipped.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import pytest

from tests.e2e._crash_harness import CrashHarness
from tests.e2e.resilience_contract.conftest import (
    poll_until_terminal,
    post_and_get_response_id,
    reconnect_stream_and_collect_events,
)

_SAMPLE = Path(__file__).resolve().parents[2] / "samples" / "sample_20_resilient_steering.py"


def _delta_count(events: list[dict[str, Any]]) -> int:
    return sum(1 for e in events if e.get("type") == "response.output_text.delta")


def _message_items(body: dict[str, Any]) -> list[dict[str, Any]]:
    return [it for it in (body.get("output") or []) if isinstance(it, dict) and it.get("type") == "message"]


def _reply_text(body: dict[str, Any]) -> str:
    parts: list[str] = []
    for item in _message_items(body):
        for part in item.get("content") or []:
            if isinstance(part, dict) and part.get("type") == "output_text":
                parts.append(part.get("text", ""))
    return " ".join(parts)


@pytest.fixture
def harness(tmp_path: Path) -> CrashHarness:
    return CrashHarness(sample_module=_SAMPLE, tmp_path=tmp_path, readiness_timeout_seconds=30.0)


@pytest.mark.asyncio
async def test_realtime_streaming(harness: CrashHarness) -> None:
    """The turn streams token-by-token → many deltas; one item, completed."""
    await harness.start()
    try:
        response_id = await post_and_get_response_id(
            harness.client,
            store=True,
            background=True,
            stream=True,
            model="agent",
            input_text="Explain quantum computing",
        )
        events = await reconnect_stream_and_collect_events(harness.client, response_id, timeout_seconds=30.0)
        assert _delta_count(events) >= 3, [e.get("type") for e in events]

        terminal = await poll_until_terminal(harness.client, response_id, timeout_seconds=30.0)
        assert terminal["status"] == "completed", terminal
        assert len(_message_items(terminal)) == 1, terminal
        assert "quantum computing" in _reply_text(terminal).lower(), terminal
    finally:
        await harness.close()


@pytest.mark.asyncio
async def test_crash_recovery_naive_rerun(harness: CrashHarness) -> None:
    """SIGKILL mid-turn, restart → naive re-run reaches completed with a full item.

    This sample does not checkpoint partial output, so recovery re-runs the whole
    turn from scratch. The final response must have exactly one message item with
    the complete reply (no partial, no duplicate).
    """
    await harness.start()
    try:
        response_id = await post_and_get_response_id(
            harness.client,
            store=True,
            background=True,
            stream=True,
            model="agent",
            input_text="Explain relativity",
        )
        # Kill mid-stream (tokens stream at ~0.05s each).
        await asyncio.sleep(0.2)
        await harness.kill()
        await harness.restart()

        terminal = await poll_until_terminal(harness.client, response_id, timeout_seconds=45.0)
        assert terminal["status"] == "completed", terminal
        assert len(_message_items(terminal)) == 1, terminal
        assert "relativity" in _reply_text(terminal).lower(), terminal
    finally:
        await harness.close()


@pytest.mark.asyncio
async def test_steering_overlapping_turn_accepted(harness: CrashHarness) -> None:
    """An overlapping second turn on the same chain is accepted (not 409); the
    steered successor completes and its reply reflects the steered input."""
    await harness.start()
    try:
        turn1 = await post_and_get_response_id(
            harness.client,
            store=True,
            background=True,
            stream=True,
            model="agent",
            input_text="Explain quantum computing",
        )
        turn2 = await post_and_get_response_id(
            harness.client,
            store=True,
            background=True,
            stream=True,
            model="agent",
            input_text="Actually explain relativity",
            extra={"previous_response_id": turn1},
        )
        assert turn2 and turn2 != turn1

        t2 = await poll_until_terminal(harness.client, turn2, timeout_seconds=45.0)
        assert t2["status"] == "completed", t2
        assert "relativity" in _reply_text(t2).lower(), t2

        t1 = await poll_until_terminal(harness.client, turn1, timeout_seconds=45.0)
        assert t1["status"] in ("completed", "cancelled"), t1
    finally:
        await harness.close()
