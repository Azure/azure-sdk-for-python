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
from pathlib import Path

import pytest
import pytest_asyncio


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


@pytest.fixture(autouse=True)
def _samples_on_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """Prepend the samples dir to ``sys.path`` (auto-restored after each test)."""
    samples = Path(__file__).resolve().parent.parent.parent / "samples"
    monkeypatch.syspath_prepend(str(samples))


async def _load_item(hf, key: str):
    store = await hf.open_checkpoint_store(_SESSION, _USER)
    async with store:
        return await store.get_item(key)


async def _seed_item(hf, key: str, value: dict) -> None:
    store = await hf.open_checkpoint_store(_SESSION, _USER)
    async with store:
        await store.set_item(key, value)


async def _wait_for_iterations(hf, key: str, minimum: int, timeout: float = 5.0) -> int:
    """Poll the durable checkpoint until ``iterations`` reaches ``minimum``."""
    loop = asyncio.get_event_loop()
    deadline = loop.time() + timeout
    while loop.time() < deadline:
        item = await _load_item(hf, key)
        if item is not None:
            iters = int(item.value.get("iterations", 0) or 0)
            if iters >= minimum:
                return iters
        await asyncio.sleep(0.02)
    raise AssertionError(
        f"iterations did not reach {minimum} within {timeout}s for task {key}"
    )


# A fixed session + user id so the tests read the same session-scoped,
# user-isolated store the worker writes to (the host injects both from request
# state at runtime).
_SESSION = "test-hf-session"
_USER = "test-hf-user"


def test_durable_task_id_is_accepted_by_task_manager() -> None:
    """``durable_task_id`` must produce an id the TaskManager accepts.

    Regression guard: a ``/`` separator (or an over-long id) is rejected by
    ``start()`` — a bug the task-level tests miss because they pass their own
    slash-free ids. Validate the helper's output with the real SDK validator,
    including long protocol ids that would blow the 128-char limit if not hashed.
    """
    from azure.ai.agentserver.core.tasks._validation import (  # noqa: WPS433
        validate_task_id,
    )
    from resilient_hello_forever import agent as hf  # noqa: WPS433

    validate_task_id(hf.durable_task_id("sess-1", "inv-1", "user-1"))
    validate_task_id(hf.durable_task_id("s" * 200, "inv_" + "x" * 200, "u" * 200))
    assert hf.durable_task_id("a", "bc", "d") != hf.durable_task_id("ab", "c", "d")
    assert hf.durable_task_id("s", "i", "u1") != hf.durable_task_id("s", "i", "u2")


@pytest.mark.asyncio
async def test_ticks_then_stops_on_cancel_with_marker(
    task_manager,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The worker ticks, then an explicit cancel + stop marker stops it."""
    from resilient_hello_forever import agent as hf  # noqa: WPS433

    monkeypatch.setattr(hf, "_TICK", 0.01)

    task_id = "hf-stop"
    run = await hf.hello_forever.start(
        task_id=task_id,
        input={"name": "alice", "session_id": _SESSION, "user_id": _USER},
    )

    # Let it tick a few times so there is real progress to stop.
    reached = await _wait_for_iterations(hf, task_id, minimum=2)

    # Request a stop: write the durable marker, then signal cancel. The worker
    # only treats cancel as a real stop when the marker is present.
    await _seed_item(hf, f"{task_id}{hf.STOP_SUFFIX}", {"stop": True})
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
    from resilient_hello_forever import agent as hf  # noqa: WPS433

    monkeypatch.setattr(hf, "_TICK", 0.01)

    task_id = "hf-marker-only"
    run = await hf.hello_forever.start(
        task_id=task_id,
        input={"name": "carol", "session_id": _SESSION, "user_id": _USER},
    )

    await _wait_for_iterations(hf, task_id, minimum=2)

    # Write ONLY the durable stop marker — do not call run.cancel().
    await _seed_item(hf, f"{task_id}{hf.STOP_SUFFIX}", {"stop": True})

    result = await asyncio.wait_for(run.result(), timeout=5.0)
    assert result["stopped"] is True
    assert result["name"] == "carol"


@pytest.mark.asyncio
async def test_resumes_from_existing_checkpoint(
    task_manager,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A pre-existing checkpoint makes the worker resume, not restart at 0."""
    from resilient_hello_forever import agent as hf  # noqa: WPS433

    monkeypatch.setattr(hf, "_TICK", 0.01)

    task_id = "hf-resume"
    await _seed_item(hf, task_id, {"name": "bob", "iterations": 5})

    run = await hf.hello_forever.start(
        task_id=task_id,
        input={"name": "bob", "session_id": _SESSION, "user_id": _USER},
    )

    # It must continue past the seeded cursor rather than counting up from 1.
    reached = await _wait_for_iterations(hf, task_id, minimum=6)
    assert reached >= 6

    await _seed_item(hf, f"{task_id}{hf.STOP_SUFFIX}", {"stop": True})
    await run.cancel()

    result = await asyncio.wait_for(run.result(), timeout=5.0)
    assert result["stopped"] is True
    assert result["iterations"] >= 6
