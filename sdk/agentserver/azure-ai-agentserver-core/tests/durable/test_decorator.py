# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for @durable_task decorator and DurableTask class."""

import asyncio

import pytest

from azure.ai.agentserver.core.durable import (
    DurableTask,
    DurableTaskOptions,
    TaskContext,
    durable_task,
)


class TestDurableTaskDecorator:
    """Tests for the @durable_task decorator."""

    def test_bare_decorator(self) -> None:
        """@durable_task with no arguments produces a DurableTask."""

        @durable_task
        async def my_task(ctx: TaskContext[str]) -> int:
            return 42

        assert isinstance(my_task, DurableTask)
        # Name includes class/method scope when defined inside a method
        assert "my_task" in my_task.name

    def test_decorator_with_name(self) -> None:
        """@durable_task(name=...) sets a custom name."""

        @durable_task(name="custom_name")
        async def my_task(ctx: TaskContext[str]) -> int:
            return 0

        assert my_task.name == "custom_name"

    def test_decorator_with_all_options(self) -> None:
        """All decorator options are forwarded to DurableTaskOptions."""
        from datetime import timedelta

        @durable_task(
            name="full",
            ephemeral=False,
            lease_duration_seconds=120,
            store_input=True,
            title="My Title",
            tags={"env": "test"},
            timeout=timedelta(minutes=5),
        )
        async def my_task(ctx: TaskContext[dict]) -> str:
            return ""

        assert my_task.name == "full"
        assert my_task._opts.ephemeral is False
        assert my_task._opts.lease_duration_seconds == 120
        assert my_task._opts.store_input is True
        assert my_task._opts.title == "My Title"
        assert my_task._opts.tags == {"env": "test"}
        assert my_task._opts.timeout == timedelta(minutes=5)

    def test_rejects_sync_function(self) -> None:
        """@durable_task rejects synchronous functions."""
        with pytest.raises(TypeError, match="async function"):

            @durable_task
            def sync_fn(ctx: TaskContext[str]) -> int:
                return 1

    def test_rejects_non_callable(self) -> None:
        """@durable_task(...) rejects non-callable objects."""
        with pytest.raises((TypeError, AttributeError)):
            durable_task(42)  # type: ignore[arg-type]


class TestDurableTaskOptions:
    """Tests for DurableTaskOptions merge via .options()."""

    def test_options_returns_new_instance(self) -> None:
        """options() returns a new DurableTask, original unchanged."""

        @durable_task(ephemeral=True)
        async def my_task(ctx: TaskContext[str]) -> int:
            return 1

        updated = my_task.options(ephemeral=False)
        assert updated is not my_task
        assert updated._opts.ephemeral is False
        assert my_task._opts.ephemeral is True

    def test_options_merges_tags(self) -> None:
        """options() merges tags with existing ones."""

        @durable_task(tags={"a": "1"})
        async def my_task(ctx: TaskContext[str]) -> int:
            return 1

        updated = my_task.options(tags={"b": "2"})
        assert updated._opts.tags == {"a": "1", "b": "2"}

    def test_options_overrides_title(self) -> None:
        """options() overrides title."""

        @durable_task(title="original")
        async def my_task(ctx: TaskContext[str]) -> int:
            return 1

        updated = my_task.options(title="override")
        assert updated._opts.title == "override"

    def test_default_options(self) -> None:
        """Default DurableTaskOptions has sensible defaults."""

        @durable_task
        async def my_task(ctx: TaskContext[str]) -> int:
            return 1

        opts = my_task._opts
        assert opts.ephemeral is True
        assert opts.lease_duration_seconds == 60
        assert opts.store_input is True  # default is True
        assert opts.tags == {}
        assert opts.timeout is None


class TestTypeExtraction:
    """Tests for generic type parameter extraction."""

    def test_input_type_str(self) -> None:
        """Extracts str as Input type from TaskContext[str]."""

        @durable_task
        async def my_task(ctx: TaskContext[str]) -> int:
            return 1

        assert my_task._input_type is str

    def test_input_type_dict(self) -> None:
        """Extracts dict as Input type."""

        @durable_task
        async def my_task(ctx: TaskContext[dict]) -> str:
            return ""

        assert my_task._input_type is dict

    def test_output_type_int(self) -> None:
        """Extracts int as Output type from return annotation."""

        @durable_task
        async def my_task(ctx: TaskContext[str]) -> int:
            return 1

        assert my_task._output_type is int
