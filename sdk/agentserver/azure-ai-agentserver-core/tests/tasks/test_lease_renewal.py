# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
""" Area A — Dynamic lease renewal cadence (, SC-3).

Verifies that the lease renewal loop:

- Includes the lease-extension trio (``lease_owner``,
  ``lease_instance_id``, ``lease_duration_seconds``) on every PATCH
  the framework issues, so every write doubles as a heartbeat
.
- Computes its next tick DYNAMICALLY from the per-task last-refresh
  time, NOT a fixed cadence. A PATCH within the last interval-seconds
  shadows the next heartbeat (/ SC-3).

Reference: docs/task-and-streaming-spec.md §22, §31, §56, §59 C-LSE-1.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from azure.ai.agentserver.core.tasks import TaskContext, task, multi_turn_task
import azure.ai.agentserver.core.tasks._manager as mgr_mod
from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
from azure.ai.agentserver.core.tasks._manager import TaskManager


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
async def test_every_patch_carries_lease_extension_trio(captured_local, monkeypatch) -> None:
    """— every PATCH the framework issues MUST carry the
    lease-extension trio (lease_owner, lease_instance_id,
    lease_duration_seconds) so every write doubles as a heartbeat.
    """

    @multi_turn_task(name="lease_trio_task")
    async def my_task(ctx: TaskContext[str]) -> str:
        await asyncio.sleep(1.2)
        return "ok"

    import azure.ai.agentserver.core.tasks._validation as val_mod

    monkeypatch.setattr(val_mod, "LEASE_DURATION_MIN", 1)
    monkeypatch.setattr(mgr_mod, "_DEFAULT_LEASE_SECONDS", 2)

    manager = TaskManager(config=_config_stub(), provider=captured_local)
    mgr_mod._manager = manager
    await manager.startup()
    try:
        await my_task.run(task_id="t-trio", input="x")
    finally:
        await manager.shutdown()
        mgr_mod._manager = None

    assert captured_local.update_calls, "expected at least one PATCH"
    for idx, (_task_id, patch, _if_match) in enumerate(captured_local.update_calls):
        # The terminal write doesn't extend the lease (it transitions
        # the task out of in_progress). For non-terminal PATCHes, the
        # trio MUST be present.
        if patch.status in ("completed", "suspended"):
            continue
        assert patch.lease_owner is not None, f"PATCH {idx} missing lease_owner "
        assert patch.lease_instance_id is not None, f"PATCH {idx} missing lease_instance_id "
        assert patch.lease_duration_seconds is not None, f"PATCH {idx} missing lease_duration_seconds "


@pytest.mark.asyncio
async def test_application_state_writes_do_not_shadow_heartbeats(captured_local, monkeypatch) -> None:
    """Application-owned state activity does not renew the task lease.

    State Store writes are independent from the task record, so the lease
    renewal loop must continue emitting heartbeat-only task PATCHes while
    application state changes.
    """

    @multi_turn_task(name="dynamic_cadence")
    async def my_task(ctx: TaskContext[str]) -> str:
        application_state: dict[str, int] = {}
        for i in range(40):
            application_state[f"write_{i}"] = i
            await asyncio.sleep(0.1)
        assert len(application_state) == 40
        return "ok"

    # Shrink the lease so the renewal interval (max(1, lease // 2) = 1s) is
    # well inside the ~4s test window; the default 60s lease yields a 30s
    # interval, so the loop would never tick and this test would pass
    # vacuously. The lease-duration knob has no public setter, so patch the
    # constant the manager reads plus the validation floor that would
    # otherwise reject a sub-10s lease.
    import azure.ai.agentserver.core.tasks._validation as val_mod

    monkeypatch.setattr(val_mod, "LEASE_DURATION_MIN", 1)
    monkeypatch.setattr(mgr_mod, "_DEFAULT_LEASE_SECONDS", 2)

    manager = TaskManager(config=_config_stub(), provider=captured_local)
    mgr_mod._manager = manager
    await manager.startup()
    try:
        await my_task.run(task_id="t-dynamic", input="x")
    finally:
        await manager.shutdown()
        mgr_mod._manager = None

    # Identify pure-heartbeat PATCHes: ones that carry ONLY the
    # lease-extension trio (no payload / tags / attachments / status /
    # error / suspension_reason).
    heartbeat_count = 0
    for _task_id, patch, _if_match in captured_local.update_calls:
        if (
            patch.payload is None
            and patch.tags is None
            and patch.attachments is None
            and patch.status is None
            and patch.error is None
            and patch.suspension_reason is None
            and patch.lease_owner is not None
        ):
            heartbeat_count += 1

    assert heartbeat_count >= 1, "application state activity must not suppress task lease heartbeats"
