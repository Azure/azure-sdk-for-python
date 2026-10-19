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
