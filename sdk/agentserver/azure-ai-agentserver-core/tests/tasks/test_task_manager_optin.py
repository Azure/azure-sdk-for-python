# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the double-gated resilient ``TaskManager`` auto-initialization.

``AgentServerHost`` stands up the resilient ``TaskManager`` (and its
potentially network-backed startup recovery scan) only when BOTH:

1. the resilient task subsystem was explicitly enabled via
   ``set_resilient_tasks_enabled(True)`` (defaults to ``False``), AND
2. at least one durable task has been declared (``@task`` /
   ``@multi_turn_task``, tracked in the ``_REGISTERED_DESCRIPTORS`` list).

Both conditions are read directly at lifespan startup. If either is false,
nothing is constructed and no task-store call is made — plain servers (e.g.
invocations-only hosts) pay nothing.
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
    the network-backed startup recovery scan runs only when BOTH the switch
    is enabled AND at least one durable task is declared."""

    @pytest.mark.asyncio
    async def test_manager_always_constructed_and_available(
        self, _clean_state, _fake_task_manager
    ) -> None:
        """Even with no opt-in, the manager is constructed and installed so
        ``get_task_manager()`` works (no ``TaskManagerNotInitialized``) — but
        its startup recovery scan does NOT run."""
        from azure.ai.agentserver.core import AgentServerHost
        from azure.ai.agentserver.core.tasks._manager import get_task_manager

        app = AgentServerHost()
        async with app.router.lifespan_context(app):
            # A manager exists and is retrievable during the active lifespan.
            assert len(_fake_task_manager.instances) == 1
            assert get_task_manager() is _fake_task_manager.instances[0]
            # No recovery scan happened (no opt-in).
            assert _fake_task_manager.instances[0].startup_called is False

        # Torn down + cleared on shutdown.
        assert _fake_task_manager.instances[0].shutdown_called is True

    @pytest.mark.asyncio
    async def test_disabled_but_task_declared_no_recovery(self, _clean_state, _fake_task_manager) -> None:
        """Switch off + a task declared: manager built, but no recovery scan."""
        from azure.ai.agentserver.core import AgentServerHost

        _declare_task()
        # switch left at default False
        app = AgentServerHost()
        async with app.router.lifespan_context(app):
            pass
        assert len(_fake_task_manager.instances) == 1
        assert _fake_task_manager.instances[0].startup_called is False

    @pytest.mark.asyncio
    async def test_enabled_but_no_task_no_recovery(self, _clean_state, _fake_task_manager) -> None:
        """Switch on + no task declared: manager built, but no recovery scan."""
        from azure.ai.agentserver.core import AgentServerHost

        set_resilient_tasks_enabled(True)
        app = AgentServerHost()
        async with app.router.lifespan_context(app):
            pass
        assert len(_fake_task_manager.instances) == 1
        assert _fake_task_manager.instances[0].startup_called is False

    @pytest.mark.asyncio
    async def test_enabled_and_task_runs_recovery(
        self, _clean_state, _fake_task_manager, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Both conditions true -> manager built AND startup recovery runs."""
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
    async def test_enabled_and_multi_turn_runs_recovery(self, _clean_state, _fake_task_manager) -> None:
        from azure.ai.agentserver.core import AgentServerHost

        set_resilient_tasks_enabled(True)

        @multi_turn_task(name="gate_lifespan_mt")
        async def _probe(ctx: "TaskContext[dict]") -> None:
            return None

        app = AgentServerHost()
        async with app.router.lifespan_context(app):
            pass

        assert len(_fake_task_manager.instances) == 1
        assert _fake_task_manager.instances[0].startup_called is True
