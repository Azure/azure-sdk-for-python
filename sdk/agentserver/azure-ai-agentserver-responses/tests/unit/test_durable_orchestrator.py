# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for the durable orchestrator internal logic."""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from azure.ai.agentserver.responses.hosting._durable_orchestrator import (
    DurableResponseOrchestrator,
    _map_entry_mode,
)


class TestEntryModeMapping:
    """Tests for entry mode mapping logic."""

    def test_fresh_maps_to_fresh(self) -> None:
        assert _map_entry_mode("fresh") == "fresh"

    def test_resumed_maps_to_fresh(self) -> None:
        """Task primitive 'resumed' maps to durability 'fresh' (new turn ≠ crash)."""
        assert _map_entry_mode("resumed") == "fresh"

    def test_recovered_maps_to_recovered(self) -> None:
        assert _map_entry_mode("recovered") == "recovered"


class TestDurableOrchestratorTaskCreation:
    """Tests that the task function is created with correct parameters."""

    def test_orchestrator_creates_task_with_correct_name(self) -> None:
        orch = DurableResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=MagicMock(steerable_conversations=False, max_pending=10),
        )
        assert orch.task_fn is not None
        assert orch.task_fn._opts.name == "responses_durable_background"

    def test_orchestrator_steerable_option_passes_through(self) -> None:
        orch = DurableResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=MagicMock(steerable_conversations=True, max_pending=5),
        )
        assert orch.task_fn._opts.steerable is True
        assert orch.task_fn._opts.max_pending == 5

    def test_orchestrator_non_steerable_by_default(self) -> None:
        orch = DurableResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=MagicMock(steerable_conversations=False, max_pending=10),
        )
        assert orch.task_fn._opts.steerable is False

    def test_task_is_non_ephemeral(self) -> None:
        """Task lives for conversation lifetime (not deleted on completion)."""
        orch = DurableResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=MagicMock(steerable_conversations=False, max_pending=10),
        )
        assert orch.task_fn._opts.ephemeral is False

    def test_task_input_is_not_stored_via_decorator_option(self) -> None:
        """Per spec 015 FR-006: ``store_input`` option is removed from @task.

        Storage is automatic. This test asserts the option is no longer
        passed (or accepted) by the orchestrator's task descriptor.
        """
        orch = DurableResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=MagicMock(steerable_conversations=False, max_pending=10),
        )
        # The TaskOptions dataclass no longer carries store_input — accessing
        # the attribute should raise (or the orchestrator must not pass it).
        assert not hasattr(orch.task_fn._opts, "store_input")


class TestDurableOrchestratorExecuteInTask:
    """Tests for _execute_in_task (the task body)."""

    @pytest.mark.asyncio
    async def test_calls_run_background_non_stream(self) -> None:
        """Task body delegates to _run_background_non_stream."""
        orch = DurableResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=MagicMock(steerable_conversations=False, max_pending=10),
        )

        ctx = MagicMock()
        ctx.entry_mode = "fresh"
        ctx.retry_attempt = 0
        ctx.was_steered = False
        ctx.pending_inputs = []
        ctx.metadata = {}
        ctx.cancel = asyncio.Event()
        ctx.task_id = "test-task-id"
        ctx.suspend = AsyncMock()
        ctx.input = {
            "response_id": "resp_123",
            "_record_ref": MagicMock(),
            "_context_ref": MagicMock(),
            "_parsed_ref": MagicMock(),
            "_cancel_ref": asyncio.Event(),
            "_runtime_state_ref": MagicMock(),
            "agent_reference": None,
            "model": "gpt-4o",
            "store": True,
            "agent_session_id": None,
            "conversation_id": None,
            "history_limit": 100,
        }

        with patch(
            "azure.ai.agentserver.responses.hosting._orchestrator._run_background_non_stream",
            new_callable=AsyncMock,
        ) as mock_run_bg:
            await orch._execute_in_task(ctx)

        # Verify _run_background_non_stream was called
        mock_run_bg.assert_called_once()
        kwargs = mock_run_bg.call_args[1]
        assert kwargs["response_id"] == "resp_123"
        assert kwargs["model"] == "gpt-4o"

    @pytest.mark.asyncio
    async def test_durability_context_attached_to_response_context(self) -> None:
        """DurabilityContext is set on the response context."""
        orch = DurableResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=MagicMock(steerable_conversations=False, max_pending=10),
        )

        mock_context = MagicMock()
        ctx = MagicMock()
        ctx.entry_mode = "fresh"
        ctx.retry_attempt = 1
        ctx.was_steered = False
        ctx.pending_inputs = ["a", "b"]
        ctx.metadata = {}
        ctx.cancel = asyncio.Event()
        ctx.task_id = "test-task-id"
        ctx.suspend = AsyncMock()
        ctx.input = {
            "response_id": "resp_456",
            "_record_ref": MagicMock(),
            "_context_ref": mock_context,
            "_parsed_ref": MagicMock(),
            "_cancel_ref": asyncio.Event(),
            "_runtime_state_ref": MagicMock(),
        }

        with patch(
            "azure.ai.agentserver.responses.hosting._orchestrator._run_background_non_stream",
            new_callable=AsyncMock,
        ):
            await orch._execute_in_task(ctx)

        # Verify durability context was attached
        mock_context._durability = mock_context._durability  # was set
        dc = mock_context._durability
        assert dc.entry_mode == "fresh"
        assert dc.retry_attempt == 1
        assert dc.pending_inputs == 2

    @pytest.mark.asyncio
    async def test_steerable_suspends_after_completion(self) -> None:
        """In steerable mode, task suspends after handler completes."""
        orch = DurableResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=MagicMock(steerable_conversations=True, max_pending=10),
        )

        ctx = MagicMock()
        ctx.entry_mode = "fresh"
        ctx.retry_attempt = 0
        ctx.was_steered = False
        ctx.pending_inputs = []
        ctx.metadata = {}
        ctx.cancel = asyncio.Event()
        ctx.task_id = "test-task-id"
        ctx.suspend = AsyncMock()
        ctx.input = {
            "response_id": "resp_789",
            "_record_ref": MagicMock(),
            "_context_ref": MagicMock(),
            "_parsed_ref": MagicMock(),
            "_cancel_ref": asyncio.Event(),
            "_runtime_state_ref": MagicMock(),
        }

        with patch(
            "azure.ai.agentserver.responses.hosting._orchestrator._run_background_non_stream",
            new_callable=AsyncMock,
        ):
            await orch._execute_in_task(ctx)

        ctx.suspend.assert_called_once()
        assert "next_turn" in ctx.suspend.call_args[1].get("reason", "")

    @pytest.mark.asyncio
    async def test_non_steerable_does_not_suspend(self) -> None:
        """In non-steerable mode, task completes (no suspend)."""
        orch = DurableResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=MagicMock(steerable_conversations=False, max_pending=10),
        )

        ctx = MagicMock()
        ctx.entry_mode = "fresh"
        ctx.retry_attempt = 0
        ctx.was_steered = False
        ctx.pending_inputs = []
        ctx.metadata = {}
        ctx.cancel = asyncio.Event()
        ctx.task_id = "test-task-id"
        ctx.suspend = AsyncMock()
        ctx.input = {
            "response_id": "resp_000",
            "_record_ref": MagicMock(),
            "_context_ref": MagicMock(),
            "_parsed_ref": MagicMock(),
            "_cancel_ref": asyncio.Event(),
            "_runtime_state_ref": MagicMock(),
        }

        with patch(
            "azure.ai.agentserver.responses.hosting._orchestrator._run_background_non_stream",
            new_callable=AsyncMock,
        ):
            await orch._execute_in_task(ctx)

        ctx.suspend.assert_not_called()


class TestDurableOrchestratorCancellationBridge:
    """Tests for cancellation signal bridging."""

    @pytest.mark.asyncio
    async def test_cancel_bridge_propagates(self) -> None:
        """Task cancel event → response cancellation_signal."""
        orch = DurableResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=MagicMock(steerable_conversations=False, max_pending=10),
        )

        cancel_signal = asyncio.Event()
        ctx = MagicMock()
        ctx.entry_mode = "fresh"
        ctx.retry_attempt = 0
        ctx.was_steered = False
        ctx.pending_inputs = []
        ctx.metadata = {}
        ctx.cancel = asyncio.Event()
        ctx.task_id = "test-task-id"
        ctx.suspend = AsyncMock()
        ctx.input = {
            "response_id": "resp_cancel",
            "_record_ref": MagicMock(),
            "_context_ref": MagicMock(),
            "_parsed_ref": MagicMock(),
            "_cancel_ref": cancel_signal,
            "_runtime_state_ref": MagicMock(),
        }

        # Set cancel before execution starts
        ctx.cancel.set()

        with patch(
            "azure.ai.agentserver.responses.hosting._orchestrator._run_background_non_stream",
            new_callable=AsyncMock,
        ) as mock_run:
            await orch._execute_in_task(ctx)

        # The cancellation_signal passed to _run_background_non_stream should be set
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["cancellation_signal"].is_set()
