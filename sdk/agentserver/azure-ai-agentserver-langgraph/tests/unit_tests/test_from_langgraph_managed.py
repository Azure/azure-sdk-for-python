# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for from_langgraph with managed checkpoints."""

import os
import pytest
from unittest.mock import Mock, patch

from azure.core.credentials_async import AsyncTokenCredential


@pytest.mark.unit
def test_managed_checkpoints_requires_project_endpoint() -> None:
    """Test that managed_checkpoints=True requires project_endpoint when env var not set."""
    from azure.ai.agentserver.langgraph import from_langgraph

    mock_graph = Mock()
    mock_credential = Mock(spec=AsyncTokenCredential)

    # Ensure environment variable is not set
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError) as exc_info:
            from_langgraph(
                mock_graph,
                credentials=mock_credential,
                managed_checkpoints=True,
                project_endpoint=None,
            )

    assert "project_endpoint" in str(exc_info.value)


@pytest.mark.unit
def test_managed_checkpoints_requires_credentials() -> None:
    """Test that managed_checkpoints=True requires credentials."""
    from azure.ai.agentserver.langgraph import from_langgraph

    mock_graph = Mock()

    with pytest.raises(ValueError) as exc_info:
        from_langgraph(
            mock_graph,
            credentials=None,
            managed_checkpoints=True,
            project_endpoint="https://test.services.ai.azure.com/api/projects/test-project",
        )

    assert "credentials" in str(exc_info.value)


@pytest.mark.unit
def test_managed_checkpoints_false_does_not_require_parameters() -> None:
    """Test that managed_checkpoints=False does not require project_endpoint."""
    from azure.ai.agentserver.langgraph import from_langgraph
    from langgraph.graph import StateGraph
    from typing_extensions import TypedDict

    # Create a simple graph
    class State(TypedDict):
        messages: list

    builder = StateGraph(State)
    builder.add_node("node1", lambda x: x)
    builder.set_entry_point("node1")
    builder.set_finish_point("node1")
    graph = builder.compile()

    # Should not raise
    adapter = from_langgraph(
        graph,
        managed_checkpoints=False,
    )

    assert adapter is not None


@pytest.mark.unit
def test_managed_checkpoints_requires_async_credential() -> None:
    """Test that managed_checkpoints=True requires AsyncTokenCredential."""
    from azure.ai.agentserver.langgraph import from_langgraph
    from azure.core.credentials import TokenCredential

    mock_graph = Mock()
    # Use a sync credential (not async)
    mock_credential = Mock(spec=TokenCredential)

    with pytest.raises(TypeError) as exc_info:
        from_langgraph(
            mock_graph,
            credentials=mock_credential,
            managed_checkpoints=True,
            project_endpoint="https://test.services.ai.azure.com/api/projects/test-project",
        )

    assert "AsyncTokenCredential" in str(exc_info.value)
