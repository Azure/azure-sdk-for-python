# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the LocalFileDurableTaskProvider."""

import json
from pathlib import Path
from typing import Any

import pytest

from azure.ai.agentserver.core.durable._local_provider import (
    LocalFileDurableTaskProvider,
)
from azure.ai.agentserver.core.durable._models import (
    TaskCreateRequest,
    TaskPatchRequest,
)


@pytest.fixture
def provider(tmp_path: Path) -> LocalFileDurableTaskProvider:
    """Create a local provider backed by a temp directory."""
    return LocalFileDurableTaskProvider(base_dir=tmp_path)


@pytest.fixture
def sample_create_request() -> TaskCreateRequest:
    """A minimal task creation request."""
    return TaskCreateRequest(
        agent_name="test-agent",
        session_id="session-001",
        status="pending",
        payload={"input": {"data": "hello"}},
        lease_owner="owner-1",
        lease_instance_id="inst-1",
        lease_duration_seconds=60,
    )


class TestLocalProviderCRUD:
    """Create, read, update operations on the local provider."""

    @pytest.mark.asyncio
    async def test_create_and_get(
        self, provider: LocalFileDurableTaskProvider, sample_create_request: TaskCreateRequest
    ) -> None:
        """create returns a TaskInfo; get retrieves it."""
        task = await provider.create(sample_create_request)
        assert task.id
        assert task.status == "pending"
        assert task.agent_name == "test-agent"

        fetched = await provider.get(task.id)
        assert fetched is not None
        assert fetched.id == task.id

    @pytest.mark.asyncio
    async def test_update_status(
        self, provider: LocalFileDurableTaskProvider, sample_create_request: TaskCreateRequest
    ) -> None:
        """update changes the status."""
        task = await provider.create(sample_create_request)
        patch = TaskPatchRequest(
            status="in_progress",
            if_match=task.etag,
        )
        updated = await provider.update(task.id, patch)
        assert updated.status == "in_progress"

    @pytest.mark.asyncio
    async def test_update_payload(
        self, provider: LocalFileDurableTaskProvider, sample_create_request: TaskCreateRequest
    ) -> None:
        """update merges payload."""
        task = await provider.create(sample_create_request)
        patch = TaskPatchRequest(
            payload={"output": {"result": 42}},
            if_match=task.etag,
        )
        updated = await provider.update(task.id, patch)
        assert updated.payload is not None
        assert updated.payload["output"]["result"] == 42
        # Original input preserved
        assert updated.payload["input"]["data"] == "hello"

    @pytest.mark.asyncio
    async def test_etag_mismatch_raises(
        self, provider: LocalFileDurableTaskProvider, sample_create_request: TaskCreateRequest
    ) -> None:
        """update raises on ETag mismatch."""
        task = await provider.create(sample_create_request)
        patch = TaskPatchRequest(
            status="in_progress",
            if_match="wrong-etag",
        )
        with pytest.raises(ValueError, match="ETag mismatch"):
            await provider.update(task.id, patch)

    @pytest.mark.asyncio
    async def test_get_nonexistent_returns_none(self, provider: LocalFileDurableTaskProvider) -> None:
        """get returns None for nonexistent task."""
        result = await provider.get("nonexistent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_task(
        self, provider: LocalFileDurableTaskProvider, sample_create_request: TaskCreateRequest
    ) -> None:
        """delete removes a task."""
        task = await provider.create(sample_create_request)
        await provider.delete(task.id)
        result = await provider.get(task.id)
        assert result is None


class TestLocalProviderListing:
    """Tests for listing/querying tasks."""

    @pytest.mark.asyncio
    async def test_list_tasks_by_agent(self, provider: LocalFileDurableTaskProvider) -> None:
        """list filters by agent_name and session_id."""
        req1 = TaskCreateRequest(
            agent_name="agent-a",
            session_id="s1",
            status="pending",
            payload={},
        )
        req2 = TaskCreateRequest(
            agent_name="agent-b",
            session_id="s1",
            status="pending",
            payload={},
        )
        await provider.create(req1)
        await provider.create(req2)

        tasks = await provider.list(agent_name="agent-a", session_id="s1")
        assert len(tasks) == 1
        assert tasks[0].agent_name == "agent-a"

    @pytest.mark.asyncio
    async def test_list_tasks_by_status(self, provider: LocalFileDurableTaskProvider) -> None:
        """list filters by status."""
        req = TaskCreateRequest(
            agent_name="agent",
            session_id="s1",
            status="pending",
            payload={},
        )
        task = await provider.create(req)
        patch = TaskPatchRequest(
            status="in_progress",
            if_match=task.etag,
        )
        await provider.update(task.id, patch)

        pending = await provider.list(agent_name="agent", session_id="s1", status="pending")
        assert len(pending) == 0

        active = await provider.list(agent_name="agent", session_id="s1", status="in_progress")
        assert len(active) == 1
