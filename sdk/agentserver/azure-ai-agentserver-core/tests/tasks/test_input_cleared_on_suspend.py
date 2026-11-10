# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Tests for  input clearing on suspend (T-024).

  scenarios 1, 2: when a steerable task transitions to suspended,
the framework clears the three input-bearing slots — ``payload["input"]``,
``_steering["active_input"]``, and ``_steering["previous_input"]`` — while
preserving the remaining ``_steering`` mechanism state.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from azure.ai.agentserver.core.tasks import TaskContext, task, multi_turn_task


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
async def test_suspend_clears_payload_input(tmp_path: Path) -> None:
    """After suspend, ``payload['input']`` is cleared (None)."""
    manager, mgr_mod = await _setup_manager(tmp_path)
    try:

        @multi_turn_task(name="suspending", steerable=True)
        async def suspending(ctx: TaskContext[dict]) -> None:
            return None

        await suspending.start(task_id="t-input-cleared", input={"msg": "secret-user-content"})
        info = None
        for _ in range(100):
            info = await manager.provider.get("t-input-cleared")
            if info is not None and info.status == "suspended":
                break
            await asyncio.sleep(0.05)
        assert info is not None
        assert info.status == "suspended"
        assert info.payload.get("input") is None, (
            f"Expected payload['input'] to be cleared after suspend, got: " f"{info.payload.get('input')!r}"
        )
    finally:
        await _teardown_manager(manager, mgr_mod)


@pytest.mark.asyncio
@pytest.mark.parametrize("turn_outcome", ["return", "raise"])
async def test_turn_end_atomically_clears_stale_drain_state(tmp_path: Path, turn_outcome: str) -> None:
    """A failed Phase-3 clear cannot leave a phantom active drain."""
    from azure.ai.agentserver.core.tasks._models import TaskCreateRequest

    manager, mgr_mod = await _setup_manager(tmp_path)
    task_id = f"t-stale-drain-{turn_outcome}"
    try:
        await manager.provider.create(
            TaskCreateRequest(
                id=task_id,
                agent_name="test-agent",
                session_id="test-session",
                status="in_progress",
                title="stale drain",
                payload={
                    "input": {"msg": "B"},
                    "schema_version": "1",
                    "steering": {
                        "active_input": {"msg": "B"},
                        "active_ack_id": "ack-b",
                        "pending_inputs": [{"msg": "C"}],
                        "pending_ack_ids": ["ack-c"],
                        "cancel_requested": True,
                        "drain_in_progress": True,
                    },
                },
                lease_owner=manager._lease_owner,
                lease_instance_id=manager._instance_id,
                lease_duration_seconds=60,
            )
        )

        if turn_outcome == "return":
            await manager._handle_multi_turn_success(task_id=task_id, opts=None)
        else:
            await manager._handle_multi_turn_failure(
                task_id=task_id,
                exc=RuntimeError("planned failure"),
                opts=None,
                error_dict={"type": "RuntimeError", "message": "planned failure", "traceback": ""},
            )

        info = await manager.provider.get(task_id)
        assert info is not None
        assert info.status == "suspended"
        steering = info.payload["steering"]
        assert steering["active_input"] is None
        assert steering["active_ack_id"] is None
        assert steering["drain_in_progress"] is False
        assert steering["pending_inputs"] == [{"msg": "C"}]
        assert steering["pending_ack_ids"] == ["ack-c"]
    finally:
        await _teardown_manager(manager, mgr_mod)
