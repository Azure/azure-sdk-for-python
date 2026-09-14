# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Tests for  supporting behaviour and regression guards.

Covers   scenarios 3 (drain doesn't consult input), 4-5 (etag-protected
suspended-resume), 6-7 (recovery preserves input), 8 (completed not affected),
and 11 (dead generation_results writes removed).
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

import pytest


from azure.ai.agentserver.core.tasks import TaskContext, task, multi_turn_task


# Module-level task definitions to allow `get_type_hints` to resolve
# TaskContext (which lives in the module namespace).


@task(name="us4-completing-ephemeral")
async def _completing_ephemeral(ctx: TaskContext[dict]) -> dict:
    return {"result": "done"}


@multi_turn_task(name="us4-completing-retain", steerable=False)
async def _completing_retain(ctx: TaskContext[dict]) -> dict:
    return {"result": "done"}


async def _setup_manager(tmp_path: Path):
    from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
    from azure.ai.agentserver.core.tasks._manager import TaskManager
    import azure.ai.agentserver.core.tasks._manager as mgr_mod

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


# ============================================================================
# T-025: drain doesn't consult payload["input"] (spec scenario 3)
# ============================================================================


def test_drain_does_not_read_payload_input() -> None:
    """Source-level assertion that ``_try_drain_steering`` doesn't read payload['input'].

    The drain primitive operates only on ``_steering`` sub-keys. Cleared input
    on suspend (from T-082) does not break drain on subsequent resumes.
    """
    import inspect

    from azure.ai.agentserver.core.tasks._manager import TaskManager

    src = inspect.getsource(TaskManager._try_drain_steering)
    # Drain reads `payload.get("steering", ...)` but never indexes
    # `payload["input"]` or `payload.get("input", ...)`.
    assert 'payload["input"]' not in src
    assert 'payload.get("input"' not in src


# ============================================================================
# T-026: recovery preserves input (spec scenarios 6, 7)
# ============================================================================
# (test_handle_suspend_only_fires_on_suspend_not_recovery removed: the
# legacy ``_handle_suspend`` scaffolding has been deleted from
# ``_manager.py``. The end-of-turn suspend transition is now handled by
# ``_handle_multi_turn_success`` / ``_handle_multi_turn_failure``, which
# only run on the multi-turn return-X / raise paths; recovery enters
# ``_execute_task`` with ``entry_mode == "recovered"`` and never touches
# the suspend handler.)


# ============================================================================
# T-027: etag-protected suspended-resume (spec scenarios 4, 5)
# ============================================================================


def test_suspended_resume_uses_etag_retry_loop() -> None:
    """The suspended-resume input patch is now etag-protected (T-083).

     note: the body of `_lifecycle_start` was extracted to
    `_lifecycle_start_inner`; source assertions follow.
    """
    import inspect

    from azure.ai.agentserver.core.tasks._decorator import Task

    src = inspect.getsource(Task._lifecycle_start_inner)
    # Etag retry loop at the suspended-resume site.
    assert "if_match=etag" in src
    # And the standard retry behaviour. The retry catches the local
    # provider's ValueError AND the hosted store's
    # TransportClassifiedError(classification="conflict") — both are
    # the same logical etag conflict.
    assert "ValueError" in src
    assert "TransportClassifiedError" in src
    #   framing.
    assert " " in src


# ============================================================================
# T-028: completed tasks not affected (spec scenario 8)
# ============================================================================


@pytest.mark.asyncio
async def test_completed_with_ephemeral_true_deletes_task(tmp_path: Path) -> None:
    """ephemeral=True: whole task is deleted on completion (existing behaviour).

    Regression guard —  must not have changed completion handling.
    """
    manager, mgr_mod = await _setup_manager(tmp_path)
    try:
        await _completing_ephemeral.start(task_id="t-complete-true", input={"msg": "hello"})
        info = "sentinel"  # type: ignore[assignment]
        for _ in range(50):
            info = await manager.provider.get("t-complete-true")
            if info is None:
                break
            await asyncio.sleep(0.05)
        # ephemeral=True: task removed from store.
        assert info is None
    finally:
        await _teardown_manager(manager, mgr_mod)


# ============================================================================
# T-029: generation_results no longer written (spec scenario 11)
# ============================================================================


def test_generation_results_write_removed() -> None:
    """The dead `_steering['generation_results']` write at _manager.py:1349-1352 is gone.

    Code-level regression guard: the assignment statement to generation_results
    must not be present (comments referencing the removal historically are fine).
    """
    import inspect
    import re

    from azure.ai.agentserver.core.tasks._manager import TaskManager

    src = inspect.getsource(TaskManager._try_drain_steering)
    # Find non-comment lines that ASSIGN to generation_results.
    non_comment_lines = [line for line in src.splitlines() if not line.lstrip().startswith("#")]
    body = "\n".join(non_comment_lines)
    # The write block — must not be present.
    assert 'steering["generation_results"] =' not in body
    assert "gen_results[" not in body


@pytest.mark.skipif(
    not hasattr(os, "fork"),
    reason="shells out to the POSIX `grep` binary, which is absent on Windows",
)
def test_no_source_reference_to_generation_results() -> None:
    """Repo-grep regression guard: no source file outside build/ has an actual
    assignment or read of ``_steering["generation_results"]`` (comments and
    docstrings are allowed for historical context).

      acceptance scenario 11.
    """
    import re
    import subprocess

    result = subprocess.run(
        [
            "grep",
            "-rn",
            "generation_results",
            "--include=*.py",
            "sdk/agentserver/azure-ai-agentserver-core/azure",
            "sdk/agentserver/azure-ai-agentserver-responses/azure",
        ],
        cwd=Path(__file__).parent.parent.parent.parent.parent.parent,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.stdout.strip():
        # An "actual use" line has an assignment (=), subscript brackets adjacent
        # to "generation_results", or a function call. Lines whose *content*
        # (after the file:line: prefix) starts with a comment character are
        # documentation only.
        actual_use_lines = []
        for line in result.stdout.splitlines():
            if "/build/" in line:
                continue
            # Split file:line:content prefix.
            parts = line.split(":", 2)
            if len(parts) < 3:
                continue
            content = parts[2].lstrip()
            if content.startswith(("#", '"""', "'''", "*")):
                continue
            # Skip embedded references inside docstring continuations.
            if "``" in content and "steering" in content and "removed" in content.lower():
                continue
            actual_use_lines.append(line)
        assert not actual_use_lines, (
            f"Expected no non-doc references to generation_results, " f"got: {chr(10).join(actual_use_lines)}"
        )
