# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for the durable orchestrator internal logic."""

from __future__ import annotations

import asyncio
from typing import Any, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from azure.ai.agentserver.responses.hosting._durable_orchestrator import (
    DurableResponseOrchestrator,
    _map_entry_mode,
)


class _FakeTaskMetadata(dict):
    """Test fixture mimicking the TaskMetadata callable+dict-like shape.

    Real TaskMetadata is callable for named namespaces; plain dicts are
    not. The orchestrator now uses ``ctx.metadata(_RESPONSES_NS)`` to
    reach the framework namespace, so unit-test fixtures must provide
    something that responds to ``__call__`` (returning an isolated
    sub-store) as well as ``__getitem__/__setitem__/get/in``.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._namespaces: dict[str, "_FakeTaskMetadata"] = {}

    def __call__(self, name: Optional[str] = None) -> "_FakeTaskMetadata":
        if name is None:
            return self
        ns = self._namespaces.get(name)
        if ns is None:
            ns = _FakeTaskMetadata()
            self._namespaces[name] = ns
        return ns

    async def flush(self) -> None:  # no-op for tests
        return None


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
            options=MagicMock(steerable_conversations=True),
        )
        assert orch.task_fn._opts.steerable is True
        # Per spec 015 FR-006, ``max_pending`` is no longer carried on
        # TaskOptions — server-side back-pressure lives at a different layer.
        assert not hasattr(orch.task_fn._opts, "max_pending")

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
        ctx.is_steered_turn = False  # Spec 016 FR-020: was_steered renamed
        ctx.pending_input_count = 0  # Spec 016 FR-019: pending_inputs Sequence renamed to live int count
        ctx.metadata = _FakeTaskMetadata()
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
        ctx.is_steered_turn = False  # Spec 016 FR-020: was_steered renamed
        ctx.pending_input_count = 2  # Spec 016 FR-019: pending_inputs Sequence renamed
        ctx.metadata = _FakeTaskMetadata()
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
        ctx.is_steered_turn = False  # Spec 016 FR-020: was_steered renamed
        ctx.pending_input_count = 0  # Spec 016 FR-019: pending_inputs Sequence renamed to live int count
        ctx.metadata = _FakeTaskMetadata()
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
        ctx.is_steered_turn = False  # Spec 016 FR-020: was_steered renamed
        ctx.pending_input_count = 0  # Spec 016 FR-019: pending_inputs Sequence renamed to live int count
        ctx.metadata = _FakeTaskMetadata()
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
        ctx.is_steered_turn = False  # Spec 016 FR-020: was_steered renamed
        ctx.pending_input_count = 0  # Spec 016 FR-019: pending_inputs Sequence renamed to live int count
        ctx.metadata = _FakeTaskMetadata()
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


# ════════════════════════════════════════════════════════════
# Spec 023 Phase 1 RED tests — per-request primitive dispatch
# ════════════════════════════════════════════════════════════
#
# Per the spec-021 §7.3 / SOT §6.6 matrix, the responses orchestrator
# selects between TWO underlying durable-task primitives per request:
#
#   | store | conv_id | prev_resp_id | steerable | Primitive  |
#   |-------|---------|--------------|-----------|------------|
#   | true  | absent  | absent       | (any)     | one-shot   |
#   | true  | absent  | present      | False     | one-shot   |
#   | true  | absent  | present      | True      | multi-turn |
#   | true  | present | (any)        | False     | multi-turn |
#   | true  | present | (any)        | True      | multi-turn |
#
# These tests target ``DurableResponseOrchestrator._pick_primitive`` and
# the two-primitive construction. They are RED until Phase 2 lands
# both primitives.


class TestPrimitiveSelectionMatrix:
    """SOT §6.6 / spec-021 §7.3 — per-request primitive selection."""

    @pytest.mark.parametrize(
        "conv_id,prev_id,steerable,expected_attr,case_id",
        [
            (None, None, False, "_one_shot_task_fn", "no_conv_no_prev_steer_off"),
            (None, None, True, "_one_shot_task_fn", "no_conv_no_prev_steer_on"),
            (None, "resp_x", False, "_one_shot_task_fn", "no_conv_prev_steer_off"),
            (None, "resp_x", True, "_multi_turn_task_fn", "no_conv_prev_steer_on"),
            ("conv_1", None, False, "_multi_turn_task_fn", "conv_no_prev_steer_off"),
            ("conv_1", None, True, "_multi_turn_task_fn", "conv_no_prev_steer_on"),
            ("conv_1", "resp_x", False, "_multi_turn_task_fn", "conv_prev_steer_off"),
            ("conv_1", "resp_x", True, "_multi_turn_task_fn", "conv_prev_steer_on"),
        ],
        ids=lambda v: v if isinstance(v, str) else repr(v),
    )
    def test_pick_primitive_matrix(
        self,
        conv_id: Optional[str],
        prev_id: Optional[str],
        steerable: bool,
        expected_attr: str,
        case_id: str,
    ) -> None:
        """Every row of the SOT §6.6 matrix routes to the expected primitive.

        Depth assertion per Constitution Principle XI: the returned
        primitive is the EXACT instance (``is`` comparison) of one of
        the two registered task fns — not just "a Task was returned".
        """
        opts = MagicMock(
            steerable_conversations=steerable,
            max_pending=10,
            default_fetch_history_count=100,
        )
        orch = DurableResponseOrchestrator(
            create_fn=AsyncMock(), provider=MagicMock(), options=opts,
        )

        # Both primitives must exist (precondition for the matrix).
        assert hasattr(orch, "_one_shot_task_fn"), (
            f"{case_id}: orchestrator must register a one-shot primitive."
        )
        assert hasattr(orch, "_multi_turn_task_fn"), (
            f"{case_id}: orchestrator must register a multi-turn primitive."
        )

        ctx_params = {
            "response_id": "resp_test",
            "agent_name": "test-agent",
            "session_id": "sess-1",
            "conversation_id": conv_id,
            "previous_response_id": prev_id,
        }
        picked = orch._pick_primitive(ctx_params)
        expected = getattr(orch, expected_attr)
        assert picked is expected, (
            f"{case_id}: pick_primitive routed to wrong primitive. "
            f"Expected {expected_attr}, got "
            f"{'_one_shot_task_fn' if picked is orch._one_shot_task_fn else '_multi_turn_task_fn' if picked is orch._multi_turn_task_fn else 'unknown'}."
        )


class TestOrchestratorConstructionValidation:
    """SOT §6.6 + Constitution Principle V (fail-fast configuration)."""

    def test_orchestrator_registers_both_primitives_on_construction(self) -> None:
        """Construction MUST register both task fns even if the
        deployment will only use one of them.

        Depth assertion per Constitution Principle V: the validation
        runs at __init__ time (not lazily at request time), so a
        deployment that mis-imports the core wheel fails fast at
        server startup instead of per-request.
        """
        opts = MagicMock(
            steerable_conversations=False, max_pending=10, default_fetch_history_count=100
        )
        orch = DurableResponseOrchestrator(
            create_fn=AsyncMock(), provider=MagicMock(), options=opts,
        )

        # Both registrations are present.
        assert hasattr(orch, "_one_shot_task_fn"), (
            "Construction must register the one-shot primitive."
        )
        assert hasattr(orch, "_multi_turn_task_fn"), (
            "Construction must register the multi-turn primitive."
        )

        # Names are distinct and well-formed.
        one_shot_name = orch._one_shot_task_fn._opts.name
        multi_turn_name = orch._multi_turn_task_fn._opts.name
        assert one_shot_name != multi_turn_name, (
            f"Primitives must have distinct registration names "
            f"(both got {one_shot_name!r})."
        )
        assert "one_shot" in one_shot_name or "oneshot" in one_shot_name, (
            f"One-shot primitive name should reflect its kind (got {one_shot_name!r})."
        )
        assert "multi_turn" in multi_turn_name or "multiturn" in multi_turn_name, (
            f"Multi-turn primitive name should reflect its kind (got {multi_turn_name!r})."
        )

        # The multi-turn primitive's steerable flag MUST match the
        # deployment's steerable_conversations option (per SOT §6.6).
        assert orch._multi_turn_task_fn._opts.steerable is False, (
            "Multi-turn primitive's steerable flag must match "
            "options.steerable_conversations."
        )

    def test_orchestrator_multi_turn_steerable_flag_propagated(self) -> None:
        """With ``steerable_conversations=True``, the multi-turn primitive
        is registered with ``steerable=True``."""
        opts = MagicMock(
            steerable_conversations=True, max_pending=10, default_fetch_history_count=100
        )
        orch = DurableResponseOrchestrator(
            create_fn=AsyncMock(), provider=MagicMock(), options=opts,
        )
        assert orch._multi_turn_task_fn._opts.steerable is True, (
            "Steerable flag must propagate from options to multi-turn primitive."
        )
