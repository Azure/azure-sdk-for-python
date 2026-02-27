# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for from_agent_framework with checkpoint repository."""

from unittest.mock import Mock

import pytest
from agent_framework import Executor, WorkflowBuilder, handler
from azure.core.credentials_async import AsyncTokenCredential


class _NoOpExecutor(Executor):
    def __init__(self) -> None:
        super().__init__(id="noop")


    @handler(input=str)
    async def handle(self, message, ctx) -> None:
        return None


def _create_builder() -> WorkflowBuilder:
    return WorkflowBuilder(start_executor=_NoOpExecutor())


class _StubWorkflowAdapter:
    def __init__(
        self,
        workflow_factory,
        credentials=None,
        session_repository=None,
        checkpoint_repository=None,
        **kwargs,
    ):
        self._workflow_factory = workflow_factory
        self._checkpoint_repository = checkpoint_repository


@pytest.mark.unit
def test_checkpoint_repository_is_optional(monkeypatch) -> None:
    """Test that checkpoint_repository is optional and defaults to None."""
    import azure.ai.agentserver.agentframework._workflow_agent_adapter as workflow_adapter_module
    from azure.ai.agentserver.agentframework import from_agent_framework

    monkeypatch.setattr(workflow_adapter_module, "AgentFrameworkWorkflowAdapter", _StubWorkflowAdapter)

    builder = _create_builder()

    adapter = from_agent_framework(builder)

    assert adapter is not None


@pytest.mark.unit
def test_foundry_checkpoint_repository_passed_directly(monkeypatch) -> None:
    """Test that FoundryCheckpointRepository can be passed via checkpoint_repository."""
    import azure.ai.agentserver.agentframework._workflow_agent_adapter as workflow_adapter_module
    from azure.ai.agentserver.agentframework import from_agent_framework
    from azure.ai.agentserver.agentframework.persistence import FoundryCheckpointRepository

    monkeypatch.setattr(workflow_adapter_module, "AgentFrameworkWorkflowAdapter", _StubWorkflowAdapter)

    builder = _create_builder()
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
