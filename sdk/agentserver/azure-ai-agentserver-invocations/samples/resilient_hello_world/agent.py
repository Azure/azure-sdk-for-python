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

Input schema: ``{"name": str, "steps": int?}``. The host also injects the
invocation's ``session_id`` into the durable input so the checkpoint store is
isolated per session (see ``checkpoint_store_name``).

Environment:

- ``STEP_DELAY`` — seconds to sleep between steps (default ``2``). Keep it
  nonzero so a crash demo has time to land mid-run.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import os
from typing import Any

from azure.ai.agentserver.core.storage import FoundryStateStore
from azure.ai.agentserver.core.tasks import TaskContext, task

logger = logging.getLogger(__name__)

_STEP_DELAY = float(os.environ.get("STEP_DELAY", "2"))


def checkpoint_store_name(session_id: str) -> str:
    """Return the **session-isolated** checkpoint store name.

    ``FoundryStateStore`` is agent-scoped and has no built-in per-session
    isolation, so the store is namespaced by the invocation's session id (as the
    other resilient samples do). This keeps one session's progress from being
    read or overwritten by another — important because POST accepts a
    caller-supplied invocation id that a different session could otherwise reuse
    as a key. Shared with app.py so the poll endpoint reads the same scope.
    """
    return f"resilient-hello-world/{session_id}"


def durable_task_id(session_id: str, invocation_id: str) -> str:
    """Return the TaskManager task id derived from BOTH ids.

    The invocations protocol accepts a *caller-supplied* invocation id, so the
    same id can appear in two different sessions. The TaskManager record is keyed
    only by task id, so keying it on the invocation id alone would let the second
    session collide with the first on ``start()`` (a 500) and let
    ``get_active_run(invocation_id)`` resolve the wrong session's run. Composing
    the id with the session keeps every start/poll/cancel path isolated. It is
    also used as the durable checkpoint item key.

    A SHA-256 digest is used (rather than ``f"{session_id}/{invocation_id}"``)
    for two reasons: task ids may only contain ``[a-zA-Z0-9\\-_.:]`` (a ``/`` is
    rejected), and they are bounded to 128 characters — a digest is a fixed,
    collision-resistant, always-valid encoding regardless of how long the two
    protocol ids are. The ``\\x00`` separator keeps ``(a, bc)`` and ``(ab, c)``
    distinct.
    """
    digest = hashlib.sha256(
        f"{session_id}\x00{invocation_id}".encode("utf-8")
    ).hexdigest()
    return f"hw-{digest}"


@task(name="hello_world")
async def hello_world(ctx: TaskContext[dict]) -> dict[str, Any]:
    """Count through ``steps`` steps, checkpointing after each one.

    The checkpoint (``completed_steps``) lives in a durable, session-scoped state
    store keyed by ``ctx.task_id``, so a crash mid-run resumes from the next step.
    """

    data = ctx.input or {}
    name = str(data.get("name", "world"))
    steps = int(data.get("steps", 10))
    # ``session_id`` is carried in the durable input so recovery re-enters with
    # the same store scope as the original run.
    session_id = str(data.get("session_id", ""))

    store = await FoundryStateStore.get_or_create(checkpoint_store_name(session_id))
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


__all__ = ["hello_world", "checkpoint_store_name", "durable_task_id"]
