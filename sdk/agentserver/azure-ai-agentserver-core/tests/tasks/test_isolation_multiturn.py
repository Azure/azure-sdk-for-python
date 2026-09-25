"""Validate MULTI-TURN task timeout hard cap under isolation.

Key scenario (§5.2): a steerable multi-turn turn that ignores cancellation is
hard-killed after timeout+grace, and if a steering input is queued the chain
DRAINS to the next turn (rather than terminating). If nothing is queued, the
chain suspends.
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


@pytest.mark.asyncio
async def test_multiturn_hardcap_drains_to_queued_next_turn(tmp_path):
    """Runaway turn 1 + queued steering input B -> hard-kill -> turn 2 runs B."""
    import _isolation_handlers as h  # noqa: F401
    manager, mgr_mod = await _setup(tmp_path)
    try:
        tid = "chain-drain-1"
        # Turn 1: runaway (ignores cancel).
        await h.iso_mt.start(task_id=tid, input={"mode": "runaway", "tag": "A"})
        await asyncio.sleep(1.0)  # let turn 1 start + flush tag A
        # Steering input B (cooperative): queued while turn 1 runs.
        await h.iso_mt.start(task_id=tid, input={"mode": "coop", "tag": "B"})
        # Turn1 timeout=2s + grace=1s -> kill ~3s, then drain -> turn 2 (B) runs.
        await asyncio.sleep(9)
        info = await manager._provider.get(tid)
        meta = _meta(info)
        seen = meta.get("seen_tags", [])
        assert "A" in seen, f"turn 1 (A) should have run; seen={seen}"
        assert "B" in seen, f"turn 2 (B) should have run after drain; seen={seen}"
        assert meta.get("last_tag") == "B", f"last turn should be B; meta={meta}"
        # Chain survived (not deleted); ends suspended after B completes.
        assert info is not None and info.status in ("suspended", "in_progress"), info.status
    finally:
        await manager.shutdown()
        mgr_mod._manager = None


@pytest.mark.asyncio
async def test_multiturn_hardcap_no_queue_suspends(tmp_path):
    """Runaway turn with NO queued input -> hard-kill -> chain suspends (not deleted)."""
    import _isolation_handlers as h  # noqa: F401
    manager, mgr_mod = await _setup(tmp_path)
    try:
        tid = "chain-suspend-1"
        run = await h.iso_mt.start(task_id=tid, input={"mode": "runaway", "tag": "A"})
        # timeout=2s + grace=1s -> kill ~3s. No steering queued.
        from azure.ai.agentserver.core.tasks import TaskCancelled
        with pytest.raises(TaskCancelled):
            await asyncio.wait_for(run.result(), timeout=12)
        await asyncio.sleep(0.5)
        info = await manager._provider.get(tid)
        # Multi-turn: chain stays alive as suspended (nanny won't recover
        # in_progress; a future .start() can resume).
        assert info is not None, "multi-turn chain should NOT be deleted"
        assert info.status == "suspended", f"expected suspended, got {info.status}"
    finally:
        await manager.shutdown()
        mgr_mod._manager = None
