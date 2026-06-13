# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""TaskRun handle and Suspended sentinel for the durable task subsystem."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
from typing import Any, Generic, TypeVar

from ._exceptions import (
    TaskNotFound,
)
from ._exceptions_internal import _HostedConflict, _translate_hosted_conflict
from ._metadata import TaskMetadata
from ._models import TaskInfo, TaskStatus
from ._provider import TaskProvider
from ._result import TaskResult

Output = TypeVar("Output")


class Suspended(Generic[Output]):
    """Sentinel return value from :meth:`TaskContext.suspend`.

    Must be used as ``return await ctx.suspend(...)``. The framework
    interprets this on function return to transition the task.

    :param reason: Human-readable suspension reason.
    :type reason: str | None
    :param output: Optional snapshot for observers.
    :type output: Output | None
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
        "_provider",
        "_result_future",
        "_metadata",
        "_cancel_event",
        "_cancel_ctx_ref",
        "_terminate_event",  # Spec 016 FR-022: retained as internal-only; will be removed when callers stop passing it
        "_terminate_reason_ref",
        "_status",
        "_execution_task",
        "_lease_expiry_count",
    )

    def __init__(
        self,
        task_id: str,
        *,
        provider: TaskProvider,
        result_future: asyncio.Future[TaskResult[Output]],
        metadata: TaskMetadata | None = None,
        cancel_event: asyncio.Event | None = None,
        status: TaskStatus = "in_progress",
        terminate_event: asyncio.Event | None = None,
        execution_task: asyncio.Task[Any] | None = None,
        terminate_reason_ref: list[str | None] | None = None,
        lease_expiry_count: int = 0,
        cancel_ctx_ref: Any = None,
        input_id: str | None = None,
    ) -> None:
        self.task_id = task_id
        # Spec 022 FR-047 — `input_id` is a public read-only attribute on
        # TaskRun. For one-shot tasks it defaults to ``task_id`` (1:1 invariant
        # per FR-004); for multi-turn tasks the framework auto-generates a
        # separate GUID per turn (per FR-005) and sets it here.
        self.input_id: str = input_id if input_id is not None else task_id
        self._provider = provider
        self._result_future = result_future
        self._metadata = metadata or TaskMetadata()
        self._cancel_event = cancel_event or asyncio.Event()
        self._terminate_event = terminate_event or asyncio.Event()
        self._terminate_reason_ref: list[str | None] = (
            terminate_reason_ref if terminate_reason_ref is not None else [None]
        )
        self._status: TaskStatus = status
        self._execution_task: asyncio.Task[Any] | None = execution_task
        self._lease_expiry_count = lease_expiry_count
        # Spec 016 FR-018 (US6): weak reference to the TaskContext so
        # TaskRun.cancel() can set ctx.cancel_requested = True before
        # setting ctx.cancel.
        self._cancel_ctx_ref: Any = cancel_ctx_ref

    @property
    def status(self) -> TaskStatus:
        """Current task status (may be stale — call :meth:`refresh` to update).

        :return: The task status.
        :rtype: TaskStatus
        """
        return self._status

    @property
    def metadata(self) -> TaskMetadata:
        """The task's metadata.

        For in-process handles, this is the live metadata reference. For
        remote observation, call :meth:`refresh` first.

        :return: The task metadata instance.
        :rtype: TaskMetadata
        """
        return self._metadata

    @property
    def lease_expiry_count(self) -> int:
        """Number of times the lease expired and ownership changed.

        Useful for dashboards to detect ownership churn. Call
        :meth:`refresh` to get the latest value.

        :return: The lease expiry count.
        :rtype: int
        """
        return self._lease_expiry_count

    async def result(self) -> TaskResult[Output]:
        """Await task completion and return the result.

        Returns a :class:`TaskResult` that wraps both completion and
        suspension outcomes. Failures, cancellation, and termination are
        still raised as exceptions.

        :return: The task result wrapper.
        :rtype: TaskResult[Output]
        :raises TaskFailed: If the function raised an exception.
        :raises TaskCancelled: If the task was cancelled.
        :raises TaskTerminated: If the task was terminated.
        :raises TaskNotFound: If the task was deleted externally.
        """
        return await self._result_future

    async def cancel(self) -> None:
        """Signal cancellation to the running task.

        Spec 016 FR-018 (US6): sets ``ctx.cancel_requested = True``
        BEFORE setting ``ctx.cancel``, so a handler observing
        ``ctx.cancel.is_set() == True`` is guaranteed to see at least
        one cause boolean already ``True``.

        The handler should check ``ctx.cancel.is_set()`` (and optionally
        branch on which cause boolean is set) to wind down cleanly.
        """
        # The cause boolean is propagated through the framework via the
        # _ActiveTask wiring; see _manager.py for the indirection. Here
        # we just set the cancel event; the framework's wrapper sets the
        # cause boolean first.
        ctx = self._cancel_ctx_ref
        if ctx is not None:
            ctx.cancel_requested = True
        self._cancel_event.set()

    async def delete(self) -> None:
        """Delete the task record from the store.

        :raises TaskNotFound: If the task does not exist.
        """
        try:
            await self._provider.delete(self.task_id, force=True)
        except _HostedConflict as exc:
            translated = _translate_hosted_conflict(exc, task_id=self.task_id)
            if translated is not None:
                raise translated from exc
            raise
        except Exception as exc:
            if "not found" in str(exc).lower():
                raise TaskNotFound(self.task_id) from exc
            raise

    async def refresh(self) -> None:
        """Re-fetch task state from the store.

        Updates :attr:`status` and :attr:`metadata` from the current
        task record.
        """
        task_info: TaskInfo | None = await self._provider.get(self.task_id)
        if task_info is None:
            raise TaskNotFound(self.task_id)
        self._status = task_info.status
        # Update lease expiry count
        if task_info.lease is not None:
            self._lease_expiry_count = task_info.lease.expiry_count
        # Update metadata from payload
        if task_info.payload and "metadata" in task_info.payload:
            meta_data: dict[str, Any] = task_info.payload["metadata"]
            for key, value in meta_data.items():
                self._metadata.set(key, value)

    def __await__(self) -> Any:
        """Awaiting a :class:`TaskRun` returns its :meth:`result`.

        Lets callers write ``result = await run`` as shorthand for
        ``result = await run.result()``. Useful when you already have
        a ``TaskRun`` handle (e.g. from :meth:`Task.start` or
        :meth:`Task.get_active_run`) and just want the terminal
        outcome.

        Usage::

            run = await my_task.start(task_id="t1", input=...)
            ...
            result = await run

        :return: The :class:`TaskResult` for this run.
        :rtype: TaskResult[Output]
        """
        return self.result().__await__()
