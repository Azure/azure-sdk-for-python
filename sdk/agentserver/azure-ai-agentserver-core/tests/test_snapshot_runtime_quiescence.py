# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Rollback must retain one identity and stop all task admission before quiescence."""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from pathlib import Path

import pytest

from azure.ai.agentserver.core.tasks import TaskContext, task
from azure.ai.agentserver.core.tasks import _manager
from azure.ai.agentserver.core.tasks._exceptions import TaskDeferred
from azure.ai.agentserver.core.tasks._lease import derive_lease_owner
from azure.ai.agentserver.core.tasks._manager import TaskManager, get_task_manager
from test_snapshot_task_activation import client, host, isolate_runtime, payload, provider_factory


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
