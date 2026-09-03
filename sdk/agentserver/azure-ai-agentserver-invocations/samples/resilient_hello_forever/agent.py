"""Minimal *indefinite* resilient long-running agent (invocations protocol).

Where ``resilient_hello_world`` runs a fixed number of steps and finishes, this
sample **never finishes on its own** — it is a durable background worker that
ticks forever until it is cancelled, surviving crashes and redeploys.

The differences from the finite sample are exactly the three things an infinite
loop needs to be a well-behaved LRA:

1. ``while True`` instead of a bounded ``for`` — it always has more work.
2. **Graceful shutdown**: on redeploy / SIGTERM the framework sets
   ``ctx.shutdown``; the loop calls ``return await ctx.exit_for_recovery()`` to
   release the lease cleanly so the next instance re-enters and continues.
3. **A stop path**: an explicit cancel writes a durable *stop marker* to the
   checkpoint store; the loop checks that marker every iteration and returns
   terminally, so the worker can actually be stopped on demand — even when the
   cancel request lands on a different replica than the one running the loop.

It also sets ``timeout=timedelta(days=7)`` — the maximum per-turn budget. The
framework's per-turn watchdog is *cooperative*: when the budget is reached it
only sets ``ctx.timeout_exceeded``/``ctx.cancel``; it does not forcibly end the
turn. This loop deliberately does not treat that as a stop, so it simply keeps
ticking. Re-entry with ``ctx.entry_mode == "recovered"`` happens on **crash** or
**redeploy** (via ``exit_for_recovery`` on ``ctx.shutdown``), and the worker
resumes from its checkpointed iteration. Raising the budget to the 7-day maximum
just avoids noisy watchdog signals for a task that is meant to run indefinitely.

Progress (the ``iterations`` cursor) is checkpointed to a durable, session-scoped
state store (``FoundryStateStore``, which uses a local on-disk backend when
running outside Foundry — so no Azure resources are required to run this locally).

Input schema: ``{"name": str}``. The host also injects the invocation's
``session_id`` into the durable input so the checkpoint store is isolated per
session (see ``checkpoint_store_name``).

Environment:

- ``TICK_SECONDS`` — seconds between iterations (default ``2``).
"""

from __future__ import annotations

import asyncio
import logging
import os
from datetime import timedelta
from typing import Any

from azure.ai.agentserver.core.storage import FoundryStateStore
from azure.ai.agentserver.core.tasks import TaskContext, task

logger = logging.getLogger(__name__)

_TICK = float(os.environ.get("TICK_SECONDS", "2"))


def checkpoint_store_name(session_id: str) -> str:
    """Return the **session-isolated** checkpoint store name.

    ``FoundryStateStore`` is agent-scoped and has no built-in per-session
    isolation, so the store is namespaced by the invocation's session id (as the
    other resilient samples do). This keeps one session's worker from being read
    or stopped by another — important because POST accepts a caller-supplied
    invocation id that a different session could otherwise reuse as a key. Shared
    with app.py so the poll/cancel endpoints read the same scope.
    """
    return f"resilient-hello-forever/{session_id}"


# Suffix for the durable "stop" marker key. The cancel endpoint (app.py) writes
# this key; the worker checks it to decide whether to stop. Keeping it in a
# SEPARATE key means the cancel write never races the checkpoint's ETag.
STOP_SUFFIX = "/stop"


@task(name="hello_forever", timeout=timedelta(days=7))
async def hello_forever(ctx: TaskContext[dict]) -> dict[str, Any]:
    """Tick forever, checkpointing the ``iterations`` cursor after each tick.

    Runs until an explicit cancel. Survives crashes (resumes from the checkpoint)
    and redeploys (yields cleanly via ``exit_for_recovery`` and resumes on the
    next instance).
    """

    name = str((ctx.input or {}).get("name", "world"))
    # ``session_id`` is carried in the durable input so recovery re-enters with
    # the same store scope as the original run.
    session_id = str((ctx.input or {}).get("session_id", ""))
    stop_key = f"{ctx.task_id}{STOP_SUFFIX}"

    # item_ttl_seconds=-1 => items never expire. An indefinite worker may run (or
    # be stopped and later polled) far past the 30-day default item TTL; letting
    # the checkpoint or stop marker expire would drop the recovery cursor and make
    # a stopped worker read back as "not_found". The TTL is fixed at store
    # creation, so every get_or_create for this store passes the same value.
    store = await FoundryStateStore.get_or_create(
        checkpoint_store_name(session_id), item_ttl_seconds=-1
    )
    try:
        item = await store.get_item(ctx.task_id)
        n = int((item.value.get("iterations", 0) if item else 0) or 0)
        etag = item.etag if item else None

        if ctx.entry_mode == "recovered":
            logger.warning("Recovered '%s' at iteration %d", name, n)

        while True:
            # 1) Graceful redeploy / SIGTERM: release the lease so the recovery
            #    scan re-enters this worker on the next instance and it continues.
            if ctx.shutdown.is_set():
                logger.info("shutdown — yielding for recovery at iteration %d", n)
                return await ctx.exit_for_recovery()

            # 2) Explicit stop. The DURABLE stop marker is the single source of
            #    truth and is checked EVERY iteration, independently of
            #    ``ctx.cancel``. A cancel routed to a *different* replica cannot
            #    set this process's ``ctx.cancel`` event, but it writes the marker
            #    — so the replica that actually owns the run still observes it here
            #    and stops. (On the owning replica, ``run.cancel()`` additionally
            #    wakes the tick sleep below so the stop is noticed within a tick
            #    rather than after a full interval.) The marker also survives the
            #    per-turn watchdog and crash/recovery, so it never races the
            #    checkpoint's ETag.
            if await store.get_item(stop_key) is not None:
                logger.info("stop requested — stopping at iteration %d", n)
                return {"name": name, "iterations": n, "stopped": True}

            # 3) One unit of ongoing work, then CHECKPOINT the durable cursor.
            n += 1
            logger.info("iteration %d for %s", n, name)
            ref = await store.set_item(
                ctx.task_id, {"name": name, "iterations": n}, if_match=etag
            )
            etag = ref.etag

            await asyncio.sleep(_TICK)  # heartbeat / interval between ticks; the
            # stop marker is re-checked at the top of every iteration, so an
            # explicit stop is honoured within one tick regardless of which replica
            # received the cancel.
    finally:
        await store.aclose()


__all__ = ["hello_forever", "checkpoint_store_name", "STOP_SUFFIX"]
