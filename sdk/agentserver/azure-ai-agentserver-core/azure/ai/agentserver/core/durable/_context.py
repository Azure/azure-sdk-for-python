# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""TaskContext — the single parameter to a durable task function.

Provides identity, typed input, mutable metadata, cancellation signals,
and the ``suspend()`` method for pausing execution.
"""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
from typing import Any, Generic, Literal, Sequence, TypeVar

from ._metadata import TaskMetadata
from ._stream import StreamHandler

Input = TypeVar("Input")
Output = TypeVar("Output")

EntryMode = Literal["fresh", "resumed", "recovered"]
"""Why the durable function was entered.

- ``"fresh"`` — First execution. Task was just created or started from pending.
- ``"resumed"`` — Re-entered after suspension. On developer-initiated resume
  (via ``.run()``), ``ctx.input`` contains the new input. On platform-initiated
  resume (via ``/tasks/{task_id}/resume``), ``ctx.input`` contains the task's
  persisted input. Also used when a steering input drains from the queue —
  check ``ctx.was_steered`` to distinguish steering re-entry from normal resume.
- ``"recovered"`` — Re-entered after stale task detection. The previous execution
  crashed or timed out. ``ctx.input`` contains the task's persisted input.
  If a steerable task crashed mid-drain, ``ctx.was_steered`` will be ``True``
  and steering context (``steering_generation``) is meaningful.
"""


class _Suspended:
    """Internal sentinel for suspended tasks. See ``Suspended`` in ``_run.py``."""

    __slots__ = ("reason", "output")

    def __init__(
        self,
        reason: str | None = None,
        output: Any | None = None,
    ) -> None:
        self.reason = reason
        self.output = output


class TaskContext(Generic[Input]):  # pylint: disable=too-many-instance-attributes
    """The single parameter to a durable task function.

    Provides access to the task's identity, typed input, mutable metadata
    for progress tracking, cancellation signals, and the ability to
    suspend execution.

    :param task_id: Unique task identifier.
    :type task_id: str
    :param session_id: Session scope identifier.
    :type session_id: str
    :param input: Typed, validated input value.
    :type input: Input
    :param metadata: Mutable progress metadata.
    :type metadata: TaskMetadata
    :param retry_attempt: Durable retry attempt counter. Survives crashes;
        increments only on failure-retries, never on crash recovery.
    :type retry_attempt: int
    :param recovery_count: Crash-recovery counter. Increments each time the
        framework re-enters this task after a lease loss or stale detection.
    :type recovery_count: int
    :param cancel: Request-level cancellation event.
    :type cancel: asyncio.Event
    :param shutdown: Container-level shutdown event.
    :type shutdown: asyncio.Event
    """

    __slots__ = (
        "task_id",
        "session_id",
        "input",
        "metadata",
        "retry_attempt",
        "recovery_count",
        "cancel",
        "shutdown",
        "_suspend_callback",
        "_stream_handler",
        "entry_mode",
        "was_steered",
        "pending_inputs",
        "steering_generation",
    )

    def __init__(
        self,
        *,
        task_id: str,
        session_id: str,
        input: Input,  # noqa: A002 — mirrors the spec naming
        metadata: TaskMetadata,
        retry_attempt: int = 0,
        recovery_count: int = 0,
        cancel: asyncio.Event | None = None,
        shutdown: asyncio.Event | None = None,
        stream_handler: StreamHandler | None = None,
        entry_mode: EntryMode = "fresh",
        was_steered: bool = False,
        pending_inputs: Sequence[Any] | None = None,
        steering_generation: int = 0,
    ) -> None:
        self.task_id = task_id
        self.session_id = session_id
        self.input = input
        self.metadata = metadata
        self.retry_attempt = retry_attempt
        self.recovery_count = recovery_count
        self.cancel = cancel or asyncio.Event()
        self.shutdown = shutdown or asyncio.Event()
        self._suspend_callback: Any = None
        self._stream_handler: StreamHandler | None = stream_handler
        self.entry_mode: EntryMode = entry_mode
        self.was_steered: bool = was_steered
        self.pending_inputs: Sequence[Any] = (
            pending_inputs if pending_inputs is not None else ()
        )
        self.steering_generation: int = steering_generation

    async def suspend(
        self,
        *,
        reason: str | None = None,
        output: Any | None = None,
    ) -> Any:
        """Suspend the task, releasing the lease and persisting state.

        Must be used as ``return await ctx.suspend(...)``. The framework
        interprets the returned sentinel to transition the task to
        ``suspended`` status.

        :keyword reason: Human-readable suspension reason.
        :paramtype reason: str | None
        :keyword output: Optional output snapshot for observers.
        :paramtype output: Any | None
        :return: A ``Suspended`` sentinel that the framework interprets.
        :rtype: Suspended
        """
        from ._run import Suspended  # pylint: disable=import-outside-toplevel

        return Suspended(reason=reason, output=output)

    async def stream(self, item: Any) -> None:
        """Emit a streaming item to observers iterating this task's output.

        When a :class:`~azure.ai.agentserver.core.durable.StreamHandler`
        is configured, the item is routed through ``handler.put(item)``.
        Otherwise the call is a no-op.

        :param item: The value to stream.
        :type item: Any
        """
        if self._stream_handler is not None:
            await self._stream_handler.put(item)
