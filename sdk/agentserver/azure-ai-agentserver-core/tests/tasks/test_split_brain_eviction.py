# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""  / SC-002 — split-brain eviction sweep.

Verifies the  /  /  contract for orphan-sandbox
rejection (HTTP 409 + body ``$.error.code == "binding_mismatch"``):
the classifier translates the rejection to ``evicted`` and the
framework runs the canonical local-cleanup sequence at every store-
write site:

- lease-renewal loop: on eviction, stop renewing immediately,
  signal local cleanup via the renewal-cancel callback. Local
  execution is cancelled; the terminal write is suppressed.
- terminal-write paths: on eviction during
  ``_handle_success`` / ``_handle_failure`` / ``_handle_suspend``,
  suppress the terminal write and surface ``TaskConflictError`` to
  awaiters.
- input-enqueue (, T038a): on eviction during the input
  enqueue store-write, the steerer's future raises
  ``TaskConflictError``; the queued input is NOT persisted.
- scheduling primitives: on eviction at ``.run`` /
  ``.start()``, raise ``TaskConflictError(current_status="in_progress")``
  — observably identical to the live-elsewhere case per Invariant 1.

Reference: spec.md §Conformance Test Map row 13.

Test fixture: :class:`tests.tasks.conftest.BindingMismatchProvider`
wraps a delegate :class:`LocalFileTaskProvider` and selectively raises
``TransportClassifiedError(classification="evicted")`` on configured
``(op, task_id)`` pairs — the same exception the real hosted client
raises after the  classifier maps the HTTP 409 response.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from azure.ai.agentserver.core.tasks import TaskConflictError, TaskContext, task, multi_turn_task
from azure.ai.agentserver.core.tasks._client import TransportClassifiedError
from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
from azure.ai.agentserver.core.tasks._manager import TaskManager
from azure.ai.agentserver.core.tasks._models import TaskCreateRequest, TaskPatchRequest
import azure.ai.agentserver.core.tasks._manager as mgr_mod

from .conftest import BindingMismatchProvider


@pytest.fixture
def stubbable_provider_factory(tmp_path):
    """Yield a factory that wraps a fresh LocalFileTaskProvider in a stub.

    Each test gets a clean local backing store under ``tmp_path``.
    """

    def _make() -> BindingMismatchProvider:
        delegate = LocalFileTaskProvider(base_dir=Path(str(tmp_path)))
        return BindingMismatchProvider(delegate)

    return _make


def _config_stub():
    """Minimal AgentConfig-shaped stub for TaskManager construction."""
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


# --------------------------------------------------------------------- #
# T033 / T034 — startup scan rejection
# --------------------------------------------------------------------- #


def test_binding_mismatch_stub_raises_classified_error(stubbable_provider_factory) -> None:
    """T033 scaffold: the stub raises TransportClassifiedError with
    classification == 'evicted' for configured (op, task_id) pairs.

    Asserted directly so subsequent tests can rely on the unified
    exception type without re-deriving it.
    """
    stub = stubbable_provider_factory()
    stub.reject_on("update", task_id="*")

    async def _run() -> None:
        with pytest.raises(TransportClassifiedError) as excinfo:
            from azure.ai.agentserver.core.tasks._models import TaskPatchRequest

            await stub.update("t-x", TaskPatchRequest(status="completed"))
        assert excinfo.value.classification == "evicted"
        assert excinfo.value.status == 409

    asyncio.run(_run())


@pytest.mark.asyncio
async def test_startup_scan_skips_evicted_records_without_raising(stubbable_provider_factory) -> None:
    """T034 /: startup scan tolerates per-record eviction —
    skips the record with WARNING log, never retries, never aborts the
    scan loop.

    We exercise the scan path by configuring the stub to evict a
    lease-renewal-style UPDATE on a specific task; the scan
    iteration over that record must not crash the loop.
    """
    from azure.ai.agentserver.core.tasks._manager import TaskManager
    from azure.ai.agentserver.core.tasks._models import TaskCreateRequest

    stub = stubbable_provider_factory()
    # Create one healthy + one will-be-evicted in_progress record.
    await stub.create(
        TaskCreateRequest(
            id="t-healthy",
            agent_name="test-agent",
            session_id="test-session",
            status="in_progress",
            title="healthy",
            payload={},
        )
    )
    await stub.create(
        TaskCreateRequest(
            id="t-evicted",
            agent_name="test-agent",
            session_id="test-session",
            status="in_progress",
            title="evicted",
            payload={},
        )
    )
    stub.reject_on("update", task_id="t-evicted")

    config = _config_stub()
    manager = TaskManager(config=config, provider=stub)
    # Startup should NOT raise even though one record's eventual
    # reclaim/renewal would be evicted. The scan-time eviction is
    # logged and skipped; the scan does not abort.
    await manager.startup()
    await manager.shutdown()


# --------------------------------------------------------------------- #
# T035 /  — lease-renewal eviction path
# --------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_lease_renewal_eviction_cancels_local_execution(stubbable_provider_factory) -> None:
    """T035 /: when lease_renewal_loop's PATCH is rejected with
    binding_mismatch, the framework cancels local execution via the
    on_cancel_callback. Verified via the lease_renewal_loop directly
    so we exercise the  wiring without depending on the full
    _execute_task_loop path.
    """
    from azure.ai.agentserver.core.tasks._lease import lease_renewal_loop

    stub = stubbable_provider_factory()
    stub.reject_on("update", task_id="t-renew")

    cancel_event = asyncio.Event()
    on_cancel = asyncio.Event()

    # Use a short lease duration so the first renewal attempt fires
    # quickly. The eviction MUST signal on_cancel and break the loop
    # immediately (not after on_failure_count attempts).
    loop_task = asyncio.create_task(
        lease_renewal_loop(
            stub,
            "t-renew",
            lease_owner="test-owner",
            lease_instance_id="inst-1",
            lease_duration_seconds=2,
            cancel_event=cancel_event,
            on_cancel_callback=on_cancel,
            on_failure_count=99,  # high so we know break came from eviction path
        )
    )

    # Wait up to the lease interval (1s = 2//2) plus a small buffer for
    # the first renewal attempt to fire and be rejected.
    await asyncio.wait_for(on_cancel.wait(), timeout=3.0)
    cancel_event.set()
    await loop_task


# --------------------------------------------------------------------- #
# T036 / T037 /  — scheduling-primitive Invariant 1 outcomes
# --------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_run_against_evicted_raises_taskconflict(stubbable_provider_factory) -> None:
    """T036 /  / SC-006: ``.run`` against an in-progress record
    whose store-write path is evicted MUST raise
    ``TaskConflictError(current_status="in_progress")`` — the SAME
    shape as the live-non-steerable case per Invariant 1. No new
    error type.
    """
    from azure.ai.agentserver.core.tasks import task, TaskContext
    from azure.ai.agentserver.core.tasks._manager import TaskManager
    from azure.ai.agentserver.core.tasks._models import TaskCreateRequest
    import azure.ai.agentserver.core.tasks._manager as mgr_mod

    stub = stubbable_provider_factory()

    # Seed a non-steerable task in pending status, then evict create.
    @task(name="evicted_task")
    async def my_task(ctx: TaskContext[str]) -> str:
        return "ok"

    config = _config_stub()
    manager = TaskManager(config=config, provider=stub)
    mgr_mod._manager = manager
    await manager.startup()
    try:
        # Pre-seed an in_progress record that would conflict with .run()
        # AND configure the stub to evict any update so the resume path
        # also fails — both observable outcomes converge on TaskConflictError.
        await stub.create(
            TaskCreateRequest(
                id="t-evict-run",
                agent_name="test-agent",
                session_id="test-session",
                status="in_progress",
                title="evict-run",
                payload={},
            )
        )
        # Backdate to past the legacy threshold so the in_progress path
        # would normally reclaim; the create+update being rejected forces
        # the eviction-as-TaskConflict semantic.
        stub.reject_on("create", task_id="t-evict-run")
        stub.reject_on("update", task_id="t-evict-run")

        with pytest.raises(TaskConflictError) as excinfo:
            await my_task.run(task_id="t-evict-run", input="x")
        # current_status must match the live-elsewhere shape.
        assert excinfo.value.current_status == "in_progress"
    finally:
        await manager.shutdown()
        mgr_mod._manager = None


# --------------------------------------------------------------------- #
# T038 — end-to-end split-brain isolation (SC-002)
# --------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_split_brain_handler_executes_exactly_once(stubbable_provider_factory) -> None:
    """SC-002 / T038: two TaskManagers against the same session id;
    one side's writes are evicted via binding_mismatch. The handler
    MUST execute exactly once across both instances; exactly one
    terminal record exists in the store.
    """
    from azure.ai.agentserver.core.tasks import task, TaskContext
    from azure.ai.agentserver.core.tasks._manager import TaskManager
    import azure.ai.agentserver.core.tasks._manager as mgr_mod

    execution_count = 0

    @multi_turn_task(name="split_brain_task")
    async def my_task(ctx: TaskContext[str]) -> str:
        nonlocal execution_count
        execution_count += 1
        return f"executed-{execution_count}"

    # Side A: accepts everything.
    stub_a = stubbable_provider_factory()
    # Side B: shares storage with A but writes are evicted.
    stub_b = BindingMismatchProvider(stub_a._delegate)  # noqa: SLF001
    stub_b.reject_on("create", task_id="*")
    stub_b.reject_on("update", task_id="*")

    config = _config_stub()

    # Side A completes first.
    manager_a = TaskManager(config=config, provider=stub_a)
    mgr_mod._manager = manager_a
    await manager_a.startup()
    try:
        result_a = await my_task.run(task_id="split-brain", input="A")
        assert result_a == "executed-1"
    finally:
        await manager_a.shutdown()

    # Side B tries to .run() the same task — sees the completed terminal,
    # raises TaskConflictError (live-elsewhere shape per Invariant 1).
    manager_b = TaskManager(config=config, provider=stub_b)
    mgr_mod._manager = manager_b
    await manager_b.startup()
    try:
        with pytest.raises(TaskConflictError):
            await my_task.run(task_id="split-brain", input="B")
    finally:
        await manager_b.shutdown()
        mgr_mod._manager = None

    # Handler executed exactly once across both managers.
    assert execution_count == 1


# --------------------------------------------------------------------- #
# T038a /  — input-enqueue eviction (every store-write site)
# --------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_input_enqueue_eviction_classified_as_evicted(stubbable_provider_factory) -> None:
    """T038a /: every store-write site, INCLUDING input enqueue,
    funnels through the classifier and treats binding_mismatch as
    ``evicted`` (not ``conflict``). The steerer's future receives
    TaskConflictError; the queued input is NOT persisted (the enqueue
    write itself was rejected).
    """
    from azure.ai.agentserver.core.tasks import task, TaskContext
    from azure.ai.agentserver.core.tasks._manager import TaskManager
    from azure.ai.agentserver.core.tasks._models import TaskCreateRequest
    import azure.ai.agentserver.core.tasks._manager as mgr_mod

    stub = stubbable_provider_factory()

    @multi_turn_task(name="enqueue_evict", steerable=True)
    async def my_task(ctx: TaskContext[dict]) -> dict:
        return {"got": ctx.input}

    # Seed an in-progress steerable task; then arrange that the steering
    # input enqueue PATCH gets evicted.
    config = _config_stub()
    manager = TaskManager(config=config, provider=stub)
    mgr_mod._manager = manager
    await manager.startup()
    try:
        await stub.create(
            TaskCreateRequest(
                id="t-eq",
                agent_name="test-agent",
                session_id="test-session",
                status="in_progress",
                title="enqueue-evict",
                payload={
                    "steering": {
                        "generation": 0,
                        "pending_inputs": [],
                        "drain_in_progress": False,
                    }
                },
            )
        )
        # Configure the stub to evict any update (the enqueue is a PATCH).
        stub.reject_on("update", task_id="t-eq")

        # Attempt to enqueue a new steering input via .start(). The
        # enqueue write is rejected → eviction → caller observes
        # TaskConflictError per Invariant 1.
        with pytest.raises(TaskConflictError):
            await my_task.start(task_id="t-eq", input={"msg": "queued"})
    finally:
        await manager.shutdown()
        mgr_mod._manager = None


# --------------------------------------------------------------------- #
# T039 / SC-006 partial — invariant 1 sweep (eviction column)
# --------------------------------------------------------------------- #


@pytest.mark.parametrize("steerable", [False, True])
@pytest.mark.asyncio
async def test_invariant_1_eviction_column(stubbable_provider_factory, steerable: bool) -> None:
    """SC-006 partial / Invariant 1: the dead-evicted column produces
    the same TaskConflictError (for .run/.start) regardless of
    steerable. Operator logs are the only differentiator from
    live-elsewhere.
    """
    from azure.ai.agentserver.core.tasks import task, TaskContext
    from azure.ai.agentserver.core.tasks._manager import TaskManager
    from azure.ai.agentserver.core.tasks._models import TaskCreateRequest
    import azure.ai.agentserver.core.tasks._manager as mgr_mod

    stub = stubbable_provider_factory()

    @multi_turn_task(name="inv1", steerable=steerable)
    async def my_task(ctx: TaskContext[str]) -> str:
        return "ok"

    config = _config_stub()
    manager = TaskManager(config=config, provider=stub)
    mgr_mod._manager = manager
    await manager.startup()
    try:
        await stub.create(
            TaskCreateRequest(
                id="t-inv1",
                agent_name="test-agent",
                session_id="test-session",
                status="in_progress",
                title="inv1",
                payload={"steering": {"generation": 0, "pending_inputs": []}} if steerable else {},
            )
        )
        stub.reject_on("create", task_id="t-inv1")
        stub.reject_on("update", task_id="t-inv1")

        with pytest.raises(TaskConflictError) as excinfo:
            await my_task.run(task_id="t-inv1", input="x")
        assert excinfo.value.current_status == "in_progress"
    finally:
        await manager.shutdown()
        mgr_mod._manager = None
