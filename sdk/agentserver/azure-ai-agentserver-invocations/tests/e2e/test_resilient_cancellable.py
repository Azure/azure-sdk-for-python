# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""End-to-end test for the ``resilient_cancellable`` minimal sample.

Fully self-contained (no LLM, no cloud): the durable checkpoint uses local
file-backed storage rooted at the test's ``tmp_path``. Drives the sample's task
in-process to exercise its core promise — a finite job that runs to completion,
but stops early (``status: cancelled``) when a durable cancel marker is present,
including across a recovery boundary.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
import pytest_asyncio


@pytest_asyncio.fixture
async def task_manager(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """A real TaskManager backed by the local file provider at tmp_path."""

    (tmp_path / "tasks").mkdir(parents=True, exist_ok=True)
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
            "agent_name": "test-cancellable",
            "session_id": "test-cancellable-session",
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
    import sys

    samples = Path(__file__).resolve().parent.parent.parent / "samples"
    sp = str(samples)
    if sp not in sys.path:
        sys.path.insert(0, sp)


_SESSION = "test-cj-session"
_USER = "test-cj-user"


async def _load_item(cj, key: str):
    store = await cj.open_checkpoint_store(_SESSION, _USER)
    async with store:
        return await store.get_item(key)


async def _seed_item(cj, key: str, value: dict) -> None:
    store = await cj.open_checkpoint_store(_SESSION, _USER)
    async with store:
        await store.set_item(key, value)


async def _wait_for_steps(cj, key: str, minimum: int, timeout: float = 5.0) -> int:
    """Poll the durable checkpoint until ``completed_steps`` reaches ``minimum``."""
    loop = asyncio.get_event_loop()
    deadline = loop.time() + timeout
    while loop.time() < deadline:
        item = await _load_item(cj, key)
        if item is not None:
            done = int(item.value.get("completed_steps", 0) or 0)
            if done >= minimum:
                return done
        await asyncio.sleep(0.02)
    raise AssertionError(
        f"completed_steps did not reach {minimum} within {timeout}s for {key}"
    )


@pytest.mark.asyncio
async def test_runs_to_completion_when_not_cancelled(
    task_manager, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Without a cancel marker the job finishes all steps."""
    _ensure_sample_importable()
    from resilient_cancellable import agent as cj  # noqa: WPS433

    monkeypatch.setattr(cj, "_STEP_DELAY", 0.0)

    task_id = "cj-complete"
    run = await cj.cancellable_job.start(
        task_id=task_id,
        input={"name": "alice", "steps": 3, "session_id": _SESSION, "user_id": _USER},
    )
    result = await run.result()

    assert result["status"] == "completed"
    item = await _load_item(cj, task_id)
    assert item.value.get("completed_steps") == 3
    assert item.value.get("status") == "completed"


@pytest.mark.asyncio
async def test_cancel_marker_before_start_stops_immediately(
    task_manager, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A cancel marker present before the first step stops the job at step 0."""
    _ensure_sample_importable()
    from resilient_cancellable import agent as cj  # noqa: WPS433

    monkeypatch.setattr(cj, "_STEP_DELAY", 0.0)

    task_id = "cj-cancel-early"
    await _seed_item(cj, f"{task_id}{cj.CANCEL_SUFFIX}", {"cancel": True})

    run = await cj.cancellable_job.start(
        task_id=task_id,
        input={"name": "bob", "steps": 5, "session_id": _SESSION, "user_id": _USER},
    )
    result = await run.result()

    assert result["status"] == "cancelled"
    assert result["completed_steps"] == 0
    item = await _load_item(cj, task_id)
    assert item.value.get("status") == "cancelled"


@pytest.mark.asyncio
async def test_cancel_mid_run_stops_early(
    task_manager, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A cancel marker written mid-run stops the job before it finishes."""
    _ensure_sample_importable()
    from resilient_cancellable import agent as cj  # noqa: WPS433

    monkeypatch.setattr(cj, "_STEP_DELAY", 0.02)

    task_id = "cj-cancel-mid"
    run = await cj.cancellable_job.start(
        task_id=task_id,
        input={"name": "carol", "steps": 50, "session_id": _SESSION, "user_id": _USER},
    )

    # Let it make some progress, then request cancel.
    reached = await _wait_for_steps(cj, task_id, minimum=2)
    await _seed_item(cj, f"{task_id}{cj.CANCEL_SUFFIX}", {"cancel": True})

    result = await asyncio.wait_for(run.result(), timeout=5.0)
    assert result["status"] == "cancelled"
    # Stopped early: at least where we saw it, and short of the full 50.
    assert reached <= result["completed_steps"] < 50
    item = await _load_item(cj, task_id)
    assert item.value.get("status") == "cancelled"


@pytest.mark.asyncio
async def test_recovered_run_honours_pending_cancel(
    task_manager, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A partially-done job with a pending cancel marker cancels on resume."""
    _ensure_sample_importable()
    from resilient_cancellable import agent as cj  # noqa: WPS433

    monkeypatch.setattr(cj, "_STEP_DELAY", 0.0)

    task_id = "cj-recover-cancel"
    # Simulate a run that had done 2/10 steps and a cancel that landed before a
    # crash: both the checkpoint and the cancel marker are already durable.
    await _seed_item(
        cj,
        task_id,
        {"name": "dave", "steps": 10, "completed_steps": 2, "status": "in_progress"},
    )
    await _seed_item(cj, f"{task_id}{cj.CANCEL_SUFFIX}", {"cancel": True})

    run = await cj.cancellable_job.start(
        task_id=task_id,
        input={"name": "dave", "steps": 10, "session_id": _SESSION, "user_id": _USER},
    )
    result = await run.result()

    assert result["status"] == "cancelled"
    # Stopped at the resume point (2), not restarted at 0 and not finished at 10.
    assert result["completed_steps"] == 2
