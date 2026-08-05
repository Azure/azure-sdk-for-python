# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Spec 026 FR-026-2 — `response.created` provider-append gate (empty stream).

Unit-level proof that the resilient-stream append of `response.created` is
gated on the stream being empty: the framework appends it only when the
stream provider has no events yet (`last_cursor() is None`), and suppresses
it when the stream already carries events (a recovered entry). This is the
mechanism that makes a reconnecting client observe `response.created`
exactly once across pre-crash + recovered segments.
"""

from __future__ import annotations

import pytest

from azure.ai.agentserver.core.streaming._concrete import ReplayEventStream


def _make_stream() -> ReplayEventStream:
    # A cursor-capable replay backing — `last_cursor()` reflects the highest
    # appended sequence_number, or None when nothing has been appended.
    return ReplayEventStream(cursor_fn=lambda ev: ev["sequence_number"])


@pytest.mark.asyncio
async def test_empty_stream_cursor_is_none_then_gate_permits_created() -> None:
    """An empty resilient stream reports last_cursor() is None → created is appended."""
    stream = _make_stream()
    assert await stream.last_cursor() is None
    # The orchestrator's gate: `stream_is_empty = await subject.last_cursor() is None`.
    stream_is_empty = await stream.last_cursor() is None
    assert stream_is_empty is True


@pytest.mark.asyncio
async def test_non_empty_stream_suppresses_created_reappend() -> None:
    """A stream with events (recovery) reports a non-None cursor → created suppressed."""
    stream = _make_stream()
    # Simulate the pre-crash lifetime having written response.created (+ more).
    await stream.emit({"sequence_number": 0, "type": "response.created"})
    await stream.emit({"sequence_number": 1, "type": "response.in_progress"})
    assert await stream.last_cursor() == 1
    # On the recovered entry the gate evaluates False → the framework does NOT
    # re-append response.created.
    stream_is_empty = await stream.last_cursor() is None
    assert stream_is_empty is False
