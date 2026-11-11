# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""  scenario 5: suspended-long-ago precondition contract.

A task is suspended with all input slots cleared (effect) but
`_last_input_id` persisted across the suspend. Resume with a
matching predecessor succeeds; resume with a stale predecessor fails.

This is the cross-phase composition test of  (input clearing) and
(precondition primitive).
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from azure.ai.agentserver.core.tasks import LastInputIdPreconditionFailed, TaskContext, task, multi_turn_task


@multi_turn_task(name="us2-suspend-long-ago", steerable=True)
async def _suspend_long_ago(ctx: TaskContext[dict]) -> dict:
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
async def test_suspended_long_ago_resume_with_correct_predecessor_succeeds(tmp_path: Path) -> None:
    """After a long-suspend, `_last_input_id` survives input clearing."""
    manager, mgr_mod = await _setup_manager(tmp_path)
    try:
        await _suspend_long_ago.start(task_id="t-suspend-long", input={"turn": 1}, input_id="msg-1")
        await asyncio.sleep(0.2)
        # Verify task is suspended and input slots are cleared,
        # but _last_input_id slot survives.
        info = await manager.provider.get("t-suspend-long")
        assert info is not None
        assert info.status == "suspended"
        assert info.payload.get("input") is None
        steering = info.payload.get("steering", {})
        assert steering.get("active_input") is None
        assert steering.get("previous_input") is None
        # _last_input_id slot persists.
        assert info.payload["last_input_id"] == "msg-1"

        # Resume with matching predecessor succeeds.
        await _suspend_long_ago.start(
            task_id="t-suspend-long", input={"turn": 2}, input_id="msg-2", if_last_input_id="msg-1"
        )
        await asyncio.sleep(0.2)
        info = await manager.provider.get("t-suspend-long")
        assert info is not None
        assert info.payload["last_input_id"] == "msg-2"
    finally:
        await _teardown_manager(manager, mgr_mod)


@pytest.mark.asyncio
async def test_suspended_long_ago_resume_with_stale_predecessor_fails(tmp_path: Path) -> None:
    """Stale `if_last_input_id` against a long-suspended task is rejected."""
    manager, mgr_mod = await _setup_manager(tmp_path)
    try:
        await _suspend_long_ago.start(task_id="t-suspend-long-stale", input={"turn": 1}, input_id="msg-1")
        await asyncio.sleep(0.2)

        with pytest.raises(LastInputIdPreconditionFailed) as excinfo:
            await _suspend_long_ago.start(
                task_id="t-suspend-long-stale", input={"turn": 2}, input_id="msg-2", if_last_input_id="msg-XYZ"
            )
        #: exception.task_id removed
        assert excinfo.value.actual_last_input_id == "msg-1"
        # Task remains suspended, slot unchanged.
        info = await manager.provider.get("t-suspend-long-stale")
        assert info is not None
        assert info.status == "suspended"
        assert info.payload["last_input_id"] == "msg-1"
    finally:
        await _teardown_manager(manager, mgr_mod)
