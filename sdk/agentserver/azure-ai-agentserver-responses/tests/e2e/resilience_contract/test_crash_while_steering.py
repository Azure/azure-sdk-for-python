# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Crash-WHILE-steering resilience (follow-up to the retired ``verify_crash_steer``).

Scenario: a steerable resilient conversation is running turn 1 (response A) when
the client steers a new turn (response B) via ``previous_response_id``. The
framework supersedes A (it ends cleanly) and drains the steering input to run
turn B. A SIGKILL then lands **while turn B is mid-flight** (``drain_in_progress``
is set on the core task). After restart the core task is reclaimed and the
steered turn is recovered.

Contract asserted:

- The superseded turn A reaches a terminal state (``completed``) — it closed
  cleanly before the crash.
- The **steered** turn B ALSO recovers to a terminal state (``completed``) and
  its output reflects the steered input. A steered turn interrupted by a crash
  must not be orphaned in ``in_progress`` forever.

Unlike the old battery ``verify_crash_steer`` script (which used steering only
as a crash-*delivery* mechanism — now obsolete because a bare ``crash`` pinned
via ``agent_session_id`` lands on the same sandbox), this test uses steering as
the feature under test and injects the crash out-of-band via the harness
SIGKILL, so it validates *steering-feature* resilience deterministically in CI.
"""

from __future__ import annotations

import asyncio
import json

import httpx
import pytest

from tests.e2e._crash_harness import CrashHarness
from tests.e2e.resilience_contract.conftest import LONG_GRACE_S, poll_until_terminal

_STEERING_HANDLER_MODULE = "tests.e2e.resilience_contract._steering_handler"

# The steered turn sleeps this long mid-flight; the crash lands inside it.
_STEER_SLEEP_MS = 5000


def _make_steering_harness(tmp_path, *, resilient_background: bool = True) -> CrashHarness:
    return CrashHarness(
        sample_module=_STEERING_HANDLER_MODULE,
        tmp_path=tmp_path,
        readiness_timeout_seconds=15.0,
        env_extras={
            "CONFORMANCE_RESILIENT_BACKGROUND": "true" if resilient_background else "false",
            "CONFORMANCE_STEER_SLEEP_MS": str(_STEER_SLEEP_MS),
            "AGENTSERVER_SHUTDOWN_GRACE_SECONDS": str(LONG_GRACE_S),
            "AGENTSERVER_GRACEFUL_SHUTDOWN_TIMEOUT_SECONDS": str(LONG_GRACE_S),
            "LOGLEVEL": "WARNING",
        },
    )


async def _post_until_first_delta(
    client: httpx.AsyncClient,
    body: dict,
    *,
    max_seconds: float = 30.0,
) -> str:
    """POST a streaming create/steer and return the response id once its first
    ``output_text.delta`` lands (i.e. that turn's handler is executing)."""
    timeout = httpx.Timeout(connect=10.0, read=max_seconds, write=10.0, pool=10.0)
    response_id = ""
    async with client.stream("POST", "/responses", json=body, timeout=timeout) as resp:
        assert resp.status_code == 200, f"unexpected status {resp.status_code}"
        buf = bytearray()
        async for chunk in resp.aiter_bytes():
            buf.extend(chunk)
            while b"\n\n" in buf:
                raw, _, rest = buf.partition(b"\n\n")
                buf = bytearray(rest)
                for line in raw.split(b"\n"):
                    if not line.startswith(b"data:"):
                        continue
                    try:
                        payload = json.loads(line[5:].strip())
                    except json.JSONDecodeError:
                        continue
                    if not response_id:
                        rid = (payload.get("response") or {}).get("id")
                        if rid:
                            response_id = rid
                    if "output_text.delta" in (payload.get("type") or ""):
                        return response_id
    return response_id


def _final_texts(response_body: dict) -> list[str]:
    texts: list[str] = []
    for item in response_body.get("output") or []:
        if not isinstance(item, dict):
            continue
        for part in item.get("content") or []:
            if isinstance(part, dict) and part.get("type") == "output_text":
                texts.append(part.get("text", ""))
    return texts


@pytest.mark.asyncio
async def test_crash_while_steering_recovers_steered_turn(tmp_path) -> None:
    """A crash mid-steered-turn recovers the steered response to terminal."""
    harness = _make_steering_harness(tmp_path)
    await harness.start()
    try:
        client = harness.client

        # Turn 1 (response A): start the steerable conversation streaming.
        turn1 = {
            "model": "conformance-test",
            "input": "explain topic one",
            "store": True,
            "background": True,
            "stream": True,
        }
        rid_a = await _post_until_first_delta(client, turn1)
        assert rid_a, "turn 1 did not stream a first delta"

        # Steer (response B): supersede turn 1 with a new turn on the same
        # conversation. Reading until B's first delta guarantees the steering
        # input has drained and turn B is now mid-flight (drain_in_progress).
        turn2 = {
            "model": "conformance-test",
            "input": "actually explain topic two",
            "store": True,
            "background": True,
            "stream": True,
            "previous_response_id": rid_a,
        }
        rid_b = await _post_until_first_delta(client, turn2)
        assert rid_b and rid_b != rid_a, f"steered turn id invalid (a={rid_a} b={rid_b})"

        # Crash the container while turn B is mid-flight, then restart.
        await harness.kill()
        await harness.restart()

        # The superseded turn A closed cleanly before the crash → terminal.
        body_a = await poll_until_terminal(harness.client, rid_a, timeout_seconds=45.0)
        assert body_a.get("status") == "completed", f"turn A not completed: {body_a.get('status')}"

        # The steered turn B must recover to terminal (finding-t5): it must not
        # be orphaned in in_progress after the mid-drain crash.
        body_b = await poll_until_terminal(harness.client, rid_b, timeout_seconds=45.0)
        assert body_b.get("status") == "completed", (
            f"steered turn B did not recover to terminal (status="
            f"{body_b.get('status')}) — steered turn orphaned after crash"
        )

        # B's recovered output reflects the steered input (turn 2) AND carries
        # the recovered-lifetime tag (``L1``), proving the crash landed
        # mid-flight and the steered turn was re-run by crash recovery (not a
        # pre-crash completion).
        texts_b = " ".join(_final_texts(body_b))
        assert "input=actually explain topic two" in texts_b, (
            f"recovered steered turn B output does not reflect the steered input: {texts_b!r}"
        )
        assert "_L1_" in texts_b, (
            f"steered turn B did not go through crash recovery (no L1 lifetime tag): {texts_b!r}"
        )
    finally:
        await harness.close()
