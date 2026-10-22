# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Spec 032 / B1 — reset-event CONTENT after a real crash recovery.

The streaming sub-contract (``resilience-contract.md`` clause 3) says: on
re-invocation the recovered handler MUST emit a ``response.in_progress`` event
as its first client-visible event **carrying the corrected output items**.

Existing tests assert the reset event EXISTS (with ``seq >`` the pre-crash
events) and assert the TERMINAL ``response.output`` — but none inspects the
``response`` payload INSIDE that post-recovery ``response.in_progress`` event to
prove its ``output`` reflects post-recovery (seeded) state rather than empty or
stale pre-crash content. This module closes that gap.

It uses the Row 11 checkpoint handler with the ``after_checkpoint:1`` cutpoint:
phase 1's checkpoint persists (2 items: ``L0_phase0``, ``L0_phase1``) before the
SIGKILL. On recovery the handler seeds the stream from
``context.persisted_response`` (those 2 items) and resumes at phase 2. The
post-recovery reset ``response.in_progress`` event MUST therefore carry exactly
those 2 corrected items in its ``response.output``.

Real signal only: SIGKILL via ``_crash_harness`` (Path C). No mocked crash, no
fabricated context.

Contract source: ``docs/resilience-contract.md`` § Streaming sub-contract,
clause 3 (``response.in_progress`` reset event carrying corrected output items).
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Callable

import pytest

from tests.e2e._crash_harness import CrashHarness
from tests.e2e.resilience_contract.conftest import (
    LONG_GRACE_S,
    output_text_markers,
    poll_until_terminal,
    post_and_get_response_id,
)


async def _full_stream(client, response_id: str) -> list[dict]:
    """GET the full resilient stream from the start and collect parsed events."""
    events: list[dict] = []
    url = f"/responses/{response_id}?stream=true&starting_after=0"
    async with client.stream("GET", url) as resp:
        assert resp.status_code == 200, resp.status_code
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
async def test_reset_event_carries_corrected_output_items(
    make_checkpoint_harness: Callable[..., CrashHarness],
) -> None:
    """The post-recovery response.in_progress reset event's response.output
    reflects the seeded/post-recovery items, not empty/stale content."""
    harness = make_checkpoint_harness(
        phases=3,
        crash_cutpoint="after_checkpoint:1",  # 2 items persisted before SIGKILL
        shutdown_grace_seconds=LONG_GRACE_S,
    )
    await harness.start()
    try:
        response_id = await post_and_get_response_id(
            harness.client,
            store=True,
            background=True,
            stream=True,
        )
        # Let the fresh handler reach + park at the cutpoint (after phase 1's
        # checkpoint persists), then SIGKILL deterministically.
        await asyncio.sleep(1.0)
        await harness.kill()
        await harness.restart()

        terminal = await poll_until_terminal(harness.client, response_id, timeout_seconds=30.0)
        assert terminal["status"] == "completed", terminal
        # Recovery resumed correctly (sanity): final output is the full plan.
        assert output_text_markers(terminal) == [
            "L0_phase0",
            "L0_phase1",
            "L1_phase2",
        ], terminal

        events = await _full_stream(harness.client, response_id)

        # Identify the post-recovery (second-or-later) response.in_progress
        # reset event. The first response.in_progress belongs to the fresh
        # lifetime; the recovery reset is the one whose sequence_number comes
        # after the last pre-crash event.
        in_progress = [e for e in events if e.get("type") == "response.in_progress"]
        assert len(in_progress) >= 2, (
            "Expected at least two response.in_progress events (fresh + recovery "
            f"reset). Got {len(in_progress)}. Event types: {[e.get('type') for e in events]}"
        )
        reset_event = in_progress[-1]

        # B1 — the reset event MUST carry the corrected output items in its
        # OWN response payload (not merely exist). After the after_checkpoint:1
        # cutpoint, recovery seeds the 2 checkpointed phase items, so the reset
        # event's response.output must carry exactly those 2 corrected items.
        reset_snapshot = reset_event.get("response") or {}
        reset_markers = output_text_markers(reset_snapshot)
        assert reset_markers == ["L0_phase0", "L0_phase1"], (
            "The post-recovery response.in_progress reset event MUST carry the "
            "corrected output items reflecting post-recovery (seeded) state "
            "(resilience-contract.md streaming clause 3). Expected "
            f"['L0_phase0', 'L0_phase1'], got {reset_markers!r}. "
            f"Full reset snapshot output: {reset_snapshot.get('output')!r}"
        )
    finally:
        await harness.close()
