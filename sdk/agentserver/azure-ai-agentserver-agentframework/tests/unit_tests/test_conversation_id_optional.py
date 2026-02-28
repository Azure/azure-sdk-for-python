# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from unittest.mock import AsyncMock, Mock
from typing import Dict

import pytest
from agent_framework import AgentSession, BaseHistoryProvider, Content, InMemoryCheckpointStorage, Message
from azure.core.credentials_async import AsyncTokenCredential

from azure.ai.agentserver.agentframework.persistence._foundry_conversation_history_provider import (
    FoundryConversationHistoryProvider,
)
from azure.ai.agentserver.agentframework.persistence._foundry_conversation_session_repository import (
    FoundryConversationSessionRepository,
)
from azure.ai.agentserver.agentframework.persistence.agent_session_repository import (
    InMemoryAgentSessionRepository,
    SerializedAgentSessionRepository,
)
from azure.ai.agentserver.agentframework.persistence.checkpoint_repository import (
    InMemoryCheckpointRepository,
)


class _MemorySerializedSessionRepository(SerializedAgentSessionRepository):
    def __init__(self) -> None:
        super().__init__()
        self._storage: Dict[str, dict] = {}

    async def read_from_storage(self, conversation_id):
        if not conversation_id:
            return None
        return self._storage.get(conversation_id)

    async def write_to_storage(self, conversation_id, serialized_session):
        if not conversation_id:
            return
        self._storage[conversation_id] = serialized_session


@pytest.mark.unit
@pytest.mark.asyncio
async def test_inmemory_session_repository_ignores_missing_conversation_id() -> None:
    repo = InMemoryAgentSessionRepository()
    session = Mock(spec=AgentSession)

    await repo.set(None, session)
    assert await repo.get(None) is None

    await repo.set("conv-1", session)
    assert await repo.get("conv-1") is session


@pytest.mark.unit
@pytest.mark.asyncio
async def test_inmemory_checkpoint_repository_returns_none_without_conversation_id() -> None:
    repo = InMemoryCheckpointRepository()

    assert await repo.get_or_create(None) is None

    storage = await repo.get_or_create("conv-1")
    assert isinstance(storage, InMemoryCheckpointStorage)


@pytest.mark.unit
def test_foundry_history_provider_is_base_history_provider() -> None:
    provider = FoundryConversationHistoryProvider(project_client=Mock())

    assert isinstance(provider, BaseHistoryProvider)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_foundry_history_provider_reads_remote_and_cached_messages(monkeypatch) -> None:
    provider = FoundryConversationHistoryProvider(project_client=Mock())
    history_message = Message(role="assistant", contents=[Content.from_text("history")])
    new_message = Message(role="user", contents=[Content.from_text("new")])

    get_history = AsyncMock(return_value=[history_message])
    monkeypatch.setattr(provider, "_get_conversation_history", get_history)

    state = {"conversation_id": "conv-1"}
    first_messages = await provider.get_messages("conv-1", state=state)
    await provider.save_messages("conv-1", [new_message], state=state)
    second_messages = await provider.get_messages("conv-1", state=state)

    assert [message.text for message in first_messages] == ["history"]
    assert [message.role for message in second_messages] == ["assistant", "user"]
    assert [message.text for message in second_messages] == ["history", "new"]
    get_history.assert_awaited_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_foundry_session_repository_sets_conversation_state(monkeypatch) -> None:
    import azure.ai.agentserver.agentframework.persistence._foundry_conversation_session_repository as repo_module

    monkeypatch.setattr(repo_module, "AIProjectClient", lambda endpoint, credential: Mock())

    repo = FoundryConversationSessionRepository(
        project_endpoint="https://test.services.ai.azure.com/api/projects/test-project",
        credential=Mock(spec=AsyncTokenCredential),
    )

    session_one = await repo.get("conv-1")
    session_two = await repo.get("conv-2")
    source_id = repo.history_provider.source_id

    assert session_one is not None
    assert session_two is not None
    assert session_one.session_id == "conv-1"
    assert session_one.service_session_id == "conv-1"
    assert session_two.session_id == "conv-2"
    assert session_two.service_session_id == "conv-2"
    assert session_one.state[source_id]["conversation_id"] == "conv-1"
    assert session_two.state[source_id]["conversation_id"] == "conv-2"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_foundry_session_repository_reuses_existing_session(monkeypatch) -> None:
    import azure.ai.agentserver.agentframework.persistence._foundry_conversation_session_repository as repo_module

    monkeypatch.setattr(repo_module, "AIProjectClient", lambda endpoint, credential: Mock())

    repo = FoundryConversationSessionRepository(
        project_endpoint="https://test.services.ai.azure.com/api/projects/test-project",
        credential=Mock(spec=AsyncTokenCredential),
    )

    first_session = await repo.get("conv-1")
    second_session = await repo.get("conv-1")

    assert first_session is second_session


@pytest.mark.unit
@pytest.mark.asyncio
async def test_serialized_session_repository_uses_agent_session_to_dict_from_dict() -> None:
    repo = _MemorySerializedSessionRepository()
    session = AgentSession(session_id="local-1", service_session_id="service-1")
    session.state["counter"] = 2

    await repo.set("conv-1", session)
    loaded = await repo.get("conv-1")

    assert loaded is not None
    assert loaded.session_id == "local-1"
    assert loaded.service_session_id == "service-1"
    assert loaded.state["counter"] == 2
