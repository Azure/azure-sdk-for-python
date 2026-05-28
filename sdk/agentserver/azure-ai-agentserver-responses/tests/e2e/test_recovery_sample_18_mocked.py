# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Mocked e2e test for sample_18 — durable Copilot SDK handler.

Pins:

1. Fresh entry creates a session with a fresh UUID and calls
   ``session.send`` exactly once. The ``last_processed_input_item_id``
   watermark is updated.
2. Recovered entry with the watermark already pointing at the current
   input does NOT call ``session.send`` again.
3. Recovered entry where the watermark is stale DOES call
   ``session.send`` once, and reattaches to the same stored session id.
4. Pre-entry STEERED sends the user input to Copilot (preserving
   conversation history) and emits ``response.completed``.
5. Pre-entry CLIENT_CANCELLED / SHUTTING_DOWN return without touching
   the SDK.
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from azure.ai.agentserver.responses import (
    CancellationReason,
    CreateResponse,
    ResponseContext,
)
from azure.ai.agentserver.responses._durability_context import (
    DurabilityContext,
    _FilteredMetadata,
)
from azure.ai.agentserver.responses._id_generator import IdGenerator

try:
    import copilot  # type: ignore[import-untyped]  # noqa: F401
except ImportError:  # pragma: no cover
    pytest.skip("github-copilot-sdk not installed", allow_module_level=True)


# ---------------------------------------------------------------------------
# Scaffolding
# ---------------------------------------------------------------------------


def _make_context(
    *,
    response_id: str,
    entry_mode: str = "fresh",
    metadata: dict[str, Any] | None = None,
    input_item_id: str = "item-1",
) -> ResponseContext:
    durability = DurabilityContext(
        entry_mode=entry_mode,  # type: ignore[arg-type]
        run_attempt=0 if entry_mode == "fresh" else 1,
        was_steered=False,
        pending_inputs=0,
        metadata=_FilteredMetadata(metadata or {}),
    )
    context = MagicMock(spec=ResponseContext)
    context.response_id = response_id
    context.durability = durability
    context.cancellation_reason = None

    async def _get_input_text() -> str:
        return "test prompt"

    async def _get_input_items(*, resolve_references: bool = True) -> list[Any]:
        item = MagicMock()
        item.id = input_item_id
        return [item]

    context.get_input_text = _get_input_text
    context.get_input_items = _get_input_items
    return context


def _make_request() -> CreateResponse:
    return CreateResponse(model="copilot", input="test prompt")  # type: ignore[call-arg]


async def _drive(handler_coro_fn, request, context, cancellation_signal) -> list[Any]:
    events = []
    async for event in handler_coro_fn(request, context, cancellation_signal):
        events.append(event)
    return events


def _event_type(e: Any) -> str | None:
    return getattr(e, "type", None) or (e.get("type") if isinstance(e, dict) else None)


def _make_session_stub_classes(reply_text: str = "fizzbuzz"):
    """Return (CopilotClient_stub, send_calls, create_calls)."""
    from copilot.generated.session_events import (
        AssistantMessageData,
        SessionIdleData,
    )

    send_calls: list[str] = []
    create_calls: list[dict[str, Any]] = []

    class _Event:
        def __init__(self, data: Any) -> None:
            self.data = data

    class _StubSession:
        def __init__(self, **kwargs: Any) -> None:
            self.kwargs = kwargs
            self._handlers: list[Any] = []

        async def __aenter__(self) -> "_StubSession":
            return self

        async def __aexit__(self, *args: Any) -> None:
            return None

        def on(self, callback: Any) -> None:
            self._handlers.append(callback)

        async def send(self, prompt: str) -> None:
            send_calls.append(prompt)
            for handler in self._handlers:
                handler(
                    _Event(
                        AssistantMessageData(content=reply_text, message_id="m1")
                    )
                )
                handler(_Event(SessionIdleData()))

        async def abort(self) -> None:
            pass

    class _StubClient:
        async def __aenter__(self) -> "_StubClient":
            return self

        async def __aexit__(self, *args: Any) -> None:
            return None

        async def create_session(self, **kwargs: Any) -> _StubSession:
            create_calls.append(kwargs)
            return _StubSession(**kwargs)

    return _StubClient, send_calls, create_calls


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestSample18FreshEntry:
    async def test_fresh_entry_creates_session_sends_once_updates_watermark(self) -> None:
        from samples import sample_18_durable_copilot as mod  # type: ignore[import-not-found]

        stub_client, send_calls, create_calls = _make_session_stub_classes()
        with patch.object(mod, "CopilotClient", stub_client):
            ctx = _make_context(
                response_id=IdGenerator.new_response_id(),
                input_item_id="item-fresh",
            )
            events = await _drive(mod.handler, _make_request(), ctx, asyncio.Event())

        assert len(create_calls) == 1
        new_uuid = create_calls[0].get("session_id")
        assert isinstance(new_uuid, str) and len(new_uuid) == 36
        assert ctx.durability.metadata.get("copilot_session_id") == new_uuid

        assert send_calls == ["test prompt"]
        assert ctx.durability.metadata.get("last_processed_input_item_id") == "item-fresh"

        assert "response.completed" in [_event_type(e) for e in events]


@pytest.mark.asyncio
class TestSample18RecoverySkipsSendWhenWatermarkMatches:
    async def test_recovery_with_matching_watermark_does_not_send(self) -> None:
        from samples import sample_18_durable_copilot as mod  # type: ignore[import-not-found]

        stub_client, send_calls, create_calls = _make_session_stub_classes()
        with patch.object(mod, "CopilotClient", stub_client):
            ctx = _make_context(
                response_id=IdGenerator.new_response_id(),
                entry_mode="recovered",
                metadata={
                    "copilot_session_id": "preserved-session-uuid",
                    "last_processed_input_item_id": "item-already-sent",
                },
                input_item_id="item-already-sent",
            )
            events = await _drive(mod.handler, _make_request(), ctx, asyncio.Event())

        # Session reattached with the same id.
        assert create_calls[0]["session_id"] == "preserved-session-uuid"
        # Watermark matched → no send call this attempt.
        assert send_calls == []


@pytest.mark.asyncio
class TestSample18RecoverySendsWhenWatermarkStale:
    async def test_recovery_with_stale_watermark_does_send(self) -> None:
        from samples import sample_18_durable_copilot as mod  # type: ignore[import-not-found]

        stub_client, send_calls, create_calls = _make_session_stub_classes()
        with patch.object(mod, "CopilotClient", stub_client):
            ctx = _make_context(
                response_id=IdGenerator.new_response_id(),
                entry_mode="recovered",
                metadata={
                    "copilot_session_id": "preserved-session-uuid",
                    "last_processed_input_item_id": "item-from-prior-turn",
                },
                input_item_id="item-current-turn",
            )
            events = await _drive(mod.handler, _make_request(), ctx, asyncio.Event())

        assert create_calls[0]["session_id"] == "preserved-session-uuid"
        assert send_calls == ["test prompt"]
        assert ctx.durability.metadata.get("last_processed_input_item_id") == "item-current-turn"


@pytest.mark.asyncio
class TestSample18PreEntrySteeredPreservesInput:
    async def test_pre_entry_steered_sends_input_and_completes(self) -> None:
        from samples import sample_18_durable_copilot as mod  # type: ignore[import-not-found]

        stub_client, send_calls, create_calls = _make_session_stub_classes()
        with patch.object(mod, "CopilotClient", stub_client):
            ctx = _make_context(
                response_id=IdGenerator.new_response_id(),
                input_item_id="item-steered",
            )
            ctx.cancellation_reason = CancellationReason.STEERED
            signal = asyncio.Event()
            signal.set()

            events = await _drive(mod.handler, _make_request(), ctx, signal)

        assert send_calls == ["test prompt"]
        assert ctx.durability.metadata.get("last_processed_input_item_id") == "item-steered"
        assert "response.completed" in [_event_type(e) for e in events]


@pytest.mark.asyncio
class TestSample18PreEntryOtherCancellationDoesNotTouchSDK:
    async def test_pre_entry_client_cancelled_does_not_touch_sdk(self) -> None:
        from samples import sample_18_durable_copilot as mod  # type: ignore[import-not-found]

        stub_client, send_calls, create_calls = _make_session_stub_classes()
        with patch.object(mod, "CopilotClient", stub_client):
            ctx = _make_context(response_id=IdGenerator.new_response_id())
            ctx.cancellation_reason = CancellationReason.CLIENT_CANCELLED
            signal = asyncio.Event()
            signal.set()

            events = await _drive(mod.handler, _make_request(), ctx, signal)

        assert create_calls == []
        assert send_calls == []
        assert "response.completed" not in [_event_type(e) for e in events]

    async def test_pre_entry_shutdown_does_not_touch_sdk(self) -> None:
        from samples import sample_18_durable_copilot as mod  # type: ignore[import-not-found]

        stub_client, send_calls, create_calls = _make_session_stub_classes()
        with patch.object(mod, "CopilotClient", stub_client):
            ctx = _make_context(response_id=IdGenerator.new_response_id())
            ctx.cancellation_reason = CancellationReason.SHUTTING_DOWN
            signal = asyncio.Event()
            signal.set()

            events = await _drive(mod.handler, _make_request(), ctx, signal)

        assert create_calls == []
        assert send_calls == []
        assert "response.completed" not in [_event_type(e) for e in events]


@pytest.mark.asyncio
class TestSample18FlushBeforeSend:
    """Pin watermark-flush-then-send ordering for the Copilot sample.

    Same contract as sample_17: flush() must come BEFORE session.send().
    A crash between the in-memory watermark write and the actual upstream
    call must not lose the watermark; if it did, the recovered handler
    would re-send and duplicate the user message in Copilot's session.
    """

    async def test_flush_called_before_send_on_watermarked_send(self) -> None:
        from samples import sample_18_durable_copilot as mod  # type: ignore[import-not-found]

        events_in_order: list[str] = []

        stub_client, send_calls, create_calls = _make_session_stub_classes()

        # Patch the session class returned by create_session to record the
        # order in which send() is invoked.
        original_create_session = stub_client.create_session

        async def _recording_create_session(self_inner, **kwargs):
            session = await original_create_session(self_inner, **kwargs)
            original_send = session.send

            async def _recording_send(prompt: str) -> None:
                events_in_order.append("send")
                await original_send(prompt)

            session.send = _recording_send  # type: ignore[method-assign]
            return session

        stub_client.create_session = _recording_create_session  # type: ignore[method-assign]

        with patch.object(mod, "CopilotClient", stub_client):
            ctx = _make_context(
                response_id=IdGenerator.new_response_id(),
                input_item_id="item-flush-2",
            )

            metadata = ctx.durability.metadata
            original_flush = metadata.flush

            async def _recording_flush() -> None:
                events_in_order.append("flush")
                await original_flush()

            metadata.flush = _recording_flush  # type: ignore[assignment]

            await _drive(mod.handler, _make_request(), ctx, asyncio.Event())

        assert "flush" in events_in_order, (
            "sample_18 must call await durability.metadata.flush() after the "
            "watermark write — see backlog B0 (deterministic metadata persistence)"
        )
        flush_idx = events_in_order.index("flush")
        send_idx = events_in_order.index("send")
        assert flush_idx < send_idx, (
            f"flush() must happen BEFORE session.send(). Got order: "
            f"{events_in_order}. If flush is after send, a crash between them "
            f"loses the watermark and recovery re-sends (duplicate user message)."
        )

    async def test_flush_is_at_most_once_per_watermarked_send(self) -> None:
        from samples import sample_18_durable_copilot as mod  # type: ignore[import-not-found]

        flush_count = [0]

        stub_client, _send_calls, _create_calls = _make_session_stub_classes()
        with patch.object(mod, "CopilotClient", stub_client):
            ctx = _make_context(
                response_id=IdGenerator.new_response_id(),
                input_item_id="item-once-2",
            )
            metadata = ctx.durability.metadata
            original_flush = metadata.flush

            async def _counting_flush() -> None:
                flush_count[0] += 1
                await original_flush()

            metadata.flush = _counting_flush  # type: ignore[assignment]

            await _drive(mod.handler, _make_request(), ctx, asyncio.Event())

        assert flush_count[0] >= 1, "sample_18 must flush at least once after watermark write"
        assert flush_count[0] <= 2, (
            f"sample_18 flushed {flush_count[0]} times; expected at most 2. "
            f"Excess flushes suggest watermark is being re-written or dirty "
            f"tracking is broken."
        )
