# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
r"""Sample 21 — Resilient LangGraph with SqliteSaver checkpointing.

Wraps a LangGraph ``StateGraph`` in a steerable resilient response handler.
LangGraph's ``SqliteSaver`` checkpointer is the canonical example of an
**upstream framework that owns resilience** — the SDK does the heavy
lifting; the response handler is just the bridge.

This sample implements the recovery contract by **composing two
checkpointers**:

- LangGraph's ``SqliteSaver`` owns **graph-execution** resume, keyed by the
  thread id = ``context.conversation_chain_id`` (the stable, per-conversation
  chain id — same across turns and recovery attempts).
- The **framework** owns the **client-visible response** (output items + their
  ids): ``yield stream.checkpoint()`` after emitting the AI reply persists the
  response snapshot. On a recovered entry the handler seeds the stream from
  ``context.persisted_response`` — so an already-checkpointed reply is present
  with its **original id** — and emits ``response.in_progress`` (the reset
  point) to re-emit it verbatim. It never invents new ids.
- The recovered attempt resumes ``graph.stream(None, ...)`` from the live
  SqliteSaver checkpoint; already-completed nodes are not re-run. The reply is
  emitted only if it is not already present in the persisted response, so it is
  neither duplicated nor lost across any crash window.
- Steering between turns forks the graph via ``graph.update_state(...)`` from a
  ``stable_checkpoint_id`` watermark.

Demonstrates:

- Composing framework ``stream.checkpoint()`` / ``context.persisted_response``
  with an upstream framework's own checkpointer (LangGraph ``SqliteSaver``).
- Recovery that re-emits the SAME items with their ORIGINAL ids (no invented ids).
- ``graph.stream()`` for inter-node cancellation.
- Cancellation policy applied at pre-entry / mid-stream / post-stream.
- Fork-on-steer for new turns that supersede a prior one.

Requirements::

    pip install langgraph langgraph-checkpoint-sqlite langchain-core

Usage::

    python sample_21_resilient_langgraph.py

    # Turn 1
    curl -N -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "langgraph", "input": "Research quantum computing",
             "stream": true, "store": true, "background": true}'

    # Steer (fork from stable checkpoint with new message)
    curl -N -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "langgraph", "input": "Focus on error correction",
             "stream": true, "store": true, "background": true,
             "previous_response_id": "<id>"}'

    # Simulate mid-node shutdown
    SIMULATE_SHUTDOWN_MS=2500 python sample_21_resilient_langgraph.py
"""

import asyncio
import os
import sqlite3
import typing
from pathlib import Path
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph, add_messages
from langgraph.types import Command, interrupt

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
    ResponsesServerOptions,
)


# ─── Graph State ────────────────────────────────────────────────────────────


class ConversationState(typing.TypedDict):
    """Multi-turn conversation state with LangGraph's add_messages reducer."""

    messages: typing.Annotated[list, add_messages]
    is_complete: bool


# ─── Graph Nodes ────────────────────────────────────────────────────────────

_STEP_DELAY = 1.0  # Seconds per node — makes inter-node cancel observable


async def analyze_input(state: ConversationState) -> dict[str, Any]:
    """Simulate intent detection / input analysis."""
    await asyncio.sleep(_STEP_DELAY)
    return {}


async def generate_response(state: ConversationState) -> dict[str, Any]:
    """Generate AI response (replace with real LLM call)."""
    await asyncio.sleep(_STEP_DELAY)
    messages = state["messages"]
    user_msgs = [m for m in messages if isinstance(m, HumanMessage)]
    turn = len(user_msgs)
    last = user_msgs[-1].content if user_msgs else ""
    reply = f"Turn {turn}: Processing '{last}' with full context from {turn} turns."
    return {"messages": [AIMessage(content=reply)]}


async def refine_response(state: ConversationState) -> dict[str, Any]:
    """Post-processing (safety checks, formatting)."""
    await asyncio.sleep(_STEP_DELAY * 0.5)
    return {}


def wait_for_user(state: ConversationState) -> dict[str, Any]:
    """Pause graph — wait for next human message via interrupt."""
    user_input: str = interrupt({"prompt": "Next message (or 'done'):"})
    if user_input.strip().lower() == "done":
        return {"is_complete": True}
    return {"messages": [HumanMessage(content=user_input)], "is_complete": False}


def _should_continue(state: ConversationState) -> str:
    if state.get("is_complete", False):
        return "end"
    return "continue"


# ─── Persistent Checkpointer ───────────────────────────────────────────────

_DATA_DIR = Path.home() / ".agentserver-sessions" / "langgraph-responses"
_DATA_DIR.mkdir(parents=True, exist_ok=True)
_DB_PATH = _DATA_DIR / "checkpoints.db"

_conn = sqlite3.connect(str(_DB_PATH), check_same_thread=False)
_checkpointer = SqliteSaver(_conn)
_checkpointer.setup()


# ─── Build Graph ────────────────────────────────────────────────────────────


def _build_graph() -> Any:
    """Multi-node graph: analyze → generate → refine → wait_for_user (loop)."""
    builder = StateGraph(ConversationState)
    builder.add_node("analyze_input", analyze_input)
    builder.add_node("generate_response", generate_response)
    builder.add_node("refine_response", refine_response)
    builder.add_node("wait_for_user", wait_for_user)

    builder.add_edge(START, "analyze_input")
    builder.add_edge("analyze_input", "generate_response")
    builder.add_edge("generate_response", "refine_response")
    builder.add_edge("refine_response", "wait_for_user")
    builder.add_conditional_edges("wait_for_user", _should_continue, {"continue": "analyze_input", "end": END})
    return builder.compile(checkpointer=_checkpointer)


_graph = _build_graph()


# ─── Server ─────────────────────────────────────────────────────────────────

options = ResponsesServerOptions(
    resilient_background=True,
    steerable_conversations=True,
)
app = ResponsesAgentServerHost(options=options)

_SIMULATE_SHUTDOWN_MS = int(os.environ.get("SIMULATE_SHUTDOWN_MS", "0"))


def _invoke_cancellable(
    graph: Any,
    graph_input: Any,
    config: dict[str, Any],
    cancel_event: asyncio.Event,
) -> tuple[bool, list[str]]:
    """Stream graph node-by-node with inter-node cancellation.

    Returns (completed, node_names_executed). LangGraph pseudo-events
    (``__end__``, ``__interrupt__``, …) are filtered out — only real node
    names count as executed nodes (so a resume that re-yields ``__interrupt__``
    does not surface as spurious node progress). ``durability="sync"`` ensures
    each node's checkpoint is durable before the update is observed, matching
    this sample's contract that SqliteSaver owns graph-execution resume.
    """
    nodes_executed: list[str] = []
    for chunk in graph.stream(graph_input, config, stream_mode="updates", durability="sync"):
        for node_name in chunk:
            if not node_name.startswith("__"):
                nodes_executed.append(node_name)
        if cancel_event.is_set():
            return False, nodes_executed
    return True, nodes_executed


def _fork_from_checkpoint(
    graph: Any,
    config: dict[str, Any],
    target_checkpoint_id: str,
    new_message: str,
) -> bool:
    """Fork graph state from a stable checkpoint with a new message."""
    target_config = {"configurable": {**config["configurable"], "checkpoint_id": target_checkpoint_id}}
    target = graph.get_state(target_config)
    if not target or not target.config:
        return False
    graph.update_state(
        target.config,
        values={"messages": [HumanMessage(content=new_message)]},
        as_node="wait_for_user",
    )
    return True


def _reply_already_persisted(resp_stream: ResponseEventStream) -> bool:
    """True if a reply ``message`` item is already present in the response.

    On a recovered entry the stream is seeded from
    ``context.persisted_response``, so any reply that was checkpointed before
    the crash is already in ``resp_stream.response.output`` (with its ORIGINAL
    id). We must NOT re-emit it (that would duplicate it with a fresh id). This
    is the robust recovery guard: decide by "is the reply already represented
    in the persisted response?" — NOT by "did generate_response run this
    attempt?" (which would lose a reply that LangGraph committed but the
    framework had not yet checkpointed).
    """
    return any(getattr(item, "type", None) == "message" for item in resp_stream.response.output)


@app.response_handler
async def handler(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """LangGraph with SqliteSaver checkpoints + framework checkpoints.

    Composition of two checkpointers:
    - **LangGraph SqliteSaver** owns graph-execution resume (keyed by the
      thread id = ``context.conversation_chain_id``).
    - **The framework** owns the client-visible response (output items + their
      ids): ``stream.checkpoint()`` persists the response snapshot, and on a
      recovered entry ``context.persisted_response`` re-emits the SAME items
      with their ORIGINAL ids (never invents new ids).
    """
    input_text = await context.get_input_text()

    # Stable chain id — same value across every turn of this conversation and
    # across all recovery attempts; the intended upstream thread/session id.
    thread_id = context.conversation_chain_id
    thread_config: dict[str, Any] = {"configurable": {"thread_id": thread_id}}

    # ── Recovery branch ─────────────────────────────────────────────
    # On recovered entry, seed the stream from the last framework checkpoint
    # (``context.persisted_response``). Any output item checkpointed before the
    # crash is already in ``resp_stream.response.output`` with its ORIGINAL id;
    # the ``response.in_progress`` emitted below re-emits those items and IS the
    # client-visible reset point. LangGraph's SqliteSaver independently resumes
    # graph execution from its own checkpoint below.
    if context.is_recovery and context.persisted_response is not None:
        resp_stream = ResponseEventStream(
            response_id=context.response_id,
            response=context.persisted_response,
        )
    else:
        resp_stream = ResponseEventStream(response_id=context.response_id, request=request)

    yield resp_stream.emit_created()

    # ── Phase 1: Pre-entry cancel / shutdown ───────────────────────
    # Still inject the message into graph state so next turn has context.
    # Only emit completed for steering. Others (client-cancel, shutdown):
    # just return.
    if cancellation_signal.is_set() or context.shutdown.is_set():
        stable_cp = context.conversation_chain_metadata.get("stable_checkpoint_id")
        if stable_cp:
            await asyncio.to_thread(_fork_from_checkpoint, _graph, thread_config, stable_cp, input_text)
        if cancellation_signal.is_set() and context.pending_input_count > 0:
            yield resp_stream.emit_completed()
        return

    yield resp_stream.emit_in_progress()

    # Shutdown simulation
    shutdown_timer: asyncio.Task | None = None
    if _SIMULATE_SHUTDOWN_MS > 0:
        shutdown_timer = asyncio.create_task(_simulate_shutdown(context))

    # ── Fork-on-steer (fresh-entry only) ────────────────────────────
    # If this turn is the *successor* of a steered turn AND there is a
    # stable checkpoint to fork from, branch the graph to that point
    # with the new message. Skip on a recovered entry — we never want to
    # re-fork on recovery; the SqliteSaver state IS the source of truth.
    stable_cp = context.conversation_chain_metadata.get("stable_checkpoint_id")
    if not context.is_recovery and stable_cp and context.is_steered_turn:
        forked = await asyncio.to_thread(_fork_from_checkpoint, _graph, thread_config, stable_cp, input_text)
        if forked:
            completed, nodes = await asyncio.to_thread(
                _invoke_cancellable, _graph, None, thread_config, cancellation_signal
            )
            # Emit node progress as function call outputs
            for node in nodes:
                fn_call = resp_stream.add_output_item_function_call(name=node, call_id=f"node_{node}", arguments="{}")
                yield fn_call.emit_added()
                yield fn_call.emit_done()

            if not completed or cancellation_signal.is_set():
                if shutdown_timer and not shutdown_timer.done():
                    shutdown_timer.cancel()
                # Shutdown: return without terminal → re-entered on restart.
                if context.shutdown.is_set():
                    return
                yield resp_stream.emit_completed()
                return

            # Save new stable checkpoint
            state = await asyncio.to_thread(_graph.get_state, thread_config)
            context.conversation_chain_metadata["stable_checkpoint_id"] = state.config["configurable"]["checkpoint_id"]
            # Emit the AI reply (fresh — fork-on-steer never runs on recovery).
            for event in _build_reply_events(resp_stream, state):
                yield event
            # Framework checkpoint: persist the response snapshot (reply item +
            # its id) so a crash before the terminal re-emits it verbatim.
            yield resp_stream.checkpoint()
            if shutdown_timer and not shutdown_timer.done():
                shutdown_timer.cancel()
            yield resp_stream.emit_completed()
            return

    # ── Phase 2: Normal invocation (graph.stream with inter-node cancel) ─
    state = await asyncio.to_thread(_graph.get_state, thread_config)

    if state.next:
        graph_input = Command(resume=input_text)
    else:
        graph_input = {"messages": [HumanMessage(content=input_text)], "is_complete": False}

    completed, nodes = await asyncio.to_thread(
        _invoke_cancellable, _graph, graph_input, thread_config, cancellation_signal
    )

    for node in nodes:
        fn_call = resp_stream.add_output_item_function_call(name=node, call_id=f"node_{node}", arguments="{}")
        yield fn_call.emit_added()
        yield fn_call.emit_done()

    if shutdown_timer and not shutdown_timer.done():
        shutdown_timer.cancel()

    # ── Phase 3: Post-completion handling ───────────────────────────
    if not completed or cancellation_signal.is_set():
        # Shutdown: return without terminal → re-entered on restart.
        if context.shutdown.is_set():
            return
        yield resp_stream.emit_completed()
        return

    # Save stable checkpoint reference (for fork-on-steer)
    state = await asyncio.to_thread(_graph.get_state, thread_config)
    context.conversation_chain_metadata["stable_checkpoint_id"] = state.config["configurable"]["checkpoint_id"]

    # Emit this turn's reply only if it isn't already in the persisted
    # response. On a recovered entry where the reply was checkpointed before
    # the crash, it is already seeded (with its original id) and re-emitted via
    # the in_progress reset — re-emitting here would duplicate it with a fresh
    # id. If the reply is NOT yet persisted (crash before the framework
    # checkpoint), we emit it from the current graph state — which is durable
    # via SqliteSaver — so the reply is never lost.
    if not _reply_already_persisted(resp_stream):
        for event in _build_reply_events(resp_stream, state):
            yield event
        # Framework checkpoint: persist the response snapshot (reply item + its
        # id) so recovery re-emits it verbatim rather than inventing a new id.
        yield resp_stream.checkpoint()
    yield resp_stream.emit_completed()


def _build_reply_events(resp_stream: ResponseEventStream, state: Any) -> list[Any]:
    """Build response events for the latest AI message from graph state."""
    messages = state.values.get("messages", [])
    ai_messages = [m for m in messages if isinstance(m, AIMessage)]
    if not ai_messages:
        return []
    reply = ai_messages[-1].content
    message = resp_stream.add_output_item_message()
    text = message.add_text_content()
    return [
        message.emit_added(),
        text.emit_added(),
        text.emit_delta(reply),
        text.emit_text_done(),
        text.emit_done(),
        message.emit_done(),
    ]


async def _simulate_shutdown(context: ResponseContext) -> None:
    """Fire SHUTTING_DOWN after a delay (local testing only)."""
    await asyncio.sleep(_SIMULATE_SHUTDOWN_MS / 1000.0)
    context.shutdown.set()


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
