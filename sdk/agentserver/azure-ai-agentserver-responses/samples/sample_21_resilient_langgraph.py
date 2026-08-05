# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
r"""Sample 21 — Real-time streaming LangGraph agent (resilient + steerable).

A fully-async LangGraph ``StateGraph`` wrapped in a resilient, steerable
response handler that streams **in real time** — the ``generate_response``
node emits its answer token-by-token (with delays between tokens) and each
token is forwarded to the client as a ``response.output_text.delta`` the
instant the node produces it. Node execution and token generation are
consumed via ``graph.astream(...)``; nothing waits for the whole graph to
finish before returning events.

Capabilities showcased (see ``docs/resilient-responses-developer-guide.md``
and ``docs/handler-implementation-guide.md``):

- **Real-time token streaming** — ``generate_response`` streams tokens via
  LangGraph's custom stream writer; the handler relays each as a delta.
- **Composed checkpointing (1:1)** — LangGraph's ``AsyncSqliteSaver`` owns
  graph-execution resume; the framework owns the client-visible response (items
  + ids). Every time LangGraph commits a node the handler also takes a framework
  ``stream.checkpoint()``, recording the LangGraph checkpoint id in
  ``internal_metadata`` — so the two stores stay in lockstep and
  ``persisted_response`` is the single source of truth for recovery.
- **Crash recovery** — a recovered entry seeds the stream from
  ``context.persisted_response`` (re-emitting the SAME items with their ORIGINAL
  ids) and rewinds the graph to the checkpoint id recorded in
  ``internal_metadata`` (always consistent with the persisted items). Resuming
  from there re-runs only the not-yet-persisted work, so the reply is produced
  exactly once — never duplicated, never lost, no divergence window.
- **Steering** — ``context.is_steered_turn`` / ``context.pending_input_count``;
  a steered successor turn forks the graph from the last stable checkpoint.
- **Cancellation** — inter-token cancellation plus pre-entry / mid-stream /
  post-stream handling; shutdown (SIGTERM) defers to next-lifetime recovery.

Requirements::

    pip install langgraph langgraph-checkpoint-sqlite aiosqlite langchain-core

Usage::

    python sample_21_resilient_langgraph.py

    # Turn 1 (watch tokens arrive one at a time)
    curl -N -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "langgraph", "input": "Research quantum computing",
             "stream": true, "store": true, "background": true}'

    # Steer (fork from stable checkpoint with a new message)
    curl -N -X POST http://localhost:8088/responses \
        -H "Content-Type: application/json" \
        -d '{"model": "langgraph", "input": "Focus on error correction",
             "stream": true, "store": true, "background": true,
             "previous_response_id": "<id>"}'

    # Crash / graceful-shutdown recovery: SIGKILL or SIGTERM the process
    # mid-turn; the next lifetime recovers from persisted_response and resumes.
"""

import asyncio
import os
import typing
from pathlib import Path
from typing import Any

import aiosqlite
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.config import get_stream_writer
from langgraph.graph import END, START, StateGraph, add_messages
from langgraph.types import Command, interrupt

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
    ResponsesServerOptions,
)
from azure.ai.agentserver.core.tasks import set_resilient_tasks_enabled

try:
    from _state_store import ConversationStateStore
except ModuleNotFoundError:
    from samples._state_store import ConversationStateStore


# ─── Graph state ────────────────────────────────────────────────────────────


class ConversationState(typing.TypedDict):
    """Multi-turn conversation state with LangGraph's add_messages reducer."""

    messages: typing.Annotated[list, add_messages]
    is_complete: bool


# ─── Graph nodes ────────────────────────────────────────────────────────────

_STEP_DELAY = float(os.environ.get("LANGGRAPH_STEP_DELAY_SEC", "0.4"))  # Seconds per non-streaming node.
_TOKEN_DELAY = float(os.environ.get("LANGGRAPH_TOKEN_DELAY_SEC", "0.08"))  # Seconds between streamed tokens.


async def analyze_input(state: ConversationState) -> dict[str, Any]:
    """Simulate intent detection / input analysis."""
    await asyncio.sleep(_STEP_DELAY)
    return {}


async def generate_response(state: ConversationState) -> dict[str, Any]:
    """Generate the AI reply, streaming it token-by-token in real time.

    Replace the simulated loop with a real streaming LLM call. Each token is
    pushed through LangGraph's custom stream writer, so the handler can relay
    it to the client the instant it is produced.
    """
    writer = get_stream_writer()
    user_msgs = [m for m in state["messages"] if isinstance(m, HumanMessage)]
    turn = len(user_msgs)
    last = user_msgs[-1].content if user_msgs else ""
    reply = f"Turn {turn}: answering '{last}' with full context from {turn} turn(s)."

    accumulated = ""
    for token in reply.split():
        await asyncio.sleep(_TOKEN_DELAY)
        piece = token + " "
        accumulated += piece
        writer({"token": piece})  # → surfaced as a "custom" astream chunk
    return {"messages": [AIMessage(content=accumulated.strip())]}


async def refine_response(state: ConversationState) -> dict[str, Any]:
    """Post-processing (safety checks, formatting)."""
    await asyncio.sleep(_STEP_DELAY * 0.5)
    return {}


def wait_for_user(state: ConversationState) -> dict[str, Any]:
    """Pause the graph — wait for the next human message via interrupt."""
    user_input: str = interrupt({"prompt": "Next message (or 'done'):"})
    if user_input.strip().lower() == "done":
        return {"is_complete": True}
    return {"messages": [HumanMessage(content=user_input)], "is_complete": False}


def _should_continue(state: ConversationState) -> str:
    return "end" if state.get("is_complete", False) else "continue"


# ─── Persistent async checkpointer + graph (lazy — needs a running loop) ─────

# Co-locate the LangGraph checkpoint DB with the deployment's state root when
# one is configured (so all of this deployment's durable state lives together
# and survives restarts); fall back to a per-user dir for local runs.
_STATE_ROOT = os.environ.get("AGENTSERVER_STATE_ROOT")
_DATA_DIR = (
    Path(_STATE_ROOT) / "langgraph" if _STATE_ROOT else Path.home() / ".agentserver-sessions" / "langgraph-responses"
)
_DATA_DIR.mkdir(parents=True, exist_ok=True)
_DB_PATH = _DATA_DIR / "checkpoints.db"

_graph: Any = None
_graph_lock = asyncio.Lock()


def _build_graph(checkpointer: Any) -> Any:
    """analyze → generate → refine → wait_for_user (loop)."""
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
    return builder.compile(checkpointer=checkpointer)


async def _get_graph() -> Any:
    """Build the graph + ``AsyncSqliteSaver`` once, lazily (both need a loop).

    A file-backed SqliteSaver is used so LangGraph's graph-execution state
    survives a process crash/restart (the resilience contract's premise).
    """
    global _graph  # pylint: disable=global-statement
    if _graph is None:
        async with _graph_lock:
            if _graph is None:
                conn = await aiosqlite.connect(str(_DB_PATH))
                saver = AsyncSqliteSaver(conn)
                await saver.setup()
                _graph = _build_graph(saver)
    return _graph


# ─── Server ───────────────────────────────────────────────────────────────

options = ResponsesServerOptions(
    resilient_background=True,
    steerable_conversations=True,
)
app = ResponsesAgentServerHost(options=options)
_state_store = ConversationStateStore("resilient-langgraph")

# Explicitly opt into resilient-task startup recovery, for parity with the
# invocations resilient samples. The Responses framework already registers its
# internal durable tasks at host construction (so recovery runs regardless);
# this call just makes the opt-in intent explicit.
set_resilient_tasks_enabled(True)

# Metadata key: the LangGraph checkpoint id whose completed work matches the
# response items persisted so far. Recorded in ``internal_metadata`` (persisted
# atomically WITH the items on every ``stream.checkpoint()``, stripped on
# egress), so recovery can rewind the graph to exactly that point — closing the
# dual-store divergence window. See the "composing an external durable engine"
# section of docs/handler-implementation-guide.md.
_GRAPH_CP_KEY = "graph_checkpoint_id"


def _reply_already_persisted(stream: ResponseEventStream) -> bool:
    """True if a reply ``message`` item is already present in the response.

    On a recovered entry the stream is seeded from ``context.persisted_response``;
    a reply persisted before the crash is already present (with its ORIGINAL id)
    and re-emitted via the ``in_progress`` reset — so it must not be produced
    again. It also becomes True the moment this attempt closes a fresh reply item.
    """
    return any(
        isinstance(item, dict) and item.get("type") == "message" for item in (stream.response.get("output") or [])
    )


async def _fork_from_checkpoint(graph: Any, config: dict[str, Any], checkpoint_id: str, new_message: str) -> bool:
    """Fork graph state from a stable checkpoint with a new (steered) message."""
    # The sqlite checkpointer requires ``checkpoint_ns`` on the config it writes
    # through; the resilient context only carries ``thread_id``, so seed the
    # default namespace explicitly before resolving + forking the state.
    target_config = {"configurable": {"checkpoint_ns": "", **config["configurable"], "checkpoint_id": checkpoint_id}}
    target = await graph.aget_state(target_config)
    if not target or not target.config:
        return False
    await graph.aupdate_state(
        target.config,
        values={"messages": [HumanMessage(content=new_message)]},
        as_node="wait_for_user",
    )
    return True


async def _record_stable(context: ResponseContext, state: Any) -> None:
    """Record the current graph checkpoint as the stable fork point for steering."""
    cfg = getattr(state, "config", None) or {}
    checkpoint_id = cfg.get("configurable", {}).get("checkpoint_id")
    if checkpoint_id:
        await _state_store.save(
            context.conversation_chain_id,
            {"stable_checkpoint_id": checkpoint_id},
        )


@app.response_handler
async def handler(
    request: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
):
    """Real-time streaming LangGraph handler with resilience + steering.

    Forward and recovery share ONE streaming loop; they differ only in where the
    graph resumes from. Recovery rewinds the graph to the checkpoint recorded in
    ``persisted_response.internal_metadata`` (always consistent with the persisted
    items), so ``persisted_response`` is the single source of truth and there is
    no window in which the reply can be lost or duplicated.
    """
    graph = await _get_graph()
    chain_id = context.conversation_chain_id
    thread_config: dict[str, Any] = {"configurable": {"thread_id": chain_id}}

    # Seed from the last framework checkpoint so already-emitted items keep their
    # ORIGINAL ids; the in_progress below re-emits them (the reset point).
    if context.is_recovery and context.persisted_response is not None:
        stream = ResponseEventStream(response_id=context.response_id, response=context.persisted_response)
    else:
        stream = ResponseEventStream(response_id=context.response_id, request=request)

    yield stream.emit_created()

    # Shutdown and cancellation are mutually exclusive. Shutdown → defer to the
    # next lifetime. Cancellation with a queued steering input → this superseded
    # turn winds down cleanly (the STEERED SUCCESSOR turn — is_steered_turn — is
    # the one that forks the graph and runs the new message, not this turn).
    if context.shutdown.is_set():
        await context.exit_for_recovery()
    if cancellation_signal.is_set():
        if context.pending_input_count > 0:
            yield stream.emit_in_progress()
            yield stream.emit_completed()
        return

    yield stream.emit_in_progress()

    # ── Resolve where the graph runs from ───────────────────────────
    if context.is_recovery:
        # Rewind to the checkpoint that matches the persisted items and resume
        # with None: the turn's input was already applied at/before that
        # checkpoint, so nodes after it (incl. the token-streaming node, if its
        # reply was not yet persisted) re-run — re-streaming the reply exactly
        # when needed and nothing more.
        graph_cp = stream.internal_metadata.get(_GRAPH_CP_KEY) if context.persisted_response is not None else None
        run_config = {"configurable": {"thread_id": chain_id, "checkpoint_id": graph_cp}} if graph_cp else thread_config
        graph_input: Any = None
    else:
        input_text = await context.get_input_text()
        conversation_state = await _state_store.load(chain_id)
        stable_cp = conversation_state.get("stable_checkpoint_id")
        state = await graph.aget_state(thread_config)
        run_config = thread_config
        parked_at_interrupt = "wait_for_user" in (state.next or ())
        if stable_cp and context.is_steered_turn:
            # Fresh steered successor: fork from the last stable checkpoint with
            # the new message, then resume (input=None).
            forked = await _fork_from_checkpoint(graph, thread_config, stable_cp, input_text)
            graph_input = None if forked else {"messages": [HumanMessage(content=input_text)], "is_complete": False}
        elif parked_at_interrupt:
            # Cleanly paused at the wait_for_user interrupt — the next turn of the
            # conversation; satisfy the interrupt with the new message.
            graph_input = Command(resume=input_text)
        elif stable_cp:
            # Graph left mid-turn (e.g. a prior turn was cancelled before its
            # interrupt) — do NOT Command(resume) a non-interrupt node; fork a
            # clean turn from the last stable checkpoint instead.
            forked = await _fork_from_checkpoint(graph, thread_config, stable_cp, input_text)
            graph_input = None if forked else {"messages": [HumanMessage(content=input_text)], "is_complete": False}
        else:
            graph_input = {"messages": [HumanMessage(content=input_text)], "is_complete": False}

    # ── One real-time streaming loop (forward AND recovery) ─────────
    # ``custom`` chunks carry tokens (relayed instantly). ``checkpoints`` chunks
    # mark each LangGraph node commit — mirror every one with a framework
    # checkpoint, recording the graph checkpoint id in internal_metadata so the
    # two stores stay in lockstep (1:1). The reply item is closed on the first
    # checkpoint after its tokens (i.e. the streaming node's own commit).
    message: Any = None
    text: Any = None
    reply_open = False
    reply_closed = False
    saw_generate_commit = False
    interrupted = False
    async for mode, chunk in graph.astream(
        graph_input, run_config, stream_mode=["updates", "custom", "checkpoints"], durability="sync"
    ):
        if mode == "custom" and "token" in chunk:
            if not reply_open and not _reply_already_persisted(stream):
                message = stream.add_output_item_message()
                yield message.emit_added()
                text = message.add_text_content()
                yield text.emit_added()
                reply_open = True
            if reply_open:
                yield text.emit_delta(chunk["token"])
        elif mode == "updates" and "generate_response" in chunk:
            # The token-streaming node has committed — its next checkpoint chunk
            # is the point at which the reply is durable.
            saw_generate_commit = True
        elif mode == "checkpoints":
            checkpoint_id = chunk.get("config", {}).get("configurable", {}).get("checkpoint_id")
            if reply_open and not reply_closed and saw_generate_commit:
                yield text.emit_text_done()
                yield text.emit_done()
                yield message.emit_done()
                reply_closed = True
            if checkpoint_id:
                # Persist the items + the resume pointer atomically (1:1 mirror
                # of the LangGraph checkpoint that just committed).
                stream.internal_metadata[_GRAPH_CP_KEY] = checkpoint_id
                yield stream.checkpoint()
        if cancellation_signal.is_set() or context.shutdown.is_set():
            interrupted = True
            break

    # Close a still-open reply item (interrupted mid-stream) so the persisted
    # event stream stays well-formed.
    if reply_open and not reply_closed:
        yield text.emit_text_done()
        yield text.emit_done()
        yield message.emit_done()

    # ── Post-stream cancel / shutdown ───────────────────────────────
    if interrupted:
        if context.shutdown.is_set():
            # Shutdown mid-stream → defer to next-lifetime recovery.
            await context.exit_for_recovery()
        # Client cancel / steering → finish the turn with partial output.
        yield stream.emit_completed()
        return

    # ── Turn complete — record the stable fork point for steering ────
    await _record_stable(context, await graph.aget_state(thread_config))
    yield stream.emit_completed()


def main() -> None:
    app.run()


if __name__ == "__main__":
    main()
