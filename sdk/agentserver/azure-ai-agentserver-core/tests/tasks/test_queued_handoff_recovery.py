# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Failure boundaries for queued multi-turn input recovery."""

import asyncio
from datetime import timedelta

import pytest
from pydantic import BaseModel

from azure.ai.agentserver.core.tasks import RetryPolicy, TaskConflictError, TaskContext, TaskDeferred, multi_turn_task
from azure.ai.agentserver.core.tasks._exceptions import TaskCancelled
from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
from azure.ai.agentserver.core.tasks._manager import TaskManager, set_task_manager
from azure.ai.agentserver.core.tasks._models import TaskCreateRequest, TaskPatchRequest
from azure.ai.agentserver.core._config import AgentConfig


def _manager(provider):
    return TaskManager(
        AgentConfig(
            agent_name="repro",
            agent_id="repro:1",
            agent_version="1",
            is_hosted=False,
            project_endpoint="",
            project_id="",
            session_id="repro",
            port=8088,
            appinsights_connection_string="",
            otlp_endpoint="",
            sse_keepalive_interval=0,
        ),
        provider=provider,
        shutdown_grace_seconds=1,
    )


async def _seed_suspended(provider, *, reason="run_completion", source_type="agentserver.task", schema=True):
    task = await provider.create(
        TaskCreateRequest(
            id="sequence",
            title="repro-suspended",
            agent_name="repro",
            session_id="repro",
            status="in_progress",
            lease_owner="repro|session:repro",
            lease_instance_id="previous-worker",
            lease_duration_seconds=60,
            source={"type": source_type, "name": "repro-suspended"},
            payload={
                **({"schema_version": "1"} if schema else {}),
                "input": None,
                "steering": {"pending_inputs": [{"value": 2}, {"value": 3}], "cancel_requested": True},
            },
        )
    )
    return await provider.update(
        "sequence", TaskPatchRequest(status="suspended", suspension_reason=reason, if_match=task.etag)
    )


@pytest.mark.asyncio
async def test_issue_active_queued_turn_survives_restart(tmp_path):
    first_started, finish_first, second_started, restarted = (asyncio.Event() for _ in range(4))
    observed = []

    @multi_turn_task(name="repro-active-input", steerable=True)
    async def worker(ctx: TaskContext[dict]) -> dict:
        observed.append((ctx.input, ctx.entry_mode))
        if ctx.entry_mode == "recovered":
            restarted.set()
        elif ctx.input["value"] == 1:
            first_started.set()
            await finish_first.wait()
        else:
            second_started.set()
            await ctx.shutdown.wait()
            return await ctx.exit_for_recovery()
        return {"observed": ctx.input}

    provider = LocalFileTaskProvider(tmp_path)
    manager = _manager(provider)
    set_task_manager(manager)
    try:
        await manager.startup()
        first = await worker.start(task_id="sequence", input={"value": 1}, input_id="one")
        await asyncio.wait_for(first_started.wait(), 5)
        second = await worker.start(task_id="sequence", input={"value": 2}, input_id="two")
        finish_first.set()
        await asyncio.wait_for(second_started.wait(), 5)
        await first.result()
    finally:
        await manager.shutdown()
        set_task_manager(None)
    with pytest.raises(TaskDeferred):
        await second.result()

    manager = _manager(provider)
    set_task_manager(manager)
    try:
        await manager.startup()
        await asyncio.wait_for(restarted.wait(), 5)
        assert observed[-1] == ({"value": 2}, "recovered")
    finally:
        await manager.shutdown()
        set_task_manager(None)


@pytest.mark.asyncio
async def test_issue_pending_input_recovers_after_drain_failure(tmp_path):
    started, finish, drain_attempted, processed = (asyncio.Event() for _ in range(4))

    @multi_turn_task(name="repro-drain-boundary", steerable=True)
    async def worker(ctx: TaskContext[dict]) -> dict:
        if ctx.input["value"] == 1:
            started.set()
            await finish.wait()
        else:
            processed.set()
        return ctx.input

    async def unavailable_drain(**_kwargs):
        drain_attempted.set()
        raise OSError("Synthetic failure before the queued claim")

    provider = LocalFileTaskProvider(tmp_path)
    manager = _manager(provider)
    manager._try_drain_steering = unavailable_drain
    set_task_manager(manager)
    try:
        await manager.startup()
        first = await worker.start(task_id="sequence", input={"value": 1}, input_id="one")
        await asyncio.wait_for(started.wait(), 5)
        await worker.start(task_id="sequence", input={"value": 2}, input_id="two")
        finish.set()
        await first.result()
        await asyncio.wait_for(drain_attempted.wait(), 5)
    finally:
        await manager.shutdown()
        set_task_manager(None)

    saved = await provider.get("sequence")
    assert saved.payload["steering"]["pending_inputs"] == [{"value": 2}]
    manager = _manager(provider)
    set_task_manager(manager)
    try:
        await manager.startup()
        await asyncio.wait_for(processed.wait(), 5)
    finally:
        await manager.shutdown()
        set_task_manager(None)


@pytest.mark.asyncio
@pytest.mark.parametrize("replacement_finishes", [False, True])
async def test_live_drain_cannot_take_a_recovered_turn(tmp_path, monkeypatch, replacement_finishes):
    entered_first, finish_first, drain_paused, release_drain, entered_second, finish_second = (
        asyncio.Event() for _ in range(6)
    )
    observed = []

    @multi_turn_task(name="repro-two-managers", steerable=True)
    async def worker(ctx: TaskContext[dict]) -> int:
        value = ctx.input["value"]
        observed.append(value)
        if value == 1:
            entered_first.set()
            await finish_first.wait()
        elif value == 2:
            entered_second.set()
            await finish_second.wait()
        return value

    provider = LocalFileTaskProvider(tmp_path)
    original = _manager(provider)
    replacement = None
    set_task_manager(original)
    try:
        await original.startup()
        first = await worker.start(task_id="sequence", input={"value": 1})
        await asyncio.wait_for(entered_first.wait(), 5)
        second = await worker.start(task_id="sequence", input={"value": 2})
        third = await worker.start(task_id="sequence", input={"value": 3})
        original_drain = original._try_drain_steering

        async def hold_drain(**kwargs):
            drain_paused.set()
            await release_drain.wait()
            return await original_drain(**kwargs)

        monkeypatch.setattr(original, "_try_drain_steering", hold_drain)
        original_execution = original._active_tasks["sequence"].execution_task
        finish_first.set()
        assert await asyncio.wait_for(first.result(), 5) == 1
        await asyncio.wait_for(drain_paused.wait(), 5)

        replacement = _manager(provider)
        set_task_manager(replacement)
        await replacement.startup()
        await asyncio.wait_for(entered_second.wait(), 5)
        if replacement_finishes:

            async def fail_replacement_drain(**_kwargs):
                raise OSError("replacement's handoff interrupted")

            monkeypatch.setattr(replacement, "_try_drain_steering", fail_replacement_drain)
            replacement_execution = replacement._active_tasks["sequence"].execution_task
            finish_second.set()
            await asyncio.wait_for(replacement_execution, 5)
            suspended = await provider.get("sequence")
            assert suspended.status == "suspended"
            assert suspended.payload["steering"]["pending_inputs"] == [{"value": 3}]
        release_drain.set()
        await asyncio.wait_for(original_execution, 5)
        saved = await provider.get("sequence")
        assert saved.status == ("suspended" if replacement_finishes else "in_progress")
        assert saved.payload["input"] == (None if replacement_finishes else {"value": 2})
        assert saved.payload["steering"]["pending_inputs"] == [{"value": 3}]
        assert observed == [1, 2]
        for queued in (second, third):
            with pytest.raises(TaskConflictError):
                await asyncio.wait_for(queued.result(), 5)
        with pytest.raises(TaskConflictError):
            await third.cancel()
        assert (await provider.get("sequence")).payload["steering"]["pending_inputs"] == [{"value": 3}]
    finally:
        release_drain.set()
        finish_first.set()
        finish_second.set()
        await original.shutdown()
        if replacement is not None:
            await replacement.shutdown()
        set_task_manager(None)


@pytest.mark.asyncio
async def test_cancelled_committed_append_and_lost_claim_keep_caller_binding(tmp_path, monkeypatch):
    entered_first, finish_first, appended, reply, entered_second, finish_second = (asyncio.Event() for _ in range(6))
    contexts = []

    @multi_turn_task(name="repro-lost-claim", steerable=True)
    async def worker(ctx: TaskContext[dict]) -> int:
        value = ctx.input["value"]
        if value == 1:
            entered_first.set()
            await finish_first.wait()
        elif value == 2:
            contexts.append((ctx.is_steered_turn, ctx.cancel.is_set(), ctx.pending_input_count))
            entered_second.set()
            await finish_second.wait()
        return value

    provider = LocalFileTaskProvider(tmp_path)
    manager = _manager(provider)
    set_task_manager(manager)
    try:
        await manager.startup()
        first = await worker.start(task_id="sequence", input={"value": 1})
        await asyncio.wait_for(entered_first.wait(), 5)
        second = await worker.start(task_id="sequence", input={"value": 2})
        original_update = provider.update
        intercept_append = True

        async def hold_committed_append(task_id, patch):
            nonlocal intercept_append
            steering = (patch.payload or {}).get("steering") or {}
            if intercept_append and len(steering.get("pending_inputs") or []) == 2:
                intercept_append = False
                result = await original_update(task_id, patch)
                appended.set()
                await reply.wait()
                return result
            return await original_update(task_id, patch)

        monkeypatch.setattr(provider, "update", hold_committed_append)
        third_start = asyncio.create_task(worker.start(task_id="sequence", input={"value": 3}))
        await asyncio.wait_for(appended.wait(), 5)
        third_start.cancel()
        with pytest.raises(asyncio.CancelledError):
            await third_start
        reply.set()

        execution = manager._active_tasks["sequence"].execution_task
        drain = manager._try_drain_steering
        interrupt_once = True

        async def fail_drain_once(**kwargs):
            nonlocal interrupt_once
            if interrupt_once:
                interrupt_once = False
                raise OSError("handoff interrupted")
            return await drain(**kwargs)

        monkeypatch.setattr(manager, "_try_drain_steering", fail_drain_once)
        finish_first.set()
        assert await asyncio.wait_for(first.result(), 5) == 1
        await asyncio.wait_for(execution, 5)
        lose_reply = True

        async def claim_commits_without_reply(task_id, patch):
            nonlocal lose_reply
            result = await original_update(task_id, patch)
            if lose_reply and patch.status == "in_progress":
                lose_reply = False
                raise OSError("claim response lost")
            return result

        monkeypatch.setattr(provider, "update", claim_commits_without_reply)
        await manager._recover_stale_tasks()
        await manager._recover_stale_tasks()
        await asyncio.wait_for(entered_second.wait(), 5)
        finish_second.set()
        assert await asyncio.wait_for(second.result(), 5) == 2
        assert contexts == [(True, True, 1)]
    finally:
        reply.set()
        finish_first.set()
        finish_second.set()
        await manager.shutdown()
        set_task_manager(None)


@pytest.mark.asyncio
@pytest.mark.parametrize("committed", [False, True], ids=["uncommitted", "committed"])
async def test_unknown_removal_response_does_not_shift_queued_callers(tmp_path, monkeypatch, committed):
    entered, finish = asyncio.Event(), asyncio.Event()

    @multi_turn_task(name="repro-removal", steerable=True)
    async def worker(ctx: TaskContext[dict]) -> int:
        if ctx.input["value"] == 1:
            entered.set()
            await finish.wait()
        return ctx.input["value"]

    provider = LocalFileTaskProvider(tmp_path)
    manager = _manager(provider)
    set_task_manager(manager)
    try:
        await manager.startup()
        first = await worker.start(task_id="sequence", input={"value": 1})
        await asyncio.wait_for(entered.wait(), 5)
        second = await worker.start(task_id="sequence", input={"value": 2})
        third = await worker.start(task_id="sequence", input={"value": 3})
        original_update = provider.update
        intercept = True

        async def unknown_removal(task_id, patch):
            nonlocal intercept
            steering = (patch.payload or {}).get("steering") or {}
            if intercept and steering.get("pending_inputs") == [{"value": 3}]:
                intercept = False
                if committed:
                    await original_update(task_id, patch)
                raise OSError("removal response lost")
            return await original_update(task_id, patch)

        monkeypatch.setattr(provider, "update", unknown_removal)
        if committed:
            await second.cancel()
        else:
            with pytest.raises(OSError, match="removal response lost"):
                await second.cancel()
        saved = await provider.get("sequence")
        assert saved.payload["steering"]["pending_inputs"] == (
            [{"value": 3}] if committed else [{"value": 2}, {"value": 3}]
        )
        fourth = await worker.start(task_id="sequence", input={"value": 4})
        finish.set()
        assert await asyncio.wait_for(first.result(), 5) == 1
        if committed:
            with pytest.raises(TaskCancelled):
                await asyncio.wait_for(second.result(), 5)
        else:
            assert await asyncio.wait_for(second.result(), 5) == 2
        assert await asyncio.wait_for(third.result(), 5) == 3
        assert await asyncio.wait_for(fourth.result(), 5) == 4
    finally:
        finish.set()
        await manager.shutdown()
        set_task_manager(None)


class TurnInput(BaseModel):
    value: int


@pytest.mark.asyncio
async def test_recovered_queued_turn_keeps_typed_input_retry_and_context(tmp_path):
    observed = []
    reached = asyncio.Event()

    @multi_turn_task(
        name="repro-suspended",
        steerable=True,
        retry=RetryPolicy.fixed_delay(delay=timedelta(0), max_attempts=2),
    )
    async def worker(ctx: TaskContext[TurnInput]) -> int:
        observed.append(
            (
                type(ctx.input),
                ctx.input.value,
                ctx.retry_attempt,
                ctx.is_steered_turn,
                ctx.cancel.is_set(),
                ctx.pending_input_count,
            )
        )
        if ctx.retry_attempt == 0:
            raise OSError("transient")
        if ctx.input.value == 3:
            reached.set()
        return ctx.input.value

    provider = LocalFileTaskProvider(tmp_path)
    await _seed_suspended(provider)
    manager = _manager(provider)
    set_task_manager(manager)
    try:
        await manager.startup()
        await asyncio.wait_for(reached.wait(), 5)
        assert observed == [
            (TurnInput, 2, 0, True, True, 1),
            (TurnInput, 2, 1, True, True, 1),
            (TurnInput, 3, 0, True, False, 0),
            (TurnInput, 3, 1, True, False, 0),
        ]
    finally:
        await manager.shutdown()
        set_task_manager(None)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("reason", "source_type", "schema"),
    [
        ("awaiting_input", "agentserver.task", True),
        ("run_completion", "other.framework", True),
        ("run_completion", "agentserver.task", False),
    ],
)
async def test_unrelated_suspended_tasks_are_not_recovered(tmp_path, reason, source_type, schema):
    called = asyncio.Event()

    @multi_turn_task(name="repro-suspended", steerable=True)
    async def worker(ctx: TaskContext[dict]) -> int:
        called.set()
        return ctx.input["value"]

    provider = LocalFileTaskProvider(tmp_path)
    original = await _seed_suspended(provider, reason=reason, source_type=source_type, schema=schema)
    manager = _manager(provider)
    set_task_manager(manager)
    try:
        await manager.startup()
        assert not called.is_set()
        saved = await provider.get("sequence")
        assert saved.status == "suspended"
        assert saved.etag == original.etag
        assert saved.payload["steering"]["pending_inputs"] == [{"value": 2}, {"value": 3}]
    finally:
        await manager.shutdown()
        set_task_manager(None)


@pytest.mark.asyncio
async def test_new_caller_after_legacy_backlog_keeps_its_own_result(tmp_path):
    entered, finish = asyncio.Event(), asyncio.Event()
    observed = []

    @multi_turn_task(name="repro-suspended", steerable=True)
    async def worker(ctx: TaskContext[dict]) -> int:
        value = ctx.input["value"]
        observed.append(value)
        if value == 2:
            entered.set()
            await finish.wait()
        return value

    provider = LocalFileTaskProvider(tmp_path)
    await _seed_suspended(provider)
    manager = _manager(provider)
    set_task_manager(manager)
    try:
        await manager.startup()
        await asyncio.wait_for(entered.wait(), 5)
        fourth = await worker.start(task_id="sequence", input={"value": 4})
        saved = await provider.get("sequence")
        assert saved.payload["steering"]["pending_input_ids"][0] is None
        finish.set()
        assert await asyncio.wait_for(fourth.result(), 5) == 4
        assert observed == [2, 3, 4]
    finally:
        finish.set()
        await manager.shutdown()
        set_task_manager(None)


@pytest.mark.asyncio
async def test_foreground_start_queues_behind_stranded_suspended_input(tmp_path, monkeypatch):
    entered, finish = asyncio.Event(), asyncio.Event()
    observed = []

    @multi_turn_task(name="repro-foreground", steerable=True)
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
        first = await worker.start(task_id="sequence", input={"value": 1})
        await asyncio.wait_for(entered.wait(), 5)
        second = await worker.start(task_id="sequence", input={"value": 2})
        original_drain = manager._try_drain_steering
        fail_once = True

        async def unavailable_once(**kwargs):
            nonlocal fail_once
            if fail_once:
                fail_once = False
                raise OSError("handoff unavailable")
            return await original_drain(**kwargs)

        monkeypatch.setattr(manager, "_try_drain_steering", unavailable_once)
        execution = manager._active_tasks["sequence"].execution_task
        finish.set()
        assert await asyncio.wait_for(first.result(), 5) == 1
        await asyncio.wait_for(execution, 5)
        third = await worker.start(task_id="sequence", input={"value": 3})
        saved = await provider.get("sequence")
        assert saved.payload["steering"]["pending_inputs"] == [{"value": 2}, {"value": 3}]
        await manager._recover_stale_tasks()
        assert await asyncio.wait_for(second.result(), 5) == 2
        assert await asyncio.wait_for(third.result(), 5) == 3
        assert observed == [1, 2, 3]
    finally:
        finish.set()
        await manager.shutdown()
        set_task_manager(None)


@pytest.mark.asyncio
async def test_first_queue_append_during_terminal_retry_is_preserved(tmp_path, monkeypatch):
    entered, finish = asyncio.Event(), asyncio.Event()
    observed = []

    @multi_turn_task(name="repro-terminal-race", steerable=True)
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
        first = await worker.start(task_id="sequence", input={"value": 1})
        await asyncio.wait_for(entered.wait(), 5)
        original_update = provider.update
        queued = None

        async def append_during_terminal(task_id, patch):
            nonlocal queued
            if patch.status == "suspended" and queued is None:
                queued = await worker.start(task_id="sequence", input={"value": 2})
            return await original_update(task_id, patch)

        monkeypatch.setattr(provider, "update", append_during_terminal)
        finish.set()
        assert await asyncio.wait_for(first.result(), 5) == 1
        assert queued is not None
        assert await asyncio.wait_for(queued.result(), 5) == 2
        assert observed == [1, 2]
    finally:
        finish.set()
        await manager.shutdown()
        set_task_manager(None)


@pytest.mark.asyncio
async def test_cancelled_removal_waits_for_committed_write(tmp_path, monkeypatch):
    entered, finish, committed, reply = (asyncio.Event() for _ in range(4))

    @multi_turn_task(name="repro-interrupted-removal", steerable=True)
    async def worker(ctx: TaskContext[dict]) -> int:
        if ctx.input["value"] == 1:
            entered.set()
            await finish.wait()
        return ctx.input["value"]

    provider = LocalFileTaskProvider(tmp_path)
    manager = _manager(provider)
    set_task_manager(manager)
    reply.set()
    try:
        await manager.startup()
        first = await worker.start(task_id="sequence", input={"value": 1})
        await asyncio.wait_for(entered.wait(), 5)
        queued = await worker.start(task_id="sequence", input={"value": 2})
        original_update = provider.update
        reply.clear()

        async def hold_removal(task_id, patch):
            result = await original_update(task_id, patch)
            steering = (patch.payload or {}).get("steering") or {}
            if "pending_input_ids" in steering and not steering["pending_inputs"]:
                committed.set()
                await reply.wait()
            return result

        monkeypatch.setattr(provider, "update", hold_removal)
        cancelling = asyncio.create_task(queued.cancel())
        await asyncio.wait_for(committed.wait(), 5)
        cancelling.cancel()
        reply.set()
        with pytest.raises(asyncio.CancelledError):
            await cancelling
        with pytest.raises(TaskCancelled):
            await queued.result()
        third = await worker.start(task_id="sequence", input={"value": 3})
        finish.set()
        assert await asyncio.wait_for(first.result(), 5) == 1
        assert await asyncio.wait_for(third.result(), 5) == 3
    finally:
        reply.set()
        finish.set()
        await manager.shutdown()
        set_task_manager(None)


@pytest.mark.asyncio
async def test_foreground_start_waits_for_inflight_recovery_claim(tmp_path, monkeypatch):
    committed, reply, entered, finish = (asyncio.Event() for _ in range(4))

    @multi_turn_task(name="repro-suspended", steerable=True)
    async def worker(ctx: TaskContext[dict]) -> int:
        if ctx.input["value"] == 2:
            entered.set()
            await finish.wait()
        return ctx.input["value"]

    provider = LocalFileTaskProvider(tmp_path)
    await _seed_suspended(provider)
    manager = _manager(provider)
    set_task_manager(manager)
    reply.set()
    try:
        original_update = provider.update
        reply.clear()

        async def hold_claim(task_id, patch):
            result = await original_update(task_id, patch)
            if patch.status == "in_progress" and (patch.payload or {}).get("input") == {"value": 2}:
                committed.set()
                await reply.wait()
            return result

        monkeypatch.setattr(provider, "update", hold_claim)
        starting = asyncio.create_task(manager.startup())
        await asyncio.wait_for(committed.wait(), 5)
        fourth_start = asyncio.create_task(worker.start(task_id="sequence", input={"value": 4}))
        await asyncio.sleep(0)
        assert not fourth_start.done()
        reply.set()
        await asyncio.wait_for(starting, 5)
        await asyncio.wait_for(entered.wait(), 5)
        fourth = await asyncio.wait_for(fourth_start, 5)
        saved = await provider.get("sequence")
        assert saved.payload["input"] == {"value": 2}
        assert saved.payload["steering"]["pending_inputs"] == [{"value": 3}, {"value": 4}]
        finish.set()
        assert await asyncio.wait_for(fourth.result(), 5) == 4
    finally:
        reply.set()
        finish.set()
        await manager.shutdown()
        set_task_manager(None)


@pytest.mark.asyncio
async def test_delete_waits_for_recovery_claim_and_dispatch(tmp_path, monkeypatch):
    committed, reply = asyncio.Event(), asyncio.Event()
    entered = asyncio.Event()

    @multi_turn_task(name="repro-suspended", steerable=True)
    async def worker(ctx: TaskContext[dict]) -> int:
        entered.set()
        await ctx.shutdown.wait()
        return ctx.input["value"]

    provider = LocalFileTaskProvider(tmp_path)
    await _seed_suspended(provider)
    manager = _manager(provider)
    set_task_manager(manager)
    reply.set()
    try:
        original_update = provider.update
        reply.clear()

        async def hold_claim(task_id, patch):
            result = await original_update(task_id, patch)
            if patch.status == "in_progress" and (patch.payload or {}).get("input") == {"value": 2}:
                committed.set()
                await reply.wait()
            return result

        monkeypatch.setattr(provider, "update", hold_claim)
        starting = asyncio.create_task(manager.startup())
        await asyncio.wait_for(committed.wait(), 5)
        deleting = asyncio.create_task(worker.delete("sequence"))
        await asyncio.sleep(0)
        assert not deleting.done()
        reply.set()
        await asyncio.wait_for(starting, 5)
        await asyncio.wait_for(deleting, 5)
        assert await provider.get("sequence") is None
        active = manager._active_tasks.get("sequence")
        if active is not None:
            await asyncio.wait_for(active.execution_task, 5)
        assert not manager._active_tasks.get("sequence")
    finally:
        reply.set()
        await manager.shutdown()
        set_task_manager(None)


@pytest.mark.asyncio
async def test_legacy_writer_changes_tokened_queue_without_misbinding(tmp_path):
    entered, finish, processed = (asyncio.Event() for _ in range(3))
    observed = []

    @multi_turn_task(name="repro-mixed-writers", steerable=True)
    async def worker(ctx: TaskContext[dict]) -> int:
        value = ctx.input["value"]
        observed.append(value)
        if value == 1:
            entered.set()
            await finish.wait()
        if value == 4:
            processed.set()
        return value

    provider = LocalFileTaskProvider(tmp_path)
    manager = _manager(provider)
    set_task_manager(manager)
    try:
        await manager.startup()
        first = await worker.start(task_id="sequence", input={"value": 1})
        await asyncio.wait_for(entered.wait(), 5)
        second = await worker.start(task_id="sequence", input={"value": 2})
        third = await worker.start(task_id="sequence", input={"value": 3})
        saved = await provider.get("sequence")
        steering = dict(saved.payload["steering"])
        steering["pending_inputs"] = [*steering["pending_inputs"], {"value": 4}]
        await provider.update("sequence", TaskPatchRequest(payload={"steering": steering}, if_match=saved.etag))
        finish.set()
        assert await asyncio.wait_for(first.result(), 5) == 1
        await asyncio.wait_for(processed.wait(), 5)
        assert observed == [1, 2, 3, 4]
        for queued in (second, third):
            with pytest.raises(TaskConflictError):
                await asyncio.wait_for(queued.result(), 5)
    finally:
        finish.set()
        await manager.shutdown()
        set_task_manager(None)


@pytest.mark.asyncio
async def test_claim_commits_without_reply_preserves_typed_retry_and_context(tmp_path, monkeypatch):
    observed = []
    processed = asyncio.Event()

    @multi_turn_task(
        name="repro-suspended",
        steerable=True,
        retry=RetryPolicy.fixed_delay(delay=timedelta(0), max_attempts=2),
    )
    async def worker(ctx: TaskContext[TurnInput]) -> int:
        observed.append(
            (type(ctx.input), ctx.input.value, ctx.retry_attempt, ctx.is_steered_turn, ctx.pending_input_count)
        )
        if ctx.input.value == 2 and ctx.retry_attempt == 0:
            raise OSError("transient")
        if ctx.input.value == 3:
            processed.set()
        return ctx.input.value

    provider = LocalFileTaskProvider(tmp_path)
    await _seed_suspended(provider)
    manager = _manager(provider)
    set_task_manager(manager)
    try:
        original_update = provider.update
        lose_reply = True

        async def claim_commits_without_reply(task_id, patch):
            nonlocal lose_reply
            result = await original_update(task_id, patch)
            if lose_reply and patch.status == "in_progress" and (patch.payload or {}).get("input") == {"value": 2}:
                lose_reply = False
                raise OSError("claim response lost")
            return result

        monkeypatch.setattr(provider, "update", claim_commits_without_reply)
        await manager.startup()
        await manager._recover_stale_tasks()
        await asyncio.wait_for(processed.wait(), 5)
        assert observed == [
            (TurnInput, 2, 0, True, 1),
            (TurnInput, 2, 1, True, 1),
            (TurnInput, 3, 0, True, 0),
        ]
    finally:
        await manager.shutdown()
        set_task_manager(None)


@pytest.mark.asyncio
async def test_cancelling_duplicate_value_removes_only_its_identity(tmp_path):
    entered, finish = asyncio.Event(), asyncio.Event()

    @multi_turn_task(name="repro-duplicate-input", steerable=True)
    async def worker(ctx: TaskContext[dict]) -> int:
        if ctx.input["value"] == 1:
            entered.set()
            await finish.wait()
        return ctx.input["value"]

    provider = LocalFileTaskProvider(tmp_path)
    manager = _manager(provider)
    set_task_manager(manager)
    try:
        await manager.startup()
        first = await worker.start(task_id="sequence", input={"value": 1})
        await asyncio.wait_for(entered.wait(), 5)
        second = await worker.start(task_id="sequence", input={"value": 2})
        third = await worker.start(task_id="sequence", input={"value": 2})
        second_token, third_token = manager._pending_steering_futures["sequence"]
        await third.cancel()
        saved = await provider.get("sequence")
        assert saved.payload["steering"]["pending_inputs"] == [{"value": 2}]
        assert saved.payload["steering"]["pending_input_ids"] == [second_token]
        assert third_token not in manager._pending_steering_futures["sequence"]
        finish.set()
        assert await asyncio.wait_for(first.result(), 5) == 1
        assert await asyncio.wait_for(second.result(), 5) == 2
        with pytest.raises(TaskCancelled):
            await third.result()
    finally:
        finish.set()
        await manager.shutdown()
        set_task_manager(None)


@pytest.mark.asyncio
async def test_active_lookup_waits_for_committed_claim_reply(tmp_path, monkeypatch):
    committed, reply, entered, finish = (asyncio.Event() for _ in range(4))
    entered_third = asyncio.Event()
    observed = []

    @multi_turn_task(name="repro-suspended", steerable=True)
    async def worker(ctx: TaskContext[dict]) -> int:
        observed.append(ctx.input["value"])
        if ctx.input["value"] == 2:
            entered.set()
            await finish.wait()
        if ctx.input["value"] == 3:
            entered_third.set()
        return ctx.input["value"]

    provider = LocalFileTaskProvider(tmp_path)
    await _seed_suspended(provider)
    manager = _manager(provider)
    set_task_manager(manager)
    reply.set()
    try:
        original_update = provider.update
        reply.clear()

        async def hold_claim(task_id, patch):
            result = await original_update(task_id, patch)
            if patch.status == "in_progress" and (patch.payload or {}).get("input") == {"value": 2}:
                committed.set()
                await reply.wait()
            return result

        monkeypatch.setattr(provider, "update", hold_claim)
        starting = asyncio.create_task(manager.startup())
        await asyncio.wait_for(committed.wait(), 5)
        looking_up = asyncio.create_task(manager.get_active_run("sequence"))
        await asyncio.sleep(0)
        assert not looking_up.done()
        reply.set()
        await asyncio.wait_for(starting, 5)
        run = await asyncio.wait_for(looking_up, 5)
        assert run is not None
        await asyncio.wait_for(entered.wait(), 5)
        finish.set()
        assert await asyncio.wait_for(run.result(), 5) == 2
        await asyncio.wait_for(entered_third.wait(), 5)
        assert observed == [2, 3]
    finally:
        reply.set()
        finish.set()
        await manager.shutdown()
        set_task_manager(None)


@pytest.mark.asyncio
async def test_two_recovery_scans_claim_a_queued_turn_once(tmp_path):
    entered, finish = asyncio.Event(), asyncio.Event()
    observed = []

    @multi_turn_task(name="repro-suspended", steerable=True)
    async def worker(ctx: TaskContext[dict]) -> int:
        observed.append(ctx.input["value"])
        if ctx.input["value"] == 2:
            entered.set()
            await finish.wait()
        return ctx.input["value"]

    provider = LocalFileTaskProvider(tmp_path)
    await _seed_suspended(provider)
    first_manager = _manager(provider)
    second_manager = _manager(provider)
    set_task_manager(first_manager)
    try:
        await asyncio.gather(first_manager.startup(), second_manager.startup())
        await asyncio.wait_for(entered.wait(), 5)
        saved = await provider.get("sequence")
        assert saved.payload["input"] == {"value": 2}
        assert saved.payload["steering"]["pending_inputs"] == [{"value": 3}]
        assert observed == [2]
        finish.set()
        await asyncio.wait_for(
            (
                first_manager._active_tasks.get("sequence").execution_task
                if "sequence" in first_manager._active_tasks
                else second_manager._active_tasks["sequence"].execution_task
            ),
            5,
        )
        assert observed == [2, 3]
    finally:
        finish.set()
        await first_manager.shutdown()
        await second_manager.shutdown()
        set_task_manager(None)


@pytest.mark.asyncio
async def test_crash_after_claim_before_dispatch_recovers_canonical_input(tmp_path):
    observed = []
    finished = asyncio.Event()

    @multi_turn_task(name="repro-suspended", steerable=True)
    async def worker(ctx: TaskContext[dict]) -> int:
        observed.append((ctx.input["value"], ctx.entry_mode, ctx.is_steered_turn))
        if ctx.input["value"] == 3:
            finished.set()
        return ctx.input["value"]

    provider = LocalFileTaskProvider(tmp_path)
    suspended = await _seed_suspended(provider)
    crashed = _manager(provider)
    payload, attachments, _ = crashed._prepare_steering_input(suspended)
    claimed = await provider.update(
        "sequence",
        TaskPatchRequest(
            status="in_progress",
            payload=payload,
            attachments=attachments or None,
            lease_owner=crashed._lease_owner,
            lease_instance_id=crashed._instance_id,
            lease_duration_seconds=60,
            if_match=suspended.etag,
        ),
    )
    await provider.update(
        "sequence",
        TaskPatchRequest(
            lease_owner=crashed._lease_owner,
            lease_instance_id=crashed._instance_id,
            lease_duration_seconds=0,
            if_match=claimed.etag,
        ),
    )
    replacement = _manager(provider)
    set_task_manager(replacement)
    try:
        await replacement.startup()
        await asyncio.wait_for(finished.wait(), 5)
        assert observed == [(2, "recovered", True), (3, "resumed", True)]
    finally:
        await replacement.shutdown()
        set_task_manager(None)


@pytest.mark.asyncio
async def test_other_manager_completed_backlog_rejects_stranded_local_callers(tmp_path, monkeypatch):
    entered, finish, processed = (asyncio.Event() for _ in range(3))
    observed = []

    @multi_turn_task(name="repro-cross-manager-results", steerable=True)
    async def worker(ctx: TaskContext[dict]) -> int:
        value = ctx.input["value"]
        observed.append(value)
        if value == 1:
            entered.set()
            await finish.wait()
        if value == 3:
            processed.set()
        return value

    provider = LocalFileTaskProvider(tmp_path)
    original = _manager(provider)
    replacement = None
    set_task_manager(original)
    try:
        await original.startup()
        first = await worker.start(task_id="sequence", input={"value": 1})
        await asyncio.wait_for(entered.wait(), 5)
        second = await worker.start(task_id="sequence", input={"value": 2})
        third = await worker.start(task_id="sequence", input={"value": 3})
        execution = original._active_tasks["sequence"].execution_task
        fail_once = True
        actual_drain = original._try_drain_steering

        async def fail_original_drain(**kwargs):
            nonlocal fail_once
            if fail_once:
                fail_once = False
                raise OSError("handoff unavailable")
            return await actual_drain(**kwargs)

        monkeypatch.setattr(original, "_try_drain_steering", fail_original_drain)
        finish.set()
        assert await asyncio.wait_for(first.result(), 5) == 1
        await asyncio.wait_for(execution, 5)
        replacement = _manager(provider)
        set_task_manager(replacement)
        await replacement.startup()
        await asyncio.wait_for(processed.wait(), 5)
        assert observed == [1, 2, 3]
        assert (await provider.get("sequence")).payload["steering"]["pending_inputs"] == []

        await original._recover_stale_tasks()
        for queued in (second, third):
            with pytest.raises(TaskConflictError):
                await asyncio.wait_for(queued.result(), 2)
    finally:
        finish.set()
        await original.shutdown()
        if replacement is not None:
            await replacement.shutdown()
        set_task_manager(None)
