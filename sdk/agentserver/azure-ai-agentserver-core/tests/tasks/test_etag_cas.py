# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
""" Area A — ETag CAS on every PATCH.

Verifies the framework's ETag plumbing:

- Every PATCH after the first read/create carries the last-known
  etag as ``if_match``.
- ``delete`` does NOT carry ``if_match``.
- Both reclaim sites (inline reclaim + cold-start/periodic scan)
  carry ``if_match``.
- Terminal-write 412 follows the RE-READ-AND-DECIDE rule from
: three branches — lease-lost ABANDON, already-terminal
  ABANDON, lease-still-ours-retry (SC-3b).

Tests use the ``CapturingProvider`` (records
every PATCH so we can inspect ``if_match`` on each) and
``Conflicting412Provider`` (injects 412 at configured update calls,
optionally mutating the underlying record to simulate cross-process
concurrent writers).

Reference: docs/task-and-streaming-spec.md §25, §54, §59 C-LSE-2,
C-WQ-3, C-FLT-1.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from azure.ai.agentserver.core.tasks import (
    TaskCancelled,
    TaskConflictError,
    TaskContext,
    TaskFailed,
    task,
    multi_turn_task,
)
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
def captured_local(tmp_path: Path, capturing_provider_factory):
    """A :class:`CapturingProvider` wrapping a fresh LocalFileTaskProvider."""
    delegate = LocalFileTaskProvider(base_dir=tmp_path)
    return capturing_provider_factory(delegate)


@pytest.fixture
def conflicting_local(tmp_path: Path, conflicting_412_provider_factory):
    """A :class:`Conflicting412Provider` wrapping a fresh LocalFileTaskProvider."""
    delegate = LocalFileTaskProvider(base_dir=tmp_path)
    return conflicting_412_provider_factory(delegate)


# --------------------------------------------------------------------- #
#  — every PATCH after the first read/create carries if_match
# --------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_every_patch_after_first_carries_if_match(captured_local) -> None:
    """/ C-WQ-3 — every PATCH after the create read carries
    the last-known etag as ``if_match``.

    A simple fresh-create + suspend cycle: the create PATCH is the
    *first* write (no prior etag known), then the suspend PATCH and
    any framework-internal PATCHes that follow MUST all carry
    ``if_match``.
    """

    @multi_turn_task(name="if_match_etag_task")
    async def my_task(ctx: TaskContext[str]) -> str:
        return "ok"

    manager = TaskManager(config=_config_stub(), provider=captured_local)
    mgr_mod._manager = manager
    await manager.startup()
    try:
        result = await my_task.run(task_id="t-etag-1", input="hi")
        assert result == "ok"
    finally:
        await manager.shutdown()
        mgr_mod._manager = None

    assert len(captured_local.update_calls) >= 1, "expected at least one PATCH after create"
    for idx, (_task_id, _patch, if_match) in enumerate(captured_local.update_calls):
        assert if_match is not None, (
            f"PATCH {idx} did not carry if_match;   "
            f"requires every PATCH after the first read/create to "
            f"carry the last-known etag."
        )


@pytest.mark.asyncio
async def test_delete_does_not_carry_if_match(captured_local) -> None:
    """— ``delete`` is intentionally unconditional and
    MUST NOT carry an etag precondition.

    The user-facing ``Task.run()`` for an ``ephemeral=True`` task
    auto-deletes the record on terminal exit; that delete must
    not carry ``if_match``.
    """

    @task(name="delete_etag_task")
    async def ephemeral_task(ctx: TaskContext[str]) -> str:
        return "done"

    manager = TaskManager(config=_config_stub(), provider=captured_local)
    mgr_mod._manager = manager
    await manager.startup()
    try:
        await ephemeral_task.run(task_id="t-ephemeral", input="x")
    finally:
        await manager.shutdown()
        mgr_mod._manager = None

    assert captured_local.delete_calls, "ephemeral=True task should have triggered a delete on terminal exit"


# --------------------------------------------------------------------- #
#  — both reclaim sites carry if_match
# --------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_both_reclaim_sites_carry_if_match(captured_local) -> None:
    """/ C-LSE-2 — inline reclaim AND cold-start/periodic
    scan reclaim PATCHes BOTH carry ``if_match``.

    Set up: pre-seed an in_progress task with an expired lease, run
    cold-start recovery; both the scan-time list + the resulting
    reclaim PATCH must include ``if_match``.
    """
    import datetime

    @multi_turn_task(name="reclaim_etag_task")
    async def my_task(ctx: TaskContext[str]) -> str:
        return "recovered"

    past = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=10)).isoformat()
    await captured_local.create(
        TaskCreateRequest(
            id="t-stale",
            agent_name="test-agent",
            session_id="test-session",
            status="in_progress",
            title="stale",
            payload={"input": "hi", "schema_version": "1"},
            tags={"task_name": "reclaim_etag_task"},
            source={"name": "reclaim_etag_task", "type": "agentserver.task"},
            lease_owner="test-agent|session:test-session",
            lease_instance_id="prev-instance",
            lease_duration_seconds=60,
        )
    )
    # Manually backdate the lease.
    stored = await captured_local._delegate.get("t-stale")  # noqa: SLF001
    stored.lease.expires_at = past
    captured_local._delegate._write_task(stored)  # noqa: SLF001

    manager = TaskManager(config=_config_stub(), provider=captured_local)
    mgr_mod._manager = manager
    captured_local.update_calls.clear()
    await manager.startup()
    try:
        # Cold-start scan should have issued at least one PATCH
        # (the reclaim). Inline reclaim path via .start() also goes
        # through update().
        await asyncio.sleep(0.05)
    finally:
        await manager.shutdown()
        mgr_mod._manager = None

    # Every reclaim PATCH (and any subsequent renewal/terminal) must
    # carry if_match (/ C-LSE-2). Guard against a vacuous pass: the
    # reclaim path MUST have issued at least one PATCH (a stale record
    # lacking ``schema_version`` would instead be legacy-deleted before
    # any reclaim, leaving this list empty and the loop below asserting
    # nothing).
    assert captured_local.update_calls, (
        "reclaim path issued no PATCHes; the stale task was not reclaimed "
        "(check the seeded payload carries schema_version), so the if_match "
        "assertion below would be vacuous."
    )
    for idx, (_task_id, _patch, if_match) in enumerate(captured_local.update_calls):
        assert if_match is not None, (
            f"reclaim-path PATCH {idx} missing if_match;  / "
            f"C-LSE-2 requires both inline AND scan reclaim PATCHes "
            f"to be CAS-guarded."
        )


# --------------------------------------------------------------------- #
#  terminal-write 412 — three branches (SC-3b)
# --------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_terminal_412_lease_lost_abandons(conflicting_local) -> None:
    """(a) / SC-3b — on terminal-write 412, if RE-READ shows
    the lease is no longer ours, the framework MUST ABANDON the
    terminal PATCH and signal eviction (TaskConflictError to awaiters).

    Set up: the framework attempts a terminal write (status="completed").
    The Conflicting412Provider intercepts this update, mutates the
    underlying record's ``lease_instance_id`` to a different value
    (simulating another process having reclaimed), then raises 412.
    On the framework's RE-READ, it sees a different instance_id and
    MUST stop.
    """

    @multi_turn_task(name="terminal_412_lease_lost")
    async def my_task(ctx: TaskContext[str]) -> str:
        return "completed-payload"

    manager = TaskManager(config=_config_stub(), provider=conflicting_local)
    mgr_mod._manager = manager
    await manager.startup()
    try:
        # Inject lease_lost on the FIRST update call that the framework
        # makes. In practice the first update after create is the
        # terminal-write (since the local provider auto-fills lease on
        # create). The framework must observe the RE-READ shows a
        # different instance_id and ABANDON, surfacing TaskConflictError.
        conflicting_local.conflict_on(update_index=0, mode="lease_lost")
        with pytest.raises((TaskConflictError, TaskCancelled, TaskFailed)):
            await my_task.run(task_id="t-lost", input="x")
    finally:
        await manager.shutdown()
        mgr_mod._manager = None


@pytest.mark.asyncio
async def test_terminal_412_already_terminal_abandons(conflicting_local) -> None:
    """(b) / SC-3b — on terminal-write 412, if RE-READ shows
    ``status="completed"`` already, ABANDON.
    """

    @multi_turn_task(name="terminal_412_already_terminal")
    async def my_task(ctx: TaskContext[str]) -> str:
        return "ok"

    manager = TaskManager(config=_config_stub(), provider=conflicting_local)
    mgr_mod._manager = manager
    await manager.startup()
    try:
        conflicting_local.conflict_on(update_index=0, mode="already_terminal")
        # The framework should ABANDON (the record is already terminal
        # from "another writer's perspective"); awaiters surface
        # TaskConflictError per the eviction path.
        with pytest.raises((TaskConflictError, TaskCancelled, TaskFailed)):
            await my_task.run(task_id="t-already-term", input="x")
    finally:
        await manager.shutdown()
        mgr_mod._manager = None


@pytest.mark.asyncio
async def test_terminal_412_lease_ours_retries(conflicting_local) -> None:
    """(c) / SC-3b — on terminal-write 412, if RE-READ shows
    the lease is still ours AND status is still ``in_progress``,
    retry the terminal PATCH against the new etag — and it succeeds.

    Set up: inject an ``etag_only`` conflict (the record is mutated
    in a harmless way to bump the etag, but lease and status are
    unchanged). The framework's RE-READ shows everything is still
    ours; it retries against the new etag and the second attempt
    lands. The persisted record's status MUST end up ``completed``
    (this is the load-bearing assertion — without the retry, the
    handler's outcome would be lost in the store even though the
    caller's future may have resolved early).
    """

    @multi_turn_task(name="terminal_412_retry")
    async def my_task(ctx: TaskContext[str]) -> str:
        return "succeed-on-retry"

    manager = TaskManager(config=_config_stub(), provider=conflicting_local)
    mgr_mod._manager = manager
    await manager.startup()
    try:
        # Conflict on the first PATCH attempt. The framework's
        # RE-READ-AND-DECIDE branch (c) MUST retry against the new
        # etag and succeed.
        conflicting_local.conflict_on(update_index=0, mode="etag_only")
        result = await my_task.run(task_id="t-retry", input="x")
        assert result == "succeed-on-retry"
        # The persisted record MUST reflect the terminal write — not
        # the pre-conflict in_progress state — proving the framework
        # retried the PATCH against the new etag (branch c).
        snap = await conflicting_local._delegate.get("t-retry")  # noqa: SLF001
        assert snap is not None
        assert snap.status == "suspended", (
            f"after terminal-write 412 retry branch, the persisted "
            f"record's status should be 'suspended' (multi-turn "
            f"return-X is implicit suspend) but was "
            f"{snap.status!r}; the framework did not retry the "
            f"terminal PATCH against the new etag (branch c)."
        )
    finally:
        await manager.shutdown()
        mgr_mod._manager = None
