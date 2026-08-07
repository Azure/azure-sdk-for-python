# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Tests for  input clearing on suspend (T-024).

  scenarios 1, 2: when a steerable task transitions to suspended,
the framework clears the three input-bearing slots — ``payload["input"]``,
``_steering["active_input"]``, and ``_steering["previous_input"]`` — while
preserving ``_steering`` mechanism state and ``metadata``.
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
async def test_suspend_preserves_metadata(tmp_path: Path) -> None:
    """Metadata survives the suspend transition."""
    manager, mgr_mod = await _setup_manager(tmp_path)
    try:

        @multi_turn_task(name="meta", steerable=True)
        async def with_metadata(ctx: TaskContext[dict]) -> None:
            ctx.metadata["dev_key"] = "dev_value"
            await ctx.metadata.flush()
            return None

        await with_metadata.start(task_id="t-meta-survives", input={"msg": "hi"})
        info = None
        for _ in range(100):
            info = await manager.provider.get("t-meta-survives")
            if info is not None and info.status == "suspended":
                break
            await asyncio.sleep(0.05)
        assert info is not None
        assert info.status == "suspended"
        meta = info.payload.get("metadata", {})
        assert meta.get("dev_key") == "dev_value"
    finally:
        await _teardown_manager(manager, mgr_mod)
