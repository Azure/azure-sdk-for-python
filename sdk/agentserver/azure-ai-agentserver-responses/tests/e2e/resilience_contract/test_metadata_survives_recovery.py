# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Metadata persistence across recovery (Spec 014 Phase 9 follow-up, T-173).

Pins the contract clause from ``resilience-contract.md`` § Per-row
contracts → Row 1 → Recovery handler entry contract:

> ``context.conversation_chain_metadata`` is a persistent ``MutableMapping[str, Any]``
> whose contents from prior invocations survive the crash. The framework
> guarantees keys written via ``metadata[key] = value`` plus a subsequent
> ``await metadata.flush()`` are visible to the recovered invocation.

Method:

1. Spawn the conformance handler with ``emit_metadata_watermark=True``
   and a slow handler so SIGKILL lands MID-handler after the watermark
   has been flushed.
2. POST a Row 1 streaming response.
3. Wait for at least one pre-sleep delta on the wire (proves the handler
   reached the watermark-flush code path).
4. SIGKILL the subprocess.
5. Restart.
6. Wait for terminal.
7. GET the full event stream and inspect the recovered handler's final
   text. It carries ``visited=[0, 1]`` only if the recovered handler
   read the metadata watermark written by lifetime 0 AND added its own
   entry. ``visited=[1]`` (lifetime 0 marker lost) indicates the
   metadata didn't survive recovery — a contract violation.

This is also implicitly a smoke test of the at-most-once side-effect
pattern: the watermark logic is exactly the kind of pre-side-effect
flush the contract requires handlers to use.
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


async def _post_and_wait_for_first_delta(
    client: httpx.AsyncClient,
) -> str:
    """POST stream=true bg=true store=true; read until first delta lands."""
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
                        return response_id
    return response_id


async def _get_full_stream(client: httpx.AsyncClient, response_id: str) -> list[dict]:
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
async def test_metadata_visited_marker_survives_recovery(
    make_harness: Callable[..., CrashHarness],
) -> None:
    """Metadata written + flushed pre-crash is visible to recovered handler."""
    harness = make_harness(
        resilient_background=True,
        emit_metadata_watermark=True,
        handler_sleep_ms=int(LONG_TIME_SECS * 1000),
        pre_sleep_deltas=1,
        shutdown_grace_seconds=LONG_GRACE_S,
    )
    await harness.start()
    try:
        response_id = await _post_and_wait_for_first_delta(harness.client)
        assert response_id

        # Give the framework a beat to flush the metadata + first delta.
        await asyncio.sleep(0.2)

        await harness.kill()
        await harness.restart()

        terminal = await poll_until_terminal(harness.client, response_id, timeout_seconds=30.0)
        assert terminal["status"] == "completed", terminal

        events = await _get_full_stream(harness.client, response_id)

        # Find the recovered handler's output_text.done — its final text
        # carries the ``visited=[…]`` segment. We want the LAST one in the
        # stream (the recovered lifetime's terminal text).
        done_events = [e for e in events if e.get("type") == "response.output_text.done"]
        assert done_events, "No response.output_text.done in replay. Event types: " f"{[e.get('type') for e in events]}"
        final_text = done_events[-1].get("text", "")
        assert "visited=" in final_text, (
            "Recovered handler's final text must include the visited list. " f"Got: {final_text!r}"
        )
        # Parse the visited segment.
        visited_seg = next(
            (seg for seg in final_text.split("|") if seg.startswith("visited=")),
            None,
        )
        assert visited_seg is not None, f"No visited= segment in {final_text!r}"
        visited_list = visited_seg[len("visited=") :]
        # Lifetime 0 wrote 0; lifetime 1 read [0] + appended 1 → expect [0, 1].
        assert "0" in visited_list and "1" in visited_list, (
            "Metadata watermark from lifetime 0 must survive recovery and be "
            "visible to lifetime 1 (expected visited=[0, 1] or similar). "
            f"Got visited={visited_list!r}, full final_text={final_text!r}"
        )
    finally:
        await harness.close()
