# Copyright (c) Microsoft. All rights reserved.

"""The durable research task — this is what makes the agent crash-resilient.

The ONLY things you need for durability:
  1. ``@durable_task`` decorator
  2. ``ctx.metadata[...] = value`` + ``await ctx.metadata.flush()`` to checkpoint

That's it. Everything else here is just normal agent logic.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any

from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential

from azure.ai.agentserver.core.durable import TaskContext, durable_task

logger = logging.getLogger(__name__)

# ── Azure AI client setup ─────────────────────────────────────────────────────

_endpoint = os.environ.get("FOUNDRY_PROJECT_ENDPOINT")
if not _endpoint:
    raise EnvironmentError("FOUNDRY_PROJECT_ENDPOINT is required.")

_model = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4.1-mini")
_credential = DefaultAzureCredential()
_project_client = AIProjectClient(endpoint=_endpoint, credential=_credential)
_openai_client = _project_client.get_openai_client()

# ── File-backed stream handler ────────────────────────────────────────────────
# Stores stream items to disk so consumers can reconnect after a crash/disconnect
# and replay from where they left off.

_STREAM_DIR = Path.home() / ".durable-tasks" / "_streams"


class FileStreamHandler:
    """Stream handler that persists items to a file for crash-resilient replay.

    On init, if the stream file already exists (i.e. recovering after crash),
    all previously written items are loaded back into the queue so that a
    consumer iterating via ``get()`` sees the full history followed by new items.
    """

    def __init__(self, task_id: str) -> None:
        self._task_id = task_id
        self._dir = _STREAM_DIR / task_id
        self._dir.mkdir(parents=True, exist_ok=True)
        self._file = self._dir / "stream.jsonl"
        self._queue: asyncio.Queue[Any] = asyncio.Queue()
        self._closed = False
        self._SENTINEL = object()

        # Replay persisted items into the queue on recovery
        if self._file.exists():
            for line in self._file.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    data = json.loads(line)
                    if "__done__" not in data:
                        self._queue.put_nowait(data)

    async def put(self, item: Any) -> None:
        """Persist item to disk and enqueue for live consumer."""
        with open(self._file, "a", encoding="utf-8") as f:
            f.write(json.dumps(item) + "\n")
        await self._queue.put(item)

    async def get(self) -> Any:
        """Get next item (live consumer path)."""
        item = await self._queue.get()
        if item is self._SENTINEL:
            raise StopAsyncIteration
        return item

    async def close(self) -> None:
        """Mark stream as done."""
        self._closed = True
        with open(self._file, "a", encoding="utf-8") as f:
            f.write(json.dumps({"__done__": True}) + "\n")
        await self._queue.put(self._SENTINEL)


def file_stream_factory(task_id: str) -> FileStreamHandler:
    """Factory for creating file-backed stream handlers."""
    return FileStreamHandler(task_id)


# ── Research stages ───────────────────────────────────────────────────────────
# A realistic deep-research pipeline — each stage is a distinct step that
# naturally takes time (LLM call + processing delay).

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

STAGE_DURATION = int(os.environ.get("STAGE_DURATION", "5"))


# ── The durable task ──────────────────────────────────────────────────────────

@durable_task(name="deep_research", stream_handler_factory=file_stream_factory)
async def deep_research(ctx: TaskContext[dict]) -> dict[str, Any]:
    """Long-running deep research task that survives crashes.

    Runs through 12 distinct research stages, each making an LLM call.
    On crash recovery, resumes from the last checkpointed stage.
    Can be cancelled early via the cancel invocation handler.
    """
    topic: str = ctx.input["topic"]
    completed: int = ctx.metadata.get("completed_stages", 0)
    results: list = ctx.metadata.get("results", [])
    total = len(STAGES)

    if ctx.entry_mode == "recovered":
        logger.warning("⚡ Recovered! Resuming from stage %d/%d", completed + 1, total)
        await ctx.stream(json.dumps({
            "type": "token",
            "content": f"\n\n⚡ **Recovered from crash!** Resuming from stage {completed + 1}/{total}...\n\n",
        }))

    for stage_idx in range(completed, total):
        # Check for cancellation
        if ctx.cancel.is_set():
            await ctx.stream(json.dumps({
                "type": "token",
                "content": "\n\n---\n🛑 **Research cancelled.**\n",
            }))
            return {"topic": topic, "stages_completed": stage_idx, "cancelled": True}

        stage = STAGES[stage_idx]

        # Announce stage
        await ctx.stream(json.dumps({
            "type": "token",
            "content": f"\n\n**[Stage {stage_idx + 1}/{total}]** {stage}...\n",
        }))

        # Do the work — streaming LLM tokens
        result = await _run_stage_streaming(ctx, topic, stage, prior_results=results[-3:])
        results.append({"stage": stage, "result": result})

        # ── CHECKPOINT ── crash-recovery boundary ─────
        ctx.metadata["completed_stages"] = stage_idx + 1
        ctx.metadata["results"] = results
        await ctx.metadata.flush()

        await ctx.stream(json.dumps({
            "type": "token",
            "content": f"\n✅ Stage {stage_idx + 1}/{total} complete.\n",
        }))

    # Done!
    await ctx.stream(json.dumps({
        "type": "token",
        "content": "\n\n---\n✅ **Research complete!**\n",
    }))
    return {
        "topic": topic,
        "report": results[-1]["result"] if results else "",
        "stages_completed": total,
    }


# ── LLM helpers ───────────────────────────────────────────────────────────────

async def _run_stage_streaming(
    ctx: TaskContext, topic: str, stage: str, *, prior_results: list
) -> str:
    """Call the LLM for one research stage, streaming tokens to the consumer."""
    await asyncio.sleep(STAGE_DURATION)

    if prior_results:
        findings = "\n".join(f"- {r['stage']}: {r['result'][:80]}" for r in prior_results[-3:])
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
    input_text = f"Research topic: {topic}"

    # Stream tokens from the LLM
    full_text = ""
    async for event in await _openai_client.responses.create(
        model=_model,
        instructions=instructions,
        input=input_text,
        store=False,
        stream=True,
    ):
        if event.type == "response.output_text.delta":
            full_text += event.delta
            await ctx.stream(json.dumps({"type": "token", "content": event.delta}))

    return full_text
