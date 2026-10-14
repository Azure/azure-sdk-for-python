# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the ``TaskManagerNotInitialized`` typed exception.

``get_task_manager()`` raises this typed exception (a ``RuntimeError``
subclass) when no manager is installed, letting callers distinguish
"no resilient-task subsystem is available" from a genuine task failure
without probing global state.
"""

import asyncio

import pytest

from azure.ai.agentserver.core.tasks import TaskManagerNotInitialized
from azure.ai.agentserver.core.tasks._manager import (
    TaskManager,
    get_task_manager,
    set_task_manager,
)
from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider


def _config_stub():
    """Minimal config object accepted by ``TaskManager``."""
    return type(
        "C",
        (),
        {
            "agent_name": "s035-test-agent",
            "session_id": "s035-test-session",
            "agent_version": "1.0.0",
            "is_hosted": False,
        },
    )()


@pytest.fixture(autouse=True)
def _clear_manager():
    """Ensure each test starts and ends with no installed manager."""
    set_task_manager(None)
    try:
        yield
    finally:
        set_task_manager(None)


def test_get_task_manager_raises_typed_when_absent() -> None:
    """No manager installed → ``TaskManagerNotInitialized`` (not bare RuntimeError)."""
    with pytest.raises(TaskManagerNotInitialized):
        get_task_manager()


def test_typed_exception_is_runtimeerror_subclass() -> None:
    """Backward compatibility: callers catching ``RuntimeError`` still match."""
    assert issubclass(TaskManagerNotInitialized, RuntimeError)
    with pytest.raises(RuntimeError):
        get_task_manager()


def test_get_task_manager_returns_installed_manager(tmp_path) -> None:
    """With a manager installed, ``get_task_manager`` returns it (no raise)."""
    mgr = TaskManager(
        config=_config_stub(),
        provider=LocalFileTaskProvider(base_dir=tmp_path / "tasks"),
        shutdown_event=asyncio.Event(),
    )
    set_task_manager(mgr)
    assert get_task_manager() is mgr
