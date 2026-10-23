# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Task creation provenance survives newer workers and input replacement."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from azure.ai.agentserver.core.tasks import RetryPolicy, TaskContext, multi_turn_task, task
from azure.ai.agentserver.core.tasks import _decorator, _manager
from azure.ai.agentserver.core.tasks._lease import derive_lease_owner
from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
from azure.ai.agentserver.core.tasks._manager import TaskManager, _SCHEMA_VERSION, _SCHEMA_VERSION_KEY
from azure.ai.agentserver.core.tasks._models import TaskCreateRequest, TaskInfo


def _config(version: str):
    return SimpleNamespace(
        agent_name="origin-agent", session_id="origin-session", agent_version=version, is_hosted=False
    )


@pytest.fixture(autouse=True)
def _isolated_registration(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(_decorator, "_REGISTERED_DESCRIPTORS", [])
    monkeypatch.setattr(_manager, "_manager", None)


async def _suspended(provider: LocalFileTaskProvider, task_id: str) -> TaskInfo:
    async def wait():
        while True:
            info = await provider.get(task_id)
            if info is not None and info.status == "suspended":
                return info
            await asyncio.sleep(0.01)

    return await asyncio.wait_for(wait(), timeout=5)


def test_task_info_round_trips_service_version_and_legacy_absence() -> None:
    wire = {"id": "task", "agent_name": "agent", "session_id": "session", "status": "pending"}
    assert TaskInfo.from_dict(wire).origin_agent_version is None
    wire["origin_agent_version"] = "1"
    info = TaskInfo.from_dict(wire)
    assert info.origin_agent_version == "1"
    assert info.to_dict()["origin_agent_version"] == "1"


def test_task_info_rejects_non_string_origin() -> None:
    with pytest.raises(TypeError, match="origin_agent_version"):
        TaskInfo.from_dict({"id": "task", "origin_agent_version": 1})


def test_context_origin_is_read_only_and_does_not_infer_current_version(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FOUNDRY_AGENT_VERSION", "2")
    context = TaskContext(task_id="task", session_id="session", input={}, origin_agent_version="1")
    assert context.origin_agent_version == "1"
    with pytest.raises(AttributeError):
        context.origin_agent_version = "2"
    assert TaskContext(task_id="legacy", session_id="session", input={}).origin_agent_version is None


@pytest.mark.parametrize("version", ["1", ""])
def test_default_local_backend_captures_configured_creation_version(tmp_path, monkeypatch, version: str) -> None:
    monkeypatch.setenv("AGENTSERVER_TASKS_BACKEND", "local")
    monkeypatch.setenv("AGENTSERVER_STATE_ROOT", str(tmp_path))
    provider = TaskManager._create_provider(_config(version))
    assert isinstance(provider, LocalFileTaskProvider)
    assert provider._origin_agent_version == (version or None)


@pytest.mark.parametrize("origin", ["1", None])
@pytest.mark.asyncio
async def test_resume_keeps_origin_and_new_task_uses_new_worker_version(tmp_path, origin: str | None) -> None:
    observed = []

    @multi_turn_task(name="versioned-conversation")
    async def conversation(ctx: TaskContext[str]) -> str | None:
        observed.append((ctx.input, ctx.entry_mode, ctx.origin_agent_version))
        return ctx.origin_agent_version

    first_provider = LocalFileTaskProvider(tmp_path, origin_agent_version=origin)
    first = TaskManager(_config("1"), provider=first_provider)
    _manager.set_task_manager(first)
    await first.startup()
    try:
        run = await conversation.start(task_id="existing", input="first")
        assert await asyncio.wait_for(run.result(), timeout=5) == origin
        assert (await _suspended(first_provider, "existing")).origin_agent_version == origin
    finally:
        await first.shutdown()
    second_provider = LocalFileTaskProvider(tmp_path, origin_agent_version="2")
    second = TaskManager(_config("2"), provider=second_provider)
    _manager.set_task_manager(second)
    await second.startup()
    try:
        assert len(observed) == 1
        resumed = await conversation.start(task_id="existing", input="second")
        assert await asyncio.wait_for(resumed.result(), timeout=5) == origin
        assert (await _suspended(second_provider, "existing")).origin_agent_version == origin
        fresh = await conversation.start(task_id="new", input="new")
        assert await asyncio.wait_for(fresh.result(), timeout=5) == "2"
        assert (await _suspended(second_provider, "new")).origin_agent_version == "2"
        assert observed == [("first", "fresh", origin), ("second", "resumed", origin), ("new", "fresh", "2")]
    finally:
        await second.shutdown()


async def _interrupted_task(provider: LocalFileTaskProvider, name: str) -> None:
    info = await provider.create(
        TaskCreateRequest(
            id="interrupted",
            agent_name="origin-agent",
            session_id="origin-session",
            status="in_progress",
            title="Interrupted versioned task",
            payload={"input": "first", _SCHEMA_VERSION_KEY: _SCHEMA_VERSION},
            tags={"task_name": name},
            source=TaskManager._build_source(name),
            lease_owner=derive_lease_owner("origin-agent", "origin-session"),
            lease_instance_id="previous-worker",
            lease_duration_seconds=60,
        )
    )
    assert info.lease is not None
    info.lease.expires_at = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
    provider._write_task(info)


@pytest.mark.parametrize("origin", ["1", None])
@pytest.mark.parametrize("recovery_path", ["startup", "inline", "periodic"])
@pytest.mark.asyncio
async def test_recovery_reads_persisted_origin_not_new_worker(
    tmp_path, monkeypatch: pytest.MonkeyPatch, origin: str | None, recovery_path: str
) -> None:
    observed = []

    @multi_turn_task(name="versioned-recovery")
    async def recovered(ctx: TaskContext[str]) -> str | None:
        observed.append((ctx.entry_mode, ctx.origin_agent_version))
        return ctx.origin_agent_version

    creator = LocalFileTaskProvider(tmp_path, origin_agent_version=origin)
    current_provider = LocalFileTaskProvider(tmp_path, origin_agent_version="2")
    current = TaskManager(_config("2"), provider=current_provider)
    _manager.set_task_manager(current)
    if recovery_path == "periodic":
        monkeypatch.setattr(_manager, "_PERIODIC_RECOVERY_INTERVAL_SECONDS", 0.01)
    if recovery_path == "startup":
        await _interrupted_task(creator, recovered.name)
    await current.startup()
    try:
        if recovery_path != "startup":
            await _interrupted_task(creator, recovered.name)
        if recovery_path == "inline":
            run = await current.get_active_run("interrupted")
            assert run is not None
            assert await asyncio.wait_for(run.result(), timeout=5) == origin
        record = await _suspended(current_provider, "interrupted")
        assert observed == [("recovered", origin)]
        assert record.origin_agent_version == origin
    finally:
        await current.shutdown()


@pytest.mark.asyncio
async def test_steered_turn_keeps_recovered_task_origin(tmp_path) -> None:
    first_entered = asyncio.Event()
    observed = []

    @multi_turn_task(name="versioned-steering", steerable=True)
    async def conversation(ctx: TaskContext[str]) -> str | None:
        observed.append((ctx.input, ctx.entry_mode, ctx.origin_agent_version))
        if ctx.input == "first":
            first_entered.set()
            await ctx.cancel.wait()
            return None
        return ctx.origin_agent_version

    creator = LocalFileTaskProvider(tmp_path, origin_agent_version="1")
    await _interrupted_task(creator, conversation.name)
    provider = LocalFileTaskProvider(tmp_path, origin_agent_version="2")
    manager = TaskManager(_config("2"), provider=provider, shutdown_grace_seconds=0.1)
    _manager.set_task_manager(manager)
    await manager.startup()
    try:
        await asyncio.wait_for(first_entered.wait(), timeout=5)
        queued = await conversation.start(task_id="interrupted", input="second")
        assert await asyncio.wait_for(queued.result(), timeout=5) == "1"
        assert (await _suspended(provider, "interrupted")).origin_agent_version == "1"
        assert observed == [("first", "recovered", "1"), ("second", "resumed", "1")]
    finally:
        await manager.shutdown()


@pytest.mark.asyncio
async def test_retry_keeps_provider_origin_instead_of_worker_configuration(tmp_path) -> None:
    observed = []

    @task(name="versioned-retry", retry=RetryPolicy(initial_delay=0, max_delay=0, max_attempts=2, jitter=False))
    async def work(ctx: TaskContext[str]) -> str | None:
        observed.append((ctx.retry_attempt, ctx.origin_agent_version))
        if ctx.retry_attempt == 0:
            raise ValueError("retry once")
        return ctx.origin_agent_version

    provider = LocalFileTaskProvider(tmp_path, origin_agent_version="1")
    manager = TaskManager(_config("2"), provider=provider)
    _manager.set_task_manager(manager)
    await manager.startup()
    try:
        run = await work.start(task_id="retry", input="input")
        assert await asyncio.wait_for(run.result(), timeout=5) == "1"
        assert observed == [(0, "1"), (1, "1")]
    finally:
        await manager.shutdown()
