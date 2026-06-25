# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Output-item slot reconciliation across recovery (Spec 014 Phase 9 follow-up, T-173).

Pins the contract clause from ``resilience-contract.md`` § Streaming
sub-contract:

> Server rule 3: ``response.in_progress`` reset event (row 1 Paths B
> post-restart, and C). On handler re-invocation, the recovered handler
> MUST emit a ``response.in_progress`` event as the first event of the
> new invocation. This event MUST carry the corrected ``output_items``
> (reflecting the post-recovery state if any output items were
> finalized pre-crash).
>
> Client-side rule: A streaming client MUST reset its in-memory
> accumulator on EVERY ``response.in_progress`` event AFTER the first
> one. The post-reset events (which the handler emits as the first
> events of its recovered invocation) carry the corrected state.

The conformance handler always emits its single output item at
``output_index=0``, so the recovered handler's ``output_item.added`` at
the same index exercises the reset-reconciliation semantics: a client
that observes the post-reset events overrides the pre-crash slot
content with the recovered slot content.

Method:

1. Spawn the handler configured to emit pre-sleep deltas (so a
   pre-crash output_item.added + content_part.added land in the
   persisted stream).
2. POST a Row 1 streaming response.
3. Wait until a pre-crash delta lands.
4. SIGKILL + restart.
5. Wait for terminal.
6. GET the full event stream and assert:
   - Two ``response.output_item.added`` events at ``output_index=0``
     (one per lifetime), each correctly preceded by a
     ``response.in_progress`` event with seq > prior events.
   - The recovered ``output_item.added`` has seq > the pre-crash
     ``output_item.added`` (the framework MUST NOT replace in-place).
   - The final ``response.completed`` event's ``response.output[0]``
     reflects the recovered handler's content (lifetime 1's final
     text, not lifetime 0's). This proves the client-side
     reconciliation rule is enforceable: the snapshot a client
     reconstructs from the assembled stream IS the recovered handler's
     intent, not a stale pre-crash mixture.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Callable

import httpx
import pytest

from tests.e2e._crash_harness import CrashHarness
from tests.e2e.resilience_contract.conftest import (
    LONG_GRACE_S,
    LONG_TIME_SECS,
    poll_until_terminal,
)


async def _post_until_first_delta(client: httpx.AsyncClient) -> str:
    body = {
        "model": "conformance-test",
        "input": "hello",
        "store": True,
        "background": True,
        "stream": True,
    }
    timeout = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=10.0)
    response_id = ""
    async with client.stream("POST", "/responses", json=body, timeout=timeout) as resp:
        assert resp.status_code == 200
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
                        rid = payload.get("response", {}).get("id")
                        if rid:
                            response_id = rid
                    if "output_text.delta" in (payload.get("type") or ""):
                        return response_id
    return response_id


async def _full_stream(client: httpx.AsyncClient, response_id: str) -> list[dict]:
    timeout = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=10.0)
    events: list[dict] = []
    async with client.stream(
        "GET",
        f"/responses/{response_id}",
        params={"stream": "true", "starting_after": "0"},
        timeout=timeout,
    ) as resp:
        assert resp.status_code == 200
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
async def test_output_item_slot_reused_by_recovered_handler(
    make_harness: Callable[..., CrashHarness],
) -> None:
    """Recovered handler's output_item.added at same index produces two added events with correct content reconciliation."""
    harness = make_harness(
        resilient_background=True,
        pre_sleep_deltas=1,
        handler_sleep_ms=int(LONG_TIME_SECS * 1000),
        shutdown_grace_seconds=LONG_GRACE_S,
    )
    await harness.start()
    try:
        response_id = await _post_until_first_delta(harness.client)
        assert response_id

        await asyncio.sleep(0.2)
        await harness.kill()
        await harness.restart()

        terminal = await poll_until_terminal(harness.client, response_id, timeout_seconds=30.0)
        assert terminal["status"] == "completed", terminal

        events = await _full_stream(harness.client, response_id)

        # There must be at least two output_item.added events at index 0:
        # one from lifetime 0 (pre-crash), one from lifetime 1 (recovered).
        item_added_at_0 = [
            (e.get("sequence_number"), e)
            for e in events
            if e.get("type") == "response.output_item.added" and e.get("output_index") == 0
        ]
        assert len(item_added_at_0) >= 2, (
            "Expected TWO response.output_item.added events at output_index=0 "
            "(one per lifetime — recovery does NOT replace in-place, it emits "
            "a fresh added event after the in_progress reset). "
            f"Got {len(item_added_at_0)}: {[seq for seq, _ in item_added_at_0]}."
        )

        # Pre-crash item.added must come before recovered item.added.
        seqs = [seq for seq, _ in item_added_at_0]
        for a, b in zip(seqs, seqs[1:]):
            assert isinstance(a, int) and isinstance(b, int) and b > a, (
                f"output_item.added events must be strictly monotonic in seq. " f"Got: {seqs}"
            )

        # Between the two item.added events, there MUST be at least one
        # response.in_progress event — the reset marker that signals clients
        # to discard the pre-crash slot.
        first_added_seq = seqs[0]
        second_added_seq = seqs[1]
        in_progress_between = [
            e.get("sequence_number")
            for e in events
            if e.get("type") == "response.in_progress"
            and first_added_seq < (e.get("sequence_number") or -1) < second_added_seq
        ]
        assert in_progress_between, (
            "Recovered output_item.added must be preceded by a "
            "response.in_progress reset event (seq strictly between the "
            "two added events). Got events:\n"
            + "\n".join(
                f"  seq={e.get('sequence_number')} type={e.get('type')} " f"output_index={e.get('output_index')}"
                for e in events
            )
        )

        # The recovered handler's final text (lifetime 1) must be the
        # content reflected in the response.completed snapshot. The
        # snapshot is in the terminal event's ``response.output``.
        completed = [e for e in events if e.get("type") == "response.completed"][-1]
        resp_output = (completed.get("response") or {}).get("output") or []
        assert resp_output, f"response.completed has empty output: {completed!r}"
        # The output item carries the assembled text. For sample 18 style
        # handlers, the text is in output[0]["content"][0]["text"]. The
        # conformance handler emits this as the recovered handler's
        # final_text composite which must start with ``L1_done``.
        first_item = resp_output[0]
        contents = first_item.get("content", [])
        assert contents, f"output item has no content: {first_item!r}"
        text_field = contents[0].get("text", "")
        assert "L1_done" in text_field, (
            "response.completed's output must reflect the recovered "
            f"(lifetime 1) handler's intent. Got text={text_field!r}, "
            "expected to contain 'L1_done' (the recovered handler's "
            "composite final text)."
        )
        # Pre-crash lifetime 0's composite final text must NOT appear —
        # the snapshot is built from the assembled stream and the
        # recovered handler's content replaces lifetime 0's via the
        # reset-on-in_progress reconciliation rule.
        assert "L0_done" not in text_field, (
            "Snapshot text must not include the pre-crash composite "
            f"(reset-on-in_progress reconciliation). Got: {text_field!r}"
        )
    finally:
        await harness.close()
