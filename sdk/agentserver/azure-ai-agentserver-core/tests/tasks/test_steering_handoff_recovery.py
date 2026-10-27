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
from azure.ai.agentserver.core.tasks._attachments import (
    _FUNCTION_INPUT_KEY,
    _INPUT_THRESHOLD_BYTES,
    _is_ref,
    _make_ref,
    _read_input_value,
)
from azure.ai.agentserver.core.tasks._exceptions import TaskCancelled
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
async def test_public_resume_and_recovery_share_admission(tmp_path, monkeypatch):
    read, resume_read, scan = (asyncio.Event() for _ in range(3))
    started, finish, finish_third = (asyncio.Event() for _ in range(3))
    observed, runs, executions = [], [], set()

    @multi_turn_task(name="handoff", steerable=True)
    async def worker(ctx: TaskContext[dict]) -> int:
        executions.add(asyncio.current_task())
        value = ctx.input["value"]
        observed.append(value)
        if value == 2:
            started.set()
            await finish.wait()
        else:
            await finish_third.wait()
        return value

    provider = LocalFileTaskProvider(tmp_path)
    manager = _manager(provider)
    set_task_manager(manager)
    public_start = recovery = None
    try:
        await manager.startup()
        await _seed(provider)
        get = manager._provider_get_tracked
        armed = True

        async def stale_read(task_id):
            nonlocal armed
            info = await get(task_id)
            if armed and info.status == "suspended":
                armed = False
                read.set()
                await resume_read.wait()
            return info

        list_tasks = provider.list

        async def scanned(**kwargs):
            infos = await list_tasks(**kwargs)
            if kwargs.get("status") == "suspended":
                scan.set()
            return infos

        monkeypatch.setattr(manager, "_provider_get_tracked", stale_read)
        monkeypatch.setattr(provider, "list", scanned)
        public_start = asyncio.create_task(worker.start(task_id="chain", input={"value": 3}))
        await asyncio.wait_for(read.wait(), 5)
        recovery = asyncio.create_task(manager._recover_stale_tasks())
        await asyncio.wait_for(scan.wait(), 5)
        resume_read.set()
        try:
            third = await asyncio.wait_for(public_start, 5)
        except TaskConflictError:
            # An unclaimed queued handoff is busy, not a new idle turn.
            await asyncio.wait_for(recovery, 5)
            await asyncio.wait_for(started.wait(), 5)
            third = await worker.start(task_id="chain", input={"value": 3})
        runs.append(third)
        await asyncio.wait_for(started.wait(), 5)
        saved = await provider.get("chain")
        assert saved.payload["input"] == {"value": 2}
        assert manager._active_tasks["chain"].context.input == {"value": 2}
        assert observed == [2]
        assert saved.payload["steering"]["pending_inputs"] == [{"value": 3}]
        finish.set()
        finish_third.set()
        assert await asyncio.wait_for(third.result(), 5) == 3
        await asyncio.wait_for(recovery, 5)
        assert observed == [2, 3]
    finally:
        resume_read.set()
        finish.set()
        finish_third.set()
        await manager.shutdown()
        await asyncio.gather(
            *(asyncio.wait_for(task, 5) for task in (public_start, recovery) if task is not None),
            *(asyncio.wait_for(task, 5) for task in executions),
            *(asyncio.wait_for(run.result(), 1) for run in runs),
            return_exceptions=True,
        )
        set_task_manager(None)


@pytest.mark.asyncio
@pytest.mark.parametrize("already_queued", [False, True], ids=["first-append", "later-append"])
@pytest.mark.parametrize("large", [False, True], ids=["inline", "attachment"])
async def test_completion_retry_preserves_raced_append(tmp_path, monkeypatch, already_queued, large):
    started, finish = asyncio.Event(), asyncio.Event()
    observed, runs = [], []

    @multi_turn_task(name="handoff", steerable=True)
    async def worker(ctx: TaskContext[dict]) -> int:
        observed.append(ctx.input["value"])
        if ctx.input["value"] == 1:
            started.set()
            await finish.wait()
        return ctx.input["value"]

    provider = LocalFileTaskProvider(tmp_path)
    manager = _manager(provider)
    set_task_manager(manager)
    try:
        await manager.startup()
        first = await worker.start(task_id="chain", input={"value": 1})
        runs.append(first)
        await asyncio.wait_for(started.wait(), 5)
        if already_queued:
            runs.append(await worker.start(task_id="chain", input={"value": 2}))
        execution = manager._active_tasks["chain"].execution_task
        get = manager._provider_get_tracked
        armed = True

        async def append_after_read(task_id):
            nonlocal armed
            info = await get(task_id)
            if armed:
                armed = False
                value = 3 if already_queued else 2
                runs.append(
                    await worker.start(
                        task_id="chain",
                        input={"value": value, "text": "x" * (_INPUT_THRESHOLD_BYTES + 1024 if large else 0)},
                    )
                )
            return info

        monkeypatch.setattr(manager, "_provider_get_tracked", append_after_read)
        finish.set()
        assert await asyncio.wait_for(first.result(), 5) == 1
        await asyncio.wait_for(execution, 5)
        assert observed == ([1, 2, 3] if already_queued else [1, 2])
        assert await asyncio.wait_for(runs[-1].result(), 5) == observed[-1]
        saved = await provider.get("chain")
        assert saved.status == "suspended"
        assert saved.payload["steering"]["pending_inputs"] == []
        assert "handoff_id" not in saved.payload["steering"]
    finally:
        finish.set()
        await manager.shutdown()
        await asyncio.gather(
            *(asyncio.wait_for(run.result(), 1) for run in runs),
            return_exceptions=True,
        )
        set_task_manager(None)


@pytest.mark.asyncio
async def test_active_suspended_handoff_queues_new_input(tmp_path, monkeypatch):
    started, finish = asyncio.Event(), asyncio.Event()
    suspended, reply = asyncio.Event(), asyncio.Event()
    observed, runs = [], []

    @multi_turn_task(name="handoff", steerable=True)
    async def worker(ctx: TaskContext[dict]) -> int:
        observed.append(ctx.input["value"])
        if ctx.input["value"] == 1:
            started.set()
            await finish.wait()
        return ctx.input["value"]

    provider = LocalFileTaskProvider(tmp_path)
    manager = _manager(provider)
    update = provider.update
    pause_once = True

    async def delay_completion_reply(task_id, patch):
        nonlocal pause_once
        info = await update(task_id, patch)
        if pause_once and patch.status == "suspended":
            pause_once = False
            suspended.set()
            await reply.wait()
        return info

    monkeypatch.setattr(provider, "update", delay_completion_reply)
    set_task_manager(manager)
    try:
        await manager.startup()
        first = await worker.start(task_id="chain", input={"value": 1})
        runs.append(first)
        await asyncio.wait_for(started.wait(), 5)
        execution = manager._active_tasks["chain"].execution_task
        finish.set()
        await asyncio.wait_for(suspended.wait(), 5)
        second = await worker.start(task_id="chain", input={"value": 2})
        runs.append(second)
        assert observed == [1]
        assert manager._active_tasks["chain"].context.input == {"value": 1}
        saved = await provider.get("chain")
        assert saved.status == "suspended"
        assert saved.lease is None
        assert saved.payload["steering"]["pending_inputs"] == [{"value": 2}]
        reply.set()
        assert await asyncio.wait_for(first.result(), 5) == 1
        assert await asyncio.wait_for(second.result(), 5) == 2
        await asyncio.wait_for(execution, 5)
        assert observed == [1, 2]
    finally:
        finish.set()
        reply.set()
        await manager.shutdown()
        await asyncio.gather(
            *(asyncio.wait_for(run.result(), 1) for run in runs),
            return_exceptions=True,
        )
        set_task_manager(None)


@pytest.mark.asyncio
@pytest.mark.parametrize("large", [False, True], ids=["inline", "attachment"])
async def test_idle_resume_admits_input_with_lease_atomically(tmp_path, monkeypatch, large):
    @multi_turn_task(name="handoff", steerable=True)
    async def worker(ctx: TaskContext[dict]) -> int:
        return ctx.input["value"]

    provider = LocalFileTaskProvider(tmp_path)
    manager = _manager(provider)
    set_task_manager(manager)
    try:
        await manager.startup()
        suspended = await _seed(provider, pending=[])
        update = provider.update
        admissions = []

        async def record_admission(task_id, patch):
            if (patch.payload or {}).get("input") is not None:
                admissions.append(patch)
            return await update(task_id, patch)

        monkeypatch.setattr(provider, "update", record_admission)
        value = {"value": 3, "text": "x" * (_INPUT_THRESHOLD_BYTES + 1024 if large else 0)}
        run = await worker.start(task_id="chain", input=value, input_id="turn-3")
        assert await asyncio.wait_for(run.result(), 5) == 3
        assert len(admissions) == 1
        patch = admissions[0]
        assert patch.status == "in_progress"
        assert patch.lease_owner == manager._lease_owner
        assert patch.lease_instance_id == manager._instance_id
        assert patch.if_match == suspended.etag
        assert patch.payload["last_input_id"] == "turn-3"
        assert _read_input_value(patch.payload["input"], patch.attachments) == value
    finally:
        await manager.shutdown()
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
async def test_concurrent_recovery_scans_dispatch_once(tmp_path, monkeypatch):
    started, finish = asyncio.Event(), asyncio.Event()
    observed = []

    @multi_turn_task(name="handoff", steerable=True)
    async def worker(ctx: TaskContext[dict]) -> dict:
        observed.append(ctx.input)
        started.set()
        await finish.wait()
        return ctx.input

    provider = LocalFileTaskProvider(tmp_path)
    manager = _manager(provider)
    set_task_manager(manager)
    await manager.startup()
    await _seed(provider)
    # Let two scans of the same manager read the same suspended snapshot.
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
        await asyncio.gather(manager._recover_queued_steering_tasks(), manager._recover_queued_steering_tasks())
        await asyncio.wait_for(started.wait(), 5)
        assert observed == [{"value": 2}]
        assert "chain" in manager._active_tasks
    finally:
        finish.set()
        await manager.shutdown()
        set_task_manager(None)


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


@pytest.mark.asyncio
@pytest.mark.parametrize("committed_before_cancel", [False, True], ids=["before-commit", "after-commit"])
async def test_cancelled_append_reply_keeps_committed_queue_slot(tmp_path, monkeypatch, committed_before_cancel):
    entered, finish, paused, reply = (asyncio.Event() for _ in range(4))
    observed = []

    @multi_turn_task(name="handoff", steerable=True)
    async def worker(ctx: TaskContext[dict]) -> int:
        value = ctx.input["value"]
        observed.append(value)
        if value == 1:
            entered.set()
            await finish.wait()
        return value

    provider = LocalFileTaskProvider(tmp_path)
    manager = _manager(provider)
    set_task_manager(manager)
    try:
        await manager.startup()
        first = await worker.start(task_id="chain", input={"value": 1})
        await asyncio.wait_for(entered.wait(), 5)
        update = provider.update
        delayed = True

        async def delayed_append(task_id, patch):
            nonlocal delayed
            if delayed and len(((patch.payload or {}).get("steering") or {}).get("pending_inputs") or []) == 1:
                delayed = False
                if not committed_before_cancel:
                    paused.set()
                    await reply.wait()
                result = await update(task_id, patch)
                if committed_before_cancel:
                    paused.set()
                await reply.wait()
                return result
            return await update(task_id, patch)

        monkeypatch.setattr(provider, "update", delayed_append)
        append = asyncio.create_task(worker.start(task_id="chain", input={"value": 2}))
        await asyncio.wait_for(paused.wait(), 5)
        append.cancel()
        with pytest.raises(asyncio.CancelledError):
            await append
        reply.set()

        third = await worker.start(task_id="chain", input={"value": 3})
        finish.set()
        assert await asyncio.wait_for(first.result(), 5) == 1
        assert await asyncio.wait_for(third.result(), 5) == 3
        assert observed == ([1, 2, 3] if committed_before_cancel else [1, 3])
    finally:
        reply.set()
        finish.set()
        await manager.shutdown()
        set_task_manager(None)


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel_queued", [False, True])
async def test_replacement_backlog_keeps_new_caller_aligned(tmp_path, cancel_queued):
    entered, finish = asyncio.Event(), asyncio.Event()
    observed = []

    @multi_turn_task(name="handoff", steerable=True)
    async def worker(ctx: TaskContext[dict]) -> int:
        value = ctx.input["value"]
        observed.append(value)
        if value == 2:
            entered.set()
            await finish.wait()
        return value

    provider = LocalFileTaskProvider(tmp_path)
    await _seed(provider, pending=[{"value": 2}, {"value": 3}])
    manager = _manager(provider)
    set_task_manager(manager)
    try:
        await manager.startup()
        await asyncio.wait_for(entered.wait(), 5)
        fourth = await worker.start(task_id="chain", input={"value": 4})
        target = fourth
        if cancel_queued:
            await fourth.cancel()
            with pytest.raises(TaskCancelled):
                await fourth.result()
            target = await worker.start(task_id="chain", input={"value": 5})
        finish.set()
        assert await asyncio.wait_for(target.result(), 5) == (5 if cancel_queued else 4)
        assert observed == ([2, 3, 5] if cancel_queued else [2, 3, 4])
    finally:
        finish.set()
        await manager.shutdown()
        set_task_manager(None)


@pytest.mark.asyncio
async def test_cancel_queued_after_suspended_completion_reply(tmp_path, monkeypatch):
    entered, finish, committed, reply = (asyncio.Event() for _ in range(4))

    @multi_turn_task(name="handoff", steerable=True)
    async def worker(ctx: TaskContext[dict]) -> int:
        if ctx.input["value"] == 1:
            entered.set()
            await finish.wait()
        return ctx.input["value"]

    provider = LocalFileTaskProvider(tmp_path)
    manager = _manager(provider)
    set_task_manager(manager)
    first = None
    try:
        await manager.startup()
        first = await worker.start(task_id="chain", input={"value": 1})
        await asyncio.wait_for(entered.wait(), 5)
        queued = await worker.start(task_id="chain", input={"value": 2})
        update = provider.update

        async def delayed_completion(task_id, patch):
            result = await update(task_id, patch)
            if patch.status == "suspended" and patch.suspension_reason == "run_completion":
                committed.set()
                await reply.wait()
            return result

        monkeypatch.setattr(provider, "update", delayed_completion)
        info = await provider.get("chain")
        transition = asyncio.create_task(
            provider.update(
                "chain",
                TaskPatchRequest(status="suspended", suspension_reason="run_completion", if_match=info.etag),
            )
        )
        await asyncio.wait_for(committed.wait(), 5)
        assert (await provider.get("chain")).status == "suspended"
        assert "chain" in manager._active_tasks
        await queued.cancel()
        assert (await provider.get("chain")).payload["steering"]["pending_inputs"] == []
        reply.set()
        await asyncio.wait_for(transition, 5)
        with pytest.raises(TaskCancelled):
            await queued.result()
    finally:
        reply.set()
        finish.set()
        await manager.shutdown()
        if first is not None:
            await asyncio.gather(first.result(), return_exceptions=True)
        set_task_manager(None)


@pytest.mark.asyncio
async def test_active_lookup_waits_for_queued_recovery_claim(tmp_path, monkeypatch):
    entered, finish, committed, reply, lookup_locked = (asyncio.Event() for _ in range(5))
    observed = []

    @multi_turn_task(name="handoff", steerable=True)
    async def worker(ctx: TaskContext[dict]) -> int:
        observed.append(ctx.input["value"])
        entered.set()
        await finish.wait()
        return ctx.input["value"]

    provider = LocalFileTaskProvider(tmp_path)
    manager = _manager(provider)
    set_task_manager(manager)
    recovery = lookup = None
    try:
        await manager.startup()
        await _seed(provider)
        update = provider.update
        delayed = True

        async def delayed_claim(task_id, patch):
            nonlocal delayed
            result = await update(task_id, patch)
            if delayed and patch.status == "in_progress":
                delayed = False
                committed.set()
                await reply.wait()
            return result

        monkeypatch.setattr(provider, "update", delayed_claim)
        get_lock = manager._get_task_admission_lock

        def observed_lock(task_id):
            if asyncio.current_task() is lookup:
                lookup_locked.set()
            return get_lock(task_id)

        monkeypatch.setattr(manager, "_get_task_admission_lock", observed_lock)
        recovery = asyncio.create_task(manager._recover_queued_steering_tasks())
        await asyncio.wait_for(committed.wait(), 5)
        lookup = asyncio.create_task(manager.get_active_run("chain"))
        await asyncio.wait_for(lookup_locked.wait(), 5)
        reply.set()
        await asyncio.wait_for(recovery, 5)
        assert await asyncio.wait_for(lookup, 5) is not None
        await asyncio.wait_for(entered.wait(), 5)
        assert observed == [2]
    finally:
        reply.set()
        finish.set()
        await manager.shutdown()
        await asyncio.gather(*(task for task in (recovery, lookup) if task is not None), return_exceptions=True)
        set_task_manager(None)
