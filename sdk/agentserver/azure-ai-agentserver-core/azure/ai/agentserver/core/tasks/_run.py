# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""TaskRun handle for the resilient task subsystem.

 (Q9 / Q17 /  /): slim public shape.

Public surface:
- attributes: ``task_id``, ``input_id``
- methods: ``result()`` (returns ``Output``), ``cancel()``
- dunder: ``__await__``

The legacy ``status``, ``lease_expiry_count``, ``delete()``, ``refresh()``,
and the ``Suspended`` sentinel are intentionally removed. The
``TaskResult`` wrapper is no longer exposed: ``await run`` / ``await
run.result()`` resolves to the raw ``Output`` value (or raises
``TaskFailed`` / ``TaskCancelled`` / ``TaskDeferred``).
"""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
from typing import Any, Generic, TypeVar

from azure.ai.agentserver.core._experimental import experimental

Output = TypeVar("Output")


def _unwrap_result(res: Any) -> Any:
    """: futures now resolve to raw Output directly.

    Identity helper retained so older monkey-patches in tests that
    pre-wrap futures still pass unchanged.

    :param res: The already-resolved result value.
    :type res: Any
    :return: The same value, unchanged.
    :rtype: Any
    """
    return res


@experimental
class TaskRun(Generic[Output]):  # pylint: disable=too-many-instance-attributes
    """Handle to a running or completed resilient task.

    Returned by :meth:`Task.start`. Provides external observation
    and control of the task lifecycle.

    :param task_id: The task identifier.
    :type task_id: str
    :param provider: Storage provider for refresh/delete operations.
    :type provider: TaskProvider
    :param result_future: Future that resolves with the task output.
    :type result_future: asyncio.Future[Output]
    :param cancel_event: Event to signal cancellation.
    :type cancel_event: asyncio.Event
    :param status: Initial task status.
    :type status: TaskStatus
    """

    __slots__ = (
        "task_id",
        "input_id",  #   — public read-only attribute
        "_result_future",
        "_cancel_event",
        "_cancel_ctx_ref",
        "_execution_task",
        "_queued_cancel_callback",
    )

    def __init__(  # pylint: disable=unused-argument
        self,
        task_id: str,
        *,
        provider: Any = None,  # noqa: ARG002 — kept for ctor compat, no longer stored (Phase 5)
        result_future: asyncio.Future[Any],
        cancel_event: asyncio.Event | None = None,
        status: Any = None,  # noqa: ARG002 — accepted but ignored (Phase 5)
        terminate_event: asyncio.Event | None = None,  # noqa: ARG002 — accepted but ignored (Phase 5)
        execution_task: asyncio.Task[Any] | None = None,
        terminate_reason_ref: list[str | None] | None = None,  # noqa: ARG002 — accepted but ignored (Phase 5)
        lease_expiry_count: int = 0,  # noqa: ARG002 — accepted but ignored (Phase 5)
        cancel_ctx_ref: Any = None,
        input_id: str | None = None,
        queued_cancel_callback: Any = None,
    ) -> None:
        self.task_id = task_id
        #   — `input_id` is a public read-only attribute on
        # TaskRun. For one-shot tasks it defaults to ``task_id`` (1:1 invariant
        # ); for multi-turn tasks the framework auto-generates a
        # separate GUID per turn  and sets it here.
        self.input_id: str = input_id if input_id is not None else task_id
        self._result_future = result_future
        self._cancel_event = cancel_event or asyncio.Event()
        self._execution_task: asyncio.Task[Any] | None = execution_task
        #: weak reference to the TaskContext so
        # TaskRun.cancel() can set ctx.cancel_requested = True before
        # setting ctx.cancel.
        self._cancel_ctx_ref: Any = cancel_ctx_ref
        # Optional callback installed by the framework when this handle
        # represents a queued (not-yet-promoted) steering input.
        # ``cancel()`` invokes the callback instead of the in-process
        # cancel signal — the callback removes the queued slot from
        # ``_steering.pending_inputs`` and resolves the future with
        # ``TaskCancelled``.
        self._queued_cancel_callback: Any = queued_cancel_callback

    @property
    def is_queued(self) -> bool:
        """Whether this handle represents a *queued* steering input.

        ``True`` when this :class:`TaskRun` is a queued (not-yet-promoted)
        steering input on a steerable chain — i.e. the request landed while a
        turn was already in flight and is awaiting drain — and ``False`` for a
        freshly-started or active run. A queued run's :meth:`cancel` removes the
        queued slot and resolves :meth:`result` with ``TaskCancelled`` without
        affecting the active turn.

        This is the supported, public way to distinguish a queued steering
        handle from a freshly-started one.

        :return: ``True`` if this handle is a queued steering input.
        :rtype: bool
        """
        return self._queued_cancel_callback is not None

    async def result(self) -> Output:
        """Await task completion and return the raw output value.

        : returns ``Output`` directly (not a wrapper).
                Failures, cancellation, deferral are raised as exceptions.

                :return: The task's output value.
                :rtype: Output
                :raises TaskFailed: If the function raised an exception (one-shot).
                :raises TaskCancelled: If the task was cancelled.
                :raises TaskDeferred: If the task called ``ctx.exit_for_recovery()``.
        """
        return _unwrap_result(await self._result_future)

    async def cancel(self) -> None:
        """Signal cancellation to the running task.

        : sets ``ctx.cancel_requested = True``
                BEFORE setting ``ctx.cancel``, so a handler observing
                ``ctx.cancel.is_set() == True`` is guaranteed to see at least
                one cause boolean already ``True``.

                The handler should check ``ctx.cancel.is_set()`` (and optionally
                branch on which cause boolean is set) to wind down cleanly.

        For a queued (not-yet-promoted) steering input, ``cancel()``
        removes the queued slot from the chain's pending-inputs queue
        and resolves :meth:`result` with ``TaskCancelled``. The active
        turn (if any) is not affected.
        """
        if self._queued_cancel_callback is not None:
            await self._queued_cancel_callback()
            return
        ctx = self._cancel_ctx_ref
        if ctx is not None:
            ctx.cancel_requested = True
        self._cancel_event.set()

    def __await__(self) -> Any:
        """Awaiting a :class:`TaskRun` returns its raw :meth:`result`.

        : resolves to ``Output`` (not a wrapper). Mirrors
                ``await run.result()`` exactly.

                :return: The raw output value.
                :rtype: Output
        """
        return self.result().__await__()
