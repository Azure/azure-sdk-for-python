# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for FoundryCheckpointSaver."""

import pytest
from unittest.mock import Mock

from azure.core.credentials import TokenCredential
from azure.core.credentials_async import AsyncTokenCredential

from azure.ai.agentserver.langgraph.checkpointer import FoundryCheckpointSaver
from azure.ai.agentserver.langgraph.checkpointer._foundry_checkpoint_saver import (
    BaseCheckpointSaver,
)
from azure.ai.agentserver.langgraph.checkpointer._item_id import make_item_id

from ..mocks import MockFoundryCheckpointClient


class TestableFoundryCheckpointSaver(FoundryCheckpointSaver):
    """Testable version that accepts a mock client directly (bypasses credential check)."""

    def __init__(self, client: MockFoundryCheckpointClient) -> None:
        """Initialize with a mock client."""
        # Skip FoundryCheckpointSaver.__init__ and call BaseCheckpointSaver directly
        BaseCheckpointSaver.__init__(self, serde=None)
        self._client = client  # type: ignore[assignment]
        self._session_cache: set[str] = set()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_aget_tuple_returns_none_for_missing_checkpoint() -> None:
    """Test that aget_tuple returns None when checkpoint doesn't exist."""
    client = MockFoundryCheckpointClient()
    saver = TestableFoundryCheckpointSaver(client=client)

    config = {"configurable": {"thread_id": "thread-1"}}
    result = await saver.aget_tuple(config)

    assert result is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_aput_creates_checkpoint_item() -> None:
    """Test that aput creates a checkpoint item."""
    client = MockFoundryCheckpointClient()
    saver = TestableFoundryCheckpointSaver(client=client)

    config = {"configurable": {"thread_id": "thread-1", "checkpoint_ns": ""}}
    checkpoint = {
        "id": "cp-001",
        "channel_values": {},
        "channel_versions": {},
        "versions_seen": {},
        "pending_sends": [],
    }
    metadata = {"source": "test"}

    result = await saver.aput(config, checkpoint, metadata, {})

    assert result["configurable"]["checkpoint_id"] == "cp-001"
    assert result["configurable"]["thread_id"] == "thread-1"

    # Verify item was created
    item_ids = await client.list_item_ids("thread-1")
    assert len(item_ids) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_aput_creates_blob_items_for_new_versions() -> None:
    """Test that aput creates blob items for channel values."""
    client = MockFoundryCheckpointClient()
    saver = TestableFoundryCheckpointSaver(client=client)

    config = {"configurable": {"thread_id": "thread-1", "checkpoint_ns": ""}}
    checkpoint = {
        "id": "cp-001",
        "channel_values": {"messages": ["hello", "world"]},
        "channel_versions": {"messages": "1"},
        "versions_seen": {},
        "pending_sends": [],
    }
    metadata = {"source": "test"}
    new_versions = {"messages": "1"}

    await saver.aput(config, checkpoint, metadata, new_versions)

    # Should have 2 items: checkpoint + 1 blob
    item_ids = await client.list_item_ids("thread-1")
    assert len(item_ids) == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_aput_returns_config_with_checkpoint_id() -> None:
    """Test that aput returns config with the correct checkpoint ID."""
    client = MockFoundryCheckpointClient()
    saver = TestableFoundryCheckpointSaver(client=client)

    config = {"configurable": {"thread_id": "thread-1", "checkpoint_ns": "ns1"}}
    checkpoint = {
        "id": "my-checkpoint-id",
        "channel_values": {},
        "channel_versions": {},
        "versions_seen": {},
        "pending_sends": [],
    }

    result = await saver.aput(config, checkpoint, {}, {})

    assert result["configurable"]["checkpoint_id"] == "my-checkpoint-id"
    assert result["configurable"]["thread_id"] == "thread-1"
    assert result["configurable"]["checkpoint_ns"] == "ns1"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_aget_tuple_returns_checkpoint_with_data() -> None:
    """Test that aget_tuple returns checkpoint data correctly."""
    client = MockFoundryCheckpointClient()
    saver = TestableFoundryCheckpointSaver(client=client)

    # Save a checkpoint first
    config = {"configurable": {"thread_id": "thread-1", "checkpoint_ns": ""}}
    checkpoint = {
        "id": "cp-001",
        "channel_values": {},
        "channel_versions": {},
        "versions_seen": {},
        "pending_sends": [],
    }
    metadata = {"source": "test", "step": 1}

    await saver.aput(config, checkpoint, metadata, {})

    # Now retrieve it
    get_config = {"configurable": {"thread_id": "thread-1", "checkpoint_id": "cp-001"}}
    result = await saver.aget_tuple(get_config)

    assert result is not None
    assert result.checkpoint["id"] == "cp-001"
    assert result.metadata["source"] == "test"
    assert result.metadata["step"] == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_aget_tuple_returns_latest_without_checkpoint_id() -> None:
    """Test that aget_tuple returns the latest checkpoint when no ID specified."""
    client = MockFoundryCheckpointClient()
    saver = TestableFoundryCheckpointSaver(client=client)

    # Save multiple checkpoints
    config = {"configurable": {"thread_id": "thread-1", "checkpoint_ns": ""}}

    for i in range(3):
        checkpoint = {
            "id": f"cp-00{i}",
            "channel_values": {},
            "channel_versions": {},
            "versions_seen": {},
            "pending_sends": [],
        }
        config = await saver.aput(config, checkpoint, {"step": i}, {})

    # Retrieve without specifying checkpoint_id
    get_config = {"configurable": {"thread_id": "thread-1"}}
    result = await saver.aget_tuple(get_config)

    assert result is not None
    # Should get the latest (max checkpoint_id)
    assert result.checkpoint["id"] == "cp-002"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_aput_writes_creates_write_items() -> None:
    """Test that aput_writes creates write items."""
    client = MockFoundryCheckpointClient()
    saver = TestableFoundryCheckpointSaver(client=client)

    # First create a checkpoint
    config = {"configurable": {"thread_id": "thread-1", "checkpoint_ns": ""}}
    checkpoint = {
        "id": "cp-001",
        "channel_values": {},
        "channel_versions": {},
        "versions_seen": {},
        "pending_sends": [],
    }
    config = await saver.aput(config, checkpoint, {}, {})

    # Now add writes
    writes = [("channel1", "value1"), ("channel2", "value2")]
    await saver.aput_writes(config, writes, task_id="task-1")

    # Should have 3 items: checkpoint + 2 writes
    item_ids = await client.list_item_ids("thread-1")
    assert len(item_ids) == 3


@pytest.mark.unit
@pytest.mark.asyncio
async def test_aget_tuple_returns_pending_writes() -> None:
    """Test that aget_tuple includes pending writes."""
    client = MockFoundryCheckpointClient()
    saver = TestableFoundryCheckpointSaver(client=client)

    # Create checkpoint and add writes
    config = {"configurable": {"thread_id": "thread-1", "checkpoint_ns": ""}}
    checkpoint = {
        "id": "cp-001",
        "channel_values": {},
        "channel_versions": {},
        "versions_seen": {},
        "pending_sends": [],
    }
    config = await saver.aput(config, checkpoint, {}, {})

    writes = [("channel1", "value1")]
    await saver.aput_writes(config, writes, task_id="task-1")

    # Retrieve and check pending writes
    result = await saver.aget_tuple(config)

    assert result is not None
    assert result.pending_writes is not None
    assert len(result.pending_writes) == 1
    assert result.pending_writes[0][1] == "channel1"
    assert result.pending_writes[0][2] == "value1"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_alist_returns_checkpoints_in_order() -> None:
    """Test that alist returns checkpoints in reverse order."""
    client = MockFoundryCheckpointClient()
    saver = TestableFoundryCheckpointSaver(client=client)

    # Save multiple checkpoints
    config = {"configurable": {"thread_id": "thread-1", "checkpoint_ns": ""}}
    for i in range(3):
        checkpoint = {
            "id": f"cp-00{i}",
            "channel_values": {},
            "channel_versions": {},
            "versions_seen": {},
            "pending_sends": [],
        }
        config = await saver.aput(config, checkpoint, {"step": i}, {})

    # List checkpoints
    list_config = {"configurable": {"thread_id": "thread-1"}}
    results = []
    async for cp in saver.alist(list_config):
        results.append(cp)

    assert len(results) == 3
    # Should be in reverse order (newest first)
    assert results[0].checkpoint["id"] == "cp-002"
    assert results[1].checkpoint["id"] == "cp-001"
    assert results[2].checkpoint["id"] == "cp-000"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_alist_filters_by_namespace() -> None:
    """Test that alist filters by checkpoint namespace."""
    client = MockFoundryCheckpointClient()
    saver = TestableFoundryCheckpointSaver(client=client)

    # Save checkpoints in different namespaces
    for ns in ["ns1", "ns2"]:
        config = {"configurable": {"thread_id": "thread-1", "checkpoint_ns": ns}}
        checkpoint = {
            "id": f"cp-{ns}",
            "channel_values": {},
            "channel_versions": {},
            "versions_seen": {},
            "pending_sends": [],
        }
        await saver.aput(config, checkpoint, {}, {})

    # List only ns1
    list_config = {"configurable": {"thread_id": "thread-1", "checkpoint_ns": "ns1"}}
    results = []
    async for cp in saver.alist(list_config):
        results.append(cp)

    assert len(results) == 1
    assert results[0].checkpoint["id"] == "cp-ns1"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_alist_applies_limit() -> None:
    """Test that alist respects the limit parameter."""
    client = MockFoundryCheckpointClient()
    saver = TestableFoundryCheckpointSaver(client=client)

    # Save multiple checkpoints
    config = {"configurable": {"thread_id": "thread-1", "checkpoint_ns": ""}}
    for i in range(5):
        checkpoint = {
            "id": f"cp-00{i}",
            "channel_values": {},
            "channel_versions": {},
            "versions_seen": {},
            "pending_sends": [],
        }
        config = await saver.aput(config, checkpoint, {}, {})

    # List with limit
    list_config = {"configurable": {"thread_id": "thread-1"}}
    results = []
    async for cp in saver.alist(list_config, limit=2):
        results.append(cp)

    assert len(results) == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_adelete_thread_deletes_session() -> None:
    """Test that adelete_thread removes all checkpoints for a thread."""
    client = MockFoundryCheckpointClient()
    saver = TestableFoundryCheckpointSaver(client=client)

    # Create a checkpoint
    config = {"configurable": {"thread_id": "thread-1", "checkpoint_ns": ""}}
    checkpoint = {
        "id": "cp-001",
        "channel_values": {},
        "channel_versions": {},
        "versions_seen": {},
        "pending_sends": [],
    }
    await saver.aput(config, checkpoint, {}, {})

    # Verify it exists
    item_ids = await client.list_item_ids("thread-1")
    assert len(item_ids) == 1

    # Delete the thread
    await saver.adelete_thread("thread-1")

    # Verify it's gone
    item_ids = await client.list_item_ids("thread-1")
    assert len(item_ids) == 0


@pytest.mark.unit
def test_sync_methods_raise_not_implemented() -> None:
    """Test that sync methods raise NotImplementedError."""
    client = MockFoundryCheckpointClient()
    saver = TestableFoundryCheckpointSaver(client=client)

    config = {"configurable": {"thread_id": "thread-1"}}
    checkpoint = {"id": "cp-001", "channel_values": {}, "channel_versions": {}}

    with pytest.raises(NotImplementedError, match="aget_tuple"):
        saver.get_tuple(config)

    with pytest.raises(NotImplementedError, match="aput"):
        saver.put(config, checkpoint, {}, {})

    with pytest.raises(NotImplementedError, match="aput_writes"):
        saver.put_writes(config, [], "task-1")

    with pytest.raises(NotImplementedError, match="alist"):
        list(saver.list(config))

    with pytest.raises(NotImplementedError, match="adelete_thread"):
        saver.delete_thread("thread-1")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_aget_tuple_returns_parent_config() -> None:
    """Test that aget_tuple includes parent config when checkpoint has parent."""
    client = MockFoundryCheckpointClient()
    saver = TestableFoundryCheckpointSaver(client=client)

    # Save parent checkpoint
    config = {"configurable": {"thread_id": "thread-1", "checkpoint_ns": ""}}
    parent_checkpoint = {
        "id": "cp-001",
        "channel_values": {},
        "channel_versions": {},
        "versions_seen": {},
        "pending_sends": [],
    }
    config = await saver.aput(config, parent_checkpoint, {}, {})

    # Save child checkpoint
    child_checkpoint = {
        "id": "cp-002",
        "channel_values": {},
        "channel_versions": {},
        "versions_seen": {},
        "pending_sends": [],
    }
    await saver.aput(config, child_checkpoint, {}, {})

    # Retrieve child
    get_config = {"configurable": {"thread_id": "thread-1", "checkpoint_id": "cp-002"}}
    result = await saver.aget_tuple(get_config)

    assert result is not None
    assert result.parent_config is not None
    assert result.parent_config["configurable"]["checkpoint_id"] == "cp-001"


@pytest.mark.unit
def test_constructor_requires_async_credential() -> None:
    """Test that FoundryCheckpointSaver raises TypeError for sync credentials."""
    mock_credential = Mock(spec=TokenCredential)

    with pytest.raises(TypeError, match="AsyncTokenCredential"):
        FoundryCheckpointSaver(
            project_endpoint="https://test.services.ai.azure.com/api/projects/test",
            credential=mock_credential,
        )


@pytest.mark.unit
def test_constructor_accepts_async_credential() -> None:
    """Test that FoundryCheckpointSaver accepts AsyncTokenCredential."""
    mock_credential = Mock(spec=AsyncTokenCredential)

    saver = FoundryCheckpointSaver(
        project_endpoint="https://test.services.ai.azure.com/api/projects/test",
        credential=mock_credential,
    )

    assert saver is not None
    assert saver._client is not None
