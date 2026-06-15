# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Mocked e2e test for sample_17 — durable Claude Agent SDK handler.

Pins:

1. Fresh entry calls ``client.query`` exactly once. The Claude options
   carry ``session_id=<new uuid>`` (not ``resume``, never ``fork_session``).
2. Recovered entry where the upstream session ALREADY contains our
   input as its most recent user message does NOT call ``client.query``
   again. Recovery options carry ``resume=…``, never ``fork_session``.
3. Recovered entry where upstream session does NOT contain our input
   (e.g. crashed before the user message was committed to JSONL) DOES
   call ``client.query`` once.
4. Pre-entry STEERED sends the input to Claude (preserving conversation
   context) and emits ``response.completed``.
5. Pre-entry CLIENT_CANCELLED and SHUTTING_DOWN return without making
   any SDK calls.
6. The sample never uses ``fork_session`` in any code path.
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
)
from azure.ai.agentserver.responses._id_generator import IdGenerator
from azure.ai.agentserver.responses._durability_context import _DeveloperMetadataFacade

try:
    import claude_agent_sdk  # type: ignore[import-untyped]  # noqa: F401
except ImportError:  # pragma: no cover
    pytest.skip("claude_agent_sdk not installed", allow_module_level=True)


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
    context = MagicMock(spec=ResponseContext)
    context.response_id = response_id
    context.is_recovery = entry_mode == "recovered"
    context.is_steered_turn = False
    context.pending_input_count = 0
    context.durable_metadata = _DeveloperMetadataFacade(metadata or {})
    context.cancel = asyncio.Event()
    context.shutdown = asyncio.Event()
    context.client_cancelled = False

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
    return CreateResponse(model="claude", input="test prompt")  # type: ignore[call-arg]


async def _drive(handler_coro_fn, request, context) -> list[Any]:
    events = []
    async for event in handler_coro_fn(request, context):
        events.append(event)
    return events


def _event_type(e: Any) -> str | None:
    return getattr(e, "type", None) or (e.get("type") if isinstance(e, dict) else None)


def _make_session_message(*, msg_type: str, text: str) -> Any:
    """Build a SessionMessage-shaped object the sample's history extractor accepts."""
    from claude_agent_sdk import SessionMessage

    return SessionMessage(
        type=msg_type,  # type: ignore[arg-type]
        uuid="msg-stub",
        session_id="session-stub",
        message={"role": msg_type, "content": text},
    )


def _make_claude_client_stub(
    reply_text: str = "Hello back.",
    new_session_id: str | None = None,
):
    from claude_agent_sdk import AssistantMessage, ResultMessage, TextBlock

    query_calls: list[dict[str, Any]] = []

    class _StubClient:
        def __init__(self, *, options: Any) -> None:
            self.options = options

        async def __aenter__(self) -> "_StubClient":
            return self

        async def __aexit__(self, *exc_info: Any) -> None:
            return None

        async def query(self, prompt: str) -> None:
            query_calls.append({"prompt": prompt, "options": self.options})

        async def interrupt(self) -> None:
            pass

        async def receive_response(self):
            yield AssistantMessage(content=[TextBlock(text=reply_text)], model="claude")
            yield ResultMessage(
                subtype="success",
                duration_ms=10,
                duration_api_ms=10,
                is_error=False,
                num_turns=1,
                session_id=new_session_id or "session-after",
                total_cost_usd=None,
                usage=None,
                result=None,
                uuid="uuid-1",
            )

    return _StubClient, query_calls


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestSample17FreshEntry:
    async def test_fresh_entry_calls_query_once_with_session_id(self) -> None:
        from samples import sample_17_durable_claude as mod  # type: ignore[import-not-found]

        stub_class, query_calls = _make_claude_client_stub()
        with patch.object(mod, "ClaudeSDKClient", stub_class):
            # Fresh session → get_session_messages returns nothing.
            with patch.object(mod, "get_session_messages", return_value=[]):
                ctx = _make_context(response_id=IdGenerator.new_response_id())
                events = await _drive(mod.handler, _make_request(), ctx)

        assert len(query_calls) == 1
        assert query_calls[0]["prompt"] == "test prompt"
        opts = query_calls[0]["options"]
        assert getattr(opts, "session_id", None) is not None
        assert getattr(opts, "resume", None) is None
        assert getattr(opts, "fork_session", False) is False
        assert "response.completed" in [_event_type(e) for e in events]


@pytest.mark.asyncio
class TestSample17RecoverySkipsWhenSessionHasOurInput:
    async def test_recovery_with_input_already_in_session_skips_query(self) -> None:
        from samples import sample_17_durable_claude as mod  # type: ignore[import-not-found]

        stub_class, query_calls = _make_claude_client_stub()
        # Upstream session JSONL already ends with our user message.
        history = [_make_session_message(msg_type="user", text="test prompt")]

        with patch.object(mod, "ClaudeSDKClient", stub_class):
            with patch.object(mod, "get_session_messages", return_value=history):
                ctx = _make_context(
                    response_id=IdGenerator.new_response_id(),
                    entry_mode="recovered",
                    metadata={"claude_session_id": "original-session"},
                )
                await _drive(mod.handler, _make_request(), ctx)

        # No query — Claude already has our message.
        assert query_calls == []


@pytest.mark.asyncio
class TestSample17RecoveryQueriesWhenSessionMissesOurInput:
    async def test_recovery_with_input_not_in_session_does_query(self) -> None:
        from samples import sample_17_durable_claude as mod  # type: ignore[import-not-found]

        stub_class, query_calls = _make_claude_client_stub()
        # Session has a prior assistant reply but not our new input.
        history = [
            _make_session_message(msg_type="user", text="prior question"),
            _make_session_message(msg_type="assistant", text="prior reply"),
        ]

        with patch.object(mod, "ClaudeSDKClient", stub_class):
            with patch.object(mod, "get_session_messages", return_value=history):
                ctx = _make_context(
                    response_id=IdGenerator.new_response_id(),
                    entry_mode="recovered",
                    metadata={"claude_session_id": "original-session"},
                )
                await _drive(mod.handler, _make_request(), ctx)

        assert len(query_calls) == 1
        opts = query_calls[0]["options"]
        assert getattr(opts, "resume", None) == "original-session"
        assert getattr(opts, "fork_session", False) is False
        assert getattr(opts, "session_id", None) is None


@pytest.mark.asyncio
class TestSample17NeverForks:
    async def test_no_attempt_uses_fork_session(self) -> None:
        from samples import sample_17_durable_claude as mod  # type: ignore[import-not-found]
        import inspect

        src = inspect.getsource(mod)
        assert "fork_session" not in src, (
            "sample_17 must not use fork_session — forking abandons in-flight " "session state and defeats durability"
        )


@pytest.mark.asyncio
class TestSample17NoWatermarkOrFlush:
    """Regression guard: the sample MUST NOT use a handler-managed watermark
    or call context.durable_metadata.flush(). The upstream session is the source
    of truth; relying on metadata persistence ordering reintroduces the
    crash-window inconsistency.
    """

    async def test_no_last_processed_input_item_id(self) -> None:
        from samples import sample_17_durable_claude as mod  # type: ignore[import-not-found]
        import inspect

        src = inspect.getsource(mod)
        assert "last_processed_input_item_id" not in src, (
            "sample_17 must use upstream history (get_session_messages) for "
            "deduplication, not a handler-managed watermark"
        )

    async def test_no_metadata_flush_call(self) -> None:
        from samples import sample_17_durable_claude as mod  # type: ignore[import-not-found]
        import inspect

        src = inspect.getsource(mod)
        assert ".metadata.flush(" not in src, (
            "sample_17 must not depend on metadata flush ordering; the " "upstream session is the source of truth"
        )


@pytest.mark.asyncio
class TestSample17PreEntrySteeredPreservesInput:
    async def test_pre_entry_steered_sends_input_to_claude_then_completes(self) -> None:
        from samples import sample_17_durable_claude as mod  # type: ignore[import-not-found]

        stub_class, query_calls = _make_claude_client_stub()
        with patch.object(mod, "ClaudeSDKClient", stub_class):
            with patch.object(mod, "get_session_messages", return_value=[]):
                ctx = _make_context(response_id=IdGenerator.new_response_id())
                ctx.cancel.set()
                signal = asyncio.Event()
                signal.set()

                events = await _drive(mod.handler, _make_request(), ctx)

        assert len(query_calls) == 1
        assert query_calls[0]["prompt"] == "test prompt"
        assert "response.completed" in [_event_type(e) for e in events]


@pytest.mark.asyncio
class TestSample17PreEntryNonSteeredCancelDoesNotTouchSDK:
    async def test_pre_entry_client_cancelled_does_not_call_sdk(self) -> None:
        from samples import sample_17_durable_claude as mod  # type: ignore[import-not-found]

        stub_class, query_calls = _make_claude_client_stub()
        with patch.object(mod, "ClaudeSDKClient", stub_class):
            ctx = _make_context(response_id=IdGenerator.new_response_id())
            ctx.client_cancelled = True

            ctx.cancel.set()
            signal = asyncio.Event()
            signal.set()

            events = await _drive(mod.handler, _make_request(), ctx)

        assert query_calls == []
        assert "response.completed" not in [_event_type(e) for e in events]

    async def test_pre_entry_shutdown_does_not_call_sdk(self) -> None:
        from samples import sample_17_durable_claude as mod  # type: ignore[import-not-found]

        stub_class, query_calls = _make_claude_client_stub()
        with patch.object(mod, "ClaudeSDKClient", stub_class):
            ctx = _make_context(response_id=IdGenerator.new_response_id())
            ctx.shutdown.set()

            ctx.cancel.set()
            signal = asyncio.Event()
            signal.set()

            events = await _drive(mod.handler, _make_request(), ctx)

        assert query_calls == []
        assert "response.completed" not in [_event_type(e) for e in events]
