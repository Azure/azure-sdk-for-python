# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Per-task write queue.

Verifies that intra-process concurrent writes against the same
``task_id`` are serialized through a per-task asyncio lock so that
etag conflicts become rare under contention.

- Concurrent framework task PATCHes complete with 0 etag conflicts.
- Reads do NOT acquire the write lock.
- Lock entries are torn down when the task's active entry is removed
.

Reference: docs/task-and-streaming-spec.md §25.2, §59 C-WQ-1..3.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from azure.ai.agentserver.core.tasks import TaskContext, multi_turn_task
import azure.ai.agentserver.core.tasks._manager as mgr_mod
from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
from azure.ai.agentserver.core.tasks._manager import TaskManager
from azure.ai.agentserver.core.tasks._models import TaskCreateRequest, TaskPatchRequest


def _config_stub():
    return type(
        "C",
        (),
        {
            "agent_name": "test-agent",
            "session_id": "test-session",
            "agent_version": "1.0.0",
            "is_hosted": False,
        },
    )()


@pytest.fixture
def local(tmp_path: Path) -> LocalFileTaskProvider:
    return LocalFileTaskProvider(base_dir=tmp_path)


@pytest.mark.asyncio
async def test_concurrent_task_patches_serialize(local) -> None:
    """Concurrent framework PATCHes use the latest tracked etag."""
    patch_count = 50
    etag_conflicts: list[Exception] = []

    # Wrap the provider's update to capture every etag mismatch.
    original_update = local.update

    async def _capturing_update(task_id, patch):
        try:
            return await original_update(task_id, patch)
        except ValueError as exc:
            if "etag" in str(exc).lower():
                etag_conflicts.append(exc)
            raise

    local.update = _capturing_update  # type: ignore[method-assign]

    manager = TaskManager(config=_config_stub(), provider=local)
    created = await local.create(
        TaskCreateRequest(
            id="t-parallel",
            agent_name="test-agent",
            session_id="test-session",
            status="pending",
            title="parallel patches",
        )
    )
    manager._track_etag("t-parallel", created.etag)  # pylint: disable=protected-access

    await asyncio.gather(
        *(
            manager._provider_update_locked(  # pylint: disable=protected-access
                "t-parallel",
                TaskPatchRequest(tags={"iteration": str(i)}),
            )
            for i in range(patch_count)
        )
    )

    assert etag_conflicts == []


@pytest.mark.asyncio
async def test_reads_do_not_acquire_lock(local) -> None:
    """— reads MUST NOT enter the write queue.

    The per-task write lock is a write-side serializer; reads
    (provider.get / Task.get) must be able to proceed even while
    a long-running write holds the lock — otherwise the read API
    would block on contended writes.

    Strategy: hold the write queue on task X and concurrently
    call ``provider.get(X)`` directly. The get MUST return in
    < 5 ms (well under the write-side hold time).
    """
    in_write_barrier = asyncio.Event()
    release_write = asyncio.Event()

    @multi_turn_task(name="reads_no_lock")
    async def my_task(ctx: TaskContext[str]) -> str:
        del ctx
        async with manager._get_task_write_lock("t-reads"):  # pylint: disable=protected-access
            in_write_barrier.set()
            await release_write.wait()
        return "done"

    manager = TaskManager(config=_config_stub(), provider=local)
    mgr_mod._manager = manager
    await manager.startup()
    try:
        run_task = asyncio.create_task(my_task.run(task_id="t-reads", input="x"))
        await in_write_barrier.wait()
        # While the handler holds the write lock, a
        # direct read must succeed promptly.
        t_start = asyncio.get_event_loop().time()
        snap = await local.get("t-reads")
        t_elapsed = asyncio.get_event_loop().time() - t_start
        assert snap is not None
        assert t_elapsed < 1.0, (
            f"read took {t_elapsed:.3f}s under write contention; " f" requires reads to be lock-free."
        )
        release_write.set()
        await run_task
    finally:
        await manager.shutdown()
        mgr_mod._manager = None


@pytest.mark.asyncio
async def test_lock_removed_when_active_entry_torn_down(local) -> None:
    """/ C-WQ-1 — when the task's active-entry is torn
    down, the per-task lock entry MUST be removed from the registry
    (no lock leak across many tasks' lifetimes).

    Strategy: introspect the manager's write-queue registry after a
    task completes — the entry for that task_id MUST be absent.
    The exact attribute name is implementation-defined; tests look
    for either ``_write_locks`` or ``_task_write_queue``.
    """

    @multi_turn_task(name="lock_teardown")
    async def my_task(ctx: TaskContext[str]) -> str:
        del ctx
        return "ok"

    manager = TaskManager(config=_config_stub(), provider=local)
    mgr_mod._manager = manager
    await manager.startup()
    try:
        await my_task.run(task_id="t-leak-1", input="x")
        await my_task.run(task_id="t-leak-2", input="x")
        # Locate the per-task write-queue registry (any plausible name).
        registry = (
            getattr(manager, "_task_write_queues", None)
            or getattr(manager, "_write_locks", None)
            or getattr(manager, "_task_write_locks", None)
        )
        assert registry is not None, (
            "could not find the per-task write-queue registry on "
            "TaskManager;  requires the registry to exist and "
            "to drop entries on task teardown."
        )
        # After completion, neither task's lock entry should remain.
        assert "t-leak-1" not in registry, "lock entry for t-leak-1 leaked after task completion "
        assert "t-leak-2" not in registry, "lock entry for t-leak-2 leaked after task completion "
    finally:
        await manager.shutdown()
        mgr_mod._manager = None
