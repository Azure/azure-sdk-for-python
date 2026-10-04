"""Validate the per-chain persistent worker reuse path (§13.6).

Reuse is layered on top of isolation and applied ONLY to multi-turn chains: a
single child process is created per ``task_id`` and reused across the chain's
turns (import paid once, not per turn). A hard-cap kill or crash discards the
worker so the next turn re-spawns; a warm worker survives the suspend gap and
is evicted by the idle-TTL reaper.
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import pytest

_HANDLER_DIR = str(Path(__file__).parent)
_CORE_ROOT = str(Path(__file__).resolve().parents[2])


@pytest.fixture(autouse=True)
def _iso_env(monkeypatch):
    monkeypatch.setenv("AGENTSERVER_TASK_ISOLATION", "1")
    monkeypatch.setenv("AGENTSERVER_TASK_WORKER_REUSE", "1")
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


def _meta(info):
    return (info.payload or {}).get("metadata", {}) if info else {}


async def _wait_for(manager, tid, predicate, timeout=10.0):
    deadline = asyncio.get_event_loop().time() + timeout
    last = None
    while asyncio.get_event_loop().time() < deadline:
        info = await manager._provider.get(tid)
        last = info
        if predicate(info):
            return info
        await asyncio.sleep(0.1)
    return last


@pytest.mark.asyncio
async def test_reuse_same_pid_across_turns(tmp_path):
    """Two turns of one chain run in the SAME warm worker process."""
    import _isolation_handlers as h  # noqa: F401
    manager, mgr_mod = await _setup(tmp_path)
    try:
        tid = "reuse-same-1"
        await h.iso_reuse.start(task_id=tid, input={"tag": "A"})
        await _wait_for(manager, tid, lambda i: _meta(i).get("last_tag") == "A")
        # A warm worker should be registered for the chain.
        assert tid in manager._reuse_workers
        pid_after_a = manager._reuse_workers[tid].pid

        # Resume the suspended chain with a second turn.
        await h.iso_reuse.start(task_id=tid, input={"tag": "B"})
        info = await _wait_for(manager, tid, lambda i: _meta(i).get("last_tag") == "B")
        pids = _meta(info).get("pids", [])
        assert len(pids) == 2, f"expected 2 turns recorded; pids={pids}"
        assert pids[0] == pids[1], f"turns should reuse ONE worker; pids={pids}"
        assert pids[1] == pid_after_a, "registry worker pid should match the running child"
    finally:
        await manager.shutdown()
        mgr_mod._manager = None


@pytest.mark.asyncio
async def test_reuse_hardkill_respawns_new_pid(tmp_path):
    """Runaway turn A is hard-killed -> worker discarded -> queued turn B runs
    in a NEW worker process (different pid)."""
    import _isolation_handlers as h  # noqa: F401
    manager, mgr_mod = await _setup(tmp_path)
    try:
        tid = "reuse-kill-1"
        await h.iso_reuse_mt.start(task_id=tid, input={"mode": "runaway", "tag": "A"})
        await _wait_for(manager, tid, lambda i: "A" in _meta(i).get("seen_tags", []))
        pid_a = manager._reuse_workers[tid].pid
        # Queue turn B while A runs away.
        await h.iso_reuse_mt.start(task_id=tid, input={"mode": "coop", "tag": "B"})
        # timeout=2s + grace=1s -> kill ~3s, then drain -> turn B in a new worker.
        info = await _wait_for(
            manager, tid, lambda i: "B" in _meta(i).get("seen_tags", []), timeout=15
        )
        seen = _meta(info).get("seen_tags", [])
        pids = _meta(info).get("pids", [])
        assert "A" in seen and "B" in seen, f"both turns should run; seen={seen}"
        assert len(pids) == 2 and pids[0] != pids[1], (
            f"hard-kill must respawn a NEW worker; pids={pids}"
        )
        assert pids[0] == pid_a, "first pid should be the killed worker"
    finally:
        await manager.shutdown()
        mgr_mod._manager = None


@pytest.mark.asyncio
async def test_reuse_idle_ttl_evicts_worker(tmp_path):
    """A warm worker idle beyond the TTL is evicted; next turn spawns fresh."""
    import _isolation_handlers as h  # noqa: F401
    manager, mgr_mod = await _setup(tmp_path)
    try:
        tid = "reuse-ttl-1"
        await h.iso_reuse.start(task_id=tid, input={"tag": "A"})
        await _wait_for(manager, tid, lambda i: _meta(i).get("last_tag") == "A")
        worker = manager._reuse_workers.get(tid)
        assert worker is not None and worker.alive
        pid_a = worker.pid

        # Force the worker to look idle and drive one reap pass deterministically.
        now = asyncio.get_event_loop().time()
        worker.last_active_monotonic = now - 3600  # long idle
        evicted = manager._reap_idle_workers(now, ttl=1.0)
        assert evicted == 1, "idle worker should have been evicted"
        assert tid not in manager._reuse_workers, "evicted worker must be deregistered"

        # Next turn spawns a fresh worker (different pid).
        await h.iso_reuse.start(task_id=tid, input={"tag": "B"})
        info = await _wait_for(manager, tid, lambda i: _meta(i).get("last_tag") == "B")
        pids = _meta(info).get("pids", [])
        assert len(pids) == 2 and pids[1] != pid_a, (
            f"post-eviction turn must use a NEW worker; pids={pids}"
        )
    finally:
        await manager.shutdown()
        mgr_mod._manager = None
