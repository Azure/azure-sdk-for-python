# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from unittest.mock import Mock

import pytest
from agent_framework import AgentThread, InMemoryCheckpointStorage

from azure.ai.agentserver.agentframework.persistence.agent_thread_repository import (
    InMemoryAgentThreadRepository,
)
from azure.ai.agentserver.agentframework.persistence.checkpoint_repository import (
    InMemoryCheckpointRepository,
)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_inmemory_thread_repository_ignores_missing_conversation_id() -> None:
    repo = InMemoryAgentThreadRepository()
    thread = Mock(spec=AgentThread)

    await repo.set(None, thread)
    assert await repo.get(None) is None

    await repo.set("conv-1", thread)
    assert await repo.get("conv-1") is thread


@pytest.mark.unit
@pytest.mark.asyncio
async def test_inmemory_checkpoint_repository_returns_none_without_conversation_id() -> None:
    repo = InMemoryCheckpointRepository()

    assert await repo.get_or_create(None) is None

    storage = await repo.get_or_create("conv-1")
    assert isinstance(storage, InMemoryCheckpointStorage)
