"""Minimal "hello world" resilient long-running agent (invocations protocol).

The smallest possible long-running agent (LRA): it depends on ONLY
``azure-ai-agentserver-core`` and ``azure-ai-agentserver-invocations`` — no LLM,
no streaming, no cloud services — so it runs with a minimal dependency and
memory footprint.

It counts through ``steps`` steps, sleeping between them to simulate slow work
that outlives a single request, and **checkpoints its progress after every
step** to a durable state store (``FoundryStateStore``, which uses a local
on-disk backend when running outside Foundry — so no Azure resources are
required to run this locally). If the container crashes mid-run, the platform
restarts it and the framework re-enters this task with
``ctx.entry_mode == "recovered"`` — the handler reads ``completed_steps`` from
the checkpoint and resumes at the next step instead of starting over.

Input schema: ``{"name": str, "steps": int?}``

Environment:

- ``STEP_DELAY`` — seconds to sleep between steps (default ``2``). Keep it
  nonzero so a crash demo has time to land mid-run.
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

from azure.ai.agentserver.core.storage import FoundryStateStore
from azure.ai.agentserver.core.tasks import TaskContext, task

logger = logging.getLogger(__name__)

_STEP_DELAY = float(os.environ.get("STEP_DELAY", "2"))

# The state store that holds each run's durable checkpoint. Shared with app.py
# so the poll endpoint can read the same progress.
CHECKPOINT_STORE = "hello_world_checkpoints"


@task(name="hello_world")
async def hello_world(ctx: TaskContext[dict]) -> dict[str, Any]:
    """Count through ``steps`` steps, checkpointing after each one.

    The checkpoint (``completed_steps``) lives in a durable state store keyed by
    ``ctx.task_id``, so a crash mid-run resumes from the next step.
    """

    data = ctx.input or {}
    name = str(data.get("name", "world"))
    steps = int(data.get("steps", 10))

    store = await FoundryStateStore.get_or_create(CHECKPOINT_STORE)
    try:
        item = await store.get_item(ctx.task_id)
        completed = int((item.value.get("completed_steps", 0) if item else 0) or 0)
        etag = item.etag if item else None

        if ctx.entry_mode == "recovered":
            logger.warning(
                "Recovered — resuming '%s' at step %d/%d", name, completed + 1, steps
            )

        for i in range(completed, steps):
            await asyncio.sleep(_STEP_DELAY)  # stand-in for real long-running work
            logger.info("step %d/%d done for %s", i + 1, steps, name)

            # ── CHECKPOINT — the durable crash-recovery boundary ──
            # After this write, a crash resumes at step (i + 2), not step 1.
            ref = await store.set_item(
                ctx.task_id,
                {"name": name, "steps": steps, "completed_steps": i + 1},
                if_match=etag,
            )
            etag = ref.etag

        logger.info("Finished %d steps for %s", steps, name)
        return {"name": name, "steps": steps, "status": "complete"}
    finally:
        await store.aclose()


__all__ = ["hello_world", "CHECKPOINT_STORE"]
