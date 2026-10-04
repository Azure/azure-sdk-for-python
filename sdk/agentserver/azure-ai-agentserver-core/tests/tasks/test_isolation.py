"""Integration tests for process-isolated handler execution + the timeout hard cap.

These run the real ``TaskManager`` (local file provider) with
``AGENTSERVER_TASK_ISOLATION=1`` so the handler executes in a child process.
Windows/macOS/Linux compatible (``asyncio.create_subprocess_exec``).
"""
from __future__ import annotations

import asyncio
import os
import sys
import uuid
from pathlib import Path

import pytest

_HANDLER_DIR = str(Path(__file__).parent)


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


@pytest.fixture(autouse=True)
def _isolation_env(monkeypatch):
    # Enable isolation + a short hard-cap grace so the cap fires quickly.
    monkeypatch.setenv("AGENTSERVER_TASK_ISOLATION", "1")
    monkeypatch.setenv("AGENTSERVER_TASK_TIMEOUT_HARDCAP_GRACE_SECONDS", "1")
    # The child subprocess must be able to import the handler module + the SDK.
    existing = os.environ.get("PYTHONPATH", "")
    core_root = str(Path(__file__).resolve().parents[2])  # azure-ai-agentserver-core
    monkeypatch.setenv("PYTHONPATH", os.pathsep.join([_HANDLER_DIR, core_root, existing]))
    if _HANDLER_DIR not in sys.path:
        sys.path.insert(0, _HANDLER_DIR)
    yield


@pytest.mark.asyncio
async def test_isolated_echo_returns_result(tmp_path):
    import _isolation_handlers as h  # noqa: F401  (registers the tasks)
    manager, mgr_mod = await _setup(tmp_path)
    try:
        result = await h.iso_echo.run(input={"msg": "hi"})
        assert result["echoed"] == {"msg": "hi"}, result
        assert "task_id" in result, result
    finally:
        await manager.shutdown()
        mgr_mod._manager = None


@pytest.mark.asyncio
async def test_isolated_hard_cap_kills_runaway_oneshot(tmp_path):
    from azure.ai.agentserver.core.tasks import TaskCancelled
    import _isolation_handlers as h  # noqa: F401
    manager, mgr_mod = await _setup(tmp_path)
    try:
        run = await h.iso_never.start(input={"n": 1})
        task_id = run.task_id
        # timeout=1s + grace=1s -> hard-killed within a few seconds.
        with pytest.raises(TaskCancelled):
            await asyncio.wait_for(run.result(), timeout=15)
        # One-shot ephemeral: the record is deleted on the cancel finalization.
        await asyncio.sleep(0.5)
        info = await manager._provider.get(task_id)
        assert info is None or info.status in ("completed", "failed", "suspended"), (
            f"runaway one-shot should be gone/terminal, got {getattr(info, 'status', None)}"
        )
    finally:
        await manager.shutdown()
        mgr_mod._manager = None
