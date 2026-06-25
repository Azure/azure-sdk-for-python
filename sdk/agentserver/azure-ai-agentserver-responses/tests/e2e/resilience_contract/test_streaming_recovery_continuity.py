# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Streaming-recovery continuity test (Spec 014 Phase 9 follow-up).

Pins the contract that **pre-crash SSE events survive recovery and a
reconnecting client can replay the complete event log** for a Row 1
resilient streaming response.

Scenario:

1. Spawn the conformance handler configured to emit several
   ``output_text.delta`` events BEFORE its interruptible sleep.
2. POST a streaming Row 1 request (``store=true, bg=true,
   resilient_bg=True, stream=true``).
3. Read the wire stream until the pre-sleep deltas have all landed
   (we know their content prefix is ``L0_pre_d0``, ``L0_pre_d1``, …
   per the per-lifetime tagging in :mod:`_test_handler_markers`).
4. SIGKILL the subprocess (Path C).
5. Restart the subprocess. The resilient framework re-invokes the handler.
6. ``GET /responses/{id}?stream=true&starting_after=0`` and collect
   every event in the persisted stream.

Assertions:

- All pre-crash deltas (``L0_pre_d0`` … ``L0_pre_d{N-1}``) are still
  present in the persisted stream — they must NOT have been erased
  by the recovered attempt's terminal-time bookkeeping.
- The persisted stream's sequence numbers are strictly monotonically
  increasing — the recovered handler's events have sequence numbers
  that succeed (rather than overlap or reset) the pre-crash events.
- The recovered attempt's events include at least one
  ``response.in_progress`` reset (the snapshot-reconciliation marker)
  AND a ``response.completed`` terminal.
- The recovered attempt's deltas (``L1_pre_d{i}`` and ``L1_post_d{j}``)
  appear with sequence numbers strictly greater than the last pre-crash
  event.

This test was RED before the Spec 014 Phase 9 follow-up fix that

- changed ``_PipelineState`` to track ``next_seq`` and seed it from
  the prior persisted event count on recovered entry, and
- removed the truncating ``save_stream_events`` calls in
  ``_persist_and_resolve_terminal`` and ``_finalize_bg_stream`` for
  the resilient-stream case (the incremental ``append_stream_event``
  calls in ``_process_handler_events`` already provide persistence).

Contract source: ``resilience-contract.md`` § Streaming sub-contract
(stream events persist across recovery attempts).
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Callable

import httpx
import pytest

from tests.e2e._crash_harness import CrashHarness
from tests.e2e.resilience_contract._test_handler_markers import (
    PHASE_PRE,
    delta_content,
)
from tests.e2e.resilience_contract.conftest import (
    LONG_GRACE_S,
    LONG_TIME_SECS,
    poll_until_terminal,
)

_PRE_DELTAS = 3


async def _post_and_read_until_pre_deltas(
    client: httpx.AsyncClient,
    expected_deltas: int,
) -> tuple[str, int]:
    """POST stream=true request; read wire events until `expected_deltas` deltas land.

    Returns (response_id, count_of_pre_crash_deltas_seen).
    """
    body = {
        "model": "conformance-test",
        "input": "hello",
        "store": True,
        "background": True,
        "stream": True,
    }
    response_id = ""
    delta_count = 0
    timeout = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=10.0)
    async with client.stream("POST", "/responses", json=body, timeout=timeout) as resp:
        assert resp.status_code == 200, f"POST failed: {resp.status_code}"
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
                    t = payload.get("type", "")
                    if not response_id:
                        rid = payload.get("response", {}).get("id")
                        if rid:
                            response_id = rid
                    if "output_text.delta" in t:
                        delta_count += 1
                        if delta_count >= expected_deltas:
                            return response_id, delta_count
    return response_id, delta_count


async def _get_full_stream(client: httpx.AsyncClient, response_id: str) -> list[dict]:
    """GET ?stream=true&starting_after=0 and collect all events to terminal."""
    events: list[dict] = []
    timeout = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=10.0)
    async with client.stream(
        "GET",
        f"/responses/{response_id}",
        params={"stream": "true", "starting_after": "0"},
        timeout=timeout,
    ) as resp:
        assert resp.status_code == 200, f"GET failed: {resp.status_code}"
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
                    events.append(payload)
                    if payload.get("type") in (
                        "response.completed",
                        "response.failed",
                        "response.cancelled",
                    ):
                        return events
    return events


@pytest.mark.asyncio
async def test_pre_crash_deltas_survive_recovery(
    make_harness: Callable[..., CrashHarness],
) -> None:
    """Pre-crash deltas must remain in the persisted stream after recovery."""
    harness = make_harness(
        resilient_background=True,
        # Long handler sleep so the SIGKILL lands MID-sleep, after the
        # pre-sleep deltas have all been emitted to the wire.
        handler_sleep_ms=int(LONG_TIME_SECS * 1000),
        pre_sleep_deltas=_PRE_DELTAS,
        shutdown_grace_seconds=LONG_GRACE_S,
    )
    await harness.start()
    try:
        response_id, delta_count = await _post_and_read_until_pre_deltas(harness.client, expected_deltas=_PRE_DELTAS)
        assert response_id, "never captured response id"
        assert delta_count >= _PRE_DELTAS, (
            f"only saw {delta_count}/{_PRE_DELTAS} pre-crash deltas before "
            "the read loop returned — handler may have completed before "
            "SIGKILL window opened"
        )

        # Give the framework a beat to finish appending the deltas to the
        # persistent stream before we kill the subprocess.
        await asyncio.sleep(0.2)

        await harness.kill()
        await harness.restart()

        # Wait for the recovered handler to reach terminal.
        terminal = await poll_until_terminal(harness.client, response_id, timeout_seconds=30.0)
        assert terminal["status"] == "completed", terminal

        # Now read the full persisted event stream and assert continuity.
        events = await _get_full_stream(harness.client, response_id)

        # Find the deltas with our pre-crash content (lifetime 0 pre-sleep).
        pre_crash_delta_contents = {delta_content(0, PHASE_PRE, i) for i in range(_PRE_DELTAS)}
        seen_pre_crash = []
        for ev in events:
            if ev.get("type") == "response.output_text.delta":
                delta = ev.get("delta", "")
                if delta in pre_crash_delta_contents:
                    seen_pre_crash.append((ev.get("sequence_number"), delta))

        assert len(seen_pre_crash) == _PRE_DELTAS, (
            f"Pre-crash deltas missing from persisted stream after recovery. "
            f"Expected {_PRE_DELTAS} deltas with content "
            f"{sorted(pre_crash_delta_contents)}, saw {seen_pre_crash}. "
            f"Full event types: {[e.get('type') for e in events]}"
        )

        # Sequence numbers must be strictly monotonically increasing across
        # the assembled (pre-crash + recovered) stream.
        seq_numbers = [e.get("sequence_number") for e in events]
        assert all(
            isinstance(s, int) for s in seq_numbers
        ), f"All events must have integer sequence_number; got {seq_numbers}"
        for prev, curr in zip(seq_numbers, seq_numbers[1:]):
            assert curr > prev, (
                f"Sequence numbers must be strictly monotonically increasing "
                f"across recovery attempts. Got {seq_numbers}."
            )

        # The recovered handler MUST have emitted a response.in_progress
        # reset event (per the streaming sub-contract) AFTER the pre-crash
        # deltas, with a seq number > the highest pre-crash delta's seq.
        max_pre_crash_seq = max(seq for seq, _ in seen_pre_crash)
        post_recovery_in_progress = [
            e
            for e in events
            if e.get("type") == "response.in_progress" and (e.get("sequence_number") or -1) > max_pre_crash_seq
        ]
        assert post_recovery_in_progress, (
            "Recovered handler must emit at least one response.in_progress "
            "reset event with seq > the last pre-crash event. Full stream:\n"
            + "\n".join(f"  seq={e.get('sequence_number')} type={e.get('type')}" for e in events)
        )

        # (Spec 026 FR-026-1 / Streaming sub-contract clause 5) The recovered
        # lifetime MUST NOT re-emit response.created to the resilient stream.
        # ``_get_full_stream`` reads with starting_after=0, which excludes the
        # single legitimate seq-0 response.created; any response.created event
        # appearing in this stream therefore has seq > 0 and is a duplicate
        # written by the recovered lifetime — which is exactly the defect this
        # asserts against. (RED before the empty-stream gate; GREEN after.)
        duplicate_created = [e for e in events if e.get("type") == "response.created"]
        assert duplicate_created == [], (
            "Recovered resilient stream must not re-emit response.created "
            "(a stream has exactly one, at seq 0). Found "
            f"{len(duplicate_created)} duplicate(s) at seq "
            f"{[e.get('sequence_number') for e in duplicate_created]}. Full stream:\n"
            + "\n".join(f"  seq={e.get('sequence_number')} type={e.get('type')}" for e in events)
        )

        # Recovered deltas (lifetime 1) must also be present with seq > max
        # pre-crash seq — the per-lifetime tagging makes this verifiable.
        recovered_deltas = [
            (e.get("sequence_number"), e.get("delta", ""))
            for e in events
            if e.get("type") == "response.output_text.delta" and (e.get("delta") or "").startswith("L1_")
        ]
        assert recovered_deltas, (
            "Recovered handler must emit at least one L1_ delta (its own "
            f"pre-sleep or post-sleep content). Got events: "
            f"{[e.get('type') for e in events]}"
        )
        for seq, _ in recovered_deltas:
            assert (
                isinstance(seq, int) and seq > max_pre_crash_seq
            ), f"Recovered delta seq must be > {max_pre_crash_seq}, got {seq}"

        # Final assertion: the response.completed terminal must also have
        # seq > max_pre_crash_seq (otherwise we'd be looking at a leftover
        # from the killed attempt).
        completed = [e for e in events if e.get("type") == "response.completed"]
        assert completed, "no response.completed in full replay"
        assert (completed[-1].get("sequence_number") or -1) > max_pre_crash_seq
    finally:
        await harness.close()
