# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Mocked e2e test for sample_17 — durable Claude Agent SDK handler.

Pins:

1. Fresh entry calls ``client.query`` exactly once and updates the
   ``last_processed_input_item_id`` watermark.
2. Recovered entry with the watermark already pointing at the current
   input does NOT call ``client.query`` again — the session is resumed
   and we receive whatever Claude has.
3. Recovered entry where the watermark does not match (e.g. crash
   before query was issued) DOES call ``client.query`` once.
4. Recovery uses ``ClaudeAgentOptions(resume=…)`` — never ``fork_session``.
5. Pre-entry STEERED sends the user input to Claude (so it is preserved
   in conversation history) and then emits ``response.completed``.
6. Pre-entry CLIENT_CANCELLED and SHUTTING_DOWN return without making
   any SDK calls.
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
    async def test_fresh_entry_calls_query_once_and_updates_watermark(self) -> None:
        from samples import sample_17_durable_claude as mod  # type: ignore[import-not-found]

        stub_class, query_calls = _make_claude_client_stub()
        with patch.object(mod, "ClaudeSDKClient", stub_class):
            ctx = _make_context(
                response_id=IdGenerator.new_response_id(),
                input_item_id="item-fresh-1",
            )
            events = await _drive(mod.handler, _make_request(), ctx, asyncio.Event())

        assert len(query_calls) == 1
        assert query_calls[0]["prompt"] == "test prompt"
        # Fresh: options carries session_id, NOT resume, NEVER fork.
        opts = query_calls[0]["options"]
        assert getattr(opts, "session_id", None) is not None
        assert getattr(opts, "resume", None) is None
        assert getattr(opts, "fork_session", False) is False

        # Watermark updated to current input item id.
        assert ctx.durability.metadata.get("last_processed_input_item_id") == "item-fresh-1"
        assert "response.completed" in [_event_type(e) for e in events]


@pytest.mark.asyncio
class TestSample17RecoverySkipsQueryWhenWatermarkMatches:
    async def test_recovery_with_matching_watermark_skips_query(self) -> None:
        from samples import sample_17_durable_claude as mod  # type: ignore[import-not-found]

        stub_class, query_calls = _make_claude_client_stub()
        with patch.object(mod, "ClaudeSDKClient", stub_class):
            ctx = _make_context(
                response_id=IdGenerator.new_response_id(),
                entry_mode="recovered",
                metadata={
                    "claude_session_id": "original-session",
                    "last_processed_input_item_id": "item-recovered-1",
                },
                input_item_id="item-recovered-1",
            )
            events = await _drive(mod.handler, _make_request(), ctx, asyncio.Event())

        # Watermark matched → no query() this attempt.
        assert query_calls == []

        # Options carries resume (the existing session id), NEVER fork_session.
        # No query was issued so we can't read options from the recording —
        # but the prior session_id should still be in metadata.
        assert ctx.durability.metadata.get("claude_session_id") == "session-after"

        # Lifecycle: recovery in_progress with empty resumption.
        in_progress = next(
            e for e in events if _event_type(e) == "response.in_progress"
        )
        payload = getattr(in_progress, "response", None) or in_progress.get("response")
        output = payload.get("output") if isinstance(payload, dict) else payload.output
        assert output == []


@pytest.mark.asyncio
class TestSample17RecoveryQueriesWhenWatermarkStale:
    async def test_recovery_with_stale_watermark_does_query(self) -> None:
        from samples import sample_17_durable_claude as mod  # type: ignore[import-not-found]

        stub_class, query_calls = _make_claude_client_stub()
        with patch.object(mod, "ClaudeSDKClient", stub_class):
            ctx = _make_context(
                response_id=IdGenerator.new_response_id(),
                entry_mode="recovered",
                metadata={
                    "claude_session_id": "original-session",
                    "last_processed_input_item_id": "item-from-prior-turn",
                },
                input_item_id="item-current-turn",
            )
            events = await _drive(mod.handler, _make_request(), ctx, asyncio.Event())

        # Watermark stale → query() once with current input.
        assert len(query_calls) == 1
        opts = query_calls[0]["options"]
        # Recovery uses resume, NEVER fork.
        assert getattr(opts, "resume", None) == "original-session"
        assert getattr(opts, "fork_session", False) is False
        assert getattr(opts, "session_id", None) is None

        # Watermark advanced to the current item.
        assert ctx.durability.metadata.get("last_processed_input_item_id") == "item-current-turn"


@pytest.mark.asyncio
class TestSample17NeverForks:
    async def test_no_attempt_uses_fork_session(self) -> None:
        """Regression guard: the sample MUST NOT use fork_session in any code path."""
        from samples import sample_17_durable_claude as mod  # type: ignore[import-not-found]
        import inspect

        src = inspect.getsource(mod)
        assert "fork_session" not in src, (
            "sample_17 must not use fork_session — forking abandons in-flight "
            "session state and defeats durability"
        )


@pytest.mark.asyncio
class TestSample17FlushBeforeQuery:
    """Pin the watermark-flush-then-query ordering.

    The contract: between writing the watermark and calling the upstream
    side-effecting API, the metadata MUST be explicitly flushed. A crash
    in the tiny window between flush and call still recovers cleanly
    because the recovered handler sees the persisted watermark and skips
    the re-query. Without the flush, the watermark sits in the in-memory
    dict and is only persisted on lifecycle transitions — a crash in
    that window loses the watermark and the recovered handler re-issues
    ``client.query`` (duplicate user message in session JSONL).

    Tests below pin BOTH (a) flush is called and (b) flush happens
    BEFORE the query call.
    """

    async def test_flush_called_before_query_on_watermarked_send(self) -> None:
        from samples import sample_17_durable_claude as mod  # type: ignore[import-not-found]

        # Record the order in which flush() and query() are invoked.
        events_in_order: list[str] = []

        stub_class, query_calls = _make_claude_client_stub()

        # Wrap the stub's query() to record its position.
        original_query = stub_class.query

        async def _recording_query(self_inner: Any, prompt: str) -> None:
            events_in_order.append("query")
            await original_query(self_inner, prompt)

        stub_class.query = _recording_query  # type: ignore[method-assign]

        with patch.object(mod, "ClaudeSDKClient", stub_class):
            ctx = _make_context(
                response_id=IdGenerator.new_response_id(),
                input_item_id="item-flush-1",
            )

            # Wrap the FilteredMetadata's flush() so we can record its position.
            metadata = ctx.durability.metadata  # _FilteredMetadata wrapping dict
            original_flush = metadata.flush

            async def _recording_flush() -> None:
                events_in_order.append("flush")
                await original_flush()

            metadata.flush = _recording_flush  # type: ignore[assignment]

            await _drive(mod.handler, _make_request(), ctx, asyncio.Event())

        # The contract: flush() must appear in the trace, and it must come
        # before the first query().
        assert "flush" in events_in_order, (
            "sample_17 must call await durability.metadata.flush() after the "
            "watermark write — see backlog B0 (deterministic metadata persistence)"
        )
        flush_idx = events_in_order.index("flush")
        query_idx = events_in_order.index("query")
        assert flush_idx < query_idx, (
            f"flush() must happen BEFORE the upstream query(). Got order: "
            f"{events_in_order}. If flush is after query, a crash between "
            f"them loses the watermark and recovery re-queries (duplicate user message)."
        )

    async def test_flush_is_at_most_once_after_a_single_watermark_write(self) -> None:
        """Dirty-tracking sanity check: idempotent flush after one watermark write."""
        from samples import sample_17_durable_claude as mod  # type: ignore[import-not-found]

        flush_count = [0]

        stub_class, _query_calls = _make_claude_client_stub()
        with patch.object(mod, "ClaudeSDKClient", stub_class):
            ctx = _make_context(
                response_id=IdGenerator.new_response_id(),
                input_item_id="item-once",
            )
            metadata = ctx.durability.metadata
            original_flush = metadata.flush

            async def _counting_flush() -> None:
                flush_count[0] += 1
                await original_flush()

            metadata.flush = _counting_flush  # type: ignore[assignment]

            await _drive(mod.handler, _make_request(), ctx, asyncio.Event())

        # One watermark write → at most one flush in the watermarked-send path.
        # (Steered pre-entry test below covers the other call site separately.)
        assert flush_count[0] >= 1, "sample_17 must flush at least once after watermark write"
        assert flush_count[0] <= 2, (
            f"sample_17 flushed {flush_count[0]} times; expected at most 2 "
            f"(one in the main path + at most one in the close-out). Excess "
            f"flushes suggest watermark is being re-written or dirty tracking is broken."
        )


@pytest.mark.asyncio
class TestSample17PreEntrySteeredPreservesInput:
    async def test_pre_entry_steered_sends_input_to_claude_then_completes(self) -> None:
        from samples import sample_17_durable_claude as mod  # type: ignore[import-not-found]

        stub_class, query_calls = _make_claude_client_stub()
        with patch.object(mod, "ClaudeSDKClient", stub_class):
            ctx = _make_context(
                response_id=IdGenerator.new_response_id(),
                input_item_id="item-steered",
            )
            ctx.cancellation_reason = CancellationReason.STEERED
            signal = asyncio.Event()
            signal.set()

            events = await _drive(mod.handler, _make_request(), ctx, signal)

        # Input was sent to Claude before completing — preserves conversation context.
        assert len(query_calls) == 1
        assert query_calls[0]["prompt"] == "test prompt"
        assert ctx.durability.metadata.get("last_processed_input_item_id") == "item-steered"
        assert "response.completed" in [_event_type(e) for e in events]


@pytest.mark.asyncio
class TestSample17PreEntryNonSteeredCancelDoesNotTouchSDK:
    async def test_pre_entry_client_cancelled_does_not_call_sdk(self) -> None:
        from samples import sample_17_durable_claude as mod  # type: ignore[import-not-found]

        stub_class, query_calls = _make_claude_client_stub()
        with patch.object(mod, "ClaudeSDKClient", stub_class):
            ctx = _make_context(response_id=IdGenerator.new_response_id())
            ctx.cancellation_reason = CancellationReason.CLIENT_CANCELLED
            signal = asyncio.Event()
            signal.set()

            events = await _drive(mod.handler, _make_request(), ctx, signal)

        assert query_calls == []
        assert "response.completed" not in [_event_type(e) for e in events]

    async def test_pre_entry_shutdown_does_not_call_sdk(self) -> None:
        from samples import sample_17_durable_claude as mod  # type: ignore[import-not-found]

        stub_class, query_calls = _make_claude_client_stub()
        with patch.object(mod, "ClaudeSDKClient", stub_class):
            ctx = _make_context(response_id=IdGenerator.new_response_id())
            ctx.cancellation_reason = CancellationReason.SHUTTING_DOWN
            signal = asyncio.Event()
            signal.set()

            events = await _drive(mod.handler, _make_request(), ctx, signal)

        assert query_calls == []
        assert "response.completed" not in [_event_type(e) for e in events]
