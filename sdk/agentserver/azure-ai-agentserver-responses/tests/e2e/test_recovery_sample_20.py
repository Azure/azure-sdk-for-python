# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""E2E test for sample_20 — resilient steerable handler with cancellation × recovery.

Pins:

1. Fresh entry produces a single message item + emits ``completed``.
2. Recovered entry seeds the stream with an empty resumption response,
   emits ``response.in_progress`` (the reset point), then re-streams a
   single fresh message item.
3. Pre-entry STEERED cancellation emits ``completed`` (no output).
4. Pre-entry CLIENT_CANCELLED returns without terminal (framework
   forces ``cancelled``).
5. Mid-stream SHUTTING_DOWN closes builders, returns without terminal.
6. ``turn_count`` metadata watermark persists across simulated turns.
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
from azure.ai.agentserver.responses._id_generator import IdGenerator
from azure.ai.agentserver.responses._resilience_context import _DeveloperMetadataFacade


def _make_context(
    *,
    response_id: str,
    entry_mode: str = "fresh",
    metadata: dict[str, Any] | None = None,
) -> ResponseContext:
    context = MagicMock(spec=ResponseContext)
    context.response_id = response_id
    context.is_recovery = entry_mode == "recovered"
    context.is_steered_turn = False
    context.pending_input_count = 0
    context.conversation_chain_metadata = _DeveloperMetadataFacade(metadata or {})
    context._cancellation_signal = asyncio.Event()
    context.shutdown = asyncio.Event()
    context.client_cancelled = False

    async def _get_input_text() -> str:
        return "test prompt"

    context.get_input_text = _get_input_text

    async def _exit_for_recovery() -> Any:
        from azure.ai.agentserver.responses import ResponseExitForRecovery

        raise ResponseExitForRecovery()

    context.exit_for_recovery = _exit_for_recovery
    return context


def _make_request() -> CreateResponse:
    return CreateResponse(model="test-model", input="test prompt")  # type: ignore[call-arg]


async def _drive(handler_coro_fn, request, context) -> list[Any]:
    events = []
    async for event in handler_coro_fn(request, context, context._cancellation_signal):
        events.append(event)
    return events


def _event_type(e: Any) -> str | None:
    return getattr(e, "type", None) or (e.get("type") if isinstance(e, dict) else None)


@pytest.mark.asyncio
class TestSample20FreshEntry:
    async def test_fresh_entry_produces_message_and_completed(self) -> None:
        from samples.sample_20_resilient_steering import handler  # type: ignore[import-not-found]

        ctx = _make_context(response_id=IdGenerator.new_response_id())
        events = await _drive(handler, _make_request(), ctx)
        types = [_event_type(e) for e in events]

        assert "response.created" in types
        assert "response.in_progress" in types
        assert "response.completed" in types
        assert types.count("response.output_item.added") == 1
        assert types.count("response.output_item.done") == 1
        assert ctx.conversation_chain_metadata.get("turn_count") == 1


@pytest.mark.asyncio
class TestSample20Recovery:
    async def test_recovered_entry_emits_reset_in_progress_then_fresh_content(
        self,
    ) -> None:
        from samples.sample_20_resilient_steering import handler  # type: ignore[import-not-found]

        # Recovery: turn_count carried over from a prior attempt.
        ctx = _make_context(
            response_id=IdGenerator.new_response_id(),
            entry_mode="recovered",
            metadata={"turn_count": 1},
        )
        events = await _drive(handler, _make_request(), ctx)

        # in_progress carries an empty resumption response (single-turn
        # handler can't safely carry partial token output forward).
        in_progress = next(e for e in events if _event_type(e) == "response.in_progress")
        payload = getattr(in_progress, "response", None) or in_progress.get("response")
        output_field = payload.get("output") if isinstance(payload, dict) else payload.output
        assert output_field == [], "recovery in_progress must carry empty resumption"

        # The recovered attempt re-streams a single message item fresh.
        assert sum(1 for e in events if _event_type(e) == "response.output_item.added") == 1
        # turn_count incremented from carry-over watermark.
        assert ctx.conversation_chain_metadata.get("turn_count") == 2


@pytest.mark.asyncio
class TestSample20PreEntryCancellation:
    async def test_pre_entry_steered_emits_completed_no_output(self) -> None:
        from samples.sample_20_resilient_steering import handler  # type: ignore[import-not-found]

        ctx = _make_context(response_id=IdGenerator.new_response_id())
        # Steering: cancellation_signal fires AND pending_input_count > 0.
        ctx._cancellation_signal.set()
        ctx.pending_input_count = 1
        signal = asyncio.Event()
        signal.set()

        events = await _drive(handler, _make_request(), ctx)
        types = [_event_type(e) for e in events]
        assert "response.created" in types
        assert "response.completed" in types
        assert "response.output_item.added" not in types

    async def test_pre_entry_client_cancelled_returns_without_terminal(self) -> None:
        from samples.sample_20_resilient_steering import handler  # type: ignore[import-not-found]

        ctx = _make_context(response_id=IdGenerator.new_response_id())
        ctx.client_cancelled = True

        ctx._cancellation_signal.set()
        signal = asyncio.Event()
        signal.set()

        events = await _drive(handler, _make_request(), ctx)
        types = [_event_type(e) for e in events]
        # Only `created` is emitted; no terminal — framework forces cancelled.
        assert types == ["response.created"]


@pytest.mark.asyncio
class TestSample20Shutdown:
    async def test_pre_entry_shutdown_defers_to_recovery(self) -> None:
        from azure.ai.agentserver.responses import ResponseExitForRecovery
        from samples.sample_20_resilient_steering import handler  # type: ignore[import-not-found]

        ctx = _make_context(response_id=IdGenerator.new_response_id())
        # Shutdown does NOT fire cancellation_signal — they are distinct surfaces.
        ctx.shutdown.set()

        # The handler emits `response.created`, then signals recovery via the
        # unified primitive `await context.exit_for_recovery()`, which raises
        # ResponseExitForRecovery (the orchestrator translates it to
        # next-lifetime recovery — no terminal is emitted).
        events: list[Any] = []
        with pytest.raises(ResponseExitForRecovery):
            async for event in handler(_make_request(), ctx, ctx._cancellation_signal):
                events.append(event)
        types = [_event_type(e) for e in events]
        assert types == ["response.created"]
