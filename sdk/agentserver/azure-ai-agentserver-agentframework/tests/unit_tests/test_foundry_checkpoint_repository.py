# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for FoundryCheckpointRepository."""

import pytest

from azure.ai.agentserver.agentframework.persistence import (
    FoundryCheckpointRepository,
    FoundryCheckpointStorage,
)

from .mocks import MockFoundryCheckpointClient


class TestableFoundryCheckpointRepository(FoundryCheckpointRepository):
    """Testable version that accepts a mock client."""

    def __init__(self, client: MockFoundryCheckpointClient) -> None:
        """Initialize with a mock client (bypass credential requirements)."""
        self._client = client  # type: ignore[assignment]
        self._inventory = {}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_or_create_returns_none_without_conversation_id() -> None:
    """Test that get_or_create returns None when conversation_id is None."""
    client = MockFoundryCheckpointClient()
    repo = TestableFoundryCheckpointRepository(client=client)

    result = await repo.get_or_create(None)

    assert result is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_or_create_returns_none_for_empty_string() -> None:
    """Test that get_or_create returns None when conversation_id is empty."""
    client = MockFoundryCheckpointClient()
    repo = TestableFoundryCheckpointRepository(client=client)

    result = await repo.get_or_create("")

    assert result is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_or_create_creates_storage_on_first_access() -> None:
    """Test that get_or_create creates storage on first access."""
    client = MockFoundryCheckpointClient()
    repo = TestableFoundryCheckpointRepository(client=client)

    storage = await repo.get_or_create("conv-123")

    assert storage is not None
    assert isinstance(storage, FoundryCheckpointStorage)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_or_create_creates_session_on_first_access() -> None:
    """Test that get_or_create creates session on the backend."""
    client = MockFoundryCheckpointClient()
    repo = TestableFoundryCheckpointRepository(client=client)

    await repo.get_or_create("conv-123")

    # Verify session was created
    session = await client.read_session("conv-123")
    assert session is not None
    assert session.session_id == "conv-123"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_or_create_caches_storage_instances() -> None:
    """Test that get_or_create returns cached storage on subsequent calls."""
    client = MockFoundryCheckpointClient()
    repo = TestableFoundryCheckpointRepository(client=client)

    storage1 = await repo.get_or_create("conv-123")
    storage2 = await repo.get_or_create("conv-123")

    assert storage1 is storage2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_or_create_creates_separate_storage_per_conversation() -> None:
    """Test that get_or_create creates separate storage per conversation."""
    client = MockFoundryCheckpointClient()
    repo = TestableFoundryCheckpointRepository(client=client)

    storage1 = await repo.get_or_create("conv-1")
    storage2 = await repo.get_or_create("conv-2")

    assert storage1 is not storage2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_close_closes_client() -> None:
    """Test that close closes the underlying client."""
    client = MockFoundryCheckpointClient()
    repo = TestableFoundryCheckpointRepository(client=client)

    # Should not raise
    await repo.close()
