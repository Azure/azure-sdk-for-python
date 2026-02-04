# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for from_agent_framework with managed checkpoints."""

import pytest
from unittest.mock import Mock, AsyncMock

from azure.core.credentials_async import AsyncTokenCredential


@pytest.mark.unit
def test_managed_checkpoints_requires_foundry_endpoint() -> None:
    """Test that managed_checkpoints=True requires foundry_endpoint."""
    from azure.ai.agentserver.agentframework import from_agent_framework
    from agent_framework import WorkflowBuilder

    builder = WorkflowBuilder()
    mock_credential = Mock(spec=AsyncTokenCredential)

    with pytest.raises(ValueError) as exc_info:
        from_agent_framework(
            builder,
            credentials=mock_credential,
            managed_checkpoints=True,
            foundry_endpoint=None,
            project_id="test-project",
        )

    assert "foundry_endpoint" in str(exc_info.value)


@pytest.mark.unit
def test_managed_checkpoints_requires_project_id() -> None:
    """Test that managed_checkpoints=True requires project_id."""
    from azure.ai.agentserver.agentframework import from_agent_framework
    from agent_framework import WorkflowBuilder

    builder = WorkflowBuilder()
    mock_credential = Mock(spec=AsyncTokenCredential)

    with pytest.raises(ValueError) as exc_info:
        from_agent_framework(
            builder,
            credentials=mock_credential,
            managed_checkpoints=True,
            foundry_endpoint="https://test.api.azureml.ms",
            project_id=None,
        )

    assert "project_id" in str(exc_info.value)


@pytest.mark.unit
def test_managed_checkpoints_requires_credentials() -> None:
    """Test that managed_checkpoints=True requires credentials."""
    from azure.ai.agentserver.agentframework import from_agent_framework
    from agent_framework import WorkflowBuilder

    builder = WorkflowBuilder()

    with pytest.raises(ValueError) as exc_info:
        from_agent_framework(
            builder,
            credentials=None,
            managed_checkpoints=True,
            foundry_endpoint="https://test.api.azureml.ms",
            project_id="test-project",
        )

    assert "credentials" in str(exc_info.value)


@pytest.mark.unit
def test_managed_checkpoints_false_does_not_require_parameters() -> None:
    """Test that managed_checkpoints=False does not require endpoint/project_id."""
    from azure.ai.agentserver.agentframework import from_agent_framework
    from agent_framework import WorkflowBuilder

    builder = WorkflowBuilder()

    # Should not raise
    adapter = from_agent_framework(
        builder,
        managed_checkpoints=False,
    )

    assert adapter is not None
