# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Recovery of admitted input after an interrupted completion-to-drain handoff."""

import asyncio
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from pydantic import BaseModel

from azure.ai.agentserver.core.tasks import RetryPolicy, TaskConflictError, TaskContext, multi_turn_task
from azure.ai.agentserver.core.tasks import _manager as manager_module
from azure.ai.agentserver.core.tasks._attachments import (
    _FUNCTION_INPUT_KEY,
    _INPUT_THRESHOLD_BYTES,
    _is_ref,
    _make_ref,
    _read_input_value,
)
from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
from azure.ai.agentserver.core.tasks._manager import TaskManager, set_task_manager
from azure.ai.agentserver.core.tasks._models import TaskCreateRequest, TaskPatchRequest


class TurnInput(BaseModel):
    value: int
    text: str = ""


def _manager(provider):
    config = SimpleNamespace(
        agent_name="handoff-agent",
        session_id="handoff-session",
        agent_version="1",
        is_hosted=False,
    )
    return TaskManager(config=config, provider=provider, shutdown_grace_seconds=1)


async def _seed(
    provider, *, name="handoff", pending=None, attachments=None, reason="run_completion", source_type="agentserver.task"
):
    info = await provider.create(
        TaskCreateRequest(
            id="chain",
            title="handoff",
            agent_name="handoff-agent",
            session_id="handoff-session",
            status="in_progress",
            lease_owner="handoff-agent|session:handoff-session",
            lease_instance_id="previous-worker",
            lease_duration_seconds=60,
            source={"type": source_type, "name": name},
            payload={
                "schema_version": "1",
                "input": None,
                "retry_attempt": None,
                "steering": {
                    "pending_inputs": pending if pending is not None else [{"value": 2}],
                    "active_input": None,
                    "cancel_requested": True,
                },
            },
            attachments=attachments,
        )
    )
    return await provider.update(
        "chain", TaskPatchRequest(status="suspended", suspension_reason=reason, if_match=info.etag)
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("replacement", [False, True], ids=["periodic-scan", "replacement-startup"])
async def test_drain_failure_does_not_strand_input(tmp_path, monkeypatch, replacement):
    started, finish, processed = (asyncio.Event() for _ in range(3))
    observed = []

    @multi_turn_task(name="handoff", steerable=True)
    async def worker(ctx: TaskContext[TurnInput]) -> int:
        observed.append((ctx.input.value, ctx.entry_mode, ctx.is_steered_turn))
        if ctx.input.value == 1:
            started.set()
            await finish.wait()
        else:
            processed.set()
        return ctx.input.value

    provider = LocalFileTaskProvider(tmp_path)
    manager = _manager(provider)
    set_task_manager(manager)
    try:
        await manager.startup()
        drain = manager._try_drain_steering
        monkeypatch.setattr(manager, "_try_drain_steering", AsyncMock(side_effect=OSError("handoff unavailable")))
        first = await worker.start(task_id="chain", input=TurnInput(value=1))
        await asyncio.wait_for(started.wait(), 5)
        queued = await worker.start(task_id="chain", input=TurnInput(value=2))
        execution = manager._active_tasks["chain"].execution_task
        finish.set()
        assert await asyncio.wait_for(first.result(), 5) == 1
        await asyncio.wait_for(execution, 5)
        saved = await provider.get("chain")
        assert saved.status == "suspended"
        assert saved.lease is None
        assert saved.payload["steering"]["pending_inputs"] == [{"value": 2, "text": ""}]
        if replacement:
            await manager.shutdown()
            manager = _manager(provider)
            set_task_manager(manager)
            await manager.startup()
        else:
            monkeypatch.setattr(manager, "_try_drain_steering", drain)
            await manager._recover_stale_tasks()
            assert await asyncio.wait_for(queued.result(), 5) == 2
        await asyncio.wait_for(processed.wait(), 5)
        assert observed == [(1, "fresh", False), (2, "resumed", True)]
    finally:
        await manager.shutdown()
        set_task_manager(None)


@pytest.mark.asyncio
@pytest.mark.parametrize("size", [32 * 1024, _INPUT_THRESHOLD_BYTES + 1024])
async def test_crash_boundary_recovers_fifo_and_attachment_backed_input(tmp_path, size):
    started, finish, done = (asyncio.Event() for _ in range(3))
    large = "x" * size
    observed = []

    @multi_turn_task(name="handoff", steerable=True)
    async def worker(ctx: TaskContext[TurnInput]) -> int:
        observed.append((ctx.input, ctx.entry_mode, ctx.is_steered_turn, ctx.pending_input_count))
        if ctx.input.value == 2:
            started.set()
            await finish.wait()
        else:
            done.set()
        return ctx.input.value

    provider = LocalFileTaskProvider(tmp_path)
    # Exact durable state left by a crash after successful suspend, before drain.
    await _seed(
        provider,
        pending=[_make_ref("steering_input_0", {"value": 2, "text": large}), {"value": 3}],
        attachments={"steering_input_0": {"value": 2, "text": large}},
    )
    manager = _manager(provider)
    set_task_manager(manager)
    try:
        await manager.startup()
        await asyncio.wait_for(started.wait(), 5)
        saved = await provider.get("chain")
        assert saved.status == "in_progress"
        assert saved.lease.owner == manager._lease_owner
        assert saved.lease.instance_id == manager._instance_id
        assert saved.payload["steering"]["pending_inputs"] == [{"value": 3}]
        assert "steering_input_0" not in (saved.attachments or {})
        assert _is_ref(saved.payload["input"]) == (size > _INPUT_THRESHOLD_BYTES)
        assert _read_input_value(saved.payload["input"], saved.attachments) == {"value": 2, "text": large}
        assert (_FUNCTION_INPUT_KEY in (saved.attachments or {})) == (size > _INPUT_THRESHOLD_BYTES)
        finish.set()
        await asyncio.wait_for(done.wait(), 5)
        assert observed == [
            (TurnInput(value=2, text=large), "resumed", True, 1),
            (TurnInput(value=3), "resumed", True, 0),
        ]
    finally:
        finish.set()
        await manager.shutdown()
        set_task_manager(None)


@pytest.mark.asyncio
async def test_queued_recovery_preserves_retry_policy_for_each_turn(tmp_path):
    started, finish = asyncio.Event(), asyncio.Event()
    observed = []

    @multi_turn_task(
        name="handoff",
        steerable=True,
        retry=RetryPolicy.fixed_delay(delay=timedelta(0), max_attempts=2),
    )
    async def worker(ctx: TaskContext[TurnInput]) -> int:
        observed.append((ctx.input.value, ctx.retry_attempt))
        if ctx.input.value == 2 and ctx.retry_attempt == 0:
            started.set()
            await finish.wait()
        if ctx.retry_attempt == 0:
            raise OSError("transient turn failure")
        return ctx.input.value

    provider = LocalFileTaskProvider(tmp_path)
    await _seed(provider, pending=[{"value": 2}, {"value": 3}])
    manager = _manager(provider)
    set_task_manager(manager)
    try:
        await manager.startup()
        await asyncio.wait_for(started.wait(), 5)
        execution = manager._active_tasks["chain"].execution_task
        finish.set()
        await asyncio.wait_for(execution, 5)
        assert observed == [(2, 0), (2, 1), (3, 0), (3, 1)]
        saved = await provider.get("chain")
        assert saved.status == "suspended"
        assert saved.error is None
        assert saved.payload["retry_attempt"] is None
        assert saved.payload["steering"]["pending_inputs"] == []
    finally:
        finish.set()
        await manager.shutdown()
        set_task_manager(None)


@pytest.mark.asyncio
@pytest.mark.parametrize("claim_timing", ["before-live-read", "conflict-retry"])
@pytest.mark.parametrize("recovery_progress", ["running", "suspended"])
async def test_live_drain_does_not_steal_recovered_handoff(tmp_path, monkeypatch, claim_timing, recovery_progress):
    first_started, finish_first = asyncio.Event(), asyncio.Event()
    drain_paused, resume_drain = asyncio.Event(), asyncio.Event()
    second_started, finish_second = asyncio.Event(), asyncio.Event()
    recovery_paused, resume_recovery = asyncio.Event(), asyncio.Event()
    observed = []
    provider = LocalFileTaskProvider(tmp_path)
    original, recovery = _manager(provider), _manager(provider)
    runs = []
    conflict_injected = False
    # Turn timestamps may be identical; ownership must not depend on the clock.
    now = manager_module._utc_now_iso()
    monkeypatch.setattr(manager_module, "_utc_now_iso", lambda: now)

    @multi_turn_task(name="handoff", steerable=True)
    async def worker(ctx: TaskContext[dict]) -> int:
        value = ctx.input["value"]
        owner = "original" if ctx.shutdown is original._shutdown_event else "recovery"
        observed.append((owner, value))
        if value == 1:
            first_started.set()
            await finish_first.wait()
        elif value == 2:
            second_started.set()
            await finish_second.wait()
        return value

    live_drain = original._try_drain_steering

    async def paused_live_drain(**kwargs):
        drain_paused.set()
        await resume_drain.wait()
        return await live_drain(**kwargs)

    recovery_drain = recovery._try_drain_steering

    async def paused_recovery_drain(**kwargs):
        recovery_paused.set()
        await resume_recovery.wait()
        return await recovery_drain(**kwargs)

    monkeypatch.setattr(original, "_try_drain_steering", paused_live_drain)
    monkeypatch.setattr(recovery, "_try_drain_steering", paused_recovery_drain)
    recovery_execution = None

    async def claim_recovery():
        nonlocal recovery_execution
        await recovery.startup()
        await asyncio.wait_for(second_started.wait(), 5)
        recovery_execution = recovery._active_tasks["chain"].execution_task
        if recovery_progress == "suspended":
            finish_second.set()
            await asyncio.wait_for(recovery_paused.wait(), 5)

    update = provider.update

    async def race_claim(task_id, patch):
        nonlocal conflict_injected
        active_input = ((patch.payload or {}).get("steering") or {}).get("active_input")
        if (
            claim_timing == "conflict-retry"
            and not conflict_injected
            and patch.lease_instance_id == original._instance_id
            and active_input == {"value": 2}
        ):
            conflict_injected = True
            await claim_recovery()
        return await update(task_id, patch)

    monkeypatch.setattr(provider, "update", race_claim)
    set_task_manager(original)
    try:
        await original.startup()
        first = await worker.start(task_id="chain", input={"value": 1})
        runs.append(first)
        await asyncio.wait_for(first_started.wait(), 5)
        second = await worker.start(task_id="chain", input={"value": 2})
        third = await worker.start(task_id="chain", input={"value": 3})
        runs.extend([second, third])
        original_execution = original._active_tasks["chain"].execution_task
        finish_first.set()
        assert await asyncio.wait_for(first.result(), 5) == 1
        await asyncio.wait_for(drain_paused.wait(), 5)
        set_task_manager(recovery)
        if claim_timing == "before-live-read":
            await claim_recovery()
        resume_drain.set()
        await asyncio.wait_for(original_execution, 5)

        assert observed == [("original", 1), ("recovery", 2)]
        assert conflict_injected == (claim_timing == "conflict-retry")
        saved = await provider.get("chain")
        expected_status = "in_progress" if recovery_progress == "running" else "suspended"
        assert saved.status == expected_status
        assert saved.payload["steering"]["pending_inputs"] == [{"value": 3}]
        if recovery_progress == "running":
            assert saved.payload["input"] == {"value": 2}
            assert saved.lease.instance_id == recovery._instance_id
        else:
            assert saved.payload["input"] is None
            assert saved.lease is None
        for run in (second, third):
            with pytest.raises(TaskConflictError) as error:
                await asyncio.wait_for(run.result(), 5)
            assert error.value.current_status == expected_status

        finish_second.set()
        resume_recovery.set()
        assert recovery_execution is not None
        await asyncio.wait_for(recovery_execution, 5)
        assert observed == [("original", 1), ("recovery", 2), ("recovery", 3)]
        saved = await provider.get("chain")
        assert saved.status == "suspended"
        assert saved.payload["steering"]["pending_inputs"] == []
    finally:
        finish_first.set()
        resume_drain.set()
        finish_second.set()
        resume_recovery.set()
        await asyncio.gather(original.shutdown(), recovery.shutdown())
        await asyncio.gather(
            *(asyncio.wait_for(run.result(), 1) for run in runs),
            return_exceptions=True,
        )
        set_task_manager(None)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "excluded",
    ["empty", "waiting", "unknown-name", "disabled", "non-steerable", "host-unbound", "foreign", "legacy"],
)
async def test_queued_recovery_preserves_eligibility_fences(tmp_path, excluded):
    invoked = asyncio.Event()

    @multi_turn_task(name="handoff", steerable=excluded != "non-steerable")
    async def worker(ctx: TaskContext[dict]) -> dict:
        invoked.set()
        return ctx.input

    provider = LocalFileTaskProvider(tmp_path)
    saved = await _seed(
        provider,
        name="unregistered" if excluded == "unknown-name" else "handoff",
        pending=[] if excluded == "empty" else None,
        reason="waiting_for_input" if excluded == "waiting" else "run_completion",
        source_type="third-party" if excluded == "foreign" else "agentserver.task",
    )
    if excluded == "legacy":
        saved.payload.pop("schema_version")
        provider._write_task(saved)
    manager = _manager(provider)
    if excluded == "disabled":
        manager._disable_recovery_for("handoff")
    elif excluded == "host-unbound":
        from azure.ai.agentserver.core.tasks._decorator import _HOST_BOUND_TASK_NAMES

        _HOST_BOUND_TASK_NAMES.add("handoff")
    set_task_manager(manager)
    try:
        await manager.startup()
        assert not invoked.is_set()
        assert await provider.get("chain") is not None
        current = await provider.get("chain")
        assert current.etag == saved.etag
        assert current.payload == saved.payload
    finally:
        await manager.shutdown()
        set_task_manager(None)
        if excluded == "host-unbound":
            _HOST_BOUND_TASK_NAMES.discard("handoff")


@pytest.mark.asyncio
async def test_competing_recovery_uses_snapshot_etag(tmp_path, monkeypatch):
    started, finish = asyncio.Event(), asyncio.Event()
    observed = []

    @multi_turn_task(name="handoff", steerable=True)
    async def worker(ctx: TaskContext[dict]) -> dict:
        observed.append(ctx.input)
        started.set()
        await finish.wait()
        return ctx.input

    provider = LocalFileTaskProvider(tmp_path)
    await _seed(provider)
    first, second = _manager(provider), _manager(provider)
    # Let both managers see the same suspended snapshot before either claims it.
    original_list = provider.list
    readers = 0
    both_read = asyncio.Event()

    async def synchronized_list(**kwargs):
        nonlocal readers
        result = await original_list(**kwargs)
        if kwargs.get("status") == "suspended":
            assert "lease_owner" not in kwargs
            assert kwargs["source_type"] == "agentserver.task"
            readers += 1
            if readers == 2:
                both_read.set()
            await asyncio.wait_for(both_read.wait(), 5)
        return result

    monkeypatch.setattr(provider, "list", synchronized_list)
    try:
        await asyncio.gather(first.startup(), second.startup())
        await asyncio.wait_for(started.wait(), 5)
        assert observed == [{"value": 2}]
        assert sum("chain" in manager._active_tasks for manager in (first, second)) == 1
    finally:
        finish.set()
        await asyncio.gather(first.shutdown(), second.shutdown())


@pytest.mark.asyncio
async def test_raced_queue_append_is_not_overwritten(tmp_path, monkeypatch):
    done = asyncio.Event()
    observed = []

    @multi_turn_task(name="handoff", steerable=True)
    async def worker(ctx: TaskContext[dict]) -> dict:
        observed.append(ctx.input)
        if ctx.input["value"] == 3:
            done.set()
        return ctx.input

    provider = LocalFileTaskProvider(tmp_path)
    await _seed(provider)
    original_update = provider.update
    append_once = True

    async def append_before_claim(task_id, patch):
        nonlocal append_once
        if append_once and patch.status == "in_progress":
            append_once = False
            current = await provider.get(task_id)
            steering = dict(current.payload["steering"])
            steering["pending_inputs"].append({"value": 3})
            await original_update(task_id, TaskPatchRequest(payload={"steering": steering}, if_match=current.etag))
        return await original_update(task_id, patch)

    monkeypatch.setattr(provider, "update", append_before_claim)
    manager = _manager(provider)
    try:
        await manager.startup()
        assert observed == []
        saved = await provider.get("chain")
        assert saved.status == "suspended"
        assert saved.payload["steering"]["pending_inputs"] == [{"value": 2}, {"value": 3}]
        await manager._recover_stale_tasks()
        await asyncio.wait_for(done.wait(), 5)
        assert observed == [{"value": 2}, {"value": 3}]
    finally:
        await manager.shutdown()
