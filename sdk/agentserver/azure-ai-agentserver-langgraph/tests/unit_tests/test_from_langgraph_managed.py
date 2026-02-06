# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for from_langgraph with checkpointer via compile."""

import pytest
from unittest.mock import Mock

from azure.core.credentials_async import AsyncTokenCredential


@pytest.mark.unit
def test_from_langgraph_basic() -> None:
    """Test that from_langgraph works without a checkpointer."""
    from azure.ai.agentserver.langgraph import from_langgraph
    from langgraph.graph import StateGraph
    from typing_extensions import TypedDict

    class State(TypedDict):
        messages: list

    builder = StateGraph(State)
    builder.add_node("node1", lambda x: x)
    builder.set_entry_point("node1")
    builder.set_finish_point("node1")
    graph = builder.compile()

    adapter = from_langgraph(graph)

    assert adapter is not None


@pytest.mark.unit
def test_graph_with_foundry_checkpointer_via_compile() -> None:
    """Test that FoundryCheckpointSaver can be set via builder.compile()."""
    from azure.ai.agentserver.langgraph import from_langgraph
    from azure.ai.agentserver.langgraph.checkpointer import FoundryCheckpointSaver
    from langgraph.graph import StateGraph
    from typing_extensions import TypedDict

    class State(TypedDict):
        messages: list

    builder = StateGraph(State)
    builder.add_node("node1", lambda x: x)
    builder.add_node("node2", lambda x: x)
    builder.add_edge("node1", "node2")
    builder.set_entry_point("node1")
    builder.set_finish_point("node2")

    mock_credential = Mock(spec=AsyncTokenCredential)
    saver = FoundryCheckpointSaver(
        project_endpoint="https://test.services.ai.azure.com/api/projects/test-project",
        credential=mock_credential,
    )

    # User sets checkpointer via LangGraph's native compile()
    graph = builder.compile(
        checkpointer=saver,
        interrupt_before=["node1"],
        interrupt_after=["node2"],
        debug=True,
    )

    adapter = from_langgraph(graph)

    # Verify checkpointer and compile parameters are preserved
    assert adapter is not None
    assert isinstance(adapter._graph.checkpointer, FoundryCheckpointSaver)
    assert adapter._graph.interrupt_before_nodes == ["node1"]
    assert adapter._graph.interrupt_after_nodes == ["node2"]
    assert adapter._graph.debug is True
