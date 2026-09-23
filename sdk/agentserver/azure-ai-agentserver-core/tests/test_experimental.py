# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import asyncio
import inspect
import logging

import pytest

from azure.ai.agentserver.core import experimental
from azure.ai.agentserver.core._experimental import (
    DISABLE_EXPERIMENTAL_WARNING_ENV_VAR,
    EXPERIMENTAL_CLASS_MESSAGE,
    EXPERIMENTAL_LINK_MESSAGE,
    EXPERIMENTAL_METHOD_MESSAGE,
    _warning_cache,
)
from azure.ai.agentserver.core.tasks import multi_turn_task, resilient_tasks_enabled, task


@experimental
class ExperimentalClass:
    """A test class."""

    def __init__(self) -> None:
        self.value = 1


@experimental
def experimental_function() -> bool:
    """A test function."""
    return True


@experimental
async def experimental_async_function() -> bool:
    """A test coroutine function."""
    return True


@experimental
def outer_experimental_function() -> bool:
    """A sync experimental function that calls another experimental function."""
    return experimental_function()


@experimental
async def outer_experimental_async_function() -> bool:
    """An async experimental function that awaits another experimental coroutine function."""
    return await experimental_async_function()


@experimental
def scheduling_experimental_function() -> "asyncio.Task[bool]":
    """A sync experimental function that spawns a task running another experimental
    coroutine function, mirroring schedule_flush_spans -> _coalesced_flush -> flush_spans_async."""
    return asyncio.get_running_loop().create_task(experimental_async_function())


def _duplicate_init(self) -> None:
    self.value = 1


ExperimentalDuplicateA = experimental(
    type("ExperimentalDuplicate", (), {"__module__": "test.module_a", "__init__": _duplicate_init})
)
ExperimentalDuplicateB = experimental(
    type("ExperimentalDuplicate", (), {"__module__": "test.module_b", "__init__": _duplicate_init})
)


@experimental
class ExperimentalBase:
    """A test base class."""

    def __init__(self) -> None:
        self.value = 1


@experimental
class ExperimentalChild(ExperimentalBase):
    """A test child class."""


def test_experimental_decorator_on_class(caplog) -> None:
    _warning_cache.clear()

    with caplog.at_level(logging.WARNING, logger=experimental.__module__):
        ExperimentalClass()

    assert ExperimentalClass.__doc__.startswith(".. note::")
    assert EXPERIMENTAL_CLASS_MESSAGE in ExperimentalClass.__doc__
    assert EXPERIMENTAL_LINK_MESSAGE in ExperimentalClass.__doc__
    assert len(caplog.records) == 1
    assert EXPERIMENTAL_CLASS_MESSAGE in caplog.records[0].message


def test_experimental_decorator_on_function(caplog) -> None:
    _warning_cache.clear()

    with caplog.at_level(logging.WARNING, logger=experimental.__module__):
        assert experimental_function() is True

    assert experimental_function.__doc__.startswith(".. note::")
    assert EXPERIMENTAL_METHOD_MESSAGE in experimental_function.__doc__
    assert EXPERIMENTAL_LINK_MESSAGE in experimental_function.__doc__
    assert len(caplog.records) == 1
    assert EXPERIMENTAL_METHOD_MESSAGE in caplog.records[0].message


def test_experimental_decorator_on_async_function_preserves_coroutine_introspection(caplog) -> None:
    _warning_cache.clear()

    assert inspect.iscoroutinefunction(experimental_async_function)
    assert asyncio.iscoroutinefunction(experimental_async_function)

    with caplog.at_level(logging.WARNING, logger=experimental.__module__):
        assert asyncio.run(experimental_async_function()) is True

    assert experimental_async_function.__doc__.startswith(".. note::")
    assert EXPERIMENTAL_METHOD_MESSAGE in experimental_async_function.__doc__
    assert EXPERIMENTAL_LINK_MESSAGE in experimental_async_function.__doc__
    assert len(caplog.records) == 1
    assert EXPERIMENTAL_METHOD_MESSAGE in caplog.records[0].message


def test_experimental_decorator_no_duplicate_warnings(caplog) -> None:
    _warning_cache.clear()

    with caplog.at_level(logging.WARNING, logger=experimental.__module__):
        experimental_function()
        experimental_function()

    assert len(caplog.records) == 1


def test_experimental_decorator_suppresses_nested_sync_call_warning(caplog) -> None:
    """A sync experimental function calling another experimental function directly
    must only warn once, for the outermost call."""
    _warning_cache.clear()

    with caplog.at_level(logging.WARNING, logger=experimental.__module__):
        assert outer_experimental_function() is True

    assert len(caplog.records) == 1
    assert "outer_experimental_function" in caplog.records[0].message


def test_experimental_decorator_suppresses_nested_async_call_warning(caplog) -> None:
    """An async experimental function awaiting another experimental coroutine
    function must only warn once, for the outermost call."""
    _warning_cache.clear()

    with caplog.at_level(logging.WARNING, logger=experimental.__module__):
        assert asyncio.run(outer_experimental_async_function()) is True

    assert len(caplog.records) == 1
    assert "outer_experimental_async_function" in caplog.records[0].message


@pytest.mark.asyncio
async def test_experimental_decorator_suppresses_warning_in_spawned_task(caplog) -> None:
    """A sync experimental function that spawns a task running another experimental
    coroutine function must only warn once. asyncio.Task copies the active context
    at creation, so the re-entrancy guard set before create_task() still applies
    inside the task even after the outer call returns."""
    _warning_cache.clear()

    with caplog.at_level(logging.WARNING, logger=experimental.__module__):
        task = scheduling_experimental_function()
        assert await task is True

    assert len(caplog.records) == 1
    assert "scheduling_experimental_function" in caplog.records[0].message


def test_experimental_decorator_uses_qualified_cache_keys(caplog) -> None:
    _warning_cache.clear()

    with caplog.at_level(logging.WARNING, logger=experimental.__module__):
        ExperimentalDuplicateA()
        ExperimentalDuplicateB()

    assert len(caplog.records) == 2
    assert "test.module_a.ExperimentalDuplicate" in caplog.records[0].message
    assert "test.module_b.ExperimentalDuplicate" in caplog.records[1].message


def test_experimental_decorator_only_warns_for_outermost_class(caplog) -> None:
    _warning_cache.clear()

    with caplog.at_level(logging.WARNING, logger=experimental.__module__):
        ExperimentalChild()

    assert len(caplog.records) == 1
    assert "ExperimentalChild" in caplog.records[0].message
    assert "ExperimentalBase" not in caplog.records[0].message


def test_experimental_decorator_env_var_suppresses_warning(monkeypatch, caplog) -> None:
    _warning_cache.clear()
    monkeypatch.setenv(DISABLE_EXPERIMENTAL_WARNING_ENV_VAR, "true")

    with caplog.at_level(logging.WARNING, logger=experimental.__module__):
        experimental_function()

    assert len(caplog.records) == 0


def test_resilient_task_public_api_is_experimental(caplog) -> None:
    _warning_cache.clear()

    with caplog.at_level(logging.WARNING, logger=experimental.__module__):
        resilient_tasks_enabled()

    assert resilient_tasks_enabled.__doc__.startswith(".. note::")
    assert EXPERIMENTAL_METHOD_MESSAGE in resilient_tasks_enabled.__doc__
    assert len(caplog.records) == 1


def test_resilient_task_decorator_factories_are_experimental(caplog) -> None:
    _warning_cache.clear()

    with caplog.at_level(logging.WARNING, logger=experimental.__module__):
        task(name="test-task")
        multi_turn_task(name="test-multi-turn-task")

    assert task.__doc__.startswith(".. note::")
    assert multi_turn_task.__doc__.startswith(".. note::")
    assert len(caplog.records) == 2
