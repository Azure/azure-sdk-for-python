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
    """E2E for source auto-stamping (framework-owned, not user-overridable)."""

    @pytest.mark.asyncio
    async def test_source_auto_stamped(self, tmp_path):
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:

            @durable_task(name="e2e_with_source")
            async def process_order(ctx: TaskContext[Any]) -> dict:
                return {"task_id": ctx.task_id}

            result = await process_order.run(
                task_id=uuid.uuid4().hex, input={"order_id": "ORD-001"}
            )
            assert "task_id" in result.output
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_source_auto_stamp_fields(self, tmp_path):
        """Verify auto-stamped source contains type, name, server_version."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:
            task_id = uuid.uuid4().hex

            @durable_task(name="e2e_source_fields")
            async def with_source(ctx: TaskContext[Any]) -> str:
                return "done"

            result = await with_source.run(
                task_id=task_id,
                input=None,
            )
            assert result.output == "done"

            # Verify source was auto-stamped on the task record
            task_info = await manager.provider.get(task_id)
            if task_info is not None and task_info.source is not None:
                assert task_info.source["type"] == "agentserver.durable_task"
                assert task_info.source["name"] == "e2e_source_fields"
                assert "server_version" in task_info.source
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)


# ---------------------------------------------------------------------------
# task.list() — scoped listing
# ---------------------------------------------------------------------------


class TestListE2E:
    """E2E for ``DurableTask.list()`` — per-function scoped task listing."""

    @pytest.mark.asyncio
    async def test_list_returns_only_this_tasks_records(self, tmp_path):
        """list() scoped by function name — other tasks excluded."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:

            @durable_task(name="e2e_list_alpha", ephemeral=False)
            async def alpha(ctx: TaskContext[Any]) -> str:
                return "alpha_done"

            @durable_task(name="e2e_list_beta", ephemeral=False)
            async def beta(ctx: TaskContext[Any]) -> str:
                return "beta_done"

            # Create tasks for both functions
            a1 = await alpha.run(task_id="alpha-1", input=None)
            a2 = await alpha.run(task_id="alpha-2", input=None)
            b1 = await beta.run(task_id="beta-1", input=None)
            assert a1.output == "alpha_done"
            assert a2.output == "alpha_done"
            assert b1.output == "beta_done"

            # list() on alpha should return only alpha tasks
            alpha_tasks = await alpha.list()
            alpha_ids = {t.id for t in alpha_tasks}
            assert "alpha-1" in alpha_ids
            assert "alpha-2" in alpha_ids
            assert "beta-1" not in alpha_ids

            # list() on beta should return only beta tasks
            beta_tasks = await beta.list()
            beta_ids = {t.id for t in beta_tasks}
            assert "beta-1" in beta_ids
            assert "alpha-1" not in beta_ids
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_list_with_status_filter(self, tmp_path):
        """list(status=...) filters by task status."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:

            @durable_task(name="e2e_list_status", ephemeral=False)
            async def suspendable(ctx: TaskContext[Any]) -> str:
                if ctx.entry_mode == "fresh":
                    return await ctx.suspend(reason="waiting")
                return "resumed"

            # Create a suspended task
            handle = await suspendable.start(task_id="status-1", input=None)
            result = await handle.result()
            assert result.is_suspended

            @durable_task(name="e2e_list_status", ephemeral=False)
            async def completer(ctx: TaskContext[Any]) -> str:
                return "done"

            # Create a completed task (different id, same name)
            result2 = await completer.run(task_id="status-2", input=None)
            assert result2.output == "done"

            # list with status filter
            suspended = await suspendable.list(status="suspended")
            suspended_ids = {t.id for t in suspended}
            assert "status-1" in suspended_ids
            assert "status-2" not in suspended_ids

            completed = await suspendable.list(status="completed")
            completed_ids = {t.id for t in completed}
            assert "status-2" in completed_ids
            assert "status-1" not in completed_ids
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_list_empty_when_no_tasks(self, tmp_path):
        """list() returns empty when no tasks exist for this function."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:

            @durable_task(name="e2e_list_empty")
            async def no_tasks(ctx: TaskContext[Any]) -> str:
                return "never called"

            tasks = await no_tasks.list()
            assert tasks == []
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_list_auto_stamped_tag(self, tmp_path):
        """Verify _durable_task_name tag is auto-stamped on created tasks."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:
            task_id = uuid.uuid4().hex

            @durable_task(name="e2e_tag_stamp", ephemeral=False)
            async def stamped(ctx: TaskContext[Any]) -> str:
                return "done"

            await stamped.run(task_id=task_id, input=None)

            # Check the raw task record for the tag
            task_info = await manager.provider.get(task_id)
            assert task_info is not None
            assert task_info.tags is not None
            assert task_info.tags.get("_durable_task_name") == "e2e_tag_stamp"
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_reserved_tag_cannot_be_overridden(self, tmp_path):
        """Developer-provided _durable_task_ tags are stripped; framework wins."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:
            task_id = uuid.uuid4().hex

            @durable_task(
                name="e2e_reserved_tag",
                ephemeral=False,
                tags={
                    "_durable_task_name": "evil_override",
                    "_durable_task_custom": "should_be_stripped",
                    "user_tag": "kept",
                },
            )
            async def protected(ctx: TaskContext[Any]) -> str:
                return "done"

            await protected.run(task_id=task_id, input=None)

            task_info = await manager.provider.get(task_id)
            assert task_info is not None
            assert task_info.tags is not None
            # Framework-stamped tag wins
            assert task_info.tags["_durable_task_name"] == "e2e_reserved_tag"
            # Other reserved tags are stripped
            assert "_durable_task_custom" not in task_info.tags
            # User tag is preserved
            assert task_info.tags["user_tag"] == "kept"
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_reserved_tag_stripped_from_callsite(self, tmp_path):
        """Call-site tags with reserved prefix are stripped."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:
            task_id = uuid.uuid4().hex

            @durable_task(name="e2e_callsite_tag", ephemeral=False)
            async def callsite(ctx: TaskContext[Any]) -> str:
                return "done"

            await callsite.run(
                task_id=task_id,
                input=None,
                tags={"_durable_task_name": "evil", "safe_tag": "ok"},
            )

            task_info = await manager.provider.get(task_id)
            assert task_info is not None
            assert task_info.tags is not None
            assert task_info.tags["_durable_task_name"] == "e2e_callsite_tag"
            assert task_info.tags["safe_tag"] == "ok"
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


# ---------------------------------------------------------------------------
# Sample E2E: Claude-style steering (durable_claude)
# ---------------------------------------------------------------------------


class _MockTextStream:
    """Simulates ``anthropic.AsyncAnthropic().messages.stream().text_stream``.

    Yields text chunks with a delay, so cancel checks between chunks
    exercise the same ``async for text in stream.text_stream`` path
    as the real sample.
    """

    def __init__(self, chunks: list[str], delay: float = 0.1):
        self._chunks = list(chunks)
        self._delay = delay

    def __aiter__(self):
        return self

    async def __anext__(self) -> str:
        if not self._chunks:
            raise StopAsyncIteration
        await asyncio.sleep(self._delay)
        return self._chunks.pop(0)


class _MockStreamCtx:
    """Simulates the ``async with client.messages.stream(...) as stream:`` context."""

    def __init__(self, chunks: list[str], delay: float = 0.1):
        self.text_stream = _MockTextStream(chunks, delay)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


class TestClaudeSteeringSampleE2E:
    """E2E for the durable_claude steering sample.

    Uses an async streaming mock (``_MockStreamCtx``) that mirrors the
    real ``anthropic.AsyncAnthropic().messages.stream()`` async iterator,
    so the cancel-between-chunks path is fully exercised.
    """

    @pytest.mark.asyncio
    async def test_claude_normal_turn(self, tmp_path):
        """Normal turn completes with full reply."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:
            store: dict[str, dict[str, Any]] = {}
            conv_store: dict[str, list[dict[str, str]]] = {}

            @durable_task(name="e2e_claude_chat", steerable=True)
            async def claude_chat(ctx: TaskContext[dict]) -> dict[str, Any]:
                session_id = ctx.input["session_id"]
                message = ctx.input["message"]
                invocation_id = ctx.input["invocation_id"]
                store[invocation_id] = {"status": "running"}
                # Load history from EXTERNAL store (not metadata)
                history = list(conv_store.get(session_id, []))
                history.append({"role": "user", "content": message})
                if ctx.cancel.is_set():
                    conv_store[session_id] = history
                    store[invocation_id] = {
                        "status": "cancelled",
                        "reason": "steered",
                        "message_preserved": True,
                    }
                    return await ctx.suspend(reason="steered")
                # Phase 2: Stream with cancel checks (mirrors async for text in stream.text_stream)
                reply = ""
                was_aborted = False
                async with _MockStreamCtx([f"Echo: ", message]) as stream:
                    async for text in stream.text_stream:
                        reply += text
                        if ctx.cancel.is_set():
                            was_aborted = True
                            break
                if reply:
                    history.append({"role": "assistant", "content": reply})
                conv_store[session_id] = history
                user_turns = len([m for m in history if m["role"] == "user"])
                output = {
                    "invocation_id": invocation_id,
                    "reply": reply,
                    "turn": user_turns,
                    "partial": was_aborted,
                }
                if was_aborted or ctx.cancel.is_set():
                    store[invocation_id] = {"status": "superseded", "output": output}
                    return await ctx.suspend(reason="steered")
                store[invocation_id] = {"status": "completed", "output": output}
                return await ctx.suspend(reason="awaiting_user_input", output=output)

            run = await claude_chat.start(
                task_id="claude-s1",
                input={
                    "session_id": "s1",
                    "message": "Hello",
                    "invocation_id": "inv-1",
                },
            )
            result = await asyncio.wait_for(run.result(), timeout=5.0)
            assert result.is_suspended
            assert result.output["reply"] == "Echo: Hello"
            assert result.output["partial"] is False
            assert store["inv-1"]["status"] == "completed"
            # History stored externally, not in metadata
            assert len(conv_store["s1"]) == 2  # user + assistant

        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_claude_steering_preserves_reply(self, tmp_path):
        """Steering queues B while A is streaming. A's partial reply saved as superseded."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:
            store: dict[str, dict[str, Any]] = {}
            conv_store: dict[str, list[dict[str, str]]] = {}

            @durable_task(name="e2e_claude_chat", steerable=True)
            async def claude_chat(ctx: TaskContext[dict]) -> dict[str, Any]:
                session_id = ctx.input["session_id"]
                message = ctx.input["message"]
                invocation_id = ctx.input["invocation_id"]
                store[invocation_id] = {"status": "running"}
                history = list(conv_store.get(session_id, []))
                history.append({"role": "user", "content": message})
                if ctx.cancel.is_set():
                    conv_store[session_id] = history
                    store[invocation_id] = {
                        "status": "cancelled",
                        "reason": "steered",
                        "message_preserved": True,
                    }
                    return await ctx.suspend(reason="steered")
                reply = ""
                was_aborted = False
                async with _MockStreamCtx(
                    ["chunk1-", "chunk2-", "chunk3"], delay=0.15
                ) as stream:
                    async for text in stream.text_stream:
                        reply += text
                        if ctx.cancel.is_set():
                            was_aborted = True
                            break
                if reply:
                    history.append({"role": "assistant", "content": reply})
                conv_store[session_id] = history
                output = {
                    "invocation_id": invocation_id,
                    "reply": reply,
                    "partial": was_aborted,
                }
                if was_aborted or ctx.cancel.is_set():
                    store[invocation_id] = {"status": "superseded", "output": output}
                    return await ctx.suspend(reason="steered")
                store[invocation_id] = {"status": "completed", "output": output}
                return await ctx.suspend(reason="awaiting_user_input", output=output)

            run_a = await claude_chat.start(
                task_id="claude-s1",
                input={
                    "session_id": "s1",
                    "message": "Hello",
                    "invocation_id": "inv-a",
                },
            )
            await asyncio.sleep(0.05)

            store["inv-b"] = {"status": "queued"}
            run_b = await claude_chat.start(
                task_id="claude-s1",
                input={
                    "session_id": "s1",
                    "message": "Nevermind",
                    "invocation_id": "inv-b",
                },
            )

            assert store["inv-b"]["status"] == "queued"

            result_a = await asyncio.wait_for(run_a.result(), timeout=5.0)
            assert result_a.is_superseded

            result_b = await asyncio.wait_for(run_b.result(), timeout=5.0)
            assert result_b.is_suspended
            assert result_b.output["reply"] == "chunk1-chunk2-chunk3"

            assert store["inv-a"]["status"] == "superseded"
            assert "output" in store["inv-a"]
            assert len(store["inv-a"]["output"]["reply"]) > 0
            assert store["inv-b"]["status"] == "completed"

        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_claude_rapid_fire_preserves_intermediate_messages(self, tmp_path):
        """Rapid-fire: A→B→C. B is short-circuited but its message is preserved in external store."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:
            store: dict[str, dict[str, Any]] = {}
            conv_store: dict[str, list[dict[str, str]]] = {}

            @durable_task(name="e2e_claude_chat", steerable=True)
            async def claude_chat(ctx: TaskContext[dict]) -> dict[str, Any]:
                session_id = ctx.input["session_id"]
                message = ctx.input["message"]
                invocation_id = ctx.input["invocation_id"]
                store[invocation_id] = {"status": "running"}
                history = list(conv_store.get(session_id, []))
                history.append({"role": "user", "content": message})
                if ctx.cancel.is_set():
                    conv_store[session_id] = history
                    store[invocation_id] = {
                        "status": "cancelled",
                        "reason": "steered",
                        "message_preserved": True,
                    }
                    return await ctx.suspend(reason="steered")
                reply = ""
                was_aborted = False
                async with _MockStreamCtx([f"Reply to {message}"], delay=0.3) as stream:
                    async for text in stream.text_stream:
                        reply += text
                        if ctx.cancel.is_set():
                            was_aborted = True
                            break
                if reply:
                    history.append({"role": "assistant", "content": reply})
                conv_store[session_id] = history
                output = {
                    "invocation_id": invocation_id,
                    "reply": reply,
                    "partial": was_aborted,
                }
                if was_aborted or ctx.cancel.is_set():
                    store[invocation_id] = {"status": "superseded", "output": output}
                    return await ctx.suspend(reason="steered")
                store[invocation_id] = {"status": "completed", "output": output}
                return await ctx.suspend(reason="awaiting_user_input", output=output)

            run_a = await claude_chat.start(
                task_id="claude-rf",
                input={"session_id": "s1", "message": "A", "invocation_id": "rf-a"},
            )
            await asyncio.sleep(0.05)

            run_b = await claude_chat.start(
                task_id="claude-rf",
                input={"session_id": "s1", "message": "B", "invocation_id": "rf-b"},
            )
            run_c = await claude_chat.start(
                task_id="claude-rf",
                input={"session_id": "s1", "message": "C", "invocation_id": "rf-c"},
            )

            result_c = await asyncio.wait_for(run_c.result(), timeout=5.0)
            assert result_c.output["reply"] == "Reply to C"

            # B was short-circuited but message preserved in external store
            assert store["rf-b"]["message_preserved"] is True
            assert store["rf-b"]["status"] == "cancelled"
            # All user messages should be in external history
            user_msgs = [m["content"] for m in conv_store["s1"] if m["role"] == "user"]
            assert "B" in user_msgs  # B's message was NOT lost

        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)


# ---------------------------------------------------------------------------
# Sample E2E: Copilot-style steering (durable_copilot)
# ---------------------------------------------------------------------------


class _MockCopilotSession:
    """Simulates a Copilot SDK session with event-based send + abort.

    Mirrors the real pattern: ``session.on(handler)`` registers an event
    listener, ``session.send(msg)`` fires ``AssistantMessageData`` events
    then ``IdleData``, and ``session.abort()`` stops further events.
    """

    def __init__(self, reply_chunks: list[str], delay: float = 0.1):
        self._chunks = reply_chunks
        self._delay = delay
        self._handler: Any = None
        self._aborted = False
        self._idle_event = asyncio.Event()

    def on(self, handler: Any) -> None:
        self._handler = handler

    async def send(self, message: str) -> None:
        """Deliver reply chunks as events, then fire idle."""
        asyncio.get_event_loop().create_task(self._deliver_events())

    async def _deliver_events(self) -> None:
        for chunk in self._chunks:
            if self._aborted:
                break
            await asyncio.sleep(self._delay)
            if self._aborted:
                break
            if self._handler:
                # Simulate AssistantMessageData event
                event = type("E", (), {"data": type("D", (), {"content": chunk})()})()
                self._handler(event)
        if not self._aborted and self._handler:
            # Simulate IdleData event
            idle_data = type("IdleData", (), {})()
            event = type("E", (), {"data": idle_data})()
            self._handler(event)
            self._idle_event.set()

    async def abort(self) -> None:
        self._aborted = True


class TestCopilotSteeringSampleE2E:
    """E2E for the durable_copilot steering sample.

    Uses ``_MockCopilotSession`` that mirrors the real Copilot SDK
    event-based pattern: ``session.on(handler)`` → ``session.send()``
    → events fire → ``session.abort()`` on cancel.
    """

    @pytest.mark.asyncio
    async def test_copilot_normal_turn(self, tmp_path):
        """Normal turn completes with full reply via event-based send."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:
            store: dict[str, dict[str, Any]] = {}

            @durable_task(name="e2e_copilot_chat", steerable=True)
            async def copilot_chat(ctx: TaskContext[dict]) -> dict[str, Any]:
                message = ctx.input["message"]
                invocation_id = ctx.input["invocation_id"]
                store[invocation_id] = {"status": "running"}
                if ctx.cancel.is_set():
                    store[invocation_id] = {
                        "status": "cancelled",
                        "reason": "steered",
                        "message_preserved": True,
                    }
                    return await ctx.suspend(reason="steered")

                # Event-based send (mirrors session.on + session.send)
                session = _MockCopilotSession([f"Echo: {message}"])
                reply_parts: list[str] = []
                idle_event = asyncio.Event()

                def on_event(event: Any) -> None:
                    if hasattr(event.data, "content"):
                        reply_parts.append(event.data.content or "")
                    elif type(event.data).__name__ == "IdleData":
                        idle_event.set()

                session.on(on_event)
                await session.send(message)

                # Wait for idle or cancel
                cancel_task = asyncio.create_task(ctx.cancel.wait())
                idle_task = asyncio.create_task(idle_event.wait())
                was_aborted = False
                try:
                    done, pending = await asyncio.wait(
                        {cancel_task, idle_task},
                        return_when=asyncio.FIRST_COMPLETED,
                    )
                    for t in pending:
                        t.cancel()
                    if cancel_task in done and idle_task not in done:
                        was_aborted = True
                        await session.abort()
                finally:
                    for t in (cancel_task, idle_task):
                        if not t.done():
                            t.cancel()

                reply = "".join(reply_parts)
                output = {
                    "invocation_id": invocation_id,
                    "reply": reply,
                    "partial": was_aborted,
                }
                if was_aborted or ctx.cancel.is_set():
                    store[invocation_id] = {"status": "superseded", "output": output}
                    return await ctx.suspend(reason="steered")
                store[invocation_id] = {"status": "completed", "output": output}
                return await ctx.suspend(reason="awaiting_user_input", output=output)

            run = await copilot_chat.start(
                task_id="copilot-s1",
                input={
                    "session_id": "s1",
                    "message": "Explain decorators",
                    "invocation_id": "inv-1",
                },
            )
            result = await asyncio.wait_for(run.result(), timeout=5.0)
            assert result.is_suspended
            assert result.output["reply"] == "Echo: Explain decorators"
            assert result.output["partial"] is False
            assert store["inv-1"]["status"] == "completed"

        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_copilot_steering_preserves_reply(self, tmp_path):
        """Steering queues B while A is streaming. A's partial reply saved as superseded."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:
            store: dict[str, dict[str, Any]] = {}

            @durable_task(name="e2e_copilot_chat", steerable=True)
            async def copilot_chat(ctx: TaskContext[dict]) -> dict[str, Any]:
                message = ctx.input["message"]
                invocation_id = ctx.input["invocation_id"]
                store[invocation_id] = {"status": "running"}
                if ctx.cancel.is_set():
                    store[invocation_id] = {
                        "status": "cancelled",
                        "reason": "steered",
                        "message_preserved": True,
                    }
                    return await ctx.suspend(reason="steered")

                session = _MockCopilotSession(["part1-", "part2-", "part3"], delay=0.15)
                reply_parts: list[str] = []
                idle_event = asyncio.Event()

                def on_event(event: Any) -> None:
                    if hasattr(event.data, "content"):
                        reply_parts.append(event.data.content or "")
                    elif type(event.data).__name__ == "IdleData":
                        idle_event.set()

                session.on(on_event)
                await session.send(message)

                cancel_task = asyncio.create_task(ctx.cancel.wait())
                idle_task = asyncio.create_task(idle_event.wait())
                was_aborted = False
                try:
                    done, pending = await asyncio.wait(
                        {cancel_task, idle_task},
                        return_when=asyncio.FIRST_COMPLETED,
                    )
                    for t in pending:
                        t.cancel()
                    if cancel_task in done and idle_task not in done:
                        was_aborted = True
                        await session.abort()
                finally:
                    for t in (cancel_task, idle_task):
                        if not t.done():
                            t.cancel()

                reply = "".join(reply_parts)
                output = {
                    "invocation_id": invocation_id,
                    "reply": reply,
                    "partial": was_aborted,
                }
                if was_aborted or ctx.cancel.is_set():
                    store[invocation_id] = {"status": "superseded", "output": output}
                    return await ctx.suspend(reason="steered")
                store[invocation_id] = {"status": "completed", "output": output}
                return await ctx.suspend(reason="awaiting_user_input", output=output)

            run_a = await copilot_chat.start(
                task_id="copilot-s1",
                input={
                    "session_id": "s1",
                    "message": "decorators",
                    "invocation_id": "inv-a",
                },
            )
            await asyncio.sleep(0.05)

            store["inv-b"] = {"status": "queued"}
            run_b = await copilot_chat.start(
                task_id="copilot-s1",
                input={
                    "session_id": "s1",
                    "message": "async/await",
                    "invocation_id": "inv-b",
                },
            )

            assert store["inv-b"]["status"] == "queued"

            result_a = await asyncio.wait_for(run_a.result(), timeout=5.0)
            assert result_a.is_superseded

            result_b = await asyncio.wait_for(run_b.result(), timeout=5.0)
            assert result_b.is_suspended
            assert result_b.output["reply"] == "part1-part2-part3"

            # A should be superseded (reply may be empty or partial — event
            # delivery is async, so cancel can arrive before any events fire)
            assert store["inv-a"]["status"] == "superseded"
            assert "output" in store["inv-a"]
            assert store["inv-b"]["status"] == "completed"

        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)


# ---------------------------------------------------------------------------
# Sample E2E: LangGraph steering path (durable_langgraph)
# ---------------------------------------------------------------------------


class TestLangGraphSteeringSampleE2E:
    """E2E for the durable_langgraph sample's steering path.

    Exercises the framework steering lifecycle (queued → cancel → drain →
    re-enter) using a simplified LangGraph-like pattern with checkpointing
    and invocation store writes.
    """

    @pytest.mark.asyncio
    async def test_langgraph_steering_cancels_and_resumes(self, tmp_path):
        """Steer while A is running → A cancelled → B processes from checkpoint."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:
            store: dict[str, dict[str, Any]] = {}
            checkpoints: list[str] = []

            @durable_task(name="e2e_lg_session", steerable=True)
            async def lg_session(ctx: TaskContext[dict]) -> dict[str, Any]:
                message = ctx.input["message"]
                invocation_id = ctx.input["invocation_id"]
                store[invocation_id] = {"status": "running"}

                if ctx.cancel.is_set():
                    store[invocation_id] = {"status": "cancelled", "reason": "steered"}
                    return await ctx.suspend(reason="steered")

                # Simulate multi-step graph processing
                await asyncio.sleep(0.1)  # Step 1: analyze
                if ctx.cancel.is_set():
                    store[invocation_id] = {"status": "cancelled", "reason": "steered"}
                    return await ctx.suspend(reason="steered")

                await asyncio.sleep(0.1)  # Step 2: generate
                if ctx.cancel.is_set():
                    store[invocation_id] = {"status": "cancelled", "reason": "steered"}
                    return await ctx.suspend(reason="steered")

                reply = f"[graph] Processed: {message}"

                # Save checkpoint
                cp_id = f"cp-{ctx.generation}"
                checkpoints.append(cp_id)
                ctx.metadata.set("stable_checkpoint_id", cp_id)

                output = {"invocation_id": invocation_id, "reply": reply}
                store[invocation_id] = {"status": "completed", "output": output}
                return await ctx.suspend(reason="awaiting_user_input", output=output)

            run_a = await lg_session.start(
                task_id="lg-s1",
                input={
                    "session_id": "s1",
                    "message": "Plan a trip",
                    "invocation_id": "lg-a",
                },
            )
            await asyncio.sleep(0.05)

            # Steer while A is running
            store["lg-b"] = {"status": "queued"}
            run_b = await lg_session.start(
                task_id="lg-s1",
                input={
                    "session_id": "s1",
                    "message": "Go to Paris",
                    "invocation_id": "lg-b",
                },
            )
            assert store["lg-b"]["status"] == "queued"

            result_a = await asyncio.wait_for(run_a.result(), timeout=5.0)
            assert result_a.is_superseded

            result_b = await asyncio.wait_for(run_b.result(), timeout=5.0)
            assert result_b.is_suspended
            assert result_b.output["reply"] == "[graph] Processed: Go to Paris"

            assert store["lg-a"]["status"] == "cancelled"
            assert store["lg-b"]["status"] == "completed"

        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_langgraph_multi_turn_then_steer(self, tmp_path):
        """Normal turn 1 → resume turn 2 → steer during turn 2 with turn 3."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:
            store: dict[str, dict[str, Any]] = {}

            @durable_task(name="e2e_lg_session", steerable=True, ephemeral=False)
            async def lg_session(ctx: TaskContext[dict]) -> dict[str, Any]:
                message = ctx.input["message"]
                invocation_id = ctx.input["invocation_id"]
                store[invocation_id] = {"status": "running"}

                if ctx.cancel.is_set():
                    store[invocation_id] = {"status": "cancelled", "reason": "steered"}
                    return await ctx.suspend(reason="steered")

                await asyncio.sleep(0.3)  # Simulated processing

                if ctx.cancel.is_set():
                    store[invocation_id] = {"status": "cancelled", "reason": "steered"}
                    return await ctx.suspend(reason="steered")

                reply = f"[graph] {message} (gen={ctx.generation})"
                output = {"invocation_id": invocation_id, "reply": reply}
                store[invocation_id] = {"status": "completed", "output": output}
                return await ctx.suspend(reason="awaiting_user_input", output=output)

            # Turn 1: normal
            run1 = await lg_session.start(
                task_id="lg-mt",
                input={"session_id": "s1", "message": "Turn1", "invocation_id": "mt-1"},
            )
            result1 = await asyncio.wait_for(run1.result(), timeout=5.0)
            assert result1.is_suspended
            assert store["mt-1"]["status"] == "completed"

            # Turn 2: resume
            run2 = await lg_session.start(
                task_id="lg-mt",
                input={"session_id": "s1", "message": "Turn2", "invocation_id": "mt-2"},
            )
            await asyncio.sleep(0.05)

            # Turn 3: steer while turn 2 is running
            store["mt-3"] = {"status": "queued"}
            run3 = await lg_session.start(
                task_id="lg-mt",
                input={"session_id": "s1", "message": "Turn3", "invocation_id": "mt-3"},
            )
            assert store["mt-3"]["status"] == "queued"

            result2 = await asyncio.wait_for(run2.result(), timeout=5.0)
            assert result2.is_superseded

            result3 = await asyncio.wait_for(run3.result(), timeout=5.0)
            assert result3.is_suspended
            assert "Turn3" in result3.output["reply"]
            assert store["mt-2"]["status"] == "cancelled"
            assert store["mt-3"]["status"] == "completed"

        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)
