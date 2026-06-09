# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT license.
"""Spec 018 — Steering-input queue redesign end-to-end (Phase 4).

Verifies:

- Small steering input stays inline (raw value in pending_inputs).
- Large steering input is promoted to ``attachments["_steering_input_<seq>"]``
  with a ref slot in pending_inputs.
- Drain of a ref-shaped queue entry deletes the attachment via the
  SAME PATCH (atomicity).
- The monotonic-seq invariant — drain does NOT renumber other entries.
- 9-cap raises SteeringQueueFull on the 10th append.
- Orphan attachment cleanup runs at recovery and deletes
  unreferenced ``_steering_input_*`` keys.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import pytest
import pytest_asyncio

from azure.ai.agentserver.core.durable import TaskContext, task
from azure.ai.agentserver.core.durable._attachments import (
    _STEERING_INPUT_KEY_PREFIX,
    _STEERING_QUEUE_CAP,
    _STEERING_THRESHOLD_BYTES,
    _is_ref,
    _ref_key,
)
from azure.ai.agentserver.core.durable._exceptions import SteeringQueueFull
from azure.ai.agentserver.core.durable._local_provider import (
    LocalFileTaskProvider,
)
from azure.ai.agentserver.core.durable._manager import (
    TaskManager,
    set_task_manager,
)
from azure.ai.agentserver.core.durable._models import TaskPatchRequest


def _config_stub(session_id: str = "s018-steer-session"):
    return type(
        "C",
        (),
        {
            "agent_name": "s018-steer-agent",
            "session_id": session_id,
            "agent_version": "1.0.0",
            "is_hosted": False,
        },
    )()


@pytest_asyncio.fixture
async def manager_local(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AGENTSERVER_DURABLE_TASKS_PATH", str(tmp_path / "tasks"))
    monkeypatch.delenv("FOUNDRY_HOSTING_ENVIRONMENT", raising=False)
    config = _config_stub()
    mgr = TaskManager(
        config=config,
        provider=LocalFileTaskProvider(base_dir=tmp_path / "tasks"),
        shutdown_event=asyncio.Event(),
    )
    set_task_manager(mgr)
    await mgr.startup()
    try:
        yield mgr
    finally:
        await mgr.shutdown()
        set_task_manager(None)


# --------------------------------------------------------------------------- #
# Append: small input stays inline; large input promotes
# --------------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_small_steering_input_stays_inline(manager_local: TaskManager) -> None:
    """SC-4: small steering input is appended as a raw value."""

    started = asyncio.Event()
    proceed = asyncio.Event()

    @task(name="t-steer-small", steerable=True)
    async def runner(ctx: TaskContext[dict]) -> dict:
        started.set()
        await proceed.wait()
        return await ctx.suspend(reason="done", output={"ok": True})

    # First start — initial input, runs the handler.
    run1 = await runner.start(task_id="t-steer-small-1", input={"first": True})
    await asyncio.wait_for(started.wait(), timeout=2.0)

    # While handler is mid-run, append a small steering input.
    run2 = await runner.start(task_id="t-steer-small-1", input={"small": "value"})

    # Inspect state — pending_inputs has the small value inline.
    info = await manager_local.provider.get("t-steer-small-1")
    assert info is not None
    pending = info.payload["_steering"]["pending_inputs"]
    assert len(pending) == 1
    assert pending[0] == {"small": "value"}
    assert not _is_ref(pending[0])
    # No steering attachment because below threshold.
    if info.attachments:
        assert not any(
            k.startswith(_STEERING_INPUT_KEY_PREFIX) for k in info.attachments
        )

    proceed.set()
    # Cancel both runs to clean up.
    await run1.cancel()


@pytest.mark.asyncio
async def test_large_steering_input_promoted(manager_local: TaskManager) -> None:
    """SC-5: steering input > 20 KiB is promoted to attachment with ref in queue."""

    big = "y" * (_STEERING_THRESHOLD_BYTES + 1024)

    started = asyncio.Event()
    proceed = asyncio.Event()

    @task(name="t-steer-big", steerable=True)
    async def runner(ctx: TaskContext[dict]) -> dict:
        started.set()
        await proceed.wait()
        return await ctx.suspend(reason="done", output={"ok": True})

    run1 = await runner.start(task_id="t-steer-big-1", input={"first": True})
    await asyncio.wait_for(started.wait(), timeout=2.0)

    # Append a large steering input.
    await runner.start(task_id="t-steer-big-1", input=big)

    # Inspect: pending_inputs has a ref; attachments has the value.
    info = await manager_local.provider.get("t-steer-big-1")
    assert info is not None
    pending = info.payload["_steering"]["pending_inputs"]
    assert len(pending) == 1
    assert _is_ref(pending[0])
    key = _ref_key(pending[0])
    assert key.startswith(_STEERING_INPUT_KEY_PREFIX)
    assert info.attachments is not None
    assert info.attachments[key] == big
    # next_input_seq has advanced.
    assert info.payload["_steering"]["next_input_seq"] == 1

    proceed.set()
    await run1.cancel()


# --------------------------------------------------------------------------- #
# Monotonic seq invariant — the user's key concern
# --------------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_drain_does_not_renumber_existing_attachments(
    manager_local: TaskManager,
) -> None:
    """The user's concern: dequeue MUST NOT trigger re-upload / re-keying.

    After appending A and B (both promoted) and draining A, B's
    attachment key MUST be the one it was assigned at append time.
    """

    a_value = "a" * (_STEERING_THRESHOLD_BYTES + 100)
    b_value = "b" * (_STEERING_THRESHOLD_BYTES + 100)

    drain_signal = asyncio.Event()
    started_count = 0

    @task(name="t-steer-monotonic", steerable=True)
    async def runner(ctx: TaskContext[dict]) -> dict:
        nonlocal started_count
        started_count += 1
        # Wait until the test signals to advance.
        await drain_signal.wait()
        drain_signal.clear()
        return await ctx.suspend(reason="done")

    run = await runner.start(task_id="t-monotonic-1", input={"initial": True})
    await asyncio.sleep(0.1)  # let initial turn enter

    # Append A (promoted; key allocated at seq=0 → _steering_input_0).
    await runner.start(task_id="t-monotonic-1", input=a_value)
    # Append B (promoted; key allocated at seq=1 → _steering_input_1).
    await runner.start(task_id="t-monotonic-1", input=b_value)

    # Inspect pre-drain: A and B are both in pending, with their respective keys.
    info_pre = await manager_local.provider.get("t-monotonic-1")
    assert info_pre is not None
    pending_pre = info_pre.payload["_steering"]["pending_inputs"]
    assert len(pending_pre) == 2
    assert _ref_key(pending_pre[0]) == "_steering_input_0"
    assert _ref_key(pending_pre[1]) == "_steering_input_1"
    assert info_pre.attachments["_steering_input_0"] == a_value
    assert info_pre.attachments["_steering_input_1"] == b_value

    # Let the initial turn complete → drain advances A into active_input.
    drain_signal.set()
    await asyncio.sleep(0.5)  # let drain happen

    # Inspect post-drain: A's attachment is GONE; B's attachment key UNCHANGED.
    info_mid = await manager_local.provider.get("t-monotonic-1")
    assert info_mid is not None
    pending_mid = info_mid.payload["_steering"]["pending_inputs"]
    # Only B left in the queue.
    assert len(pending_mid) == 1
    # B's attachment key MUST still be _steering_input_1 (not renamed to _0).
    assert _ref_key(pending_mid[0]) == "_steering_input_1"
    # A's attachment is gone; B's is unchanged.
    assert "_steering_input_0" not in (info_mid.attachments or {})
    assert info_mid.attachments["_steering_input_1"] == b_value
    # next_input_seq has not regressed (still at 2; monotonic).
    assert info_mid.payload["_steering"]["next_input_seq"] == 2

    # Let B's turn complete too.
    drain_signal.set()
    await asyncio.sleep(0.5)
    await run.cancel()


# --------------------------------------------------------------------------- #
# 9-cap on the steering queue
# --------------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_steering_queue_9_cap(manager_local: TaskManager) -> None:
    """SC-7: 9th append succeeds; 10th raises SteeringQueueFull(9)."""

    started = asyncio.Event()
    block = asyncio.Event()

    @task(name="t-steer-9cap", steerable=True)
    async def runner(ctx: TaskContext[dict]) -> dict:
        started.set()
        await block.wait()
        return await ctx.suspend(reason="done")

    run = await runner.start(task_id="t-9cap-1", input={"initial": True})
    await asyncio.wait_for(started.wait(), timeout=2.0)

    # Append 9 steering inputs (small inline) — all should succeed.
    for i in range(_STEERING_QUEUE_CAP):
        await runner.start(task_id="t-9cap-1", input={"steer": i})

    # 10th raises.
    with pytest.raises(SteeringQueueFull) as excinfo:
        await runner.start(task_id="t-9cap-1", input={"steer": 999})
    assert excinfo.value.task_id == "t-9cap-1"
    assert excinfo.value.max_pending == _STEERING_QUEUE_CAP

    block.set()
    await run.cancel()


# --------------------------------------------------------------------------- #
# Drain co-deletes the attachment in the SAME PATCH (atomicity proxy)
# --------------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_drain_co_deletes_attachment(manager_local: TaskManager) -> None:
    """SC-6: drain of a ref-shaped entry MUST delete the attachment.

    Verified indirectly: post-drain, the attachment is absent.
    (The single-PATCH-atomicity invariant is structural; the test
    pins the observable outcome.)
    """

    big = "z" * (_STEERING_THRESHOLD_BYTES + 200)
    drain_signal = asyncio.Event()

    @task(name="t-steer-drain", steerable=True)
    async def runner(ctx: TaskContext[dict]) -> dict:
        await drain_signal.wait()
        drain_signal.clear()
        return await ctx.suspend(reason="done")

    run = await runner.start(task_id="t-drain-1", input={"initial": True})
    await asyncio.sleep(0.1)

    # Queue a large steering input → attachment is created.
    await runner.start(task_id="t-drain-1", input=big)

    info_pre = await manager_local.provider.get("t-drain-1")
    assert info_pre is not None
    assert info_pre.attachments is not None
    steering_keys_pre = [
        k for k in info_pre.attachments if k.startswith(_STEERING_INPUT_KEY_PREFIX)
    ]
    assert len(steering_keys_pre) == 1

    # Trigger drain.
    drain_signal.set()
    await asyncio.sleep(0.5)

    # Post-drain: the steering attachment is gone.
    info_post = await manager_local.provider.get("t-drain-1")
    assert info_post is not None
    steering_keys_post = [
        k for k in (info_post.attachments or {}) if k.startswith(_STEERING_INPUT_KEY_PREFIX)
    ]
    assert steering_keys_post == [], (
        f"Steering attachments should be empty after drain; got {steering_keys_post}"
    )

    drain_signal.set()
    await run.cancel()


# --------------------------------------------------------------------------- #
# Orphan attachment cleanup
# --------------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_orphan_cleanup_deletes_unreferenced_steering_attachments(
    manager_local: TaskManager,
) -> None:
    """SC-12: orphaned _steering_input_* attachments are cleaned up on recovery."""

    # Manually plant a task in the local provider with an orphaned
    # steering attachment (a key whose ref is NOT in pending_inputs).
    from azure.ai.agentserver.core.durable._models import (
        LeaseInfo,
        TaskCreateRequest,
    )

    create = TaskCreateRequest(
        agent_name="s018-steer-agent",
        session_id="s018-steer-session",
        id="t-orphan-1",
        title="orphan-test",
        status="in_progress",
        lease_owner=manager_local._lease_owner,
        lease_instance_id="prior-instance-that-died",
        lease_duration_seconds=60,
        payload={
            "input": {"task": "noop"},
            "_steering": {
                "pending_inputs": [],  # empty — no refs
                "next_input_seq": 3,
                "cancel_requested": False,
            },
        },
        attachments={
            "_steering_input_0": "orphan-A",  # not referenced
            "_steering_input_1": "orphan-B",  # not referenced
            "_input": "real input",  # NOT a steering key — must be preserved
        },
    )
    await manager_local.provider.create(create)

    # Invoke the cleanup directly (it would normally fire from
    # _recover_stale_tasks before reclaim).
    task_info = await manager_local.provider.get("t-orphan-1")
    assert task_info is not None
    await manager_local._steering_cleanup_orphan_attachments(task_info)

    # Verify: orphan steering attachments are gone; _input is preserved.
    info_after = await manager_local.provider.get("t-orphan-1")
    assert info_after is not None
    keys_after = set(info_after.attachments or {})
    assert "_steering_input_0" not in keys_after
    assert "_steering_input_1" not in keys_after
    assert "_input" in keys_after  # non-steering attachment untouched
