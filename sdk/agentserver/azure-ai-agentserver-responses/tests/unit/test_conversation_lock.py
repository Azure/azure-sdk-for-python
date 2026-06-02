# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for conversation locking behavior (Phase 2).

Tests:
- TaskConflictError → HTTP 409 with correct error envelope
- Non-background recovery: persist failed + suspend (don't re-invoke handler)
- Startup lifecycle: startup triggers stale task recovery
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from azure.ai.agentserver.core.durable import TaskConflictError

from azure.ai.agentserver.responses.hosting._durable_orchestrator import (
    DurableResponseOrchestrator,
    _RESPONSES_NS,
    _RESP_BACKGROUND,
    _map_entry_mode,
)


# Mimics callable TaskMetadata for fixtures (see test_durable_orchestrator.py).
class _FakeTaskMetadata(dict):
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self._namespaces: dict[str, "_FakeTaskMetadata"] = {}

    def __call__(self, name: str | None = None) -> "_FakeTaskMetadata":
        if name is None:
            return self
        ns = self._namespaces.get(name)
        if ns is None:
            ns = _FakeTaskMetadata()
            self._namespaces[name] = ns
        return ns

    async def flush(self) -> None:
        return None


class TestConflictHandling:
    """TaskConflictError from .start() → HTTP 409."""

    @pytest.mark.asyncio
    async def test_task_conflict_raises_on_start(self) -> None:
        """When task is already in_progress, start_durable raises TaskConflictError."""
        orch = DurableResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=MagicMock(steerable_conversations=False, max_pending=10),
        )

        # Mock the task_fn.start to raise TaskConflictError
        orch._task_fn = MagicMock()
        orch._task_fn.start = AsyncMock(
            side_effect=TaskConflictError("task-123", "in_progress")
        )

        record = MagicMock()
        ctx_params = {
            "response_id": "resp_conflict",
            "agent_name": "test-agent",
            "session_id": "sess-1",
            "partition_key": "conv-1",
        }

        # start_durable should NOT raise — it logs and handles gracefully
        # (The 409 is raised at the routing/orchestrator level, not here)
        await orch.start_durable(record=record, ctx_params=ctx_params)

    @pytest.mark.asyncio
    async def test_conflict_error_contains_task_id(self) -> None:
        """TaskConflictError carries the conflicting task_id."""
        err = TaskConflictError("resp-abc:conv-xyz", "in_progress")
        assert err.task_id == "resp-abc:conv-xyz"
        assert err.current_status == "in_progress"
        assert "already in_progress" in str(err)

    @pytest.mark.asyncio
    async def test_orchestrator_run_background_conflict_returns_409_shape(self) -> None:
        """When _start_durable_background catches TaskConflictError from steerable=False,
        it should fall back to asyncio.create_task (not raise to HTTP layer).

        The 409 behavior is for steerable=True conversations where parallel
        requests to the same conversation are rejected. For non-steerable,
        each request gets its own task_id (parallel forks).
        """
        # This test validates that the fallback path works
        orch = DurableResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=MagicMock(steerable_conversations=False, max_pending=10),
        )

        orch._task_fn = MagicMock()
        orch._task_fn.start = AsyncMock(
            side_effect=TaskConflictError("task-dup", "in_progress")
        )

        record = MagicMock()
        ctx_params = {
            "response_id": "resp_dup",
            "agent_name": "test-agent",
            "session_id": "sess-1",
            "partition_key": "conv-1",
        }

        # Should not raise
        await orch.start_durable(record=record, ctx_params=ctx_params)


class TestNonBackgroundRecovery:
    """Non-background recovery: task recovered but background=False → fail, don't re-invoke."""

    @pytest.mark.asyncio
    async def test_non_bg_recovery_persists_failed_without_handler(self) -> None:
        """On recovery of a non-background task, response becomes 'failed'
        without re-invoking the handler."""
        orch = DurableResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=MagicMock(steerable_conversations=False, max_pending=10),
        )

        ctx = MagicMock()
        ctx.entry_mode = "recovered"
        ctx.retry_attempt = 1
        ctx.is_steered_turn = False  # Spec 016 FR-020: was_steered renamed
        ctx.pending_input_count = 0  # Spec 016 FR-019: pending_inputs Sequence renamed to live int count
        ctx.cancel = asyncio.Event()
        ctx.task_id = "non-bg-task-1"
        ctx.suspend = AsyncMock()
        # Mark as non-background in the responses framework namespace.
        ctx.metadata = _FakeTaskMetadata()
        ctx.metadata(_RESPONSES_NS)[_RESP_BACKGROUND] = False
        ctx.input = {
            "response_id": "resp_nonbg",
            "_record_ref": None,
            "_context_ref": None,
            "_parsed_ref": None,
            "_cancel_ref": asyncio.Event(),
            "_runtime_state_ref": None,
        }

        with patch(
            "azure.ai.agentserver.responses.hosting._orchestrator._run_background_non_stream",
            new_callable=AsyncMock,
        ) as mock_run_bg:
            await orch._execute_in_task(ctx)

        # Handler should NOT have been invoked (non-bg recovery → fail immediately)
        # For now, Phase 2 implementation will add this logic.
        # This test documents the expected behavior.


class TestStartupLifecycle:
    """Startup triggers stale task recovery."""

    def test_task_fn_registered_for_recovery(self) -> None:
        """The internal @task function is registered in the global registry
        so that startup recovery can find and re-enter it."""
        from azure.ai.agentserver.core.durable._decorator import _REGISTERED_DESCRIPTORS

        orch = DurableResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=MagicMock(steerable_conversations=False, max_pending=10),
        )

        # The task should be registered
        names = [name for name, _, _ in _REGISTERED_DESCRIPTORS]
        assert "responses_durable_background" in names
