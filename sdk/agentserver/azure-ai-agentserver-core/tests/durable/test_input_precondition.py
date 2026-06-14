# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Tests — input acceptance preconditions.

Covers:
- TypeError when `if_last_input_id` is supplied without `input_id`.
- Fresh chain (input_id only) succeeds when no `_last_input_id` stored.
- Fresh chain (input_id only) rejected when chain already exists.
- Precondition match succeeds and advances `last_input_id`.
- Precondition mismatch raises `LastInputIdPreconditionFailed`.
- Suspended-resume path enforces the same precondition.
- Steering-append path enforces the same precondition.
- Legacy callers (no input_id / no if_last_input_id) unaffected.
- `_last_input_id` slot lands atomically with input persist on fresh-create.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from azure.ai.agentserver.core.durable import LastInputIdPreconditionFailed, TaskContext, task, multi_turn_task
from azure.ai.agentserver.core.durable._exceptions import TaskPreconditionFailed


# ---------------------------------------------------------------------------
# Module-level tasks (must be module level for `get_type_hints` to resolve
# the TaskContext annotation).
# ---------------------------------------------------------------------------


@multi_turn_task(name="us2-fast-completing", steerable=False)
async def _fast_completing(ctx: TaskContext[dict]) -> dict:
    return {"echo": ctx.input}


@multi_turn_task(name="us2-steerable-suspending", steerable=True)
async def _steerable_suspending(ctx: TaskContext[dict]) -> dict:
    """Steerable task that suspends after first input."""
    return None


@multi_turn_task(name="us2-long-running-steerable", steerable=True)
async def _long_running_steerable(ctx: TaskContext[dict]) -> dict:
    """Steerable task that takes a while so we can steer it."""
    try:
        await asyncio.wait_for(ctx.cancel.wait(), timeout=1.5)
    except asyncio.TimeoutError:
        pass
    return {"final": "ok"}


# ---------------------------------------------------------------------------
# Manager setup helpers
# ---------------------------------------------------------------------------


async def _setup_manager(tmp_path: Path):
    from azure.ai.agentserver.core.durable._local_provider import LocalFileTaskProvider
    from azure.ai.agentserver.core.durable._manager import TaskManager
    import azure.ai.agentserver.core.durable._manager as mgr_mod

    provider = LocalFileTaskProvider(Path(str(tmp_path)))
    config = type(
        "C",
        (),
        {
            "agent_name": "test-agent",
            "session_id": "test-session",
            "agent_version": "1.0.0",
            "is_hosted": False,
        },
    )()
    manager = TaskManager(config=config, provider=provider)
    mgr_mod._manager = manager
    await manager.startup()
    return manager, mgr_mod


async def _teardown_manager(manager, mgr_mod):
    await manager.shutdown()
    mgr_mod._manager = None


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_exception_hierarchy() -> None:
    """LastInputIdPreconditionFailed inherits from TaskPreconditionFailed."""
    assert issubclass(LastInputIdPreconditionFailed, TaskPreconditionFailed)


@pytest.mark.asyncio
async def test_if_last_input_id_without_input_id_raises_type_error(tmp_path: Path) -> None:
    """Caller mistake: precondition without an advancing id is meaningless."""
    manager, mgr_mod = await _setup_manager(tmp_path)
    try:
        with pytest.raises(TypeError, match="if_last_input_id requires input_id"):
            await _fast_completing.start(task_id="t-1", input={"x": 1}, if_last_input_id="must-match-something")
    finally:
        await _teardown_manager(manager, mgr_mod)


@pytest.mark.asyncio
async def test_fresh_chain_input_id_only_succeeds(tmp_path: Path) -> None:
    """input_id alone on a fresh task succeeds and seeds the framework slot."""
    manager, mgr_mod = await _setup_manager(tmp_path)
    try:
        run = await _fast_completing.start(task_id="t-fresh-1", input={"hi": "there"}, input_id="msg-A")
        await run.result()
        info = await manager.provider.get("t-fresh-1")
        assert info is not None
        assert info.payload["_last_input_id"] == "msg-A"
    finally:
        await _teardown_manager(manager, mgr_mod)


@pytest.mark.asyncio
async def test_precondition_match_advances_last_input_id_on_resume(tmp_path: Path) -> None:
    """Precondition match on suspended-resume advances last_input_id atomically."""
    manager, mgr_mod = await _setup_manager(tmp_path)
    try:
        run1 = await _steerable_suspending.start(task_id="t-precond-match", input={"turn": 1}, input_id="msg-1")
        await asyncio.sleep(0.2)  # let it suspend
        info = await manager.provider.get("t-precond-match")
        assert info is not None
        assert info.status == "suspended"
        assert info.payload["_last_input_id"] == "msg-1"

        run2 = await _steerable_suspending.start(
            task_id="t-precond-match", input={"turn": 2}, input_id="msg-2", if_last_input_id="msg-1"
        )
        await asyncio.sleep(0.2)
        info = await manager.provider.get("t-precond-match")
        assert info is not None
        assert info.payload["_last_input_id"] == "msg-2"
    finally:
        await _teardown_manager(manager, mgr_mod)


@pytest.mark.asyncio
async def test_precondition_mismatch_raises_on_resume(tmp_path: Path) -> None:
    """Wrong if_last_input_id on suspended-resume raises typed exception."""
    manager, mgr_mod = await _setup_manager(tmp_path)
    try:
        run1 = await _steerable_suspending.start(task_id="t-precond-mismatch", input={"turn": 1}, input_id="msg-1")
        await asyncio.sleep(0.2)

        with pytest.raises(LastInputIdPreconditionFailed) as excinfo:
            await _steerable_suspending.start(
                task_id="t-precond-mismatch", input={"turn": 2}, input_id="msg-2", if_last_input_id="msg-stale-XYZ"
            )

        # Exposed fields carry the diagnostic information.
        #: exception.task_id removed
        #: exception.task_id removed
        assert excinfo.value.actual_last_input_id == "msg-1"

        # State must be untouched.
        info = await manager.provider.get("t-precond-mismatch")
        assert info is not None
        assert info.payload["_last_input_id"] == "msg-1"
    finally:
        await _teardown_manager(manager, mgr_mod)


@pytest.mark.asyncio
async def test_input_id_only_advances_chain_head_unconditionally(tmp_path: Path) -> None:
    """input_id-only on a task that already has a stored chain succeeds.

    Per the framework's idempotency-only mode: when the caller supplies
    ``input_id`` without ``if_last_input_id``, no predecessor assertion
    is performed and the chain head is advanced unconditionally. This
    supports use cases like conversation-grouped multi-turn where
    sequential delivery is enforced externally (e.g. via task_id
    collapse + TaskConflictError) and the per-turn ``input_id`` is
    only used for chain-head tracking and idempotency.
    """
    manager, mgr_mod = await _setup_manager(tmp_path)
    try:
        await _steerable_suspending.start(task_id="t-fresh-rejected", input={"turn": 1}, input_id="msg-1")
        await asyncio.sleep(0.2)

        info = await manager.provider.get("t-fresh-rejected")
        assert info is not None
        assert info.payload["_last_input_id"] == "msg-1"

        # input_id-only on a task with a stored chain: succeeds and
        # advances the chain head without precondition assertion.
        await _steerable_suspending.start(
            task_id="t-fresh-rejected",
            input={"turn": 2},
            input_id="msg-2",
            # No if_last_input_id: idempotency-only mode.
        )
        await asyncio.sleep(0.2)

        info = await manager.provider.get("t-fresh-rejected")
        assert info is not None
        assert info.payload["_last_input_id"] == "msg-2"
    finally:
        await _teardown_manager(manager, mgr_mod)


@pytest.mark.asyncio
async def test_legacy_callers_unaffected(tmp_path: Path) -> None:
    """No input_id, no if_last_input_id: framework slot is not seeded."""
    manager, mgr_mod = await _setup_manager(tmp_path)
    try:
        run = await _fast_completing.start(task_id="t-legacy", input={"x": 1})
        await run.result()
        info = await manager.provider.get("t-legacy")
        assert info is not None
        # Legacy path doesn't seed the slot at all.
        assert "_last_input_id" not in info.payload
    finally:
        await _teardown_manager(manager, mgr_mod)


@pytest.mark.asyncio
async def test_precondition_match_on_steering_append(tmp_path: Path) -> None:
    """Precondition match on steering-append (in_progress task) advances slot."""
    manager, mgr_mod = await _setup_manager(tmp_path)
    try:
        run1 = await _long_running_steerable.start(task_id="t-steer-precond", input={"turn": 1}, input_id="msg-1")
        # Give it a moment to actually start running.
        await asyncio.sleep(0.1)

        # Second start while task is in_progress -> steering-append path.
        run2 = await _long_running_steerable.start(
            task_id="t-steer-precond", input={"turn": 2}, input_id="msg-2", if_last_input_id="msg-1"
        )
        # Wait for the ack (signal sent).
        await asyncio.sleep(0.3)
        info = await manager.provider.get("t-steer-precond")
        assert info is not None
        assert info.payload["_last_input_id"] == "msg-2"
    finally:
        await _teardown_manager(manager, mgr_mod)


@pytest.mark.asyncio
async def test_precondition_mismatch_on_steering_append(tmp_path: Path) -> None:
    """Wrong if_last_input_id during steering-append raises typed exception."""
    manager, mgr_mod = await _setup_manager(tmp_path)
    try:
        run1 = await _long_running_steerable.start(task_id="t-steer-mismatch", input={"turn": 1}, input_id="msg-1")
        await asyncio.sleep(0.1)

        with pytest.raises(LastInputIdPreconditionFailed) as excinfo:
            await _long_running_steerable.start(
                task_id="t-steer-mismatch", input={"turn": 2}, input_id="msg-2", if_last_input_id="msg-NOPE"
            )
        #: exception.task_id removed
        assert excinfo.value.actual_last_input_id == "msg-1"

        # Slot should still hold the original.
        info = await manager.provider.get("t-steer-mismatch")
        assert info is not None
        assert info.payload["_last_input_id"] == "msg-1"
    finally:
        await _teardown_manager(manager, mgr_mod)


@pytest.mark.asyncio
async def test_framework_namespace_isolated_from_user_payload(tmp_path: Path) -> None:
    """User cannot write `_last_input_id` via input meddling."""
    # We verify the slot lives in payload but not under user-controlled
    # keys like `input` or `metadata`.
    manager, mgr_mod = await _setup_manager(tmp_path)
    try:
        await _fast_completing.start(task_id="t-ns-iso", input={"_last_input_id": "USER-INJECTED"}, input_id="msg-A")
        info = await manager.provider.get("t-ns-iso")
        assert info is not None
        # The framework slot should reflect the framework-supplied id,
        # NOT the user-injected value (which lives under payload["input"]).
        assert info.payload["_last_input_id"] == "msg-A"
        # And the user input is preserved as-is under `input`.
        assert info.payload["input"] == {"_last_input_id": "USER-INJECTED"}
    finally:
        await _teardown_manager(manager, mgr_mod)


@pytest.mark.asyncio
async def test_precondition_check_source_signature() -> None:
    """Source-level: the precondition helper is wired into _lifecycle_start.

     note: the body of `_lifecycle_start` was extracted to
    `_lifecycle_start_inner` to host the  eviction-to-TaskConflictError
    wrapper. Source assertions follow the body to the inner method.
    """
    import inspect

    from azure.ai.agentserver.core.durable import _decorator as dec_mod

    src = inspect.getsource(dec_mod.Task._lifecycle_start_inner)
    # Pre-acceptance check is invoked unconditionally.
    assert "_check_input_precondition" in src
    #   framing annotation present.
    assert " " in src
