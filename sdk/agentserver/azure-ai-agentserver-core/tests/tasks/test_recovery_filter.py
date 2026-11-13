# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
""" Area B — Recovery scan source_type filter (, SC-4).

Verifies that the framework's cold-start AND periodic recovery scans
pass ``source_type=_SOURCE_TYPE`` to ``provider.list(...)`` so that
tasks created by other systems sharing the same agent_name /
session_id / lease_owner are NOT picked up by the recovery path.

Reference: docs/task-and-streaming-spec.md §31, §49, §54, §D, §59
C-FLT-1.
"""

from __future__ import annotations

import asyncio
import datetime
from pathlib import Path

import pytest

from azure.ai.agentserver.core.tasks import TaskContext, task, multi_turn_task
import azure.ai.agentserver.core.tasks._manager as mgr_mod
from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
from azure.ai.agentserver.core.tasks._manager import TaskManager
from azure.ai.agentserver.core.tasks._models import TaskCreateRequest


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
    delegate = LocalFileTaskProvider(base_dir=tmp_path)
    return capturing_provider_factory(delegate)


@pytest.mark.asyncio
async def test_recovery_scan_passes_source_type(captured_local) -> None:
    """/ C-FLT-1 — the recovery scan's ``provider.list`` call
    MUST include ``source_type=<framework constant>``.

    Asserted by inspecting the captured ``list`` call kwargs from
    cold-start recovery.
    """
    manager = TaskManager(config=_config_stub(), provider=captured_local)
    mgr_mod._manager = manager
    await manager.startup()
    try:
        # Cold-start recovery happens during startup; the list call
        # is now captured.
        assert captured_local.list_calls, "expected at least one provider.list call during cold-start " "recovery"
        # Find recovery-scan list calls (status='in_progress').
        scan_calls = [c for c in captured_local.list_calls if c.get("status") == "in_progress"]
        assert scan_calls, (
            "expected at least one recovery-scan list call with " "status='in_progress' during cold-start recovery"
        )
        for call in scan_calls:
            assert call.get("source_type") == "agentserver.task", (
                f"recovery-scan list call did not include "
                f"source_type='agentserver.task';  / C-FLT-1 "
                f"require the framework to scope the scan to its own "
                f"records. Got kwargs: {call}"
            )
    finally:
        await manager.shutdown()
        mgr_mod._manager = None


@pytest.mark.asyncio
async def test_recovery_does_not_pick_up_foreign_typed_task(captured_local) -> None:
    """SC-4 /  — a foreign-typed task with matching (agent,
    session, lease_owner) MUST NOT be picked up by the recovery
    scan.

    Set up: pre-seed two in_progress records, both with the same
    agent_name / session_id / lease_owner triple. One has
    ``source.type = "agentserver.task"`` (framework-owned), the
    other has ``source.type = "third_party.runner"`` (foreign).
    Both have expired leases. After cold-start, the framework MUST
    have reclaimed only the framework-owned record.
    """

    @multi_turn_task(name="reclaim_target")
    async def my_task(ctx: TaskContext[str]) -> str:
        return "recovered"

    past = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=10)).isoformat()

    # Framework-owned record.
    await captured_local.create(
        TaskCreateRequest(
            id="t-ours",
            agent_name="test-agent",
            session_id="test-session",
            status="in_progress",
            title="ours",
            payload={"input": "x"},
            tags={"task_name": "reclaim_target"},
            source={"name": "reclaim_target", "type": "agentserver.task"},
            lease_owner="test-agent|session:test-session",
            lease_instance_id="prev-instance",
            lease_duration_seconds=60,
        )
    )
    foreign_record = await captured_local.create(
        TaskCreateRequest(
            id="t-foreign",
            agent_name="test-agent",
            session_id="test-session",
            status="in_progress",
            title="foreign",
            payload={"input": "y"},
            tags={"task_name": "third_party_task"},
            source={"name": "third_party_task", "type": "third_party.runner"},
            lease_owner="test-agent|session:test-session",
            lease_instance_id="prev-instance",
            lease_duration_seconds=60,
        )
    )
    # Backdate both leases.
    for tid in ("t-ours", "t-foreign"):
        stored = await captured_local._delegate.get(tid)  # noqa: SLF001
        stored.lease.expires_at = past
        captured_local._delegate._write_task(stored)  # noqa: SLF001

    captured_local.update_calls.clear()
    manager = TaskManager(config=_config_stub(), provider=captured_local)
    mgr_mod._manager = manager
    await manager.startup()
    try:
        # The foreign-typed record MUST NOT have been touched by any
        # reclaim PATCH issued during startup recovery.
        touched_foreign = [call for call in captured_local.update_calls if call[0] == "t-foreign"]
        assert not touched_foreign, (
            f"recovery scan picked up a foreign-typed task with "
            f"source.type='third_party.runner';  / C-FLT-1 "
            f"require the scan to filter by source_type. Touched: "
            f"{touched_foreign}"
        )
        # And the foreign record's lease_instance_id must still be
        # the original ('prev-instance'), proving no reclaim happened.
        snap = await captured_local._delegate.get("t-foreign")  # noqa: SLF001
        assert snap is not None
        assert snap.lease is not None
        assert snap.lease.instance_id == "prev-instance", (
            f"foreign-typed task's lease_instance_id changed from "
            f"'prev-instance' to {snap.lease.instance_id!r}; the "
            f"framework should never touch foreign-typed records "
            f"."
        )
    finally:
        await manager.shutdown()
        mgr_mod._manager = None
    # Silence unused-arg warning on the helper.
    _ = foreign_record


@pytest.mark.parametrize("recovery_path", ["startup", "periodic", "inline"])
@pytest.mark.asyncio
async def test_disabled_recovery_does_not_mutate_task(
    captured_local, monkeypatch: pytest.MonkeyPatch, recovery_path: str
) -> None:
    from azure.ai.agentserver.core.tasks import _decorator
    from azure.ai.agentserver.core.tasks._manager import _SCHEMA_VERSION, _SCHEMA_VERSION_KEY

    monkeypatch.setattr(_decorator, "_REGISTERED_DESCRIPTORS", [])
    monkeypatch.setattr(mgr_mod, "_manager", None)
    if recovery_path == "periodic":
        monkeypatch.setattr(mgr_mod, "_PERIODIC_RECOVERY_INTERVAL_SECONDS", 0.01)
    eligible_ran = asyncio.Event()
    excluded_calls = []

    @task(name="protocol_disabled")
    async def excluded(ctx: TaskContext[str]) -> str:
        excluded_calls.append(ctx.input)
        return "must not execute"

    @task(name="protocol_enabled")
    async def eligible(ctx: TaskContext[str]) -> str:
        eligible_ran.set()
        return "recovered"

    manager = TaskManager(config=_config_stub(), provider=captured_local)
    manager._disable_recovery_for(excluded.name)
    started = False
    try:
        if recovery_path != "startup":
            await manager.startup()
            started = True
        for primitive in (excluded, eligible):
            info = await captured_local.create(
                TaskCreateRequest(
                    id=primitive.name,
                    agent_name="test-agent",
                    session_id="test-session",
                    status="in_progress",
                    title=primitive.name,
                    payload={"input": "persisted", _SCHEMA_VERSION_KEY: _SCHEMA_VERSION},
                    tags={"task_name": primitive.name},
                    source=TaskManager._build_source(primitive.name),
                    lease_owner="test-agent|session:test-session",
                    lease_instance_id="interrupted-instance",
                    lease_duration_seconds=60,
                )
            )
            info.lease.expires_at = (
                datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=10)
            ).isoformat()
            captured_local._delegate._write_task(info)
        before = await captured_local.get(excluded.name)
        captured_local.update_calls.clear()
        if recovery_path == "startup":
            await manager.startup()
            started = True
        elif recovery_path == "inline":
            assert await manager.get_active_run(excluded.name) is None
            assert await manager.get_active_run(eligible.name) is not None
        await asyncio.wait_for(eligible_ran.wait(), timeout=5)
        if recovery_path == "periodic":

            async def wait_for_another_scan():
                while len(captured_local.list_calls) < 3:
                    await asyncio.sleep(0.01)

            await asyncio.wait_for(wait_for_another_scan(), timeout=5)
        after = await captured_local.get(excluded.name)
        assert excluded_calls == []
        assert after.status == before.status == "in_progress"
        assert after.etag == before.etag
        assert after.lease.instance_id == before.lease.instance_id == "interrupted-instance"
        assert after.lease.generation == before.lease.generation
        assert after.payload == before.payload
        assert not [call for call in captured_local.update_calls if call[0] == excluded.name]
    finally:
        if started:
            await manager.shutdown()
