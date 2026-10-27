# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Rollback must retain one identity and stop all task admission before quiescence."""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from pathlib import Path

import pytest

from azure.ai.agentserver.core.tasks import TaskContext, multi_turn_task, task
from azure.ai.agentserver.core.tasks import _manager
from azure.ai.agentserver.core.tasks._exceptions import TaskDeferred
from azure.ai.agentserver.core.tasks._lease import derive_lease_owner
from azure.ai.agentserver.core.tasks._manager import TaskManager, get_task_manager
from azure.ai.agentserver.core.tasks._models import TaskPatchRequest
from test_snapshot_task_activation import client, host, isolate_runtime, payload, provider_factory, seed_expired_task


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["exception", "cancel"])
@pytest.mark.parametrize("started", [False, True])
async def test_agent_name_override_does_not_retain_incompatible_runtime(
    monkeypatch, provider_factory, failure, started
):
    provider, factory = provider_factory
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_ID", "session-1")
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_GUID", "a" * 32)
    running, finish, failing = asyncio.Event(), asyncio.Event(), asyncio.Event()
    managers, final_agents = [], []
    app = host()

    @task(name="agent_identity_startup")
    async def startup(ctx: TaskContext[str]) -> str:
        running.set()
        try:
            await finish.wait()
            return ctx.input
        finally:
            final_agents.append(app.config.agent_name)

    @app.after_restore_handler
    async def initialize(context):
        managers.append(get_task_manager())
        if len(managers) == 1:
            if started:
                await startup.start(task_id="agent-startup", input=context.session_id)
                await asyncio.wait_for(running.wait(), 2)
            failing.set()
            if failure == "exception":
                raise RuntimeError("Fail the overridden agent startup")
            await asyncio.Event().wait()
        assert app.config.agent_name == "snapshot-agent"

    first = payload()
    first["session_context"]["session_env_overrides"]["FOUNDRY_AGENT_NAME"] = "overridden-agent"
    async with app.router.lifespan_context(app), client(app) as http:
        request = asyncio.create_task(http.post("/_agent/after-restore", json=first))
        try:
            await asyncio.wait_for(failing.wait(), 2)
            if failure == "cancel":
                request.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await request
            else:
                assert (await request).status_code == 500
            response = await http.post("/_agent/after-restore", json=payload())
            assert response.status_code == 200, response.text
            assert managers[0] is not managers[1]
            assert managers[0]._shutdown_event.is_set()
            assert not managers[0]._has_live_workers
            assert managers[1]._lease_owner == derive_lease_owner("snapshot-agent", "session-1")
            assert factory.call_count == 2
            assert final_agents == (["overridden-agent"] if started else [])
            if started:
                stored = await provider.get("agent-startup")
                assert stored.agent_name == "overridden-agent"
                assert stored.payload["input"] == "session-1"
                assert stored.status == "in_progress"
                assert stored.lease.owner == derive_lease_owner("overridden-agent", "session-1")
                assert datetime.fromisoformat(stored.lease.expires_at) <= datetime.now(timezone.utc)
        finally:
            finish.set()
            if not request.done():
                request.cancel()
            await asyncio.gather(request, return_exceptions=True)


@pytest.mark.asyncio
async def test_live_agent_override_is_rejected_before_mutation(provider_factory):
    provider, _ = provider_factory
    app = host()
    running, finish = asyncio.Event(), asyncio.Event()
    callbacks = []

    @task(name="live_agent_startup")
    async def startup(ctx: TaskContext[str]) -> str:
        running.set()
        await finish.wait()
        return ctx.input

    @app.after_restore_handler
    async def initialize(context):
        callbacks.append(context.restore_id)
        await startup.start(task_id="live-agent-startup", input=context.session_id)
        await asyncio.wait_for(running.wait(), 2)

    async with app.router.lifespan_context(app), client(app) as http:
        try:
            assert (await http.post("/_agent/after-restore", json=payload())).status_code == 200
            manager = get_task_manager()
            changed = payload(restore_id="restore-2")
            changed["session_context"]["session_env_overrides"]["FOUNDRY_AGENT_NAME"] = "other-agent"
            response = await http.post("/_agent/after-restore", json=changed)
            assert response.status_code == 409
            assert callbacks == ["restore-1"]
            assert os.environ["FOUNDRY_AGENT_NAME"] == app.config.agent_name == "snapshot-agent"
            assert manager._materialization_restore_id == "restore-1"
            assert manager._lease_owner == derive_lease_owner("snapshot-agent", "session-1")
            stored = await provider.get("live-agent-startup")
            assert stored.lease.owner == manager._lease_owner
        finally:
            finish.set()


@pytest.mark.asyncio
@pytest.mark.parametrize("guid", ["b" * 32, "", None], ids=["changed", "cleared", "captured-baseline"])
async def test_live_guid_override_preserves_manager_and_worker_lease_identity(provider_factory, monkeypatch, guid):
    provider, _ = provider_factory
    running, finish = asyncio.Event(), asyncio.Event()
    callbacks, renewal_identities, runs = [], [], []
    original_renewal = _manager.lease_renewal_loop
    app = host()

    async def renewal(*args, **kwargs):
        renewal_identities.append((kwargs["lease_owner"], kwargs["lease_instance_id"]))
        await original_renewal(*args, **kwargs)

    monkeypatch.setattr(_manager, "lease_renewal_loop", renewal)

    @task(name="live_guid_startup")
    async def startup(ctx: TaskContext[str]) -> str:
        running.set()
        await finish.wait()
        return ctx.input

    @app.after_restore_handler
    async def initialize(context):
        callbacks.append(context.restore_id)
        runs.append(await startup.start(task_id="live-guid-startup", input=context.session_id))
        await asyncio.wait_for(running.wait(), 2)

    async with app.router.lifespan_context(app), client(app) as http:
        try:
            assert (await http.post("/_agent/after-restore", json=payload())).status_code == 200
            manager = get_task_manager()
            identity = (manager._lease_owner, manager._instance_id)
            worker = manager._active_tasks["live-guid-startup"]
            changed = payload(restore_id="restore-2")
            overrides = changed["session_context"]["session_env_overrides"]
            if guid is None:
                overrides.pop("FOUNDRY_AGENT_SESSION_GUID")
            else:
                overrides["FOUNDRY_AGENT_SESSION_GUID"] = guid
            response = await http.post("/_agent/after-restore", json=changed)
            assert response.status_code == 409, response.text
            assert response.json()["error"]["code"] == "session_guid_mismatch"
            assert get_task_manager() is manager
            assert callbacks == ["restore-1"]
            assert manager._materialization_restore_id == "restore-1"
            assert (manager._lease_owner, manager._instance_id) == identity
            assert renewal_identities == [identity]
            assert manager._active_tasks["live-guid-startup"] is worker
            assert not worker.execution_task.done()
            assert not worker.renewal_task.done()
            assert os.environ["FOUNDRY_AGENT_SESSION_GUID"] == app.config.session_guid == "a" * 32
            stored = await provider.get("live-guid-startup")
            assert (stored.lease.owner, stored.lease.instance_id) == identity
        finally:
            finish.set()
            await asyncio.wait_for(asyncio.gather(*(run.result() for run in runs), return_exceptions=True), 2)


@pytest.mark.asyncio
@pytest.mark.parametrize("work", ["running", "admitted"])
@pytest.mark.parametrize("duplicate", [False, True])
async def test_compatible_restore_preserves_owned_task_lease_identity(provider_factory, monkeypatch, work, duplicate):
    provider, factory = provider_factory
    app = host()
    written, release, running, finish = (asyncio.Event() for _ in range(4))
    callbacks, renewal_identities = [], []
    original_create = provider.create
    original_renewal = _manager.lease_renewal_loop

    async def create(request):
        stored = await original_create(request)
        if work == "admitted":
            written.set()
            await release.wait()
        return stored

    async def renewal(*args, **kwargs):
        renewal_identities.append((kwargs["lease_owner"], kwargs["lease_instance_id"]))
        await original_renewal(*args, **kwargs)

    monkeypatch.setattr(provider, "create", create)
    monkeypatch.setattr(_manager, "lease_renewal_loop", renewal)

    @task(name="compatible_restore")
    async def startup(ctx: TaskContext[str]) -> str:
        running.set()
        await finish.wait()
        return ctx.input

    @app.after_restore_handler
    async def initialize(context):
        callbacks.append(context.restore_id)

    producer = None
    run = None
    async with app.router.lifespan_context(app), client(app) as http:
        try:
            assert (await http.post("/_agent/after-restore", json=payload())).status_code == 200
            manager = get_task_manager()
            identity = (manager._lease_owner, manager._instance_id)
            scanner = manager._periodic_recovery_task
            producer = asyncio.create_task(startup.start(task_id="compatible-restore", input="saved"))
            if work == "admitted":
                await asyncio.wait_for(written.wait(), 2)
                assert manager._active_admissions
                assert manager._admitted_task_ids["compatible-restore"] > 0
                assert not manager._active_tasks
            else:
                run = await asyncio.wait_for(producer, 2)
                await asyncio.wait_for(running.wait(), 2)
            changed = payload(restore_id="restore-2")
            requests = [http.post("/_agent/after-restore", json=changed)]
            if duplicate:
                requests.append(http.post("/_agent/after-restore", json=changed))
            responses = await asyncio.gather(*requests)
            assert all(response.status_code == 200 for response in responses)
            assert get_task_manager() is manager
            assert factory.call_count == 1
            assert callbacks == ["restore-1", "restore-2"]
            assert manager._materialization_restore_id == "restore-2"
            assert (manager._lease_owner, manager._instance_id) == identity
            assert manager._periodic_recovery_task is scanner
            release.set()
            run = await asyncio.wait_for(producer, 2)
            await asyncio.wait_for(running.wait(), 2)
            assert not manager._admitted_task_ids
            assert renewal_identities == [identity]
            await manager._provider_update_locked(
                "compatible-restore",
                TaskPatchRequest(
                    payload={"probe": "after-compatible-restore"},
                    **manager._lease_ext_kwargs("compatible-restore"),
                ),
            )
            stored = await provider.get("compatible-restore")
            assert (stored.lease.owner, stored.lease.instance_id) == identity
            assert stored.payload["input"] == "saved"
            assert stored.payload["probe"] == "after-compatible-restore"
        finally:
            release.set()
            finish.set()
            if producer is not None:
                result = await asyncio.wait_for(asyncio.gather(producer, return_exceptions=True), 2)
                if run is None and not isinstance(result[0], BaseException):
                    run = result[0]
            if run is not None:
                await asyncio.wait_for(asyncio.gather(run.result(), return_exceptions=True), 2)


@pytest.mark.asyncio
@pytest.mark.parametrize("api", ["start", "run", "get-active", "manager-keyword", "recovery"])
async def test_inline_claim_registration_is_excluded_from_recovery(provider_factory, monkeypatch, api):
    provider, _ = provider_factory
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_ID", "session-1")
    manager = TaskManager(config=host().config, provider=provider, shutdown_grace_seconds=0)
    _manager.set_task_manager(manager)
    claimed, release, running, finish = (asyncio.Event() for _ in range(4))
    observed = []
    blocked = False
    original_update = provider.update

    @task(name="inline_claim_registration")
    async def existing(ctx: TaskContext[dict[str, str]]) -> str:
        observed.append(ctx.input)
        running.set()
        await finish.wait()
        return ctx.input["value"]

    async def update(task_id, patch):
        nonlocal blocked
        result = await original_update(task_id, patch)
        if not blocked and patch.lease_instance_id == manager._instance_id and patch.lease_duration_seconds:
            blocked = True
            claimed.set()
            await release.wait()
        return result

    await manager.startup(restore_id="restore-1")
    await seed_expired_task(provider, existing.name)
    monkeypatch.setattr(provider, "update", update)
    if api == "start":
        operation = existing.start(task_id="existing-task", input={"value": "saved-input"})
    elif api == "run":
        operation = existing.run(task_id="existing-task", input={"value": "saved-input"})
    elif api == "get-active":
        operation = existing.get_active_run("existing-task")
    elif api == "recovery":
        operation = manager._recover_stale_tasks()
    else:
        operation = manager.get_active_run(task_id="existing-task")
    inline = asyncio.create_task(operation)
    recovery = None
    run = None
    try:
        await asyncio.wait_for(claimed.wait(), 2)
        stored = await provider.get("existing-task")
        assert stored.lease.instance_id == manager._instance_id
        assert not manager._active_tasks
        recovery = asyncio.create_task(manager._recover_stale_tasks())
        await asyncio.wait_for(asyncio.shield(recovery), 1)
        assert manager._admitted_task_ids["existing-task"] > 0
        assert observed == []
        release.set()
        if api not in ("run", "recovery"):
            run = await asyncio.wait_for(inline, 2)
            assert run is not None
        await asyncio.wait_for(running.wait(), 2)
        if api == "recovery":
            await asyncio.wait_for(inline, 2)
            run = await manager.get_active_run(task_id="existing-task")
            assert run is not None
        await manager._recover_stale_tasks()
        assert observed == [{"value": "saved-input"}]
        assert not manager._admitted_task_ids
        finish.set()
        if api == "run":
            assert await asyncio.wait_for(inline, 2) == "saved-input"
        else:
            assert await asyncio.wait_for(run.result(), 2) == "saved-input"
    finally:
        release.set()
        finish.set()
        pending = [inline] + ([recovery] if recovery is not None else [])
        results = await asyncio.wait_for(asyncio.gather(*pending, return_exceptions=True), 2)
        if api != "run" and not isinstance(results[0], BaseException) and results[0] is not None:
            await asyncio.wait_for(asyncio.gather(results[0].result(), return_exceptions=True), 2)
        await manager.shutdown(wait_for_workers=True, preserve_recoverable_tasks=True)


@pytest.mark.asyncio
@pytest.mark.parametrize("preserve", [False, True])
async def test_shutdown_interrupts_blocked_periodic_recovery_list(provider_factory, monkeypatch, preserve):
    provider, _ = provider_factory
    monkeypatch.setattr(_manager, "_PERIODIC_RECOVERY_INTERVAL_SECONDS", 0.01)
    manager = TaskManager(config=host().config, provider=provider, shutdown_grace_seconds=0)
    blocked, release, cancelled = (asyncio.Event() for _ in range(3))
    original_list = provider.list
    calls = 0

    async def list_tasks(**kwargs):
        nonlocal calls
        calls += 1
        if calls > 1:
            blocked.set()
            try:
                await release.wait()
            except asyncio.CancelledError:
                cancelled.set()
                raise
        return await original_list(**kwargs)

    monkeypatch.setattr(provider, "list", list_tasks)
    shutdown = None
    try:
        await manager.startup(restore_id="restore-1")
        scanner = manager._periodic_recovery_task
        await asyncio.wait_for(blocked.wait(), 2)
        shutdown = asyncio.create_task(manager.shutdown(wait_for_workers=True, preserve_recoverable_tasks=preserve))
        await asyncio.wait_for(asyncio.shield(shutdown), 1)
        assert cancelled.is_set()
        assert scanner.done()
        assert manager._periodic_recovery_task is None
        assert manager._admissions_drained.is_set()
        assert not manager._active_admissions
        assert not manager._has_live_workers
    finally:
        release.set()
        if shutdown is not None:
            await asyncio.wait_for(asyncio.gather(shutdown, return_exceptions=True), 2)
        await manager.shutdown(wait_for_workers=True, preserve_recoverable_tasks=preserve)


@pytest.mark.asyncio
@pytest.mark.parametrize("inner_id", ["outer", "inner"])
async def test_task_registration_admission_cleans_up_nested_failure(provider_factory, inner_id):
    provider, _ = provider_factory
    manager = TaskManager(config=host().config, provider=provider, shutdown_grace_seconds=0)
    with manager._task_admission(task_id="outer"):
        with pytest.raises(RuntimeError, match="nested failure"):
            with manager._task_admission(task_id=inner_id):
                assert manager._admitted_task_ids == ({"outer": 2} if inner_id == "outer" else {"outer": 1, "inner": 1})
                raise RuntimeError("nested failure")
        assert manager._admitted_task_ids == {"outer": 1}
        assert not manager._admissions_drained.is_set()
    assert not manager._admitted_task_ids
    assert not manager._active_admissions
    assert manager._admissions_drained.is_set()
    await manager.shutdown(wait_for_workers=True)


@pytest.mark.asyncio
async def test_compatible_restore_without_owned_task_work_rotates_lease_identity(provider_factory):
    _, factory = provider_factory
    app = host()
    async with app.router.lifespan_context(app), client(app) as http:
        assert (await http.post("/_agent/after-restore", json=payload())).status_code == 200
        manager = get_task_manager()
        await asyncio.wait_for(manager._admissions_drained.wait(), 2)
        instance = manager._instance_id
        scanner = manager._periodic_recovery_task
        assert scanner is not None and not scanner.done()
        assert not manager._active_tasks
        assert all(worker is scanner or worker.done() for worker in manager._owned_workers)
        response = await http.post("/_agent/after-restore", json=payload(restore_id="restore-2"))
        assert response.status_code == 200, response.text
        assert get_task_manager() is manager
        assert manager._instance_id != instance
        assert manager._materialization_restore_id == "restore-2"
        assert manager._periodic_recovery_task is scanner
        assert factory.call_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("provider_change", ["endpoint", "backend", "state_root", "home"])
async def test_live_provider_override_preserves_manager_and_worker_lease_identity(
    provider_factory, monkeypatch, tmp_path, provider_change
):
    provider, factory = provider_factory
    backend = "local" if provider_change in ("state_root", "home") else "hosted"
    monkeypatch.setenv("AGENTSERVER_TASKS_BACKEND", backend)
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://captured.example.invalid/project")
    monkeypatch.setenv("AGENTSERVER_STATE_ROOT", str(tmp_path / "captured"))
    if provider_change == "home":
        monkeypatch.setattr(Path, "home", classmethod(lambda cls: Path(os.environ["HOME"])))
        monkeypatch.setenv("HOME", str(tmp_path / "captured-home"))
        monkeypatch.setenv("AGENTSERVER_STATE_ROOT", "")
    key, value = {
        "endpoint": ("FOUNDRY_PROJECT_ENDPOINT", "https://other.example.invalid/project"),
        "backend": ("AGENTSERVER_TASKS_BACKEND", "local"),
        "state_root": ("AGENTSERVER_STATE_ROOT", str(tmp_path / "other-root")),
        "home": ("HOME", str(tmp_path / "other-home")),
    }[provider_change]
    original_value = os.environ[key]
    running, finish = asyncio.Event(), asyncio.Event()
    callbacks, renewal_identities, runs = [], [], []
    original_renewal = _manager.lease_renewal_loop
    app = host()

    async def renewal(*args, **kwargs):
        renewal_identities.append((kwargs["lease_owner"], kwargs["lease_instance_id"]))
        await original_renewal(*args, **kwargs)

    monkeypatch.setattr(_manager, "lease_renewal_loop", renewal)

    @task(name="live_provider_startup")
    async def startup(ctx: TaskContext[str]) -> str:
        running.set()
        await finish.wait()
        return ctx.input

    @app.after_restore_handler
    async def initialize(context):
        callbacks.append(context.restore_id)
        runs.append(await startup.start(task_id="live-provider-startup", input=context.session_id))
        await asyncio.wait_for(running.wait(), 2)

    async with app.router.lifespan_context(app), client(app) as http:
        try:
            assert (await http.post("/_agent/after-restore", json=payload())).status_code == 200
            manager = get_task_manager()
            identity = (manager._lease_owner, manager._instance_id)
            binding = manager._provider_binding
            worker = manager._active_tasks["live-provider-startup"]
            original_config = vars(app.config).copy()
            changed = payload(restore_id="restore-2")
            changed["session_context"]["session_env_overrides"][key] = value
            response = await http.post("/_agent/after-restore", json=changed)
            assert response.status_code == 500, response.text
            assert response.json()["error"]["code"] == "after_restore_failed"
            assert get_task_manager() is manager
            assert manager.provider is provider
            assert factory.call_count == 1
            assert callbacks == ["restore-1"]
            assert manager._materialization_restore_id == "restore-1"
            assert (manager._lease_owner, manager._instance_id) == identity
            assert renewal_identities == [identity]
            assert manager._provider_binding == binding
            assert manager._provider_configuration_matches()
            assert manager._active_tasks["live-provider-startup"] is worker
            assert not worker.execution_task.done()
            assert not worker.renewal_task.done()
            assert vars(app.config) == original_config
            assert os.environ[key] == original_value
            await manager._provider_update_locked(
                "live-provider-startup",
                TaskPatchRequest(
                    payload={"probe": "after-rejection"},
                    **manager._lease_ext_kwargs("live-provider-startup"),
                ),
            )
            stored = await provider.get("live-provider-startup")
            assert (stored.lease.owner, stored.lease.instance_id) == identity
            assert stored.payload["input"] == "session-1"
            assert stored.payload["probe"] == "after-rejection"
        finally:
            finish.set()
            await asyncio.wait_for(asyncio.gather(*(run.result() for run in runs), return_exceptions=True), 2)


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["exception", "cancel"])
@pytest.mark.parametrize("api", ["handle", "run"])
@pytest.mark.parametrize("kind", ["one-shot", "multi-turn"])
async def test_failed_restore_before_handler_defers_accepted_callers(provider_factory, monkeypatch, failure, api, kind):
    provider, _ = provider_factory
    app = host()
    blocked, setup_cancelled, failing, recovered = (asyncio.Event() for _ in range(4))
    managers, waiters, observed = [], [], []
    original_read = TaskManager._provider_get_tracked
    decorate = task if kind == "one-shot" else multi_turn_task

    async def read(manager, task_id):
        active = manager._active_tasks.get(task_id)
        if managers and manager is managers[0] and active is not None:
            if active.execution_task is asyncio.current_task():
                blocked.set()
                try:
                    await asyncio.Event().wait()
                except asyncio.CancelledError:
                    setup_cancelled.set()
                    raise
        return await original_read(manager, task_id)

    monkeypatch.setattr(TaskManager, "_provider_get_tracked", read)

    @decorate(name="initial_setup_rollback")
    async def startup(ctx: TaskContext[str]) -> str:
        observed.append((ctx.input, ctx.entry_mode))
        recovered.set()
        return ctx.input

    @app.after_restore_handler
    async def initialize(context):
        managers.append(get_task_manager())
        if len(managers) != 1:
            return
        if api == "handle":
            run = await startup.start(task_id="initial-setup", input=context.session_id)
            waiters.append(asyncio.create_task(run.result()))
        else:
            waiters.append(asyncio.create_task(startup.run(task_id="initial-setup", input=context.session_id)))
        await asyncio.wait_for(blocked.wait(), 2)
        failing.set()
        if failure == "exception":
            raise RuntimeError("Fail restore before the accepted task enters its handler")
        await asyncio.Event().wait()

    async with app.router.lifespan_context(app), client(app) as http:
        request = asyncio.create_task(http.post("/_agent/after-restore", json=payload()))
        try:
            await asyncio.wait_for(failing.wait(), 2)
            if failure == "cancel":
                request.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await request
            else:
                assert (await request).status_code == 500
            assert setup_cancelled.is_set()
            assert not managers[0]._has_live_workers
            assert observed == []
            with pytest.raises(TaskDeferred):
                await asyncio.wait_for(waiters[0], 2)
            stored = await provider.get("initial-setup")
            assert stored.status == "in_progress"
            assert stored.payload["input"] == "session-1"
            assert datetime.fromisoformat(stored.lease.expires_at) <= datetime.now(timezone.utc)
            response = await http.post("/_agent/after-restore", json=payload())
            assert response.status_code == 200, response.text
            await asyncio.wait_for(recovered.wait(), 2)
            assert managers[0] is not managers[1]
            assert observed == [("session-1", "recovered")]
            active = managers[1]._active_tasks.get("initial-setup")
            if active is not None:
                await asyncio.wait_for(asyncio.shield(active.execution_task), 2)
        finally:
            if not request.done():
                request.cancel()
            for waiter in waiters:
                if not waiter.done():
                    waiter.cancel()
            await asyncio.gather(request, *waiters, return_exceptions=True)


@pytest.mark.asyncio
@pytest.mark.parametrize("boundary", ["final-patch", "watchdog"])
async def test_shutdown_after_steering_promotion_does_not_dispatch_handler(provider_factory, monkeypatch, boundary):
    provider, _ = provider_factory
    manager = TaskManager(config=host().config, provider=provider, shutdown_grace_seconds=1)
    _manager.set_task_manager(manager)
    running, finish_turn, blocked, release = (asyncio.Event() for _ in range(4))
    observed = []
    original_update = manager._provider_update_locked
    original_watchdog = manager._spawn_watchdog_for_turn

    async def update(task_id, patch):
        steering = (patch.payload or {}).get("steering", {})
        if (
            boundary == "final-patch"
            and steering.get("drain_in_progress") is False
            and (patch.payload or {}).get("input") == "next"
        ):
            blocked.set()
            await release.wait()
        return await original_update(task_id, patch)

    async def watchdog(*, task_id, opts, ctx):
        if boundary == "watchdog" and ctx.is_steered_turn:
            blocked.set()
            await release.wait()
        await original_watchdog(task_id=task_id, opts=opts, ctx=ctx)

    monkeypatch.setattr(manager, "_provider_update_locked", update)
    monkeypatch.setattr(manager, "_spawn_watchdog_for_turn", watchdog)

    @multi_turn_task(name="steering_dispatch_boundary", steerable=True)
    async def step(ctx: TaskContext[str]) -> str:
        observed.append(ctx.input)
        if ctx.input == "first":
            running.set()
            await finish_turn.wait()
        return ctx.input

    shutdown = None
    try:
        first = await step.start(task_id="dispatch-boundary", input="first")
        await asyncio.wait_for(running.wait(), 2)
        queued = await step.start(task_id="dispatch-boundary", input="next")
        finish_turn.set()
        await asyncio.wait_for(blocked.wait(), 2)
        shutdown = asyncio.create_task(manager.shutdown(wait_for_workers=True, preserve_recoverable_tasks=True))
        await asyncio.wait_for(manager._shutdown_event.wait(), 2)
        release.set()
        await asyncio.wait_for(shutdown, 2)
        assert observed == ["first"]
        assert await first.result() == "first"
        with pytest.raises(TaskDeferred):
            await asyncio.wait_for(queued.result(), 2)
        stored = await provider.get("dispatch-boundary")
        assert stored.status == "in_progress"
        assert stored.payload["input"] == "next"
        assert stored.payload["steering"]["pending_inputs"] == []
        assert datetime.fromisoformat(stored.lease.expires_at) <= datetime.now(timezone.utc)
        assert not manager._pending_steering_futures
        assert not manager._active_generation_future
        assert not manager._has_live_workers
    finally:
        finish_turn.set()
        release.set()
        if shutdown is not None:
            await asyncio.gather(shutdown, return_exceptions=True)
        await manager.shutdown(wait_for_workers=True, preserve_recoverable_tasks=True)


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["exception", "cancel"])
@pytest.mark.parametrize("api", ["handle", "run"])
async def test_failed_restore_defers_queued_steering_callers_before_retry(provider_factory, monkeypatch, failure, api):
    provider, _ = provider_factory
    monkeypatch.setenv("AGENTSERVER_SHUTDOWN_GRACE_SECONDS", "0.5")
    app = host()
    running, queued, failing, recovered = (asyncio.Event() for _ in range(4))
    managers, waiters, observed = [], [], []
    original_update = provider.update

    async def update(task_id, patch):
        result = await original_update(task_id, patch)
        if (patch.payload or {}).get("steering", {}).get("pending_inputs"):
            queued.set()
        return result

    monkeypatch.setattr(provider, "update", update)

    @multi_turn_task(name="rollback_queued_caller", steerable=True)
    async def step(ctx: TaskContext[str]) -> str:
        observed.append(ctx.input)
        if ctx.input == "first":
            running.set()
            await ctx.shutdown.wait()
        else:
            recovered.set()
        return ctx.input

    @app.after_restore_handler
    async def initialize(context):
        managers.append(get_task_manager())
        if len(managers) != 1:
            return
        await step.start(task_id="queued-caller", input="first")
        await asyncio.wait_for(running.wait(), 2)
        if api == "handle":
            run = await step.start(task_id="queued-caller", input="next")
            waiters.append(asyncio.create_task(run.result()))
        else:
            waiters.append(asyncio.create_task(step.run(task_id="queued-caller", input="next")))
        await asyncio.wait_for(queued.wait(), 2)
        failing.set()
        if failure == "exception":
            raise RuntimeError("Fail restore after accepting a queued steering input")
        await asyncio.Event().wait()

    async with app.router.lifespan_context(app), client(app) as http:
        request = asyncio.create_task(http.post("/_agent/after-restore", json=payload()))
        try:
            await asyncio.wait_for(failing.wait(), 2)
            if failure == "cancel":
                request.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await request
            else:
                assert (await request).status_code == 500
            with pytest.raises(TaskDeferred):
                await asyncio.wait_for(waiters[0], 2)
            assert observed == ["first"]
            assert not managers[0]._pending_steering_futures
            assert not managers[0]._active_generation_future
            stored = await provider.get("queued-caller")
            assert stored.status == "in_progress"
            assert stored.payload["input"] == "next"
            assert datetime.fromisoformat(stored.lease.expires_at) <= datetime.now(timezone.utc)
            response = await http.post("/_agent/after-restore", json=payload())
            assert response.status_code == 200, response.text
            await asyncio.wait_for(recovered.wait(), 2)
            assert managers[0] is not managers[1]
            assert observed == ["first", "next"]
        finally:
            if not request.done():
                request.cancel()
            for waiter in waiters:
                if not waiter.done():
                    waiter.cancel()
            await asyncio.gather(request, *waiters, return_exceptions=True)


@pytest.mark.asyncio
@pytest.mark.parametrize("preserve", [False, True])
async def test_shutdown_settles_only_unfinished_steering_futures(provider_factory, preserve):
    provider, _ = provider_factory
    manager = TaskManager(config=host().config, provider=provider, shutdown_grace_seconds=0)
    queued = manager._register_steering_future("queued")
    completed = manager._register_steering_future("queued")
    completed.set_result("already completed")
    cancelled = manager._register_steering_future("queued")
    cancelled.cancel()
    promoted = asyncio.get_running_loop().create_future()
    manager._active_generation_future["promoted"] = promoted
    manager._active_generation_future["queued"] = queued
    await manager.shutdown(wait_for_workers=True, preserve_recoverable_tasks=preserve)
    for future in (queued, promoted):
        assert future.done()
        with pytest.raises(TaskDeferred):
            await future
    assert await completed == "already completed"
    assert cancelled.cancelled()
    assert not manager._pending_steering_futures
    assert not manager._active_generation_future


@pytest.mark.asyncio
@pytest.mark.parametrize("root", [None, ""])
@pytest.mark.parametrize("failure", ["exception", "cancel"])
@pytest.mark.parametrize("started", [False, True])
async def test_default_local_home_change_rebuilds_runtime(monkeypatch, tmp_path, root, failure, started):
    # Exercise Linux HOME semantics on Windows as well.
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: Path(os.environ["HOME"])))
    monkeypatch.setenv("HOME", str(tmp_path / "captured-home"))
    monkeypatch.setenv("AGENTSERVER_TASKS_BACKEND", "local")
    if root is None:
        monkeypatch.delenv("AGENTSERVER_STATE_ROOT", raising=False)
    else:
        monkeypatch.setenv("AGENTSERVER_STATE_ROOT", root)
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_ID", "session-1")
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_GUID", "a" * 32)
    app = host()
    running, finish, failing = asyncio.Event(), asyncio.Event(), asyncio.Event()
    managers = []

    @task(name="home_root_startup")
    async def startup(ctx: TaskContext[str]) -> str:
        running.set()
        await finish.wait()
        return ctx.input

    @app.after_restore_handler
    async def initialize(context):
        managers.append(get_task_manager())
        if len(managers) == 1:
            if started:
                await startup.start(task_id="home-startup", input=context.session_id)
                await asyncio.wait_for(running.wait(), 2)
            failing.set()
            if failure == "exception":
                raise RuntimeError("Fail the overridden HOME startup")
            await asyncio.Event().wait()
        assert get_task_manager().provider._base_dir == tmp_path / "captured-home" / ".agentserver" / "tasks"

    first = payload()
    first["session_context"]["session_env_overrides"]["HOME"] = str(tmp_path / "overridden-home")
    async with app.router.lifespan_context(app), client(app) as http:
        request = asyncio.create_task(http.post("/_agent/after-restore", json=first))
        try:
            await asyncio.wait_for(failing.wait(), 2)
            if failure == "cancel":
                request.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await request
            else:
                assert (await request).status_code == 500
            response = await http.post("/_agent/after-restore", json=payload())
            assert response.status_code == 200, response.text
            assert managers[0] is not managers[1]
            assert not managers[0]._has_live_workers
            assert managers[0]._shutdown_event.is_set()
            if started:
                stored = await managers[0].provider.get("home-startup")
                assert stored.status == "in_progress"
                assert stored.payload["input"] == "session-1"
                assert datetime.fromisoformat(stored.lease.expires_at) <= datetime.now(timezone.utc)
        finally:
            finish.set()
            if not request.done():
                request.cancel()
            await asyncio.gather(request, return_exceptions=True)


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["exception", "cancel"])
async def test_child_submission_from_cancelled_finally_cannot_escape_rollback(provider_factory, failure):
    provider, _ = provider_factory
    app = host()
    running, finish = asyncio.Event(), asyncio.Event()
    child_ran = asyncio.Event()
    runs, managers = [], []
    callbacks = 0

    @task(name="shutdown_child")
    async def child(ctx: TaskContext[str]) -> str:
        child_ran.set()
        await finish.wait()
        return ctx.input

    @task(name="shutdown_parent")
    async def parent(ctx: TaskContext[str]) -> str:
        running.set()
        try:
            await finish.wait()
            return ctx.input
        finally:
            if ctx.entry_mode == "fresh":
                await child.start(task_id="escaping-child", input="must not run")

    @app.after_restore_handler
    async def initialize(context):
        nonlocal callbacks
        callbacks += 1
        managers.append(get_task_manager())
        if callbacks == 1:
            runs.append(await parent.start(task_id="shutdown-parent", input=context.session_id))
            await asyncio.wait_for(running.wait(), 2)
            if failure == "exception":
                raise RuntimeError("Trigger parent cancellation cleanup")
            await asyncio.Event().wait()
        else:
            runs.append(await parent.get_active_run("shutdown-parent"))

    async with app.router.lifespan_context(app), client(app) as http:
        request = asyncio.create_task(http.post("/_agent/after-restore", json=payload()))
        try:
            await asyncio.wait_for(running.wait(), 2)
            if failure == "cancel":
                request.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await request
            else:
                assert (await request).status_code == 500
            with pytest.raises(TaskDeferred):
                await runs[0].result()
            assert not child_ran.is_set()
            assert await provider.get("escaping-child") is None
            assert not managers[0]._has_live_workers
            stored = await provider.get("shutdown-parent")
            assert stored.status == "in_progress"
            assert stored.payload["input"] == "session-1"
            assert datetime.fromisoformat(stored.lease.expires_at) <= datetime.now(timezone.utc)
            running.clear()
            assert (await http.post("/_agent/after-restore", json=payload())).status_code == 200
            await asyncio.wait_for(running.wait(), 2)
            assert managers[0] is not managers[1]
            assert not child_ran.is_set()
        finally:
            finish.set()
            if not request.done():
                request.cancel()
            await asyncio.gather(request, return_exceptions=True)
            for manager in managers:
                workers = set(manager._owned_workers)
                for worker in workers:
                    if not worker.done():
                        worker.cancel()
                await asyncio.gather(*workers, return_exceptions=True)


@pytest.mark.asyncio
@pytest.mark.parametrize("api", ["task", "manager"])
async def test_shutdown_waits_for_accepted_submission_before_snapshot(provider_factory, api):
    provider, _ = provider_factory
    written, release = asyncio.Event(), asyncio.Event()
    original_create = provider.create
    app = host()
    manager = TaskManager(config=app.config, provider=provider, shutdown_grace_seconds=0)
    _manager.set_task_manager(manager)

    @task(name="inflight_submission")
    async def startup(ctx: TaskContext[str]) -> str:
        await ctx.shutdown.wait()
        raise asyncio.CancelledError

    async def create(request):
        result = await original_create(request)
        written.set()
        await release.wait()
        return result

    provider.create = create
    if api == "task":
        operation = startup.start(task_id="inflight-startup", input="saved")
    else:
        operation = manager.create_and_start(
            fn=startup._fn,
            fn_name=startup.name,
            task_id="inflight-startup",
            input_val="saved",
            input_type=str,
            session_id=None,
            title="inflight",
            tags={},
            opts=startup._opts,
        )
    submission = asyncio.create_task(operation)
    shutdown = None
    try:
        await asyncio.wait_for(written.wait(), 2)
        shutdown = asyncio.create_task(manager.shutdown(wait_for_workers=True, preserve_recoverable_tasks=True))
        await asyncio.wait_for(manager._shutdown_event.wait(), 2)
        await asyncio.sleep(0)
        assert not shutdown.done()
        with pytest.raises(RuntimeError, match="shutting down"):
            await startup.start(task_id="rejected-startup", input="must not run")
        assert await provider.get("rejected-startup") is None
        release.set()
        run = await asyncio.wait_for(submission, 2)
        await asyncio.wait_for(shutdown, 2)
        with pytest.raises(TaskDeferred):
            await run.result()
        assert not manager._has_live_workers
        stored = await provider.get("inflight-startup")
        assert stored.status == "in_progress"
        assert stored.payload["input"] == "saved"
        assert datetime.fromisoformat(stored.lease.expires_at) <= datetime.now(timezone.utc)
    finally:
        release.set()
        await asyncio.gather(submission, return_exceptions=True)
        if shutdown is not None:
            await asyncio.gather(shutdown, return_exceptions=True)
        await manager.shutdown(wait_for_workers=True, preserve_recoverable_tasks=True)


@pytest.mark.asyncio
async def test_child_task_does_not_inherit_admission_from_its_producer(provider_factory):
    provider, _ = provider_factory
    manager = TaskManager(config=host().config, provider=provider, shutdown_grace_seconds=0)
    _manager.set_task_manager(manager)

    @task(name="admission_inheritance")
    async def startup(ctx: TaskContext[str]) -> str:
        pytest.fail("A new child task must acquire its own admission")

    with manager._task_admission():
        shutdown = asyncio.create_task(manager.shutdown(wait_for_workers=True, preserve_recoverable_tasks=True))
        await asyncio.wait_for(manager._shutdown_event.wait(), 2)
        submission = asyncio.create_task(startup.start(task_id="unaccepted-child", input="denied"))
        with pytest.raises(RuntimeError, match="shutting down"):
            await submission
        assert not shutdown.done()
    await asyncio.wait_for(shutdown, 2)
    assert await provider.get("unaccepted-child") is None
    assert not manager._active_admissions


@pytest.mark.asyncio
async def test_shutdown_does_not_wait_for_a_run_callers_result(provider_factory):
    provider, _ = provider_factory
    manager = TaskManager(config=host().config, provider=provider, shutdown_grace_seconds=0)
    _manager.set_task_manager(manager)
    running = asyncio.Event()

    @task(name="admission_run_wait")
    async def startup(ctx: TaskContext[str]) -> str:
        running.set()
        await ctx.shutdown.wait()
        raise asyncio.CancelledError

    request = asyncio.create_task(startup.run(task_id="run-wait", input="saved"))
    await asyncio.wait_for(running.wait(), 2)
    await asyncio.wait_for(manager.shutdown(wait_for_workers=True, preserve_recoverable_tasks=True), 2)
    with pytest.raises(TaskDeferred):
        await request
    assert not manager._active_admissions
    stored = await provider.get("run-wait")
    assert stored.status == "in_progress"
    assert stored.payload["input"] == "saved"


@pytest.mark.asyncio
async def test_rollback_waits_for_inflight_submission_before_restoring_config(provider_factory, monkeypatch):
    provider, _ = provider_factory
    original_create = provider.create
    written, release = asyncio.Event(), asyncio.Event()
    app = host()
    submissions, managers = [], []

    @task(name="rollback_inflight")
    async def startup(ctx: TaskContext[str]) -> str:
        await ctx.shutdown.wait()
        raise asyncio.CancelledError

    async def create(request):
        result = await original_create(request)
        written.set()
        await release.wait()
        return result

    monkeypatch.setattr(provider, "create", create)

    @app.after_restore_handler
    async def initialize(context):
        managers.append(get_task_manager())
        submissions.append(asyncio.create_task(startup.start(task_id="rollback-inflight", input=context.session_id)))
        await asyncio.wait_for(written.wait(), 2)
        raise RuntimeError("Fail while a submission is still settling")

    async with app.router.lifespan_context(app), client(app) as http:
        request = asyncio.create_task(http.post("/_agent/after-restore", json=payload()))
        try:
            await asyncio.wait_for(written.wait(), 2)
            await asyncio.wait_for(managers[0]._shutdown_event.wait(), 2)
            assert not request.done()
            assert app.config.session_id == "session-1"
            release.set()
            assert (await asyncio.wait_for(request, 2)).status_code == 500
            run = await asyncio.wait_for(submissions[0], 2)
            with pytest.raises(TaskDeferred):
                await run.result()
            assert app.config.session_id == ""
            assert not managers[0]._has_live_workers
            stored = await provider.get("rollback-inflight")
            assert stored.payload["input"] == "session-1"
            assert datetime.fromisoformat(stored.lease.expires_at) <= datetime.now(timezone.utc)
        finally:
            release.set()
            if not request.done():
                request.cancel()
            await asyncio.gather(request, *submissions, return_exceptions=True)
