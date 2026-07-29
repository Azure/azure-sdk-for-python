# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
""" T-1.9 — active-run attachment for one-shot and multi-turn tasks."""

from __future__ import annotations

import asyncio
import importlib
import shutil
import uuid
from contextlib import suppress
from pathlib import Path
from typing import Any

import pytest

from azure.ai.agentserver.core.tasks import TaskContext, task


PACKAGE_ROOT = Path(__file__).resolve().parents[2]
STORE_ROOT = PACKAGE_ROOT / ".test-runs" / "resilient-active-run"


def _unique(prefix: str) -> str:
    return f"t022_active_{prefix}_{uuid.uuid4().hex}"


def _multi_turn_task(**kwargs: Any) -> Any:
    resilient = importlib.import_module("azure.ai.agentserver.core.tasks")
    decorator = getattr(resilient, "multi_turn_task", None)
    assert decorator is not None, " requires public multi_turn_task"
    return decorator(**kwargs)


def _output(result: Any) -> Any:
    return getattr(result, "output", result)


class _ManagerFixture:
    """Set up TaskManager with local storage under the repository, not /tmp."""

    @staticmethod
    async def setup() -> tuple[Any, Any, Path]:
        from azure.ai.agentserver.core.tasks._local_provider import LocalFileTaskProvider
        from azure.ai.agentserver.core.tasks._manager import TaskManager

        import azure.ai.agentserver.core.tasks._manager as mgr_mod

        store_dir = STORE_ROOT / uuid.uuid4().hex
        store_dir.mkdir(parents=True, exist_ok=False)
        provider = LocalFileTaskProvider(store_dir)
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
        manager = TaskManager(config=config, provider=provider, shutdown_grace_seconds=0.1)
        mgr_mod._manager = manager  # noqa: SLF001
        await manager.startup()
        return manager, mgr_mod, store_dir

    @staticmethod
    async def teardown(manager: Any, mgr_mod: Any, store_dir: Path) -> None:
        with suppress(BaseException):
            await manager.shutdown()
        mgr_mod._manager = None  # noqa: SLF001
        shutil.rmtree(store_dir, ignore_errors=True)


class TestOneShotGetActiveRun:
    """— task.get_active_run(task_id) — in-process / reclaimable inline only."""

    @pytest.mark.asyncio
    async def test_get_active_run_returns_None_for_nonexistent(self):
        @task(name=_unique("none"))
        async def my_task(ctx: TaskContext[str]) -> str:
            return f"ok:{ctx.input}"

        manager, mgr_mod, store_dir = await _ManagerFixture.setup()
        try:
            assert await my_task.get_active_run("never-started") is None
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)

    @pytest.mark.asyncio
    async def test_get_active_run_returns_handle_for_in_flight(self):
        entered = asyncio.Event()
        release = asyncio.Event()

        @task(name=_unique("inflight"))
        async def my_task(ctx: TaskContext[str]) -> str:
            entered.set()
            await release.wait()
            return f"done:{ctx.input}"

        manager, mgr_mod, store_dir = await _ManagerFixture.setup()
        try:
            task_id = _unique("one")
            original = await my_task.start(task_id=task_id, input="x")
            await asyncio.wait_for(entered.wait(), timeout=2.0)

            active = await my_task.get_active_run(task_id)
            assert active is not None
            assert active.task_id == task_id

            release.set()
            assert _output(await asyncio.wait_for(active.result(), timeout=2.0)) == "done:x"
            assert _output(await asyncio.wait_for(original.result(), timeout=2.0)) == "done:x"
        finally:
            release.set()
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)

    @pytest.mark.asyncio
    async def test_get_active_run_returns_None_after_terminal(self):
        @task(name=_unique("terminal"))
        async def my_task(ctx: TaskContext[str]) -> str:
            return f"done:{ctx.input}"

        manager, mgr_mod, store_dir = await _ManagerFixture.setup()
        try:
            task_id = _unique("one")
            run = await my_task.start(task_id=task_id, input="x")
            assert _output(await asyncio.wait_for(run.result(), timeout=2.0)) == "done:x"

            assert await my_task.get_active_run(task_id) is None
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)


class TestMultiTurnGetActiveRun:
    """— multi_turn_task.get_active_run(task_id, input_id) — exact match required."""

    @pytest.mark.asyncio
    async def test_get_active_run_signature_requires_both_args(self):
        @_multi_turn_task(name=_unique("signature"))
        async def chat(ctx: TaskContext[str]) -> str:
            return f"turn:{ctx.input}"

        with pytest.raises(TypeError):
            await chat.get_active_run("chat-1")

    @pytest.mark.asyncio
    async def test_get_active_run_exact_match_returns_handle(self):
        entered = asyncio.Event()
        release = asyncio.Event()

        @_multi_turn_task(name=_unique("exact"))
        async def chat(ctx: TaskContext[str]) -> str:
            entered.set()
            await release.wait()
            return f"turn:{ctx.input}"

        manager, mgr_mod, store_dir = await _ManagerFixture.setup()
        try:
            task_id = _unique("chat")
            run = await chat.start(task_id=task_id, input_id="i5", input="hello")
            await asyncio.wait_for(entered.wait(), timeout=2.0)

            active = await chat.get_active_run(task_id, "i5")
            assert active is not None
            assert active.task_id == task_id
            assert getattr(active, "input_id", None) == "i5"

            release.set()
            assert _output(await asyncio.wait_for(active.result(), timeout=2.0)) == "turn:hello"
            assert _output(await asyncio.wait_for(run.result(), timeout=2.0)) == "turn:hello"
        finally:
            release.set()
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)

    @pytest.mark.asyncio
    async def test_get_active_run_mismatched_input_id_returns_None(self):
        entered = asyncio.Event()
        release = asyncio.Event()

        @_multi_turn_task(name=_unique("mismatch"))
        async def chat(ctx: TaskContext[str]) -> str:
            entered.set()
            await release.wait()
            return f"turn:{ctx.input}"

        manager, mgr_mod, store_dir = await _ManagerFixture.setup()
        try:
            task_id = _unique("chat")
            run = await chat.start(task_id=task_id, input_id="i5", input="hello")
            await asyncio.wait_for(entered.wait(), timeout=2.0)

            assert await chat.get_active_run(task_id, "i6") is None

            release.set()
            assert _output(await asyncio.wait_for(run.result(), timeout=2.0)) == "turn:hello"
        finally:
            release.set()
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)

    @pytest.mark.asyncio
    async def test_get_active_run_returns_None_for_terminated_run(self):
        @_multi_turn_task(name=_unique("terminated"))
        async def chat(ctx: TaskContext[str]) -> str:
            return f"turn:{ctx.input}"

        manager, mgr_mod, store_dir = await _ManagerFixture.setup()
        try:
            task_id = _unique("chat")
            run = await chat.start(task_id=task_id, input_id="i5", input="hello")
            assert _output(await asyncio.wait_for(run.result(), timeout=2.0)) == "turn:hello"

            assert await chat.get_active_run(task_id, "i5") is None
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)


class TestSC002SequentialMetadataAccumulation:
    """SC-002 — multi-turn chat-style: N invocations accumulate per-turn metadata."""

    @pytest.mark.asyncio
    async def test_N_sequential_turns_metadata_accumulates(self):
        @_multi_turn_task(name=_unique("metadata"))
        async def chat(ctx: TaskContext[str]) -> str:
            history = list(ctx.metadata.get("history", []))
            output = f"O:{ctx.input}"
            history.append([ctx.input, output])
            ctx.metadata["history"] = history
            return output

        manager, mgr_mod, store_dir = await _ManagerFixture.setup()
        try:
            task_id = _unique("chat")
            first = await chat.start(task_id=task_id, input_id="i1", input="I1")
            assert _output(await asyncio.wait_for(first.result(), timeout=2.0)) == "O:I1"

            second = await chat.start(task_id=task_id, input_id="i2", input="I2")
            assert _output(await asyncio.wait_for(second.result(), timeout=2.0)) == "O:I2"

            assert second.metadata.get("history") == [["I1", "O:I1"], ["I2", "O:I2"]]
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod, store_dir)
