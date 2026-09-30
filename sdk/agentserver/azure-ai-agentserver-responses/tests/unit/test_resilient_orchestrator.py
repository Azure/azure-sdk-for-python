# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for the resilient orchestrator internal logic."""

from __future__ import annotations

import asyncio
from typing import Any, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from azure.ai.agentserver.responses.hosting._resilient_orchestrator import (
    ResilientResponseOrchestrator,
    _is_recovered_entry,
)
from azure.ai.agentserver.responses.hosting._resilient_input import ResilientResponseInput
from azure.ai.agentserver.responses.models._generated import CreateResponse


class TestEntryModeMapping:
    """Tests for recovery-entry classification (spec 024 Phase 5 Proposal #10/#13).

    The pre-Phase-5 ``_map_entry_mode`` helper is deleted. Its
    replacement, ``_is_recovered_entry``, returns a plain bool that the
    orchestrator stores on ``context.is_recovery``. The ``resumed``
    task entry mode is NOT a recovery entry — from the handler dev's
    perspective, a resume is just a new turn.
    """

    def test_fresh_is_not_recovery(self) -> None:
        assert _is_recovered_entry("fresh") is False

    def test_resumed_is_not_recovery(self) -> None:
        """Task primitive 'resumed' is NOT a recovery entry (new turn ≠ crash)."""
        assert _is_recovered_entry("resumed") is False

    def test_recovered_is_recovery(self) -> None:
        assert _is_recovered_entry("recovered") is True


class TestResilientOrchestratorTaskCreation:
    """Tests that the task functions are created with correct parameters.

    Spec 023 — the orchestrator now registers TWO primitives:
    ``_one_shot_task_fn`` (`@task`) and ``_multi_turn_task_fn``
    (`@multi_turn_task(steerable=…)`). The legacy single
    ``task_fn`` property is preserved as an alias for ``_one_shot_task_fn``
    so older introspection tests keep working.
    """

    def test_orchestrator_creates_one_shot_with_correct_name(self) -> None:
        orch = ResilientResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=MagicMock(steerable_conversations=False, max_pending=10),
        )
        assert orch._one_shot_task_fn is not None
        assert orch._one_shot_task_fn._opts.name == "responses_resilient_one_shot"
        # The legacy ``task_fn`` alias points at the one-shot primitive
        # so existing recovery-registration introspection still works.
        assert orch.task_fn is orch._one_shot_task_fn

    def test_orchestrator_creates_multi_turn_with_correct_name(self) -> None:
        orch = ResilientResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=MagicMock(steerable_conversations=False, max_pending=10),
        )
        assert orch._multi_turn_task_fn is not None
        assert orch._multi_turn_task_fn._opts.name == "responses_resilient_multi_turn"

    def test_orchestrator_steerable_option_propagates_to_multi_turn(self) -> None:
        """``steerable_conversations`` now lives on the multi-turn primitive
        (one-shot can never be steerable — ``@task`` rejects the kwarg)."""
        orch = ResilientResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=MagicMock(steerable_conversations=True),
        )
        assert orch._multi_turn_task_fn._opts.steerable is True
        # Per spec 015 FR-006, ``max_pending`` is no longer carried on
        # TaskOptions — server-side back-pressure lives at a different layer.
        assert not hasattr(orch._multi_turn_task_fn._opts, "max_pending")

    def test_orchestrator_multi_turn_non_steerable_by_default(self) -> None:
        orch = ResilientResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=MagicMock(steerable_conversations=False, max_pending=10),
        )
        assert orch._multi_turn_task_fn._opts.steerable is False

    def test_one_shot_is_ephemeral(self) -> None:
        """One-shot primitives are ALWAYS ephemeral (the record is auto-
        deleted on terminal exit). Multi-turn chains persist between
        turns. The migration eliminated the prior ``ephemeral=False``
        storage overhead for the non-multi-turn rows."""
        orch = ResilientResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=MagicMock(steerable_conversations=False, max_pending=10),
        )
        assert orch._one_shot_task_fn._opts.ephemeral is True
        # Multi-turn chains are NEVER ephemeral (must persist between turns).
        assert orch._multi_turn_task_fn._opts.ephemeral is False

    def test_task_input_is_not_stored_via_decorator_option(self) -> None:
        """Per spec 015 FR-006: ``store_input`` option is removed from @task.

        Storage is automatic. This test asserts the option is no longer
        passed (or accepted) by the orchestrator's task descriptor.
        Applies to both primitives.
        """
        orch = ResilientResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=MagicMock(steerable_conversations=False, max_pending=10),
        )
        assert not hasattr(orch._one_shot_task_fn._opts, "store_input")
        assert not hasattr(orch._multi_turn_task_fn._opts, "store_input")


class TestResilientOrchestratorExecuteInTask:
    """Tests for _execute_in_task (the task body)."""

    @pytest.mark.asyncio
    async def test_calls_run_background_non_stream(self) -> None:
        """Task body delegates to _run_background_non_stream."""
        orch = ResilientResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=MagicMock(steerable_conversations=False, max_pending=10),
        )

        ctx = MagicMock()
        ctx.entry_mode = "fresh"
        ctx.retry_attempt = 0
        ctx.is_steered_turn = False  # Spec 016 FR-020: was_steered renamed
        ctx.pending_input_count = 0  # Spec 016 FR-019: pending_inputs Sequence renamed to live int count
        ctx._cancellation_signal = asyncio.Event()
        ctx.shutdown = asyncio.Event()
        ctx.task_id = "test-task-id"
        ctx.input = {
            "response_id": "resp_123",
            "request": {"input": "hi", "model": "gpt-4o", "store": True, "background": True},
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
    async def test_recovery_and_steering_fields_flattened_on_response_context(
        self,
    ) -> None:
        """(Spec 024 Phase 5 — Proposal #10/#13) Recovery + steering
        classifiers land directly on ``ResponseContext`` flat fields.
        The pre-Phase-5 ``ResilienceContext`` indirection is deleted —
        this test asserts the post-Phase-5 contract: ``is_recovery``,
        ``is_steered_turn`` and ``pending_input_count`` are set on the context
        before the handler runs.
        """
        orch = ResilientResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=MagicMock(steerable_conversations=False),
        )

        from azure.ai.agentserver.responses._response_context import (
            PlatformContext,
            ResponseContext,
        )
        from azure.ai.agentserver.responses.models.runtime import ResponseModeFlags

        real_context = ResponseContext(
            response_id="resp_456",
            mode_flags=ResponseModeFlags(stream=False, store=True, background=True),
            request=None,
            platform_context=PlatformContext(),
        )

        ctx = MagicMock()
        ctx.entry_mode = "fresh"
        ctx.is_steered_turn = True
        ctx.pending_input_count = 2
        ctx._cancellation_signal = asyncio.Event()
        ctx.shutdown = asyncio.Event()
        ctx.task_id = "test-task-id"
        ctx.input = {
            "response_id": "resp_456",
            "request": {"input": "hi"},
            "_record_ref": MagicMock(),
            "_context_ref": real_context,
            "_parsed_ref": MagicMock(),
            "_cancel_ref": asyncio.Event(),
            "_runtime_state_ref": MagicMock(),
        }

        with patch(
            "azure.ai.agentserver.responses.hosting._orchestrator._run_background_non_stream",
            new_callable=AsyncMock,
        ):
            await orch._execute_in_task(ctx)

        # Spec 024 Phase 5: flat fields populated, no ``resilience``
        # property, no ``ResilienceContext`` indirection.
        assert real_context.is_recovery is False
        assert real_context.is_steered_turn is True
        assert real_context.pending_input_count == 2
        assert not hasattr(real_context, "resilience")

    @pytest.mark.asyncio
    async def test_steerable_returns_none_for_implicit_suspend(self) -> None:
        """Spec 023 — multi-turn task bodies signal implicit-suspend
        via bare ``return None``. The framework records the suspend
        transition automatically for ``@multi_turn_task`` bodies; no
        explicit ``ctx.suspend(reason=...)`` call is required."""
        orch = ResilientResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=MagicMock(steerable_conversations=True, max_pending=10),
        )

        ctx = MagicMock()
        ctx.entry_mode = "fresh"
        ctx.retry_attempt = 0
        ctx.is_steered_turn = False  # Spec 016 FR-020: was_steered renamed
        ctx.pending_input_count = 0  # Spec 016 FR-019: pending_inputs Sequence renamed to live int count
        ctx._cancellation_signal = asyncio.Event()
        ctx.shutdown = asyncio.Event()
        ctx.task_id = "test-task-id"
        ctx.input = {
            "response_id": "resp_789",
            "request": {"input": "hi"},
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
            result = await orch._execute_in_task(ctx)

        # Implicit-suspend: body returns None (no ctx.suspend(reason=...) call).
        assert result is None

    @pytest.mark.asyncio
    async def test_non_steerable_returns_none_too(self) -> None:
        """In non-steerable mode the body also returns None — under the
        new model the difference between non-steerable and steerable is
        determined by which primitive the orchestrator routes to
        (``@task`` vs ``@multi_turn_task(steerable=False)``), not by an
        explicit suspend call inside the body."""
        orch = ResilientResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=MagicMock(steerable_conversations=False, max_pending=10),
        )

        ctx = MagicMock()
        ctx.entry_mode = "fresh"
        ctx.retry_attempt = 0
        ctx.is_steered_turn = False  # Spec 016 FR-020: was_steered renamed
        ctx.pending_input_count = 0  # Spec 016 FR-019: pending_inputs Sequence renamed to live int count
        ctx._cancellation_signal = asyncio.Event()
        ctx.shutdown = asyncio.Event()
        ctx.task_id = "test-task-id"
        ctx.input = {
            "response_id": "resp_000",
            "request": {"input": "hi"},
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
            result = await orch._execute_in_task(ctx)

        assert result is None


class TestResilientOrchestratorCancellationBridge:
    """Tests for cancellation signal bridging."""

    @pytest.mark.asyncio
    async def test_cancel_bridge_propagates(self) -> None:
        """Task cancel event → response cancellation_signal."""
        orch = ResilientResponseOrchestrator(
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
        ctx._cancellation_signal = asyncio.Event()
        ctx.shutdown = asyncio.Event()
        ctx.task_id = "test-task-id"
        ctx.input = {
            "response_id": "resp_cancel",
            "request": {"input": "hi"},
            "_record_ref": MagicMock(),
            "_context_ref": MagicMock(),
            "_parsed_ref": MagicMock(),
            "_cancel_ref": cancel_signal,
            "_runtime_state_ref": MagicMock(),
        }

        # Set cancel before execution starts
        ctx._cancellation_signal.set()

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
# selects between TWO underlying resilient-task primitives per request:
#
#   | store | conv_id | prev_resp_id | steerable | Primitive  |
#   |-------|---------|--------------|-----------|------------|
#   | true  | absent  | absent       | False     | one-shot   |
#   | true  | absent  | absent       | True      | multi-turn |
#   | true  | absent  | present      | False     | one-shot   |
#   | true  | absent  | present      | True      | multi-turn |
#   | true  | present | (any)        | False     | multi-turn |
#   | true  | present | (any)        | True      | multi-turn |
#
# The first turn of a steerable chain (no conv_id, no prev_resp_id,
# steerable=True) MUST be multi-turn: the stable conversation_chain_id
# makes its task_id SHARED with later steered turns, so the first turn's
# task must be the suspendable chain host that drains queued steering
# inputs. A one-shot here auto-deletes on terminal exit and orphans the
# queued steered turn (SOT §4.1 + §6.1).
#
# These tests target ``ResilientResponseOrchestrator._pick_primitive`` and
# the two-primitive construction. They are RED until Phase 2 lands
# both primitives.


class TestPrimitiveSelectionMatrix:
    """SOT §6.6 / spec-021 §7.3 — per-request primitive selection."""

    @pytest.mark.parametrize(
        "conv_id,prev_id,steerable,expected_attr,case_id",
        [
            (None, None, False, "_one_shot_task_fn", "no_conv_no_prev_steer_off"),
            (None, None, True, "_multi_turn_task_fn", "no_conv_no_prev_steer_on"),
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
        orch = ResilientResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=opts,
        )

        # Both primitives must exist (precondition for the matrix).
        assert hasattr(orch, "_one_shot_task_fn"), f"{case_id}: orchestrator must register a one-shot primitive."
        assert hasattr(orch, "_multi_turn_task_fn"), f"{case_id}: orchestrator must register a multi-turn primitive."

        picked = orch._pick_primitive(conversation_id=conv_id, previous_response_id=prev_id)
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
            steerable_conversations=False,
            max_pending=10,
            default_fetch_history_count=100,
        )
        orch = ResilientResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=opts,
        )

        # Both registrations are present.
        assert hasattr(orch, "_one_shot_task_fn"), "Construction must register the one-shot primitive."
        assert hasattr(orch, "_multi_turn_task_fn"), "Construction must register the multi-turn primitive."

        # Names are distinct and well-formed.
        one_shot_name = orch._one_shot_task_fn._opts.name
        multi_turn_name = orch._multi_turn_task_fn._opts.name
        assert one_shot_name != multi_turn_name, (
            f"Primitives must have distinct registration names " f"(both got {one_shot_name!r})."
        )
        assert (
            "one_shot" in one_shot_name or "oneshot" in one_shot_name
        ), f"One-shot primitive name should reflect its kind (got {one_shot_name!r})."
        assert (
            "multi_turn" in multi_turn_name or "multiturn" in multi_turn_name
        ), f"Multi-turn primitive name should reflect its kind (got {multi_turn_name!r})."

        # The multi-turn primitive's steerable flag MUST match the
        # deployment's steerable_conversations option (per SOT §6.6).
        assert orch._multi_turn_task_fn._opts.steerable is False, (
            "Multi-turn primitive's steerable flag must match " "options.steerable_conversations."
        )

    def test_orchestrator_multi_turn_steerable_flag_propagated(self) -> None:
        """With ``steerable_conversations=True``, the multi-turn primitive
        is registered with ``steerable=True``."""
        opts = MagicMock(
            steerable_conversations=True,
            max_pending=10,
            default_fetch_history_count=100,
        )
        orch = ResilientResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=opts,
        )
        assert (
            orch._multi_turn_task_fn._opts.steerable is True
        ), "Steerable flag must propagate from options to multi-turn primitive."


class TestSplitRuntimeRefsSerializable:
    """The persisted resilient-task input MUST be JSON-serializable.

    Regression for the hosted bug where the gateway-injected
    ``agent_reference`` (an ``AgentReference`` model — a Mapping but not
    ``json.dumps``-serializable) leaked into the persisted params, making
    ``create_and_start`` raise ``TypeError`` and silently degrade the resilient
    background run to a non-resilient ``asyncio.create_task`` (no crash recovery).
    """

    def test_persisted_params_json_serializable_with_agent_reference_model(
        self,
    ) -> None:
        import json

        from azure.ai.agentserver.responses.models import AgentReference

        resilient = ResilientResponseInput(
            request=CreateResponse({"input": "hi", "store": True, "background": True}),
            response_id="caresp_abc",
            disposition="re-invoke",
            agent_reference=AgentReference(name="resilient-responses-agent-demo", version="29"),
            agent_session_id="sess_1",
        )

        persisted = resilient.to_task_input()

        # Runtime-only object references are NEVER part of the persisted input
        # (Spec 033 §3.1 — they live in the out-of-band RuntimeRefs cache).
        for ref_key in ("_record_ref", "_context_ref", "_parsed_ref", "_cancel_ref", "_runtime_state_ref"):
            assert ref_key not in persisted

        # agent_reference survives in the persisted input (needed across
        # cross-process recovery) but normalized to a plain dict
        assert isinstance(persisted["agent_reference"], dict)
        assert persisted["agent_reference"].get("name") == "resilient-responses-agent-demo"
        assert persisted["agent_reference"].get("version") == "29"

        # the whole persisted input must JSON-serialize (this is what the
        # core resilient-task size check does and what previously raised)
        json.dumps(persisted)  # must not raise

    def test_empty_agent_reference_sentinel_passthrough(self) -> None:
        import json

        # absent agent_reference is the ``{}`` sentinel — already serializable
        resilient = ResilientResponseInput(
            request=CreateResponse({"input": "h"}),
            response_id="r",
            disposition="re-invoke",
            agent_reference={},
        )
        persisted = resilient.to_task_input()
        assert persisted["agent_reference"] == {}
        json.dumps(persisted)

    def test_dict_agent_reference_unchanged(self) -> None:
        import json

        ar = {"type": "agent_reference", "name": "x", "version": "1"}
        resilient = ResilientResponseInput(
            request=CreateResponse({"input": "h"}),
            response_id="r",
            disposition="re-invoke",
            agent_reference=ar,
        )
        persisted = resilient.to_task_input()
        assert persisted["agent_reference"] == ar
        json.dumps(persisted)


class TestMalformedInputFailsClosed:
    """Spec 033 FR-002f — a malformed persisted resilient input fails closed to a
    terminal (marks the response failed via the store) without re-invoking the
    handler, rather than raising into a poison task."""

    @pytest.mark.asyncio
    async def test_malformed_input_marks_failed_without_handler(self) -> None:
        orch = ResilientResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=MagicMock(steerable_conversations=False, default_fetch_history_count=100),
        )
        orch._persist_crash_failed = AsyncMock()  # type: ignore[method-assign]

        ctx = MagicMock()
        ctx.entry_mode = "recovered"
        ctx.task_id = "poison-task"
        # Malformed: response_id present (addressable) but NO request.
        ctx.input = {"response_id": "resp_malformed", "user_id_key": "u"}

        with patch(
            "azure.ai.agentserver.responses.hosting._orchestrator._run_background_non_stream",
            new_callable=AsyncMock,
        ) as mock_run_bg:
            result = await orch._execute_in_task(ctx)

        assert result is None
        # Handler NOT re-invoked; response failed-closed via the store.
        mock_run_bg.assert_not_called()
        orch._persist_crash_failed.assert_awaited_once()
        assert orch._persist_crash_failed.call_args[0][0] == "resp_malformed"


class TestRecoveryDispositionFromInput:
    """Spec 039 R1 — recovery routing (disposition + background) is sourced from
    the durable task input. ``_handle_recovery_disposition`` takes the values
    as arguments from ``ResilientResponseInput`` and the request.
    """

    def _orch(self) -> ResilientResponseOrchestrator:
        orch = ResilientResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=MagicMock(),
            options=MagicMock(steerable_conversations=False, default_fetch_history_count=100),
        )
        orch._persist_crash_failed = AsyncMock()  # type: ignore[method-assign]
        return orch

    @pytest.mark.asyncio
    async def test_mark_failed_recovery_dispatches_from_input_disposition(self) -> None:
        orch = self._orch()
        handled = await orch._handle_recovery_disposition(
            disposition="mark-failed",
            is_recovery=True,
            response_id="resp_mf",
            params={"response_id": "resp_mf"},
            background=True,
        )
        assert handled is True
        orch._persist_crash_failed.assert_awaited_once()
        assert orch._persist_crash_failed.call_args[0][0] == "resp_mf"

    @pytest.mark.asyncio
    async def test_reinvoke_recovery_does_not_mark_failed(self) -> None:
        orch = self._orch()
        handled = await orch._handle_recovery_disposition(
            disposition="re-invoke",
            is_recovery=True,
            response_id="resp_ri",
            params={"response_id": "resp_ri"},
            background=True,
        )
        assert handled is False
        orch._persist_crash_failed.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_non_background_recovery_marks_failed_from_request_flag(self) -> None:
        """A recovered foreground (background=False) response is marked failed
        without re-invoking — driven purely by the request-derived flag."""
        orch = self._orch()
        handled = await orch._handle_recovery_disposition(
            disposition="re-invoke",
            is_recovery=True,
            response_id="resp_fg",
            params={"response_id": "resp_fg"},
            background=False,
        )
        assert handled is True
        orch._persist_crash_failed.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_fresh_entry_never_marks_failed(self) -> None:
        orch = self._orch()
        for disposition in ("re-invoke", "mark-failed"):
            orch._persist_crash_failed.reset_mock()
            handled = await orch._handle_recovery_disposition(
                disposition=disposition,
                is_recovery=False,
                response_id="resp_fresh",
                params={"response_id": "resp_fresh"},
                background=True,
            )
            assert handled is False
            orch._persist_crash_failed.assert_not_awaited()

    def test_no_responses_namespace_symbols_remain(self) -> None:
        """The ``_responses`` framework namespace and its mirror helpers are
        fully removed (single source of truth = task input)."""
        import azure.ai.agentserver.responses.hosting._resilient_orchestrator as mod

        assert not hasattr(mod, "_RESPONSES_NS")
        assert not hasattr(mod, "_RESP_DISPOSITION")
        assert not hasattr(mod, "_RESP_BACKGROUND")
        assert not hasattr(mod, "_RESP_RESPONSE_ID")
        assert not hasattr(mod, "_read_disposition")


class TestPersistCrashFailedRecovery:
    """``_persist_crash_failed`` runs on cross-process recovery of a
    ``mark-failed`` task. Regression for two bugs that combined to leave a
    Foundry-backed, isolation-partitioned response with no client-visible
    terminal after a crash-before-terminal:

    1. The update-not-found fallback only caught ``KeyError``, but the Foundry
       store raises ``FoundryResourceNotFoundError`` — so ``create_response``
       (which actually lands the failed terminal) was never attempted.
    2. ``isolation`` was read from the runtime-only ``_context_ref`` (stripped
       from the persisted input, hence always ``None`` on recovery), so the
       marker was written to the default partition the client never queries.
    """

    @pytest.mark.asyncio
    async def test_foundry_notfound_falls_back_to_create_with_persisted_isolation(self) -> None:
        from unittest.mock import AsyncMock, MagicMock

        from azure.ai.agentserver.responses.store._foundry_errors import (
            FoundryResourceNotFoundError,
        )

        provider = MagicMock()
        # Foundry raises FoundryResourceNotFoundError (NOT KeyError) for missing.
        provider.get_response = AsyncMock(side_effect=FoundryResourceNotFoundError("nf"))
        provider.update_response = AsyncMock(side_effect=FoundryResourceNotFoundError("nf"))
        provider.create_response = AsyncMock()

        orch = ResilientResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=provider,
            options=MagicMock(steerable_conversations=False),
        )

        params = {
            # Persisted isolation keys (what _start_resilient_background stamps).
            "user_id_key": "user-123",
            # No "_context_ref": it is stripped from the resilient input, so the
            # old code's isolation derivation always yielded None here.
        }

        await orch._persist_crash_failed("caresp_x", params)

        # Bug 1: the create fallback MUST run despite Foundry raising
        # FoundryResourceNotFoundError (not KeyError) on update.
        provider.create_response.assert_awaited_once()

        # Bug 2: every store call must target the client's partition built from
        # the persisted user_id_key.
        create_iso = provider.create_response.call_args.kwargs["context"]
        assert create_iso.user_id_key == "user-123"
        assert create_iso.call_id is None
        get_iso = provider.get_response.call_args.kwargs["context"]
        assert get_iso.user_id_key == "user-123"
        assert get_iso.call_id is None

    @pytest.mark.asyncio
    async def test_crash_failed_preserves_persisted_snapshot(self) -> None:
        """The crash-failed marker MUST preserve the developer's persisted
        response object — overlaying only ``status`` + ``error`` — rather than
        writing a synthetic minimal object.

        Regression (two coupled defects): the crash-failure payload was
        synthesized from scratch with ``output=[]`` and NO ``agent_reference``.
        (1) Discarding the persisted snapshot threw away the developer's
        durably-persisted progress (output items) and response fields. (2) The
        Foundry storage API validates that every write carries an
        ``agent_reference`` with both ``name`` and ``version`` and rejects the
        write when it is missing — so the failed terminal never persisted and
        the response stayed ``in_progress`` forever (Path B / mark-failed
        recovery). Preserving the snapshot fixes both: agent_reference/model/
        output all carry through, and only the terminal status + error are
        overlaid.
        """
        from unittest.mock import AsyncMock, MagicMock

        from azure.ai.agentserver.responses.models._generated import ResponseObject

        persisted = ResponseObject(
            {
                "id": "caresp_x",
                "object": "response",
                "status": "in_progress",
                "agent_reference": {"type": "agent_reference", "name": "my-agent", "version": "7"},
                "model": "gpt-5.4-nano",
                "output": [{"type": "message", "id": "msg_1", "role": "assistant"}],
            }
        )

        provider = MagicMock()
        provider.get_response = AsyncMock(return_value=persisted)
        provider.update_response = AsyncMock()
        provider.create_response = AsyncMock()

        orch = ResilientResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=provider,
            options=MagicMock(steerable_conversations=False),
        )

        params = {"user_id_key": "user-123"}

        await orch._persist_crash_failed("caresp_x", params)

        provider.update_response.assert_awaited_once()
        written = provider.update_response.call_args[0][0]
        payload = written.as_dict() if hasattr(written, "as_dict") else dict(written)

        # Terminal + error overlaid.
        assert payload.get("status") == "failed"
        assert payload["error"]["code"] == "server_error"
        # SOT ResponseError is {code, message} only — no internal
        # ``additionalInfo``/``shutdown_reason`` leaked to the customer.
        assert "additionalInfo" not in payload["error"]
        assert "type" not in payload["error"]
        # agent_reference preserved (satisfies the store's mandatory field).
        assert payload["agent_reference"]["name"] == "my-agent"
        assert payload["agent_reference"]["version"] == "7"
        # Progress + developer fields preserved, NOT discarded.
        assert payload.get("model") == "gpt-5.4-nano"
        assert payload.get("output") == [{"type": "message", "id": "msg_1", "role": "assistant"}]

    @pytest.mark.asyncio
    async def test_crash_failed_synthesizes_agent_reference_when_never_persisted(self) -> None:
        """When no response was ever persisted (handler crashed before
        ``response.created``), the synthesized minimal ``failed`` object MUST
        still carry ``agent_reference`` + ``model`` from the persisted task
        input so the write satisfies the store's agent-reference requirement.
        Output is legitimately empty (no progress existed).
        """
        from unittest.mock import AsyncMock, MagicMock

        provider = MagicMock()
        provider.get_response = AsyncMock(side_effect=KeyError("missing"))
        provider.update_response = AsyncMock()
        provider.create_response = AsyncMock()

        orch = ResilientResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=provider,
            options=MagicMock(steerable_conversations=False),
        )

        params = {
            "user_id_key": "user-123",
            "agent_reference": {"type": "agent_reference", "name": "my-agent", "version": "7"},
            "request": {"model": "gpt-5.4-nano"},
        }

        await orch._persist_crash_failed("caresp_x", params)

        provider.update_response.assert_awaited_once()
        written = provider.update_response.call_args[0][0]
        payload = written.as_dict() if hasattr(written, "as_dict") else dict(written)
        assert payload.get("status") == "failed"
        assert payload["agent_reference"]["name"] == "my-agent"
        assert payload["agent_reference"]["version"] == "7"
        assert payload.get("model") == "gpt-5.4-nano"
        assert payload.get("output") == []

    @pytest.mark.asyncio
    async def test_crash_failed_unknown_store_state_never_clobbers(self) -> None:
        """When the snapshot read fails for an *unknown* reason (not a
        confirmed-absent error), a progressed response may still exist in the
        store. The recovery path MUST NOT ``update`` with a minimal
        ``output=[]`` object — that would clobber the progress with empty
        output now that the synthesized marker carries ``agent_reference`` and
        the store would accept the write. It falls back to a best-effort
        ``create`` only (which the store rejects if the response already
        exists, leaving progress intact).
        """
        from unittest.mock import AsyncMock, MagicMock

        provider = MagicMock()
        # Unknown/transient read failure on every attempt (NOT KeyError /
        # FoundryResourceNotFoundError).
        provider.get_response = AsyncMock(side_effect=RuntimeError("store unavailable"))
        provider.update_response = AsyncMock()
        provider.create_response = AsyncMock()

        orch = ResilientResponseOrchestrator(
            create_fn=AsyncMock(),
            provider=provider,
            options=MagicMock(steerable_conversations=False),
        )

        params = {
            "user_id_key": "user-123",
            "agent_reference": {"type": "agent_reference", "name": "my-agent", "version": "7"},
        }

        await orch._persist_crash_failed("caresp_x", params)

        # MUST NOT overwrite (update) — that would clobber any progress.
        provider.update_response.assert_not_awaited()
        # Best-effort create only.
        provider.create_response.assert_awaited_once()
        # The read is retried once before giving up on the unknown error.
        assert provider.get_response.await_count == 2
