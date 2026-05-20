# Copyright (c) Microsoft. All rights reserved.

"""LangGraph-powered deep research agent with SQLite checkpointing.

Durability is handled entirely by LangGraph's checkpoint system:
  - SqliteSaver persists graph state after each node execution
  - On crash recovery, resuming with the same thread_id picks up from the
    last completed node automatically
  - No manual checkpointing, no FileStreamHandler, no metadata management

The graph loops through 12 research stages. Each stage is a node execution
that makes an LLM call and streams tokens to the consumer via an asyncio.Queue.
"""

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path
from typing import Annotated, Any

from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

logger = logging.getLogger(__name__)

# ── Azure AI client setup ─────────────────────────────────────────────────────

_endpoint = os.environ.get("FOUNDRY_PROJECT_ENDPOINT")
if not _endpoint:
    raise EnvironmentError("FOUNDRY_PROJECT_ENDPOINT is required.")

_model = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4.1-mini")
_credential = DefaultAzureCredential()
_project_client = AIProjectClient(endpoint=_endpoint, credential=_credential)
_openai_client = _project_client.get_openai_client()

STAGE_DURATION = int(os.environ.get("STAGE_DURATION", "5"))

# ── Checkpoint store ──────────────────────────────────────────────────────────

_DATA_DIR = Path.home() / ".durable-research"
_DATA_DIR.mkdir(parents=True, exist_ok=True)
_DB_PATH = _DATA_DIR / "checkpoints.db"

checkpointer: AsyncSqliteSaver | None = None
_checkpointer_conn = None


async def init_checkpointer() -> AsyncSqliteSaver:
    """Initialize the async SQLite checkpointer (call once at startup)."""
    global checkpointer, _checkpointer_conn
    if checkpointer is None:
        import aiosqlite
        _checkpointer_conn = await aiosqlite.connect(str(_DB_PATH))
        checkpointer = AsyncSqliteSaver(_checkpointer_conn)
        await checkpointer.setup()
        logger.info("LangGraph checkpoints: %s", _DB_PATH)
    return checkpointer


# ── Research stages ───────────────────────────────────────────────────────────

STAGES = [
    "Decomposing topic into focused research questions",
    "Surveying foundational literature and key concepts",
    "Identifying leading researchers and institutions",
    "Analyzing recent breakthroughs and publications",
    "Examining competing theories and approaches",
    "Evaluating experimental evidence and data quality",
    "Mapping connections to adjacent fields",
    "Identifying open problems and knowledge gaps",
    "Assessing real-world applications and impact",
    "Analyzing funding landscape and research trends",
    "Synthesizing findings into a coherent narrative",
    "Generating key insights and recommendations",
]


# ── Graph state ───────────────────────────────────────────────────────────────


def _append_results(existing: list[dict], new: list[dict]) -> list[dict]:
    """Reducer: append new results to existing list."""
    return existing + new


class ResearchState(TypedDict):
    """State for the research graph."""
    topic: str
    current_stage: int
    results: Annotated[list[dict], _append_results]
    is_cancelled: bool
    is_complete: bool


# ── Streaming infrastructure ──────────────────────────────────────────────────
# Each running graph gets an asyncio.Queue for live token streaming.
# The HTTP handler iterates this queue to emit SSE events.

_active_streams: dict[str, asyncio.Queue] = {}
_active_cancel: asyncio.Event | None = None  # cancel event for current execution
_SENTINEL = object()


def get_stream_queue(thread_id: str) -> asyncio.Queue | None:
    """Get the live stream queue for a running graph, or None."""
    return _active_streams.get(thread_id)


# ── Graph nodes ───────────────────────────────────────────────────────────────


async def research_stage(state: ResearchState) -> dict[str, Any]:
    """Execute one research stage: LLM call with token streaming."""
    stage_idx = state["current_stage"]
    topic = state["topic"]
    total = len(STAGES)

    if stage_idx >= total:
        return {"is_complete": True}

    # Check cancel before starting work
    if _active_cancel and _active_cancel.is_set():
        return {"is_cancelled": True}

    stage = STAGES[stage_idx]
    results = state.get("results", [])

    # Find the stream queue for this graph execution
    queue = _active_streams.get("_current_")

    # Announce stage
    if queue:
        await queue.put({"type": "token", "content": f"\n\n**[Stage {stage_idx + 1}/{total}]** {stage}...\n"})

    # Simulate processing delay
    await asyncio.sleep(STAGE_DURATION)

    # Build prompt with prior context
    if results:
        findings = "\n".join(f"- {r['stage']}: {r['result'][:80]}" for r in results[-3:])
        instructions = (
            f"You are a research assistant performing: '{stage}'. "
            f"Build on these prior findings:\n{findings}\n\n"
            "Provide 3-4 sentences of new, specific, detailed findings. Be informative."
        )
    else:
        instructions = (
            f"You are a research assistant performing: '{stage}'. "
            "Provide 3-4 sentences of specific, detailed findings. Be informative and engaging."
        )

    # Stream tokens from the LLM
    full_text = ""
    async for event in await _openai_client.responses.create(
        model=_model,
        instructions=instructions,
        input=f"Research topic: {topic}",
        store=False,
        stream=True,
    ):
        if event.type == "response.output_text.delta":
            full_text += event.delta
            if queue:
                await queue.put({"type": "token", "content": event.delta})

    # Announce completion
    if queue:
        await queue.put({"type": "token", "content": f"\n✅ Stage {stage_idx + 1}/{total} complete.\n"})

    return {
        "current_stage": stage_idx + 1,
        "results": [{"stage": stage, "result": full_text}],
    }


def should_continue(state: ResearchState) -> str:
    """Route: continue to next stage or finish."""
    if state.get("is_cancelled", False):
        return "end"
    if state.get("is_complete", False):
        return "end"
    if state["current_stage"] >= len(STAGES):
        return "end"
    return "next_stage"


# ── Build the graph ───────────────────────────────────────────────────────────


def build_graph() -> StateGraph:
    """Construct the research state graph."""
    builder = StateGraph(ResearchState)

    builder.add_node("research_stage", research_stage)

    builder.add_edge(START, "research_stage")
    builder.add_conditional_edges(
        "research_stage",
        should_continue,
        {"next_stage": "research_stage", "end": END},
    )

    return builder


_graph_builder = build_graph()


async def get_compiled_graph():
    """Get the compiled graph with checkpointer."""
    cp = await init_checkpointer()
    return _graph_builder.compile(checkpointer=cp)


# ── Public API ────────────────────────────────────────────────────────────────


async def run_research(thread_id: str, topic: str, *, cancel_event: asyncio.Event | None = None) -> asyncio.Queue:
    """Start or resume a research graph, returning the live stream queue.

    If the graph already has checkpoint state for this thread_id, it resumes
    from where it left off (re-invokes with the checkpointed state).
    Otherwise it starts fresh.

    The returned queue yields dicts: {"type": "token", "content": "..."}.
    A sentinel None signals completion.
    """
    global _active_cancel
    queue: asyncio.Queue = asyncio.Queue()
    _active_streams[thread_id] = queue
    _active_streams["_current_"] = queue  # for the node to find
    _active_cancel = cancel_event  # for the node to check

    async def _run():
        global _active_cancel
        try:
            graph = await get_compiled_graph()
            config = {"configurable": {"thread_id": thread_id}}

            # Check existing state — if we have a checkpoint, resume from it
            snapshot = await graph.aget_state(config)
            existing_stage = 0
            if snapshot and snapshot.values:
                existing_stage = snapshot.values.get("current_stage", 0)

            if existing_stage > 0 and existing_stage < len(STAGES):
                # Resuming from crash — re-invoke with checkpointed state
                total = len(STAGES)
                logger.warning(
                    "\u26a1 Resuming from stage %d/%d (thread=%s)",
                    existing_stage + 1, total, thread_id,
                )
                await queue.put({
                    "type": "token",
                    "content": f"\n\n\u26a1 **Recovered from crash!** Resuming from stage {existing_stage + 1}/{total}...\n\n",
                })
                # Clear any stale cancel flag from previous run
                resume_state = {**snapshot.values, "is_cancelled": False}
                async for _ in graph.astream(resume_state, config):
                    pass
            elif existing_stage >= len(STAGES):
                # Already complete — just signal done
                await queue.put({"type": "token", "content": "\n\n---\n\u2705 **Research already complete!**\n"})
            else:
                # Fresh start
                initial_state = {
                    "topic": topic,
                    "current_stage": 0,
                    "results": [],
                    "is_cancelled": False,
                    "is_complete": False,
                }
                async for _ in graph.astream(initial_state, config):
                    pass

            # Signal completion
            if cancel_event and cancel_event.is_set():
                await queue.put({"type": "token", "content": "\n\n---\n\U0001f6d1 **Research cancelled.**\n"})
            elif existing_stage < len(STAGES):
                await queue.put({"type": "token", "content": "\n\n---\n\u2705 **Research complete!**\n"})
        except Exception as exc:
            logger.exception("Graph execution failed: %s", exc)
            await queue.put({"type": "error", "content": f"Error: {exc}"})
        finally:
            await queue.put(None)  # sentinel
            _active_streams.pop(thread_id, None)
            _active_streams.pop("_current_", None)
            _active_cancel = None

    asyncio.create_task(_run())
    return queue


async def get_checkpoint_state(thread_id: str) -> dict[str, Any] | None:
    """Load the latest checkpoint state for replay (used by GET handler)."""
    graph = await get_compiled_graph()
    config = {"configurable": {"thread_id": thread_id}}
    state = await graph.aget_state(config)
    if state and state.values:
        return state.values
    return None
