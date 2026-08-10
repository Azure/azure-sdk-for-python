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
async def test_every_patch_carries_lease_extension_trio(captured_local) -> None:
    """— every PATCH the framework issues MUST carry the
    lease-extension trio (lease_owner, lease_instance_id,
    lease_duration_seconds) so every write doubles as a heartbeat.
    """

    @multi_turn_task(name="lease_trio_task")
    async def my_task(ctx: TaskContext[str]) -> str:
        ctx.metadata["k"] = 1
        await ctx.metadata.flush()
        return "ok"

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
async def test_dynamic_cadence_shadows_heartbeats(captured_local, monkeypatch) -> None:
    """/ SC-3 — under high metadata-flush traffic, the lease
    renewal loop's separate heartbeat PATCH count drops to 0 in the
    full-shadow regime: every flush PATCH carries the lease-extension
    trio, so the loop sees the lease was just refreshed and skips its
    own scheduled tick.

    Test setup: a handler that issues a metadata flush every 100ms
    for ~4 seconds. The lease is shrunk (via the ``_DEFAULT_LEASE_SECONDS``
    constant the manager reads when starting the renewal loop, plus the
    validation floor) so the renewal interval is ``max(1, lease // 2) = 1s``
    — well inside the test window, so the loop DOES tick several times and
    would emit heartbeats if the shadow logic were broken. We do NOT expect
    ANY PATCH that lacks a payload / tags / attachments / status / error
    change — i.e., a pure heartbeat-only PATCH (lease fields only, nothing
    else).
    """

    @multi_turn_task(name="dynamic_cadence")
    async def my_task(ctx: TaskContext[str]) -> str:
        # Issue many flushes spaced well under the renewal interval so
        # every scheduled heartbeat tick is shadowed by a recent flush.
        for i in range(40):
            ctx.metadata[f"flush_{i}"] = i
            await ctx.metadata.flush()
            await asyncio.sleep(0.1)
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
    # error / suspension_reason). Per  the dynamic cadence
    # should drive this count to 0 in the shadow window because each
    # flush already piggybacked the trio.
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

    assert heartbeat_count == 0, (
        f"expected 0 pure-heartbeat PATCHes in the dynamic-cadence "
        f"shadow window, got {heartbeat_count}. The lease renewal loop "
        f"should compute its next tick from the per-task last-refresh "
        f"time so that a recent flush shadows the next heartbeat "
        f"."
    )
