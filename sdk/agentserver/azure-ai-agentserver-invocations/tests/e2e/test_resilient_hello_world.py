# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""End-to-end test for the ``resilient_hello_world`` minimal sample.

The hello-world sample is **fully self-contained** (no Azure OpenAI, no
Copilot CLI, no Foundry endpoint). Its durable checkpoint uses local
file-backed storage rooted at the test's ``tmp_path``.

This is *not* a live test: it imports the sample's task directly and drives
it through completion and a resume-from-checkpoint boundary in the same
process. It exercises the durable-checkpoint contract for the sample (the
structure test in ``test_resilient_samples_structure.py`` proves the files
exist and opt in to durable tasks; this file proves the task actually
checkpoints and resumes).

Coverage:

- A fresh run counts through every step and finishes ``complete``.
- Each step persists ``completed_steps`` to the durable checkpoint.
- A run whose checkpoint already shows every step done finishes without
  redoing any work (resume-from-checkpoint skips completed steps).
- A partially-completed checkpoint resumes at the next step, not step 1.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import pytest_asyncio

from azure.ai.agentserver.core.storage import FoundryStateStore

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
            "agent_name": "test-hello-world",
            "session_id": "test-hello-world-session",
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
    """Add the samples directory to sys.path so ``resilient_hello_world`` resolves."""
    import sys

    samples = Path(__file__).resolve().parent.parent.parent / "samples"
    sp = str(samples)
    if sp not in sys.path:
        sys.path.insert(0, sp)


async def _load_item(store_name: str, key: str):
    store = await FoundryStateStore.get_or_create(store_name)
    async with store:
        return await store.get_item(key)


async def _seed_item(store_name: str, key: str, value: dict):
    """Write an initial checkpoint and return its ETag."""
    store = await FoundryStateStore.get_or_create(store_name)
    async with store:
        ref = await store.set_item(key, value)
        return ref.etag


# A fixed session id so the tests read the same session-scoped store the task
# writes to (the host injects this from ``?agent_session_id=`` at runtime).
_SESSION = "test-hw-session"


def test_durable_task_id_is_accepted_by_task_manager() -> None:
    """``durable_task_id`` must produce an id the TaskManager accepts.

    Regression guard: a ``/`` separator (or an over-long id) is rejected by
    ``start()`` — a bug the task-level tests miss because they pass their own
    slash-free ids. Validate the helper's output with the real SDK validator,
    including long protocol ids that would blow the 128-char limit if not hashed.
    """
    _ensure_sample_importable()
    from azure.ai.agentserver.core.tasks._decorator import (  # noqa: WPS433
        _validate_task_id,
    )
    from resilient_hello_world import agent as hw  # noqa: WPS433

    _validate_task_id(hw.durable_task_id("sess-1", "inv-1"))
    _validate_task_id(hw.durable_task_id("s" * 200, "inv_" + "x" * 200))
    # Distinct inputs must not collide, and the boundary must be unambiguous.
    assert hw.durable_task_id("a", "bc") != hw.durable_task_id("ab", "c")


@pytest.mark.asyncio
async def test_runs_to_completion_and_checkpoints_every_step(
    task_manager,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A fresh run finishes ``complete`` with the final step checkpointed."""
    _ensure_sample_importable()
    from resilient_hello_world import agent as hw  # noqa: WPS433

    monkeypatch.setattr(hw, "_STEP_DELAY", 0.0)

    task_id = "hw-complete"
    run = await hw.hello_world.start(
        task_id=task_id,
        input={"name": "alice", "steps": 3, "session_id": _SESSION},
    )
    result = await run.result()

    assert result == {"name": "alice", "steps": 3, "status": "complete"}

    item = await _load_item(hw.checkpoint_store_name(_SESSION), task_id)
    assert item is not None
    assert item.value.get("completed_steps") == 3
    assert item.value.get("steps") == 3


@pytest.mark.asyncio
async def test_completed_checkpoint_skips_all_work(
    task_manager,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A checkpoint already at ``steps`` finishes without rewriting it.

    An unchanged ETag proves the handler resumed from the checkpoint and ran
    zero steps instead of starting over.
    """
    _ensure_sample_importable()
    from resilient_hello_world import agent as hw  # noqa: WPS433

    monkeypatch.setattr(hw, "_STEP_DELAY", 0.0)

    task_id = "hw-already-done"
    store_name = hw.checkpoint_store_name(_SESSION)
    seeded_etag = await _seed_item(
        store_name,
        task_id,
        {"name": "bob", "steps": 3, "completed_steps": 3},
    )

    run = await hw.hello_world.start(
        task_id=task_id,
        input={"name": "bob", "steps": 3, "session_id": _SESSION},
    )
    result = await run.result()

    assert result["status"] == "complete"

    item = await _load_item(store_name, task_id)
    assert item is not None
    assert item.value.get("completed_steps") == 3
    # No step ran, so no checkpoint write happened → ETag is unchanged.
    assert item.etag == seeded_etag


@pytest.mark.asyncio
async def test_partial_checkpoint_resumes_at_next_step(
    task_manager,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A partial checkpoint continues to completion instead of restarting."""
    _ensure_sample_importable()
    from resilient_hello_world import agent as hw  # noqa: WPS433

    monkeypatch.setattr(hw, "_STEP_DELAY", 0.0)

    task_id = "hw-partial"
    store_name = hw.checkpoint_store_name(_SESSION)
    seeded_etag = await _seed_item(
        store_name,
        task_id,
        {"name": "carol", "steps": 4, "completed_steps": 2},
    )

    run = await hw.hello_world.start(
        task_id=task_id,
        input={"name": "carol", "steps": 4, "session_id": _SESSION},
    )
    result = await run.result()

    assert result == {"name": "carol", "steps": 4, "status": "complete"}

    item = await _load_item(store_name, task_id)
    assert item is not None
    assert item.value.get("completed_steps") == 4
    # Work continued from the seed, so the checkpoint was rewritten.
    assert item.etag != seeded_etag
