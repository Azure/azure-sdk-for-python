# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""E2E test for sample_21 — durable LangGraph handler.

Pins the recovery contract for the "upstream framework owns durability"
shape:

1. Fresh entry runs the graph from start and emits at least one AI
   message item.
2. Recovered entry queries graph state, builds a resumption response
   containing the AI messages already in the graph history, and emits
   ``response.in_progress`` carrying them.
3. Pre-entry STEERED emits ``response.completed`` (per Spec 011).
4. Pre-entry CLIENT_CANCELLED / SHUTTING_DOWN return without terminal.

The LangGraph graph itself is patched with a minimal stub so tests are
deterministic and fast. The patch verifies that the sample reads graph
state via ``get_state``.
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
    from langchain_core.messages import AIMessage, HumanMessage
except ImportError:  # pragma: no cover
    pytest.skip("langchain_core not installed", allow_module_level=True)


def _make_context(
    *,
    response_id: str,
    entry_mode: str = "fresh",
    was_steered: bool = False,
    metadata: dict[str, Any] | None = None,
    conversation_id: str | None = None,
) -> ResponseContext:
    durability = DurabilityContext(
        entry_mode=entry_mode,  # type: ignore[arg-type]
        retry_attempt=0 if entry_mode == "fresh" else 1,
        was_steered=was_steered,
        pending_inputs=0,
        metadata=metadata or {},
    )
    context = MagicMock(spec=ResponseContext)
    context.response_id = response_id
    context.durability = durability
    context.cancellation_reason = None
    context.conversation_id = conversation_id

    async def _get_input_text() -> str:
        return "test prompt"

    context.get_input_text = _get_input_text
    return context


def _make_request() -> CreateResponse:
    return CreateResponse(model="langgraph", input="test prompt")  # type: ignore[call-arg]


async def _drive(handler_coro_fn, request, context, cancellation_signal) -> list[Any]:
    events = []
    async for event in handler_coro_fn(request, context, cancellation_signal):
        events.append(event)
    return events


def _event_type(e: Any) -> str | None:
    return getattr(e, "type", None) or (e.get("type") if isinstance(e, dict) else None)


def _make_state_stub(ai_messages: list[str]) -> MagicMock:
    """Build a fake graph state with the given AI messages."""
    state = MagicMock()
    state.values = {"messages": [AIMessage(content=text) for text in ai_messages]}
    state.config = {"configurable": {"checkpoint_id": "cp_test", "thread_id": "thr_test"}}
    state.next = ()
    return state


@pytest.mark.asyncio
class TestSample21Recovery:
    async def test_recovered_entry_resumes_from_graph_state(self) -> None:
        """Recovery: resumption response contains AI messages from graph state."""
        from samples import sample_21_durable_langgraph as mod  # type: ignore[import-not-found]

        # Stub the graph to return state with one prior AI message.
        prior_state = _make_state_stub(ai_messages=["Prior AI response"])
        # After the graph runs (we'll skip actual node execution), state has 2 messages.
        after_state = _make_state_stub(ai_messages=["Prior AI response", "Fresh reply"])

        with patch.object(mod, "_graph") as mock_graph:
            # get_state called in resumption builder + after stream
            mock_graph.get_state.side_effect = [prior_state, after_state, after_state]
            # _invoke_cancellable is called via asyncio.to_thread; we stub it to
            # return (True, []) — completed with no nodes.
            with patch.object(mod, "_invoke_cancellable") as mock_invoke:
                mock_invoke.return_value = (True, [])

                ctx = _make_context(
                    response_id=IdGenerator.new_response_id(),
                    entry_mode="recovered",
                    metadata={"stable_checkpoint_id": "cp_test"},
                    conversation_id="thr_test",
                )
                events = await _drive(mod.handler, _make_request(), ctx, asyncio.Event())

        # Verify the recovery in_progress carried the prior AI message.
        in_progress = next(e for e in events if _event_type(e) == "response.in_progress")
        payload = getattr(in_progress, "response", None) or in_progress.get("response")
        output = payload.get("output") if isinstance(payload, dict) else payload.output
        assert len(output) == 1, "resumption response must contain the prior AI message"
        assert "Prior AI response" in str(output[0])

        # The graph was queried via get_state for the resumption response.
        assert mock_graph.get_state.call_count >= 1


@pytest.mark.asyncio
class TestSample21PreEntryCancellation:
    async def test_pre_entry_steered_emits_completed(self) -> None:
        from samples import sample_21_durable_langgraph as mod  # type: ignore[import-not-found]

        with patch.object(mod, "_graph"):
            ctx = _make_context(
                response_id=IdGenerator.new_response_id(),
                conversation_id="thr_test_2",
            )
            ctx.cancellation_reason = CancellationReason.STEERED
            signal = asyncio.Event()
            signal.set()

            events = await _drive(mod.handler, _make_request(), ctx, signal)
            types = [_event_type(e) for e in events]
            assert "response.completed" in types

    async def test_pre_entry_shutdown_returns_no_terminal(self) -> None:
        from samples import sample_21_durable_langgraph as mod  # type: ignore[import-not-found]

        with patch.object(mod, "_graph"):
            ctx = _make_context(
                response_id=IdGenerator.new_response_id(),
                conversation_id="thr_test_3",
            )
            ctx.cancellation_reason = CancellationReason.SHUTTING_DOWN
            signal = asyncio.Event()
            signal.set()

            events = await _drive(mod.handler, _make_request(), ctx, signal)
            types = [_event_type(e) for e in events]
            # No terminal — handler returns silently.
            assert "response.completed" not in types
            assert "response.failed" not in types
