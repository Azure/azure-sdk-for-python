# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for @task decorator and Task class.

Spec 015 Phase 3 (FR-006): the developer-facing `@task` decorator surface
no longer accepts ``description``, ``store_input``, ``lease_duration_seconds``,
or ``max_pending``. ``stream_handler_factory`` remains supported. ``TaskOptions``
is no longer in the public ``__all__`` (it is an internal implementation
detail; the ``_opts`` attribute is still observable for asserts).
"""

import asyncio

import pytest

from azure.ai.agentserver.core.durable import (
    Task,
    TaskContext,
    task,
)


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

        @task(
            name="full",
            ephemeral=False,
            title="My Title",
            tags={"env": "test"},
            timeout=timedelta(minutes=5),
        )
        async def my_task(ctx: TaskContext[dict]) -> str:
            return ""

        assert my_task.name == "full"
        assert my_task._opts.ephemeral is False
        assert my_task._opts.title == "My Title"
        assert my_task._opts.tags == {"env": "test"}
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

    def test_stream_handler_factory_still_accepted(self) -> None:
        """FR-006: ``stream_handler_factory=`` remains a supported @task kwarg."""
        from azure.ai.agentserver.core.durable import QueueStreamHandler

        @task(stream_handler_factory=lambda task_id: QueueStreamHandler())
        async def my_task(ctx: TaskContext[str]) -> int:
            return 1

        assert my_task._opts.stream_handler_factory is not None

    @pytest.mark.parametrize(
        "kwarg",
        [
            "description",
            "store_input",
            "lease_duration_seconds",
            "max_pending",
        ],
    )
    def test_task_decorator_rejects_retired_args(self, kwarg: str) -> None:
        """FR-006: ``@task`` rejects the four retired decorator options.

        These were removed in Spec 015 Phase 3 because zero developer code
        relied on them; their behavior is now fixed at internal defaults
        (lease=60s, max_pending=10, input is always persisted, description
        is no longer modeled on the public surface).
        """
        with pytest.raises(TypeError):
            task(**{kwarg: 1})  # type: ignore[arg-type]


class TestTaskOptionsMerge:
    """Tests for option merge via ``Task.options()``."""

    def test_options_returns_new_instance(self) -> None:
        """options() returns a new Task, original unchanged."""

        @task(ephemeral=True)
        async def my_task(ctx: TaskContext[str]) -> int:
            return 1

        updated = my_task.options(ephemeral=False)
        assert updated is not my_task
        assert updated._opts.ephemeral is False
        assert my_task._opts.ephemeral is True

    def test_options_merges_tags(self) -> None:
        """options() merges tags with existing ones."""

        @task(tags={"a": "1"})
        async def my_task(ctx: TaskContext[str]) -> int:
            return 1

        updated = my_task.options(tags={"b": "2"})
        assert updated._opts.tags == {"a": "1", "b": "2"}

    def test_options_overrides_title(self) -> None:
        """options() overrides title."""

        @task(title="original")
        async def my_task(ctx: TaskContext[str]) -> int:
            return 1

        updated = my_task.options(title="override")
        assert updated._opts.title == "override"

    def test_default_options(self) -> None:
        """Default TaskOptions has sensible defaults."""

        @task
        async def my_task(ctx: TaskContext[str]) -> int:
            return 1

        opts = my_task._opts
        assert opts.ephemeral is True
        assert opts.tags == {}
        assert opts.timeout is None


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
# Spec 016 US1 — stale_timeout removal from developer surface (T025)
# --------------------------------------------------------------------- #


class TestStaleTimeoutRemoved:
    """Spec 016 FR-001 / US1: ``stale_timeout`` MUST be removed from the
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

    def test_task_options_rejects_stale_timeout(self) -> None:
        """Task.options(stale_timeout=...) raises TypeError (kwarg removed)."""

        @task
        async def my_task(ctx: TaskContext[str]) -> int:
            return 0

        with pytest.raises(TypeError):
            my_task.options(stale_timeout=1.0)  # type: ignore[call-arg]
