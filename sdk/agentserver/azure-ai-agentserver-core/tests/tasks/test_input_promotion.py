# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT license.
""" — Function-input promotion end-to-end (Phase 3).

Drives a fresh ``TaskManager`` + ``LocalFileTaskProvider`` through the
``@task`` API to verify:

- Small inputs stay inline (no attachments written).
- Large inputs are promoted to ``attachments["input"]`` with a ref
  slot in ``payload["input"]``.
- Recovery from both shapes reconstructs the original input value.
- Suspend deletes the promoted attachment + clears the ref atomically.
- Oversized inputs (> 10 MiB) raise ``InputTooLarge`` pre-HTTP.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import pytest
import pytest_asyncio

from azure.ai.agentserver.core.tasks import TaskContext, task, multi_turn_task
from azure.ai.agentserver.core.tasks._attachments import (
    _FUNCTION_INPUT_KEY,
    _INPUT_THRESHOLD_BYTES,
    _MAX_ATTACHMENT_SIZE_BYTES,
    _compute_attachment_hash,
    _is_ref,
    _ref_hash,
    _ref_key,
)
from azure.ai.agentserver.core.tasks._exceptions import InputTooLarge
from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
from azure.ai.agentserver.core.tasks._manager import TaskManager, set_task_manager


def _config_stub(session_id: str = "s018-test-session"):
    return type(
        "C",
        (),
        {
            "agent_name": "s018-test-agent",
            "session_id": session_id,
            "agent_version": "1.0.0",
            "is_hosted": False,
        },
    )()


@pytest_asyncio.fixture
async def manager_local(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Real TaskManager backed by LocalFileTaskProvider at tmp_path."""
    # (Spec 024 Phase 3a) Use AGENTSERVER_STATE_ROOT so any code that
    # uses the _config.resolve_state_subdir resolver gets
    # isolated to tmp_path. The explicit base_dir below still wins for
    # the LocalFileTaskProvider directly.
    monkeypatch.setenv("AGENTSERVER_STATE_ROOT", str(tmp_path))
    monkeypatch.delenv("FOUNDRY_HOSTING_ENVIRONMENT", raising=False)

    config = _config_stub()
    mgr = TaskManager(
        config=config, provider=LocalFileTaskProvider(base_dir=tmp_path / "tasks"), shutdown_event=asyncio.Event()
    )
    set_task_manager(mgr)
    await mgr.startup()
    try:
        yield mgr
    finally:
        await mgr.shutdown()
        set_task_manager(None)


# Each test defines its own task to avoid cross-test fn-name collisions
# in the resilient registry. The task body just echoes the input back.


@pytest.mark.asyncio
async def test_small_input_stays_inline_in_payload(manager_local: TaskManager) -> None:
    """SC-1: function input ≤ 200 KiB stays as a raw value in payload['input']."""

    started = asyncio.Event()
    proceed = asyncio.Event()

    @multi_turn_task(name="t-small-inline", steerable=True)
    async def blocking(ctx: TaskContext[dict]) -> dict:
        started.set()
        await proceed.wait()
        return {"ok": True}

    run = await blocking.start(task_id="t-small-1", input={"topic": "ice cream"})
    await asyncio.wait_for(started.wait(), timeout=2.0)

    # Mid-run inspection: small input MUST be inline (raw value).
    info = await manager_local.provider.get("t-small-1")
    assert info is not None
    assert info.payload is not None
    # Raw value, not a ref dict.
    assert not _is_ref(info.payload["input"])
    assert info.payload["input"] == {"topic": "ice cream"}
    # No attachments created for an inline input.
    assert info.attachments is None or _FUNCTION_INPUT_KEY not in (info.attachments or {})

    proceed.set()
    await run.result()


@pytest.mark.asyncio
async def test_large_input_promoted_to_attachment(manager_local: TaskManager) -> None:
    """SC-2 + SC-3: function input > 200 KiB → attachment; recovers via ref."""

    big = {"history": "x" * (_INPUT_THRESHOLD_BYTES + 1024)}  # ~ 201 KiB

    seen_input: dict[str, Any] = {}

    @multi_turn_task(name="t-big-input", steerable=True)
    async def capture(ctx: TaskContext[dict]) -> dict:
        seen_input["v"] = ctx.input  # capture so test can compare
        return {"captured": True}

    run = await capture.start(task_id="t-big", input=big)
    res = await run.result()
    #: result is raw output (Suspended wrapper removed)
    assert res == {"captured": True}

    # Handler MUST have received the original value (regardless of promotion).
    assert seen_input["v"] == big

    # After suspend, the attachment MUST have been deleted (C-8/SC-9).
    info = await manager_local.provider.get("t-big")
    assert info is not None
    assert info.attachments is None or _FUNCTION_INPUT_KEY not in (info.attachments or {})


@pytest.mark.asyncio
async def test_large_input_writes_ref_and_attachment_atomically(manager_local: TaskManager) -> None:
    """SC-2: at create time the task MUST have attachments['_input'] + ref in payload['input']."""

    big = {"v": "y" * (_INPUT_THRESHOLD_BYTES + 50)}

    # Build a task that blocks so we can inspect mid-run.
    started = asyncio.Event()
    proceed = asyncio.Event()

    @multi_turn_task(name="t-big-blocking", steerable=True)
    async def blocking(ctx: TaskContext[dict]) -> dict:
        started.set()
        await proceed.wait()
        return {"ok": True}

    run = await blocking.start(task_id="t-big-block", input=big)
    await asyncio.wait_for(started.wait(), timeout=2.0)

    # Mid-run: payload.input is the ref; attachments has _input.
    info = await manager_local.provider.get("t-big-block")
    assert info is not None
    assert info.attachments is not None
    assert _FUNCTION_INPUT_KEY in info.attachments
    # The handler-captured input matches what's in the attachment.
    assert info.attachments[_FUNCTION_INPUT_KEY] == big
    # payload["input"] is a ref pointing at it.
    assert _is_ref(info.payload["input"])
    assert _ref_key(info.payload["input"]) == _FUNCTION_INPUT_KEY
    assert _ref_hash(info.payload["input"]) == _compute_attachment_hash(big)

    proceed.set()
    await run.result()


@pytest.mark.asyncio
async def test_oversized_input_raises_input_too_large(manager_local: TaskManager) -> None:
    """SC-10: an input that serializes to > 10 MiB raises pre-HTTP."""

    too_big = {"v": "z" * (_MAX_ATTACHMENT_SIZE_BYTES + 100)}

    @task(name="t-oversize")
    async def never_runs(ctx: TaskContext[dict]) -> dict:
        return ctx.input  # pragma: no cover -- shouldn't run

    with pytest.raises(InputTooLarge) as excinfo:
        await never_runs.start(task_id="t-oversize-1", input=too_big)
    #: exception.task_id removed


@pytest.mark.asyncio
async def test_suspend_with_promoted_input_deletes_attachment_atomically(manager_local: TaskManager) -> None:
    """SC-9 + C-8: suspend PATCH must include attachments={'_input': None}."""

    big = {"v": "w" * (_INPUT_THRESHOLD_BYTES + 1000)}

    @multi_turn_task(name="t-suspend-clear", steerable=True)
    async def will_suspend(ctx: TaskContext[dict]) -> dict:
        return None

    run = await will_suspend.start(task_id="t-suspend-clear-1", input=big)
    await run.result()

    info = await manager_local.provider.get("t-suspend-clear-1")
    assert info is not None
    # Attachment must be GONE (deleted by the suspend co-PATCH).
    assert info.attachments is None or _FUNCTION_INPUT_KEY not in (info.attachments or {})
    # payload["input"] must also be cleared.
    assert info.payload is None or info.payload.get("input") is None


# --------------------------------------------------------------------------- #
# TDD-gap tests (added retroactively to make the suite a true contract guard)
# --------------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_recovery_surfaces_promoted_input_as_ctx_input(manager_local: TaskManager) -> None:
    """SC-3 end-to-end: after a "crash" (manager teardown + fresh manager
    + recovery), a task whose input was promoted MUST present that input
    to ``ctx.input`` exactly as the caller passed it.

    This pins the read path through the recovery code path, not just
    the cold-start read path (covered by
    ``test_large_input_promoted_to_attachment``).
    """
    big = {"v": "r" * (_INPUT_THRESHOLD_BYTES + 100), "marker": "recovery-probe"}

    # Define + register the handler. @task decoration is lazy: the
    # callback only enters _resume_callbacks at the first .start() call.
    # We manually register so recovery dispatch works without a prior
    # in-band start.
    captured: dict[str, Any] = {}

    @multi_turn_task(name="t-recovery-capture", steerable=True)
    async def recover(ctx: TaskContext[dict]) -> dict:
        captured["input"] = ctx.input
        captured["entry_mode"] = ctx.entry_mode
        return None

    manager_local._resume_callbacks["t-recovery-capture"] = recover._fn  # type: ignore[attr-defined]
    manager_local._resume_opts["t-recovery-capture"] = recover._opts  # type: ignore[attr-defined]

    # Plant a task in the store with a promoted input shape — simulates
    # what a previous lifetime would have written before being evicted.
    from azure.ai.agentserver.core.tasks._attachments import _FUNCTION_INPUT_KEY, _make_ref
    from azure.ai.agentserver.core.tasks._models import TaskCreateRequest

    ref = _make_ref(_FUNCTION_INPUT_KEY, big)
    await manager_local.provider.create(
        TaskCreateRequest(
            agent_name=manager_local._config.agent_name,
            session_id=manager_local._config.session_id,
            id="t-recovery-1",
            title="recovery-probe",
            status="in_progress",
            lease_owner=manager_local._lease_owner,
            lease_instance_id="prior-instance-that-died",
            lease_duration_seconds=60,
            payload={"input": ref, "metadata": {}, "schema_version": "1"},
            attachments={_FUNCTION_INPUT_KEY: big},
            tags={"task_name": "t-recovery-capture"},
            source={"name": "t-recovery-capture", "type": "agentserver.task"},
        )
    )

    # Drive recovery scan directly (simulates the periodic loop / startup).
    await manager_local._recover_stale_tasks()
    # Allow the recovered handler to run.
    await asyncio.sleep(0.5)

    # The handler MUST have seen the original input — promotion is invisible.
    assert "input" in captured, "recovered handler never ran"
    assert captured["input"] == big
    assert captured["entry_mode"] == "recovered"
