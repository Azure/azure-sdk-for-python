"""ONE-SHOT task timeout cancellation under the FORK isolation backend.

Mirrors test_isolation_oneshot.py but forces the fork worker backend
(AGENTSERVER_TASK_WORKER_FORK=1). Fork is Unix-only, so the whole module is
skipped on non-Linux platforms.
"""
from __future__ import annotations

import asyncio
import os
import sys
import time
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    not sys.platform.startswith("linux"), reason="fork worker backend is Linux-only"
)

_HANDLER_DIR = str(Path(__file__).parent)
_CORE_ROOT = str(Path(__file__).resolve().parents[2])

_TURN_STARTED_AT_KEY = "turn_started_at"
_TIMEOUT_CANCELLED_AT_KEY = "timeout_cancelled_at"


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


@pytest.mark.asyncio
async def test_fork_oneshot_cooperative_winds_down_not_killed(tmp_path):
    import _isolation_handlers as h  # noqa: F401
    manager, mgr_mod = await _setup(tmp_path)
    try:
        result = await asyncio.wait_for(h.iso_coop.run(input={"n": 1}), timeout=20)
        assert result == {"wound_down": True, "timeout_exceeded": True}, result
    finally:
        await manager.shutdown()
        mgr_mod._manager = None


@pytest.mark.asyncio
async def test_fork_oneshot_runaway_hard_killed_and_deleted(tmp_path):
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
        assert elapsed >= 1.5, f"killed too early ({elapsed:.2f}s) — grace not respected"
        assert elapsed < 8.0, f"killed too late ({elapsed:.2f}s)"
        await asyncio.sleep(0.4)
        info = await manager._provider.get(task_id)
        assert info is None, f"runaway one-shot should be deleted, got {getattr(info,'status',None)}"
    finally:
        await manager.shutdown()
        mgr_mod._manager = None


@pytest.mark.asyncio
async def test_fork_oneshot_marker_persisted_during_grace(tmp_path):
    import _isolation_handlers as h  # noqa: F401
    manager, mgr_mod = await _setup(tmp_path)
    try:
        run = await h.iso_never.start(input={"n": 1})
        task_id = run.task_id
        await asyncio.sleep(1.4)
        info = await manager._provider.get(task_id)
        assert info is not None, "record should still exist mid-grace"
        assert info.status == "in_progress", f"expected in_progress mid-grace, got {info.status}"
        marker = (info.payload or {}).get(_TIMEOUT_CANCELLED_AT_KEY)
        assert marker, f"timeout_cancelled_at marker should be persisted, payload={info.payload}"
        with pytest.raises(Exception):
            await asyncio.wait_for(run.result(), timeout=8)
        await asyncio.sleep(0.4)
        assert await manager._provider.get(task_id) is None, "should be deleted after kill"
    finally:
        await manager.shutdown()
        mgr_mod._manager = None
