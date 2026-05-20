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
from typing import Any

from azure.ai.agentserver.core.durable import TaskContext, durable_task

logger = logging.getLogger(__name__)

# ── Research stages ───────────────────────────────────────────────────────────

STAGES = [
    "Analyzing topic and forming research questions",
    "Searching academic and authoritative sources",
    "Cross-referencing and validating findings",
    "Synthesizing insights from multiple sources",
    "Generating final report with key takeaways",
]

STAGE_DURATION = int(os.environ.get("STAGE_DURATION", "15"))


# ── The durable task ──────────────────────────────────────────────────────────

@durable_task(name="deep_research")
async def deep_research(ctx: TaskContext[dict]) -> dict[str, Any]:
    """Multi-stage research task that survives crashes.

    On crash recovery, ``ctx.metadata`` still has everything we saved —
    so we just skip the stages we already completed.
    """
    topic: str = ctx.input["topic"]
    completed: int = ctx.metadata.get("completed_stages", 0)
    results: list = ctx.metadata.get("results", [])

    if ctx.entry_mode == "recovered":
        logger.warning("⚡ Recovered! Resuming from stage %d/%d", completed + 1, len(STAGES))
        await ctx.stream(json.dumps({
            "type": "recovery",
            "message": f"⚡ Recovered from crash! Resuming from stage {completed + 1}/{len(STAGES)}",
        }))

    # Run remaining stages
    for i in range(completed, len(STAGES)):
        stage = STAGES[i]

        await ctx.stream(json.dumps({
            "type": "progress",
            "stage": i + 1,
            "total": len(STAGES),
            "message": f"[{i + 1}/{len(STAGES)}] {stage}...",
        }))

        # Do the work (LLM call + simulated delay)
        result = await _run_stage(topic, stage, is_final=(i == len(STAGES) - 1), prior_results=results)
        results.append({"stage": stage, "result": result})

        # ── CHECKPOINT ── this is the crash-recovery boundary ─────
        ctx.metadata["completed_stages"] = i + 1
        ctx.metadata["results"] = results
        await ctx.metadata.flush()

        await ctx.stream(json.dumps({
            "type": "stage_done",
            "stage": i + 1,
            "total": len(STAGES),
            "preview": result[:150],
        }))

    # Done!
    await ctx.stream(json.dumps({"type": "complete", "message": "✅ Research complete!"}))
    return {
        "topic": topic,
        "report": results[-1]["result"],
        "stages_completed": len(STAGES),
    }


# ── LLM helpers (swap these for your own logic) ──────────────────────────────

async def _run_stage(topic: str, stage: str, *, is_final: bool, prior_results: list) -> str:
    """Call the LLM for one research stage."""
    import app  # deferred import to avoid circular dependency

    client = app.get_openai_client()
    model = app.get_model()

    await asyncio.sleep(STAGE_DURATION)

    if is_final:
        findings = "\n".join(f"- {r['stage']}: {r['result']}" for r in prior_results)
        response = await client.responses.create(
            model=model,
            instructions="Compile these research findings into a concise summary with key insights.",
            input=f"Topic: {topic}\n\nFindings:\n{findings}",
            store=False,
        )
    else:
        response = await client.responses.create(
            model=model,
            instructions=f"You are a research assistant performing: '{stage}'. Provide 2-3 sentences of findings.",
            input=f"Research topic: {topic}",
            store=False,
        )

    return response.output_text
