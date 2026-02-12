# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from types import SimpleNamespace

import pytest

from azure.ai.agentserver.langgraph.models.response_api_default_converter import ResponseAPIDefaultConverter


class DummyGraphState:
    def __init__(self):
        self.values = "state"

class _DummyGraph:
    def __init__(self) -> None:
        self.checkpointer = object()
        self.last_config = None

    async def aget_state(self, config):
        self.last_config = config
        return DummyGraphState()


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

    assert state is not None
    assert state.values == "state"
    assert graph.last_config["configurable"]["thread_id"] == "conv-1"
