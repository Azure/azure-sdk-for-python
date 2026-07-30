# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the gated resilient ``TaskManager`` startup recovery scan.

``AgentServerHost`` always constructs the resilient ``TaskManager`` (a cheap,
in-memory object that makes no task-store calls), so ``get_task_manager()`` and
``.run()`` / ``.start()`` work regardless. Its network-backed **startup
recovery scan** (and the periodic recovery loop it spawns) runs when EITHER:

1. at least one durable task has been declared (``@task`` /
   ``@multi_turn_task``, tracked in the ``_REGISTERED_DESCRIPTORS`` list), OR
2. the switch was set via ``set_resilient_tasks_enabled(True)`` (default
   ``False``) — a force-enable.

Both signals are read directly at lifespan startup. When neither is true, no
task-store call is made — plain servers (e.g. invocations-only hosts) pay
nothing.
"""
import logging

import pytest

from azure.ai.agentserver.core._base import (
    _has_registered_tasks,
    _resilient_tasks_enabled,
)
from azure.ai.agentserver.core.tasks import (
    TaskContext,
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
    """The TaskManager is ALWAYS constructed (cheap, no task-store calls);
    the network-backed startup recovery scan runs when EITHER the switch is
    enabled OR at least one durable task is declared."""

    @pytest.mark.asyncio
    async def test_neither_enabled_nor_task_no_recovery(
        self, _clean_state, _fake_task_manager
    ) -> None:
        """No switch, no task: the manager is constructed and installed so
        ``get_task_manager()`` works (no ``TaskManagerNotInitialized``) — but
        the startup recovery scan does NOT run (plain invocations host)."""
        from azure.ai.agentserver.core import AgentServerHost
        from azure.ai.agentserver.core.tasks._manager import get_task_manager

        app = AgentServerHost()
        async with app.router.lifespan_context(app):
            # A manager exists and is retrievable during the active lifespan.
            assert len(_fake_task_manager.instances) == 1
            assert get_task_manager() is _fake_task_manager.instances[0]
            # No recovery scan happened (neither gate true).
            assert _fake_task_manager.instances[0].startup_called is False

        # Torn down + cleared on shutdown.
        assert _fake_task_manager.instances[0].shutdown_called is True

    @pytest.mark.asyncio
    async def test_task_declared_runs_recovery_without_switch(self, _clean_state, _fake_task_manager) -> None:
        """A declared task alone runs recovery (backward compatible — an
        existing ``@task`` app gets recovery without calling the switch)."""
        from azure.ai.agentserver.core import AgentServerHost

        _declare_task()
        # switch left at default False
        app = AgentServerHost()
        async with app.router.lifespan_context(app):
            pass
        assert len(_fake_task_manager.instances) == 1
        assert _fake_task_manager.instances[0].startup_called is True

    @pytest.mark.asyncio
    async def test_switch_alone_runs_recovery_without_task(self, _clean_state, _fake_task_manager) -> None:
        """The switch alone runs recovery (force-enable) — starting the
        periodic recovery loop so a task declared later is picked up."""
        from azure.ai.agentserver.core import AgentServerHost

        set_resilient_tasks_enabled(True)
        app = AgentServerHost()
        async with app.router.lifespan_context(app):
            pass
        assert len(_fake_task_manager.instances) == 1
        assert _fake_task_manager.instances[0].startup_called is True

    @pytest.mark.asyncio
    async def test_switch_and_task_runs_recovery(
        self, _clean_state, _fake_task_manager, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Both signals true -> manager built and startup recovery runs."""
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
    async def test_multi_turn_task_runs_recovery_without_switch(self, _clean_state, _fake_task_manager) -> None:
        """A declared ``@multi_turn_task`` alone also runs recovery."""
        from azure.ai.agentserver.core import AgentServerHost

        @multi_turn_task(name="gate_lifespan_mt")
        async def _probe(ctx: "TaskContext[dict]") -> None:
            return None

        app = AgentServerHost()
        async with app.router.lifespan_context(app):
            pass

        assert len(_fake_task_manager.instances) == 1
        assert _fake_task_manager.instances[0].startup_called is True
