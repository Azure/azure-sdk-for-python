# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""End-to-end tests for the ``resilient_langgraph`` invocations sample.

Spawns the real sample (``resilient_langgraph.app``) as a subprocess via
:class:`CrashHarness` (file-backed task provider + langgraph checkpoints + the
invocation store all rooted at the test ``tmp_path`` via ``AGENTSERVER_STATE_ROOT``)
and drives it over real HTTP. Unlike the ``_live`` samples this needs no cloud
endpoint — the graph nodes are simulated — so it always runs when ``langgraph``
is installed.

Exercises the LangGraph-integration correctness the sample was reworked for
(Spec 041 A1), applying the responses-sample learnings:

- **Turn completion + multi-turn context** — a turn runs to ``completed`` with a
  reply; a second turn on the same session accumulates conversation context.
- **Steering** — an overlapping second turn on the same session supersedes the
  first; the steered turn completes.
- **Crash recovery** — SIGKILL mid-turn-2 + restart: recovery forks from the last
  stable checkpoint and re-runs the turn cleanly, reaching ``completed`` with the
  correct (turn-2) output — never mis-attributing the input or losing the turn.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

import pytest

pytest.importorskip("langgraph", reason="langgraph required for resilient_langgraph e2e")
pytest.importorskip("langgraph.checkpoint.sqlite", reason="langgraph sqlite checkpointer required")

from ._crash_harness import CrashHarness  # noqa: E402

_SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "samples"


def _harness(tmp_path: Path) -> CrashHarness:
    env_extras = {
        "PYTHONPATH": (f"{_SAMPLES_DIR}{os.pathsep}{os.environ.get('PYTHONPATH', '')}").rstrip(os.pathsep),
        # Fast graph nodes so the e2e runs quickly.
        "LANGGRAPH_STEP_DELAY_SEC": "0.3",
    }
    return CrashHarness(
        sample_module="resilient_langgraph.app",
        tmp_path=tmp_path,
        env_extras=env_extras,
        readiness_timeout_seconds=20.0,
    )


async def _post_turn(harness: CrashHarness, session: str, message: str) -> str:
    resp = await harness.client.post(
        f"/invocations?agent_session_id={session}",
        json={"message": message},
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code in (200, 202), (resp.status_code, resp.text)
    inv_id = resp.json().get("invocation_id") or resp.headers.get("x-agent-invocation-id")
    assert inv_id
    return inv_id


async def _poll_until_terminal(
    harness: CrashHarness,
    inv_id: str,
    *,
    statuses: set[str] = frozenset({"completed", "cancelled"}),
    timeout: float = 40.0,
) -> dict:
    loop = asyncio.get_event_loop()
    deadline = loop.time() + timeout
    last: dict = {}
    while loop.time() < deadline:
        resp = await harness.client.get(f"/invocations/{inv_id}")
        if resp.status_code == 200:
            last = resp.json()
            if last.get("status") in statuses:
                return last
        await asyncio.sleep(0.25)
    raise AssertionError(f"invocation {inv_id} never reached {statuses}; last={last}")


@pytest.mark.asyncio
async def test_turn_completes_with_reply(tmp_path: Path) -> None:
    harness = _harness(tmp_path)
    await harness.start()
    try:
        inv = await _post_turn(harness, "lg-single", "Help me plan a trip to Tokyo")
        body = await _poll_until_terminal(harness, inv)
        assert body["status"] == "completed", body
        assert body.get("output", {}).get("turn") == 1, body
        assert body["output"].get("reply"), body
    finally:
        await harness.close()


@pytest.mark.asyncio
async def test_multiturn_accumulates_context(tmp_path: Path) -> None:
    harness = _harness(tmp_path)
    await harness.start()
    try:
        inv1 = await _post_turn(harness, "lg-multi", "I want to plan a vacation")
        b1 = await _poll_until_terminal(harness, inv1)
        assert b1["status"] == "completed" and b1["output"]["turn"] == 1, b1

        inv2 = await _post_turn(harness, "lg-multi", "Budget is $5000 for two weeks")
        b2 = await _poll_until_terminal(harness, inv2)
        assert b2["status"] == "completed", b2
        # Second turn on the same session sees the accumulated conversation.
        assert b2["output"]["turn"] == 2, b2
    finally:
        await harness.close()


@pytest.mark.asyncio
async def test_steering_supersedes_running_turn(tmp_path: Path) -> None:
    harness = _harness(tmp_path)
    await harness.start()
    try:
        inv1 = await _post_turn(harness, "lg-steer", "Plan a long detailed itinerary for Tokyo")
        # Immediately steer with a second turn while turn 1 is still running.
        inv2 = await _post_turn(harness, "lg-steer", "Actually, let us go to Paris instead")
        assert inv2 != inv1

        # The steered successor must complete.
        b2 = await _poll_until_terminal(harness, inv2)
        assert b2["status"] == "completed", b2
        # Turn 1 reaches a terminal state (superseded → cancelled, or completed).
        b1 = await _poll_until_terminal(harness, inv1)
        assert b1["status"] in ("cancelled", "completed"), b1
    finally:
        await harness.close()


@pytest.mark.asyncio
async def test_crash_recovery_reruns_turn_from_stable_checkpoint(tmp_path: Path) -> None:
    """SIGKILL mid-turn-2 + restart → recovery forks from turn-1's stable
    checkpoint and re-runs turn 2 cleanly, reaching completed with turn==2."""
    harness = _harness(tmp_path)
    await harness.start()
    try:
        # Turn 1 completes → records a stable checkpoint for the session.
        inv1 = await _post_turn(harness, "lg-crash", "First message to establish context")
        b1 = await _poll_until_terminal(harness, inv1)
        assert b1["status"] == "completed", b1

        # Turn 2 — crash while it is mid-flight (nodes run at 0.3s each).
        inv2 = await _post_turn(harness, "lg-crash", "Second message that will survive a crash")
        await asyncio.sleep(0.4)  # let analyze/generate get underway
        await harness.kill()
        await harness.restart()

        # After restart the framework reclaims the orphaned task and re-invokes
        # with entry_mode=recovered; the reworked handler forks from turn-1's
        # stable checkpoint and re-runs turn 2 to a clean, deterministic result.
        b2 = await _poll_until_terminal(harness, inv2, timeout=60.0)
        assert b2["status"] == "completed", b2
        assert b2["output"]["turn"] == 2, b2
        assert b2["output"].get("reply"), b2
    finally:
        await harness.close()
