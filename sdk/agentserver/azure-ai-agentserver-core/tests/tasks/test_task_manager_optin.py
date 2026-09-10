# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the gated resilient ``TaskManager`` construction + recovery.

The resilient ``TaskManager`` is CONSTRUCTED ONLY when resilient tasks were
explicitly enabled via ``set_resilient_tasks_enabled(True)`` (default
``False``). Recovery — and the durable task subsystem as a whole — is strictly
opt-in.

When the switch is off the manager is NOT installed, so ``get_task_manager()``
raises ``TaskManagerNotInitialized``; callers that route through the manager
(e.g. the responses ``store=true`` path) swallow that at their outer catch and
degrade to non-durable in-process execution. Merely declaring a durable task
(``@task`` / ``@multi_turn_task``) — including internal protocol primitives —
does NOT turn the subsystem on. A plain server pays nothing: no manager, no
task-store call.
"""
import logging

import pytest

from azure.ai.agentserver.core._base import (
    _has_registered_tasks,
    _resilient_tasks_enabled,
)
from azure.ai.agentserver.core.tasks import (
    TaskContext,
    TaskManagerNotInitialized,
    multi_turn_task,
    resilient_tasks_enabled,
    set_resilient_tasks_enabled,
    task,
)
from azure.ai.agentserver.core.tasks import _decorator as _decorator_mod
from azure.ai.agentserver.core.tasks._manager import set_task_manager


@pytest.fixture
def _clean_state():
    """Snapshot/clear/restore the global registry, manager, and enable switch.

    ``_REGISTERED_DESCRIPTORS`` and the enable switch are process-global and
    may be touched by other test modules; snapshot and reset them so each test
    controls the gate, then restore afterwards.
    """
    saved_desc = list(_decorator_mod._REGISTERED_DESCRIPTORS)
    saved_enabled = resilient_tasks_enabled()
    _decorator_mod._REGISTERED_DESCRIPTORS.clear()
    set_resilient_tasks_enabled(False)
    set_task_manager(None)
    try:
        yield
    finally:
        _decorator_mod._REGISTERED_DESCRIPTORS.clear()
        _decorator_mod._REGISTERED_DESCRIPTORS.extend(saved_desc)
        set_resilient_tasks_enabled(saved_enabled)
        set_task_manager(None)


class _FakeTaskManager:
    """Records construction + lifecycle without touching network/disk."""

    instances: "list[_FakeTaskManager]" = []

    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
        self.startup_called = False
        self.shutdown_called = False
        _FakeTaskManager.instances.append(self)

    async def startup(self) -> None:
        self.startup_called = True

    async def shutdown(self) -> None:
        self.shutdown_called = True


@pytest.fixture
def _fake_task_manager(monkeypatch: pytest.MonkeyPatch):
    """Patch ``TaskManager`` so no real provider/token/task-store call happens."""
    _FakeTaskManager.instances.clear()
    monkeypatch.setattr(
        "azure.ai.agentserver.core.tasks._manager.TaskManager",
        _FakeTaskManager,
    )
    return _FakeTaskManager


def _declare_task(name: str = "gate_probe") -> None:
    @task(name=name)
    async def _probe(ctx: "TaskContext[dict]") -> None:
        return None


# ------------------------------------------------------------------ #
# The two gate signals
# ------------------------------------------------------------------ #


class TestGateSignals:
    """Unit tests for the enable switch and the descriptor-list check."""

    def test_switch_defaults_false(self, _clean_state) -> None:
        assert resilient_tasks_enabled() is False
        assert _resilient_tasks_enabled() is False

    def test_switch_toggles(self, _clean_state) -> None:
        set_resilient_tasks_enabled(True)
        assert _resilient_tasks_enabled() is True
        set_resilient_tasks_enabled(False)
        assert _resilient_tasks_enabled() is False

    def test_set_with_no_arg_enables(self, _clean_state) -> None:
        set_resilient_tasks_enabled()
        assert resilient_tasks_enabled() is True

    def test_has_registered_tasks_empty(self, _clean_state) -> None:
        assert _has_registered_tasks() is False

    def test_has_registered_tasks_after_task(self, _clean_state) -> None:
        _declare_task()
        assert _has_registered_tasks() is True

    def test_has_registered_tasks_after_multi_turn(self, _clean_state) -> None:
        @multi_turn_task(name="gate_probe_mt")
        async def _probe(ctx: "TaskContext[dict]") -> None:
            return None

        assert _has_registered_tasks() is True


# ------------------------------------------------------------------ #
# The AND gate at lifespan startup
# ------------------------------------------------------------------ #


class TestLifespanManagerAndRecovery:
    """The resilient TaskManager is CONSTRUCTED ONLY when the switch is
    explicitly enabled via ``set_resilient_tasks_enabled(True)``. With the
    switch off no manager is installed and ``get_task_manager()`` raises —
    callers swallow that and degrade to non-durable execution."""

    @pytest.mark.asyncio
    async def test_neither_enabled_nor_task_no_manager(
        self, _clean_state, _fake_task_manager
    ) -> None:
        """No switch, no task: the manager is NOT constructed and
        ``get_task_manager()`` raises ``TaskManagerNotInitialized``."""
        from azure.ai.agentserver.core import AgentServerHost
        from azure.ai.agentserver.core.tasks._manager import get_task_manager

        app = AgentServerHost()
        async with app.router.lifespan_context(app):
            # No manager constructed (switch off).
            assert len(_fake_task_manager.instances) == 0
            with pytest.raises(TaskManagerNotInitialized):
                get_task_manager()

    @pytest.mark.asyncio
    async def test_task_declared_without_switch_no_manager(self, _clean_state, _fake_task_manager) -> None:
        """A declared task alone does NOT construct the manager: the durable
        task subsystem is opt-in and gated solely on the switch."""
        from azure.ai.agentserver.core import AgentServerHost
        from azure.ai.agentserver.core.tasks._manager import get_task_manager

        _declare_task()
        # switch left at default False
        app = AgentServerHost()
        async with app.router.lifespan_context(app):
            assert len(_fake_task_manager.instances) == 0
            with pytest.raises(TaskManagerNotInitialized):
                get_task_manager()

    @pytest.mark.asyncio
    async def test_switch_alone_builds_manager_and_runs_recovery(self, _clean_state, _fake_task_manager) -> None:
        """The switch constructs the manager and runs recovery (force-enable)
        — starting the periodic recovery loop so a task declared later is
        picked up."""
        from azure.ai.agentserver.core import AgentServerHost
        from azure.ai.agentserver.core.tasks._manager import get_task_manager

        set_resilient_tasks_enabled(True)
        app = AgentServerHost()
        async with app.router.lifespan_context(app):
            assert len(_fake_task_manager.instances) == 1
            assert get_task_manager() is _fake_task_manager.instances[0]
            assert _fake_task_manager.instances[0].startup_called is True
        assert _fake_task_manager.instances[0].shutdown_called is True

    @pytest.mark.asyncio
    async def test_switch_and_task_builds_manager_and_runs_recovery(
        self, _clean_state, _fake_task_manager, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Switch on and a task declared -> manager built and startup recovery
        runs."""
        from azure.ai.agentserver.core import AgentServerHost

        set_resilient_tasks_enabled(True)
        _declare_task()

        app = AgentServerHost()
        with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
            async with app.router.lifespan_context(app):
                pass

        assert len(_fake_task_manager.instances) == 1
        mgr = _fake_task_manager.instances[0]
        assert mgr.startup_called is True
        assert mgr.shutdown_called is True
        assert any("TaskManager initialized with startup recovery" in r.message for r in caplog.records)

    @pytest.mark.asyncio
    async def test_multi_turn_task_declared_without_switch_no_manager(
        self, _clean_state, _fake_task_manager
    ) -> None:
        """A declared ``@multi_turn_task`` alone also does NOT construct the
        manager (opt-in)."""
        from azure.ai.agentserver.core import AgentServerHost
        from azure.ai.agentserver.core.tasks._manager import get_task_manager

        @multi_turn_task(name="gate_lifespan_mt")
        async def _probe(ctx: "TaskContext[dict]") -> None:
            return None

        app = AgentServerHost()
        async with app.router.lifespan_context(app):
            assert len(_fake_task_manager.instances) == 0
            with pytest.raises(TaskManagerNotInitialized):
                get_task_manager()

    @pytest.mark.asyncio
    async def test_switch_on_startup_failure_fails_lifespan(
        self, _clean_state, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """When resilient tasks are ENABLED but manager startup fails, the
        lifespan must fail fast (fail-fast at boot) rather than start a server
        that would silently run store=true work non-durably. The partially
        started manager must be torn down and the singleton cleared so it is not
        left visible through ``get_task_manager()``."""
        from azure.ai.agentserver.core import AgentServerHost
        from azure.ai.agentserver.core.tasks._manager import get_task_manager

        shutdown_calls: list[int] = []

        class _FailingManager:
            def __init__(self, **kwargs) -> None:
                pass

            async def startup(self) -> None:
                raise RuntimeError("simulated boot failure")

            async def shutdown(self) -> None:
                shutdown_calls.append(1)

        monkeypatch.setattr(
            "azure.ai.agentserver.core.tasks._manager.TaskManager",
            _FailingManager,
        )
        set_resilient_tasks_enabled(True)

        app = AgentServerHost()
        with pytest.raises(RuntimeError, match="simulated boot failure"):
            async with app.router.lifespan_context(app):
                pass

        # The partially started manager was torn down and the singleton cleared.
        assert shutdown_calls == [1]
        with pytest.raises(TaskManagerNotInitialized):
            get_task_manager()
