# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""  — concurrent-race precondition test (T-033).

Two concurrent `start()` calls with the same `if_last_input_id` race on the
input-precondition primitive. Exactly one wins; the other re-checks against
the now-advanced `last_input_id` on its etag-retry and raises
`LastInputIdPreconditionFailed`.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from azure.ai.agentserver.core.tasks import LastInputIdPreconditionFailed, TaskContext, task, multi_turn_task


@multi_turn_task(name="us2-race-steerable", steerable=True)
async def _race_steerable(ctx: TaskContext[dict]) -> dict:
    return None


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


@pytest.mark.asyncio
async def test_concurrent_resume_with_same_predecessor_one_wins(tmp_path: Path) -> None:
    """Two concurrent resumes with the same predecessor: one wins, one loses."""
    manager, mgr_mod = await _setup_manager(tmp_path)
    try:
        # Establish a chain at last_input_id="msg-1" by suspending after turn 1.
        await _race_steerable.start(task_id="t-race", input={"turn": 1}, input_id="msg-1")
        await asyncio.sleep(0.2)

        # Race: two concurrent resume calls each claiming if_last_input_id="msg-1"
        # with different new ids. Exactly one must succeed.
        async def _attempt(new_id: str) -> str:
            try:
                await _race_steerable.start(
                    task_id="t-race", input={"turn": new_id}, input_id=new_id, if_last_input_id="msg-1"
                )
                return "ok"
            except LastInputIdPreconditionFailed:
                return "rejected"

        results = await asyncio.gather(_attempt("msg-2a"), _attempt("msg-2b"))

        # One should succeed, the other rejected.
        oks = [r for r in results if r == "ok"]
        rejecteds = [r for r in results if r == "rejected"]
        assert len(oks) == 1, f"Expected one winner: {results}"
        assert len(rejecteds) == 1, f"Expected one rejection: {results}"

        # Whichever id won is now persisted.
        info = await manager.provider.get("t-race")
        assert info is not None
        winner = info.payload["last_input_id"]
        assert winner in ("msg-2a", "msg-2b")
    finally:
        await _teardown_manager(manager, mgr_mod)
