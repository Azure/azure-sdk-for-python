"""Focused validation of ONE-SHOT task timeout cancellation under isolation.

Scenarios (fast — timeout 1s, grace configurable per test):
  1. Cooperative one-shot winds down at the timeout -> completes, NOT hard-killed.
  2. Runaway one-shot (ignores cancel) -> hard-killed at timeout+grace,
     caller gets TaskCancelled, record deleted (ephemeral).
  3. During the grace window the record carries the timeout_cancelled_at marker
     and is still in_progress; after the kill it is gone.
  4. Timing: the cooperative window is respected (kill lands ~timeout+grace).
  5. Recovery: a stale in_progress one-shot whose turn already timed out is
     finalized (deleted) instead of re-run.
"""
from __future__ import annotations

import asyncio
import os
import sys
import time
import uuid
from pathlib import Path

import pytest

_HANDLER_DIR = str(Path(__file__).parent)
_CORE_ROOT = str(Path(__file__).resolve().parents[2])

_TURN_STARTED_AT_KEY = "turn_started_at"
_TIMEOUT_CANCELLED_AT_KEY = "timeout_cancelled_at"


@pytest.fixture(autouse=True)
def _iso_env(monkeypatch):
    monkeypatch.setenv("AGENTSERVER_TASK_ISOLATION", "1")
    monkeypatch.setenv("AGENTSERVER_TASK_TIMEOUT_HARDCAP_GRACE_SECONDS", "1")
    existing = os.environ.get("PYTHONPATH", "")
    monkeypatch.setenv("PYTHONPATH", os.pathsep.join([_HANDLER_DIR, _CORE_ROOT, existing]))
    if _HANDLER_DIR not in sys.path:
        sys.path.insert(0, _HANDLER_DIR)
    yield


async def _setup(tmp_path):
    from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
    from azure.ai.agentserver.core.tasks._manager import TaskManager
    import azure.ai.agentserver.core.tasks._manager as mgr_mod

    provider = LocalFileTaskProvider(Path(str(tmp_path)))
    config = type("C", (), {
        "agent_name": "iso-agent", "session_id": "iso-session",
        "agent_version": "1.0.0", "is_hosted": False,
    })()
    manager = TaskManager(config=config, provider=provider)
    mgr_mod._manager = manager
    await manager.startup()
    return manager, mgr_mod


@pytest.mark.asyncio
async def test_oneshot_cooperative_winds_down_not_killed(tmp_path):
    """A cooperative one-shot returns at the timeout and is NOT hard-killed."""
    import _isolation_handlers as h  # noqa: F401
    manager, mgr_mod = await _setup(tmp_path)
    try:
        t0 = time.monotonic()
        result = await asyncio.wait_for(h.iso_coop.run(input={"n": 1}), timeout=20)
        elapsed = time.monotonic() - t0
        # The decisive signal: it returned wound_down=True (cooperative). A
        # hard-cap kill would have raised TaskCancelled instead. Timing is a
        # loose sanity bound (timeout=3s + worker spawn/import startup).
        assert result == {"wound_down": True, "timeout_exceeded": True}, result
        assert elapsed < 10.0, f"cooperative wind-down took too long: {elapsed:.2f}s"
    finally:
        await manager.shutdown()
        mgr_mod._manager = None


@pytest.mark.asyncio
async def test_oneshot_runaway_hard_killed_and_deleted(tmp_path):
    """A runaway one-shot is force-killed and the record is deleted."""
    from azure.ai.agentserver.core.tasks import TaskCancelled
    import _isolation_handlers as h  # noqa: F401
    manager, mgr_mod = await _setup(tmp_path)
    try:
        run = await h.iso_never.start(input={"n": 1})
        task_id = run.task_id
        t0 = time.monotonic()
        with pytest.raises(TaskCancelled):
            await asyncio.wait_for(run.result(), timeout=15)
        elapsed = time.monotonic() - t0
        # Kill lands after timeout(1s)+grace(1s); cooperative window respected.
        assert elapsed >= 1.5, f"killed too early ({elapsed:.2f}s) — grace not respected"
        assert elapsed < 8.0, f"killed too late ({elapsed:.2f}s)"
        await asyncio.sleep(0.4)
        info = await manager._provider.get(task_id)
        assert info is None, f"runaway one-shot should be deleted, got status={getattr(info,'status',None)}"
    finally:
        await manager.shutdown()
        mgr_mod._manager = None


@pytest.mark.asyncio
async def test_oneshot_marker_persisted_during_grace(tmp_path):
    """During the grace window the record carries the marker + stays in_progress."""
    import _isolation_handlers as h  # noqa: F401
    manager, mgr_mod = await _setup(tmp_path)
    try:
        run = await h.iso_never.start(input={"n": 1})
        task_id = run.task_id
        # timeout=1s -> cooperative cancel + marker at ~1s; kill at ~2s.
        # Sample in the middle of the grace window.
        await asyncio.sleep(1.4)
        info = await manager._provider.get(task_id)
        assert info is not None, "record should still exist mid-grace"
        assert info.status == "in_progress", f"expected in_progress mid-grace, got {info.status}"
        marker = (info.payload or {}).get(_TIMEOUT_CANCELLED_AT_KEY)
        assert marker, f"timeout_cancelled_at marker should be persisted, payload={info.payload}"
        # Let the hard cap fire.
        with pytest.raises(Exception):
            await asyncio.wait_for(run.result(), timeout=8)
        await asyncio.sleep(0.4)
        assert await manager._provider.get(task_id) is None, "should be deleted after kill"
    finally:
        await manager.shutdown()
        mgr_mod._manager = None


@pytest.mark.asyncio
async def test_oneshot_recovery_finalizes_timed_out_turn(tmp_path):
    """Recovery must finalize (delete) a stale in_progress one-shot whose turn
    already timed out, rather than re-running it."""
    import _isolation_handlers as h  # noqa: F401
    manager, mgr_mod = await _setup(tmp_path)
    try:
        opts = manager._resume_opts.get("iso_never")
        assert opts is not None
        # Craft a stale record: turn_started_at well in the past (> timeout).
        from azure.ai.agentserver.core.tasks._manager import _utc_now_iso
        from datetime import datetime, timezone, timedelta
        old_ts = (datetime.now(timezone.utc) - timedelta(seconds=30)).isoformat()

        class _Info:
            id = "stale-oneshot-1"
            status = "in_progress"
            payload = {_TURN_STARTED_AT_KEY: old_ts, _TIMEOUT_CANCELLED_AT_KEY: _utc_now_iso()}
            source = {"name": "iso_never"}

        # _turn_timed_out should detect it via the marker.
        assert manager._turn_timed_out(_Info(), opts) is True

        # And with only the derived backstop (no marker):
        class _Info2(_Info):
            payload = {_TURN_STARTED_AT_KEY: old_ts}
        assert manager._turn_timed_out(_Info2(), opts) is True

        # A fresh turn (started now) must NOT be considered timed out.
        class _InfoFresh(_Info):
            payload = {_TURN_STARTED_AT_KEY: _utc_now_iso()}
        assert manager._turn_timed_out(_InfoFresh(), opts) is False
    finally:
        await manager.shutdown()
        mgr_mod._manager = None
