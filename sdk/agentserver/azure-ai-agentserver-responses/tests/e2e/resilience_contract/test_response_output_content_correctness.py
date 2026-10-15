# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Response.output content correctness for non-streaming rows (Spec 014 Phase 9 follow-up, T-173).

Closes the response.output content gap identified in the Phase 9
reflection: existing per-cell tests check ``response.status`` but not
the assembled ``response.output`` content. For stream=false clients,
``response.output`` IS the contract surface — a recovered handler that
emits wrong content would still pass a status-only test.

The conformance handler emits a composite final text
``L{lifetime}_done|pre=N|post=M|chain=…|visited=…`` so tests can assert
the polled snapshot reflects the correct lifetime's intent:

- Row 1 Path A: ``output[0].content[0].text`` starts with ``L0_done`` —
  fresh-attempt content.
- Row 1 Path C: ``output[0].content[0].text`` starts with ``L1_done`` —
  recovered-attempt content (the recovered handler's snapshot
  replaces the fresh attempt's).
- Row 2 Path A: ``output[0].content[0].text`` starts with ``L0_done``.
- Row 3 Path A: same.

Failed-terminal rows (Row 2/3 Path B/C) have no useful output text;
those are covered by the existing per-cell tests' `response.error.code`
assertions. This file focuses on the **completed** cells where
content correctness matters.
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


async def _post_bg_polled(client: httpx.AsyncClient) -> str:
    r = await client.post(
        "/responses",
        json={
            "model": "conformance-test",
            "input": "hello",
            "store": True,
            "background": True,
            "stream": False,
        },
    )
    assert r.status_code == 200, r.text
    return r.json()["id"]


async def _post_bg_streamed_until_response_id(client: httpx.AsyncClient) -> str:
    timeout = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=10.0)
    response_id = ""
    async with client.stream(
        "POST",
        "/responses",
        json={
            "model": "conformance-test",
            "input": "hello",
            "store": True,
            "background": True,
            "stream": True,
        },
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
                    if not response_id:
                        rid = payload.get("response", {}).get("id")
                        if rid:
                            response_id = rid
                    if "output_text.delta" in (payload.get("type") or ""):
                        return response_id
    return response_id


def _final_text_from_snapshot(snapshot: dict) -> str:
    """Extract the assembled output text from a response snapshot."""
    output = snapshot.get("output") or []
    assert output, f"snapshot has empty output: {snapshot!r}"
    contents = output[0].get("content") or []
    assert contents, f"output item has no content: {output[0]!r}"
    return contents[0].get("text", "")


@pytest.mark.asyncio
async def test_row_1_path_a_polled_response_output_reflects_fresh_handler(
    make_harness: Callable[..., CrashHarness],
) -> None:
    """Row 1 Path A stream=F: polled GET reflects lifetime-0 handler's intent."""
    harness = make_harness(
        resilient_background=True,
        handler_sleep_ms=50,  # fast completion within grace
        shutdown_grace_seconds=LONG_GRACE_S,
    )
    await harness.start()
    try:
        response_id = await _post_bg_polled(harness.client)
        terminal = await poll_until_terminal(harness.client, response_id, timeout_seconds=15.0)
        assert terminal["status"] == "completed", terminal
        text = _final_text_from_snapshot(terminal)
        assert text.startswith("L0_done"), f"Fresh handler must produce L0_done… final text. Got: {text!r}"
        # Spec 038: the chain id is a stable native id — a chain-scoped
        # ``cchain_…`` / ``rchain_…`` id, OR the ``response_id`` verbatim for a
        # non-steerable one-shot.
        import re as _re

        _m = _re.search(r"chain=(\S+)", text)
        assert _m is not None, f"final text must carry a chain= segment. Got: {text!r}"
        _chain = _m.group(1)
        assert (
            _re.fullmatch(r"[a-z]+_[A-Za-z0-9]+", _chain) and len(_chain) <= 128
        ), f"chain= must be a native id (<=128 chars). Got chain={_chain!r}."
    finally:
        await harness.close()


@pytest.mark.asyncio
async def test_row_1_path_c_polled_response_output_reflects_recovered_handler(
    make_harness: Callable[..., CrashHarness],
) -> None:
    """Row 1 Path C stream=F: post-recovery GET reflects lifetime-1 handler's intent."""
    harness = make_harness(
        resilient_background=True,
        handler_sleep_ms=int(LONG_TIME_SECS * 1000),
        pre_sleep_deltas=1,
        shutdown_grace_seconds=LONG_GRACE_S,
    )
    await harness.start()
    try:
        # POST polled but we still need the handler to have started
        # before SIGKILL. Use bg=true,stream=true so we can capture the
        # response_id and confirm content arrives pre-crash; then GET
        # snapshot post-recovery (which is the polled-style observation).
        response_id = await _post_bg_streamed_until_response_id(harness.client)
        assert response_id
        await asyncio.sleep(0.2)
        await harness.kill()
        await harness.restart()

        terminal = await poll_until_terminal(harness.client, response_id, timeout_seconds=30.0)
        assert terminal["status"] == "completed", terminal
        text = _final_text_from_snapshot(terminal)
        # With pre_sleep_deltas=1, the snapshot text accumulates the
        # recovered handler's pre-sleep delta (``L1_pre_d0``) followed by
        # the composite final text (``L1_done|…``). Assert the composite
        # is in the text — proves the recovered handler's intent is
        # what landed, not lifetime 0's stale content.
        assert "L1_done" in text, (
            f"Recovered handler must produce L1_done… composite in final "
            f"text (reflecting lifetime-1's intent, NOT a stale "
            f"lifetime-0 value). Got: {text!r}"
        )
        # Crucially, lifetime 0's composite must NOT appear — the
        # snapshot is built from the assembled stream and the recovered
        # handler's composite replaces lifetime 0's.
        assert "L0_done" not in text, (
            "Snapshot text must not include the pre-crash composite "
            f"(reset-on-in_progress reconciliation). Got: {text!r}"
        )
    finally:
        await harness.close()


@pytest.mark.asyncio
async def test_row_2_path_a_polled_response_output_reflects_fresh_handler(
    make_harness: Callable[..., CrashHarness],
) -> None:
    """Row 2 Path A stream=F: polled GET reflects lifetime-0 handler's intent."""
    harness = make_harness(
        resilient_background=False,  # Row 2: non-resilient background
        handler_sleep_ms=50,
        shutdown_grace_seconds=LONG_GRACE_S,
    )
    await harness.start()
    try:
        response_id = await _post_bg_polled(harness.client)
        terminal = await poll_until_terminal(harness.client, response_id, timeout_seconds=15.0)
        assert terminal["status"] == "completed", terminal
        text = _final_text_from_snapshot(terminal)
        assert text.startswith("L0_done"), f"Row 2 fresh handler must produce L0_done… final text. Got: {text!r}"
    finally:
        await harness.close()


@pytest.mark.asyncio
async def test_row_3_path_a_foreground_response_output_reflects_fresh_handler(
    make_harness: Callable[..., CrashHarness],
) -> None:
    """Row 3 Path A stream=F: foreground POST returns the snapshot inline with correct content."""
    harness = make_harness(
        resilient_background=True,  # immaterial for fg
        handler_sleep_ms=50,
        shutdown_grace_seconds=LONG_GRACE_S,
    )
    await harness.start()
    try:
        r = await harness.client.post(
            "/responses",
            json={
                "model": "conformance-test",
                "input": "hello",
                "store": True,
                "background": False,
                "stream": False,
            },
            timeout=15.0,
        )
        assert r.status_code == 200, r.text
        snapshot = r.json()
        assert snapshot["status"] == "completed", snapshot
        text = _final_text_from_snapshot(snapshot)
        assert text.startswith("L0_done"), (
            f"Row 3 foreground handler must produce L0_done… final text. " f"Got: {text!r}"
        )
    finally:
        await harness.close()
