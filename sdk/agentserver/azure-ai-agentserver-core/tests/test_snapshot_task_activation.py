# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Session activation tests; author startup task submissions are out of scope."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import os
import socket
import time
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import httpx
import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.core import AgentServerHost, AgentSessionContext
from azure.ai.agentserver.core._base import _read_memory_snapshot_enabled
from azure.ai.agentserver.core.tasks import (
    TaskContext,
    TaskManagerNotInitialized,
    multi_turn_task,
    resilient_tasks_enabled,
    set_resilient_tasks_enabled,
    task,
)
from azure.ai.agentserver.core.tasks import _decorator, _manager
from azure.ai.agentserver.core.tasks._lease import derive_lease_owner
from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
from azure.ai.agentserver.core.tasks._manager import TaskManager, get_task_manager
from azure.ai.agentserver.core.tasks._models import TaskCreateRequest, TaskPatchRequest


@pytest.fixture(autouse=True)
def isolate_runtime(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    previous_environment = dict(os.environ)
    previous_manager = _manager._manager
    previous_enabled = resilient_tasks_enabled()
    previous_definitions = list(_decorator._REGISTERED_DESCRIPTORS)
    _manager.set_task_manager(None)
    set_resilient_tasks_enabled(True)
    _decorator._REGISTERED_DESCRIPTORS.clear()
    monkeypatch.setenv("FOUNDRY_AGENT_NAME", "snapshot-agent")
    monkeypatch.setenv("AGENTSERVER_SHUTDOWN_GRACE_SECONDS", "0")
    for name in (
        "FOUNDRY_HOSTING_ENVIRONMENT",
        "FOUNDRY_AGENT_SESSION_ID",
        "FOUNDRY_AGENT_SESSION_GUID",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("FOUNDRY_MEMORY_SNAPSHOT_ENABLED", "true")
    try:
        yield
    finally:
        _manager.set_task_manager(previous_manager)
        set_resilient_tasks_enabled(previous_enabled)
        _decorator._REGISTERED_DESCRIPTORS[:] = previous_definitions
        os.environ.clear()
        os.environ.update(previous_environment)


@pytest.fixture
def provider_factory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[LocalFileTaskProvider, Mock]:
    provider = LocalFileTaskProvider(base_dir=tmp_path)
    factory = Mock(return_value=provider)
    monkeypatch.setattr(TaskManager, "_create_provider", staticmethod(factory))
    return provider, factory


def payload(restore_id: str = "restore-1", session_id: str = "session-1") -> dict[str, Any]:
    return {
        "session_context": {
            "session_id": session_id,
            "restore_id": restore_id,
            "session_env_overrides": {
                "FOUNDRY_AGENT_SESSION_GUID": "a" * 32,
            },
        }
    }


def host() -> AgentServerHost:
    return AgentServerHost(configure_observability=None, graceful_shutdown_timeout=0)


def client(app: AgentServerHost) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")


@pytest.mark.parametrize(
    ("value", "expected"),
    [(None, False), ("true", True), ("TRUE", True), (" false ", False), ("false", False)],
)
def test_snapshot_flag_defaults_absence_to_false(
    monkeypatch: pytest.MonkeyPatch, value: str | None, expected: bool
) -> None:
    if value is None:
        monkeypatch.delenv("FOUNDRY_MEMORY_SNAPSHOT_ENABLED", raising=False)
    else:
        monkeypatch.setenv("FOUNDRY_MEMORY_SNAPSHOT_ENABLED", value)
    assert _read_memory_snapshot_enabled() is expected


@pytest.mark.parametrize("enabled", [False, True])
@pytest.mark.parametrize("value", [None, "false", "true"])
def test_sequential_lifespans_restart_enabled_tasks(
    monkeypatch: pytest.MonkeyPatch,
    provider_factory: tuple[LocalFileTaskProvider, Mock],
    enabled: bool,
    value: str | None,
) -> None:
    set_resilient_tasks_enabled(enabled)
    if value is None:
        monkeypatch.delenv("FOUNDRY_MEMORY_SNAPSHOT_ENABLED", raising=False)
    else:
        monkeypatch.setenv("FOUNDRY_MEMORY_SNAPSHOT_ENABLED", value)
    _, factory = provider_factory
    app = host()
    managers: list[TaskManager] = []

    for cycle in range(2):
        with TestClient(app) as http:
            assert http.get("/readiness").status_code == 200
            if value == "true":
                assert app._task_manager is None
                response = http.post("/_agent/after-restore", json=payload(restore_id=f"cycle-{cycle}"))
                assert response.status_code == 200, response.text
            if enabled:
                managers.append(get_task_manager())
                assert managers[-1] is app._task_manager
            else:
                factory.assert_not_called()
                assert app._task_manager is None
        assert app._task_manager is None

    if enabled:
        assert managers[0] is not managers[1]
        assert factory.call_count == 2


@pytest.mark.asyncio
@pytest.mark.parametrize("value", ["", " ", "0", "1", "yes", "invalid"])
async def test_invalid_present_flag_fails_startup(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    monkeypatch.setenv("FOUNDRY_MEMORY_SNAPSHOT_ENABLED", value)
    app = host()
    with pytest.raises(ValueError, match="must be 'true' or 'false'"):
        async with app.router.lifespan_context(app):
            pytest.fail("Invalid configuration was accepted")


@pytest.mark.asyncio
async def test_capture_and_snapshot_startup_do_not_construct_tasks(
    provider_factory: tuple[LocalFileTaskProvider, Mock],
) -> None:
    _, factory = provider_factory
    app = host()
    async with app.router.lifespan_context(app), client(app) as http:
        assert (await http.get("/readiness")).status_code == 200
        assert (await http.post("/_agent/before-snapshot", json={})).status_code == 200
        factory.assert_not_called()
        assert app._task_manager is None
        with pytest.raises(TaskManagerNotInitialized):
            get_task_manager()


@pytest.mark.asyncio
@pytest.mark.parametrize("value", [None, "false"])
async def test_false_or_absent_keeps_cold_activation(
    monkeypatch: pytest.MonkeyPatch,
    provider_factory: tuple[LocalFileTaskProvider, Mock],
    value: str | None,
) -> None:
    if value is None:
        monkeypatch.delenv("FOUNDRY_MEMORY_SNAPSHOT_ENABLED", raising=False)
    else:
        monkeypatch.setenv("FOUNDRY_MEMORY_SNAPSHOT_ENABLED", value)
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_ID", "cold-session")
    _, factory = provider_factory
    app = host()
    async with app.router.lifespan_context(app):
        manager = get_task_manager()
        assert manager is app._task_manager
        assert manager._lease_owner == derive_lease_owner("snapshot-agent", "cold-session")
        assert manager._periodic_recovery_task is not None
        assert not manager._periodic_recovery_task.done()
        assert all(phase.completed for phase in manager._startup_phases.values())
        await manager.startup()
        factory.assert_called_once()
    assert app._task_manager is None
    with pytest.raises(TaskManagerNotInitialized):
        get_task_manager()


@pytest.mark.asyncio
@pytest.mark.parametrize("enabled", [False, True])
@pytest.mark.parametrize("value", [None, "true", "false"])
async def test_startup_and_restore_honor_resilience_and_snapshot_flags(
    monkeypatch: pytest.MonkeyPatch,
    provider_factory: tuple[LocalFileTaskProvider, Mock],
    enabled: bool,
    value: str | None,
) -> None:
    set_resilient_tasks_enabled(enabled)
    if value is None:
        monkeypatch.delenv("FOUNDRY_MEMORY_SNAPSHOT_ENABLED", raising=False)
    else:
        monkeypatch.setenv("FOUNDRY_MEMORY_SNAPSHOT_ENABLED", value)
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_ID", "session-1")
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_GUID", "a" * 32)
    _, factory = provider_factory
    app = host()
    async with app.router.lifespan_context(app), client(app) as http:
        if enabled and value != "true":
            assert get_task_manager() is app._task_manager
            factory.assert_called_once()
        else:
            factory.assert_not_called()
            assert app._task_manager is None
            with pytest.raises(TaskManagerNotInitialized):
                get_task_manager()

        assert (await http.post("/_agent/after-restore", json=payload())).status_code == 200
        if enabled:
            manager = get_task_manager()
            assert manager is app._task_manager
            assert manager._config.session_id == "session-1"
            assert manager._periodic_recovery_task is not None
            assert not manager._periodic_recovery_task.done()
            factory.assert_called_once()
        else:
            factory.assert_not_called()
            assert app._task_manager is None
            with pytest.raises(TaskManagerNotInitialized):
                get_task_manager()
        assert os.environ.get("FOUNDRY_MEMORY_SNAPSHOT_ENABLED") == value
    assert app._task_manager is None


@pytest.mark.asyncio
@pytest.mark.parametrize("value", [None, "false"])
async def test_cold_runtime_rejects_restore_for_another_session(
    monkeypatch: pytest.MonkeyPatch,
    provider_factory: tuple[LocalFileTaskProvider, Mock],
    value: str | None,
) -> None:
    if value is None:
        monkeypatch.delenv("FOUNDRY_MEMORY_SNAPSHOT_ENABLED", raising=False)
    else:
        monkeypatch.setenv("FOUNDRY_MEMORY_SNAPSHOT_ENABLED", value)
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_ID", "cold-session")
    _, factory = provider_factory
    app = host()
    async with app.router.lifespan_context(app), client(app) as http:
        manager = get_task_manager()
        response = await http.post("/_agent/after-restore", json=payload())
        assert response.status_code == 409
        assert get_task_manager() is manager
        assert manager._config.session_id == "cold-session"
        factory.assert_called_once()


@pytest.mark.asyncio
async def test_restore_binds_after_dependencies_and_loads_saved_definitions(
    provider_factory: tuple[LocalFileTaskProvider, Mock],
) -> None:
    _, factory = provider_factory

    @task(name="registered_before_capture")
    async def declaration(ctx: TaskContext[dict[str, str]]) -> str:
        return ctx.input["value"]

    app = host()
    callback_seen = False

    @app.after_restore_handler
    async def dependencies(context: AgentSessionContext) -> None:
        nonlocal callback_seen
        assert context.session_id == "session-1"
        assert app.config.session_guid == "a" * 32
        assert app._task_manager is None
        callback_seen = True

    async with app.router.lifespan_context(app), client(app) as http:
        response = await http.post("/_agent/after-restore", json=payload())
        assert response.status_code == 200, response.text
        manager = get_task_manager()
        assert callback_seen
        assert manager._config.session_id == "session-1"
        assert manager._lease_owner == derive_lease_owner("snapshot-agent", "session-1")
        assert manager._resume_callbacks[declaration.name] is declaration._fn
        assert len(_decorator._REGISTERED_DESCRIPTORS) == 1
        assert all(
            phase.completed and phase.completed_restore_id == "restore-1" for phase in manager._startup_phases.values()
        )
        assert (await http.post("/_agent/after-restore", json=payload())).status_code == 200
        factory.assert_called_once()
    assert app._task_manager is None


@pytest.mark.asyncio
async def test_duplicate_inflight_restore_has_one_runtime_and_scanner(
    provider_factory: tuple[LocalFileTaskProvider, Mock], monkeypatch: pytest.MonkeyPatch
) -> None:
    _, factory = provider_factory
    entered, release = asyncio.Event(), asyncio.Event()
    original = TaskManager._recover_stale_tasks
    scans = 0

    async def recovery(manager: TaskManager) -> None:
        nonlocal scans
        scans += 1
        entered.set()
        await release.wait()
        await original(manager)

    monkeypatch.setattr(TaskManager, "_recover_stale_tasks", recovery)
    app = host()
    async with app.router.lifespan_context(app), client(app) as http:
        first = asyncio.create_task(http.post("/_agent/after-restore", json=payload()))
        await asyncio.wait_for(entered.wait(), 2)
        second = asyncio.create_task(http.post("/_agent/after-restore", json=payload()))
        await asyncio.sleep(0)
        assert not second.done()
        release.set()
        responses = await asyncio.gather(first, second)
        assert [response.status_code for response in responses] == [200, 200]
        scanner = get_task_manager()._periodic_recovery_task
        assert scanner is not None and not scanner.done()
        assert scans == 1
        factory.assert_called_once()
    assert scanner.done()


@pytest.mark.asyncio
async def test_partial_recovery_failure_reuses_valid_inactive_phases(
    provider_factory: tuple[LocalFileTaskProvider, Mock], monkeypatch: pytest.MonkeyPatch
) -> None:
    _, factory = provider_factory
    original = TaskManager._recover_stale_tasks
    scans = 0

    async def recovery(manager: TaskManager) -> None:
        nonlocal scans
        scans += 1
        if scans == 1:
            raise RuntimeError("Interrupted essential initialization")
        await original(manager)

    monkeypatch.setattr(TaskManager, "_recover_stale_tasks", recovery)
    app = host()
    async with app.router.lifespan_context(app), client(app) as http:
        first = await http.post("/_agent/after-restore", json=payload())
        assert first.status_code == 500
        manager = app._task_manager
        assert manager is not None
        assert manager._startup_phases["register"].completed
        assert not manager._startup_phases["recovery"].completed
        assert not manager._has_live_workers
        assert app.config.session_id == ""
        wrong_session = await http.post("/_agent/after-restore", json=payload(session_id="another-session"))
        assert wrong_session.status_code == 409
        second = await http.post("/_agent/after-restore", json=payload())
        assert second.status_code == 200, second.text
        assert get_task_manager() is manager
        assert scans == 2
        factory.assert_called_once()


@pytest.mark.asyncio
async def test_completed_recovery_is_not_repeated_after_scanner_creation_failure(
    provider_factory: tuple[LocalFileTaskProvider, Mock], monkeypatch: pytest.MonkeyPatch
) -> None:
    _, factory = provider_factory
    original_recovery = TaskManager._recover_stale_tasks
    loop = asyncio.get_running_loop()
    original_create = loop.create_task
    scans = 0
    fail_scanner = True

    async def recovery(manager: TaskManager) -> None:
        nonlocal scans
        scans += 1
        await original_recovery(manager)

    def create(coroutine: Any, *args: Any, **kwargs: Any) -> asyncio.Task[Any]:
        nonlocal fail_scanner
        code = getattr(coroutine, "cr_code", None)
        if fail_scanner and code is not None and code.co_name == "_periodic_recovery_loop":
            fail_scanner = False
            coroutine.close()
            raise RuntimeError("Scanner allocation failed")
        return original_create(coroutine, *args, **kwargs)

    monkeypatch.setattr(TaskManager, "_recover_stale_tasks", recovery)
    monkeypatch.setattr(loop, "create_task", create)
    app = host()
    async with app.router.lifespan_context(app), client(app) as http:
        first = await http.post("/_agent/after-restore", json=payload())
        assert first.status_code == 500
        manager = get_task_manager()
        assert manager._startup_phases["recovery"].completed
        assert not manager._startup_phases["periodic"].completed
        assert (await http.post("/_agent/after-restore", json=payload())).status_code == 200
        assert get_task_manager() is manager
        assert scans == 1
        factory.assert_called_once()


@pytest.mark.asyncio
async def test_list_failure_keeps_best_effort_startup_and_periodic_retry(
    provider_factory: tuple[LocalFileTaskProvider, Mock],
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.WARNING, logger="azure.ai.agentserver")
    provider, _ = provider_factory
    calls = 0
    retried = asyncio.Event()

    async def listing(**kwargs: Any) -> list[Any]:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise RuntimeError("Temporary LIST failure")
        retried.set()
        return []

    monkeypatch.setattr(provider, "list", listing)
    monkeypatch.setattr(_manager, "_PERIODIC_RECOVERY_INTERVAL_SECONDS", 0.01)
    app = host()
    async with app.router.lifespan_context(app), client(app) as http:
        response = await http.post("/_agent/after-restore", json=payload())
        assert response.status_code == 200, response.text
        assert get_task_manager()._startup_phases["recovery"].completed
        await asyncio.wait_for(retried.wait(), 2)
        assert "Temporary LIST failure" in caplog.text


async def seed_expired_task(provider: LocalFileTaskProvider, name: str, *, steering: bool = False) -> None:
    owner = derive_lease_owner("snapshot-agent", "session-1")
    task_payload: dict[str, Any] = {"input": {"value": "saved-input"}, "schema_version": "1"}
    if steering:
        task_payload["steering"] = {
            "cancel_requested": True,
            "active_input": {"value": "saved-input"},
            "pending_inputs": [{"value": "queued-input"}],
        }
    await provider.create(
        TaskCreateRequest(
            id="existing-task",
            agent_name="snapshot-agent",
            session_id="session-1",
            status="in_progress",
            title="Existing LRA",
            payload=task_payload,
            source={"type": "agentserver.task", "name": name},
            tags={"task_name": name},
            lease_owner=owner,
            lease_instance_id="old-executor",
            lease_duration_seconds=60,
        )
    )
    await provider.update(
        "existing-task",
        TaskPatchRequest(
            lease_owner=owner,
            lease_instance_id="old-executor",
            lease_duration_seconds=0,
        ),
    )


@pytest.mark.asyncio
async def test_recovered_task_runs_before_hook_success(
    provider_factory: tuple[LocalFileTaskProvider, Mock], monkeypatch: pytest.MonkeyPatch
) -> None:
    provider, _ = provider_factory
    running, finish, release_hook = asyncio.Event(), asyncio.Event(), asyncio.Event()
    heartbeat = asyncio.Event()
    observed: list[tuple[Any, str, bool]] = []
    app = host()

    @task(name="existing_lra")
    async def existing(ctx: TaskContext[dict[str, str]]) -> str:
        observed.append((ctx.input, ctx.entry_mode, app._lifecycle.restored_session_context is not None))
        running.set()
        await finish.wait()
        return "done"

    await seed_expired_task(provider, existing.name)
    monkeypatch.setattr(_manager, "_DEFAULT_LEASE_SECONDS", 10)
    original_update = provider.update

    async def update(task_id: str, patch: TaskPatchRequest) -> Any:
        result = await original_update(task_id, patch)
        if running.is_set() and patch.lease_duration_seconds == 10:
            heartbeat.set()
        return result

    monkeypatch.setattr(provider, "update", update)
    original = TaskManager._recover_stale_tasks

    async def recovery(manager: TaskManager) -> None:
        await original(manager)
        await running.wait()
        await release_hook.wait()

    monkeypatch.setattr(TaskManager, "_recover_stale_tasks", recovery)
    async with app.router.lifespan_context(app), client(app) as http:
        restore = asyncio.create_task(http.post("/_agent/after-restore", json=payload()))
        try:
            await asyncio.wait_for(running.wait(), 2)
            assert not restore.done()
            assert observed == [({"value": "saved-input"}, "recovered", False)]
            assert app._lifecycle.lock.locked()
            assert app._lifecycle.restored_session_context is None
            await asyncio.wait_for(heartbeat.wait(), 7)
            assert not restore.done()
            release_hook.set()
            assert (await restore).status_code == 200
        finally:
            release_hook.set()
            finish.set()
            if not restore.done():
                restore.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await restore


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["cancel", "exception"])
@pytest.mark.parametrize("kind", ["one_shot", "multi_turn", "steerable"])
@pytest.mark.parametrize("cooperative", [False, True])
async def test_cancelled_recovery_stops_workers_before_binding_rollback_and_retries(
    provider_factory: tuple[LocalFileTaskProvider, Mock],
    monkeypatch: pytest.MonkeyPatch,
    failure: str,
    kind: str,
    cooperative: bool,
) -> None:
    provider, factory = provider_factory
    running, finish = asyncio.Event(), asyncio.Event()
    final_bindings: list[str] = []
    resumed_inputs: list[tuple[str, Any, str]] = []
    app = host()

    decorator = (
        task(name="cancelled_lra")
        if kind == "one_shot"
        else multi_turn_task(name="cancelled_lra", steerable=kind == "steerable")
    )

    @decorator
    async def existing(ctx: TaskContext[dict[str, str]]) -> str:
        resumed_inputs.append((ctx.task_id, ctx.input, ctx.entry_mode))
        running.set()
        try:
            if cooperative:
                await ctx.shutdown.wait()
                raise asyncio.CancelledError
            await finish.wait()
            return ctx.input["value"]
        finally:
            final_bindings.append(app.config.session_id)

    await seed_expired_task(provider, existing.name, steering=kind == "steerable")
    original = TaskManager._recover_stale_tasks
    scans = 0
    managers: list[TaskManager] = []

    async def recovery(manager: TaskManager) -> None:
        nonlocal scans
        scans += 1
        managers.append(manager)
        await original(manager)
        if scans == 1:
            await running.wait()
            if failure == "exception":
                raise RuntimeError("Failure after recovered work started")
            await asyncio.Event().wait()

    monkeypatch.setattr(TaskManager, "_recover_stale_tasks", recovery)
    async with app.router.lifespan_context(app), client(app) as http:
        restore = asyncio.create_task(http.post("/_agent/after-restore", json=payload()))
        try:
            await asyncio.wait_for(running.wait(), 2)
            first = managers[0]
            first_instance = first._instance_id
            if failure == "cancel":
                restore.cancel()
            done, _ = await asyncio.wait({restore}, timeout=2)
            assert restore in done, "Rollback did not finish after stopping the original execution"
            if failure == "cancel":
                with pytest.raises(asyncio.CancelledError):
                    await restore
            else:
                assert (await restore).status_code == 500
            assert final_bindings == ["session-1"]
            assert not first._active_tasks
            assert first._shutdown_event.is_set()
            assert app.config.session_id == ""
            assert app._task_manager is None
            with pytest.raises(TaskManagerNotInitialized):
                get_task_manager()
            stored = await provider.get("existing-task")
            assert stored is not None
            assert stored.status == "in_progress"
            assert stored.payload["input"] == {"value": "saved-input"}
            assert stored.lease is not None
            assert datetime.fromisoformat(stored.lease.expires_at).timestamp() <= time.time()
            if kind == "steerable":
                assert stored.payload["steering"]["pending_inputs"] == [{"value": "queued-input"}]
            running.clear()
            response = await http.post("/_agent/after-restore", json=payload())
            assert response.status_code == 200, response.text
            second = get_task_manager()
            assert second is not first
            assert second._instance_id != first_instance
            assert second._lease_owner == first._lease_owner
            assert factory.call_count == 2
            await asyncio.wait_for(running.wait(), 2)
            assert resumed_inputs == [
                ("existing-task", {"value": "saved-input"}, "recovered"),
                ("existing-task", {"value": "saved-input"}, "recovered"),
            ]
        finally:
            finish.set()
            if not restore.done():
                restore.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await restore


@pytest.mark.asyncio
async def test_retry_with_unchanged_binding_keeps_live_worker_identity(
    provider_factory: tuple[LocalFileTaskProvider, Mock], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_ID", "session-1")
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_GUID", "a" * 32)
    provider, _ = provider_factory
    running, finish = asyncio.Event(), asyncio.Event()
    app = host()

    @task(name="same_binding_recovery")
    async def existing(ctx: TaskContext[dict[str, str]]) -> str:
        running.set()
        await finish.wait()
        return ctx.input["value"]

    await seed_expired_task(provider, existing.name)
    original = TaskManager._recover_stale_tasks
    scans = 0

    async def recovery(manager: TaskManager) -> None:
        nonlocal scans
        scans += 1
        await original(manager)
        if scans == 1:
            await running.wait()
            raise RuntimeError("Recovery failed after dispatch under an unchanged binding")

    monkeypatch.setattr(TaskManager, "_recover_stale_tasks", recovery)
    async with app.router.lifespan_context(app), client(app) as http:
        try:
            assert (await http.post("/_agent/after-restore", json=payload())).status_code == 500
            manager = get_task_manager()
            instance = manager._instance_id
            response = await http.post("/_agent/after-restore", json=payload())
            assert response.status_code == 200, response.text
            assert get_task_manager() is manager
            assert manager._instance_id == instance
            stored = await provider.get("existing-task")
            assert stored is not None and stored.lease is not None
            assert stored.lease.instance_id == instance
        finally:
            finish.set()


@pytest.mark.asyncio
async def test_rollback_joins_renewal_after_handler_observes_shutdown(
    provider_factory: tuple[LocalFileTaskProvider, Mock], monkeypatch: pytest.MonkeyPatch
) -> None:
    provider, _ = provider_factory
    running, renewal_started, renewal_cancelled, release = (asyncio.Event() for _ in range(4))
    final_bindings: list[str] = []
    app = host()

    @task(name="cooperative_rollback")
    async def existing(ctx: TaskContext[dict[str, str]]) -> str:
        running.set()
        await ctx.shutdown.wait()
        raise asyncio.CancelledError

    async def renewal(*_args: Any, **_kwargs: Any) -> None:
        renewal_started.set()
        try:
            await release.wait()
        except asyncio.CancelledError:
            renewal_cancelled.set()
            await release.wait()
        finally:
            final_bindings.append(app.config.session_id)

    await seed_expired_task(provider, existing.name)
    original = TaskManager._recover_stale_tasks

    async def recovery(manager: TaskManager) -> None:
        await original(manager)
        await running.wait()
        await renewal_started.wait()
        raise RuntimeError("Recovery failed with renewal still in flight")

    monkeypatch.setattr(_manager, "lease_renewal_loop", renewal)
    monkeypatch.setattr(TaskManager, "_recover_stale_tasks", recovery)
    async with app.router.lifespan_context(app), client(app) as http:
        restore = asyncio.create_task(http.post("/_agent/after-restore", json=payload()))
        try:
            await asyncio.wait_for(renewal_started.wait(), 2)
            done, _ = await asyncio.wait({restore}, timeout=0.1)
            assert not done, "Configuration rolled back while a retained renewal worker was still running"
            assert renewal_cancelled.is_set()
            assert app.config.session_id == "session-1"
        finally:
            release.set()
            response = await restore
        assert response.status_code == 500
        assert final_bindings == ["session-1"]
        assert app.config.session_id == ""
        stored = await provider.get("existing-task")
        assert stored is not None and stored.lease is not None
        assert datetime.fromisoformat(stored.lease.expires_at).timestamp() <= time.time()


@pytest.mark.asyncio
async def test_rollback_joins_renewal_after_completed_handler_leaves_active_entries(
    provider_factory: tuple[LocalFileTaskProvider, Mock], monkeypatch: pytest.MonkeyPatch
) -> None:
    provider, _ = provider_factory
    running, complete, renewal_started, renewal_cancelled, release = (asyncio.Event() for _ in range(5))
    final_bindings: list[str] = []
    managers: list[TaskManager] = []
    app = host()

    @task(name="completed_handler_rollback")
    async def existing(ctx: TaskContext[dict[str, str]]) -> str:
        running.set()
        await complete.wait()
        return ctx.input["value"]

    async def renewal(*_args: Any, **_kwargs: Any) -> None:
        renewal_started.set()
        try:
            await release.wait()
        except asyncio.CancelledError:
            renewal_cancelled.set()
            await release.wait()
        finally:
            final_bindings.append(app.config.session_id)

    await seed_expired_task(provider, existing.name)
    original = TaskManager._recover_stale_tasks

    async def recovery(manager: TaskManager) -> None:
        managers.append(manager)
        await original(manager)
        await running.wait()
        await renewal_started.wait()
        execution = manager._active_tasks["existing-task"].execution_task
        complete.set()
        await execution
        assert not manager._active_tasks
        raise RuntimeError("Recovery failed after a completed handler dropped its active entry")

    monkeypatch.setattr(_manager, "lease_renewal_loop", renewal)
    monkeypatch.setattr(TaskManager, "_recover_stale_tasks", recovery)
    async with app.router.lifespan_context(app), client(app) as http:
        restore = asyncio.create_task(http.post("/_agent/after-restore", json=payload()))
        try:
            await asyncio.wait_for(renewal_started.wait(), 2)
            done, _ = await asyncio.wait({restore}, timeout=0.1)
            assert not done, "Rollback missed a renewal whose handler had already completed"
            assert renewal_cancelled.is_set()
            assert app.config.session_id == "session-1"
        finally:
            release.set()
            response = await restore
        assert response.status_code == 500
        assert final_bindings == ["session-1"]
        assert app.config.session_id == ""
        assert not managers[0]._has_live_workers
        assert not managers[0]._owned_workers


@pytest.mark.asyncio
@pytest.mark.parametrize("interrupt_drain", [False, True])
async def test_rollback_defers_queued_input_after_current_turn_returns_normally(
    provider_factory: tuple[LocalFileTaskProvider, Mock],
    monkeypatch: pytest.MonkeyPatch,
    interrupt_drain: bool,
) -> None:
    monkeypatch.setenv("AGENTSERVER_SHUTDOWN_GRACE_SECONDS", "0.2")
    provider, _ = provider_factory
    running, queued, finish = (asyncio.Event() for _ in range(3))
    observed: list[tuple[Any, str]] = []
    app = host()

    @multi_turn_task(name="normal_return_rollback", steerable=True)
    async def existing(ctx: TaskContext[dict[str, str]]) -> str:
        observed.append((ctx.input, ctx.entry_mode))
        if ctx.input["value"] == "saved-input":
            running.set()
            await ctx.shutdown.wait()
            return "current turn finished"
        queued.set()
        await finish.wait()
        return ctx.input["value"]

    await seed_expired_task(provider, existing.name, steering=True)
    original = TaskManager._recover_stale_tasks
    original_get = TaskManager._provider_get_tracked
    drain_cancelled = asyncio.Event()
    blocked = False
    scans = 0

    async def read_for_drain(manager: TaskManager, task_id: str) -> Any:
        nonlocal blocked
        stored = await original_get(manager, task_id)
        if interrupt_drain and not blocked and stored is not None and stored.status == "suspended":
            blocked = True
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                drain_cancelled.set()
                raise
        return stored

    async def recovery(manager: TaskManager) -> None:
        nonlocal scans
        scans += 1
        await original(manager)
        if scans == 1:
            await running.wait()
            raise RuntimeError("Recovery failed before the handler returned during shutdown")

    monkeypatch.setattr(TaskManager, "_recover_stale_tasks", recovery)
    monkeypatch.setattr(TaskManager, "_provider_get_tracked", read_for_drain)
    async with app.router.lifespan_context(app), client(app) as http:
        try:
            assert (await http.post("/_agent/after-restore", json=payload())).status_code == 500
            assert not queued.is_set()
            assert drain_cancelled.is_set() == interrupt_drain
            stored = await provider.get("existing-task")
            assert stored is not None
            assert stored.status == "in_progress"
            assert stored.payload["input"] == {"value": "queued-input"}
            assert stored.payload["steering"]["pending_inputs"] == []
            response = await http.post("/_agent/after-restore", json=payload())
            assert response.status_code == 200, response.text
            await asyncio.wait_for(queued.wait(), 2)
            assert observed == [
                ({"value": "saved-input"}, "recovered"),
                ({"value": "queued-input"}, "recovered"),
            ]
        finally:
            finish.set()


@pytest.mark.asyncio
@pytest.mark.parametrize("new_restore", [False, True], ids=["same-restore", "new-restore"])
@pytest.mark.parametrize(
    ("failure", "failures", "retry_mode"),
    [
        pytest.param("read", 1, "restore", id="read-once"),
        pytest.param("read", 2, "restore", id="read-twice"),
        pytest.param("claim", 1, "restore", id="claim-once"),
        pytest.param("claim", 2, "restore", id="claim-twice"),
        pytest.param("committed_claim", 1, "restore", id="committed-claim"),
        pytest.param("read", 1, "cancel", id="cancelled-cleanup"),
        pytest.param("read", 1, "shutdown", id="shutdown-cleanup"),
    ],
)
async def test_restore_retries_pending_cleanup_without_losing_queued_inputs(
    provider_factory: tuple[LocalFileTaskProvider, Mock],
    monkeypatch: pytest.MonkeyPatch,
    failure: str,
    failures: int,
    retry_mode: str,
    new_restore: bool,
) -> None:
    monkeypatch.setenv("AGENTSERVER_SHUTDOWN_GRACE_SECONDS", "0.2")
    provider, factory = provider_factory
    running, queued, finish, drain_cancelled = (asyncio.Event() for _ in range(4))
    observed: list[Any] = []
    callbacks: list[str] = []
    in_reconciliation = False
    block_reconciliation = False
    cleanup_entered, release_cleanup = asyncio.Event(), asyncio.Event()
    cleanup_request: asyncio.Task[httpx.Response] | None = None
    remaining_failures = failures
    scans = 0
    app = host()

    @app.after_restore_handler
    async def dependencies(context: AgentSessionContext) -> None:
        callbacks.append(context.restore_id)
        assert app._task_manager is None

    @multi_turn_task(name="retry_cleanup", steerable=True)
    async def existing(ctx: TaskContext[dict[str, str]]) -> str:
        observed.append(ctx.input)
        if ctx.input["value"] == "saved-input":
            running.set()
            await ctx.shutdown.wait()
            return "current turn finished"
        queued.set()
        await finish.wait()
        return ctx.input["value"]

    await seed_expired_task(provider, existing.name, steering=True)
    stored = await provider.get("existing-task")
    assert stored is not None and stored.payload is not None
    steering = dict(stored.payload["steering"])
    steering["pending_inputs"].append({"value": "later-input"})
    await provider.update("existing-task", TaskPatchRequest(payload={"steering": steering}))
    original_read = TaskManager._provider_get_tracked
    original_update = provider.update
    original_reconcile = TaskManager._reconcile_steering_for_rollback
    original_recovery = TaskManager._recover_stale_tasks

    async def read(manager: TaskManager, task_id: str) -> Any:
        nonlocal remaining_failures
        if in_reconciliation and failure == "read" and remaining_failures:
            remaining_failures -= 1
            raise RuntimeError("Temporary reconciliation read failure")
        result = await original_read(manager, task_id)
        if not in_reconciliation and result is not None and result.status == "suspended":
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                drain_cancelled.set()
                raise
        return result

    async def update(task_id: str, patch: TaskPatchRequest) -> Any:
        nonlocal remaining_failures
        if in_reconciliation and patch.status == "in_progress" and failure != "read" and remaining_failures:
            remaining_failures -= 1
            if failure == "committed_claim":
                await original_update(task_id, patch)
            raise RuntimeError("Temporary reconciliation claim failure")
        return await original_update(task_id, patch)

    async def reconcile(manager: TaskManager, active_tasks: list[Any]) -> None:
        nonlocal in_reconciliation
        assert manager._materialization_restore_id == "restore-1"
        assert manager._config.session_guid == "a" * 32
        in_reconciliation = True
        try:
            if block_reconciliation:
                cleanup_entered.set()
                await release_cleanup.wait()
            await original_reconcile(manager, active_tasks)
        finally:
            in_reconciliation = False

    async def recovery(manager: TaskManager) -> None:
        nonlocal scans
        scans += 1
        await original_recovery(manager)
        if scans == 1:
            await asyncio.wait_for(running.wait(), 2)
            raise RuntimeError("Trigger rollback with pending steering input")

    monkeypatch.setattr(TaskManager, "_provider_get_tracked", read)
    monkeypatch.setattr(provider, "update", update)
    monkeypatch.setattr(TaskManager, "_reconcile_steering_for_rollback", reconcile)
    monkeypatch.setattr(TaskManager, "_recover_stale_tasks", recovery)
    retry_payload = payload(restore_id="restore-2" if new_restore else "restore-1")
    if new_restore:
        retry_payload["session_context"]["session_env_overrides"]["FOUNDRY_AGENT_SESSION_GUID"] = "b" * 32
    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test"
        ) as http,
    ):
        try:
            assert (await http.post("/_agent/after-restore", json=payload())).status_code == 500
            stopped = app._task_manager
            assert stopped is not None and stopped._shutdown_event.is_set()
            assert stopped._pending_shutdown_tasks
            assert drain_cancelled.is_set()
            assert not queued.is_set()
            for _ in range(failures - 1):
                assert (await http.post("/_agent/after-restore", json=retry_payload)).status_code == 500
                assert app._task_manager is get_task_manager() is stopped
                assert callbacks == ["restore-1"]
            if retry_mode == "shutdown":
                await app._shutdown_task_manager()
            elif retry_mode == "cancel":
                block_reconciliation = True
                cleanup_request = asyncio.create_task(http.post("/_agent/after-restore", json=retry_payload))
                await asyncio.wait_for(cleanup_entered.wait(), 2)
                cleanup_request.cancel()
                await asyncio.sleep(0)
                assert not cleanup_request.done()
                cleanup_request.cancel()
                release_cleanup.set()
                with pytest.raises(asyncio.CancelledError):
                    await asyncio.wait_for(cleanup_request, 2)
                block_reconciliation = False
            if retry_mode != "restore":
                assert app._task_manager is None
                assert not stopped._has_live_workers
                assert callbacks == ["restore-1"]
            response = await http.post("/_agent/after-restore", json=retry_payload)
            assert response.status_code == 200, response.text
            await asyncio.wait_for(queued.wait(), 2)
            assert remaining_failures == 0
            assert get_task_manager() is app._task_manager is not stopped
            assert not stopped._has_live_workers
            assert not stopped._pending_shutdown_tasks
            assert observed == [{"value": "saved-input"}, {"value": "queued-input"}]
            assert callbacks == ["restore-1", retry_payload["session_context"]["restore_id"]]
            stored = await provider.get("existing-task")
            assert stored is not None and stored.payload is not None
            assert stored.payload["input"] == {"value": "queued-input"}
            assert stored.payload["steering"]["pending_inputs"] == [{"value": "later-input"}]
            assert (await http.post("/_agent/after-restore", json=retry_payload)).status_code == 200
            assert len(callbacks) == 2
            assert len(observed) == 2
            assert scans == 2
            assert factory.call_count == 2
        finally:
            release_cleanup.set()
            finish.set()
            if cleanup_request is not None:
                if not cleanup_request.done():
                    cleanup_request.cancel()
                await asyncio.gather(cleanup_request, return_exceptions=True)


@pytest.mark.asyncio
async def test_http_timeout_continues_activation_and_retry_deduplicates(
    provider_factory: tuple[LocalFileTaskProvider, Mock],
) -> None:
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    _, factory = provider_factory
    app = host()
    callback_started = asyncio.Event()
    calls = 0

    @app.after_restore_handler
    async def dependencies(context: AgentSessionContext) -> None:
        nonlocal calls
        assert context.restore_id == "restore-1"
        calls += 1
        callback_started.set()
        await asyncio.sleep(0.4)

    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    config = Config()
    config.bind = [f"127.0.0.1:{port}"]
    config.accesslog = None
    config.errorlog = None
    config.graceful_timeout = 1
    stop = asyncio.Event()
    server = asyncio.create_task(serve(app, config, shutdown_trigger=stop.wait))
    try:
        async with httpx.AsyncClient(base_url=f"http://127.0.0.1:{port}", timeout=2) as http:
            for _ in range(100):
                if server.done():
                    await server
                    pytest.fail("HTTP server stopped before readiness")
                try:
                    ready = await http.get("/readiness")
                except httpx.ConnectError:
                    await asyncio.sleep(0.01)
                else:
                    assert ready.status_code == 200
                    break
            else:
                pytest.fail("HTTP server did not become ready")
            with pytest.raises(httpx.ReadTimeout):
                await http.post("/_agent/after-restore", json=payload(), timeout=0.05)
            assert callback_started.is_set()
            retry = await http.post("/_agent/after-restore", json=payload())
            assert retry.status_code == 200, retry.text
            assert calls == 1
            assert get_task_manager()._startup_phases["ready"].completed
            factory.assert_called_once()
    finally:
        stop.set()
        await asyncio.wait_for(server, 5)
