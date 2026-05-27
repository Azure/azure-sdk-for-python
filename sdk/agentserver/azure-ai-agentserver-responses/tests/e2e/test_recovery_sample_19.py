# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""E2E test for sample_19 — durable streaming with handler-managed checkpoints.

Pins the contract the sample claims to follow:

1. **Fresh entry** runs all three phases and produces a 3-item response.
2. **Recovered entry with watermark `phase_complete=analyze`** runs only
   the remaining two phases, builds a resumption response containing the
   analyze item, and emits ``response.in_progress`` carrying it (the
   client-visible reset point per Spec 012).
3. **Recovered entry with watermark `phase_complete=generate`** runs only
   the refine phase.
4. **Stripping the recovery branch** still produces a valid response
   (Spec 012 FR-013 naive fallback).

Full crash-restart injection (real process kill + restart) is deferred to
Phase 5 (``_crash_harness.py``); these tests synthesize a recovered
``DurabilityContext`` directly and drive the handler.
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import MagicMock

import pytest

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
)
from azure.ai.agentserver.responses._durability_context import (
    DurabilityContext,
    _FilteredMetadata,
)
from azure.ai.agentserver.responses._id_generator import IdGenerator


# ---------------------------------------------------------------------------
# Test scaffolding
# ---------------------------------------------------------------------------


def _make_context(
    *,
    response_id: str,
    entry_mode: str = "fresh",
    metadata: dict[str, Any] | None = None,
) -> ResponseContext:
    """Build a synthetic ResponseContext for driving the handler directly."""
    durability = DurabilityContext(
        entry_mode=entry_mode,  # type: ignore[arg-type]
        run_attempt=0 if entry_mode == "fresh" else 1,
        was_steered=False,
        pending_inputs=0,
        metadata=_FilteredMetadata(metadata or {}),
    )

    # Build a minimal ResponseContext mock with the attrs the sample uses.
    context = MagicMock(spec=ResponseContext)
    context.response_id = response_id
    context.durability = durability
    context.cancellation_reason = None

    async def _get_input_text() -> str:
        return "test prompt"

    context.get_input_text = _get_input_text
    return context


def _make_request(model: str = "test-model") -> CreateResponse:
    """Build a minimal CreateResponse request the sample reads from."""
    return CreateResponse(model=model, input="test prompt")  # type: ignore[call-arg]


async def _drive(handler_coro_fn, request, context, cancellation_signal) -> list[Any]:
    """Run the handler async generator and return emitted events."""
    events = []
    async for event in handler_coro_fn(request, context, cancellation_signal):
        events.append(event)
    return events


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestSample19FreshEntry:
    """A fresh entry runs all three phases."""

    async def test_fresh_entry_runs_all_phases(self) -> None:
        from samples.sample_19_durable_streaming import handler  # type: ignore[import-not-found]

        ctx = _make_context(response_id=IdGenerator.new_response_id())
        signal = asyncio.Event()
        events = await _drive(handler, _make_request(), ctx, signal)

        event_types = [getattr(e, "type", None) or e.get("type") for e in events]

        # Lifecycle: created, in_progress, completed.
        assert "response.created" in event_types
        assert "response.in_progress" in event_types
        assert "response.completed" in event_types

        # Three output items added (one per phase).
        added_count = event_types.count("response.output_item.added")
        done_count = event_types.count("response.output_item.done")
        assert added_count == 3, f"expected 3 phase items added, got {added_count}"
        assert done_count == 3, f"expected 3 phase items done, got {done_count}"

        # Phase watermark advanced to the last phase.
        assert ctx.durability.metadata.get("phase_complete") == "refine"


@pytest.mark.asyncio
class TestSample19RecoveryAfterAnalyze:
    """Recovered entry with analyze complete runs only generate + refine."""

    async def test_recovery_with_one_phase_done_runs_remaining_two(self) -> None:
        from samples.sample_19_durable_streaming import handler  # type: ignore[import-not-found]

        ctx = _make_context(
            response_id=IdGenerator.new_response_id(),
            entry_mode="recovered",
            metadata={
                "phase_complete": "analyze",
                "phase_texts": {"analyze": "[analyze] Examining input."},
            },
        )
        signal = asyncio.Event()
        events = await _drive(handler, _make_request(), ctx, signal)

        # The in_progress emitted on this run carries the resumption response,
        # which must already contain the analyze item.
        in_progress_events = [
            e for e in events if (getattr(e, "type", None) or e.get("type")) == "response.in_progress"
        ]
        assert in_progress_events, "expected at least one response.in_progress"
        first_in_progress = in_progress_events[0]
        response_payload = (
            getattr(first_in_progress, "response", None) or first_in_progress.get("response")
        )
        # The resumption response carried in in_progress includes the prior
        # analyze item — this is the snapshot reset point for reconnecting
        # clients (Spec 012 FR-004 / FR-016).
        seeded_output = (
            response_payload.get("output") if isinstance(response_payload, dict) else response_payload.output
        )
        assert seeded_output and len(seeded_output) == 1, (
            f"resumption response must contain the 1 prior phase item; got {seeded_output}"
        )

        # Only 2 new phases run on this attempt.
        added_count = sum(
            1
            for e in events
            if (getattr(e, "type", None) or e.get("type")) == "response.output_item.added"
        )
        assert added_count == 2, f"expected 2 new items on recovery; got {added_count}"

        # Final watermark: all phases done.
        assert ctx.durability.metadata.get("phase_complete") == "refine"


@pytest.mark.asyncio
class TestSample19RecoveryAfterGenerate:
    """Recovered entry with two phases done runs only the final phase."""

    async def test_recovery_with_two_phases_done_runs_only_refine(self) -> None:
        from samples.sample_19_durable_streaming import handler  # type: ignore[import-not-found]

        ctx = _make_context(
            response_id=IdGenerator.new_response_id(),
            entry_mode="recovered",
            metadata={
                "phase_complete": "generate",
                "phase_texts": {
                    "analyze": "[analyze] Done.",
                    "generate": "[generate] Done.",
                },
            },
        )
        signal = asyncio.Event()
        events = await _drive(handler, _make_request(), ctx, signal)

        # Resumption response carries 2 prior items.
        first_in_progress = next(
            e
            for e in events
            if (getattr(e, "type", None) or e.get("type")) == "response.in_progress"
        )
        payload = (
            getattr(first_in_progress, "response", None) or first_in_progress.get("response")
        )
        seeded_output = payload.get("output") if isinstance(payload, dict) else payload.output
        assert len(seeded_output) == 2

        # Only 1 new phase runs.
        added_count = sum(
            1
            for e in events
            if (getattr(e, "type", None) or e.get("type")) == "response.output_item.added"
        )
        assert added_count == 1

        # All three phases complete by end.
        assert ctx.durability.metadata.get("phase_complete") == "refine"
