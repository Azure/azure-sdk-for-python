# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for from_agent_framework with managed checkpoints."""

import os
import pytest
from unittest.mock import Mock, AsyncMock, patch

from azure.core.credentials_async import AsyncTokenCredential


@pytest.mark.unit
def test_managed_checkpoints_requires_project_endpoint() -> None:
    """Test that managed_checkpoints=True requires project_endpoint when env var not set."""
    from azure.ai.agentserver.agentframework import from_agent_framework
    from agent_framework import WorkflowBuilder

    builder = WorkflowBuilder()
    mock_credential = Mock(spec=AsyncTokenCredential)

    # Ensure environment variable is not set
    with patch.dict(os.environ, {}, clear=True):
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


@pytest.mark.unit
def test_managed_checkpoints_and_checkpoint_repository_are_mutually_exclusive() -> None:
    """Test that managed_checkpoints=True and checkpoint_repository cannot be used together."""
    from azure.ai.agentserver.agentframework import from_agent_framework
    from azure.ai.agentserver.agentframework.persistence import InMemoryCheckpointRepository
    from agent_framework import WorkflowBuilder

    builder = WorkflowBuilder()
    mock_credential = Mock(spec=AsyncTokenCredential)
    checkpoint_repo = InMemoryCheckpointRepository()

    with pytest.raises(ValueError) as exc_info:
        from_agent_framework(
            builder,
            credentials=mock_credential,
            managed_checkpoints=True,
            checkpoint_repository=checkpoint_repo,
            project_endpoint="https://test.services.ai.azure.com/api/projects/test-project",
        )

    assert "Cannot use both" in str(exc_info.value)
    assert "managed_checkpoints" in str(exc_info.value)
    assert "checkpoint_repository" in str(exc_info.value)
