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

from azure.ai.agentserver.core.durable import Task, TaskContext, task


class TestTaskDecorator:
    """Tests for the @task decorator."""

    def test_bare_decorator(self) -> None:
        """@task with no arguments produces a Task."""

        @task
        async def my_task(ctx: TaskContext[str]) -> int:
            return 42

        assert isinstance(my_task, Task)
        # Name includes class/method scope when defined inside a method
        assert "my_task" in my_task.name

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

            @task
            def sync_fn(ctx: TaskContext[str]) -> int:
                return 1

    def test_rejects_non_callable(self) -> None:
        """@task(...) rejects non-callable objects."""
        with pytest.raises((TypeError, AttributeError)):
            task(42)  # type: ignore[arg-type]

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

        @task
        async def my_task(ctx: TaskContext[str]) -> int:
            return 1

        assert my_task._input_type is str

    def test_input_type_dict(self) -> None:
        """Extracts dict as Input type."""

        @task
        async def my_task(ctx: TaskContext[dict]) -> str:
            return ""

        assert my_task._input_type is dict

    def test_output_type_int(self) -> None:
        """Extracts int as Output type from return annotation."""

        @task
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
