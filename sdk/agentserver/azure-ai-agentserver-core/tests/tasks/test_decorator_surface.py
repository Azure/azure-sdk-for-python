# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""RED-first tests for  resilient decorator public surface.

Covers,,,,,,,,
SC-016, and SC-018.
"""

from __future__ import annotations

import inspect
from dataclasses import is_dataclass
from pathlib import Path
from uuid import UUID

import pytest

# Defer multi_turn_task / MultiTurnTask import: these symbols are part of
# 's public surface and don't exist yet (RED until Phase 2-5).
try:
    from azure.ai.agentserver.core.tasks import task, multi_turn_task, Task, MultiTurnTask, RetryPolicy, TaskContext

    _NEW_SURFACE_AVAILABLE = True
except ImportError:
    _NEW_SURFACE_AVAILABLE = False
    from azure.ai.agentserver.core.tasks import task, Task, RetryPolicy, TaskContext

    multi_turn_task = None  # type: ignore[assignment]
    MultiTurnTask = None  # type: ignore[assignment]

pytestmark = pytest.mark.skipif(
    not _NEW_SURFACE_AVAILABLE, reason=": requires `multi_turn_task` / `MultiTurnTask` (RED until Phase 2)"
)


async def _setup_manager(tmp_path: Path):
    from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
    from azure.ai.agentserver.core.tasks._manager import TaskManager

    import azure.ai.agentserver.core.tasks._manager as mgr_mod

    provider = LocalFileTaskProvider(Path(str(tmp_path)))
    config = type(
        "C",
        (),
        {
            "agent_name": "test-agent",
            "session_id": "test-session",
            "agent_version": "1.0.0",
            "is_hosted": False,
        },
    )()
    manager = TaskManager(config=config, provider=provider)
    mgr_mod._manager = manager
    await manager.startup()
    return manager, mgr_mod


async def _teardown_manager(manager, mgr_mod) -> None:
    await manager.shutdown()
    mgr_mod._manager = None


class TestDecoratorSignatures:
    """/  — decorator signatures, kwarg matrix, title-static-only, class split."""

    def test_task_returns_Task_class(self) -> None:
        """@task returns Task[I, O], not MultiTurnTask."""

        @task(name="surface-one-shot")
        async def fn(ctx: TaskContext[int]) -> int:
            return ctx.input

        assert isinstance(fn, Task)
        assert not isinstance(fn, MultiTurnTask)

    def test_multi_turn_task_returns_MultiTurnTask_class(self) -> None:
        """@multi_turn_task returns MultiTurnTask[I, O], not Task."""

        @multi_turn_task(name="surface-multi-turn")
        async def fn(ctx: TaskContext[int]) -> int:
            return ctx.input

        assert isinstance(fn, MultiTurnTask)
        assert not isinstance(fn, Task)

    def test_task_rejects_steerable_kwarg(self) -> None:
        """@task rejects steerable= at decoration time."""
        with pytest.raises(TypeError):

            @task(name="surface-task-steerable", steerable=True)  # type: ignore[call-arg]
            async def fn(ctx: TaskContext[int]) -> int:
                return ctx.input

    def test_task_rejects_ephemeral_kwarg(self) -> None:
        """@task rejects ephemeral= at decoration time."""
        with pytest.raises(TypeError):

            @task(name="surface-task-ephemeral", ephemeral=False)  # type: ignore[call-arg]
            async def fn(ctx: TaskContext[int]) -> int:
                return ctx.input

    def test_task_rejects_tags_kwarg(self) -> None:
        """@task rejects tags= at decoration time."""
        with pytest.raises(TypeError):

            @task(name="surface-task-tags", tags=["a"])  # type: ignore[call-arg]
            async def fn(ctx: TaskContext[int]) -> int:
                return ctx.input

    def test_multi_turn_task_rejects_ephemeral_kwarg(self) -> None:
        """@multi_turn_task rejects ephemeral= at decoration time."""
        with pytest.raises(TypeError):

            @multi_turn_task(name="surface-multi-ephemeral", ephemeral=False)  # type: ignore[call-arg]
            async def fn(ctx: TaskContext[int]) -> int:
                return ctx.input

    def test_multi_turn_task_rejects_tags_kwarg(self) -> None:
        """@multi_turn_task rejects tags= at decoration time."""
        with pytest.raises(TypeError):

            @multi_turn_task(name="surface-multi-tags", tags=["a"])  # type: ignore[call-arg]
            async def fn(ctx: TaskContext[int]) -> int:
                return ctx.input

    def test_multi_turn_task_accepts_steerable(self) -> None:
        """@multi_turn_task accepts steerable=."""

        @multi_turn_task(name="surface-multi-steerable", steerable=True)
        async def fn(ctx: TaskContext[int]) -> int:
            return ctx.input

        assert isinstance(fn, MultiTurnTask)

    def test_title_static_string_accepted(self) -> None:
        """Static title strings are accepted by both decorators."""

        @task(name="surface-title-task", title="My Task")
        async def one_shot(ctx: TaskContext[int]) -> int:
            return ctx.input

        @multi_turn_task(name="surface-title-multi", title="My Task")
        async def multi(ctx: TaskContext[int]) -> int:
            return ctx.input

        assert isinstance(one_shot, Task)
        assert isinstance(multi, MultiTurnTask)

    def test_title_None_default(self) -> None:
        """title=None remains the default for both decorators."""

        @task(name="surface-title-none-task", title=None)
        async def one_shot(ctx: TaskContext[int]) -> int:
            return ctx.input

        @multi_turn_task(name="surface-title-none-multi", title=None)
        async def multi(ctx: TaskContext[int]) -> int:
            return ctx.input

        assert isinstance(one_shot, Task)
        assert isinstance(multi, MultiTurnTask)

    def test_title_callable_rejected(self) -> None:
        """Callable title factories are rejected at decoration time."""
        with pytest.raises(TypeError):

            @task(name="surface-title-callable-task", title=lambda _input, _task_id: "x")  # type: ignore[call-arg]
            async def one_shot(ctx: TaskContext[int]) -> int:
                return ctx.input

        with pytest.raises(TypeError):

            @multi_turn_task(name="surface-title-callable-multi", title=lambda _input, _task_id: "x")  # type: ignore[call-arg]
            async def multi(ctx: TaskContext[int]) -> int:
                return ctx.input

    def test_title_non_string_non_None_rejected(self) -> None:
        """Non-string, non-None titles are rejected at decoration time."""
        for invalid_title in (42, ["a"]):
            with pytest.raises(TypeError):

                @task(name="surface-title-invalid-task", title=invalid_title)  # type: ignore[arg-type]
                async def one_shot(ctx: TaskContext[int]) -> int:
                    return ctx.input

            with pytest.raises(TypeError):

                @multi_turn_task(name="surface-title-invalid-multi", title=invalid_title)  # type: ignore[arg-type]
                async def multi(ctx: TaskContext[int]) -> int:
                    return ctx.input


class TestHandlerSignatureValidation:
    """— handler signature validation at decoration time."""

    def test_sync_handler_rejected(self) -> None:
        """Decorators require async def handlers."""
        with pytest.raises(TypeError, match="async def"):

            @task(name="surface-sync-handler")
            def fn(ctx: TaskContext[int]) -> int:
                return ctx.input

    def test_handler_missing_ctx_arg_rejected(self) -> None:
        """Handlers must accept a ctx argument."""
        with pytest.raises(TypeError):

            @task(name="surface-missing-ctx")
            async def fn() -> int:
                return 0

    def test_handler_wrong_first_arg_name_rejected(self) -> None:
        """Handlers must use ctx as the first argument."""
        with pytest.raises(TypeError, match="ctx|first"):

            @task(name="surface-wrong-first-arg")
            async def fn(self: TaskContext[int]) -> int:
                return self.input

    def test_handler_with_correct_signature_accepted(self) -> None:
        """async def fn(ctx: TaskContext[I]) -> O succeeds."""

        @task(name="surface-correct-signature")
        async def fn(ctx: TaskContext[int]) -> int:
            return 0

        assert isinstance(fn, Task)


class TestIdentifierSupply:
    """/  — identifier supply rules + if_last_input_id kwarg acceptance."""

    @pytest.mark.asyncio
    async def test_one_shot_auto_gen_task_id(self, tmp_path: Path) -> None:
        """One-shot .start(input=...) auto-generates a GUID task_id and 1:1 input_id."""

        @task(name="surface-auto-task-id")
        async def task_fn(ctx: TaskContext[int]) -> int:
            return ctx.input

        manager, mgr_mod = await _setup_manager(tmp_path)
        try:
            run = await task_fn.start(input=1)
            UUID(run.task_id)
            assert run.input_id == run.task_id
            await run.result()
        finally:
            await _teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_one_shot_explicit_task_id(self, tmp_path: Path) -> None:
        """One-shot .start(input=..., task_id='t1') uses the supplied id."""

        @task(name="surface-explicit-task-id")
        async def task_fn(ctx: TaskContext[str]) -> str:
            return ctx.input

        manager, mgr_mod = await _setup_manager(tmp_path)
        try:
            run = await task_fn.start(input="payload", task_id="t1")
            #: exception.task_id removed
            assert run.input_id == "t1"
            await run.result()
        finally:
            await _teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_multi_turn_requires_task_id(self) -> None:
        """Multi-turn .start(input=...) rejects missing task_id."""

        @multi_turn_task(name="surface-multi-requires-task-id")
        async def task_fn(ctx: TaskContext[str]) -> str:
            return ctx.input

        with pytest.raises(TypeError):
            await task_fn.start(input="payload")

    @pytest.mark.asyncio
    async def test_if_last_input_id_kwarg_accepted_one_shot(self, tmp_path: Path) -> None:
        """One-shot .start accepts if_last_input_id=None."""

        @task(name="surface-one-shot-if-last-input-id")
        async def task_fn(ctx: TaskContext[str]) -> str:
            return ctx.input

        manager, mgr_mod = await _setup_manager(tmp_path)
        try:
            run = await task_fn.start(input="payload", task_id="precondition-one-shot", if_last_input_id=None)
            #: exception.task_id removed
            await run.result()
        finally:
            await _teardown_manager(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_if_last_input_id_kwarg_accepted_multi_turn(self, tmp_path: Path) -> None:
        """Multi-turn .start accepts if_last_input_id=None."""

        @multi_turn_task(name="surface-multi-if-last-input-id")
        async def task_fn(ctx: TaskContext[str]) -> str:
            return ctx.input

        manager, mgr_mod = await _setup_manager(tmp_path)
        try:
            run = await task_fn.start(task_id="chain-1", input="payload", if_last_input_id=None)
            #: exception.task_id removed
            await run.result()
        finally:
            await _teardown_manager(manager, mgr_mod)


class TestClassSplitTypeSafety:
    """+ SC-016 — Task and MultiTurnTask are distinct public classes."""

    def test_Task_and_MultiTurnTask_distinct_classes(self) -> None:
        """Task and MultiTurnTask are not aliases or subclasses."""
        assert Task is not MultiTurnTask
        assert not issubclass(Task, MultiTurnTask)
        assert not issubclass(MultiTurnTask, Task)

    def test_MultiTurnTask_has_delete_classmethod(self) -> None:
        """MultiTurnTask exposes delete; one-shot Task does not."""
        assert hasattr(MultiTurnTask, "delete")
        assert callable(getattr(MultiTurnTask, "delete"))

    def test_Task_does_not_have_delete(self) -> None:
        """Task has no delete surface."""
        assert not hasattr(Task, "delete")

    def test_multi_turn_get_active_run_signature(self) -> None:
        """MultiTurnTask.get_active_run requires task_id and input_id."""
        params = inspect.signature(MultiTurnTask.get_active_run).parameters

        assert "task_id" in params
        assert "input_id" in params

    def test_one_shot_get_active_run_signature(self) -> None:
        """Task.get_active_run accepts task_id only."""
        params = inspect.signature(Task.get_active_run).parameters

        assert "task_id" in params
        assert "input_id" not in params

    def test_both_classes_exported(self) -> None:
        """Task and MultiTurnTask are exported from resilient.__all__."""
        import azure.ai.agentserver.core.tasks as resilient

        assert "Task" in resilient.__all__
        assert "MultiTurnTask" in resilient.__all__


class TestRetryPolicyShape:
    """— RetryPolicy is regular class with __slots__ + correct field names."""

    def test_RetryPolicy_uses_slots(self) -> None:
        """RetryPolicy uses __slots__ and is not a dataclass."""
        assert hasattr(RetryPolicy, "__slots__")
        assert RetryPolicy.__slots__
        assert not is_dataclass(RetryPolicy)

    def test_RetryPolicy_field_names(self) -> None:
        """RetryPolicy constructor and public attrs use  field names."""
        policy = RetryPolicy(
            max_attempts=3, initial_delay=1.0, max_delay=10.0, backoff_coefficient=2.0, jitter=0.1, retry_on=None
        )

        assert policy.max_attempts == 3
        assert policy.initial_delay == 1.0
        assert policy.max_delay == 10.0
        assert policy.backoff_coefficient == 2.0
        assert policy.jitter == 0.1
        assert policy.retry_on is None

        policy.max_attempts = 4
        policy.initial_delay = 2.0
        policy.max_delay = 20.0
        policy.backoff_coefficient = 1.5
        policy.jitter = 0.2
        policy.retry_on = ValueError

        assert policy.max_attempts == 4
        assert policy.initial_delay == 2.0
        assert policy.max_delay == 20.0
        assert policy.backoff_coefficient == 1.5
        assert policy.jitter == 0.2
        assert policy.retry_on == (ValueError)

    def test_RetryPolicy_preset_factories(self) -> None:
        """Preset factories are module-level callables with explicit signatures."""
        from azure.ai.agentserver.core.tasks._retry import exponential_backoff, fixed_delay, linear_backoff, no_retry

        for factory in (exponential_backoff, fixed_delay, linear_backoff, no_retry):
            signature = inspect.signature(factory)
            for parameter in signature.parameters.values():
                assert parameter.kind is not inspect.Parameter.VAR_POSITIONAL
                assert parameter.kind is not inspect.Parameter.VAR_KEYWORD
                assert parameter.default is not Ellipsis
            assert isinstance(factory(), RetryPolicy)
