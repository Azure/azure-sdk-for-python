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
import hashlib
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


def durable_task_id(session_id: str, invocation_id: str, user_id: str) -> str:
    """Return the TaskManager task id derived from the user, session and invocation.

    The invocations protocol accepts a *caller-supplied* invocation id, and a
    single agent session can serve multiple users, so the invocation id alone (or
    even session+invocation) is not a safe identity: two users — or two sessions —
    reusing an id would collide on the TaskManager record and let one caller poll
    or cancel another's worker. Composing the id from ``user_id`` + ``session_id``
    + ``invocation_id`` keeps every start/poll/cancel path isolated. It is also
    used as the durable checkpoint item key (and thus the prefix of the
    stop-marker key).

    A SHA-256 digest is used (rather than ``f"{user}/{session}/{invocation}"``)
    for two reasons: the provider task-id contract is ``[A-Za-z0-9_-]{1,128}``
    (a ``/`` — and ``.`` or ``:`` — is rejected), and it is bounded to 128
    characters. The hex digest plus the ``hf-`` prefix uses only ``[a-z0-9-]``
    and is a fixed 67 chars, so it is always valid regardless of how long the
    protocol ids are. The ``\\x00`` separators keep the three fields unambiguous.
    """
    digest = hashlib.sha256(
        f"{user_id}\x00{session_id}\x00{invocation_id}".encode("utf-8")
    ).hexdigest()
    return f"hf-{digest}"


async def open_checkpoint_store(session_id: str, user_id: str) -> FoundryStateStore:
    """Open the session-scoped, **user-isolated**, non-expiring checkpoint store.

    A single agent session can serve multiple users, so on top of the
    session-scoped store name the store is created with ``user_isolation=True``
    and the explicit ``user_id`` — the platform partitions items per user, so one
    user cannot read or stop another's worker even within the same session.
    ``item_ttl_seconds=-1`` keeps the checkpoint and stop marker from expiring for
    an indefinitely-running worker. Every start/poll/cancel/recover path opens it
    the same way (and the worker carries ``user_id`` in its durable input so
    recovery reopens the same partition).
    """
    return await FoundryStateStore.get_or_create(
        checkpoint_store_name(session_id),
        user_isolation=True,
        user_id=user_id or None,
        item_ttl_seconds=-1,
    )


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
    # ``session_id`` and ``user_id`` are carried in the durable input so recovery
    # re-enters with the same store scope / user partition as the original run.
    session_id = str((ctx.input or {}).get("session_id", ""))
    user_id = str((ctx.input or {}).get("user_id", ""))
    stop_key = f"{ctx.task_id}{STOP_SUFFIX}"

    store = await open_checkpoint_store(session_id, user_id)
    try:
        item = await store.get_item(ctx.task_id)
        n = int((item.value.get("iterations", 0) if item else 0) or 0)
        etag = item.etag if item else None

        if ctx.entry_mode == "recovered":
            logger.warning("Recovered '%s' at iteration %d", name, n)

        try:
            while True:
                # 1) Graceful redeploy / SIGTERM: release the lease so the
                #    recovery scan re-enters this worker on the next instance.
                if ctx.shutdown.is_set():
                    logger.info(
                        "shutdown — yielding for recovery at iteration %d", n
                    )
                    return await ctx.exit_for_recovery()

                # 2) Explicit stop. The DURABLE stop marker is the single source
                #    of truth and is checked EVERY iteration. The cancel endpoint
                #    writes the marker (it does NOT rely on an in-process signal),
                #    so a stop is observed here regardless of which replica
                #    received the cancel request. The marker also survives the
                #    per-turn watchdog and crash/recovery, so it never races the
                #    checkpoint's ETag.
                if await store.get_item(stop_key) is not None:
                    logger.info("stop requested — stopping at iteration %d", n)
                    return {"name": name, "iterations": n, "stopped": True}

                # 3) One unit of ongoing work, then CHECKPOINT the durable cursor.
                n += 1
                logger.info("iteration %d for %s", n, name)
                ref = await store.set_item(
                    ctx.task_id,
                    {"name": name, "iterations": n, "status": "running"},
                    if_match=etag,
                )
                etag = ref.etag

                await asyncio.sleep(_TICK)  # heartbeat / interval between ticks;
                # the stop marker is re-checked at the top of every iteration, so
                # an explicit stop is honoured within one tick regardless of which
                # replica received the cancel.
        except Exception as exc:  # noqa: BLE001 — record failure, then re-raise
            # A raised exception is terminal (the one-shot record is deleted), so
            # without this the durable checkpoint would keep reporting ``running``
            # forever. Best-effort write of a terminal ``failed`` status; if the
            # ETag moved we still re-raise so the framework marks the task failed.
            logger.exception("hello_forever failed for %s", name)
            try:
                current = await store.get_item(ctx.task_id)
                await store.set_item(
                    ctx.task_id,
                    {
                        "name": name,
                        "iterations": n,
                        "status": "failed",
                        "error": str(exc),
                    },
                    if_match=current.etag if current else None,
                )
            except Exception:  # noqa: BLE001 — never mask the original failure
                logger.warning("could not persist failed status for %s", name)
            raise
    finally:
        await store.aclose()


__all__ = [
    "hello_forever",
    "checkpoint_store_name",
    "durable_task_id",
    "open_checkpoint_store",
    "STOP_SUFFIX",
]
