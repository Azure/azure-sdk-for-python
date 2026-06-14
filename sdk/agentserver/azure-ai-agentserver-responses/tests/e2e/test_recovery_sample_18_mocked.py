# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Mocked e2e test for sample_18 — durable Copilot SDK handler.

Pins:

1. Fresh entry calls ``create_session(session_id=<new uuid>)`` and
   ``session.send`` exactly once.
2. Recovered entry uses ``resume_session(<stored uuid>, …)`` — never
   ``create_session``.
3. Recovered entry where Copilot's persisted event log already has our
   input as its most recent UserMessageData does NOT call
   ``session.send`` again.
4. Recovered entry where the event log does NOT contain our input DOES
   call ``session.send`` once.
5. Pre-entry STEERED sends the input (preserving conversation context)
   and emits ``response.completed``.
6. Pre-entry CLIENT_CANCELLED / SHUTTING_DOWN return without touching
   the SDK.
7. The sample uses no ``last_processed_input_item_id`` watermark and
   never calls ``durability.metadata.flush()``.
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
    input_text: str = "test prompt",
) -> ResponseContext:
    durability = DurabilityContext(
        entry_mode=entry_mode,  # type: ignore[arg-type]
        retry_attempt=0 if entry_mode == "fresh" else 1,
        was_steered=False,
        pending_inputs=0,
        metadata=metadata or {},
    )
    context = MagicMock(spec=ResponseContext)
    context.response_id = response_id
    # (Spec 013 US3) Stable chain id derived from the request. For mocked
    # fresh-entry tests this is just the response_id (no prev / no conv).
    context.conversation_chain_id = response_id
    context.durability = durability
    context.cancellation_reason = None

    async def _get_input_text() -> str:
        return input_text

    async def _get_input_items(*, resolve_references: bool = True) -> list[Any]:
        item = MagicMock()
        item.id = "item-test"
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


def _make_session_stub_classes(
    reply_text: str = "fizzbuzz",
    history_events: list[Any] | None = None,
):
    """Return (CopilotClient_stub, send_calls, create_calls, resume_calls)."""
    from copilot.generated.session_events import (
        AssistantMessageData,
        SessionIdleData,
    )

    send_calls: list[str] = []
    create_calls: list[dict[str, Any]] = []
    resume_calls: list[dict[str, Any]] = []
    initial_history = list(history_events or [])

    class _Event:
        def __init__(self, data: Any) -> None:
            self.data = data

    class _StubSession:
        def __init__(self, **kwargs: Any) -> None:
            self.kwargs = kwargs
            self._handlers: list[Any] = []
            self._history: list[Any] = list(initial_history)

        async def __aenter__(self) -> "_StubSession":
            return self

        async def __aexit__(self, *args: Any) -> None:
            return None

        def on(self, callback: Any) -> None:
            self._handlers.append(callback)

        async def get_messages(self) -> list[Any]:
            return list(self._history)

        async def send(self, prompt: str) -> None:
            send_calls.append(prompt)
            for handler in self._handlers:
                handler(_Event(AssistantMessageData(content=reply_text, message_id="m1")))
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

        async def resume_session(self, session_id: str, **kwargs: Any) -> _StubSession:
            resume_calls.append({"session_id": session_id, **kwargs})
            return _StubSession(session_id=session_id, **kwargs)

    return _StubClient, send_calls, create_calls, resume_calls


def _make_user_event(text: str) -> Any:
    """Build a SessionEvent-like with UserMessageData payload."""
    from copilot.generated.session_events import UserMessageData

    event = MagicMock()
    event.data = UserMessageData(
        content=text,
        agent_mode=None,
        attachments=None,
        interaction_id=None,
        native_document_path_fallback_paths=None,
        source=None,
        supported_native_document_mime_types=None,
        transformed_content=None,
    )
    return event


def _make_assistant_event(text: str) -> Any:
    from copilot.generated.session_events import AssistantMessageData

    event = MagicMock()
    event.data = AssistantMessageData(content=text, message_id="m-stub")
    return event


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestSample18FreshEntry:
    async def test_fresh_entry_creates_session_and_sends_once(self) -> None:
        from samples import sample_18_durable_copilot as mod  # type: ignore[import-not-found]

        stub_client, send_calls, create_calls, resume_calls = _make_session_stub_classes()
        with patch.object(mod, "CopilotClient", stub_client):
            response_id = IdGenerator.new_response_id()
            ctx = _make_context(response_id=response_id)
            events = await _drive(mod.handler, _make_request(), ctx, asyncio.Event())

        assert len(create_calls) == 1
        # (Spec 013 US3) Sample 18 now uses ``context.conversation_chain_id``
        # — for a first turn (no previous_response_id, no conversation_id)
        # the chain id is the response_id itself.
        assert create_calls[0].get("session_id") == response_id
        assert resume_calls == []
        assert send_calls == ["test prompt"]
        assert "response.completed" in [_event_type(e) for e in events]


@pytest.mark.asyncio
class TestSample18RecoveryUsesResumeSession:
    async def test_recovery_uses_resume_session_not_create(self) -> None:
        from samples import sample_18_durable_copilot as mod  # type: ignore[import-not-found]

        # History already has our input — recovery skips send.
        history = [_make_user_event("test prompt")]
        stub_client, send_calls, create_calls, resume_calls = _make_session_stub_classes(history_events=history)
        with patch.object(mod, "CopilotClient", stub_client):
            response_id = IdGenerator.new_response_id()
            ctx = _make_context(
                response_id=response_id,
                entry_mode="recovered",
            )
            await _drive(mod.handler, _make_request(), ctx, asyncio.Event())

        # Recovery used resume_session, not create_session.
        assert create_calls == []
        assert len(resume_calls) == 1
        # (Spec 013 US3) Stable chain id == response_id for first-turn chain;
        # recovery resumes against the same id.
        assert resume_calls[0]["session_id"] == response_id
        # And no send because history already has our input.
        assert send_calls == []


@pytest.mark.asyncio
class TestSample18RecoveryWithMissingInput:
    async def test_recovery_sends_when_input_not_in_history(self) -> None:
        from samples import sample_18_durable_copilot as mod  # type: ignore[import-not-found]

        # History has a prior turn but not the current input.
        history = [
            _make_user_event("prior question"),
            _make_assistant_event("prior reply"),
        ]
        stub_client, send_calls, create_calls, resume_calls = _make_session_stub_classes(history_events=history)
        with patch.object(mod, "CopilotClient", stub_client):
            ctx = _make_context(
                response_id=IdGenerator.new_response_id(),
                entry_mode="recovered",
            )
            await _drive(mod.handler, _make_request(), ctx, asyncio.Event())

        assert create_calls == []
        assert len(resume_calls) == 1
        assert send_calls == ["test prompt"]


@pytest.mark.asyncio
class TestSample18LiveDeltas:
    """Live delta streaming + recovery replay (Spec 013 feedback #3)."""

    async def test_fresh_entry_emits_delta_live_not_batched(self) -> None:
        """On a fresh send, the assistant content arrives as an
        output_text.delta event (not silently accumulated and dumped at
        the end)."""
        from samples import sample_18_durable_copilot as mod  # type: ignore[import-not-found]

        stub_client, send_calls, _create_calls, _resume_calls = _make_session_stub_classes(reply_text="hello world")
        with patch.object(mod, "CopilotClient", stub_client):
            ctx = _make_context(response_id=IdGenerator.new_response_id())
            events = await _drive(mod.handler, _make_request(), ctx, asyncio.Event())

        assert send_calls == ["test prompt"]
        # The delta event carries the reply text exactly once.
        delta_events = [e for e in events if _event_type(e) == "response.output_text.delta"]
        assert delta_events, "expected at least one output_text.delta event"
        deltas = [getattr(e, "delta", None) or e.get("delta") for e in delta_events]
        assert "hello world" in "".join(d for d in deltas if d)

    async def test_recovery_replays_accumulated_assistant_text_as_one_delta(
        self,
    ) -> None:
        """On recovery with upstream assistant content already present
        for the current turn, the handler emits a single replay delta
        containing the accumulated text *before* any new live deltas."""
        from samples import sample_18_durable_copilot as mod  # type: ignore[import-not-found]

        # Upstream session already has: user "test prompt" → assistant "partial".
        # On recovery the handler should replay "partial" as a single delta.
        history = [
            _make_user_event("test prompt"),
            _make_assistant_event("partial accumulated reply"),
        ]
        stub_client, send_calls, create_calls, resume_calls = _make_session_stub_classes(
            history_events=history,
        )
        with patch.object(mod, "CopilotClient", stub_client):
            ctx = _make_context(
                response_id=IdGenerator.new_response_id(),
                entry_mode="recovered",
            )
            events = await _drive(mod.handler, _make_request(), ctx, asyncio.Event())

        # No fresh session, only resume — matches existing recovery contract.
        assert create_calls == []
        assert len(resume_calls) == 1
        # No re-send because upstream already has our user message.
        assert send_calls == []
        # The accumulated assistant text was replayed as a single delta.
        delta_events = [e for e in events if _event_type(e) == "response.output_text.delta"]
        assert delta_events, "expected at least one output_text.delta on recovery"
        deltas = [getattr(e, "delta", None) or e.get("delta") for e in delta_events]
        joined = "".join(d for d in deltas if d)
        assert "partial accumulated reply" in joined

    async def test_recovery_with_no_accumulated_text_emits_no_replay_delta(
        self,
    ) -> None:
        """If the upstream session has no assistant content for the
        current turn (e.g. crashed pre-response.in_progress), recovery
        should NOT emit a spurious replay delta."""
        from samples import sample_18_durable_copilot as mod  # type: ignore[import-not-found]

        # Upstream has only the user message, no assistant content yet.
        history = [_make_user_event("test prompt")]
        stub_client, send_calls, _create_calls, resume_calls = _make_session_stub_classes(
            history_events=history,
        )
        with patch.object(mod, "CopilotClient", stub_client):
            ctx = _make_context(
                response_id=IdGenerator.new_response_id(),
                entry_mode="recovered",
            )
            events = await _drive(mod.handler, _make_request(), ctx, asyncio.Event())

        assert len(resume_calls) == 1
        assert send_calls == []
        delta_events = [e for e in events if _event_type(e) == "response.output_text.delta"]
        # No replay text, no live deltas (stub has no new events to deliver
        # because we didn't call send).
        deltas = [getattr(e, "delta", None) or e.get("delta") for e in delta_events]
        assert all(not d for d in deltas), deltas

    async def test_handler_uses_queue_for_live_streaming(self) -> None:
        """Source-level guard: the handler uses an asyncio.Queue for
        live delta forwarding rather than a batched list pattern."""
        from samples import sample_18_durable_copilot as mod  # type: ignore[import-not-found]
        import inspect

        src = inspect.getsource(mod.handler)
        assert "asyncio.Queue" in src, (
            "handler should drive live deltas through asyncio.Queue, not a " "batched list emitted after idle"
        )
        # And no leftover batched-accumulation pattern from the prior design.
        assert "reply_parts" not in src, (
            "handler should not accumulate a list of parts and emit them "
            "after idle; deltas should flow live as they arrive"
        )

    async def test_handler_recovery_replay_helper_is_invoked(self) -> None:
        """Source-level guard: the handler invokes the dedicated
        recovery-replay helper for upstream accumulated text."""
        from samples import sample_18_durable_copilot as mod  # type: ignore[import-not-found]
        import inspect

        src = inspect.getsource(mod.handler)
        assert "_gather_accumulated_assistant_text" in src, (
            "handler should invoke _gather_accumulated_assistant_text on "
            "recovery to replay upstream-accumulated text as a single delta"
        )


@pytest.mark.asyncio
class TestSample18NoWatermarkOrFlush:
    async def test_no_last_processed_input_item_id(self) -> None:
        from samples import sample_18_durable_copilot as mod  # type: ignore[import-not-found]
        import inspect

        src = inspect.getsource(mod)
        assert "last_processed_input_item_id" not in src, (
            "sample_18 must use upstream history (session.get_messages) for "
            "deduplication, not a handler-managed watermark"
        )

    async def test_no_metadata_flush_call(self) -> None:
        from samples import sample_18_durable_copilot as mod  # type: ignore[import-not-found]
        import inspect

        src = inspect.getsource(mod)
        assert ".metadata.flush(" not in src, (
            "sample_18 must not depend on metadata flush ordering; the " "upstream session is the source of truth"
        )


@pytest.mark.asyncio
class TestSample18PreEntrySteeredPreservesInput:
    async def test_pre_entry_steered_sends_input_and_completes(self) -> None:
        from samples import sample_18_durable_copilot as mod  # type: ignore[import-not-found]

        stub_client, send_calls, create_calls, resume_calls = _make_session_stub_classes()
        with patch.object(mod, "CopilotClient", stub_client):
            ctx = _make_context(response_id=IdGenerator.new_response_id())
            ctx.cancellation_reason = CancellationReason.STEERED
            signal = asyncio.Event()
            signal.set()

            events = await _drive(mod.handler, _make_request(), ctx, signal)

        assert send_calls == ["test prompt"]
        assert "response.completed" in [_event_type(e) for e in events]


@pytest.mark.asyncio
class TestSample18PreEntryOtherCancellationDoesNotTouchSDK:
    async def test_pre_entry_client_cancelled_does_not_touch_sdk(self) -> None:
        from samples import sample_18_durable_copilot as mod  # type: ignore[import-not-found]

        stub_client, send_calls, create_calls, resume_calls = _make_session_stub_classes()
        with patch.object(mod, "CopilotClient", stub_client):
            ctx = _make_context(response_id=IdGenerator.new_response_id())
            ctx.cancellation_reason = CancellationReason.CLIENT_CANCELLED
            signal = asyncio.Event()
            signal.set()

            events = await _drive(mod.handler, _make_request(), ctx, signal)

        assert create_calls == []
        assert resume_calls == []
        assert send_calls == []
        assert "response.completed" not in [_event_type(e) for e in events]

    async def test_pre_entry_shutdown_does_not_touch_sdk(self) -> None:
        from samples import sample_18_durable_copilot as mod  # type: ignore[import-not-found]

        stub_client, send_calls, create_calls, resume_calls = _make_session_stub_classes()
        with patch.object(mod, "CopilotClient", stub_client):
            ctx = _make_context(response_id=IdGenerator.new_response_id())
            ctx.cancellation_reason = CancellationReason.SHUTTING_DOWN
            signal = asyncio.Event()
            signal.set()

            events = await _drive(mod.handler, _make_request(), ctx, signal)

        assert create_calls == []
        assert resume_calls == []
        assert send_calls == []
        assert "response.completed" not in [_event_type(e) for e in events]
