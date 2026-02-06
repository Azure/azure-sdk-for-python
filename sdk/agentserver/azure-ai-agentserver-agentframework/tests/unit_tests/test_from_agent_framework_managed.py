# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for from_agent_framework with checkpoint repository."""

import pytest
from unittest.mock import Mock

from azure.core.credentials_async import AsyncTokenCredential


@pytest.mark.unit
def test_checkpoint_repository_is_optional() -> None:
    """Test that checkpoint_repository is optional and defaults to None."""
    from azure.ai.agentserver.agentframework import from_agent_framework
    from agent_framework import WorkflowBuilder

    builder = WorkflowBuilder()

    # Should not raise
    adapter = from_agent_framework(builder)

    assert adapter is not None


@pytest.mark.unit
def test_foundry_checkpoint_repository_passed_directly() -> None:
    """Test that FoundryCheckpointRepository can be passed via checkpoint_repository."""
    from azure.ai.agentserver.agentframework import from_agent_framework
    from azure.ai.agentserver.agentframework.persistence import FoundryCheckpointRepository
    from agent_framework import WorkflowBuilder

    builder = WorkflowBuilder()
    mock_credential = Mock(spec=AsyncTokenCredential)

    repo = FoundryCheckpointRepository(
        project_endpoint="https://test.services.ai.azure.com/api/projects/test-project",
        credential=mock_credential,
    )

    adapter = from_agent_framework(
        builder,
        checkpoint_repository=repo,
    )

    assert adapter is not None
    assert adapter._checkpoint_repository is repo
