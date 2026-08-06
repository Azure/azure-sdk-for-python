"""LangGraph conversation agent with resilient task lifecycle and steering.

Wraps a LangGraph ``StateGraph`` in a steerable resilient task.
Demonstrates the **checkpoint-and-fork** pattern for both steering and
crash recovery:

1. Pre-entry check      — short-circuit if cancel is pre-set
2. Inter-node check     — ``_invoke_cancellable`` checks between graph nodes
3. Fork-on-steer/recover — a steer (``is_steered_turn``) or crash
   (``entry_mode == "recovered"``) rolls back to the last stable checkpoint
   and re-runs this turn from there with the turn's message; the durable output
   is this function's return value, so the re-run is idempotent
4. Resume-at-interrupt  — ``Command(resume=...)`` is used ONLY when the graph is
   genuinely parked at the ``wait_for_user`` interrupt (the normal next turn)

LangGraph owns the conversation flow; the resilient task owns crash
resilience and steering orchestration. This mirrors the correctness learnings
from the responses LangGraph sample: never resume a crash-drifted graph from its
latest tip, and never mis-attribute a turn's input as the next turn's resume value.
"""

import asyncio
import logging
import os
import sqlite3
import typing
from pathlib import Path
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph, add_messages
from langgraph.types import Command, interrupt
from typing_extensions import TypedDict

from azure.ai.agentserver.core.storage import FoundryStateStore
from azure.ai.agentserver.core.tasks import TaskContext, multi_turn_task
from azure.ai.agentserver.core.streaming import streams

logger = logging.getLogger(__name__)

# Explicit application state store for invocation results and checkpoint pointers.
STATE_STORE_NAME = "resilient-langgraph"

# LangGraph's internal SQLite checkpointer remains local to this sample.
_STATE_ROOT = os.environ.get("AGENTSERVER_STATE_ROOT")
_DATA_DIR = (
    Path(_STATE_ROOT) / "langgraph-invocations"
    if _STATE_ROOT
    else Path.home() / ".agentserver-sessions"
)


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


class TaskInput(TypedDict):
    """Persisted input required to run or recover one conversation turn."""

    session_id: str
    message: str
    invocation_id: str
    call_id: str


# ---------------------------------------------------------------------------
# Graph nodes
# ---------------------------------------------------------------------------

# Simulated step delay — distributed across nodes so inter-node
# cancellation (via ``graph.stream()``) can bail out quickly. Overridable via
# ``LANGGRAPH_STEP_DELAY_SEC`` so tests (and impatient demos) can run it fast.
_STEP_DELAY = float(
    os.environ.get("LANGGRAPH_STEP_DELAY_SEC", "2")
)  # seconds per processing node


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
    time.sleep(_STEP_DELAY / 2)
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
    on_node: Any = None,
) -> bool:
    """Run the graph using ``stream()`` with inter-node cancellation.

    Instead of ``graph.invoke()`` which blocks until the full graph
    completes, this streams node-by-node and checks ``cancel_event``
    between nodes.  If cancellation is detected, execution stops before
    the next node runs.

    Returns ``True`` if the graph ran to completion (or interrupt),
    ``False`` if cancelled mid-graph.
    """
    for chunk in graph.stream(graph_input, config):
        if on_node is not None:
            on_node(chunk)
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
    # Load the target checkpoint to get its full config. The sqlite checkpointer
    # requires ``checkpoint_ns`` on the config it writes through; a bare
    # ``{"thread_id", "checkpoint_id"}`` (which is all the resilient task carries)
    # omits it, so seed the default namespace explicitly before resolving state.
    target_config = {
        "configurable": {
            "checkpoint_ns": "",
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
    store: FoundryStateStore,
    thread_config: dict[str, Any],
    invocation_id: str,
    session_id: str,
    call_id: str,
) -> dict[str, Any] | Any:
    """Save results and suspend/return after a graph invoke completes."""
    state = await asyncio.to_thread(_graph.get_state, thread_config)

    new_cp_id = state.config["configurable"]["checkpoint_id"]
    output = _build_turn_output(state) if state.next else _build_session_output(state)
    await store.set_item(
        f"session/{session_id}",
        {
            "stable_checkpoint_id": new_cp_id,
            "last_applied_invocation_id": invocation_id,
            "last_output": output,
        },
        tags={"session_id": session_id},
        call_id=call_id,
    )
    await store.set_item(
        f"invocation/{invocation_id}",
        {"status": "completed", "output": output},
        tags={"session_id": session_id},
        call_id=call_id,
    )
    return output


# ---------------------------------------------------------------------------
# Resilient task — bridges LangGraph with HTTP lifecycle
# ---------------------------------------------------------------------------


@multi_turn_task(name="langgraph_session", steerable=True)
async def langgraph_session(ctx: TaskContext[TaskInput]) -> dict[str, Any] | None:
    """Run one LangGraph conversation turn with steering + crash recovery.

    Input schema includes ``session_id``, ``message``, ``invocation_id``, and
    the opaque Foundry ``call_id`` required by outbound State Store calls.

    LangGraph integration (applying the responses-sample learnings):

    - **Steering and crash recovery both re-run this turn from the last STABLE
      checkpoint.** A steer (``is_steered_turn``) or a crash
      (``entry_mode == "recovered"``) can leave the graph drifted mid-turn.
      Rather than resuming from the graph's latest (possibly half-executed) tip
      — which would mis-attribute this turn's input or lose work — we fork from
      the checkpoint recorded after the last COMPLETED turn and re-inject this
      turn's message, re-deriving a clean, deterministic result. The durable
      output is this function's return value, so re-running is idempotent.
    - **``Command(resume=...)`` is used ONLY when the graph is genuinely parked
      at the ``wait_for_user`` interrupt** (the normal next-turn path) — never to
      "resume" a graph that a crash left pending a non-interrupt node (that would
      inject this turn's message as if it were the next turn's input).
    - A first-turn crash (no stable checkpoint yet) resumes the pending node in
      place (the message was already applied before the crash), so it is neither
      duplicated nor lost.
    - Cancellation is checked between nodes (``_invoke_cancellable``).
    """
    session_id: str = ctx.input["session_id"]
    message: str = ctx.input["message"]
    invocation_id: str = ctx.input["invocation_id"]
    call_id: str = ctx.input["call_id"]
    store = await FoundryStateStore.get_or_create(
        STATE_STORE_NAME,
        user_isolation=True,
        description="LangGraph session checkpoints and invocation results",
    )

    session_item = await store.get_item(f"session/{session_id}", call_id=call_id)
    session_state = (
        dict(session_item.value)
        if session_item is not None and isinstance(session_item.value, dict)
        else {}
    )
    if (
        ctx.entry_mode == "recovered"
        and session_state.get("last_applied_invocation_id") == invocation_id
    ):
        output = session_state.get("last_output")
        if isinstance(output, dict):
            await store.set_item(
                f"invocation/{invocation_id}",
                {"status": "completed", "output": output},
                tags={"session_id": session_id},
                call_id=call_id,
            )
            await store.aclose()
            return output

    await store.set_item(
        f"invocation/{invocation_id}",
        {"status": "running"},
        tags={"session_id": session_id},
        call_id=call_id,
    )
    stream = await streams.get_or_create(invocation_id)
    await stream.emit({"type": "lifecycle", "status": "running"})

    thread_config: dict[str, Any] = {"configurable": {"thread_id": session_id}}

    # ── Pre-entry cancel (steering supersede / client cancel) ───────
    if ctx.cancel.is_set():
        await store.set_item(
            f"invocation/{invocation_id}",
            {"status": "cancelled", "reason": "steered"},
            tags={"session_id": session_id},
            call_id=call_id,
        )
        await stream.close()
        await store.aclose()
        return None

    # ── Resolve how this turn runs ──────────────────────────────────
    recovered = ctx.entry_mode == "recovered"
    stable_cp = session_state.get("stable_checkpoint_id")
    state = await asyncio.to_thread(_graph.get_state, thread_config)
    parked_at_interrupt = bool(state.next) and "wait_for_user" in state.next

    graph_input: Any
    if (ctx.is_steered_turn or recovered) and stable_cp:
        # Steer or crash recovery: discard any drift past the last completed turn
        # and re-run THIS turn cleanly by forking from the stable checkpoint.
        if recovered:
            logger.info(
                "Recovered session %s — re-running turn from stable checkpoint %s",
                session_id,
                stable_cp,
            )
        forked = await asyncio.to_thread(
            _fork_from_checkpoint, _graph, thread_config, stable_cp, message
        )
        graph_input = (
            None
            if forked
            else {"messages": [HumanMessage(content=message)], "is_complete": False}
        )
    elif recovered:
        # First-turn crash (no stable checkpoint yet): resume the pending node in
        # place — this turn's message was already applied before the crash, so
        # re-injecting it would duplicate it.
        graph_input = None
    elif parked_at_interrupt:
        # Normal next turn — satisfy the wait_for_user interrupt with the message.
        graph_input = Command(resume=message)
    else:
        # Fresh first turn.
        graph_input = {
            "messages": [HumanMessage(content=message)],
            "is_complete": False,
        }

    # ── Run the graph with inter-node cancellation ──────────────────
    loop = asyncio.get_running_loop()
    pending_updates: list[Any] = []

    def _on_node(chunk: dict) -> None:
        """Stream node progress events from the sync graph thread."""
        node_names = list(chunk.keys())
        for name in node_names:
            pending_updates.append(
                asyncio.run_coroutine_threadsafe(
                    stream.emit({"type": "node_progress", "node": name}),
                    loop,
                )
            )
        pending_updates.append(
            asyncio.run_coroutine_threadsafe(
                store.set_item(
                    f"invocation/{invocation_id}",
                    {
                        "status": "streaming",
                        "last_node": node_names[-1] if node_names else None,
                    },
                    tags={"session_id": session_id},
                    call_id=call_id,
                ),
                loop,
            )
        )

    completed = await asyncio.to_thread(
        _invoke_cancellable,
        _graph,
        graph_input,
        thread_config,
        ctx.cancel,
        _on_node,
    )
    await asyncio.gather(*(asyncio.wrap_future(update) for update in pending_updates))

    # ── Post-run cancel check ───────────────────────────────────────
    if not completed or ctx.cancel.is_set():
        await store.set_item(
            f"invocation/{invocation_id}",
            {"status": "cancelled", "reason": "steered"},
            tags={"session_id": session_id},
            call_id=call_id,
        )
        await stream.close()
        await store.aclose()
        return None

    # ── Normal completion ───────────────────────────────────────────
    await stream.close()
    try:
        return await _finalize_invocation(
            store, thread_config, invocation_id, session_id, call_id
        )
    finally:
        await store.aclose()
