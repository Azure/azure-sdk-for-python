# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Spec 019 Area A — Dynamic lease renewal cadence (FR-A-004/-005, SC-3).

Verifies that the lease renewal loop:

- Includes the lease-extension trio (``lease_owner``,
  ``lease_instance_id``, ``lease_duration_seconds``) on every PATCH
  the framework issues, so every write doubles as a heartbeat
  (FR-A-004).
- Computes its next tick DYNAMICALLY from the per-task last-refresh
  time, NOT a fixed cadence. A PATCH within the last interval-seconds
  shadows the next heartbeat (FR-A-005 / SC-3).

Reference: docs/task-and-streaming-spec.md §22, §31, §56, §59 C-LSE-1.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from azure.ai.agentserver.core.durable import TaskContext, task
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
def captured_local(tmp_path: Path, capturing_provider_factory):
    delegate = LocalFileTaskProvider(base_dir=tmp_path)
    return capturing_provider_factory(delegate)


@pytest.mark.asyncio
async def test_every_patch_carries_lease_extension_trio(captured_local) -> None:
    """FR-A-004 — every PATCH the framework issues MUST carry the
    lease-extension trio (lease_owner, lease_instance_id,
    lease_duration_seconds) so every write doubles as a heartbeat.
    """
    @task(name="lease_trio_task", ephemeral=False)
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
        assert patch.lease_owner is not None, (
            f"PATCH {idx} missing lease_owner (FR-A-004)"
        )
        assert patch.lease_instance_id is not None, (
            f"PATCH {idx} missing lease_instance_id (FR-A-004)"
        )
        assert patch.lease_duration_seconds is not None, (
            f"PATCH {idx} missing lease_duration_seconds (FR-A-004)"
        )


@pytest.mark.asyncio
async def test_dynamic_cadence_shadows_heartbeats(captured_local) -> None:
    """FR-A-005 / SC-3 — under high metadata-flush traffic, the lease
    renewal loop's separate heartbeat PATCH count drops to 0 in the
    full-shadow regime: every flush PATCH carries the lease-extension
    trio, so the loop sees the lease was just refreshed and skips its
    own scheduled tick.

    Test setup: a handler that issues a metadata flush every 100ms
    for ~3 seconds. The lease renewal interval is much shorter than
    the test window (default 30s — but tests can use a tighter
    duration). We do NOT expect ANY PATCH that lacks a payload /
    tags / attachments / status / error change — i.e., a pure
    heartbeat-only PATCH (lease fields only, nothing else).
    """
    @task(name="dynamic_cadence", ephemeral=False)
    async def my_task(ctx: TaskContext[str]) -> str:
        # Issue many flushes spaced << default renewal interval.
        for i in range(20):
            ctx.metadata[f"flush_{i}"] = i
            await ctx.metadata.flush()
            await asyncio.sleep(0.05)
        return "ok"

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
    # error / suspension_reason). Per FR-A-005 the dynamic cadence
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
        f"(FR-A-005)."
    )
