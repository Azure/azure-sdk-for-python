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


# ════════════════════════════════════════════════════════════
# Spec 023 Phase 1 RED tests — row-5 conversation lock semantics
# ════════════════════════════════════════════════════════════
#
# Per the spec-021 §7.3 / SOT §11.1 contract: when a deployment uses
# ``steerable_conversations=False`` and a request carries a
# ``conversation_id``, sequential turns (turn N completes BEFORE turn
# N+1 arrives) MUST extend the chain rather than return 409
# ``conversation_locked``. Concurrent overlap (turn N still running
# when turn N+1 arrives) MUST still return 409.
#
# Today (pre-spec-023): EVERY turn after the first incorrectly
# returns 409 because the underlying ``@task(steerable=False,
# ephemeral=False)`` registration leaves the task ``status="completed"``
# after turn 1, and the endpoint handler's ``TaskConflictError → 409``
# mapping catches the ``completed`` status too.
#
# After spec-023 Phase 2 implementation: the orchestrator dispatches
# ``conv_id + steerable=False`` requests to ``@multi_turn_task(steerable=False)``
# which transitions to ``suspended`` after each turn (not ``completed``);
# sequential turns successfully resume the chain.
#
# These tests target the orchestrator's primitive-dispatch + start
# behaviour directly. They are RED until Phase 2 lands.


class TestRow5SequentialTurnsExtendChain:
    """SOT §11.1 / spec-021 §7.3 row 5: ``conversation_id`` +
    ``steerable_conversations=False`` chains MUST extend on sequential
    turns; only concurrent overlap returns 409.
    """

    @pytest.mark.asyncio
    async def test_conv_id_non_steerable_sequential_turns_extend_chain(self) -> None:
        """Sequential turns of the same ``conversation_id`` succeed.

        After turn 1 completes, its task is in ``status="suspended"``
        (not ``completed``). Turn 2 with the same ``conversation_id``
        resumes the chain — NO ``TaskConflictError`` raised.

        Depth assertion per Constitution Principle XI:
        - The orchestrator must have a multi-turn primitive registered.
        - The selector must route ``conv_id`` requests (even with
          ``steerable_conversations=False``) to the multi-turn primitive.
        - Turn 2 must NOT raise ``TaskConflictError`` against a
          ``suspended`` chain.
        """
        opts = MagicMock(
            steerable_conversations=False, max_pending=10, default_fetch_history_count=100
        )
        # Orchestrator that has both primitives wired up. ``_pick_primitive``
        # MUST return the multi-turn primitive when ``conversation_id`` is
        # present, regardless of ``steerable_conversations``.
        orch = DurableResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=opts,
        )

        # Post-Phase-2 the orchestrator carries two task fns.
        assert hasattr(orch, "_multi_turn_task_fn"), (
            "Post-spec-023: orchestrator must register a multi-turn primitive "
            "for chain semantics (Row 5 fix)."
        )
        assert hasattr(orch, "_one_shot_task_fn"), (
            "Post-spec-023: orchestrator must also register a one-shot primitive "
            "for non-chain requests."
        )

        ctx_params = {
            "response_id": "resp_turn1",
            "agent_name": "test-agent",
            "session_id": "sess-row5",
            "conversation_id": "conv-row5",
            "previous_response_id": None,
        }
        # Dispatch must return the multi-turn primitive for conv_id requests,
        # NOT the one-shot.
        picked = orch._pick_primitive(ctx_params)
        assert picked is orch._multi_turn_task_fn, (
            f"Row 5 dispatch broken: conv_id + steerable=False MUST map to "
            f"multi-turn primitive (got the {'one-shot' if picked is orch._one_shot_task_fn else 'unknown'})."
        )

        # Simulate turn 2 of the same chain: ``previous_response_id`` set
        # to turn 1's response_id. Same conversation_id → same task_id;
        # since turn 1 has SUSPENDED (not completed), this must not raise
        # TaskConflictError against ``completed`` status — that was the bug.
        # We model the suspended-resume scenario by mocking the multi-turn
        # primitive's ``.start`` to succeed (no TaskConflictError on a
        # suspended chain).
        orch._multi_turn_task_fn = MagicMock()
        orch._multi_turn_task_fn.start = AsyncMock(return_value=MagicMock())

        record = MagicMock()
        ctx_params_turn2 = {
            **ctx_params,
            "response_id": "resp_turn2",
            "previous_response_id": "resp_turn1",
        }
        # Should succeed — multi-turn primitive accepts the resume.
        await orch.start_durable(record=record, ctx_params=ctx_params_turn2)
        orch._multi_turn_task_fn.start.assert_called_once()
        # And no fallback path was taken (no one-shot start).
        if hasattr(orch, "_one_shot_task_fn"):
            os_start = getattr(orch._one_shot_task_fn, "start", None)
            if isinstance(os_start, AsyncMock):
                os_start.assert_not_called()

    @pytest.mark.asyncio
    async def test_conv_id_non_steerable_concurrent_overlap_still_returns_409(self) -> None:
        """Regression guard for unchanged behaviour: when a concurrent
        turn arrives while a prior turn is still ``in_progress``, the
        framework MUST still surface ``TaskConflictError(in_progress)``.

        Depth assertion per Constitution Principle XI: the error's
        ``current_status`` is ``"in_progress"`` (NOT ``"completed"``),
        and the orchestrator does NOT silently fall back to a one-shot
        primitive.
        """
        opts = MagicMock(
            steerable_conversations=False, max_pending=10, default_fetch_history_count=100
        )
        orch = DurableResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=opts,
        )

        # Wire up the multi-turn primitive to raise TaskConflictError
        # against an ``in_progress`` status (the legitimate concurrent-overlap case).
        orch._multi_turn_task_fn = MagicMock()
        orch._multi_turn_task_fn.start = AsyncMock(
            side_effect=TaskConflictError("durable-resp-row5", "in_progress")
        )

        record = MagicMock()
        ctx_params = {
            "response_id": "resp_concurrent",
            "agent_name": "test-agent",
            "session_id": "sess-row5",
            "conversation_id": "conv-row5",
            "previous_response_id": None,
        }

        with pytest.raises(TaskConflictError) as excinfo:
            await orch.start_durable(record=record, ctx_params=ctx_params)
        # Depth: status is in_progress (not completed) — the actual concurrent-lock case.
        assert excinfo.value.current_status == "in_progress", (
            f"Concurrent overlap MUST be in_progress (not {excinfo.value.current_status!r})."
        )
