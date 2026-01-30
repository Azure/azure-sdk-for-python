# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from types import SimpleNamespace

import pytest

from azure.ai.agentserver.langgraph._exceptions import LangGraphMissingConversationIdError
from azure.ai.agentserver.langgraph.langgraph import LangGraphAdapter
from azure.ai.agentserver.langgraph.models.response_api_default_converter import ResponseAPIDefaultConverter


class _DummyConverter:
    async def convert_request(self, context):  # pragma: no cover - guard should short-circuit first
        raise AssertionError("convert_request should not be called for this test")

    async def convert_response_non_stream(self, output, context):  # pragma: no cover - guard should short-circuit
        raise AssertionError("convert_response_non_stream should not be called for this test")

    async def convert_response_stream(self, output, context):  # pragma: no cover - guard should short-circuit
        raise AssertionError("convert_response_stream should not be called for this test")


class _DummyGraph:
    def __init__(self) -> None:
        self.checkpointer = object()
        self.last_config = None

    async def aget_state(self, config):
        self.last_config = config
        return "state"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_aget_state_skips_without_conversation_id() -> None:
    graph = _DummyGraph()
    converter = ResponseAPIDefaultConverter(graph)  # type: ignore[arg-type]
    context = SimpleNamespace(agent_run=SimpleNamespace(conversation_id=None))

    state = await converter._aget_state(context)  # type: ignore[arg-type]

    assert state is None
    assert graph.last_config is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_aget_state_uses_conversation_id() -> None:
    graph = _DummyGraph()
    converter = ResponseAPIDefaultConverter(graph)  # type: ignore[arg-type]
    context = SimpleNamespace(agent_run=SimpleNamespace(conversation_id="conv-1"))

    state = await converter._aget_state(context)  # type: ignore[arg-type]

    assert state == "state"
    assert graph.last_config["configurable"]["thread_id"] == "conv-1"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_agent_run_requires_conversation_id_with_checkpointer_raises() -> None:
    graph = _DummyGraph()
    adapter = LangGraphAdapter(graph, converter=_DummyConverter())  # type: ignore[arg-type]
    context = SimpleNamespace(conversation_id=None, stream=False)

    with pytest.raises(LangGraphMissingConversationIdError):
        await adapter.agent_run(context)
