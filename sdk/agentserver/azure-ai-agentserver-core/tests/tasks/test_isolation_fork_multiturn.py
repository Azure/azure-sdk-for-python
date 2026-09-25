"""MULTI-TURN + per-chain REUSE under the FORK isolation backend.

Mirrors test_isolation_multiturn.py and test_isolation_reuse.py but forces the
fork worker backend (AGENTSERVER_TASK_WORKER_FORK=1). Linux-only.
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    not sys.platform.startswith("linux"), reason="fork worker backend is Linux-only"
)

_HANDLER_DIR = str(Path(__file__).parent)
_CORE_ROOT = str(Path(__file__).resolve().parents[2])


@pytest.fixture(autouse=True)
def _iso_env(monkeypatch):
    monkeypatch.setenv("AGENTSERVER_TASK_ISOLATION", "1")
    monkeypatch.setenv("AGENTSERVER_TASK_WORKER_FORK", "1")
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


async def _wait_for(manager, tid, predicate, timeout=12.0):
    deadline = asyncio.get_event_loop().time() + timeout
    last = None
    while asyncio.get_event_loop().time() < deadline:
        info = await manager._provider.get(tid)
        last = info
        if predicate(info):
            return info
        await asyncio.sleep(0.1)
    return last


# --------------------------- multi-turn (no reuse) ---------------------------

@pytest.mark.asyncio
async def test_fork_multiturn_hardcap_drains_to_queued_next_turn(tmp_path):
    import _isolation_handlers as h  # noqa: F401
    manager, mgr_mod = await _setup(tmp_path)
    try:
        tid = "fork-chain-drain-1"
        await h.iso_mt.start(task_id=tid, input={"mode": "runaway", "tag": "A"})
        await asyncio.sleep(1.0)
        await h.iso_mt.start(task_id=tid, input={"mode": "coop", "tag": "B"})
        await asyncio.sleep(9)
        info = await manager._provider.get(tid)
        seen = _meta(info).get("seen_tags", [])
        assert "A" in seen, f"turn 1 (A) should have run; seen={seen}"
        assert "B" in seen, f"turn 2 (B) should have run after drain; seen={seen}"
        assert _meta(info).get("last_tag") == "B", f"last turn should be B; meta={_meta(info)}"
        assert info is not None and info.status in ("suspended", "in_progress"), info.status
    finally:
        await manager.shutdown()
        mgr_mod._manager = None


@pytest.mark.asyncio
async def test_fork_multiturn_hardcap_no_queue_suspends(tmp_path):
    import _isolation_handlers as h  # noqa: F401
    manager, mgr_mod = await _setup(tmp_path)
    try:
        tid = "fork-chain-suspend-1"
        run = await h.iso_mt.start(task_id=tid, input={"mode": "runaway", "tag": "A"})
        from azure.ai.agentserver.core.tasks import TaskCancelled
        with pytest.raises(TaskCancelled):
            await asyncio.wait_for(run.result(), timeout=12)
        await asyncio.sleep(0.5)
        info = await manager._provider.get(tid)
        assert info is not None, "multi-turn chain should NOT be deleted"
        assert info.status == "suspended", f"expected suspended, got {info.status}"
    finally:
        await manager.shutdown()
        mgr_mod._manager = None


# ------------------------------- reuse (fork) --------------------------------

@pytest.fixture
def _reuse_env(monkeypatch):
    monkeypatch.setenv("AGENTSERVER_TASK_WORKER_REUSE", "1")
    yield


@pytest.mark.asyncio
async def test_fork_reuse_same_pid_across_turns(tmp_path, _reuse_env):
    import _isolation_handlers as h  # noqa: F401
    manager, mgr_mod = await _setup(tmp_path)
    try:
        tid = "fork-reuse-same-1"
        await h.iso_reuse.start(task_id=tid, input={"tag": "A"})
        await _wait_for(manager, tid, lambda i: _meta(i).get("last_tag") == "A")
        assert tid in manager._reuse_workers
        pid_after_a = manager._reuse_workers[tid].pid
        await h.iso_reuse.start(task_id=tid, input={"tag": "B"})
        info = await _wait_for(manager, tid, lambda i: _meta(i).get("last_tag") == "B")
        pids = _meta(info).get("pids", [])
        assert len(pids) == 2, f"expected 2 turns recorded; pids={pids}"
        assert pids[0] == pids[1], f"turns should reuse ONE forked worker; pids={pids}"
        assert pids[1] == pid_after_a
    finally:
        await manager.shutdown()
        mgr_mod._manager = None


@pytest.mark.asyncio
async def test_fork_reuse_hardkill_respawns_new_pid(tmp_path, _reuse_env):
    import _isolation_handlers as h  # noqa: F401
    manager, mgr_mod = await _setup(tmp_path)
    try:
        tid = "fork-reuse-kill-1"
        await h.iso_reuse_mt.start(task_id=tid, input={"mode": "runaway", "tag": "A"})
        await _wait_for(manager, tid, lambda i: "A" in _meta(i).get("seen_tags", []))
        pid_a = manager._reuse_workers[tid].pid
        await h.iso_reuse_mt.start(task_id=tid, input={"mode": "coop", "tag": "B"})
        info = await _wait_for(
            manager, tid, lambda i: "B" in _meta(i).get("seen_tags", []), timeout=15
        )
        seen = _meta(info).get("seen_tags", [])
        pids = _meta(info).get("pids", [])
        assert "A" in seen and "B" in seen, f"both turns should run; seen={seen}"
        assert len(pids) == 2 and pids[0] != pids[1], f"hard-kill must respawn; pids={pids}"
        assert pids[0] == pid_a
    finally:
        await manager.shutdown()
        mgr_mod._manager = None


@pytest.mark.asyncio
async def test_fork_reuse_idle_ttl_evicts_worker(tmp_path, _reuse_env):
    import _isolation_handlers as h  # noqa: F401
    manager, mgr_mod = await _setup(tmp_path)
    try:
        tid = "fork-reuse-ttl-1"
        await h.iso_reuse.start(task_id=tid, input={"tag": "A"})
        await _wait_for(manager, tid, lambda i: _meta(i).get("last_tag") == "A")
        worker = manager._reuse_workers.get(tid)
        assert worker is not None and worker.alive
        pid_a = worker.pid
        now = asyncio.get_event_loop().time()
        worker.last_active_monotonic = now - 3600
        evicted = manager._reap_idle_workers(now, ttl=1.0)
        assert evicted == 1
        assert tid not in manager._reuse_workers
        await h.iso_reuse.start(task_id=tid, input={"tag": "B"})
        info = await _wait_for(manager, tid, lambda i: _meta(i).get("last_tag") == "B")
        pids = _meta(info).get("pids", [])
        assert len(pids) == 2 and pids[1] != pid_a, f"post-eviction must use NEW worker; pids={pids}"
    finally:
        await manager.shutdown()
        mgr_mod._manager = None
