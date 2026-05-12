# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Lease identity derivation and renewal loop for durable tasks.

Provides utility functions for constructing stable lease owner strings,
generating ephemeral instance IDs, and running the background lease
renewal loop.
"""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import logging
import os
import time
import uuid

from ._models import TaskPatchRequest
from ._provider import DurableTaskProvider

logger = logging.getLogger("azure.ai.agentserver.durable")


def derive_lease_owner(session_id: str) -> str:
    """Derive a stable lease owner string from the session ID.

    The owner is stable across process restarts within the same session,
    enabling dual-identity lease reclamation.

    :param session_id: The agent session identifier.
    :type session_id: str
    :return: A lease owner string in the format ``"session:{session_id}"``.
    :rtype: str
    """
    return f"session:{session_id}"


def generate_instance_id() -> str:
    """Generate an ephemeral lease instance ID unique to this process.

    Combines the PID and a timestamp to ensure uniqueness even after
    rapid restarts.

    :return: A unique instance identifier.
    :rtype: str
    """
    return f"worker-{os.getpid()}-{uuid.uuid4().hex[:8]}-{int(time.time())}"


async def lease_renewal_loop(
    provider: DurableTaskProvider,
    task_id: str,
    *,
    lease_owner: str,
    lease_instance_id: str,
    lease_duration_seconds: int,
    cancel_event: asyncio.Event,
    on_failure_count: int = 3,
    on_cancel_callback: asyncio.Event | None = None,
) -> None:
    """Run a background lease renewal loop at half the lease duration.

    Renews the lease by PATCHing the task with the same owner/instance.
    On ``on_failure_count`` consecutive failures, signals the optional
    ``on_cancel_callback`` event to give the task function a chance to
    checkpoint.

    The loop exits when ``cancel_event`` is set or the task is cancelled.

    :param provider: The storage provider.
    :param task_id: The task to renew.
    :param lease_owner: The stable lease owner.
    :param lease_instance_id: The ephemeral instance ID.
    :param lease_duration_seconds: The lease TTL in seconds.
    :param cancel_event: Event that stops the loop when set.
    :param on_failure_count: Consecutive failures before signalling cancel.
    :param on_cancel_callback: Event to signal on repeated renewal failure.
    """
    interval = max(1, lease_duration_seconds // 2)
    consecutive_failures = 0

    while not cancel_event.is_set():
        try:
            await asyncio.wait_for(
                _wait_for_event(cancel_event),
                timeout=interval,
            )
            # cancel_event was set — exit the loop
            break
        except asyncio.TimeoutError:
            pass

        try:
            await provider.update(
                task_id,
                TaskPatchRequest(
                    lease_owner=lease_owner,
                    lease_instance_id=lease_instance_id,
                    lease_duration_seconds=lease_duration_seconds,
                ),
            )
            consecutive_failures = 0
            logger.debug("Lease renewed for task %s", task_id)
        except Exception:  # pylint: disable=broad-exception-caught
            consecutive_failures += 1
            logger.warning(
                "Lease renewal failed for task %s (attempt %d/%d)",
                task_id,
                consecutive_failures,
                on_failure_count,
                exc_info=True,
            )
            if consecutive_failures >= on_failure_count and on_cancel_callback is not None:
                logger.error(
                    "Lease renewal failed %d times for task %s — " "signalling cancellation",
                    on_failure_count,
                    task_id,
                )
                on_cancel_callback.set()
                break


async def _wait_for_event(event: asyncio.Event) -> None:
    """Await an asyncio event. Used with ``wait_for`` for interruptible sleep."""
    await event.wait()
