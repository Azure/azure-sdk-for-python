# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Lease identity derivation and renewal loop for resilient tasks.

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
from collections.abc import Awaitable, Callable
from typing import Any

from ._models import TaskPatchRequest
from ._provider import TaskProvider
from ._client import TransportClassifiedError
from ._exceptions_internal import _HostedConflict, _translate_hosted_conflict

logger = logging.getLogger("azure.ai.agentserver.tasks")


def derive_lease_owner(agent_name: str, session_id: str) -> str:
    """Derive a stable lease owner string from the agent name and session ID.

    : the lease owner string MUST be derived from
        BOTH the agent name (from ``FOUNDRY_AGENT_NAME``) AND the session
        identifier — not from the session ID alone. Two different agents
        that happen to share a session ID (a misconfiguration or a future
        multi-agent platform topology) would otherwise collide on lease
        ownership and step on each other's tasks. The platform's
        ``binding_mismatch`` protection  covers split-brain on the
        same agent+session but is silent on this orthogonal case.

        The owner is stable across process restarts within the same
        ``(agent_name, session_id)`` pair, enabling dual-identity lease
        reclamation.

        On-the-wire format: ``"{agent_name}|session:{session_id}"``. Both
        components are recoverable from the string by splitting on the
        first ``"|"``; the format is chosen for operator readability in
        logs.

        :param agent_name: The agent name (resolved from
            ``FOUNDRY_AGENT_NAME``). Falls back to ``"unknown-agent"`` when
            the env var is unset — the caller decides whether to do the
            fallback or pass ``"unknown-agent"`` directly. The fallback
            string matches the rest of the framework's agent-name
            conventions so traces, logs, and lease ownership agree.
        :type agent_name: str
        :param session_id: The agent session identifier.
        :type session_id: str
        :return: A lease owner string containing both components in a
            stable, parseable format.
        :rtype: str
    """
    safe_agent = agent_name or "unknown-agent"
    return f"{safe_agent}|session:{session_id}"


def generate_instance_id() -> str:
    """Generate an ephemeral lease instance ID unique to this process.

    Combines the PID and a timestamp to ensure uniqueness even after
    rapid restarts.

    :return: A unique instance identifier.
    :rtype: str
    """
    return f"worker-{os.getpid()}-{uuid.uuid4().hex[:8]}-{int(time.time())}"


async def lease_renewal_loop(  # pylint: disable=too-many-statements
    provider: TaskProvider,
    task_id: str,
    *,
    lease_owner: str,
    lease_instance_id: str,
    lease_duration_seconds: int,
    cancel_event: asyncio.Event,
    on_failure_count: int = 3,
    on_cancel_callback: asyncio.Event | None = None,
    steering_poll_callback: Callable[[], Awaitable[None]] | None = None,
    last_refresh_provider: Callable[[], float] | None = None,
    update_via_queue: Callable[[str, "TaskPatchRequest"], Awaitable[Any]] | None = None,
) -> None:
    """Run a background lease renewal loop at half the lease duration.

        Renews the lease by PATCHing the task with the same owner/instance.
        On ``on_failure_count`` consecutive failures, signals the optional
        ``on_cancel_callback`` event to give the task function a chance to
        checkpoint.

        The loop exits when ``cancel_event`` is set or the task is cancelled.

        :param provider: The storage provider.
        :type provider: TaskProvider
        :param task_id: The task to renew.
        :type task_id: str
        :keyword lease_owner: The stable lease owner.
        :paramtype lease_owner: str
        :keyword lease_instance_id: The ephemeral instance ID.
        :paramtype lease_instance_id: str
        :keyword lease_duration_seconds: The lease TTL in seconds.
        :paramtype lease_duration_seconds: int
        :keyword cancel_event: Event that stops the loop when set.
        :paramtype cancel_event: asyncio.Event
        :keyword on_failure_count: Consecutive failures before signalling cancel.
        :paramtype on_failure_count: int
        :keyword on_cancel_callback: Event to signal on repeated renewal failure.
        :paramtype on_cancel_callback: asyncio.Event | None
        :keyword steering_poll_callback: Async callback invoked each renewal to poll
            for steering inputs. Called after successful lease renewal.
        :paramtype steering_poll_callback: Callable[[], Awaitable[None]] | None
        :keyword last_refresh_provider: Optional ``() -> float`` callable
            returning the ``asyncio.get_running_loop().time()`` value at the
            most-recent lease refresh (heartbeat OR side-effect refresh
            from a payload PATCH that piggybacked lease ownership via
            ``TaskManager._lease_ext_kwargs``). When provided, the loop
            skips the heartbeat for any tick whose due-time has been
            pushed past by a more-recent refresh, avoiding a redundant
            network round-trip. ``None`` preserves the legacy fixed-tick
            behaviour for tests.
        :paramtype last_refresh_provider: Callable[[], float] | None
    :keyword update_via_queue:   — optional callable
            through which the heartbeat PATCH MUST be issued so that it
            acquires the per-task write lock (and is etag-aware). When
            supplied, the loop uses this instead of ``provider.update``.
            When ``None``, falls back to the raw provider call (used by
            tests that don't construct a TaskManager).
        :paramtype update_via_queue: Callable[[str, TaskPatchRequest], Awaitable[Any]] | None
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

        # Every payload PATCH that piggybacks lease ownership
        # (TaskManager._lease_ext_kwargs) refreshes the lease as a
        # side effect. Skip a redundant heartbeat when a more-recent
        # refresh has happened within the last ``interval`` seconds.
        if last_refresh_provider is not None:
            try:
                last_refresh_t = float(last_refresh_provider())
            except Exception:  # pylint: disable=broad-exception-caught  # noqa: BLE001
                last_refresh_t = 0.0
            if last_refresh_t > 0.0:
                now_t = asyncio.get_running_loop().time()
                age = now_t - last_refresh_t
                if age < interval:
                    remaining = interval - age
                    try:
                        await asyncio.wait_for(
                            _wait_for_event(cancel_event),
                            timeout=remaining,
                        )
                        break  # cancel fired
                    except asyncio.TimeoutError:
                        continue  # re-check on the next iteration

        try:
            patch = TaskPatchRequest(
                lease_owner=lease_owner,
                lease_instance_id=lease_instance_id,
                lease_duration_seconds=lease_duration_seconds,
            )
            if update_via_queue is not None:
                await update_via_queue(task_id, patch)
            else:
                await provider.update(task_id, patch)
            consecutive_failures = 0
            logger.debug("Lease renewed for task %s", task_id)

            # Poll for steering inputs after successful renewal
            if steering_poll_callback is not None:
                try:
                    await steering_poll_callback()
                except Exception:  # pylint: disable=broad-exception-caught
                    logger.debug("Steering poll failed for task %s", task_id, exc_info=True)
        except _HostedConflict as exc:
            translated = _translate_hosted_conflict(exc, task_id=task_id)
            if translated is None or getattr(translated, "current_status", None) == "in_progress":
                if on_cancel_callback is not None:
                    logger.warning(
                        "Lease renewal lost ownership for task %s — cancelling local execution",
                        task_id,
                    )
                    on_cancel_callback.set()
                    break
            consecutive_failures += 1
            logger.warning(
                "Lease renewal failed for task %s (attempt %d/%d): %s",
                task_id,
                consecutive_failures,
                on_failure_count,
                translated,
                exc_info=True,
            )
            if consecutive_failures >= on_failure_count and on_cancel_callback is not None:
                logger.error(
                    "Lease renewal failed %d times for task %s — signalling cancellation",
                    on_failure_count,
                    task_id,
                )
                on_cancel_callback.set()
                break
        except TransportClassifiedError as exc:
            if getattr(exc, "classification", None) == "evicted" and on_cancel_callback is not None:
                #: orphan-sandbox eviction at the lease-renewal
                # site. Stop renewing immediately; signal the local cleanup
                # callback so _manager.py can cancel the local execution,
                # suppress any pending terminal write, and signal awaiters
                # with TaskConflictError. The local cleanup sequence is
                # atomic per Invariant 1 (no partial cleanup state observable).
                logger.warning(
                    "Lease renewal rejected with binding_mismatch for task %s "
                    "(orphan-sandbox eviction) — cancelling local execution",
                    task_id,
                )
                on_cancel_callback.set()
                break
            # Non-eviction classified errors fall through to the generic
            # failure-counter path (e.g. transient 503 → retry).
            consecutive_failures += 1
            logger.warning(
                "Lease renewal failed for task %s (attempt %d/%d): %s",
                task_id,
                consecutive_failures,
                on_failure_count,
                exc,
                exc_info=True,
            )
            if consecutive_failures >= on_failure_count and on_cancel_callback is not None:
                logger.error(
                    "Lease renewal failed %d times for task %s — signalling cancellation",
                    on_failure_count,
                    task_id,
                )
                on_cancel_callback.set()
                break
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
                    "Lease renewal failed %d times for task %s — signalling cancellation",
                    on_failure_count,
                    task_id,
                )
                on_cancel_callback.set()
                break


async def _wait_for_event(event: asyncio.Event) -> None:
    """Await an asyncio event. Used with ``wait_for`` for interruptible sleep.

    :param event: The asyncio event to wait for.
    :type event: asyncio.Event
    """
    await event.wait()
