# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""End-to-end tests for ``samples/sample_19_resilient_streaming.py`` (Spec 040).

Spawns the real sample as a subprocess (file-backed storage) via ``CrashHarness``
and exercises the canonical framework-checkpoint recovery strategy (NO upstream
framework): the handler runs three phases (analyze → generate → refine), emits
one message item per phase, and ``stream.checkpoint()``s after each.

- **Real-time streaming** — each phase streams tokens, so the response emits many
  ``response.output_text.delta`` events (not one batched item).
- **Crash recovery** — SIGKILL mid-turn, restart; the response reaches a
  ``completed`` terminal with exactly the three phase items (recovery seeds from
  ``context.persisted_response`` and resumes at the first not-yet-checkpointed
  phase — re-emitting the SAME items with their ORIGINAL ids, never duplicating).

This is the framework-checkpoint counterpart to
``test_sample_21_langgraph_e2e.py`` (which additionally composes an external
durable engine). Unlike sample 21 it has no optional third-party deps, so it is
never skipped.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

import pytest

from tests.e2e._crash_harness import CrashHarness
from tests.e2e.resilience_contract.conftest import (
    poll_until_terminal,
    post_and_get_response_id,
    reconnect_stream_and_collect_events,
)

pytestmark = pytest.mark.skipif(
    sys.platform == "win32",
    reason="CrashHarness uses POSIX process-group signals (os.killpg)",
)

_SAMPLE = Path(__file__).resolve().parents[2] / "samples" / "sample_19_resilient_streaming.py"

# One message item per phase, in order.
_PHASE_MARKERS = ("[analyze]", "[generate]", "[refine]")


def _delta_count(events: list[dict[str, Any]]) -> int:
    return sum(1 for e in events if e.get("type") == "response.output_text.delta")


def _message_items(body: dict[str, Any]) -> list[dict[str, Any]]:
    return [it for it in (body.get("output") or []) if isinstance(it, dict) and it.get("type") == "message"]


def _all_text(body: dict[str, Any]) -> str:
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
async def test_realtime_phase_streaming(harness: CrashHarness) -> None:
    """The three phases stream token-by-token → many deltas; 3 items, completed."""
    await harness.start()
    try:
        response_id = await post_and_get_response_id(
            harness.client,
            store=True,
            background=True,
            stream=True,
            model="streamer",
            input_text="Tell me a joke",
        )
        events = await reconnect_stream_and_collect_events(harness.client, response_id, timeout_seconds=30.0)
        assert _delta_count(events) >= 3, [e.get("type") for e in events]

        terminal = await poll_until_terminal(harness.client, response_id, timeout_seconds=30.0)
        assert terminal["status"] == "completed", terminal
        assert len(_message_items(terminal)) == 3, terminal
        text = _all_text(terminal)
        for marker in _PHASE_MARKERS:
            assert marker in text, (marker, terminal)
    finally:
        await harness.close()


@pytest.mark.asyncio
async def test_crash_recovery(harness: CrashHarness) -> None:
    """SIGKILL mid-turn, restart → completed with exactly the 3 phase items.

    Recovery seeds from the last checkpoint and resumes at the first
    not-yet-checkpointed phase, so the final response has exactly three phase
    items (no duplicate from re-emission, none lost).
    """
    await harness.start()
    try:
        response_id = await post_and_get_response_id(
            harness.client,
            store=True,
            background=True,
            stream=True,
            model="streamer",
            input_text="Research fusion energy",
        )
        # Let a phase or two complete + checkpoint before crashing.
        await asyncio.sleep(0.3)

        await harness.kill()
        await harness.restart()

        terminal = await poll_until_terminal(harness.client, response_id, timeout_seconds=45.0)
        assert terminal["status"] == "completed", terminal
        assert len(_message_items(terminal)) == 3, terminal
        text = _all_text(terminal)
        for marker in _PHASE_MARKERS:
            assert marker in text, (marker, terminal)
    finally:
        await harness.close()


async def _stream_until_and_kill(harness: CrashHarness, response_id: str, *, after_item_dones: int) -> int:
    """Reconnect via GET ?stream=true; SIGKILL after N ``output_item.done`` events.

    Crashing after a phase item completes (around its ``stream.checkpoint()``)
    exercises the "committed one phase, framework snapshot maybe not yet durable"
    window deterministically rather than by wall-clock timing. Returns how many
    item-done events were observed before the kill.
    """
    import json

    terminal = {"response.completed", "response.failed", "response.cancelled"}
    seen = 0
    async with harness.client.stream(
        "GET", f"/responses/{response_id}", params={"stream": "true"}, timeout=30.0
    ) as resp:
        resp.raise_for_status()
        async for line in resp.aiter_lines():
            if not line.startswith("data:"):
                continue
            try:
                payload = json.loads(line.removeprefix("data:").strip())
            except json.JSONDecodeError:
                continue
            event_type = payload.get("type", "")
            if event_type == "response.output_item.done":
                seen += 1
                if seen >= after_item_dones:
                    await harness.kill()
                    return seen
            elif event_type in terminal:
                await harness.kill()
                return seen
    return seen


@pytest.mark.asyncio
async def test_crash_recovery_after_phase_checkpoint(harness: CrashHarness) -> None:
    """SIGKILL right after a phase item completes (around its checkpoint).

    Recovery must still finish with exactly the three phase items and all phase
    markers — the already-checkpointed phase is re-emitted with its ORIGINAL id
    and the remaining phases run.
    """
    await harness.start()
    try:
        response_id = await post_and_get_response_id(
            harness.client,
            store=True,
            background=True,
            stream=True,
            model="streamer",
            input_text="Research fusion energy deeply",
        )
        observed = await _stream_until_and_kill(harness, response_id, after_item_dones=1)
        assert observed >= 1, "never observed a phase item completing before terminal"

        await harness.restart()

        terminal = await poll_until_terminal(harness.client, response_id, timeout_seconds=45.0)
        assert terminal["status"] == "completed", terminal
        assert len(_message_items(terminal)) == 3, terminal
        text = _all_text(terminal)
        for marker in _PHASE_MARKERS:
            assert marker in text, (marker, terminal)
    finally:
        await harness.close()
