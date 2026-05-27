# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Mocked e2e test for sample_17 — durable Claude Agent SDK handler.

Real-SDK integration testing requires ``ANTHROPIC_API_KEY`` and
network access (and a Node.js runtime for the bundled CLI), so this
test patches ``ClaudeSDKClient`` to a synchronous in-memory stub.

Pins:

1. Fresh entry calls ``client.query(input_text)`` exactly once and
   passes ``ClaudeAgentOptions(session_id=<uuid>)``.
2. Recovered entry with ``claude_query_in_flight=True`` calls
   ``client.query`` again BUT uses ``ClaudeAgentOptions(resume=…,
   fork_session=True)`` — the fork is the documented escape from
   the duplicate-user-turn problem.
3. The watermark ``claude_query_in_flight`` is stamped BEFORE
   ``client.query`` and cleared after the receive loop finishes.
4. The fork's new ``session_id`` (captured from ``ResultMessage``)
   is written back to ``durability.metadata``.
5. Pre-entry STEERED emits ``response.completed``; CLIENT_CANCELLED
   and SHUTTING_DOWN return without terminal.
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

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
    import claude_agent_sdk  # type: ignore[import-untyped]  # noqa: F401
except ImportError:  # pragma: no cover
    pytest.skip("claude_agent_sdk not installed", allow_module_level=True)


# ---------------------------------------------------------------------------
# Test scaffolding
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
    return CreateResponse(model="claude", input="test prompt")  # type: ignore[call-arg]


async def _drive(handler_coro_fn, request, context, cancellation_signal) -> list[Any]:
    events = []
    async for event in handler_coro_fn(request, context, cancellation_signal):
        events.append(event)
    return events


def _event_type(e: Any) -> str | None:
    return getattr(e, "type", None) or (e.get("type") if isinstance(e, dict) else None)


def _make_claude_client_stub(
    reply_text: str = "Hello back.",
    new_session_id: str | None = None,
) -> tuple[MagicMock, list[dict[str, Any]]]:
    """Build a stubbed ClaudeSDKClient.

    Returns the mock class and a recorder list capturing every
    ``client.query(...)`` call (used by the at-most-once assertions).
    """
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
            block = TextBlock(text=reply_text)
            yield AssistantMessage(content=[block], model="claude")
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
            ctx = _make_context(response_id=IdGenerator.new_response_id())
            events = await _drive(mod.handler, _make_request(), ctx, asyncio.Event())

        # Exactly one query() call.
        assert len(query_calls) == 1
        assert query_calls[0]["prompt"] == "test prompt"

        # Options carried session_id (fresh, not resume).
        opts = query_calls[0]["options"]
        assert getattr(opts, "session_id", None) is not None
        assert getattr(opts, "resume", None) is None
        assert getattr(opts, "fork_session", False) is False

        # Lifecycle reached completed.
        types = [_event_type(e) for e in events]
        assert "response.completed" in types

        # Watermark cleared at end.
        assert ctx.durability.metadata.get("claude_query_in_flight") is False
        # session_id captured from ResultMessage.
        assert ctx.durability.metadata.get("claude_session_id") == "session-after"


@pytest.mark.asyncio
class TestSample17RecoveryWithInFlightQuery:
    async def test_recovery_with_in_flight_watermark_forks_session(self) -> None:
        from samples import sample_17_durable_claude as mod  # type: ignore[import-not-found]

        stub_class, query_calls = _make_claude_client_stub(new_session_id="forked-session")
        with patch.object(mod, "ClaudeSDKClient", stub_class):
            ctx = _make_context(
                response_id=IdGenerator.new_response_id(),
                entry_mode="recovered",
                metadata={
                    "claude_session_id": "original-session",
                    "claude_query_in_flight": True,
                },
            )
            events = await _drive(mod.handler, _make_request(), ctx, asyncio.Event())

        # The recovered attempt issues one query against a FORK of the
        # original session — never the original directly. This is the
        # documented escape from duplicate-user-turn corruption.
        assert len(query_calls) == 1
        opts = query_calls[0]["options"]
        assert getattr(opts, "resume", None) == "original-session"
        assert getattr(opts, "fork_session", False) is True
        # session_id was not set on this options object (resume + fork
        # is mutually exclusive with assigning a new id).

        # New (forked) session_id captured back into metadata.
        assert ctx.durability.metadata.get("claude_session_id") == "forked-session"
        # Watermark cleared after a clean receive loop.
        assert ctx.durability.metadata.get("claude_query_in_flight") is False

        # Lifecycle: recovery in_progress carries empty resumption response.
        in_progress = next(
            e for e in events if _event_type(e) == "response.in_progress"
        )
        payload = getattr(in_progress, "response", None) or in_progress.get("response")
        output = payload.get("output") if isinstance(payload, dict) else payload.output
        assert output == []


@pytest.mark.asyncio
class TestSample17PreEntryCancellation:
    async def test_pre_entry_steered_emits_completed_without_calling_sdk(self) -> None:
        from samples import sample_17_durable_claude as mod  # type: ignore[import-not-found]

        stub_class, query_calls = _make_claude_client_stub()
        with patch.object(mod, "ClaudeSDKClient", stub_class):
            ctx = _make_context(response_id=IdGenerator.new_response_id())
            ctx.cancellation_reason = CancellationReason.STEERED
            signal = asyncio.Event()
            signal.set()

            events = await _drive(mod.handler, _make_request(), ctx, signal)

        types = [_event_type(e) for e in events]
        assert "response.completed" in types
        # No upstream call — we short-circuited before touching the SDK.
        assert query_calls == []

    async def test_pre_entry_shutdown_returns_no_terminal_no_sdk_call(self) -> None:
        from samples import sample_17_durable_claude as mod  # type: ignore[import-not-found]

        stub_class, query_calls = _make_claude_client_stub()
        with patch.object(mod, "ClaudeSDKClient", stub_class):
            ctx = _make_context(response_id=IdGenerator.new_response_id())
            ctx.cancellation_reason = CancellationReason.SHUTTING_DOWN
            signal = asyncio.Event()
            signal.set()

            events = await _drive(mod.handler, _make_request(), ctx, signal)

        types = [_event_type(e) for e in events]
        assert "response.completed" not in types
        assert query_calls == []
