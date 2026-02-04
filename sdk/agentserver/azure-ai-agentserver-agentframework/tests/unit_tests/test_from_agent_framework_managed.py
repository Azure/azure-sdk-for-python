# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for from_agent_framework with managed checkpoints."""

import pytest
from unittest.mock import Mock, AsyncMock

from azure.core.credentials_async import AsyncTokenCredential


@pytest.mark.unit
def test_managed_checkpoints_requires_project_endpoint() -> None:
    """Test that managed_checkpoints=True requires project_endpoint."""
    from azure.ai.agentserver.agentframework import from_agent_framework
    from agent_framework import WorkflowBuilder

    builder = WorkflowBuilder()
    mock_credential = Mock(spec=AsyncTokenCredential)

    with pytest.raises(ValueError) as exc_info:
        from_agent_framework(
            builder,
            credentials=mock_credential,
            managed_checkpoints=True,
            project_endpoint=None,
        )

    assert "project_endpoint" in str(exc_info.value)


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
            project_endpoint="https://test.services.ai.azure.com/api/projects/test-project",
        )

    assert "credentials" in str(exc_info.value)


@pytest.mark.unit
def test_managed_checkpoints_false_does_not_require_parameters() -> None:
    """Test that managed_checkpoints=False does not require project_endpoint."""
    from azure.ai.agentserver.agentframework import from_agent_framework
    from agent_framework import WorkflowBuilder

    builder = WorkflowBuilder()

    # Should not raise
    adapter = from_agent_framework(
        builder,
        managed_checkpoints=False,
    )

    assert adapter is not None
