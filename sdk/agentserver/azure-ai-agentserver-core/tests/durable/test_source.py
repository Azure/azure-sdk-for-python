"""Tests for source field support on TaskInfo and TaskCreateRequest."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from azure.ai.agentserver.core.durable._models import (
    TaskCreateRequest,
    TaskInfo,
)


class TestTaskInfoSource:
    """Source field on TaskInfo."""

    def test_default_none(self):
        info = TaskInfo(id="t1", agent_name="a", session_id="s", status="pending")
        assert info.source is None

    def test_set_at_construction(self):
        src = {"type": "user", "origin": "cli"}
        info = TaskInfo(id="t1", agent_name="a", session_id="s", status="pending", source=src)
        assert info.source == src

    def test_to_dict_includes_source(self):
        src = {"type": "api", "request_id": "r1"}
        info = TaskInfo(id="t1", agent_name="a", session_id="s", status="pending", source=src)
        d = info.to_dict()
        assert d["source"] == src

    def test_to_dict_omits_none_source(self):
        info = TaskInfo(id="t1", agent_name="a", session_id="s", status="pending")
        d = info.to_dict()
        assert "source" not in d

    def test_from_dict_with_source(self):
        data = {
            "id": "t1",
            "agent_name": "a",
            "session_id": "s",
            "status": "pending",
            "source": {"type": "workflow", "step": 3},
        }
        info = TaskInfo.from_dict(data)
        assert info.source == {"type": "workflow", "step": 3}

    def test_from_dict_without_source(self):
        data = {"id": "t1", "agent_name": "a", "session_id": "s", "status": "pending"}
        info = TaskInfo.from_dict(data)
        assert info.source is None

    def test_round_trip(self):
        src = {"origin": "test", "nested": {"a": 1}}
        info = TaskInfo(id="t1", agent_name="a", session_id="s", status="pending", source=src)
        restored = TaskInfo.from_dict(info.to_dict())
        assert restored.source == src


class TestTaskCreateRequestSource:
    """Source field on TaskCreateRequest."""

    def test_default_none(self):
        req = TaskCreateRequest(agent_name="a", session_id="s")
        assert req.source is None

    def test_set_at_construction(self):
        src = {"type": "decorator"}
        req = TaskCreateRequest(agent_name="a", session_id="s", source=src)
        assert req.source == src


class TestSourceLocalProvider:
    """Source persisted via LocalFileDurableTaskProvider."""

    @pytest.mark.asyncio
    async def test_source_persisted_and_retrieved(self, tmp_path):
        from azure.ai.agentserver.core.durable._local_provider import (
            LocalFileDurableTaskProvider,
        )

        provider = LocalFileDurableTaskProvider(Path(str(tmp_path)))
        src = {"type": "test", "run_id": "abc123"}
        req = TaskCreateRequest(
            agent_name="agent",
            session_id="test-session",
            source=src,
        )
        created = await provider.create(req)
        assert created.source == src

        # Re-read from disk
        fetched = await provider.get(created.id)
        assert fetched is not None
        assert fetched.source == src

    @pytest.mark.asyncio
    async def test_source_none_not_persisted(self, tmp_path):
        from azure.ai.agentserver.core.durable._local_provider import (
            LocalFileDurableTaskProvider,
        )

        provider = LocalFileDurableTaskProvider(Path(str(tmp_path)))
        req = TaskCreateRequest(agent_name="agent", session_id="test-session")
        created = await provider.create(req)
        assert created.source is None

        fetched = await provider.get(created.id)
        assert fetched is not None
        assert fetched.source is None

    @pytest.mark.asyncio
    async def test_source_immutable_after_create(self, tmp_path):
        """Source must not be changeable via PATCH — TaskPatchRequest has no source field."""
        from azure.ai.agentserver.core.durable._local_provider import (
            LocalFileDurableTaskProvider,
        )
        from azure.ai.agentserver.core.durable._models import TaskPatchRequest

        provider = LocalFileDurableTaskProvider(Path(str(tmp_path)))
        req = TaskCreateRequest(
            agent_name="agent",
            session_id="test-session",
            source={"type": "original"},
        )
        created = await provider.create(req)

        # Patch does not touch source
        await provider.update(created.id, TaskPatchRequest(tags={"k": "v"}))
        fetched = await provider.get(created.id)
        assert fetched is not None
        assert fetched.source == {"type": "original"}
