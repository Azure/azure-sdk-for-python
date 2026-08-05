# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""End-to-end test for the ``resilient_multiturn`` sample.

The multi-turn sample is **fully self-contained** (no Azure OpenAI, no
Copilot CLI, no Foundry endpoint). The task and its explicit application
state both use local file-backed storage rooted at the test's ``tmp_path``.

This file is *not* a live test: it imports the sample's task directly
and drives it through three turns + a recovery boundary in the same
process. It exercises the  /  contract for the sample
(the structure test in ``test_resilient_samples_structure.py`` proves
the files exist; this file proves the task actually works).

Coverage:

- Turn 1 persists session and invocation state
- Turn 2 accumulates session history from turn 1
- "done" terminator clears session history
- Invocation status and output are stored separately
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import pytest_asyncio

# Force the local-file resilient provider so the test is fully isolated
# from any hosted env vars in the shell.
os.environ.pop("FOUNDRY_HOSTING_ENVIRONMENT", None)


@pytest_asyncio.fixture
async def task_manager(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """A real TaskManager backed by ``LocalFileTaskProvider`` at tmp_path."""
    import asyncio  # noqa: WPS433

    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("AGENTSERVER_STATE_ROOT", str(tmp_path))
    monkeypatch.delenv("FOUNDRY_HOSTING_ENVIRONMENT", raising=False)

    from azure.ai.agentserver.core.tasks._manager import (  # noqa: WPS433
        TaskManager,
        set_task_manager,
    )

    config = type(
        "C",
        (),
        {
            "agent_name": "test-multiturn",
            "session_id": "test-multiturn-session",
            "agent_version": "1.0.0",
            "is_hosted": False,
        },
    )()
    mgr = TaskManager(config=config, shutdown_event=asyncio.Event())
    set_task_manager(mgr)
    await mgr.startup()
    try:
        yield mgr
    finally:
        await mgr.shutdown()
        set_task_manager(None)


def _ensure_sample_importable() -> None:
    """Add the samples directory to sys.path so ``resilient_multiturn`` resolves."""
    import sys

    samples = Path(__file__).resolve().parent.parent.parent / "samples"
    sp = str(samples)
    if sp not in sys.path:
        sys.path.insert(0, sp)


@pytest.mark.asyncio
async def test_session_workflow_runs_two_turns_and_accumulates_history(
    task_manager,
) -> None:
    """Two consecutive turns share the same session namespace."""
    _ensure_sample_importable()
    from resilient_multiturn.agent import session_workflow, state_store  # noqa: WPS433

    task_id = "session-turn-accumulate"

    run1 = await session_workflow.start(
        task_id=task_id,
        input={
            "session_id": task_id,
            "message": "I want to plan a vacation to Japan",
            "invocation_id": "inv-1",
            "call_id": "call-1",
        },
    )
    result1 = await run1.result()
    assert result1["turn"] == 1

    run2 = await session_workflow.start(
        task_id=task_id,
        input={
            "session_id": task_id,
            "message": "Budget is $5000, 2 weeks",
            "invocation_id": "inv-2",
            "call_id": "call-2",
        },
    )
    result2 = await run2.result()
    assert result2["turn"] == 2

    session = await state_store.load(f"session/{task_id}")
    assert session is not None
    history = session.get("history", [])
    assert len(history) == 4, f"Expected 4 messages, got {history}"
    assert "Japan" in history[0]["content"]
    assert "Budget" in history[2]["content"]


@pytest.mark.asyncio
async def test_session_workflow_done_clears_history(
    task_manager,
) -> None:
    """Sending ``"done"`` terminates the session and clears history."""
    _ensure_sample_importable()
    from resilient_multiturn.agent import session_workflow, state_store  # noqa: WPS433

    task_id = "session-done"

    run1 = await session_workflow.start(
        task_id=task_id,
        input={
            "session_id": task_id,
            "message": "First turn",
            "invocation_id": "inv-1",
            "call_id": "call-1",
        },
    )
    await run1.result()

    run2 = await session_workflow.start(
        task_id=task_id,
        input={
            "session_id": task_id,
            "message": "done",
            "invocation_id": "inv-2",
            "call_id": "call-2",
        },
    )
    result2 = await run2.result()
    assert result2.get("finished") is True
    assert "Session complete" in result2["reply"]

    session = await state_store.load(f"session/{task_id}")
    assert session is not None
    assert session.get("history", []) == []
    assert session.get("turn_count", 0) == 0


@pytest.mark.asyncio
async def test_invocation_status_persisted_to_default_namespace(
    task_manager,
) -> None:
    """A separate State Store item records invocation status and output."""
    _ensure_sample_importable()
    from resilient_multiturn.agent import session_workflow, state_store  # noqa: WPS433

    task_id = "session-statuses"
    run = await session_workflow.start(
        task_id=task_id,
        input={
            "session_id": task_id,
            "message": "Hello",
            "invocation_id": "inv-status",
            "call_id": "call-status",
        },
    )
    await run.result()

    invocation = await state_store.load("invocation/inv-status")
    assert invocation is not None
    assert invocation.get("status") == "completed"
    assert invocation.get("output", {}).get("turn") == 1
