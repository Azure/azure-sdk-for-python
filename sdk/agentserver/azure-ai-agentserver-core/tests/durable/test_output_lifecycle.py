# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Spec 019 Area C — Output lifecycle (FR-C-004, SC-7).

Verifies the framework clears ``payload["output"]`` AND
``attachments["_output"]`` at every suspended→in_progress
transition AND at terminal-failure writes:

- Resume PATCH (suspended → in_progress, via .run() / .start() with
  a new input): co-clears the output slot + attachment in a single
  PATCH (FR-C-004 / SC-7).
- Steering drain Phase 1 PATCH: same co-clear (FR-C-004 / US-C2.C2.2).
- ``_handle_failure`` terminal write also clears output (no stale
  prior-success value on the failure-terminal record) — US-C2.C2.3 /
  C2.6.

Reference: docs/task-and-streaming-spec.md §11, §20, §50, §52, §53,
§59 C-OUT-4..6, C-SUS-4.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from azure.ai.agentserver.core.durable import (
    RetryPolicy,
    Suspended,
    TaskContext,
    TaskFailed,
    task,
)
import azure.ai.agentserver.core.durable._manager as mgr_mod
from azure.ai.agentserver.core.durable._local_provider import LocalFileTaskProvider
from azure.ai.agentserver.core.durable._manager import TaskManager


def _config_stub():
    return type(
        "C",
        (),
        {
            "agent_name": "test-agent",
            "session_id": "test-session",
            "agent_version": "1.0.0",
            "is_hosted": False,
        },
    )()


@pytest.fixture
def local(tmp_path: Path) -> LocalFileTaskProvider:
    return LocalFileTaskProvider(base_dir=tmp_path)


@pytest.mark.skip(reason="spec 022 FR-025: payload[output] no longer written, nothing to clear")
@pytest.mark.asyncio
async def test_resume_clears_payload_output_and_attachment(local) -> None:
    """FR-C-004 / SC-7 — suspended→in_progress resume PATCH MUST set
    ``payload["output"] = null`` AND delete the ``_output`` attachment.

    Strategy: suspend with output=A; verify the record carries A;
    resume the task with a new input and arrange for the handler to
    suspend again WITHOUT producing an output; verify between the
    resume PATCH and the second suspend the output is null AND no
    ``_output`` attachment exists. The cleanest way to inspect the
    "in-flight resumed" state is to check the persisted record
    immediately after resume but BEFORE the handler exits — we use
    a barrier inside the handler.
    """
    import asyncio

    in_handler = asyncio.Event()
    release_handler = asyncio.Event()
    turn_count = 0

    @task(name="resume_clears_output", ephemeral=False)
    async def my_task(ctx: TaskContext[str]) -> Suspended[str]:
        nonlocal turn_count
        turn_count += 1
        if turn_count == 1:
            return await ctx.suspend(output="A", reason="first suspend")
        # Second turn (after resume): signal we entered, wait, then
        # suspend with no output.
        in_handler.set()
        await release_handler.wait()
        return await ctx.suspend(output=None, reason="second suspend")

    manager = TaskManager(config=_config_stub(), provider=local)
    mgr_mod._manager = manager
    await manager.startup()
    try:
        # First turn: suspends with output=A.
        result1 = await my_task.run(task_id="t-resume-clear", input="x")
    # spec 022: result is raw output (Suspended wrapper removed)
        # Sanity: record has output=A persisted.
        snap_after_suspend1 = await my_task.get("t-resume-clear")
        assert snap_after_suspend1 is not None
        assert snap_after_suspend1.output == "A"

        # Resume the task. Don't await yet — we want to peek mid-flight.
        resume_task = asyncio.create_task(
            my_task.run(task_id="t-resume-clear", input="y")
        )
        await in_handler.wait()

        # While the handler is in turn 2, the record's output MUST
        # already be null (the resume PATCH co-cleared it).
        snap_mid_resume = await my_task.get("t-resume-clear")
        assert snap_mid_resume is not None
        assert snap_mid_resume.output is None, (
            f"after resume PATCH and BEFORE the next suspend, "
            f"snapshot.output MUST be None (the resume PATCH "
            f"co-clears the slot and the _output attachment). "
            f"Got {snap_mid_resume.output!r}. FR-C-004 / SC-7."
        )

        # And no _output attachment should remain on the raw record.
        raw = await local.get("t-resume-clear")
        assert raw is not None
        if raw.attachments is not None:
            assert "_output" not in raw.attachments, (
                f"_output attachment from the prior suspend leaked "
                f"into the resumed turn; FR-C-004 requires the "
                f"resume PATCH to delete it in the same round-trip."
            )

        release_handler.set()
        await resume_task
    finally:
        await manager.shutdown()
        mgr_mod._manager = None


@pytest.mark.skip(reason="spec 022 FR-025/FR-026: payload[output] no longer written, nothing to clear")
@pytest.mark.asyncio
async def test_drain_phase1_clears_payload_output_and_attachment(local) -> None:
    """FR-C-004 / US-C2.C2.2 — drain Phase 1 PATCH MUST co-clear the
    output slot + attachment (same rule as resume).

    Strategy: steerable task; turn 1 suspends with output=A; turn 2
    is triggered by a steering append. While turn 2 is in flight,
    the output must already be cleared (Phase 1 of the drain did
    the co-clear at turn-start).

    NOTE: a steering append against a `suspended` task delivers the
    new input AS the next turn via the same drain machinery — so
    this test exercises drain Phase 1 against a steerable task that
    suspended with output and was steered. The framework's drain
    Phase 1 PATCH MUST clear the prior output.
    """
    import asyncio

    in_handler = asyncio.Event()
    release_handler = asyncio.Event()
    turn_count = 0

    @task(name="drain_clears_output", steerable=True, ephemeral=False)
    async def my_task(ctx: TaskContext[str]) -> Suspended[str]:
        nonlocal turn_count
        turn_count += 1
        if turn_count == 1:
            # First turn suspends with output=A; second turn drives the
            # drain check.
            return await ctx.suspend(output="A", reason="first")
        in_handler.set()
        await release_handler.wait()
        return await ctx.suspend(output=None, reason="second")

    manager = TaskManager(config=_config_stub(), provider=local)
    mgr_mod._manager = manager
    await manager.startup()
    try:
        first = await my_task.run(task_id="t-drain-clear", input="x")
    # spec 022: result is raw output (Suspended wrapper removed)

        # Verify intermediate output state.
        snap1 = await my_task.get("t-drain-clear")
        assert snap1 is not None and snap1.output == "A"

        # Resume via .start() (same task_id, new input) — for steerable
        # suspended tasks, .start() drives the drain Phase 1.
        resume_run_task = asyncio.create_task(
            my_task.run(task_id="t-drain-clear", input="y")
        )
        await in_handler.wait()
        snap_mid = await my_task.get("t-drain-clear")
        assert snap_mid is not None
        assert snap_mid.output is None, (
            f"after drain Phase 1, snapshot.output MUST be None "
            f"(co-cleared). Got {snap_mid.output!r}. FR-C-004."
        )
        release_handler.set()
        await resume_run_task
    finally:
        await manager.shutdown()
        mgr_mod._manager = None


@pytest.mark.skip(reason="spec 022 FR-027: payload[error] no longer written, nothing to clear")
@pytest.mark.asyncio
async def test_handle_failure_clears_output(local) -> None:
    """US-C2.C2.3 / C2.6 — ``_handle_failure`` terminal write MUST
    clear ``payload["output"]`` (and the attachment) so the
    failure-terminal record carries the failure cause, not a stale
    prior-success output.

    Strategy: a non-ephemeral task with retries: first attempt
    suspends with output=A, second attempt raises (handler raises
    a non-retryable exception, so retry budget is exhausted). The
    terminal record's status is 'completed' with an error; output
    MUST be None.
    """
    turn_count = 0

    @task(name="failure_clears_output", ephemeral=False)
    async def my_task(ctx: TaskContext[str]) -> Suspended[str]:
        nonlocal turn_count
        turn_count += 1
        if turn_count == 1:
            return await ctx.suspend(output="A", reason="first")
        raise RuntimeError("boom")

    manager = TaskManager(config=_config_stub(), provider=local)
    mgr_mod._manager = manager
    await manager.startup()
    try:
        first = await my_task.run(task_id="t-fail-clear", input="x")
    # spec 022: result is raw output (Suspended wrapper removed)

        with pytest.raises(TaskFailed):
            await my_task.run(task_id="t-fail-clear", input="y")

        snap = await my_task.get("t-fail-clear")
        assert snap is not None
        assert snap.status == "completed"
        assert snap.error is not None
        assert snap.output is None, (
            f"failure-terminal record carries stale output "
            f"{snap.output!r}; US-C2.C2.3 / C-OUT-6 require "
            f"_handle_failure to co-clear the output slot + "
            f"attachment in the terminal PATCH."
        )
        # And the raw record's attachments must not have a stale _output.
        raw = await local.get("t-fail-clear")
        assert raw is not None
        if raw.attachments is not None:
            assert "_output" not in raw.attachments, (
                "stale _output attachment leaked into failure-terminal record"
            )
    finally:
        await manager.shutdown()
        mgr_mod._manager = None
