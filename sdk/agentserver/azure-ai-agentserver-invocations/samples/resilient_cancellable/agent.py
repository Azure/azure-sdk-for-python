"""Minimal resilient long-running agent showcasing **cooperative cancellation**.

Where ``resilient_hello_world`` runs to completion and ``resilient_hello_forever``
runs until it is stopped, this sample sits in between: a **finite** job that
*would* finish on its own but can be **cancelled mid-run**. It is the smallest
end-to-end illustration of the cancel flow for a durable long-running agent.

It depends on ONLY ``azure-ai-agentserver-core`` and
``azure-ai-agentserver-invocations`` — no LLM, no cloud — and checkpoints its
progress after every step to a durable state store (``FoundryStateStore``, which
uses a local on-disk backend outside Foundry, so no Azure resources are needed
locally).

How cancel works (the important bit):

- The cancel endpoint (``app.py``) writes a durable **cancel marker** to a
  separate state-store key. It does NOT rely on an in-process signal.
- Before each step, the task reads that marker. If present, it stops early,
  records ``status: "cancelled"`` in its checkpoint, and returns.

Using a durable marker (rather than the in-process ``ctx.cancel`` event) makes
cancellation correct even when the cancel request lands on a *different* replica
than the one running the task, and it survives a crash/redeploy: a task recovered
after a cancel was requested still sees the marker and stops. Keeping the marker
in its own key means the cancel write never races the checkpoint's ETag.

Input schema: ``{"name": str, "steps": int?}``. The host also injects the
invocation's ``session_id``/``user_id``/``call_id`` into the durable input so
recovery reopens the same user-isolated store partition and Foundry call identity.

Environment:

- ``STEP_DELAY`` — seconds to sleep between steps (default ``2``). Keep it
  nonzero so a cancel (or crash) demo has time to land mid-run.
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

# Suffix for the durable "cancel" marker key. The cancel endpoint (app.py) writes
# this key; the task checks it before each step to decide whether to stop early.
# Keeping it in a SEPARATE key means the cancel write never races the
# checkpoint's ETag.
CANCEL_SUFFIX = "/cancel"


def checkpoint_store_name(session_id: str) -> str:
    """Return the **session-isolated** checkpoint store name.

    ``FoundryStateStore`` is agent-scoped and has no built-in per-session
    isolation, so the store is namespaced by the invocation's session id (as the
    other resilient samples do). Shared with app.py so the poll/cancel endpoints
    read the same scope.

    The session component is **hashed**: a protocol session id can be up to 256
    characters, and the local ``FoundryStateStore`` backend base64-encodes the
    whole store name into a single filename, which would blow past the 255-byte
    ``NAME_MAX`` and fail this no-cloud sample with ``ENAMETOOLONG``. A fixed-width
    SHA-256 digest keeps the name bounded while remaining unique per session.
    """
    digest = hashlib.sha256(session_id.encode("utf-8")).hexdigest()
    return f"resilient-cancellable/{digest}"


def durable_task_id(session_id: str, invocation_id: str, user_id: str) -> str:
    """Return the TaskManager task id derived from the user, session and invocation.

    The invocations protocol accepts a *caller-supplied* invocation id, and a
    single agent session can serve multiple users, so the invocation id alone is
    not a safe identity: two users — or two sessions — reusing an id would collide
    on the TaskManager record and let one caller poll or cancel another's job.
    Composing the id from ``user_id`` + ``session_id`` + ``invocation_id`` keeps
    every start/poll/cancel path isolated. It is also used as the durable
    checkpoint item key (and thus the prefix of the cancel-marker key).

    A SHA-256 digest is used (rather than ``f"{user}/{session}/{invocation}"``)
    because the provider task-id contract is ``[A-Za-z0-9_-]{1,128}`` (a ``/`` —
    and ``.`` or ``:`` — is rejected) and bounded to 128 characters. The hex
    digest plus the ``cj-`` prefix uses only ``[a-z0-9-]`` and is a fixed 67
    chars, so it is always valid regardless of how long the protocol ids are. The
    ``\\x00`` separators keep the three fields unambiguous.
    """
    digest = hashlib.sha256(
        f"{user_id}\x00{session_id}\x00{invocation_id}".encode("utf-8")
    ).hexdigest()
    return f"cj-{digest}"


async def open_checkpoint_store(session_id: str, user_id: str) -> FoundryStateStore:
    """Open the session-scoped, **user-isolated** checkpoint store.

    A single agent session can serve multiple users, so on top of the
    session-scoped store name the store is created with ``user_isolation=True``
    and the explicit ``user_id`` — the platform partitions items per user, so one
    user cannot read or cancel another's job even within the same session. Every
    start/poll/cancel/recover path opens it the same way (and the task carries
    ``user_id`` in its durable input so recovery reopens the same partition).
    """
    return await FoundryStateStore.get_or_create(
        checkpoint_store_name(session_id),
        user_isolation=True,
        user_id=user_id or None,
    )


@task(name="cancellable_job")
async def cancellable_job(ctx: TaskContext[dict]) -> dict[str, Any]:
    """Run ``steps`` steps, checkpointing each, but stop early if cancelled.

    Before every step the task reads the durable cancel marker; if it is present
    the task records ``status: "cancelled"`` and returns without finishing the
    remaining steps. A crash mid-run resumes from the next step (and still honours
    a cancel requested before the crash).
    """

    data = ctx.input or {}
    name = str(data.get("name", "world"))
    steps = int(data.get("steps", 10))
    # session_id/user_id are carried in the durable input so recovery re-enters
    # with the same store scope / user partition as the original run.
    session_id = str(data.get("session_id", ""))
    user_id = str(data.get("user_id", ""))
    cancel_key = f"{ctx.task_id}{CANCEL_SUFFIX}"

    store = await open_checkpoint_store(session_id, user_id)
    try:
        item = await store.get_item(ctx.task_id)
        completed = int((item.value.get("completed_steps", 0) if item else 0) or 0)
        status_at_entry = item.value.get("status") if item else None
        etag = item.etag if item else None

        if ctx.entry_mode == "recovered":
            logger.warning(
                "Recovered — resuming '%s' at step %d/%d", name, completed + 1, steps
            )

        # Already finalized (recovered after a terminal write): nothing to do.
        if status_at_entry in ("completed", "cancelled"):
            return {
                "name": name,
                "steps": steps,
                "completed_steps": completed,
                "status": status_at_entry,
            }

        try:
            done = completed
            for i in range(completed, steps):
                # ── COOPERATIVE CANCEL CHECK ──
                # Durable + cross-replica-safe + crash-durable. Checked BEFORE the
                # work so a cancel takes effect within one step interval.
                if await store.get_item(cancel_key) is not None:
                    logger.info(
                        "cancelled — stopping '%s' at step %d/%d", name, i, steps
                    )
                    await store.set_item(
                        ctx.task_id,
                        {
                            "name": name,
                            "steps": steps,
                            "completed_steps": i,
                            "status": "cancelled",
                        },
                        if_match=etag,
                    )
                    return {
                        "name": name,
                        "steps": steps,
                        "completed_steps": i,
                        "status": "cancelled",
                    }

                await asyncio.sleep(_STEP_DELAY)  # stand-in for long-running work
                logger.info("step %d/%d done for %s", i + 1, steps, name)

                # ── CHECKPOINT — the durable crash-recovery boundary ──
                ref = await store.set_item(
                    ctx.task_id,
                    {
                        "name": name,
                        "steps": steps,
                        "completed_steps": i + 1,
                        "status": "in_progress",
                    },
                    if_match=etag,
                )
                etag = ref.etag
                done = i + 1  # advance so a later failure records real progress

            logger.info("Finished %d steps for %s", steps, name)
            # ── TERMINAL SUCCESS ──
            # The one-shot task record is deleted on terminal exit, so the poll
            # endpoint has only this durable item to read. Persist an explicit
            # terminal status so a finished (or cancelled/failed) run is never
            # reported as ``in_progress`` forever.
            await store.set_item(
                ctx.task_id,
                {
                    "name": name,
                    "steps": steps,
                    "completed_steps": steps,
                    "status": "completed",
                },
                if_match=etag,
            )
            return {"name": name, "steps": steps, "status": "completed"}
        except Exception as exc:  # noqa: BLE001 — record failure, then re-raise
            # Record the *actual* progress (``done``, advanced after each
            # successful checkpoint) so failure never rolls ``completed_steps``
            # backward to the entry-time value.
            logger.exception("cancellable_job failed for %s", name)
            try:
                # Keep THIS execution's last-owned ETag. Re-reading the latest
                # ETag would defeat the checkpoint CAS: if we lost a race to a
                # recovered/new owner, our stale ``done`` must NOT clobber the
                # winner's newer progress — the if_match then fails and we skip
                # the failure write.
                await store.set_item(
                    ctx.task_id,
                    {
                        "name": name,
                        "steps": steps,
                        "completed_steps": done,
                        "status": "failed",
                        "error": str(exc),
                    },
                    if_match=etag,
                )
            except Exception:  # noqa: BLE001 — never mask the original failure
                logger.warning("could not persist failed status for %s", name)
            raise
    finally:
        await store.aclose()


__all__ = [
    "cancellable_job",
    "checkpoint_store_name",
    "durable_task_id",
    "open_checkpoint_store",
    "CANCEL_SUFFIX",
]
