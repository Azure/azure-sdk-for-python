# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""End-to-end tests for ``samples/sample_21_resilient_langgraph.py`` (Spec 040).

Spawns the real sample as a subprocess (file-backed storage) via ``CrashHarness``
and exercises the three headline capabilities the sample showcases:

- **Real-time token streaming** — the ``generate_response`` node streams tokens
  one at a time, so the response emits many ``response.output_text.delta`` events
  (not one batched item).
- **Crash recovery** — SIGKILL mid-turn, restart; the response reaches a
  ``completed`` terminal with its reply (framework checkpoint + LangGraph
  ``AsyncSqliteSaver`` compose so recovery re-emits the reply, never inventing
  ids).
- **Steering** — an overlapping second turn on the same conversation chain is
  accepted (not ``409``) and reaches terminal (``steerable_conversations=True``).

Gated on the sample's optional third-party deps (``langgraph`` / ``aiosqlite`` /
``AsyncSqliteSaver``); skipped when they are not installed.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

import pytest

pytest.importorskip("langgraph", reason="langgraph required for sample 21 e2e")
pytest.importorskip("aiosqlite", reason="aiosqlite required for sample 21 e2e")
pytest.importorskip("langgraph.checkpoint.sqlite.aio", reason="AsyncSqliteSaver required for sample 21 e2e")

from tests.e2e._crash_harness import CrashHarness  # noqa: E402
from tests.e2e.resilience_contract.conftest import (  # noqa: E402
    poll_until_terminal,
    post_and_get_response_id,
    reconnect_stream_and_collect_events,
)

pytestmark = pytest.mark.skipif(
    sys.platform == "win32",
    reason="CrashHarness uses POSIX process-group signals (os.killpg)",
)

_SAMPLE = Path(__file__).resolve().parents[2] / "samples" / "sample_21_resilient_langgraph.py"


def _delta_count(events: list[dict[str, Any]]) -> int:
    return sum(1 for e in events if e.get("type") == "response.output_text.delta")


def _reply_text(body: dict[str, Any]) -> str:
    parts: list[str] = []
    for item in body.get("output") or []:
        if isinstance(item, dict) and item.get("type") == "message":
            for part in item.get("content") or []:
                if isinstance(part, dict) and part.get("type") == "output_text":
                    parts.append(part.get("text", ""))
    return " ".join(parts)


def _message_items(body: dict[str, Any]) -> list[dict[str, Any]]:
    return [it for it in (body.get("output") or []) if isinstance(it, dict) and it.get("type") == "message"]


@pytest.fixture
def harness(tmp_path: Path) -> CrashHarness:
    return CrashHarness(sample_module=_SAMPLE, tmp_path=tmp_path, readiness_timeout_seconds=30.0)


@pytest.mark.asyncio
async def test_realtime_token_streaming(harness: CrashHarness) -> None:
    """The reply streams token-by-token → many delta events, terminal completed."""
    await harness.start()
    try:
        response_id = await post_and_get_response_id(
            harness.client,
            store=True,
            background=True,
            stream=True,
            model="langgraph",
            input_text="Research quantum computing",
        )
        events = await reconnect_stream_and_collect_events(harness.client, response_id, timeout_seconds=30.0)

        # Real-time streaming: the generate node emits one token at a time, so
        # the reply must arrive as MANY deltas (not a single batched item).
        assert _delta_count(events) >= 3, [e.get("type") for e in events]

        terminal = await poll_until_terminal(harness.client, response_id, timeout_seconds=30.0)
        assert terminal["status"] == "completed", terminal
        assert "quantum" in _reply_text(terminal).lower(), terminal
    finally:
        await harness.close()


@pytest.mark.asyncio
async def test_crash_recovery(harness: CrashHarness) -> None:
    """SIGKILL mid-turn (before generate commits), restart → completed w/ reply.

    Early crash: the crash lands while the ``generate_response`` node is still
    streaming tokens (before it commits its ``AIMessage``), so on recovery the
    graph re-runs generate and re-streams the reply.
    """
    await harness.start()
    try:
        response_id = await post_and_get_response_id(
            harness.client,
            store=True,
            background=True,
            stream=True,
            model="langgraph",
            input_text="Research fusion energy",
        )
        # Let the graph get mid-turn (analyze ~0.4s, then token streaming).
        await asyncio.sleep(0.6)

        await harness.kill()
        await harness.restart()

        terminal = await poll_until_terminal(harness.client, response_id, timeout_seconds=45.0)
        assert terminal["status"] == "completed", terminal
        # Recovery produced (or preserved) exactly one reply message — no
        # duplicate from re-emission, and it is never lost.
        assert len(_message_items(terminal)) == 1, terminal
        assert "fusion" in _reply_text(terminal).lower(), terminal
    finally:
        await harness.close()


async def _stream_until_and_kill(harness: CrashHarness, response_id: str, *, targets: set[str]) -> str | None:
    """Reconnect via GET ?stream=true; SIGKILL the instant a target event lands.

    Returns the event type that triggered the kill (or a terminal type if the
    response finished first). Used to crash at a precise point in the wire
    protocol rather than relying on wall-clock timing.
    """
    import json

    terminal = {"response.completed", "response.failed", "response.cancelled"}
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
            if event_type in targets or event_type in terminal:
                await harness.kill()
                return event_type
    return None


@pytest.mark.asyncio
async def test_crash_recovery_after_reply_emitted(harness: CrashHarness) -> None:
    """SIGKILL AFTER the reply is fully streamed, around ``stream.checkpoint()``.

    Late crash: the reply has been fully emitted (so LangGraph committed its
    ``AIMessage``) but the framework may not yet have checkpointed the snapshot.
    Recovery must still yield exactly one reply message with the right text —
    reconstructing it verbatim from graph state (or re-emitting the persisted
    item if the checkpoint had landed). Never reply-less, never duplicated.
    """
    await harness.start()
    try:
        response_id = await post_and_get_response_id(
            harness.client,
            store=True,
            background=True,
            stream=True,
            model="langgraph",
            input_text="Research fusion energy deeply",
        )
        trigger = await _stream_until_and_kill(
            harness,
            response_id,
            targets={"response.output_text.done", "response.output_item.done"},
        )
        assert trigger is not None, "never observed the reply completing before terminal"

        await harness.restart()

        terminal = await poll_until_terminal(harness.client, response_id, timeout_seconds=45.0)
        assert terminal["status"] == "completed", terminal
        assert len(_message_items(terminal)) == 1, terminal
        assert "fusion" in _reply_text(terminal).lower(), terminal
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
            model="langgraph",
            input_text="Start a long research task",
        )
        # Immediately steer with a second turn while turn 1 is still running.
        turn2 = await post_and_get_response_id(
            harness.client,
            store=True,
            background=True,
            stream=True,
            model="langgraph",
            input_text="Actually focus on error correction",
            extra={"previous_response_id": turn1},
        )
        assert turn2 and turn2 != turn1

        # The steered successor must complete and its reply must reflect the
        # steered input (not merely reach any terminal state).
        t2 = await poll_until_terminal(harness.client, turn2, timeout_seconds=45.0)
        assert t2["status"] == "completed", t2
        assert "error correction" in _reply_text(t2).lower(), t2

        # Turn 1 (superseded) must also reach a terminal state — never hangs.
        t1 = await poll_until_terminal(harness.client, turn1, timeout_seconds=45.0)
        assert t1["status"] in ("completed", "cancelled"), t1
    finally:
        await harness.close()
