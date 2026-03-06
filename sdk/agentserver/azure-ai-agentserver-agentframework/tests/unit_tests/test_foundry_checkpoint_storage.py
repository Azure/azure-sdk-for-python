# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for FoundryCheckpointStorage."""

import pytest
from agent_framework import WorkflowCheckpoint

from azure.ai.agentserver.agentframework.persistence import FoundryCheckpointStorage

from .mocks import MockFoundryCheckpointClient


@pytest.mark.unit
@pytest.mark.asyncio
async def test_save_checkpoint_returns_checkpoint_id() -> None:
    """Test that save_checkpoint returns the checkpoint ID."""
    client = MockFoundryCheckpointClient()
    storage = FoundryCheckpointStorage(client=client, session_id="session-1")

    checkpoint = WorkflowCheckpoint(
        checkpoint_id="cp-123",
        workflow_id="wf-1",
    )

    result = await storage.save_checkpoint(checkpoint)

    assert result == "cp-123"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_load_checkpoint_returns_checkpoint() -> None:
    """Test that load_checkpoint returns the checkpoint."""
    client = MockFoundryCheckpointClient()
    storage = FoundryCheckpointStorage(client=client, session_id="session-1")

    checkpoint = WorkflowCheckpoint(
        checkpoint_id="cp-123",
        workflow_id="wf-1",
        iteration_count=5,
    )

    await storage.save_checkpoint(checkpoint)
    loaded = await storage.load_checkpoint("cp-123")

    assert loaded is not None
    assert loaded.checkpoint_id == "cp-123"
    assert loaded.workflow_id == "wf-1"
    assert loaded.iteration_count == 5


@pytest.mark.unit
@pytest.mark.asyncio
async def test_load_checkpoint_returns_none_for_missing() -> None:
    """Test that load_checkpoint returns None for missing checkpoint."""
    client = MockFoundryCheckpointClient()
    storage = FoundryCheckpointStorage(client=client, session_id="session-1")

    loaded = await storage.load_checkpoint("nonexistent")

    assert loaded is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_checkpoint_ids_returns_all_ids() -> None:
    """Test that list_checkpoint_ids returns all checkpoint IDs."""
    client = MockFoundryCheckpointClient()
    storage = FoundryCheckpointStorage(client=client, session_id="session-1")

    cp1 = WorkflowCheckpoint(checkpoint_id="cp-1", workflow_id="wf-1")
    cp2 = WorkflowCheckpoint(checkpoint_id="cp-2", workflow_id="wf-1")
    cp3 = WorkflowCheckpoint(checkpoint_id="cp-3", workflow_id="wf-2")

    await storage.save_checkpoint(cp1)
    await storage.save_checkpoint(cp2)
    await storage.save_checkpoint(cp3)

    ids = await storage.list_checkpoint_ids()

    assert set(ids) == {"cp-1", "cp-2", "cp-3"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_checkpoint_ids_filters_by_workflow() -> None:
    """Test that list_checkpoint_ids filters by workflow_id."""
    client = MockFoundryCheckpointClient()
    storage = FoundryCheckpointStorage(client=client, session_id="session-1")

    cp1 = WorkflowCheckpoint(checkpoint_id="cp-1", workflow_id="wf-1")
    cp2 = WorkflowCheckpoint(checkpoint_id="cp-2", workflow_id="wf-1")
    cp3 = WorkflowCheckpoint(checkpoint_id="cp-3", workflow_id="wf-2")

    await storage.save_checkpoint(cp1)
    await storage.save_checkpoint(cp2)
    await storage.save_checkpoint(cp3)

    ids = await storage.list_checkpoint_ids(workflow_id="wf-1")

    assert set(ids) == {"cp-1", "cp-2"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_checkpoints_returns_all_checkpoints() -> None:
    """Test that list_checkpoints returns all checkpoints."""
    client = MockFoundryCheckpointClient()
    storage = FoundryCheckpointStorage(client=client, session_id="session-1")

    cp1 = WorkflowCheckpoint(checkpoint_id="cp-1", workflow_id="wf-1")
    cp2 = WorkflowCheckpoint(checkpoint_id="cp-2", workflow_id="wf-2")

    await storage.save_checkpoint(cp1)
    await storage.save_checkpoint(cp2)

    checkpoints = await storage.list_checkpoints()

    assert len(checkpoints) == 2
    ids = {cp.checkpoint_id for cp in checkpoints}
    assert ids == {"cp-1", "cp-2"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_checkpoint_returns_true_for_existing() -> None:
    """Test that delete_checkpoint returns True for existing checkpoint."""
    client = MockFoundryCheckpointClient()
    storage = FoundryCheckpointStorage(client=client, session_id="session-1")

    checkpoint = WorkflowCheckpoint(checkpoint_id="cp-123", workflow_id="wf-1")
    await storage.save_checkpoint(checkpoint)

    deleted = await storage.delete_checkpoint("cp-123")

    assert deleted is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_checkpoint_returns_false_for_missing() -> None:
    """Test that delete_checkpoint returns False for missing checkpoint."""
    client = MockFoundryCheckpointClient()
    storage = FoundryCheckpointStorage(client=client, session_id="session-1")

    deleted = await storage.delete_checkpoint("nonexistent")

    assert deleted is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_checkpoint_removes_from_storage() -> None:
    """Test that delete_checkpoint actually removes the checkpoint."""
    client = MockFoundryCheckpointClient()
    storage = FoundryCheckpointStorage(client=client, session_id="session-1")

    checkpoint = WorkflowCheckpoint(checkpoint_id="cp-123", workflow_id="wf-1")
    await storage.save_checkpoint(checkpoint)

    await storage.delete_checkpoint("cp-123")
    loaded = await storage.load_checkpoint("cp-123")

    assert loaded is None
