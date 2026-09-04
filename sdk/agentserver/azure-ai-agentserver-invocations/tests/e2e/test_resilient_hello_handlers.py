# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""HTTP-handler smoke tests for the minimal resilient samples.

The other e2e tests drive the ``@task`` functions directly; they deliberately
bypass ``app.py``. This file exercises the actual invoke / poll / cancel
handlers of both minimal samples so handler-level regressions (a ``NameError``
in the cancel path, a malformed-body 500, a wrong status code, or a
pre-checkpoint 404) are caught. The handler decorators return the original
function unmodified, so we call them directly with a lightweight fake request.

Fully self-contained: local file-backed task provider + state store rooted at
the test's ``tmp_path``. No LLM, no cloud.
"""

from __future__ import annotations

import asyncio
import json
import types
from pathlib import Path

import pytest
import pytest_asyncio


class _Req:
    """Minimal stand-in for the Starlette request the handlers consume."""

    def __init__(
        self,
        *,
        body: bytes = b"",
        invocation_id: str = "",
        session_id: str = "",
        user_id: str = "u",
        call_id: str = "c",
    ) -> None:
        self._body = body
        self.state = types.SimpleNamespace(
            invocation_id=invocation_id,
            session_id=session_id,
            user_id=user_id,
            call_id=call_id,
        )

    async def body(self) -> bytes:
        return self._body


@pytest.fixture(autouse=True)
def _samples_on_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """Prepend the samples dir to ``sys.path`` (auto-restored after each test)."""
    samples = Path(__file__).resolve().parent.parent.parent / "samples"
    monkeypatch.syspath_prepend(str(samples))


@pytest_asyncio.fixture
async def task_manager(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """A real TaskManager backed by the local file provider at tmp_path."""
    import asyncio  # noqa: WPS433

    (tmp_path / "tasks").mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("AGENTSERVER_STATE_ROOT", str(tmp_path))
    monkeypatch.delenv("FOUNDRY_HOSTING_ENVIRONMENT", raising=False)

    from azure.ai.agentserver.core.tasks import (  # noqa: WPS433
        resilient_tasks_enabled,
        set_resilient_tasks_enabled,
    )
    from azure.ai.agentserver.core.tasks._manager import (  # noqa: WPS433
        TaskManager,
        set_task_manager,
    )

    # Importing the sample app modules flips the process-global opt-in flag to
    # True. Save and restore it so the flag does not leak into later tests and
    # make their behavior test-order dependent.
    prev_enabled = resilient_tasks_enabled()

    config = type(
        "C",
        (),
        {
            "agent_name": "test-hello-handlers",
            "session_id": "test-hello-handlers-session",
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
        set_resilient_tasks_enabled(prev_enabled)


def _status(response) -> tuple[int, dict]:
    return response.status_code, json.loads(response.body)


@pytest.mark.asyncio
async def test_hello_forever_handlers_lifecycle(
    task_manager, monkeypatch: pytest.MonkeyPatch
) -> None:
    """invoke -> running -> cancel -> stopped, plus 404 and 400 paths."""
    from resilient_hello_forever import agent as hf  # noqa: WPS433
    import resilient_hello_forever.app as app  # noqa: WPS433

    monkeypatch.setattr(hf, "_TICK", 0.01)
    inv, sess = "inv-hf-1", "sess-hf"

    code, body = _status(
        await app.handle_invoke(
            _Req(body=b'{"name": "ada"}', invocation_id=inv, session_id=sess)
        )
    )
    assert code == 202 and body["invocation_id"] == inv

    code, body = _status(
        await app.handle_get(_Req(invocation_id=inv, session_id=sess))
    )
    assert code == 200 and body["status"] == "running"

    # The cancel path previously raised NameError after writing the marker.
    code, body = _status(
        await app.handle_cancel(_Req(invocation_id=inv, session_id=sess))
    )
    assert code == 200 and body["status"] == "cancelling"

    code, body = _status(
        await app.handle_get(_Req(invocation_id=inv, session_id=sess))
    )
    assert code == 200 and body["status"] == "stopped"

    # Reusing the same invocation id after it stopped must NOT start a second
    # worker against the stale checkpoint/marker — the durable record already
    # exists, so invoke returns 409 with the terminal status.
    code, body = _status(
        await app.handle_invoke(
            _Req(body=b'{"name": "ada"}', invocation_id=inv, session_id=sess)
        )
    )
    assert code == 409 and body["status"] == "stopped"

    # A failed worker (one-shot record deleted) is surfaced from the durable
    # ``status: failed`` the worker persists — not reported as ``running`` forever.
    fail_inv = "inv-hf-failed"
    fail_tid = hf.durable_task_id(sess, fail_inv, "u")
    failed_store = await hf.open_checkpoint_store(sess, "u")
    async with failed_store:
        await failed_store.set_item(
            fail_tid, {"name": "z", "iterations": 4, "status": "failed", "error": "boom"}
        )
    code, body = _status(
        await app.handle_get(_Req(invocation_id=fail_inv, session_id=sess))
    )
    assert code == 200 and body["status"] == "failed" and body["error"] == "boom"

    # Unknown invocation: poll and cancel both 404, and cancel must NOT persist a
    # stop marker for it.
    code, _ = _status(await app.handle_get(_Req(invocation_id="nope", session_id=sess)))
    assert code == 404
    code, _ = _status(
        await app.handle_cancel(_Req(invocation_id="nope2", session_id=sess))
    )
    assert code == 404

    # Malformed body shapes -> 400 (not 500): non-object JSON and invalid UTF-8.
    code, _ = _status(
        await app.handle_invoke(_Req(body=b"[]", invocation_id="inv-hf-2", session_id=sess))
    )
    assert code == 400
    code, _ = _status(
        await app.handle_invoke(
            _Req(body=b"\xff\xfe", invocation_id="inv-hf-3", session_id=sess)
        )
    )
    assert code == 400


@pytest.mark.asyncio
async def test_hello_world_recovers_orphaned_seed(
    task_manager, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A nonterminal durable record with no live task is re-scheduled, not 409'd.

    Simulates the orphan window: an earlier attempt seeded ``in_progress`` then
    crashed before the TaskManager record became durable. A later POST must
    (re-)schedule the task idempotently and run it to completion rather than
    wedging behind a permanent ``in_progress`` record with nothing to recover.
    """
    from resilient_hello_world import agent as hw  # noqa: WPS433
    import resilient_hello_world.app as app  # noqa: WPS433

    monkeypatch.setattr(hw, "_STEP_DELAY", 0.0)
    inv, sess = "inv-hw-orphan", "sess-hw"

    # Seed an orphaned nonterminal record directly (no task started) with real
    # progress (3/5) so we can prove the retry does not roll it back.
    task_id = hw.durable_task_id(sess, inv, "u")
    store = await hw.open_checkpoint_store(sess, "u")
    async with store:
        await store.create_item(
            task_id, {"name": "ada", "steps": 5, "completed_steps": 3, "status": "in_progress"}
        )

    # POST with a DIFFERENT body (steps=99): must recover (202) but reuse the
    # PERSISTED parameters, not the retry's — so it finishes at the original 5.
    code, body = _status(
        await app.handle_invoke(
            _Req(body=b'{"name": "eve", "steps": 99}', invocation_id=inv, session_id=sess)
        )
    )
    assert code == 202, f"expected orphan recovery (202), got {code}: {body}"

    # And it runs to completion at the persisted total (5), preserving progress.
    for _ in range(200):
        code, body = _status(
            await app.handle_get(_Req(invocation_id=inv, session_id=sess))
        )
        if body["status"] == "completed":
            break
        await asyncio.sleep(0.01)
    assert body["status"] == "completed"
    assert body["total_steps"] == 5 and body["completed_steps"] == 5


@pytest.mark.asyncio
async def test_hello_world_handlers(
    task_manager, monkeypatch: pytest.MonkeyPatch
) -> None:
    """invoke -> poll (never 404 for a started run), plus 400/404 paths."""
    from resilient_hello_world import agent as hw  # noqa: WPS433
    import resilient_hello_world.app as app  # noqa: WPS433

    monkeypatch.setattr(hw, "_STEP_DELAY", 0.0)
    inv, sess = "inv-hw-1", "sess-hw"

    code, body = _status(
        await app.handle_invoke(
            _Req(body=b'{"name": "ada", "steps": 3}', invocation_id=inv, session_id=sess)
        )
    )
    assert code == 202 and body["total_steps"] == 3

    # Drain the (near-instant) background job to a terminal state so subsequent
    # assertions are deterministic rather than racing the task's writes.
    final = None
    for _ in range(200):
        code, body = _status(
            await app.handle_get(_Req(invocation_id=inv, session_id=sess))
        )
        assert code == 200 and body["status"] in ("in_progress", "completed")
        if body["status"] == "completed":
            final = body
            break
        await asyncio.sleep(0.01)
    assert final is not None and final["completed_steps"] == 3

    # Reusing an existing invocation id must not start a second task against the
    # existing checkpoint — invoke returns 409 with the current (terminal) status.
    code, body = _status(
        await app.handle_invoke(
            _Req(body=b'{"name": "ada", "steps": 3}', invocation_id=inv, session_id=sess)
        )
    )
    assert code == 409 and body["status"] == "completed"

    # A failed run (one-shot record deleted) is surfaced from the durable
    # ``status: failed`` the task persists — not stuck at ``in_progress`` forever.
    fail_inv = "inv-hw-failed"
    fail_tid = hw.durable_task_id(sess, fail_inv, "u")
    failed_store = await hw.open_checkpoint_store(sess, "u")
    async with failed_store:
        await failed_store.set_item(
            fail_tid,
            {"name": "z", "steps": 5, "completed_steps": 2, "status": "failed", "error": "boom"},
        )
    code, body = _status(
        await app.handle_get(_Req(invocation_id=fail_inv, session_id=sess))
    )
    assert code == 200 and body["status"] == "failed" and body["error"] == "boom"

    code, _ = _status(await app.handle_get(_Req(invocation_id="nope", session_id=sess)))
    assert code == 404

    # Malformed / invalid steps -> 400 (non-object body, non-positive, bool,
    # float, and invalid UTF-8 bytes).
    for raw in (b"[]", b'{"steps": 0}', b'{"steps": true}', b'{"steps": 2.9}', b"\xff\xfe"):
        code, _ = _status(
            await app.handle_invoke(
                _Req(body=raw, invocation_id="inv-hw-x", session_id=sess)
            )
        )
        assert code == 400, f"expected 400 for body {raw!r}, got {code}"


@pytest.mark.asyncio
async def test_cancellable_handlers_lifecycle(
    task_manager, monkeypatch: pytest.MonkeyPatch
) -> None:
    """invoke -> cancel -> cancelling -> cancelled, plus reuse 409 / 404 / 400."""
    from resilient_cancellable import agent as cj  # noqa: WPS433
    import resilient_cancellable.app as app  # noqa: WPS433

    # Nonzero step delay so the job is still running when we cancel it.
    monkeypatch.setattr(cj, "_STEP_DELAY", 0.05)
    inv, sess = "inv-cj-1", "sess-cj"

    code, body = _status(
        await app.handle_invoke(
            _Req(body=b'{"name": "ada", "steps": 50}', invocation_id=inv, session_id=sess)
        )
    )
    assert code == 202 and body["total_steps"] == 50

    # Request cancel — writes the durable marker.
    code, body = _status(
        await app.handle_cancel(_Req(invocation_id=inv, session_id=sess))
    )
    assert code == 200 and body["status"] == "cancelling"

    # Poll until the job observes the marker and finalizes as ``cancelled`` (it
    # may briefly report ``cancelling`` first).
    final = None
    for _ in range(200):
        code, body = _status(
            await app.handle_get(_Req(invocation_id=inv, session_id=sess))
        )
        assert code == 200 and body["status"] in ("cancelling", "cancelled")
        if body["status"] == "cancelled":
            final = body
            break
        await asyncio.sleep(0.02)
    assert final is not None, "job did not reach 'cancelled'"
    assert final["completed_steps"] < 50

    # Reusing the invocation id after cancel must not start a second job.
    code, body = _status(
        await app.handle_invoke(
            _Req(body=b'{"name": "ada", "steps": 50}', invocation_id=inv, session_id=sess)
        )
    )
    assert code == 409 and body["status"] == "cancelled"

    # Unknown invocation: poll and cancel both 404 (cancel must not seed a marker).
    code, _ = _status(await app.handle_get(_Req(invocation_id="nope", session_id=sess)))
    assert code == 404
    code, _ = _status(
        await app.handle_cancel(_Req(invocation_id="nope2", session_id=sess))
    )
    assert code == 404

    # Malformed bodies -> 400 (non-object, non-positive steps, invalid UTF-8).
    for raw in (b"[]", b'{"steps": 0}', b"\xff\xfe"):
        code, _ = _status(
            await app.handle_invoke(
                _Req(body=raw, invocation_id="inv-cj-x", session_id=sess)
            )
        )
        assert code == 400, f"expected 400 for body {raw!r}, got {code}"
