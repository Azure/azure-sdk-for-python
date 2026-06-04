"""Durable long-running research agent (invocations protocol).

A long-running deep-research task that survives container crashes:

- The decorated handler runs 12 research stages, each an LLM call.
- Progress is checkpointed to ``ctx.metadata`` after every stage and
  flushed durably with ``await ctx.metadata.flush()``.
- On crash recovery, ``ctx.entry_mode == "recovered"`` triggers a
  resume-from-checkpoint that picks up at the next un-completed stage.
- The handler streams incremental tokens to consumers via the SDK
  ``streams`` registry — per-turn ``invocation_id`` is the stream id
  (per streaming.md §7.8). The HTTP layer attaches the SSE
  subscriber BEFORE invoking the task (subscribe-before-start
  discipline per §5.1) so the live multi-subscriber Broadcast
  backing is safe.

This is the peer-sample-shape distillation of the larger
``samples/durable-agent-demo/src/durable-research-agent`` reference
demo. The reference demo includes a supervisor / entrypoint
scaffolding (the runtime the hosting platform spawns); this sample
strips all of that away and ships only the three files every
invocations sample ships: ``agent.py``, ``app.py``, and
``requirements.txt``. The reference demo remains in tree for users
who want to see the full hosting layout.

Input schema: ``{"topic": str}``

Environment:

- ``FOUNDRY_PROJECT_ENDPOINT`` — Azure AI Foundry project endpoint.
- ``AZURE_AI_MODEL_DEPLOYMENT_NAME`` — model deployment name
  (default: ``gpt-4.1-mini``).
- ``STAGE_DURATION`` — artificial inter-stage delay in seconds
  (default: ``5``). Keep nonzero so a crash demo has time to bite.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any

from azure.ai.agentserver.core.durable import TaskContext, task
from azure.ai.agentserver.core.streaming import streams

logger = logging.getLogger(__name__)

# ── Azure AI client setup ────────────────────────────────────────────────

_endpoint = os.environ.get("FOUNDRY_PROJECT_ENDPOINT")
_model = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4.1-mini")
_STAGE_DURATION = int(os.environ.get("STAGE_DURATION", "5"))

_openai_client: Any = None


def _get_client() -> Any:
    """Lazy Azure AI client construction — kept out of import-time so the
    sample can be imported in test/static analysis contexts that don't
    have an Azure endpoint configured."""

    global _openai_client  # pylint: disable=global-statement
    if _openai_client is not None:
        return _openai_client
    if not _endpoint:
        raise EnvironmentError(
            "FOUNDRY_PROJECT_ENDPOINT is required to run the deep-research sample."
        )
    from azure.ai.projects.aio import (  # pylint: disable=import-outside-toplevel
        AIProjectClient,
    )
    from azure.identity.aio import (  # pylint: disable=import-outside-toplevel
        DefaultAzureCredential,
    )

    project = AIProjectClient(
        endpoint=_endpoint,
        credential=DefaultAzureCredential(),
    )
    _openai_client = project.get_openai_client()
    return _openai_client


# ── Research stages ──────────────────────────────────────────────────────

STAGES: tuple[str, ...] = (
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
)


# ── The durable task ─────────────────────────────────────────────────────


@task(name="deep_research")
async def deep_research(ctx: TaskContext[dict]) -> dict[str, Any]:
    """Long-running deep research task that survives container crashes.

    Runs through ``len(STAGES)`` research stages, each an LLM call.
    Progress (``completed_stages`` watermark + accumulated ``results``)
    is checkpointed to ``ctx.metadata`` and flushed after each stage.
    On crash recovery, picks up at the next un-completed stage.

    Streaming: the handler reads its per-turn ``invocation_id`` from
    ``ctx.input`` (propagated by the HTTP layer) and emits to the SDK
    ``streams`` registry. The HTTP layer attaches the SSE subscriber
    BEFORE starting the task (subscribe-before-start discipline per
    streaming.md §5.1 + §7.8) so Broadcast is safe.
    """

    topic: str = ctx.input["topic"]
    inv_id: str = ctx.input["invocation_id"]
    stream = await streams.get_or_create(inv_id)
    completed: int = ctx.metadata.get("completed_stages", 0)
    results: list[dict[str, str]] = ctx.metadata.get("results", [])
    total = len(STAGES)

    if ctx.entry_mode == "recovered":
        logger.warning(
            "⚡ Recovered — resuming research at stage %d/%d", completed + 1, total
        )
        await stream.emit(
            {
                "type": "token",
                "content": (
                    f"\n\n⚡ **Recovered from crash.** Resuming from "
                    f"stage {completed + 1}/{total}.\n\n"
                ),
            }
        )

    for stage_idx in range(completed, total):
        if ctx.cancel.is_set():
            await stream.emit(
                {"type": "token", "content": "\n\n---\n🛑 **Research cancelled.**\n"},
                close=True,
            )
            return {"topic": topic, "stages_completed": stage_idx, "cancelled": True}

        stage = STAGES[stage_idx]
        await stream.emit(
            {
                "type": "token",
                "content": f"\n\n**[Stage {stage_idx + 1}/{total}]** {stage}…\n",
            }
        )

        result = await _run_stage_streaming(
            stream, topic, stage, prior_results=results[-3:], stage_idx=stage_idx
        )
        results.append({"stage": stage, "result": result})

        # ── CHECKPOINT — crash-recovery boundary ──────────────────
        ctx.metadata["completed_stages"] = stage_idx + 1
        ctx.metadata["results"] = results
        await ctx.metadata.flush()

        await stream.emit(
            {
                "type": "token",
                "content": f"\n✅ Stage {stage_idx + 1}/{total} complete.\n",
            }
        )

    await stream.emit(
        {"type": "token", "content": "\n\n---\n✅ **Research complete.**\n"},
        close=True,
    )
    return {
        "topic": topic,
        "report": results[-1]["result"] if results else "",
        "stages_completed": total,
    }


# ── LLM helper ───────────────────────────────────────────────────────────


async def _run_stage_streaming(
    stream: Any,
    topic: str,
    stage: str,
    *,
    prior_results: list[dict[str, str]],
    stage_idx: int = 0,
) -> str:
    """Run one research stage; stream tokens incrementally to the consumer."""

    if stage_idx > 0:
        await asyncio.sleep(_STAGE_DURATION)

    if prior_results:
        findings = "\n".join(
            f"- {r['stage']}: {r['result'][:80]}" for r in prior_results[-3:]
        )
        instructions = (
            f"You are a research assistant performing: '{stage}'. "
            f"Build on these prior findings:\n{findings}\n\n"
            "Provide 3-4 sentences of new, specific, detailed findings. "
            "Be informative."
        )
    else:
        instructions = (
            f"You are a research assistant performing: '{stage}'. "
            "Provide 3-4 sentences of specific, detailed findings. "
            "Be informative and engaging."
        )

    client = _get_client()
    full_text = ""
    async for event in await client.responses.create(
        model=_model,
        instructions=instructions,
        input=f"Research topic: {topic}",
        store=False,
        stream=True,
    ):
        if event.type == "response.output_text.delta":
            full_text += event.delta
            await stream.emit({"type": "token", "content": event.delta})
    return full_text


__all__ = ["deep_research", "STAGES"]


def to_sse(chunk: Any) -> bytes:
    """Encode a stream chunk as an SSE ``data:`` line."""

    return f"data: {json.dumps(chunk)}\n\n".encode("utf-8")
