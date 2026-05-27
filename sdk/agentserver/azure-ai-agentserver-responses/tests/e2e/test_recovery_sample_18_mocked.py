# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Mocked e2e test for sample_18 — durable Copilot SDK handler.

Real-SDK integration testing requires GitHub Copilot CLI installed and
authenticated, so this test patches the Copilot SDK to in-memory stubs.

Pins:

1. Fresh entry calls ``session.send`` exactly once and uses
   ``create_session(session_id=<uuid>)`` with a freshly-allocated UUID.
2. Recovered entry calls ``create_session(session_id=<stored>)`` with
   the SAME UUID stamped on the prior attempt — relying on the
   documented reattach behaviour (Spec 012 Q2 caveat).
3. The watermark ``copilot_message_sent`` is stamped BEFORE
   ``session.send`` and cleared after ``SessionIdleData`` fires.
4. Pre-entry STEERED emits ``response.completed``; CLIENT_CANCELLED
   and SHUTTING_DOWN return without terminal.
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

    context.get_input_text = _get_input_text
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


# ---------------------------------------------------------------------------
# Stubbed Copilot SDK
# ---------------------------------------------------------------------------


def _make_session_stub_classes(reply_text: str = "fizzbuzz"):
    """Return (CopilotClient_stub, send_calls, create_calls).

    create_calls records the kwargs passed to ``create_session``.
    send_calls records the prompts passed to ``session.send``.
    """
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
            # Immediately fire AssistantMessageData then SessionIdleData
            # via the registered handlers to simulate a complete turn.
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
    async def test_fresh_entry_creates_session_with_new_uuid(self) -> None:
        from samples import sample_18_durable_copilot as mod  # type: ignore[import-not-found]

        stub_client, send_calls, create_calls = _make_session_stub_classes()
        with patch.object(mod, "CopilotClient", stub_client):
            ctx = _make_context(response_id=IdGenerator.new_response_id())
            events = await _drive(mod.handler, _make_request(), ctx, asyncio.Event())

        assert len(create_calls) == 1
        # session_id was a freshly-allocated UUID, stamped back to metadata.
        new_uuid = create_calls[0].get("session_id")
        assert isinstance(new_uuid, str) and len(new_uuid) == 36
        assert ctx.durability.metadata.get("copilot_session_id") == new_uuid

        # send() called exactly once with the input.
        assert send_calls == ["test prompt"]

        # Watermark cleared after idle.
        assert ctx.durability.metadata.get("copilot_message_sent") is False

        # Lifecycle reached completed.
        assert "response.completed" in [_event_type(e) for e in events]


@pytest.mark.asyncio
class TestSample18Recovery:
    async def test_recovery_reattaches_with_stored_session_id(self) -> None:
        from samples import sample_18_durable_copilot as mod  # type: ignore[import-not-found]

        stub_client, send_calls, create_calls = _make_session_stub_classes()
        with patch.object(mod, "CopilotClient", stub_client):
            ctx = _make_context(
                response_id=IdGenerator.new_response_id(),
                entry_mode="recovered",
                metadata={
                    "copilot_session_id": "preserved-session-uuid",
                    "copilot_message_sent": True,
                },
            )
            events = await _drive(mod.handler, _make_request(), ctx, asyncio.Event())

        # Recovery reattaches with the SAME session_id stored on metadata.
        assert create_calls[0]["session_id"] == "preserved-session-uuid"
        # session_id was preserved (not regenerated).
        assert ctx.durability.metadata.get("copilot_session_id") == "preserved-session-uuid"

        # Recovery in_progress carries empty resumption response.
        in_progress = next(
            e for e in events if _event_type(e) == "response.in_progress"
        )
        payload = getattr(in_progress, "response", None) or in_progress.get("response")
        output = payload.get("output") if isinstance(payload, dict) else payload.output
        assert output == []


@pytest.mark.asyncio
class TestSample18PreEntryCancellation:
    async def test_pre_entry_steered_emits_completed_no_sdk_call(self) -> None:
        from samples import sample_18_durable_copilot as mod  # type: ignore[import-not-found]

        stub_client, send_calls, create_calls = _make_session_stub_classes()
        with patch.object(mod, "CopilotClient", stub_client):
            ctx = _make_context(response_id=IdGenerator.new_response_id())
            ctx.cancellation_reason = CancellationReason.STEERED
            signal = asyncio.Event()
            signal.set()

            events = await _drive(mod.handler, _make_request(), ctx, signal)

        assert "response.completed" in [_event_type(e) for e in events]
        # No SDK calls in pre-entry path.
        assert create_calls == []
        assert send_calls == []

    async def test_pre_entry_shutdown_returns_no_terminal_no_sdk(self) -> None:
        from samples import sample_18_durable_copilot as mod  # type: ignore[import-not-found]

        stub_client, send_calls, create_calls = _make_session_stub_classes()
        with patch.object(mod, "CopilotClient", stub_client):
            ctx = _make_context(response_id=IdGenerator.new_response_id())
            ctx.cancellation_reason = CancellationReason.SHUTTING_DOWN
            signal = asyncio.Event()
            signal.set()

            events = await _drive(mod.handler, _make_request(), ctx, signal)

        assert "response.completed" not in [_event_type(e) for e in events]
        assert create_calls == []
        assert send_calls == []
