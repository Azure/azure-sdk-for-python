# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for @task decorator and Task class.

: the developer-facing `@task` decorator surface
no longer accepts ``description``, ``store_input``, ``lease_duration_seconds``,
or ``max_pending``.  additionally removed ``stream_handler_factory``
(streaming is now handled via ``azure.ai.agentserver.core.streaming.streams``
— see ``test_stream_handler_factory_rejected_post_spec_017`` below).
``TaskOptions`` is no longer in the public ``__all__`` (it is an internal
implementation detail; the ``_opts`` attribute is still observable for asserts).
"""

import asyncio

import pytest

from azure.ai.agentserver.core.tasks import Task, TaskContext, task


class TestSpec037NameRequired:
    """Spec 037 #7 — ``name`` is a required, explicit, stable identity anchor.

    The prior ``name or func.__qualname__`` fallback silently rebound the
    recovery-routing identity whenever the function was renamed or moved, which
    could orphan in-flight tasks. ``name`` is now required at decoration.
    """

    def test_task_parens_without_name_raises(self) -> None:
        with pytest.raises(ValueError, match="name"):

            @task()
            async def my_task(ctx: TaskContext[str]) -> int:  # pragma: no cover
                return 0

    def test_task_whitespace_name_raises(self) -> None:
        with pytest.raises(ValueError, match="name"):

            @task(name="   ")
            async def my_task(ctx: TaskContext[str]) -> int:  # pragma: no cover
                return 0

    def test_task_explicit_name_ok(self) -> None:
        @task(name="explicit")
        async def my_task(ctx: TaskContext[str]) -> int:
            return 0

        assert my_task.name == "explicit"

    def test_multi_turn_without_name_raises(self) -> None:
        from azure.ai.agentserver.core.tasks import multi_turn_task

        with pytest.raises(ValueError, match="name"):

            @multi_turn_task
            async def my_chain(ctx: TaskContext[str]) -> int:  # pragma: no cover
                return 0


class TestSpec037TimeoutCap:
    """Spec 037 #8 — per-turn timeout defaults to 1 day and is a hard 7-day
    ceiling (fail-fast on a larger or negative value; not clamped).
    """

    def test_timeout_above_seven_days_rejected(self) -> None:
        from datetime import timedelta

        with pytest.raises(ValueError, match="timeout"):

            @task(name="t", timeout=timedelta(days=8))
            async def my_task(ctx: TaskContext[str]) -> int:  # pragma: no cover
                return 0

    def test_timeout_negative_rejected(self) -> None:
        from datetime import timedelta

        with pytest.raises(ValueError, match="timeout"):

            @task(name="t", timeout=timedelta(seconds=-1))
            async def my_task(ctx: TaskContext[str]) -> int:  # pragma: no cover
                return 0

    def test_timeout_exactly_seven_days_ok(self) -> None:
        from datetime import timedelta

        @task(name="t", timeout=timedelta(days=7))
        async def my_task(ctx: TaskContext[str]) -> int:
            return 0

        assert my_task._opts.timeout == timedelta(days=7)

    def test_timeout_above_one_day_ok(self) -> None:
        from datetime import timedelta

        @task(name="t", timeout=timedelta(days=2))
        async def my_task(ctx: TaskContext[str]) -> int:
            return 0

        assert my_task._opts.timeout == timedelta(days=2)

    def test_unset_timeout_resolves_to_one_day(self) -> None:
        from datetime import timedelta

        from azure.ai.agentserver.core.tasks._decorator import _resolve_effective_timeout

        assert _resolve_effective_timeout(None) == timedelta(days=1)
        assert _resolve_effective_timeout(timedelta(seconds=30)) == timedelta(seconds=30)


class TestSpec037InputIdValidation:
    """Spec 037 #12 — a caller-supplied ``input_id`` is validated against the
    same charset/length pattern as ``task_id``.
    """

    @pytest.mark.asyncio
    async def test_bad_input_id_rejected(self) -> None:
        @task(name="t")
        async def my_task(ctx: TaskContext[str]) -> int:  # pragma: no cover
            return 0

        with pytest.raises(ValueError, match="input_id"):
            await my_task.start(task_id="t1", input="x", input_id="bad id with spaces")

    @pytest.mark.asyncio
    async def test_valid_input_id_passes_validation(self) -> None:
        # A ``caresp_...``-style id (as the responses layer supplies) satisfies
        # the pattern; validation must not reject it. (No manager wired, so the
        # call proceeds past validation and then fails on the missing manager —
        # a ValueError from validation would fire BEFORE that.)
        @task(name="t")
        async def my_task(ctx: TaskContext[str]) -> int:  # pragma: no cover
            return 0

        with pytest.raises(Exception) as excinfo:
            await my_task.start(task_id="t1", input="x", input_id="caresp_abc-123.def")
        assert "input_id" not in str(excinfo.value)


class TestTaskDecorator:
    """Tests for the @task decorator."""

    def test_bare_decorator(self) -> None:
        """@task without an explicit name is rejected (Spec 037 #7 — name is a
        required, stable recovery/identity anchor; no function-derived fallback).
        """
        with pytest.raises(ValueError, match="name"):

            @task
            async def my_task(ctx: TaskContext[str]) -> int:  # pragma: no cover
                return 42

    def test_decorator_with_name(self) -> None:
        """@task(name=...) sets a custom name."""

        @task(name="custom_name")
        async def my_task(ctx: TaskContext[str]) -> int:
            return 0

        assert my_task.name == "custom_name"

    def test_decorator_with_all_options(self) -> None:
        """All currently-supported decorator options are forwarded to TaskOptions."""
        from datetime import timedelta

        @task(name="full", title="My Title", timeout=timedelta(minutes=5))
        async def my_task(ctx: TaskContext[dict]) -> str:
            return ""

        assert my_task.name == "full"
        assert my_task._opts.ephemeral is True
        assert my_task._opts.title == "My Title"
        assert my_task._opts.timeout == timedelta(minutes=5)

    def test_rejects_sync_function(self) -> None:
        """@task rejects synchronous functions."""
        with pytest.raises(TypeError, match="async function"):

            @task(name="sync-fn")
            def sync_fn(ctx: TaskContext[str]) -> int:
                return 1

    def test_rejects_non_callable(self) -> None:
        """@task(...) rejects non-callable objects."""
        with pytest.raises((TypeError, AttributeError)):
            task(42, name="non-callable")  # type: ignore[arg-type]

    def test_stream_handler_factory_rejected_post_spec_017(self) -> None:
        """: ``stream_handler_factory=`` is REMOVED from
        the @task signature. Passing it raises ``TypeError`` for
        unknown keyword argument. Streaming now lives in the
        ``azure.ai.agentserver.core.streaming`` peer subpackage with
        a registry-based lifecycle model."""

        with pytest.raises(TypeError, match="stream_handler_factory"):

            @task(stream_handler_factory=lambda task_id: None)  # type: ignore[call-arg]
            async def my_task(ctx: TaskContext[str]) -> int:
                return 1

    @pytest.mark.parametrize(
        "kwarg",
        [
            "description",
            "store_input",
            "lease_duration_seconds",
            "max_pending",
            "tags",
        ],
    )
    def test_task_decorator_rejects_retired_args(self, kwarg: str) -> None:
        """: ``@task`` rejects the retired decorator options.

        These were removed because zero developer code relied on them;
        their behavior is now fixed at internal defaults (lease=60s,
        max_pending=10, input is always persisted, description is no
        longer modeled on the public surface, tags is internal-only).
        """
        with pytest.raises(TypeError):
            task(**{kwarg: 1})  # type: ignore[arg-type]


class TestTypeExtraction:
    """Tests for generic type parameter extraction."""

    def test_input_type_str(self) -> None:
        """Extracts str as Input type from TaskContext[str]."""

        @task(name="extract-input-str")
        async def my_task(ctx: TaskContext[str]) -> int:
            return 1

        assert my_task._input_type is str

    def test_input_type_dict(self) -> None:
        """Extracts dict as Input type."""

        @task(name="extract-input-dict")
        async def my_task(ctx: TaskContext[dict]) -> str:
            return ""

        assert my_task._input_type is dict

    def test_output_type_int(self) -> None:
        """Extracts int as Output type from return annotation."""

        @task(name="extract-output-int")
        async def my_task(ctx: TaskContext[str]) -> int:
            return 1

        assert my_task._output_type is int


# --------------------------------------------------------------------- #
#   — stale_timeout removal from developer surface (T025)
# --------------------------------------------------------------------- #


class TestStaleTimeoutRemoved:
    """/: ``stale_timeout`` MUST be removed from the
    developer-facing recovery surface (``@task``, ``Task.options()``,
    ``TaskOptions``, ``TaskContext``). Passing the removed kwarg MUST
    raise ``TypeError``.

    Recovery is now framework-managed; see the developer guide §7
    Testing a recovery path for the new mental model.
    """

    def test_task_decorator_rejects_stale_timeout(self) -> None:
        """@task(stale_timeout=...) raises TypeError (kwarg removed)."""
        with pytest.raises(TypeError):

            @task(stale_timeout=1.0)  # type: ignore[call-arg]
            async def _my_task(ctx: TaskContext[str]) -> int:
                return 0
