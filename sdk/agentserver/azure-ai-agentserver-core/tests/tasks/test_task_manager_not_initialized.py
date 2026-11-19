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

from azure.ai.agentserver.core.tasks import TaskContext, TaskManagerNotInitialized
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


def test_scoped_manager_masks_other_host_and_receives_late_registration(tmp_path) -> None:
    from azure.ai.agentserver.core.tasks import task
    from azure.ai.agentserver.core.tasks._manager import _task_manager_scope

    first = TaskManager(config=_config_stub(), provider=LocalFileTaskProvider(tmp_path / "first"))
    second = TaskManager(config=_config_stub(), provider=LocalFileTaskProvider(tmp_path / "second"))
    set_task_manager(second)
    with _task_manager_scope(lambda: first):
        assert get_task_manager() is first

        @task(name="scoped_late_registration")
        async def late(ctx: TaskContext[dict]) -> dict:
            return ctx.input

        assert first._resume_callbacks[late.name] is late._fn
        assert late.name not in second._resume_callbacks
        with _task_manager_scope(lambda: None):
            with pytest.raises(TaskManagerNotInitialized):
                get_task_manager()
        assert get_task_manager() is first
    assert get_task_manager() is second


@pytest.mark.parametrize("explicit_registration", [False, True])
@pytest.mark.asyncio
async def test_startup_preserves_explicit_callbacks_over_imported_descriptors(
    tmp_path, monkeypatch: pytest.MonkeyPatch, explicit_registration: bool
) -> None:
    from azure.ai.agentserver.core.tasks import _decorator, task

    monkeypatch.setattr(_decorator, "_REGISTERED_DESCRIPTORS", [])

    @task(name="startup_callback_owner")
    async def owned(ctx: TaskContext[str]) -> str:
        return "owned"

    @task(name="startup_callback_owner")
    async def later_import(ctx: TaskContext[str]) -> str:
        return "later import"

    manager = TaskManager(config=_config_stub(), provider=LocalFileTaskProvider(tmp_path / "tasks"))
    if explicit_registration:
        manager.register_resume_callback(owned.name, owned._fn, owned._opts)
    await manager.startup()
    try:
        expected = owned if explicit_registration else later_import
        assert manager._resume_callbacks[expected.name] is expected._fn
        assert manager._resume_opts[expected.name] is expected._opts
    finally:
        await manager.shutdown()


@pytest.mark.parametrize("explicit_registration", [False, True])
@pytest.mark.asyncio
async def test_host_bound_callbacks_require_explicit_registration(
    tmp_path, monkeypatch: pytest.MonkeyPatch, explicit_registration: bool
) -> None:
    from azure.ai.agentserver.core.tasks import _decorator, task
    from azure.ai.agentserver.core.tasks._models import TaskInfo

    monkeypatch.setattr(_decorator, "_REGISTERED_DESCRIPTORS", [])
    monkeypatch.setattr(_decorator, "_HOST_BOUND_TASK_NAMES", set())
    with _decorator._host_bound_task_registration():

        @task(name="host_bound")
        async def owned(ctx: TaskContext[str]) -> str:
            return ctx.input

    @task(name="ordinary_core")
    async def ordinary(ctx: TaskContext[str]) -> str:
        return ctx.input

    manager = TaskManager(config=_config_stub(), provider=LocalFileTaskProvider(tmp_path / "tasks"))
    if explicit_registration:
        manager.register_resume_callback(owned.name, owned._fn, owned._opts)
    await manager.startup()
    try:
        assert manager._resume_callbacks[ordinary.name] is ordinary._fn
        info = TaskInfo(
            id="persisted", agent_name="a", session_id="s", status="in_progress", source={"name": owned.name}
        )
        assert manager._recovery_is_authorized(owned.name) is explicit_registration
        assert (manager._find_resume_callback(info) is owned._fn) is explicit_registration
        assert (owned.name in manager._resume_callbacks) is explicit_registration
    finally:
        await manager.shutdown()


def test_late_host_bound_registration_does_not_publish_into_live_manager(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from azure.ai.agentserver.core.tasks import _decorator, task
    from azure.ai.agentserver.core.tasks._models import TaskInfo

    monkeypatch.setattr(_decorator, "_HOST_BOUND_TASK_NAMES", set())
    manager = TaskManager(config=_config_stub(), provider=LocalFileTaskProvider(tmp_path / "tasks"))
    set_task_manager(manager)
    with _decorator._host_bound_task_registration():

        @task(name="late_host_bound")
        async def owned(ctx: TaskContext[str]) -> str:
            return ctx.input

    assert owned.name not in manager._resume_callbacks
    assert not manager._recovery_is_authorized(owned.name)
    info = TaskInfo(id="persisted", agent_name="a", session_id="s", status="in_progress", source={"name": owned.name})
    assert manager._find_resume_callback(info) is None


@pytest.mark.parametrize("source", [None, {}, {"name": "identity_target"}, {"name": "unknown"}, {"name": None}])
@pytest.mark.parametrize("matching_title", [False, True])
def test_explicit_identity_never_uses_legacy_fallback(tmp_path, source, matching_title: bool) -> None:
    from azure.ai.agentserver.core.tasks._models import TaskInfo

    async def target(ctx: TaskContext[str]) -> str:
        return ctx.input

    manager = TaskManager(config=_config_stub(), provider=LocalFileTaskProvider(tmp_path / "tasks"))
    manager.register_resume_callback("identity_target", target)
    info = TaskInfo(
        id="persisted",
        agent_name="a",
        session_id="s",
        status="in_progress",
        title="identity_target old" if matching_title else "unrelated",
        source=source,
    )
    expected = target if source in (None, {}, {"name": "identity_target"}) else None
    assert manager._find_resume_callback(info) is expected
