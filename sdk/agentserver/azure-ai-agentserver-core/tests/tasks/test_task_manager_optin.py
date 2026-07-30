# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for opt-in gating of resilient ``TaskManager`` auto-initialization.

``AgentServerHost`` must only stand up the ``TaskManager`` (and its
potentially network-backed startup recovery scan) when the application has
actually declared a durable task via ``@task`` / ``@multi_turn_task``.
Plain servers that never opt in — e.g. invocations-only hosts — must NOT
pay the hosted task-store startup cost (a blocking ``list()`` round-trip
plus credential-token acquisition that would gate server readiness while
having nothing to recover).

The opt-in signal is a non-empty ``_REGISTERED_DESCRIPTORS`` registry.
Both durable decorators funnel through the single ``Task.__init__``
registration site (``MultiTurnTask`` wraps an inner ``Task``), so declaring
either kind opts the app in.
"""
import logging

import pytest

from azure.ai.agentserver.core._base import _resilient_tasks_opted_in
from azure.ai.agentserver.core.tasks import (
    TaskContext,
    TaskManagerNotInitialized,
    multi_turn_task,
    task,
)
from azure.ai.agentserver.core.tasks import _decorator as _decorator_mod
from azure.ai.agentserver.core.tasks._manager import (
    get_task_manager,
    set_task_manager,
)


@pytest.fixture
def _isolate_registry():
    """Snapshot/clear/restore the global durable-task registry + manager.

    ``_REGISTERED_DESCRIPTORS`` is process-global and populated at
    decoration time by other test modules; snapshot and clear it so each
    test controls the opt-in state, then restore it (and reset the manager
    singleton) afterwards.
    """
    saved = list(_decorator_mod._REGISTERED_DESCRIPTORS)
    _decorator_mod._REGISTERED_DESCRIPTORS.clear()
    set_task_manager(None)
    try:
        yield _decorator_mod._REGISTERED_DESCRIPTORS
    finally:
        _decorator_mod._REGISTERED_DESCRIPTORS.clear()
        _decorator_mod._REGISTERED_DESCRIPTORS.extend(saved)
        set_task_manager(None)


class _FakeTaskManager:
    """Records construction + lifecycle without touching network/disk."""

    instances: "list[_FakeTaskManager]" = []

    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
        self.startup_called = False
        self.shutdown_called = False
        self.descriptors_loaded = False
        _FakeTaskManager.instances.append(self)

    def load_registered_descriptors(self) -> None:
        self.descriptors_loaded = True

    async def startup(self) -> None:
        self.startup_called = True

    async def shutdown(self) -> None:
        self.shutdown_called = True


@pytest.fixture
def _fake_task_manager(monkeypatch: pytest.MonkeyPatch):
    """Patch the ``TaskManager`` the lifespan imports so no real provider,
    token acquisition, or task-store round-trip happens during the test."""
    _FakeTaskManager.instances.clear()
    monkeypatch.setattr(
        "azure.ai.agentserver.core.tasks._manager.TaskManager",
        _FakeTaskManager,
    )
    return _FakeTaskManager


# ------------------------------------------------------------------ #
# _resilient_tasks_opted_in(): the opt-in signal
# ------------------------------------------------------------------ #


class TestOptInSignal:
    """Unit tests for ``_resilient_tasks_opted_in()``."""

    def test_empty_registry_is_not_opted_in(self, _isolate_registry) -> None:
        assert _resilient_tasks_opted_in() is False

    def test_task_decorator_opts_in(self, _isolate_registry) -> None:
        @task(name="optin_probe_one_shot")
        async def _probe(ctx: "TaskContext[dict]") -> None:
            return None

        assert _resilient_tasks_opted_in() is True

    def test_multi_turn_task_decorator_opts_in(self, _isolate_registry) -> None:
        @multi_turn_task(name="optin_probe_multi_turn")
        async def _probe(ctx: "TaskContext[dict]") -> None:
            return None

        assert _resilient_tasks_opted_in() is True

    def test_get_task_manager_still_raises_without_a_factory(
        self, _isolate_registry
    ) -> None:
        """Outside an active host lifespan (no factory installed), the raise
        behavior is preserved — lazy bootstrap only applies within a host."""
        with pytest.raises(TaskManagerNotInitialized):
            get_task_manager()


# ------------------------------------------------------------------ #
# Lifespan behaviour: gate is honoured at startup
# ------------------------------------------------------------------ #


class TestLifespanOptInGate:
    """Verify ``AgentServerHost`` lifespan honours the opt-in gate."""

    @pytest.mark.asyncio
    async def test_not_opted_in_defers_eager_init(
        self,
        _isolate_registry,
        _fake_task_manager,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """No durable task declared → no manager is eagerly constructed and
        no recovery scan runs; the expensive startup path is deferred."""
        from azure.ai.agentserver.core import AgentServerHost

        app = AgentServerHost()

        with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
            async with app.router.lifespan_context(app):
                # Nothing eagerly built during startup — no provider / token /
                # task-store round-trip happened.
                assert _fake_task_manager.instances == []

        assert not any(
            "TaskManager initialized automatically" in r.message for r in caplog.records
        )
        assert any(
            "TaskManager auto-init deferred" in r.message for r in caplog.records
        )

    @pytest.mark.asyncio
    async def test_first_task_declared_in_lifespan_lazily_bootstraps(
        self,
        _isolate_registry,
        _fake_task_manager,
    ) -> None:
        """Late-registration path: a task declared *during* the active
        lifespan (when eager init was skipped) must not fail on first use —
        ``get_task_manager()`` lazily bootstraps a manager instead of raising
        ``TaskManagerNotInitialized``."""
        from azure.ai.agentserver.core import AgentServerHost

        app = AgentServerHost()

        async with app.router.lifespan_context(app):
            # Nothing built yet.
            assert _fake_task_manager.instances == []

            # Declare the FIRST durable task now, mid-lifespan.
            @task(name="optin_late_declared_task")
            async def _late(ctx: "TaskContext[dict]") -> None:
                return None

            # First use resolves the manager — must not raise, and must
            # lazily construct + load descriptors.
            mgr = get_task_manager()
            assert mgr is _fake_task_manager.instances[0]
            assert mgr.descriptors_loaded is True

        # The lazily-bootstrapped manager is torn down on shutdown.
        assert _fake_task_manager.instances[0].shutdown_called is True

    @pytest.mark.asyncio
    async def test_opted_in_initializes_task_manager(
        self,
        _isolate_registry,
        _fake_task_manager,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """A declared ``@task`` → TaskManager is constructed and started."""
        from azure.ai.agentserver.core import AgentServerHost

        @task(name="optin_lifespan_task")
        async def _probe(ctx: "TaskContext[dict]") -> None:
            return None

        app = AgentServerHost()

        with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
            async with app.router.lifespan_context(app):
                pass

        assert len(_fake_task_manager.instances) == 1
        mgr = _fake_task_manager.instances[0]
        assert mgr.startup_called is True
        assert mgr.shutdown_called is True
        assert any(
            "TaskManager initialized automatically" in r.message for r in caplog.records
        )

    @pytest.mark.asyncio
    async def test_multi_turn_opt_in_initializes_task_manager(
        self,
        _isolate_registry,
        _fake_task_manager,
    ) -> None:
        """A declared ``@multi_turn_task`` also opts the host in."""
        from azure.ai.agentserver.core import AgentServerHost

        @multi_turn_task(name="optin_lifespan_multi_turn")
        async def _probe(ctx: "TaskContext[dict]") -> None:
            return None

        app = AgentServerHost()

        async with app.router.lifespan_context(app):
            pass

        assert len(_fake_task_manager.instances) == 1
        assert _fake_task_manager.instances[0].startup_called is True
