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
from ._metadata import TaskMetadata
from ._models import TaskInfo, TaskStatus
from ._provider import DurableTaskProvider
from ._result import TaskResult

Output = TypeVar("Output")

_STREAM_SENTINEL = object()
"""Internal sentinel put on the stream queue to signal end of iteration."""


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

    Returned by :meth:`DurableTask.start`. Provides external observation
    and control of the task lifecycle.

    :param task_id: The task identifier.
    :type task_id: str
    :param provider: Storage provider for refresh/delete operations.
    :type provider: DurableTaskProvider
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
        "_provider",
        "_result_future",
        "_metadata",
        "_cancel_event",
        "_terminate_event",
        "_terminate_reason_ref",
        "_status",
        "_stream_queue",
        "_execution_task",
        "_lease_expiry_count",
    )

    def __init__(
        self,
        task_id: str,
        *,
        provider: DurableTaskProvider,
        result_future: asyncio.Future[TaskResult[Output]],
        metadata: TaskMetadata | None = None,
        cancel_event: asyncio.Event | None = None,
        status: TaskStatus = "in_progress",
        stream_queue: asyncio.Queue[Any] | None = None,
        terminate_event: asyncio.Event | None = None,
        execution_task: asyncio.Task[Any] | None = None,
        terminate_reason_ref: list[str | None] | None = None,
        lease_expiry_count: int = 0,
    ) -> None:
        self.task_id = task_id
        self._provider = provider
        self._result_future = result_future
        self._metadata = metadata or TaskMetadata()
        self._cancel_event = cancel_event or asyncio.Event()
        self._terminate_event = terminate_event or asyncio.Event()
        self._terminate_reason_ref: list[str | None] = (
            terminate_reason_ref if terminate_reason_ref is not None else [None]
        )
        self._status = status
        self._stream_queue: asyncio.Queue[Any] | None = stream_queue
        self._execution_task: asyncio.Task[Any] | None = execution_task
        self._lease_expiry_count = lease_expiry_count

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

        Sets the ``cancel`` event on the task context. The function
        should check ``ctx.cancel.is_set()`` and exit cleanly.
        """
        self._cancel_event.set()

    async def terminate(self, *, reason: str | None = None) -> None:
        """Forcefully terminate the task.

        Unlike :meth:`cancel`, terminated tasks go through the failure path
        and do NOT stay ``in_progress`` for recovery.

        :keyword reason: Optional human-readable termination reason.
        :paramtype reason: str | None
        """
        self._terminate_reason_ref[0] = reason
        self._terminate_event.set()
        self._cancel_event.set()
        if self._execution_task is not None and not self._execution_task.done():
            self._execution_task.cancel()

    async def delete(self) -> None:
        """Delete the task record from the store.

        :raises TaskNotFound: If the task does not exist.
        """
        try:
            await self._provider.delete(self.task_id, force=True)
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

    def __aiter__(self) -> TaskRun[Output]:
        """Return self as an async iterator over streamed items.

        Usage::

            async for chunk in task_run:
                print(chunk)

        :return: Self.
        :rtype: TaskRun
        """
        return self

    async def __anext__(self) -> Any:
        """Yield the next streamed item, or raise ``StopAsyncIteration``.

        If no stream queue was provided, raises ``StopAsyncIteration``
        immediately (the task does not stream).

        :return: The next streamed item.
        :rtype: Any
        :raises StopAsyncIteration: When streaming ends.
        """
        if self._stream_queue is None:
            raise StopAsyncIteration
        item = await self._stream_queue.get()
        if item is _STREAM_SENTINEL:
            raise StopAsyncIteration
        return item
