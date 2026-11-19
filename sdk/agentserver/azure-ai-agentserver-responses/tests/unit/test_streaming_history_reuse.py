# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Initial persistence uses only matching request-local history prefetches."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.ai.agentserver.responses import ResponsesServerOptions
from azure.ai.agentserver.responses._response_context import ResponseContext
from azure.ai.agentserver.responses.hosting import _orchestrator as orchestrator
from azure.ai.agentserver.responses.hosting._execution_context import _ExecutionContext
from azure.ai.agentserver.responses.models import CreateResponse
from azure.ai.agentserver.responses.models.runtime import ResponseModeFlags
from azure.ai.agentserver.responses.store._foundry_errors import FoundryResourceNotFoundError
from azure.ai.agentserver.responses.streaming import ResponseEventStream


@pytest.mark.parametrize(
    "prefetched,previous,conversation,expected,fetches",
    [
        (["cached"], "previous", None, ["cached"], 0),
        ([], "previous", None, [], 0),
        (None, "previous", None, ["fetched"], 1),
        (["conversation-item"], None, "conversation", None, 0),
        (["conversation-item"], "previous", "conversation", ["fetched"], 1),
        (None, None, None, None, 0),
    ],
)
@pytest.mark.parametrize("background", [False, True])
async def test_registration_history(
    monkeypatch, prefetched, previous, conversation, expected, fetches, background
) -> None:
    provider = MagicMock()
    provider.get_history_item_ids = AsyncMock(return_value=["fetched"])
    provider.create_response = AsyncMock()
    subject = MagicMock()
    subject.last_cursor = AsyncMock(return_value=None)
    monkeypatch.setattr(orchestrator.streams, "get_or_create", AsyncMock(return_value=subject))
    obj = object.__new__(orchestrator._ResponseOrchestrator)
    obj._provider = provider
    obj._runtime_options = ResponsesServerOptions()
    obj._runtime_state = MagicMock(add=AsyncMock())
    obj._safe_emit = AsyncMock()
    response_context = ResponseContext(
        response_id="response",
        mode_flags=ResponseModeFlags(stream=True, store=True, background=background),
        provider=provider,
        input_items=[],
        previous_response_id=previous,
        conversation_id=conversation,
        prefetched_history_ids=prefetched,
    )
    ctx = _ExecutionContext(
        response_id="response",
        agent_reference={},
        model="m",
        store=True,
        background=background,
        stream=True,
        input_items=[],
        previous_response_id=previous,
        conversation_id=conversation,
        cancellation_signal=asyncio.Event(),
        span=MagicMock(),
        parsed=CreateResponse(model="m", input="hi"),
        prefetched_history_ids=prefetched,
        context=response_context,
    )
    first = ResponseEventStream(response_id="response", model="m").emit_created()
    state = orchestrator._PipelineState()
    state.handler_events.append(first)
    await obj._register_bg_execution(ctx, state, first)
    assert provider.get_history_item_ids.await_count == fetches
    assert provider.create_response.await_args.args[2] == expected
    assert state.provider_created
    obj._safe_emit.assert_awaited_once()
    if fetches:
        assert provider.get_history_item_ids.await_args.args == (
            previous,
            None,
            obj._runtime_options.default_fetch_history_count,
        )
        assert provider.get_history_item_ids.await_args.kwargs["context"].user_id_key is None
        assert provider.get_history_item_ids.await_args.kwargs["context"].call_id is None

    if previous and prefetched is None:
        response_context._reset_history_cache()
        provider.get_history_item_ids.side_effect = FoundryResourceNotFoundError("missing previous response")
        provider.create_response.reset_mock()
        obj._safe_emit.reset_mock()
        with pytest.raises(FoundryResourceNotFoundError):
            await obj._register_bg_execution(ctx, orchestrator._PipelineState(), first)
        provider.create_response.assert_not_awaited()
        obj._safe_emit.assert_not_awaited()
