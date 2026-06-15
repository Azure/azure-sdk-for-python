# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Spec 024 Phase 1 RED tests for bookkeeping unification.

These tests assert that the bookkeeping pattern primitives are gone from
the production code. Under spec 024 Phase 2 the framework's "register
the task, run the handler externally, signal completion" three-step
pattern is replaced by "handler runs inside the task body" (Model B in
SOT §6.4) for all rows.

EXPECTED: RED at the Phase 1 RED commit; GREEN after the Phase 2 impl
commit lands. See `sdk/agentserver/specs/024-responses-redesign.md`
Phase 1 step 5 and Phase 2 steps 9-13.
"""

from __future__ import annotations


def test_bookkeeping_events_registry_removed() -> None:
    """``_BOOKKEEPING_EVENTS`` module-level registry must be gone post-Phase-2.

    The dict was the per-process tracker for "the bookkeeping task is
    waiting for the external handler to signal completion". With the
    handler running inside the task body, the dict has no purpose.
    """
    from azure.ai.agentserver.responses.hosting import _durable_orchestrator

    assert not hasattr(_durable_orchestrator, "_BOOKKEEPING_EVENTS"), (
        "spec 024 Phase 2 deletes the _BOOKKEEPING_EVENTS registry. "
        "The bookkeeping pattern is gone — handlers run inside the task body."
    )


def test_run_bookkeeping_body_method_removed() -> None:
    """``DurableResponseOrchestrator._run_bookkeeping_body`` must be gone."""
    from azure.ai.agentserver.responses.hosting._durable_orchestrator import (
        DurableResponseOrchestrator,
    )

    assert not hasattr(DurableResponseOrchestrator, "_run_bookkeeping_body"), (
        "spec 024 Phase 2 deletes _run_bookkeeping_body. "
        "The fresh-entry branch for disposition=mark-failed runs the handler directly."
    )


def test_ensure_bookkeeping_event_method_removed() -> None:
    """``DurableResponseOrchestrator.ensure_bookkeeping_event`` must be gone."""
    from azure.ai.agentserver.responses.hosting._durable_orchestrator import (
        DurableResponseOrchestrator,
    )

    assert not hasattr(DurableResponseOrchestrator, "ensure_bookkeeping_event"), (
        "spec 024 Phase 2 deletes ensure_bookkeeping_event. "
        "No pre-registration step is needed when handler runs inside the task."
    )


def test_complete_bookkeeping_task_method_removed() -> None:
    """``DurableResponseOrchestrator.complete_bookkeeping_task`` must be gone."""
    from azure.ai.agentserver.responses.hosting._durable_orchestrator import (
        DurableResponseOrchestrator,
    )

    assert not hasattr(DurableResponseOrchestrator, "complete_bookkeeping_task"), (
        "spec 024 Phase 2 deletes complete_bookkeeping_task. "
        "No external completion signal is needed; task body finishes when handler returns."
    )


def test_orchestrator_complete_bookkeeping_task_method_removed() -> None:
    """``ResponseOrchestrator._complete_bookkeeping_task`` must be gone."""
    from azure.ai.agentserver.responses.hosting._orchestrator import ResponseOrchestrator

    assert not hasattr(ResponseOrchestrator, "_complete_bookkeeping_task"), (
        "spec 024 Phase 2 deletes ResponseOrchestrator._complete_bookkeeping_task. "
        "Callsites are removed because the bookkeeping signal pattern is gone."
    )


def test_run_background_no_shielded_runner_path() -> None:
    """``ResponseOrchestrator.run_background`` must not use ``asyncio.create_task(_shielded_runner)``.

    Under spec 024 Phase 2 all ``store=true`` background responses go
    through ``_start_durable_background`` which runs the handler inside
    the task body. The asyncio.create_task + shielded runner path is gone.
    """
    import inspect

    from azure.ai.agentserver.responses.hosting._orchestrator import ResponseOrchestrator

    src = inspect.getsource(ResponseOrchestrator.run_background)
    assert "_shielded_runner" not in src, (
        "spec 024 Phase 2 deletes the asyncio.create_task(_shielded_runner) "
        "branch in run_background. The handler runs inside the durable task body."
    )


def test_run_sync_awaits_task_run_result() -> None:
    """Row 3 foreground dispatch must use ``await TaskRun.result()``.

    Under spec 024 Phase 2 the HTTP request handler awaits the durable
    task's terminal via ``TaskRun.result()`` instead of running the
    handler synchronously in-line. Background semantics for blocking
    POST is preserved through the await.
    """
    import inspect

    from azure.ai.agentserver.responses.hosting import _orchestrator

    src = inspect.getsource(_orchestrator)
    # The post-unification path constructs a TaskRun and awaits .result()
    # at least once in the Row 3 dispatch path.
    assert "await task_run.result()" in src or "await run.result()" in src or ".result()" in src, (
        "spec 024 Phase 2 rewrites Row 3 dispatch to await TaskRun.result(). "
        "The source of _orchestrator.py should contain a `.result()` await on a TaskRun."
    )
