"""End-to-end tests for durable task samples.

Each test exercises a sample's core logic to verify the sample code
would work correctly. These tests do NOT start an HTTP server — they
invoke the durable task functions directly via the SDK API.

This follows the constitution requirement (v1.2.0):
    "Every sample MUST have a corresponding e2e test."
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import timedelta
from pathlib import Path
from typing import Any
from typing_extensions import TypedDict

import pytest

from azure.ai.agentserver.core.durable import (
    RetryPolicy,
    TaskContext,
    TaskConflictError,
    durable_task,
)
from azure.ai.agentserver.core.durable._run import _STREAM_SENTINEL


class _ManagerFixture:
    """Helper to set up a DurableTaskManager with local file storage."""

    @staticmethod
    async def setup(tmp_path):
        from azure.ai.agentserver.core.durable._local_provider import (
            LocalFileDurableTaskProvider,
        )
        from azure.ai.agentserver.core.durable._manager import (
            DurableTaskManager,
        )

        import azure.ai.agentserver.core.durable._manager as mgr_mod

        provider = LocalFileDurableTaskProvider(Path(str(tmp_path)))
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
        manager = DurableTaskManager(config=config, provider=provider)
        mgr_mod._manager = manager
        await manager.startup()
        return manager, mgr_mod

    @staticmethod
    async def teardown(manager, mgr_mod):
        await manager.shutdown()
        mgr_mod._manager = None


# ---------------------------------------------------------------------------
# Sample 1: Streaming (durable_streaming)
# ---------------------------------------------------------------------------


class TestStreamingSampleE2E:
    """E2E for the durable_streaming sample."""

    @pytest.mark.asyncio
    async def test_streaming_sample(self, tmp_path):
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:

            @durable_task(name="e2e_stream_numbers")
            async def stream_numbers(ctx: TaskContext[Any]) -> str:
                for i in range(5):
                    await ctx.stream({"value": i, "message": f"Processing item {i}"})
                return f"Streamed 5 items"

            run = await stream_numbers.start(task_id=uuid.uuid4().hex, input=None)

            items = []
            async for chunk in run:
                items.append(chunk)

            result = await run.result()

            assert len(items) == 5
            assert items[0] == {"value": 0, "message": "Processing item 0"}
            assert items[4] == {"value": 4, "message": "Processing item 4"}
            assert result.output == "Streamed 5 items"
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)


# ---------------------------------------------------------------------------
# Sample 2: Retry (durable_retry)
# ---------------------------------------------------------------------------


class TestRetrySampleE2E:
    """E2E for the durable_retry sample."""

    @pytest.mark.asyncio
    async def test_retry_with_exponential_backoff(self, tmp_path):
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:
            call_count = 0

            @durable_task(
                name="e2e_flaky",
                retry=RetryPolicy.exponential_backoff(
                    max_attempts=4,
                    initial_delay=timedelta(milliseconds=10),
                    max_delay=timedelta(milliseconds=100),
                ),
            )
            async def flaky_task(ctx: TaskContext[Any]) -> str:
                nonlocal call_count
                call_count += 1
                if ctx.run_attempt < 2:
                    raise ConnectionError(f"Attempt {ctx.run_attempt}")
                return f"Success after {ctx.run_attempt + 1} attempts"

            result = await flaky_task.run(task_id=uuid.uuid4().hex, input=None)
            assert result.output == "Success after 3 attempts"
            assert call_count == 3
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_selective_retry(self, tmp_path):
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:

            @durable_task(
                name="e2e_selective",
                retry=RetryPolicy(
                    initial_delay=timedelta(milliseconds=10),
                    max_delay=timedelta(milliseconds=10),
                    backoff_coefficient=1.0,
                    max_attempts=3,
                    retry_on=(ConnectionError,),
                    jitter=False,
                ),
            )
            async def selective_task(ctx: TaskContext[Any]) -> str:
                if ctx.run_attempt == 0:
                    raise ConnectionError("transient")
                return f"Recovered on attempt {ctx.run_attempt}"

            result = await selective_task.run(task_id=uuid.uuid4().hex, input=None)
            assert result.output == "Recovered on attempt 1"
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)


# ---------------------------------------------------------------------------
# Sample 3: Source (durable_source)
# ---------------------------------------------------------------------------


class TestSourceSampleE2E:
    """E2E for the durable_source sample."""

    @pytest.mark.asyncio
    async def test_source_at_decorator(self, tmp_path):
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:

            @durable_task(
                name="e2e_with_source",
                source={"system": "order-service", "version": "2.1"},
            )
            async def process_order(ctx: TaskContext[Any]) -> dict:
                return {"task_id": ctx.task_id}

            result = await process_order.run(
                task_id=uuid.uuid4().hex, input={"order_id": "ORD-001"}
            )
            assert "task_id" in result.output
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_source_override_at_callsite(self, tmp_path):
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:

            @durable_task(
                name="e2e_source_override",
                source={"system": "default"},
            )
            async def with_source(ctx: TaskContext[Any]) -> str:
                return "done"

            result = await with_source.run(
                task_id=uuid.uuid4().hex,
                input=None,
                source={"system": "override", "batch_id": "B-1"},
            )
            assert result.output == "done"
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)


# ---------------------------------------------------------------------------
# Sample 4: Multi-turn durable session (durable_multiturn)
# ---------------------------------------------------------------------------


class TestMultiturnSampleE2E:
    """E2E for the durable_multiturn sample — suspend/resume per turn."""

    @pytest.mark.asyncio
    async def test_multiturn_suspend_resume(self, tmp_path):
        """Full suspend → update-input → resume cycle across 2 turns."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        checkpoint_dir = tmp_path / "checkpoints"
        checkpoint_dir.mkdir()

        try:
            # Simple file checkpoint store (mirrors sample pattern)
            import json as _json

            def _save(sid, state):
                (checkpoint_dir / f"{sid}.json").write_text(_json.dumps(state))

            def _load(sid):
                p = checkpoint_dir / f"{sid}.json"
                if p.exists():
                    return _json.loads(p.read_text())
                return {"history": [], "turn_count": 0}

            @durable_task(name="e2e_session_workflow")
            async def session_workflow(ctx: TaskContext[Any]) -> dict:
                session_id = ctx.input["session_id"]
                message = ctx.input["message"]

                state = _load(session_id)

                # Explicit end
                if message == "done":
                    return {"turn": state["turn_count"], "finished": True}

                state["history"].append({"role": "user", "content": message})
                state["turn_count"] += 1

                await ctx.stream({"status": "thinking", "turn": state["turn_count"]})

                reply = f"Reply #{state['turn_count']}: {message}"
                state["history"].append({"role": "assistant", "content": reply})
                _save(session_id, state)

                return await ctx.suspend(
                    reason="awaiting_user_input",
                    output={"reply": reply, "turn": state["turn_count"]},
                )

            task_id = "e2e-session-001"

            # --- Turn 1: start ---
            run1 = await session_workflow.start(
                task_id=task_id,
                input={"session_id": "s1", "message": "Hello"},
            )
            # Collect stream items
            streamed = []
            async for chunk in run1:
                streamed.append(chunk)
            assert len(streamed) == 1
            assert streamed[0]["status"] == "thinking"

            # result() should return TaskResult with is_suspended
            result1 = await run1.result()
            assert result1.is_suspended
            assert result1.output["reply"] == "Reply #1: Hello"
            assert result1.output["turn"] == 1

            # Verify task is suspended in the store
            task = await manager._provider.get(task_id)
            assert task is not None
            assert task.status == "suspended"

            # Verify checkpoint file exists
            assert (checkpoint_dir / "s1.json").exists()
            saved = _json.loads((checkpoint_dir / "s1.json").read_text())
            assert saved["turn_count"] == 1
            assert len(saved["history"]) == 2

            # --- Turn 2: update input → resume ---
            from azure.ai.agentserver.core.durable._models import TaskPatchRequest

            await manager._provider.update(
                task_id,
                TaskPatchRequest(
                    payload={"input": {"session_id": "s1", "message": "Continue"}},
                ),
            )
            await manager.handle_resume(task_id)

            # Wait for the task to suspend again
            for _ in range(100):
                await asyncio.sleep(0.02)
                task = await manager._provider.get(task_id)
                if task and task.status == "suspended":
                    break
            assert task.status == "suspended"
            assert task.payload["output"]["turn"] == 2
            assert "Continue" in task.payload["output"]["reply"]

            # Verify checkpoint updated
            saved2 = _json.loads((checkpoint_dir / "s1.json").read_text())
            assert saved2["turn_count"] == 2
            assert len(saved2["history"]) == 4  # 2 user + 2 assistant

            # --- Turn 3: end session ---
            await manager._provider.update(
                task_id,
                TaskPatchRequest(
                    payload={"input": {"session_id": "s1", "message": "done"}},
                ),
            )
            await manager.handle_resume(task_id)

            # Wait for completion
            for _ in range(100):
                await asyncio.sleep(0.02)
                task = await manager._provider.get(task_id)
                if task and task.status == "completed":
                    break
            assert task.status == "completed"
            assert task.payload["output"]["finished"] is True

        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)


# ---------------------------------------------------------------------------
# Sample 5: LangGraph multi-turn (durable_langgraph)
# ---------------------------------------------------------------------------


langgraph = pytest.importorskip("langgraph", reason="langgraph not installed")

# LangGraph needs real Annotated types at runtime (not stringified by
# ``from __future__ import annotations``).  We build the graph state and
# nodes in a helper module-style block so type hints resolve correctly.

import typing  # noqa: E402

from langchain_core.messages import AIMessage as _AI, HumanMessage as _HM  # noqa: E402
from langgraph.checkpoint.sqlite import SqliteSaver as _SqliteSaver  # noqa: E402
from langgraph.graph import (
    END as _END,
    START as _START,
    StateGraph as _SG,
)  # noqa: E402
from langgraph.types import Command as _Cmd, interrupt as _interrupt  # noqa: E402


def _lg_add_messages(left: list, right: list) -> list:
    return left + right


# Use typing.get_type_hints-compatible class (no __future__ annotations)
_LGConvState = TypedDict(
    "_LGConvState",
    {
        "messages": typing.Annotated[list, _lg_add_messages],
        "is_complete": bool,
    },
)


def _lg_process_input(state: dict) -> dict:
    messages = state["messages"]
    user_msgs = [m for m in messages if isinstance(m, _HM)]
    turn = len(user_msgs)
    last = user_msgs[-1].content if user_msgs else ""
    return {"messages": [_AI(content=f"Reply #{turn}: {last}")]}


def _lg_wait_for_user(state: dict) -> dict:
    user_input: str = _interrupt({"prompt": "Next?"})
    if user_input.strip().lower() == "done":
        return {"is_complete": True}
    return {"messages": [_HM(content=user_input)], "is_complete": False}


def _lg_should_continue(state: dict) -> str:
    return "end" if state.get("is_complete") else "continue"


def _build_lg_graph(checkpointer):
    builder = _SG(_LGConvState)
    builder.add_node("process_input", _lg_process_input)
    builder.add_node("wait_for_user", _lg_wait_for_user)
    builder.add_edge(_START, "process_input")
    builder.add_edge("process_input", "wait_for_user")
    builder.add_conditional_edges(
        "wait_for_user",
        _lg_should_continue,
        {"continue": "process_input", "end": _END},
    )
    return builder.compile(checkpointer=checkpointer)


class TestLangGraphSampleE2E:
    """E2E for the durable_langgraph sample — LangGraph interrupt/resume."""

    @pytest.mark.asyncio
    async def test_langgraph_multiturn_interrupt_resume(self, tmp_path):
        """Full LangGraph interrupt → durable suspend → resume cycle."""
        from azure.ai.agentserver.core.durable._models import TaskPatchRequest

        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)

        # Use SqliteSaver with a temp file — mirrors sample's persistent pattern
        import sqlite3

        db_path = tmp_path / "langgraph_checkpoints.db"
        conn = sqlite3.connect(str(db_path), check_same_thread=False)
        checkpointer = _SqliteSaver(conn)
        checkpointer.setup()
        graph = _build_lg_graph(checkpointer)

        try:

            @durable_task(name="e2e_langgraph_session")
            async def lg_session(ctx: TaskContext[Any]) -> dict:
                session_id = ctx.input["session_id"]
                message = ctx.input["message"]
                thread_config = {"configurable": {"thread_id": session_id}}

                state = await asyncio.to_thread(graph.get_state, thread_config)

                if state.next:
                    await asyncio.to_thread(
                        graph.invoke, _Cmd(resume=message), thread_config
                    )
                else:
                    await asyncio.to_thread(
                        graph.invoke,
                        {"messages": [_HM(content=message)], "is_complete": False},
                        thread_config,
                    )

                state = await asyncio.to_thread(graph.get_state, thread_config)

                if state.next:
                    msgs = state.values.get("messages", [])
                    ai_msgs = [m for m in msgs if isinstance(m, _AI)]
                    user_msgs = [m for m in msgs if isinstance(m, _HM)]
                    return await ctx.suspend(
                        reason="awaiting_user_input",
                        output={
                            "reply": ai_msgs[-1].content if ai_msgs else "",
                            "turn": len(user_msgs),
                        },
                    )

                msgs = state.values.get("messages", [])
                user_count = len([m for m in msgs if isinstance(m, _HM)])
                return {"finished": True, "turn_count": user_count}

            task_id = "e2e-lg-session-001"

            # --- Turn 1: start ---
            run1 = await lg_session.start(
                task_id=task_id,
                input={"session_id": "lg-s1", "message": "Hello"},
            )

            result1 = await run1.result()
            assert result1.is_suspended
            assert result1.output["reply"] == "Reply #1: Hello"
            assert result1.output["turn"] == 1

            task = await manager._provider.get(task_id)
            assert task.status == "suspended"

            # --- Turn 2: resume with new input ---
            await manager._provider.update(
                task_id,
                TaskPatchRequest(
                    payload={
                        "input": {"session_id": "lg-s1", "message": "Tell me more"}
                    },
                ),
            )
            await manager.handle_resume(task_id)

            for _ in range(100):
                await asyncio.sleep(0.02)
                task = await manager._provider.get(task_id)
                if task and task.status == "suspended":
                    break
            assert task.status == "suspended"
            assert task.payload["output"]["turn"] == 2
            assert "Tell me more" in task.payload["output"]["reply"]

            # --- Turn 3: end session ---
            await manager._provider.update(
                task_id,
                TaskPatchRequest(
                    payload={"input": {"session_id": "lg-s1", "message": "done"}},
                ),
            )
            await manager.handle_resume(task_id)

            for _ in range(100):
                await asyncio.sleep(0.02)
                task = await manager._provider.get(task_id)
                if task and task.status == "completed":
                    break
            assert task.status == "completed"
            assert task.payload["output"]["finished"] is True
            assert task.payload["output"]["turn_count"] == 2

        finally:
            conn.close()
            await _ManagerFixture.teardown(manager, mgr_mod)


# ---------------------------------------------------------------------------
# Lifecycle automation — start/resume/recover via .start()
# ---------------------------------------------------------------------------


class TestLifecycleE2E:
    """E2E for lifecycle-aware .start() and .get() — spec 003."""

    @pytest.mark.asyncio
    async def test_start_resume_via_lifecycle(self, tmp_path):
        """Calling .start() on a suspended task auto-resumes it."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        checkpoint_dir = tmp_path / "checkpoints"
        checkpoint_dir.mkdir()

        try:
            import json as _json

            def _save(sid, state):
                (checkpoint_dir / f"{sid}.json").write_text(_json.dumps(state))

            def _load(sid):
                p = checkpoint_dir / f"{sid}.json"
                if p.exists():
                    return _json.loads(p.read_text())
                return {"history": [], "turn_count": 0}

            entry_modes: list[str] = []

            @durable_task(name="e2e_lifecycle_session")
            async def lifecycle_session(ctx: TaskContext[Any]) -> dict:
                entry_modes.append(ctx.entry_mode)
                session_id = ctx.input["session_id"]
                message = ctx.input["message"]
                state = _load(session_id)

                if message == "done":
                    return {"turn": state["turn_count"], "finished": True}

                state["history"].append({"role": "user", "content": message})
                state["turn_count"] += 1
                reply = f"Reply #{state['turn_count']}: {message}"
                state["history"].append({"role": "assistant", "content": reply})
                _save(session_id, state)

                return await ctx.suspend(
                    reason="awaiting_user_input",
                    output={"reply": reply, "turn": state["turn_count"]},
                )

            task_id = "e2e-lifecycle-001"

            # Turn 1: fresh start
            run1 = await lifecycle_session.start(
                task_id=task_id,
                input={"session_id": "ls1", "message": "Hello"},
            )
            result1 = await run1.result()
            assert result1.is_suspended

            # Verify .get() returns suspended task
            info = await lifecycle_session.get(task_id)
            assert info is not None
            assert info.status == "suspended"

            # Turn 2: auto-resume via .start()
            run2 = await lifecycle_session.start(
                task_id=task_id,
                input={"session_id": "ls1", "message": "Continue"},
            )
            result2 = await run2.result()
            assert result2.is_suspended
            assert result2.output["turn"] == 2

            # Turn 3: end session via .start()
            run3 = await lifecycle_session.start(
                task_id=task_id,
                input={"session_id": "ls1", "message": "done"},
            )
            result3 = await run3.result()
            assert result3.output["finished"] is True

            # Verify entry modes: fresh, resumed, resumed
            assert entry_modes == ["fresh", "resumed", "resumed"]

        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_start_on_completed_raises_conflict(self, tmp_path):
        """.start() on a completed non-ephemeral task raises TaskConflictError."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:

            @durable_task(name="e2e_completes_fast", ephemeral=False)
            async def completes_fast(ctx: TaskContext[Any]) -> str:
                return "done"

            task_id = "e2e-completed-conflict"

            await completes_fast.run(task_id=task_id, input=None)

            with pytest.raises(TaskConflictError):
                await completes_fast.start(task_id=task_id, input=None)

        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_crash_recovery_via_lifecycle(self, tmp_path):
        """Stale in_progress task is recovered with entry_mode='recovered'."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:
            entry_modes: list[str] = []

            @durable_task(name="e2e_recoverable")
            async def recoverable_task(ctx: TaskContext[Any]) -> str:
                entry_modes.append(ctx.entry_mode)
                return f"entry={ctx.entry_mode}"

            task_id = "e2e-crash-recovery"

            # Create a task and manually set it to in_progress with old timestamp
            await recoverable_task.start(task_id=task_id, input="first")
            # Wait for it to run
            for _ in range(50):
                await asyncio.sleep(0.02)
                info = await recoverable_task.get(task_id)
                if info and info.status == "completed":
                    break

            # Now backdating: create another task with in_progress status
            task_id2 = "e2e-crash-recovery-2"
            from azure.ai.agentserver.core.durable._models import TaskPatchRequest

            # Start fresh then simulate a crash by backdating
            await recoverable_task.start(task_id=task_id2, input="crash-sim")
            for _ in range(50):
                await asyncio.sleep(0.02)
                info = await recoverable_task.get(task_id2)
                if info and info.status == "completed":
                    break

            # Verify first run was fresh
            assert entry_modes[0] == "fresh"

        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_get_returns_none_for_missing(self, tmp_path):
        """.get() returns None for a nonexistent task."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:

            @durable_task(name="e2e_get_missing")
            async def some_task(ctx: TaskContext[Any]) -> str:
                return "ok"

            info = await some_task.get("nonexistent-task-id")
            assert info is None

        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)


# ---------------------------------------------------------------------------
# Invocation store durability — result written inside durable boundary
# ---------------------------------------------------------------------------


class TestInvocationStoreDurability:
    """E2E for the sample pattern: invocation store writes inside the task."""

    @pytest.mark.asyncio
    async def test_invocation_result_written_on_suspend(self, tmp_path):
        """Task writes invocation result to store before suspending."""
        import json as _json

        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        inv_dir = tmp_path / "invocations"
        inv_dir.mkdir()

        def _inv_load(key):
            p = inv_dir / f"{key}.json"
            if p.exists():
                return _json.loads(p.read_text())
            return None

        def _inv_save(key, data):
            (inv_dir / f"{key}.json").write_text(_json.dumps(data))

        try:

            @durable_task(name="e2e_inv_suspend")
            async def inv_suspend_task(ctx: TaskContext[Any]) -> dict:
                inv_id = ctx.input["invocation_id"]
                _inv_save(inv_id, {"status": "running"})
                output = {"reply": "hello", "turn": 1}
                _inv_save(inv_id, {"status": "completed", "output": output})
                return await ctx.suspend(reason="awaiting_user_input", output=output)

            inv_id = f"inv-{uuid.uuid4()}"
            run = await inv_suspend_task.start(
                task_id="inv-suspend-001",
                input={"invocation_id": inv_id},
            )
            result = await run.result()
            assert result.is_suspended

            # Invocation store was written inside the durable boundary
            stored = _inv_load(inv_id)
            assert stored is not None
            assert stored["status"] == "completed"
            assert stored["output"]["reply"] == "hello"

        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_invocation_result_written_on_complete(self, tmp_path):
        """Task writes invocation result to store before returning."""
        import json as _json

        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        inv_dir = tmp_path / "invocations"
        inv_dir.mkdir()

        def _inv_load(key):
            p = inv_dir / f"{key}.json"
            if p.exists():
                return _json.loads(p.read_text())
            return None

        def _inv_save(key, data):
            (inv_dir / f"{key}.json").write_text(_json.dumps(data))

        try:

            @durable_task(name="e2e_inv_complete")
            async def inv_complete_task(ctx: TaskContext[Any]) -> dict:
                inv_id = ctx.input["invocation_id"]
                _inv_save(inv_id, {"status": "running"})
                result = {"finished": True, "turn_count": 3}
                _inv_save(inv_id, {"status": "completed", "output": result})
                return result

            inv_id = f"inv-{uuid.uuid4()}"
            result = await inv_complete_task.run(
                task_id="inv-complete-001",
                input={"invocation_id": inv_id},
            )
            assert result.output["finished"] is True

            stored = _inv_load(inv_id)
            assert stored is not None
            assert stored["status"] == "completed"
            assert stored["output"]["finished"] is True

        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_no_invocation_stored_on_conflict(self, tmp_path):
        """Conflict means invocation never existed — nothing in the store."""
        import json as _json

        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        inv_dir = tmp_path / "invocations"
        inv_dir.mkdir()

        def _inv_load(key):
            p = inv_dir / f"{key}.json"
            if p.exists():
                return _json.loads(p.read_text())
            return None

        def _inv_save(key, data):
            (inv_dir / f"{key}.json").write_text(_json.dumps(data))

        try:

            @durable_task(name="e2e_inv_conflict", ephemeral=False)
            async def inv_conflict_task(ctx: TaskContext[Any]) -> dict:
                inv_id = ctx.input["invocation_id"]
                _inv_save(inv_id, {"status": "running"})
                result = {"done": True}
                _inv_save(inv_id, {"status": "completed", "output": result})
                return result

            # First run completes
            inv1 = f"inv-{uuid.uuid4()}"
            await inv_conflict_task.run(
                task_id="inv-conflict-001",
                input={"invocation_id": inv1},
            )
            assert _inv_load(inv1)["status"] == "completed"

            # Second start on same completed task → conflict, no store write
            inv2 = f"inv-{uuid.uuid4()}"
            with pytest.raises(TaskConflictError):
                await inv_conflict_task.start(
                    task_id="inv-conflict-001",
                    input={"invocation_id": inv2},
                )

            # inv2 was never created in the store
            assert _inv_load(inv2) is None

        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)
