"""LangGraph conversation agent with durable task lifecycle.

Defines a LangGraph ``StateGraph`` for multi-turn conversation with
human-in-the-loop (``interrupt`` / ``Command(resume=...)``), wrapped in a
durable task so the session survives crashes and restarts.

- **LangGraph** owns the conversation flow.
- **Durable task** owns crash resilience — ``.start()`` auto
  starts/resumes/recovers; ``ctx.entry_mode`` provides re-entry context.

Per-invocation results are written to the invocation store **inside** the
durable execution boundary — if the process crashes, the task recovers and
the write happens on re-execution.
"""

import asyncio
import logging
import sqlite3
import typing
from pathlib import Path
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
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


def _add_messages(left: list, right: list) -> list:
    """Simple message accumulator — appends new messages to existing list."""
    return left + right


class ConversationState(TypedDict):
    """Graph state for a multi-turn conversation."""

    messages: typing.Annotated[list, _add_messages]
    is_complete: bool


# ---------------------------------------------------------------------------
# Graph nodes
# ---------------------------------------------------------------------------


def process_input(state: ConversationState) -> dict[str, Any]:
    """Generate an AI response.  Replace stub with a real LLM call."""
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

_DATA_DIR = Path.home() / ".durable-sessions"
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
    """Construct the LangGraph StateGraph for multi-turn conversation."""
    builder = StateGraph(ConversationState)

    builder.add_node("process_input", process_input)
    builder.add_node("wait_for_user", wait_for_user)

    builder.add_edge(START, "process_input")
    builder.add_edge("process_input", "wait_for_user")

    builder.add_conditional_edges(
        "wait_for_user",
        _should_continue,
        {
            "continue": "process_input",
            "end": END,
        },
    )

    return builder.compile(checkpointer=_checkpointer)


_graph = _build_graph()


# ---------------------------------------------------------------------------
# Durable task — bridges LangGraph with HTTP lifecycle
# ---------------------------------------------------------------------------


@durable_task(name="langgraph_session")
async def langgraph_session(ctx: TaskContext[dict]) -> dict[str, Any]:
    """Single durable function per session.

    ``ctx.entry_mode`` tells us whether this is fresh, resumed, or recovered.

    The invocation result is written to ``invocation_store`` **inside** the
    durable boundary — if the process crashes, the task recovers and the
    write happens on re-execution.
    """
    session_id: str = ctx.input["session_id"]
    message: str = ctx.input["message"]
    invocation_id: str = ctx.input["invocation_id"]

    # Mark invocation as running — inside the durable boundary so it
    # only exists if the task is actually executing.
    invocation_store.save(invocation_id, {"status": "running"})

    thread_config: dict[str, Any] = {"configurable": {"thread_id": session_id}}

    if ctx.entry_mode == "recovered":
        logger.warning("Recovered stale task for session %s", session_id)

    # Check if graph already has a pending interrupt (resume case)
    state = await asyncio.to_thread(_graph.get_state, thread_config)

    if state.next:
        await asyncio.to_thread(
            _graph.invoke,
            Command(resume=message),
            thread_config,
        )
    else:
        await asyncio.to_thread(
            _graph.invoke,
            {
                "messages": [HumanMessage(content=message)],
                "is_complete": False,
            },
            thread_config,
        )

    # After invoke, check where the graph landed
    state = await asyncio.to_thread(_graph.get_state, thread_config)

    if state.next:
        # Graph is paused at interrupt
        messages = state.values.get("messages", [])
        ai_messages = [m for m in messages if isinstance(m, AIMessage)]
        user_messages = [m for m in messages if isinstance(m, HumanMessage)]
        last_reply = ai_messages[-1].content if ai_messages else ""

        output = {"reply": last_reply, "turn": len(user_messages)}
        invocation_store.save(invocation_id, {"status": "completed", "output": output})
        return await ctx.suspend(reason="awaiting_user_input", output=output)

    # Graph completed (user said "done")
    messages = state.values.get("messages", [])
    user_count = len([m for m in messages if isinstance(m, HumanMessage)])
    result = {
        "finished": True,
        "turn_count": user_count,
        "total_messages": len(messages),
        "summary": f"Session complete after {user_count} turns.",
    }
    invocation_store.save(invocation_id, {"status": "completed", "output": result})
    return result
