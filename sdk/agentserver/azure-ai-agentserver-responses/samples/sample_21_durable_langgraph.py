# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 21 — Durable LangGraph with SqliteSaver checkpointing.

Wraps a LangGraph ``StateGraph`` in a steerable durable response handler.
LangGraph's ``SqliteSaver`` checkpointer is the canonical example of an
**upstream framework that owns durability** — the SDK does the heavy
lifting; the response handler is just the bridge.

This sample implements the recovery contract:

- ``context.durable_metadata`` only stores a small ``stable_checkpoint_id``
  watermark — the last graph checkpoint where the handler successfully
  emitted an AI reply.
- On recovered entry, the handler queries the graph's current state,
  builds a resumption response from the AI messages already in the
  graph history, and emits ``response.in_progress`` carrying it (the
  client-visible reset point).
- The recovered attempt then resumes ``graph.stream(None, ...)`` from
  the current graph state. SqliteSaver guarantees node-boundary
  recovery, so no node is re-executed.
- Steering between turns is handled by ``fork_session``-style
  ``graph.update_state(...)`` from the stable checkpoint.

Demonstrates:

- LangGraph native checkpointing (``SqliteSaver`` is the source of truth).
- ``graph.stream()`` for inter-node cancellation.
- Recovery contract: resumption response + reset ``in_progress``.
- Cancellation policy applied at pre-entry / mid-stream / post-stream.
- Fork-on-steer for new turns that supersede a prior one.

Requirements::

    pip install langgraph langgraph-checkpoint-sqlite langchain-core

Usage::

    python sample_21_durable_langgraph.py

    # Turn 1
    curl -N -X POST http://localhost:8088/responses \\
        -H "Content-Type: application/json" \\
        -d '{"model": "langgraph", "input": "Research quantum computing",
             "stream": true, "store": true, "background": true}'

    # Steer (fork from stable checkpoint with new message)
    curl -N -X POST http://localhost:8088/responses \\
        -H "Content-Type: application/json" \\
        -d '{"model": "langgraph", "input": "Focus on error correction",
             "stream": true, "store": true, "background": true,
             "previous_response_id": "<id>"}'

    # Simulate mid-node shutdown
    SIMULATE_SHUTDOWN_MS=2500 python sample_21_durable_langgraph.py
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
from azure.ai.agentserver.responses.models._generated import ResponseObject


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

_DATA_DIR = Path.home() / ".durable-sessions" / "langgraph-responses"
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
    durable_background=True,
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

    Returns (completed, node_names_executed).
    """
    nodes_executed: list[str] = []
    for chunk in graph.stream(graph_input, config, stream_mode="updates"):
        for node_name in chunk:
            if node_name != "__end__":
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


def _build_resumption_response(
    context: ResponseContext,
    request: CreateResponse,
    thread_config: dict[str, Any],
) -> ResponseObject:
    """Build the recovery resumption response from current graph state.

    LangGraph is the source of truth for "what's safely committed" — each
    AI message in graph state was emitted at a node boundary checkpointed
    by SqliteSaver. We materialize one ``message`` output item per AI
    message currently in graph state. The recovered attempt then resumes
    ``graph.stream(None, ...)`` from the live checkpoint and any new AI
    messages get appended as fresh output items.
    """
    try:
        state = _graph.get_state(thread_config)
    except Exception:  # pylint: disable=broad-except
        state = None

    output: list[dict[str, Any]] = []
    if state is not None:
        messages = state.values.get("messages", []) if state.values else []
        for idx, msg in enumerate(m for m in messages if isinstance(m, AIMessage)):
            output.append(
                {
                    "type": "message",
                    "id": f"recovered_ai_{idx}",
                    "role": "assistant",
                    "status": "completed",
                    "content": [
                        {
                            "type": "output_text",
                            "text": str(msg.content),
                            "annotations": [],
                        }
                    ],
                }
            )

    return ResponseObject(
        {
            "id": context.response_id,
            "object": "response",
            "status": "in_progress",
            "output": output,
            "model": request.model,
        }
    )


@app.response_handler
async def handler(
    request: CreateResponse,
    context: ResponseContext,
):
    """LangGraph with SqliteSaver checkpoints + recovery contract."""
    input_text = await context.get_input_text()

    thread_id = context.conversation_id or context.response_id
    thread_config: dict[str, Any] = {"configurable": {"thread_id": thread_id}}

    # ── Recovery branch ─────────────────────────────────────────────
    # On recovered entry, seed the stream with a resumption response
    # built from the graph's current state (the upstream framework's
    # source of truth). The recovery `response.in_progress` emitted
    # below is the client-visible reset point.
    if context.is_recovery:
        resp_stream = ResponseEventStream(
            response_id=context.response_id,
            response=_build_resumption_response(context, request, thread_config),
        )
    else:
        resp_stream = ResponseEventStream(response_id=context.response_id, request=request)

    yield resp_stream.emit_created()

    # ── Phase 1: Pre-entry cancel ───────────────────────────────────
    # Still inject the message into graph state so next turn has context.
    # Only emit completed for steering. Others: just return.
    if context.cancel.is_set():
        stable_cp = context.durable_metadata.get("stable_checkpoint_id")
        if stable_cp:
            await asyncio.to_thread(_fork_from_checkpoint, _graph, thread_config, stable_cp, input_text)
        if context.cancel.is_set() and not context.client_cancelled and not context.shutdown.is_set():
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
    stable_cp = context.durable_metadata.get("stable_checkpoint_id")
    if not context.is_recovery and stable_cp and context.is_steered_turn:
        forked = await asyncio.to_thread(_fork_from_checkpoint, _graph, thread_config, stable_cp, input_text)
        if forked:
            completed, nodes = await asyncio.to_thread(_invoke_cancellable, _graph, None, thread_config, context.cancel)
            # Emit node progress as function call outputs
            for node in nodes:
                fn_call = resp_stream.add_output_item_function_call(name=node, call_id=f"node_{node}", arguments="{}")
                yield fn_call.emit_added()
                yield fn_call.emit_done()

            if not completed or context.cancel.is_set():
                if shutdown_timer and not shutdown_timer.done():
                    shutdown_timer.cancel()
                # Shutdown: return without terminal → re-entered on restart.
                if context.shutdown.is_set():
                    return
                yield resp_stream.emit_completed()
                return

            # Save new stable checkpoint
            state = await asyncio.to_thread(_graph.get_state, thread_config)
            context.durable_metadata["stable_checkpoint_id"] = state.config["configurable"]["checkpoint_id"]
            # Emit the AI reply
            for event in _build_reply_events(resp_stream, state):
                yield event
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

    completed, nodes = await asyncio.to_thread(_invoke_cancellable, _graph, graph_input, thread_config, context.cancel)

    for node in nodes:
        fn_call = resp_stream.add_output_item_function_call(name=node, call_id=f"node_{node}", arguments="{}")
        yield fn_call.emit_added()
        yield fn_call.emit_done()

    if shutdown_timer and not shutdown_timer.done():
        shutdown_timer.cancel()

    # ── Phase 3: Post-completion handling ───────────────────────────
    if not completed or context.cancel.is_set():
        # Shutdown: return without terminal → re-entered on restart.
        if context.shutdown.is_set():
            return
        yield resp_stream.emit_completed()
        return

    # Save stable checkpoint reference
    state = await asyncio.to_thread(_graph.get_state, thread_config)
    context.durable_metadata["stable_checkpoint_id"] = state.config["configurable"]["checkpoint_id"]

    for event in _build_reply_events(resp_stream, state):
        yield event
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
    if not context.cancel.is_set():
        context.shutdown.set()
        context.cancel.set()


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
