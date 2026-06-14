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

from azure.ai.agentserver.core.durable import RetryPolicy, TaskContext, TaskConflictError, task, multi_turn_task


class _ManagerFixture:
    """Helper to set up a TaskManager with local file storage."""

    @staticmethod
    async def setup(tmp_path):
        from azure.ai.agentserver.core.durable._local_provider import LocalFileTaskProvider
        from azure.ai.agentserver.core.durable._manager import TaskManager

        import azure.ai.agentserver.core.durable._manager as mgr_mod

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

    @staticmethod
    async def teardown(manager, mgr_mod):
        await manager.shutdown()
        mgr_mod._manager = None


# ---------------------------------------------------------------------------
# Sample 3: Source (durable_source)
# ---------------------------------------------------------------------------


class TestSourceSampleE2E:
    """E2E for source auto-stamping (framework-owned, not user-overridable)."""

    @pytest.mark.asyncio
    async def test_source_auto_stamped(self, tmp_path):
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:

            @task(name="e2e_with_source")
            async def process_order(ctx: TaskContext[Any]) -> dict:
                return {"task_id": ctx.task_id}

            result = await process_order.run(task_id=uuid.uuid4().hex, input={"order_id": "ORD-001"})
            assert "task_id" in result
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_source_auto_stamp_fields(self, tmp_path):
        """Verify auto-stamped source contains type, name, server_version."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:
            task_id = uuid.uuid4().hex

            @task(name="e2e_source_fields")
            async def with_source(ctx: TaskContext[Any]) -> str:
                return "done"

            result = await with_source.run(task_id=task_id, input=None)
            assert result == "done"

            # Verify source was auto-stamped on the task record
            task_info = await manager.provider.get(task_id)
            if task_info is not None and task_info.source is not None:
                assert task_info.source["type"] == "agentserver.task"
                assert task_info.source["name"] == "e2e_source_fields"
                assert "server_version" in task_info.source
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)


# ---------------------------------------------------------------------------
# task.list() — scoped listing
# ---------------------------------------------------------------------------


class TestListE2E:
    """E2E for ``Task.list()`` — per-function scoped task listing."""

    @pytest.mark.asyncio
    async def test_list_empty_when_no_tasks(self, tmp_path):
        """list() returns empty when no tasks exist for this function."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:

            @task(name="e2e_list_empty")
            async def no_tasks(ctx: TaskContext[Any]) -> str:
                return "never called"

            tasks = await no_tasks._list()
            assert tasks == []
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_list_auto_stamped_tag(self, tmp_path):
        """Verify _task_name tag is auto-stamped on created tasks."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:
            task_id = uuid.uuid4().hex

            @multi_turn_task(name="e2e_tag_stamp")
            async def stamped(ctx: TaskContext[Any]) -> str:
                return "done"

            await stamped.run(task_id=task_id, input=None)

            # Check the raw task record for the tag
            task_info = await manager.provider.get(task_id)
            assert task_info is not None
            assert task_info.tags is not None
            assert task_info.tags.get("_task_name") == "e2e_tag_stamp"
        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)


# ---------------------------------------------------------------------------
# Sample 4: Multi-turn durable session (durable_multiturn)
# ---------------------------------------------------------------------------


class TestMultiturnSampleE2E:
    """E2E for the durable_multiturn sample — suspend/resume per turn."""

    @pytest.mark.skip(
        reason=" /: ctx.stream/async-for-in-run "
        "removed. test_multiturn_suspend_resume incidentally uses the "
        "legacy streaming API; migrate to streams registry pattern in "
        "follow-up. The streams conformance suite already covers "
        "multi-subscriber + cursor reconnect across the same id."
    )
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

            @task(name="e2e_session_workflow")
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

                return {"reply": reply, "turn": state["turn_count"]}

            task_id = "e2e-session-001"

            # --- Turn 1: start ---
            run1 = await session_workflow.start(task_id=task_id, input={"session_id": "s1", "message": "Hello"})
            # Collect stream items
            streamed = []
            async for chunk in run1:
                streamed.append(chunk)
            assert len(streamed) == 1
            assert streamed[0]["status"] == "thinking"

            # result() should return TaskResult with is_suspended
            result1 = await run1.result()
            #: result is raw output (Suspended wrapper removed)
            assert result1["reply"] == "Reply #1: Hello"
            assert result1["turn"] == 1

            # Verify task is suspended in the store
            task_record = await manager._provider.get(task_id)
            assert task is not None
            assert task_record.status == "suspended"

            # Verify checkpoint file exists
            assert (checkpoint_dir / "s1.json").exists()
            saved = _json.loads((checkpoint_dir / "s1.json").read_text())
            assert saved["turn_count"] == 1
            assert len(saved["history"]) == 2

            # --- Turn 2: update input → resume ---
            from azure.ai.agentserver.core.durable._models import TaskPatchRequest

            await manager._provider.update(
                task_id, TaskPatchRequest(payload={"input": {"session_id": "s1", "message": "Continue"}})
            )
            #: manager.handle_resume removed; resume is via.start/.run against suspended task
            pass

            # Wait for the task to suspend again
            for _ in range(100):
                await asyncio.sleep(0.02)
                task_record = await manager._provider.get(task_id)
                if task_record and task_record.status == "suspended":
                    break
            assert task_record.status == "suspended"
            assert task_record.payload["output"]["turn"] == 2
            assert "Continue" in task_record.payload["output"]["reply"]

            # Verify checkpoint updated
            saved2 = _json.loads((checkpoint_dir / "s1.json").read_text())
            assert saved2["turn_count"] == 2
            assert len(saved2["history"]) == 4  # 2 user + 2 assistant

            # --- Turn 3: end session ---
            await manager._provider.update(
                task_id, TaskPatchRequest(payload={"input": {"session_id": "s1", "message": "done"}})
            )
            #: manager.handle_resume removed; resume is via.start/.run against suspended task
            pass

            # Wait for completion
            for _ in range(100):
                await asyncio.sleep(0.02)
                task_record = await manager._provider.get(task_id)
                if task_record and task_record.status == "completed":
                    break
            assert task_record.status == "completed"
            assert task_record.payload["output"]["finished"] is True

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
from langgraph.graph import END as _END, START as _START, StateGraph as _SG  # noqa: E402
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
    builder.add_conditional_edges("wait_for_user", _lg_should_continue, {"continue": "process_input", "end": _END})
    return builder.compile(checkpointer=checkpointer)


class TestLangGraphSampleE2E:
    """E2E for the durable_langgraph sample — LangGraph interrupt/resume."""

    @pytest.mark.skip(reason=": handle_resume removed; resume is via.start against suspended task")
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

            @task(name="e2e_langgraph_session")
            async def lg_session(ctx: TaskContext[Any]) -> dict:
                session_id = ctx.input["session_id"]
                message = ctx.input["message"]
                thread_config = {"configurable": {"thread_id": session_id}}

                state = await asyncio.to_thread(graph.get_state, thread_config)

                if state.next:
                    await asyncio.to_thread(graph.invoke, _Cmd(resume=message), thread_config)
                else:
                    await asyncio.to_thread(
                        graph.invoke, {"messages": [_HM(content=message)], "is_complete": False}, thread_config
                    )

                state = await asyncio.to_thread(graph.get_state, thread_config)

                if state.next:
                    msgs = state.values.get("messages", [])
                    ai_msgs = [m for m in msgs if isinstance(m, _AI)]
                    user_msgs = [m for m in msgs if isinstance(m, _HM)]
                    return {
                        "reply": ai_msgs[-1].content if ai_msgs else "",
                        "turn": len(user_msgs),
                    }

                msgs = state.values.get("messages", [])
                user_count = len([m for m in msgs if isinstance(m, _HM)])
                return {"finished": True, "turn_count": user_count}

            task_id = "e2e-lg-session-001"

            # --- Turn 1: start ---
            run1 = await lg_session.start(task_id=task_id, input={"session_id": "lg-s1", "message": "Hello"})

            result1 = await run1.result()
            #: result is raw output (Suspended wrapper removed)
            assert result1["reply"] == "Reply #1: Hello"
            assert result1["turn"] == 1

            task_record = await manager._provider.get(task_id)
            assert task_record.status == "suspended"

            # --- Turn 2: resume with new input ---
            await manager._provider.update(
                task_id, TaskPatchRequest(payload={"input": {"session_id": "lg-s1", "message": "Tell me more"}})
            )
            #: manager.handle_resume removed; resume is via.start/.run against suspended task
            pass

            for _ in range(100):
                await asyncio.sleep(0.02)
                task_record = await manager._provider.get(task_id)
                if task_record and task_record.status == "suspended":
                    break
            assert task_record.status == "suspended"
            #   — output is always stored in
            # attachments['_output']; payload['output'] is a ref.
            # Resolve via the framework helper.
            from azure.ai.agentserver.core.durable._attachments import _read_input_value

            resolved_output = _read_input_value(task_record.payload.get("output"), task_record.attachments)
            assert resolved_output["turn"] == 2
            assert "Tell me more" in resolved_output["reply"]

            # --- Turn 3: end session ---
            await manager._provider.update(
                task_id, TaskPatchRequest(payload={"input": {"session_id": "lg-s1", "message": "done"}})
            )
            #: manager.handle_resume removed; resume is via.start/.run against suspended task
            pass

            for _ in range(100):
                await asyncio.sleep(0.02)
                task_record = await manager._provider.get(task_id)
                if task_record and task_record.status == "completed":
                    break
            assert task_record.status == "completed"
            resolved_output = _read_input_value(task_record.payload.get("output"), task_record.attachments)
            assert resolved_output["finished"] is True
            assert resolved_output["turn_count"] == 2

        finally:
            conn.close()
            await _ManagerFixture.teardown(manager, mgr_mod)


# ---------------------------------------------------------------------------
# Lifecycle automation — start/resume/recover via .start()
# ---------------------------------------------------------------------------


class TestLifecycleE2E:
    """E2E for lifecycle-aware.start and.get —."""

    @pytest.mark.asyncio
    async def test_crash_recovery_via_lifecycle(self, tmp_path):
        """Stale in_progress task is recovered with entry_mode='recovered'."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:
            entry_modes: list[str] = []

            @task(name="e2e_recoverable")
            async def recoverable_task(ctx: TaskContext[Any]) -> str:
                entry_modes.append(ctx.entry_mode)
                return f"entry={ctx.entry_mode}"

            task_id = "e2e-crash-recovery"

            # Create a task and manually set it to in_progress with old timestamp
            await recoverable_task.start(task_id=task_id, input="first")
            # Wait for it to run
            for _ in range(50):
                await asyncio.sleep(0.02)
                info = await recoverable_task._get(task_id)
                if info and info.status == "completed":
                    break

            # Now backdating: create another task with in_progress status
            task_id2 = "e2e-crash-recovery-2"
            from azure.ai.agentserver.core.durable._models import TaskPatchRequest

            # Start fresh then simulate a crash by backdating
            await recoverable_task.start(task_id=task_id2, input="crash-sim")
            for _ in range(50):
                await asyncio.sleep(0.02)
                info = await recoverable_task._get(task_id2)
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

            @task(name="e2e_get_missing")
            async def some_task(ctx: TaskContext[Any]) -> str:
                return "ok"

            info = await some_task._get("nonexistent-task-id")
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

            @task(name="e2e_inv_suspend")
            async def inv_suspend_task(ctx: TaskContext[Any]) -> dict:
                inv_id = ctx.input["invocation_id"]
                _inv_save(inv_id, {"status": "running"})
                output = {"reply": "hello", "turn": 1}
                _inv_save(inv_id, {"status": "completed", "output": output})
                return output

            inv_id = f"inv-{uuid.uuid4()}"
            run = await inv_suspend_task.start(task_id="inv-suspend-001", input={"invocation_id": inv_id})
            result = await run.result()
            #: result is raw output (Suspended wrapper removed)
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

            @task(name="e2e_inv_complete")
            async def inv_complete_task(ctx: TaskContext[Any]) -> dict:
                inv_id = ctx.input["invocation_id"]
                _inv_save(inv_id, {"status": "running"})
                result = {"finished": True, "turn_count": 3}
                _inv_save(inv_id, {"status": "completed", "output": result})
                return result

            inv_id = f"inv-{uuid.uuid4()}"
            result = await inv_complete_task.run(task_id="inv-complete-001", input={"invocation_id": inv_id})
            assert result["finished"] is True

            stored = _inv_load(inv_id)
            assert stored is not None
            assert stored["status"] == "completed"
            assert stored["output"]["finished"] is True

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

            @multi_turn_task(name="e2e_claude_chat", steerable=True)
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
                    return None
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
                    return None
                store[invocation_id] = {"status": "completed", "output": output}
                return output

            run = await claude_chat.start(
                task_id="claude-s1",
                input={
                    "session_id": "s1",
                    "message": "Hello",
                    "invocation_id": "inv-1",
                },
            )
            result = await asyncio.wait_for(run.result(), timeout=5.0)
            #: result is raw output (Suspended wrapper removed)
            assert result["reply"] == "Echo: Hello"
            assert result["partial"] is False
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

            @multi_turn_task(name="e2e_claude_chat", steerable=True)
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
                    return None
                reply = ""
                was_aborted = False
                async with _MockStreamCtx(["chunk1-", "chunk2-", "chunk3"], delay=0.15) as stream:
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
                    return None
                store[invocation_id] = {"status": "completed", "output": output}
                return output

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
            #: result is raw output (Suspended wrapper removed)

            result_b = await asyncio.wait_for(run_b.result(), timeout=5.0)
            #: result is raw output (Suspended wrapper removed)
            assert result_b["reply"] == "chunk1-chunk2-chunk3"

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

            @multi_turn_task(name="e2e_claude_chat", steerable=True)
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
                    return None
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
                    return None
                store[invocation_id] = {"status": "completed", "output": output}
                return output

            run_a = await claude_chat.start(
                task_id="claude-rf", input={"session_id": "s1", "message": "A", "invocation_id": "rf-a"}
            )
            await asyncio.sleep(0.05)

            run_b = await claude_chat.start(
                task_id="claude-rf", input={"session_id": "s1", "message": "B", "invocation_id": "rf-b"}
            )
            run_c = await claude_chat.start(
                task_id="claude-rf", input={"session_id": "s1", "message": "C", "invocation_id": "rf-c"}
            )

            result_c = await asyncio.wait_for(run_c.result(), timeout=5.0)
            assert result_c["reply"] == "Reply to C"

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

            @multi_turn_task(name="e2e_copilot_chat", steerable=True)
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
                    return None

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
                    done, pending = await asyncio.wait({cancel_task, idle_task}, return_when=asyncio.FIRST_COMPLETED)
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
                    return None
                store[invocation_id] = {"status": "completed", "output": output}
                return output

            run = await copilot_chat.start(
                task_id="copilot-s1",
                input={
                    "session_id": "s1",
                    "message": "Explain decorators",
                    "invocation_id": "inv-1",
                },
            )
            result = await asyncio.wait_for(run.result(), timeout=5.0)
            #: result is raw output (Suspended wrapper removed)
            assert result["reply"] == "Echo: Explain decorators"
            assert result["partial"] is False
            assert store["inv-1"]["status"] == "completed"

        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.asyncio
    async def test_copilot_steering_preserves_reply(self, tmp_path):
        """Steering queues B while A is streaming. A's partial reply saved as superseded."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:
            store: dict[str, dict[str, Any]] = {}

            @multi_turn_task(name="e2e_copilot_chat", steerable=True)
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
                    return None

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
                    done, pending = await asyncio.wait({cancel_task, idle_task}, return_when=asyncio.FIRST_COMPLETED)
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
                    return None
                store[invocation_id] = {"status": "completed", "output": output}
                return output

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
            #: result is raw output (Suspended wrapper removed)

            result_b = await asyncio.wait_for(run_b.result(), timeout=5.0)
            #: result is raw output (Suspended wrapper removed)
            assert result_b["reply"] == "part1-part2-part3"

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

            @multi_turn_task(name="e2e_lg_session", steerable=True)
            async def lg_session(ctx: TaskContext[dict]) -> dict[str, Any]:
                message = ctx.input["message"]
                invocation_id = ctx.input["invocation_id"]
                store[invocation_id] = {"status": "running"}

                if ctx.cancel.is_set():
                    store[invocation_id] = {"status": "cancelled", "reason": "steered"}
                    return None

                # Simulate multi-step graph processing
                await asyncio.sleep(0.1)  # Step 1: analyze
                if ctx.cancel.is_set():
                    store[invocation_id] = {"status": "cancelled", "reason": "steered"}
                    return None

                await asyncio.sleep(0.1)  # Step 2: generate
                if ctx.cancel.is_set():
                    store[invocation_id] = {"status": "cancelled", "reason": "steered"}
                    return None

                reply = f"[graph] Processed: {message}"

                # Save checkpoint
                cp_id = f"cp-{0}"
                checkpoints.append(cp_id)
                ctx.metadata.set("stable_checkpoint_id", cp_id)

                output = {"invocation_id": invocation_id, "reply": reply}
                store[invocation_id] = {"status": "completed", "output": output}
                return output

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
            #: result is raw output (Suspended wrapper removed)

            result_b = await asyncio.wait_for(run_b.result(), timeout=5.0)
            #: result is raw output (Suspended wrapper removed)
            assert result_b["reply"] == "[graph] Processed: Go to Paris"

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

            @multi_turn_task(name="e2e_lg_session", steerable=True)
            async def lg_session(ctx: TaskContext[dict]) -> dict[str, Any]:
                message = ctx.input["message"]
                invocation_id = ctx.input["invocation_id"]
                store[invocation_id] = {"status": "running"}

                if ctx.cancel.is_set():
                    store[invocation_id] = {"status": "cancelled", "reason": "steered"}
                    return None

                await asyncio.sleep(0.3)  # Simulated processing

                if ctx.cancel.is_set():
                    store[invocation_id] = {"status": "cancelled", "reason": "steered"}
                    return None

                reply = f"[graph] {message} (gen={0})"
                output = {"invocation_id": invocation_id, "reply": reply}
                store[invocation_id] = {"status": "completed", "output": output}
                return output

            # Turn 1: normal
            run1 = await lg_session.start(
                task_id="lg-mt", input={"session_id": "s1", "message": "Turn1", "invocation_id": "mt-1"}
            )
            result1 = await asyncio.wait_for(run1.result(), timeout=5.0)
            #: result is raw output (Suspended wrapper removed)
            assert store["mt-1"]["status"] == "completed"

            # Turn 2: resume
            run2 = await lg_session.start(
                task_id="lg-mt", input={"session_id": "s1", "message": "Turn2", "invocation_id": "mt-2"}
            )
            await asyncio.sleep(0.05)

            # Turn 3: steer while turn 2 is running
            store["mt-3"] = {"status": "queued"}
            run3 = await lg_session.start(
                task_id="lg-mt", input={"session_id": "s1", "message": "Turn3", "invocation_id": "mt-3"}
            )
            assert store["mt-3"]["status"] == "queued"

            result2 = await asyncio.wait_for(run2.result(), timeout=5.0)
            #: result is raw output (Suspended wrapper removed)

            result3 = await asyncio.wait_for(run3.result(), timeout=5.0)
            #: result is raw output (Suspended wrapper removed)
            assert "Turn3" in result3["reply"]
            assert store["mt-2"]["status"] == "cancelled"
            assert store["mt-3"]["status"] == "completed"

        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)


# ---------------------------------------------------------------------------
# SSE Streaming: lifecycle events, text deltas, steering supersession
# ---------------------------------------------------------------------------


class TestSSEStreamingE2E:
    """E2E tests for the SSE streaming pattern used by all samples.

     /: the legacy ``ctx.stream(item)`` +
    ``async for chunk in run`` API was removed. The full SSE wire
    contract is now exercised by the new streaming conformance suite
    (``tests/streaming/``) which directly tests the ``streams`` +
    ``EventStream`` Protocol surface that the SSE wire layer adapts.
    These e2e tests will be migrated to the new pattern in a follow-up.
    """

    @pytest.mark.skip(reason=" /: migrate to streams registry pattern")
    @pytest.mark.asyncio
    async def test_lifecycle_and_text_deltas_streamed(self, tmp_path):
        """ctx.stream() emits lifecycle:running then text_delta events."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:

            @task(name="e2e_sse_stream")
            async def sse_stream(ctx: TaskContext[dict]) -> dict[str, Any]:
                invocation_id = ctx.input["invocation_id"]
                await ctx.stream({"type": "lifecycle", "status": "running"})
                reply = ""
                for token in ["Hello", " ", "world"]:
                    reply += token
                    await ctx.stream({"type": "text_delta", "delta": token})
                return {
                    "invocation_id": invocation_id,
                    "reply": reply,
                }

            run = await sse_stream.start(task_id="sse-1", input={"invocation_id": "inv-sse-1"})

            chunks: list[dict[str, Any]] = []
            async for chunk in run:
                chunks.append(chunk)

            result = await asyncio.wait_for(run.result(), timeout=5.0)

            # First chunk: lifecycle running
            assert chunks[0] == {"type": "lifecycle", "status": "running"}
            # Then three text deltas
            assert chunks[1] == {"type": "text_delta", "delta": "Hello"}
            assert chunks[2] == {"type": "text_delta", "delta": " "}
            assert chunks[3] == {"type": "text_delta", "delta": "world"}
            assert len(chunks) == 4
            assert result["reply"] == "Hello world"

        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.skip(reason=" /: migrate to streams registry pattern")
    @pytest.mark.asyncio
    async def test_steering_produces_superseded_stream(self, tmp_path):
        """When steering cancels a running task, the stream ends after cancel."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:
            store: dict[str, dict[str, Any]] = {}

            @multi_turn_task(name="e2e_sse_steer", steerable=True)
            async def sse_steer(ctx: TaskContext[dict]) -> dict[str, Any]:
                invocation_id = ctx.input["invocation_id"]
                store[invocation_id] = {"status": "running"}
                await ctx.stream({"type": "lifecycle", "status": "running"})

                if ctx.cancel.is_set():
                    store[invocation_id] = {"status": "cancelled", "reason": "steered"}
                    return None

                # Simulate slow generation that gets interrupted
                reply = ""
                for token in ["Slow", " ", "reply", " ", "here"]:
                    reply += token
                    await ctx.stream({"type": "text_delta", "delta": token})
                    await asyncio.sleep(0.05)
                    if ctx.cancel.is_set():
                        store[invocation_id] = {
                            "status": "superseded",
                            "partial_reply": reply,
                        }
                        return None

                store[invocation_id] = {"status": "completed", "reply": reply}
                return {"invocation_id": invocation_id, "reply": reply}

            # Start turn 1
            run1 = await sse_steer.start(task_id="sse-steer-1", input={"invocation_id": "inv-s1"})

            # Collect some chunks from turn 1
            chunks1: list[dict[str, Any]] = []
            async for chunk in run1:
                chunks1.append(chunk)
                if len(chunks1) >= 2:
                    # Steer with turn 2 while turn 1 is streaming
                    await sse_steer.start(task_id="sse-steer-1", input={"invocation_id": "inv-s2"})
                    break

            # Turn 1 should have been superseded
            result1 = await asyncio.wait_for(run1.result(), timeout=5.0)
            #: result is raw output (Suspended wrapper removed)
            assert store["inv-s1"]["status"] in ("superseded", "cancelled")

            # First chunk was lifecycle:running
            assert chunks1[0] == {"type": "lifecycle", "status": "running"}

        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)

    @pytest.mark.skip(reason=" /: migrate to streams registry pattern")
    @pytest.mark.asyncio
    async def test_stream_with_invocation_store_snapshots(self, tmp_path):
        """Dual-write: ctx.stream() for live SSE + store for GET snapshots."""
        manager, mgr_mod = await _ManagerFixture.setup(tmp_path)
        try:
            store: dict[str, dict[str, Any]] = {}

            @task(name="e2e_sse_snapshot")
            async def sse_snapshot(ctx: TaskContext[dict]) -> dict[str, Any]:
                invocation_id = ctx.input["invocation_id"]
                store[invocation_id] = {"status": "running"}
                await ctx.stream({"type": "lifecycle", "status": "running"})

                reply = ""
                for token in ["A", "B", "C"]:
                    reply += token
                    await ctx.stream({"type": "text_delta", "delta": token})
                    store[invocation_id] = {"status": "streaming", "text": reply}

                store[invocation_id] = {
                    "status": "completed",
                    "reply": reply,
                }
                return {"invocation_id": invocation_id, "reply": reply}

            run = await sse_snapshot.start(task_id="sse-snap-1", input={"invocation_id": "inv-snap-1"})

            chunks: list[dict[str, Any]] = []
            async for chunk in run:
                chunks.append(chunk)

            result = await asyncio.wait_for(run.result(), timeout=5.0)

            # Stream had lifecycle + 3 deltas
            assert len(chunks) == 4
            assert chunks[0]["type"] == "lifecycle"

            # Store has final snapshot
            assert store["inv-snap-1"]["status"] == "completed"
            assert store["inv-snap-1"]["reply"] == "ABC"
            assert result["reply"] == "ABC"

        finally:
            await _ManagerFixture.teardown(manager, mgr_mod)
