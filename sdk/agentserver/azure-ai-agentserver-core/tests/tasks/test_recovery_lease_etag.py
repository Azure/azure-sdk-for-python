# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Regression: cold-start recovery reclaim must refresh the tracked etag.

After ``_recover_stale_tasks`` reclaims a stale ``in_progress`` task, the
manager's tracked etag for that task MUST equal the provider's current
stored etag. Otherwise the first lease-renewal heartbeat sends the stale
pre-reclaim etag; both the ``LocalFileTaskProvider`` and the hosted task
API enforce ``If-Match`` strictly, so the renewal 412s and the renewal
loop misreads it as "lost ownership" — cancelling the recovered
execution roughly one lease half-life (~30s) in.

The bug: the cold-start scan reclaimed via a direct ``provider.update``
that discarded the post-reclaim record (and pre-tracked the *stale* scan
etag), so the heartbeat's tracked etag never advanced. The fix routes
the reclaim through ``_reclaim_one`` -> ``_provider_update_locked``
(which refreshes the tracked etag) and adopts the returned record.
"""

from __future__ import annotations

import datetime
from pathlib import Path

import pytest

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


async def _seed_stale_in_progress_task(provider: LocalFileTaskProvider, task_id: str = "t-recover") -> None:
    """Seed a framework-owned in_progress task whose lease is expired
    (simulating a crashed previous lifetime), so cold-start recovery
    reclaims it."""
    past = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=10)).isoformat()
    await provider.create(
        TaskCreateRequest(
            id=task_id,
            agent_name="test-agent",
            session_id="test-session",
            status="in_progress",
            title="recover",
            payload={"input": "x", "schema_version": "1"},
            tags={"task_name": "reclaim_target"},
            source={"name": "reclaim_target", "type": "agentserver.task"},
            lease_owner="test-agent|session:test-session",
            lease_instance_id="prev-instance",
            lease_duration_seconds=60,
        )
    )
    stored = await provider.get(task_id)
    assert stored is not None and stored.lease is not None
    stored.lease.expires_at = past
    provider._write_task(stored)  # noqa: SLF001


@pytest.mark.asyncio
async def test_recovery_reclaim_refreshes_tracked_etag(tmp_path: Path) -> None:
    """Cold-start reclaim leaves the tracked etag in sync with the store."""
    provider = LocalFileTaskProvider(base_dir=tmp_path)
    task_id = "t-recover"
    await _seed_stale_in_progress_task(provider, task_id)
    pre = await provider.get(task_id)
    assert pre is not None

    manager = TaskManager(config=_config_stub(), provider=provider)
    mgr_mod._manager = manager
    await manager.startup()
    try:
        post = await provider.get(task_id)
        assert post is not None and post.lease is not None

        # The reclaim happened: fresh etag + our instance now holds the lease.
        assert post.etag != pre.etag, "expected the cold-start scan to reclaim (re-write) the stale task"
        assert post.lease.instance_id == manager._instance_id  # noqa: SLF001

        # The invariant the bug violated: the manager's tracked etag must
        # equal the provider's post-reclaim etag, so the next lease-renewal
        # heartbeat's If-Match matches the store.
        assert manager._get_tracked_etag(task_id) == post.etag, (  # noqa: SLF001
            "cold-start reclaim left a stale tracked etag; the next lease "
            "renewal heartbeat would 412 and cancel recovery as 'lost ownership'"
        )
    finally:
        await manager.shutdown()
        mgr_mod._manager = None


@pytest.mark.asyncio
async def test_lease_renewal_after_recovery_does_not_412(tmp_path: Path) -> None:
    """A lease-renewal heartbeat after cold-start reclaim succeeds.

    Drives the heartbeat path directly (``_provider_update_locked`` with
    ``force_if_match=True``, exactly as ``lease_renewal_loop`` does). With
    the bug this raised an etag 412; with the fix it renews cleanly.
    """
    provider = LocalFileTaskProvider(base_dir=tmp_path)
    task_id = "t-recover"
    await _seed_stale_in_progress_task(provider, task_id)

    manager = TaskManager(config=_config_stub(), provider=provider)
    mgr_mod._manager = manager
    await manager.startup()
    try:
        # Simulate the renewal loop's heartbeat PATCH (lease-only, in_progress).
        renewed = await manager._provider_update_locked(  # noqa: SLF001
            task_id,
            TaskPatchRequest(
                lease_owner=manager._lease_owner,  # noqa: SLF001
                lease_instance_id=manager._instance_id,  # noqa: SLF001
                lease_duration_seconds=60,
            ),
        )
        assert renewed is not None
        # Lease still ours, and the tracked etag continues to track.
        assert renewed.lease is not None
        assert renewed.lease.instance_id == manager._instance_id  # noqa: SLF001
        assert manager._get_tracked_etag(task_id) == renewed.etag  # noqa: SLF001
    finally:
        await manager.shutdown()
        mgr_mod._manager = None
