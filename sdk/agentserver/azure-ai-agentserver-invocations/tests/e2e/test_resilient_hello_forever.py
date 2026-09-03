# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""End-to-end test for the ``resilient_hello_forever`` minimal sample.

The hello-forever sample is an *indefinite* durable worker: it ticks forever,
checkpointing its ``iterations`` cursor after every tick, and only stops on an
explicit cancel that is confirmed by a durable "stop" marker. Like the other
minimal sample it is **fully self-contained** (no LLM, no cloud) — its
checkpoint uses local file-backed storage rooted at the test's ``tmp_path``.

This is *not* a live test: it imports the sample's task directly and drives it
in-process. It exercises the two behaviours that make an infinite loop a
well-behaved LRA:

- The worker ticks and checkpoints its ``iterations`` cursor.
- An explicit cancel + durable stop marker stops it terminally (``stopped``),
  and it stops from wherever its checkpoint had reached (i.e. it resumes from a
  pre-existing checkpoint rather than restarting at 0).
"""

from __future__ import annotations

import asyncio
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
            "agent_name": "test-hello-forever",
            "session_id": "test-hello-forever-session",
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
    """Add the samples directory to sys.path so ``resilient_hello_forever`` resolves."""
    import sys

    samples = Path(__file__).resolve().parent.parent.parent / "samples"
    sp = str(samples)
    if sp not in sys.path:
        sys.path.insert(0, sp)


async def _load_item(store_name: str, key: str):
    store = await FoundryStateStore.get_or_create(store_name)
    async with store:
        return await store.get_item(key)


async def _seed_item(store_name: str, key: str, value: dict) -> None:
    store = await FoundryStateStore.get_or_create(store_name)
    async with store:
        await store.set_item(key, value)


async def _wait_for_iterations(store_name: str, key: str, minimum: int, timeout: float = 5.0) -> int:
    """Poll the durable checkpoint until ``iterations`` reaches ``minimum``."""
    loop = asyncio.get_event_loop()
    deadline = loop.time() + timeout
    while loop.time() < deadline:
        item = await _load_item(store_name, key)
        if item is not None:
            iters = int(item.value.get("iterations", 0) or 0)
            if iters >= minimum:
                return iters
        await asyncio.sleep(0.02)
    raise AssertionError(
        f"iterations did not reach {minimum} within {timeout}s for task {key}"
    )


# A fixed session id so the tests read the same session-scoped store the worker
# writes to (the host injects this from ``?agent_session_id=`` at runtime).
_SESSION = "test-hf-session"


@pytest.mark.asyncio
async def test_ticks_then_stops_on_cancel_with_marker(
    task_manager,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The worker ticks, then an explicit cancel + stop marker stops it."""
    _ensure_sample_importable()
    from resilient_hello_forever import agent as hf  # noqa: WPS433

    monkeypatch.setattr(hf, "_TICK", 0.01)

    task_id = "hf-stop"
    store_name = hf.checkpoint_store_name(_SESSION)
    run = await hf.hello_forever.start(
        task_id=task_id, input={"name": "alice", "session_id": _SESSION}
    )

    # Let it tick a few times so there is real progress to stop.
    reached = await _wait_for_iterations(store_name, task_id, minimum=2)

    # Request a stop: write the durable marker, then signal cancel. The worker
    # only treats cancel as a real stop when the marker is present.
    await _seed_item(store_name, f"{task_id}{hf.STOP_SUFFIX}", {"stop": True})
    await run.cancel()

    result = await asyncio.wait_for(run.result(), timeout=5.0)

    assert result["stopped"] is True
    assert result["name"] == "alice"
    assert result["iterations"] >= reached


@pytest.mark.asyncio
async def test_stops_on_marker_without_local_cancel(
    task_manager,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The durable stop marker alone stops the worker (cross-replica case).

    A cancel routed to a different replica writes the marker but cannot set this
    process's ``ctx.cancel``. The worker must still stop, because it re-checks
    the marker every iteration independently of ``ctx.cancel``.
    """
    _ensure_sample_importable()
    from resilient_hello_forever import agent as hf  # noqa: WPS433

    monkeypatch.setattr(hf, "_TICK", 0.01)

    task_id = "hf-marker-only"
    store_name = hf.checkpoint_store_name(_SESSION)
    run = await hf.hello_forever.start(
        task_id=task_id, input={"name": "carol", "session_id": _SESSION}
    )

    await _wait_for_iterations(store_name, task_id, minimum=2)

    # Write ONLY the durable stop marker — do not call run.cancel().
    await _seed_item(store_name, f"{task_id}{hf.STOP_SUFFIX}", {"stop": True})

    result = await asyncio.wait_for(run.result(), timeout=5.0)
    assert result["stopped"] is True
    assert result["name"] == "carol"


@pytest.mark.asyncio
async def test_resumes_from_existing_checkpoint(
    task_manager,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A pre-existing checkpoint makes the worker resume, not restart at 0."""
    _ensure_sample_importable()
    from resilient_hello_forever import agent as hf  # noqa: WPS433

    monkeypatch.setattr(hf, "_TICK", 0.01)

    task_id = "hf-resume"
    store_name = hf.checkpoint_store_name(_SESSION)
    await _seed_item(store_name, task_id, {"name": "bob", "iterations": 5})

    run = await hf.hello_forever.start(
        task_id=task_id, input={"name": "bob", "session_id": _SESSION}
    )

    # It must continue past the seeded cursor rather than counting up from 1.
    reached = await _wait_for_iterations(store_name, task_id, minimum=6)
    assert reached >= 6

    await _seed_item(store_name, f"{task_id}{hf.STOP_SUFFIX}", {"stop": True})
    await run.cancel()

    result = await asyncio.wait_for(run.result(), timeout=5.0)
    assert result["stopped"] is True
    assert result["iterations"] >= 6
