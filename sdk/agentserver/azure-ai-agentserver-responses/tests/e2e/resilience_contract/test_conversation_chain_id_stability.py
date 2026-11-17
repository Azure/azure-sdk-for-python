# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""``conversation_chain_id`` stability across recovery (Spec 014 Phase 9 follow-up, T-173).

Pins the implicit contract clause that ``context.conversation_chain_id``
returns the same value across all attempts of the same logical
conversation — fresh entry, in-process retry, and crash-recovered
re-invocation. Handlers rely on this stability when they use the chain
id as the session id for upstream frameworks (sample 18's Copilot
session id is exactly this).

Without cross-attempt stability, the recovered handler would reattach
to a DIFFERENT upstream session than the pre-crash handler used,
breaking conversational continuity.

Method:

1. Spawn the conformance handler with a slow handler so SIGKILL lands
   mid-flight.
2. POST a Row 1 streaming response.
3. Wait for the pre-crash final-text to NOT arrive (handler is still
   pre-sleep). Capture the response_id but don't bother with the chain
   id from the wire — we'll read it from the persisted stream.
4. SIGKILL + restart.
5. Wait for terminal.
6. GET the full stream and parse the ``chain={chain_id}`` segment from
   the recovered handler's final text. Assert the chain id is a stable
   non-empty value (no lifetime-1 vs lifetime-0 mismatch since the
   chain is derived from the persisted request).
7. For a standalone response (no ``conversation_id`` / no
   ``previous_response_id``), the chain id is a stable opaque hash
   derived from the response id's embedded partition key (Spec 036),
   identical across recovery attempts.
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


def _extract_chain_id(final_text: str) -> str | None:
    """Parse the ``chain=<id>`` segment from the composite final text."""
    for seg in final_text.split("|"):
        if seg.startswith("chain="):
            return seg[len("chain=") :]
    return None


@pytest.mark.asyncio
async def test_chain_id_stable_across_recovery(
    make_harness: Callable[..., CrashHarness],
) -> None:
    """conversation_chain_id is the same value for lifetime 0 and lifetime 1."""
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

        # There should be TWO output_text.done events (one per lifetime),
        # each carrying a chain= segment. They MUST be identical.
        done_events = [e for e in events if e.get("type") == "response.output_text.done"]
        # Edge case: pre-crash lifetime may not have reached output_text.done
        # if SIGKILL landed before its post-sleep phase. In that case we
        # still have lifetime 1's done event; the assertion degenerates to
        # "chain id present + matches response_id" rather than "matches
        # lifetime 0's value".
        assert done_events, "No response.output_text.done in replay. Event types: " f"{[e.get('type') for e in events]}"

        chain_ids = []
        for d in done_events:
            text = d.get("text", "")
            chain = _extract_chain_id(text)
            assert chain is not None, f"Final text missing chain= segment: {text!r}"
            chain_ids.append(chain)

        # Stability across attempts (when we have multiple done events).
        if len(chain_ids) >= 2:
            assert chain_ids[0] == chain_ids[1], (
                "context.conversation_chain_id MUST be identical across "
                f"recovery attempts. Got lifetime-0 chain={chain_ids[0]!r}, "
                f"lifetime-1 chain={chain_ids[1]!r}."
            )

        # For a standalone response (no conversation_id, no previous_response_id),
        # the chain id is a stable, opaque hex hash derived from the response id's
        # embedded partition key — NOT necessarily distinct from the response id.
        # Since Spec 038 the chain id is a native id: a chain-scoped
        # ``cchain_…`` / ``rchain_…`` id, OR the ``response_id`` verbatim for a
        # non-steerable one-shot. It must be a valid native id and identical
        # across recovery attempts.
        import re as _re

        for chain in chain_ids:
            assert (
                _re.fullmatch(r"[a-z]+_[A-Za-z0-9]+", chain) and len(chain) <= 128
            ), f"Chain id must be a native id (<=128 chars). Got chain={chain!r}."
        assert (
            len(set(chain_ids)) == 1
        ), f"context.conversation_chain_id MUST be stable across all observations. Got {chain_ids!r}."
    finally:
        await harness.close()
