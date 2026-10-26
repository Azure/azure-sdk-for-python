# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import asyncio
import inspect
import logging

from azure.ai.agentserver.core import (
    AgentSessionContext,
    FoundryAgentRequestContext,
    FoundryOriginalSubject,
    experimental,
)
from azure.ai.agentserver.core._experimental import (
    DISABLE_EXPERIMENTAL_WARNING_ENV_VAR,
    EXPERIMENTAL_CLASS_MESSAGE,
    EXPERIMENTAL_LINK_MESSAGE,
    EXPERIMENTAL_METHOD_MESSAGE,
    _warning_cache,
)
from azure.ai.agentserver.core.tasks import (
    InputTooLarge,
    LastInputIdPreconditionFailed,
    MultiTurnTask,
    RetryPolicy,
    SteeringQueueFull,
    Task,
    TaskCancelled,
    TaskConflictError,
    TaskContext,
    TaskDeferred,
    TaskFailed,
    TaskManagerNotInitialized,
    TaskRun,
    multi_turn_task,
    resilient_tasks_enabled,
    set_resilient_tasks_enabled,
    task,
)


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


def test_resilient_task_public_api_is_not_experimental(caplog) -> None:
    _warning_cache.clear()

    with caplog.at_level(logging.WARNING, logger=experimental.__module__):
        resilient_tasks_enabled()

    public_apis = (
        TaskContext,
        TaskRun,
        Task,
        MultiTurnTask,
        set_resilient_tasks_enabled,
        resilient_tasks_enabled,
        TaskFailed,
        TaskCancelled,
        TaskConflictError,
        TaskManagerNotInitialized,
        SteeringQueueFull,
        LastInputIdPreconditionFailed,
        InputTooLarge,
        TaskDeferred,
        RetryPolicy,
    )
    for public_api in public_apis:
        assert not (public_api.__doc__ or "").startswith(".. note::")
        assert not hasattr(public_api, "_azure_agentserver_experimental_cache_key")
        assert not hasattr(public_api, "_azure_agentserver_experimental_message")

    assert len(caplog.records) == 0


def test_resilient_task_decorator_factories_are_not_experimental(caplog) -> None:
    _warning_cache.clear()

    with caplog.at_level(logging.WARNING, logger=experimental.__module__):
        task(name="test-task")
        multi_turn_task(name="test-multi-turn-task")

    assert not (task.__doc__ or "").startswith(".. note::")
    assert not (multi_turn_task.__doc__ or "").startswith(".. note::")
    assert len(caplog.records) == 0


def test_agent_session_context_is_experimental(caplog) -> None:
    _warning_cache.clear()

    with caplog.at_level(logging.WARNING, logger=experimental.__module__):
        AgentSessionContext("session", "restore")

    assert AgentSessionContext.__doc__.startswith(".. note::")
    assert EXPERIMENTAL_CLASS_MESSAGE in AgentSessionContext.__doc__
    assert len(caplog.records) == 1


def test_original_subject_is_experimental(caplog) -> None:
    _warning_cache.clear()

    with caplog.at_level(logging.WARNING, logger=experimental.__module__):
        subject = FoundryOriginalSubject(oid="subject", tid="tenant", idtype="user")

    assert (subject.oid, subject.tid, subject.idtype) == ("subject", "tenant", "user")
    assert FoundryOriginalSubject.__doc__.startswith(".. note::")
    assert EXPERIMENTAL_CLASS_MESSAGE in FoundryOriginalSubject.__doc__
    assert EXPERIMENTAL_LINK_MESSAGE in FoundryOriginalSubject.__doc__
    assert len(caplog.records) == 1
    assert "FoundryOriginalSubject" in caplog.records[0].message
    assert EXPERIMENTAL_CLASS_MESSAGE in caplog.records[0].message


def test_model_attribution_headers_is_experimental(caplog) -> None:
    _warning_cache.clear()

    with caplog.at_level(logging.WARNING, logger=experimental.__module__):
        context = FoundryAgentRequestContext()
        assert context.model_attribution_headers() == {}

    method = FoundryAgentRequestContext.model_attribution_headers
    assert method.__doc__.startswith(".. note::")
    assert EXPERIMENTAL_METHOD_MESSAGE in method.__doc__
    assert EXPERIMENTAL_LINK_MESSAGE in method.__doc__
    assert len(caplog.records) == 1
    assert "FoundryAgentRequestContext.model_attribution_headers" in caplog.records[0].message
    assert EXPERIMENTAL_METHOD_MESSAGE in caplog.records[0].message
