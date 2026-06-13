# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""TaskRun handle for the durable task subsystem.

Spec 022 (Q9 / Q17 / FR-047 / FR-052): slim public shape.

Public surface:
- attributes: ``task_id``, ``input_id``
- property: ``metadata``
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

from ._metadata import TaskMetadata
from ._result import TaskResult  # internal compat: futures may resolve to TaskResult during transition

Output = TypeVar("Output")


class Suspended(Generic[Output]):
    """Internal-only transitional sentinel (Spec 022).

    No longer part of the public surface — kept only so legacy internal
    code paths in ``_manager.py`` and ``_context.py`` can continue to
    operate during the deprecation window. New code MUST NOT import
    ``Suspended`` from the public ``azure.ai.agentserver.core.durable``
    surface.
    """

    __slots__ = ("reason", "output")

    def __init__(
        self,
        reason: str | None = None,
        output: Output | None = None,
    ) -> None:
        self.reason = reason
        self.output = output

    def __repr__(self) -> str:
        return f"Suspended(reason={self.reason!r})"


def _unwrap_result(res: Any) -> Any:
    """FR-052: return raw Output from internal TaskResult (transitional)."""
    if isinstance(res, TaskResult):
        return res.output
    return res


class TaskRun(Generic[Output]):  # pylint: disable=too-many-instance-attributes
    """Handle to a running or completed durable task.

    Returned by :meth:`Task.start`. Provides external observation
    and control of the task lifecycle.

    :param task_id: The task identifier.
    :type task_id: str
    :param provider: Storage provider for refresh/delete operations.
    :type provider: TaskProvider
    :param result_future: Future that resolves with the task output.
    :type result_future: asyncio.Future[Output]
    :param metadata: The task's metadata instance.
    :type metadata: TaskMetadata
    :param cancel_event: Event to signal cancellation.
    :type cancel_event: asyncio.Event
    :param status: Initial task status.
    :type status: TaskStatus
    """

    __slots__ = (
        "task_id",
        "input_id",  # spec 022 FR-047 — public read-only attribute
        "_result_future",
        "_metadata",
        "_cancel_event",
        "_cancel_ctx_ref",
        "_execution_task",
    )

    def __init__(
        self,
        task_id: str,
        *,
        provider: Any = None,  # noqa: ARG002 — kept for ctor compat, no longer stored (Phase 5)
        result_future: asyncio.Future[Any],
        metadata: TaskMetadata | None = None,
        cancel_event: asyncio.Event | None = None,
        status: Any = None,  # noqa: ARG002 — accepted but ignored (Phase 5)
        terminate_event: asyncio.Event | None = None,  # noqa: ARG002 — accepted but ignored (Phase 5)
        execution_task: asyncio.Task[Any] | None = None,
        terminate_reason_ref: list[str | None] | None = None,  # noqa: ARG002 — accepted but ignored (Phase 5)
        lease_expiry_count: int = 0,  # noqa: ARG002 — accepted but ignored (Phase 5)
        cancel_ctx_ref: Any = None,
        input_id: str | None = None,
    ) -> None:
        self.task_id = task_id
        # Spec 022 FR-047 — `input_id` is a public read-only attribute on
        # TaskRun. For one-shot tasks it defaults to ``task_id`` (1:1 invariant
        # per FR-004); for multi-turn tasks the framework auto-generates a
        # separate GUID per turn (per FR-005) and sets it here.
        self.input_id: str = input_id if input_id is not None else task_id
        self._result_future = result_future
        self._metadata = metadata or TaskMetadata()
        self._cancel_event = cancel_event or asyncio.Event()
        self._execution_task: asyncio.Task[Any] | None = execution_task
        # Spec 016 FR-018 (US6): weak reference to the TaskContext so
        # TaskRun.cancel() can set ctx.cancel_requested = True before
        # setting ctx.cancel.
        self._cancel_ctx_ref: Any = cancel_ctx_ref

    @property
    def metadata(self) -> TaskMetadata:
        """The task's metadata.

        For in-process handles, this is the live metadata reference.

        :return: The task metadata instance.
        :rtype: TaskMetadata
        """
        return self._metadata

    async def result(self) -> Output:
        """Await task completion and return the raw output value.

        Spec 022 FR-052: returns ``Output`` directly (not a wrapper).
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

        Spec 016 FR-018 (US6): sets ``ctx.cancel_requested = True``
        BEFORE setting ``ctx.cancel``, so a handler observing
        ``ctx.cancel.is_set() == True`` is guaranteed to see at least
        one cause boolean already ``True``.

        The handler should check ``ctx.cancel.is_set()`` (and optionally
        branch on which cause boolean is set) to wind down cleanly.
        """
        ctx = self._cancel_ctx_ref
        if ctx is not None:
            ctx.cancel_requested = True
        self._cancel_event.set()

    def __await__(self) -> Any:
        """Awaiting a :class:`TaskRun` returns its raw :meth:`result`.

        Spec 022 FR-052: resolves to ``Output`` (not a wrapper). Mirrors
        ``await run.result()`` exactly.

        :return: The raw output value.
        :rtype: Output
        """
        return self.result().__await__()
