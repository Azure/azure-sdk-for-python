"""LangGraph conversation agent with durable task lifecycle and steering.

Wraps a LangGraph ``StateGraph`` in a steerable durable task.
Demonstrates the **checkpoint-and-fork** cancel pattern:

1. Pre-entry check  — short-circuit if cancel is pre-set
2. Inter-node check — ``_invoke_cancellable`` checks between graph nodes
3. Fork-on-steer    — roll back to the last stable checkpoint and fork
   with the new message

LangGraph owns the conversation flow; the durable task owns crash
resilience and steering orchestration.
"""

import asyncio
import logging
import sqlite3
import typing
from pathlib import Path
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph, add_messages
from langgraph.types import Command, interrupt
from typing_extensions import TypedDict

from azure.ai.agentserver.core.durable import TaskContext, durable_task

from .store import FileStore

logger = logging.getLogger(__name__)

_DATA_DIR = Path.home() / ".durable-sessions"

# Invocation result store — written inside the durable task so it survives crashes
invocation_store = FileStore(_DATA_DIR / "invocations")


# ---------------------------------------------------------------------------
# Graph state
# ---------------------------------------------------------------------------


class ConversationState(TypedDict):
    """Graph state for a multi-turn conversation.

    Uses LangGraph's built-in ``add_messages`` reducer for message
    accumulation across turns.
    """

    messages: typing.Annotated[list, add_messages]
    is_complete: bool


# ---------------------------------------------------------------------------
# Graph nodes
# ---------------------------------------------------------------------------

# Simulated step delay — distributed across nodes so inter-node
# cancellation (via ``graph.stream()``) can bail out quickly.
_STEP_DELAY = 2  # seconds per processing node


def analyze_input(state: ConversationState) -> dict[str, Any]:
    """Simulate analysing the user's message (e.g., intent detection)."""
    import time  # pylint: disable=import-outside-toplevel

    _ = state  # Would inspect messages in a real implementation
    time.sleep(_STEP_DELAY)
    return {}  # No state change — analysis is an internal step


def generate_response(state: ConversationState) -> dict[str, Any]:
    """Generate an AI response.  Replace stub with a real LLM call."""
    import time  # pylint: disable=import-outside-toplevel

    time.sleep(_STEP_DELAY)

    messages = state["messages"]
    user_messages = [m for m in messages if isinstance(m, HumanMessage)]
    turn = len(user_messages)
    last_msg = user_messages[-1].content if user_messages else ""

    if turn == 1:
        reply = (
            f"Thanks for reaching out! You said: '{last_msg}'. "
            "I'd love to help — could you share more details?"
        )
    elif turn == 2:
        reply = (
            f"Great context: '{last_msg}'. Building on our earlier "
            "exchange, here are some initial thoughts. What else "
            "would you like to explore?"
        )
    else:
        reply = (
            f"Turn {turn}: incorporating '{last_msg}' — I now have "
            f"context from {turn} turns. How shall we proceed?"
        )

    return {"messages": [AIMessage(content=reply)]}


def refine_response(state: ConversationState) -> dict[str, Any]:
    """Simulate post-processing (e.g., safety checks, formatting)."""
    import time  # pylint: disable=import-outside-toplevel

    _ = state  # Would inspect the generated reply in a real implementation
    time.sleep(_STEP_DELAY // 2 or 1)
    return {}  # No state change — refinement is an internal step


def wait_for_user(state: ConversationState) -> dict[str, Any]:
    """Pause the graph and wait for the next human message."""
    messages = state["messages"]
    user_count = len([m for m in messages if isinstance(m, HumanMessage)])

    user_input: str = interrupt(
        {
            "prompt": "Please provide your next message (or say 'done' to finish):",
            "current_turn": user_count,
        }
    )

    if user_input.strip().lower() == "done":
        return {"is_complete": True}

    return {
        "messages": [HumanMessage(content=user_input)],
        "is_complete": False,
    }


def _should_continue(state: ConversationState) -> str:
    """Route: loop back to process_input or end the conversation."""
    if state.get("is_complete", False):
        return "end"
    return "continue"


# ---------------------------------------------------------------------------
# Persistent graph checkpointer (survives restarts)
# ---------------------------------------------------------------------------

_DATA_DIR.mkdir(parents=True, exist_ok=True)
_DB_PATH = _DATA_DIR / "langgraph_checkpoints.db"

_conn = sqlite3.connect(str(_DB_PATH), check_same_thread=False)
_checkpointer = SqliteSaver(_conn)
_checkpointer.setup()

logger.info("LangGraph checkpoints stored at: %s", _DB_PATH)


# ---------------------------------------------------------------------------
# Build and compile the graph
# ---------------------------------------------------------------------------


def _build_graph() -> Any:
    """Construct the LangGraph StateGraph for multi-turn conversation.

    Processing is split across three nodes (``analyze_input`` →
    ``generate_response`` → ``refine_response``) so that stream-based
    cancellation can bail out between any two steps (~2 s granularity).
    """
    builder = StateGraph(ConversationState)

    builder.add_node("analyze_input", analyze_input)
    builder.add_node("generate_response", generate_response)
    builder.add_node("refine_response", refine_response)
    builder.add_node("wait_for_user", wait_for_user)

    builder.add_edge(START, "analyze_input")
    builder.add_edge("analyze_input", "generate_response")
    builder.add_edge("generate_response", "refine_response")
    builder.add_edge("refine_response", "wait_for_user")

    builder.add_conditional_edges(
        "wait_for_user",
        _should_continue,
        {
            "continue": "analyze_input",
            "end": END,
        },
    )

    return builder.compile(checkpointer=_checkpointer)


_graph = _build_graph()


# ---------------------------------------------------------------------------
# Steering — cancellable graph invocation and state forking
# ---------------------------------------------------------------------------


def _invoke_cancellable(
    graph: Any,
    graph_input: Any,
    config: dict[str, Any],
    cancel_event: asyncio.Event,
) -> bool:
    """Run the graph using ``stream()`` with inter-node cancellation.

    Instead of ``graph.invoke()`` which blocks until the full graph
    completes, this streams node-by-node and checks ``cancel_event``
    between nodes.  If cancellation is detected, execution stops before
    the next node runs.

    Returns ``True`` if the graph ran to completion (or interrupt),
    ``False`` if cancelled mid-graph.
    """
    for _chunk in graph.stream(graph_input, config):
        if cancel_event.is_set():
            return False
    return True


def _fork_from_checkpoint(
    graph: Any,
    config: dict[str, Any],
    target_checkpoint_id: str,
    new_message: str,
) -> bool:
    """Fork the graph from a previous checkpoint with a new message.

    Uses LangGraph's native state forking: ``update_state`` called with
    an old checkpoint's config creates a new branch.  The graph's head
    pointer moves to the fork, discarding any state that was added after
    the target checkpoint.

    After forking the graph is positioned after ``wait_for_user`` with
    the new message injected, so the next step is ``process_input``.

    Returns ``True`` if the fork was created.
    """
    # Load the target checkpoint to get its full config (includes checkpoint_ns)
    target_config = {
        "configurable": {
            **config["configurable"],
            "checkpoint_id": target_checkpoint_id,
        }
    }
    target = graph.get_state(target_config)
    if not target or not target.config:
        return False

    # Fork: update_state at the old checkpoint creates a new branch
    graph.update_state(
        target.config,
        values={"messages": [HumanMessage(content=new_message)]},
        as_node="wait_for_user",
    )
    return True


def _build_turn_output(state: Any) -> dict[str, Any]:
    """Extract turn output from graph state at an interrupt."""
    messages = state.values.get("messages", [])
    ai_messages = [m for m in messages if isinstance(m, AIMessage)]
    user_messages = [m for m in messages if isinstance(m, HumanMessage)]
    last_reply = ai_messages[-1].content if ai_messages else ""
    return {"reply": last_reply, "turn": len(user_messages)}


def _build_session_output(state: Any) -> dict[str, Any]:
    """Build final output when the graph conversation is complete."""
    messages = state.values.get("messages", [])
    user_count = len([m for m in messages if isinstance(m, HumanMessage)])
    return {
        "finished": True,
        "turn_count": user_count,
        "total_messages": len(messages),
        "summary": f"Session complete after {user_count} turns.",
    }


async def _finalize_invocation(
    ctx: TaskContext[dict],
    thread_config: dict[str, Any],
    invocation_id: str,
) -> dict[str, Any] | Any:
    """Save results and suspend/return after a graph invoke completes."""
    state = await asyncio.to_thread(_graph.get_state, thread_config)

    new_cp_id = state.config["configurable"]["checkpoint_id"]
    ctx.metadata.set("stable_checkpoint_id", new_cp_id)
    ctx.metadata.set("last_applied_invocation_id", invocation_id)

    if state.next:
        output = _build_turn_output(state)
        invocation_store.save(invocation_id, {"status": "completed", "output": output})
        return await ctx.suspend(reason="awaiting_user_input", output=output)

    result = _build_session_output(state)
    invocation_store.save(invocation_id, {"status": "completed", "output": result})
    return result


# ---------------------------------------------------------------------------
# Durable task — bridges LangGraph with HTTP lifecycle
# ---------------------------------------------------------------------------


@durable_task(name="langgraph_session", steerable=True)
async def langgraph_session(ctx: TaskContext[dict]) -> dict[str, Any]:
    """Run one LangGraph conversation turn with steering support.

    Input schema: ``{"session_id": str, "message": str, "invocation_id": str}``
    """
    session_id: str = ctx.input["session_id"]
    message: str = ctx.input["message"]
    invocation_id: str = ctx.input["invocation_id"]

    invocation_store.save(invocation_id, {"status": "running"})

    thread_config: dict[str, Any] = {"configurable": {"thread_id": session_id}}

    if ctx.entry_mode == "recovered":
        logger.warning("Recovered stale task for session %s", session_id)

    # ── Fork-on-steer: rollback to stable checkpoint ────────────────
    # If the previous invocation was cancelled mid-flight, the graph may
    # have drifted past the stable checkpoint.  Fork from the stable
    # checkpoint with the new message so the graph processes it cleanly.
    stable_cp = ctx.metadata.get("stable_checkpoint_id")
    if stable_cp:
        state = await asyncio.to_thread(_graph.get_state, thread_config)
        if state and state.values.get("messages"):
            current_cp = state.config["configurable"].get("checkpoint_id")
            if current_cp and current_cp != stable_cp:
                forked = await asyncio.to_thread(
                    _fork_from_checkpoint,
                    _graph,
                    thread_config,
                    stable_cp,
                    message,
                )
                if forked:
                    logger.info(
                        "Forked session %s from stable checkpoint %s",
                        session_id,
                        stable_cp,
                    )
                    completed = await asyncio.to_thread(
                        _invoke_cancellable,
                        _graph,
                        None,
                        thread_config,
                        ctx.cancel,
                    )

                    if not completed or ctx.cancel.is_set():
                        invocation_store.save(
                            invocation_id,
                            {"status": "cancelled", "reason": "steered"},
                        )
                        return await ctx.suspend(reason="steered")

                    return await _finalize_invocation(
                        ctx, thread_config, invocation_id
                    )

    # ── Phase 1: Pre-entry cancel ───────────────────────────────────
    if ctx.cancel.is_set():
        invocation_store.save(
            invocation_id, {"status": "cancelled", "reason": "steered"}
        )
        return await ctx.suspend(reason="steered")

    # ── Phase 2: Invoke graph with inter-node cancellation ──────────
    state = await asyncio.to_thread(_graph.get_state, thread_config)

    if state.next:
        graph_input = Command(resume=message)
    else:
        graph_input = {
            "messages": [HumanMessage(content=message)],
            "is_complete": False,
        }

    completed = await asyncio.to_thread(
        _invoke_cancellable, _graph, graph_input, thread_config, ctx.cancel
    )

    # ── Phase 3: Post-completion cancel check ───────────────────────
    if not completed or ctx.cancel.is_set():
        invocation_store.save(
            invocation_id, {"status": "cancelled", "reason": "steered"}
        )
        return await ctx.suspend(reason="steered")

    # Normal completion
    return await _finalize_invocation(ctx, thread_config, invocation_id)
