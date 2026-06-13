# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Spec 019 Area C — Public ``Task.get`` + ``TaskSnapshot``
(FR-C-001..003, SC-5..7).

Verifies:

- ``Task.get(task_id)`` is an instance method on the per-decorator
  ``Task`` handle (mirrors ``Task.get_active_run`` shape) returning
  ``TaskSnapshot | None`` (FR-C-001).
- Returns ``None`` for missing/deleted tasks (does NOT raise
  ``TaskNotFound``) — FR-C-001.
- Returns the expected ``TaskSnapshot`` for tasks in EACH status
  (pending, in_progress, suspended, completed) — SC-5.
- ``TaskSnapshot`` exposes ONLY the documented fields; no internal
  field leaks (lease / etag / source / attachments / _ prefixed
  payload keys) — FR-C-002 / SC-6.
- ``TaskSnapshot.output`` is the resolved value of any promoted
  ``_output`` attachment (not the ref structure) — FR-C-003.
- Calling ``Task.get`` before the manager is initialized raises
  ``RuntimeError`` — FR-C-001 / US-C1.C1.6.

Reference: docs/task-and-streaming-spec.md §32 / §33 / §35a, §59
C-INTROSPECT-1..8.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from azure.ai.agentserver.core.durable import Suspended, TaskContext, task
import azure.ai.agentserver.core.durable._manager as mgr_mod
from azure.ai.agentserver.core.durable._local_provider import LocalFileTaskProvider
from azure.ai.agentserver.core.durable._manager import TaskManager


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


# --------------------------------------------------------------------- #
# FR-C-001 — Task.get instance method exists and returns snapshot/None
# --------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_task_get_returns_none_for_missing(local) -> None:
    """FR-C-001 — Task.get(task_id) returns None for a non-existent
    task (does NOT raise TaskNotFound).
    """
    @task(name="get_none_task", ephemeral=False)
    async def my_task(ctx: TaskContext[str]) -> str:
        return "ok"

    manager = TaskManager(config=_config_stub(), provider=local)
    mgr_mod._manager = manager
    await manager.startup()
    try:
        snap = await my_task.get("does-not-exist")
        assert snap is None, (
            f"Task.get of a non-existent id MUST return None, got "
            f"{snap!r} (FR-C-001 / US-C1.C1.2)"
        )
    finally:
        await manager.shutdown()
        mgr_mod._manager = None


@pytest.mark.asyncio
async def test_task_get_raises_runtime_error_without_manager() -> None:
    """FR-C-001 / US-C1.C1.6 — calling Task.get before the
    TaskManager singleton is initialized MUST raise RuntimeError.
    """
    @task(name="no_manager_task", ephemeral=False)
    async def my_task(ctx: TaskContext[str]) -> str:
        return "ok"

    # Defensive: no manager installed.
    mgr_mod._manager = None
    with pytest.raises(RuntimeError):
        await my_task.get("any-id")


@pytest.mark.asyncio
async def test_task_get_returns_snapshot_for_each_status(local) -> None:
    """SC-5 — Task.get returns the expected TaskSnapshot for tasks
    in every status: pending, in_progress, suspended, completed.

    Spec 019 SC-5 / C-INTROSPECT-3 — explicit coverage of every
    legal stored status.
    """
    import asyncio
    from azure.ai.agentserver.core.durable import Suspended, TaskSnapshot

    in_handler = asyncio.Event()
    release_handler = asyncio.Event()

    @task(name="get_snap_task", ephemeral=False)
    async def my_task(ctx: TaskContext[str]) -> str:
        return "completed-output"

    @task(name="get_snap_suspendable", ephemeral=False)
    async def suspendable_task(ctx: TaskContext[str]) -> Suspended[str]:
        return await ctx.suspend(output="paused", reason="probe")

    @task(name="get_snap_blocked", ephemeral=False)
    async def blocking_task(ctx: TaskContext[str]) -> str:
        in_handler.set()
        await release_handler.wait()
        return "released"

    manager = TaskManager(config=_config_stub(), provider=local)
    mgr_mod._manager = manager
    await manager.startup()
    try:
        # === completed ===
        result = await my_task.run(task_id="t-snap-complete", input="hi")
        assert result == "completed-output"
        snap = await my_task.get("t-snap-complete")
        assert snap is not None and isinstance(snap, TaskSnapshot)
        assert snap.task_id == "t-snap-complete"
        assert snap.status == "completed"
        assert snap.output == "completed-output"
        assert snap.completed_at is not None
        assert snap.error is None

        # === suspended ===
        sus = await suspendable_task.run(task_id="t-snap-suspended", input="x")
        assert sus.is_suspended
        snap_sus = await suspendable_task.get("t-snap-suspended")
        assert snap_sus is not None and isinstance(snap_sus, TaskSnapshot)
        assert snap_sus.status == "suspended"
        assert snap_sus.output == "paused"
        assert snap_sus.suspension_reason == "probe"

        # === in_progress ===
        run_task = asyncio.create_task(
            blocking_task.run(task_id="t-snap-in-progress", input="x")
        )
        await asyncio.wait_for(in_handler.wait(), timeout=2.0)
        snap_in_progress = await blocking_task.get("t-snap-in-progress")
        assert snap_in_progress is not None
        assert snap_in_progress.status == "in_progress"
        assert snap_in_progress.started_at is not None
        assert snap_in_progress.completed_at is None
        release_handler.set()
        await run_task

        # === pending ===
        # Pre-seed a pending record (no .start()/.run() to trigger
        # automatic in_progress). Task.get must return status='pending'.
        from azure.ai.agentserver.core.durable._models import TaskCreateRequest

        await local.create(
            TaskCreateRequest(
                id="t-snap-pending",
                agent_name="test-agent",
                session_id="test-session",
                status="pending",
                title="probe-pending",
                payload={"input": "x"},
                source={"name": "get_snap_task", "type": "agentserver.task"},
            )
        )
        snap_pending = await my_task.get("t-snap-pending")
        assert snap_pending is not None
        assert snap_pending.status == "pending"
        assert snap_pending.started_at is None
        assert snap_pending.completed_at is None
        assert snap_pending.output is None
    finally:
        await manager.shutdown()
        mgr_mod._manager = None


# --------------------------------------------------------------------- #
# FR-C-002 / SC-6 — TaskSnapshot exposes only documented fields
# --------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_task_snapshot_exposes_only_documented_fields(local) -> None:
    """FR-C-002 / SC-6 — TaskSnapshot MUST NOT expose internal fields:
    lease (whole object), tags, source, attachments (raw), etag, or
    framework-internal payload keys starting with ``_``.

    Asserted by inspecting the snapshot's attributes against the
    documented allowlist.
    """
    from azure.ai.agentserver.core.durable import TaskSnapshot

    @task(name="snap_field_excl", ephemeral=False)
    async def my_task(ctx: TaskContext[str]) -> str:
        return "ok"

    manager = TaskManager(config=_config_stub(), provider=local)
    mgr_mod._manager = manager
    await manager.startup()
    try:
        await my_task.run(task_id="t-snap-fields", input="x")
        snap = await my_task.get("t-snap-fields")
        assert snap is not None
    finally:
        await manager.shutdown()
        mgr_mod._manager = None

    # Documented fields (design-spec §35a).
    allowed_fields = {
        "task_id",
        "status",
        "created_at",
        "updated_at",
        "started_at",
        "completed_at",
        "output",
        "error",
        "suspension_reason",
        "metadata",
        "lease_expiry_count",
    }
    # Forbidden fields — these are framework-internal and MUST NOT
    # leak onto the snapshot's public attribute surface.
    forbidden_fields = {
        "lease",
        "tags",
        "source",
        "attachments",
        "etag",
        "payload",
        "_steering",
        "_retry_attempt",
        "_turn_started_at",
    }

    public_attrs = {a for a in dir(snap) if not a.startswith("_")}
    leaked = public_attrs & forbidden_fields
    assert not leaked, (
        f"TaskSnapshot leaks framework-internal fields: {sorted(leaked)}; "
        f"FR-C-002 / SC-6 / US-C1.C1.4 forbid these from the public "
        f"snapshot surface."
    )
    # And every documented field MUST be present.
    missing = allowed_fields - public_attrs
    assert not missing, (
        f"TaskSnapshot missing documented fields: {sorted(missing)}"
    )


@pytest.mark.asyncio
async def test_task_snapshot_resolves_output_ref(local) -> None:
    """FR-C-003 — TaskSnapshot.output MUST resolve promoted ``_output``
    attachments transparently — the developer sees the value, not the
    ref structure.

    Strategy: complete a task with a non-trivial output, then read the
    snapshot; output MUST be the value the handler returned, not a
    ``{"__attachment_ref__": ...}`` dict.
    """
    @task(name="snap_resolves_ref", ephemeral=False)
    async def my_task(ctx: TaskContext[str]) -> dict:
        # A non-trivial payload that will be promoted to _output.
        return {"phase": "done", "items": list(range(100))}

    manager = TaskManager(config=_config_stub(), provider=local)
    mgr_mod._manager = manager
    await manager.startup()
    try:
        await my_task.run(task_id="t-snap-ref", input="x")
        snap = await my_task.get("t-snap-ref")
        assert snap is not None
        assert isinstance(snap.output, dict)
        # Must be the resolved value, not the ref shape.
        assert "__attachment_ref__" not in snap.output, (
            f"snapshot.output leaks the ref shape; FR-C-003 / "
            f"C-INTROSPECT-5 require the snapshot to resolve refs "
            f"transparently. Got: {snap.output!r}"
        )
        assert snap.output.get("phase") == "done"
        assert snap.output.get("items") == list(range(100))
    finally:
        await manager.shutdown()
        mgr_mod._manager = None
