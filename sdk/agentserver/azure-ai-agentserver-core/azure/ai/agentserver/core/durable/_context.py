# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""TaskContext — the single parameter to a durable task function.

Provides identity, typed input, mutable metadata, cancellation signals,
and the ``suspend()`` method for pausing execution.
"""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
from typing import Any, Generic, Literal, TypeVar

from ._metadata import TaskMetadata

Input = TypeVar("Input")
Output = TypeVar("Output")

EntryMode = Literal["fresh", "resumed", "recovered"]
"""Why the durable function was entered.

- ``"fresh"`` — First execution. Task was just created or started from pending.
- ``"resumed"`` — Re-entered after suspension. On developer-initiated resume
  (via ``.run()``), ``ctx.input`` contains the new input. On platform-initiated
  resume (via ``/tasks/{task_id}/resume``), ``ctx.input`` contains the task's
  persisted input.
- ``"recovered"`` — Re-entered after stale task detection. The previous execution
  crashed or timed out. ``ctx.input`` contains the task's persisted input.
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


class TaskContext(Generic[Input]):
    """The single parameter to a durable task function.

    Provides access to the task's identity, typed input, mutable metadata
    for progress tracking, cancellation signals, and the ability to
    suspend execution.

    :param task_id: Unique task identifier.
    :type task_id: str
    :param title: Human-readable task title.
    :type title: str
    :param session_id: Session scope identifier.
    :type session_id: str
    :param agent_name: Agent name from config.
    :type agent_name: str
    :param tags: Merged decorator + call-site tags.
    :type tags: dict[str, str]
    :param input: Typed, validated input value.
    :type input: Input
    :param metadata: Mutable progress metadata.
    :type metadata: TaskMetadata
    :param run_attempt: Framework retry attempt counter.
    :type run_attempt: int
    :param lease_generation: Lease re-acquisition counter.
    :type lease_generation: int
    :param cancel: Request-level cancellation event.
    :type cancel: asyncio.Event
    :param shutdown: Container-level shutdown event.
    :type shutdown: asyncio.Event
    """

    __slots__ = (
        "task_id",
        "title",
        "session_id",
        "agent_name",
        "tags",
        "input",
        "metadata",
        "run_attempt",
        "lease_generation",
        "cancel",
        "shutdown",
        "_suspend_callback",
        "_stream_queue",
        "entry_mode",
    )

    def __init__(
        self,
        *,
        task_id: str,
        title: str,
        session_id: str,
        agent_name: str,
        tags: dict[str, str],
        input: Input,  # noqa: A002 — mirrors the spec naming
        metadata: TaskMetadata,
        run_attempt: int = 0,
        lease_generation: int = 0,
        cancel: asyncio.Event | None = None,
        shutdown: asyncio.Event | None = None,
        stream_queue: asyncio.Queue[Any] | None = None,
        entry_mode: EntryMode = "fresh",
    ) -> None:
        self.task_id = task_id
        self.title = title
        self.session_id = session_id
        self.agent_name = agent_name
        self.tags = tags
        self.input = input
        self.metadata = metadata
        self.run_attempt = run_attempt
        self.lease_generation = lease_generation
        self.cancel = cancel or asyncio.Event()
        self.shutdown = shutdown or asyncio.Event()
        self._suspend_callback: Any = None
        self._stream_queue: asyncio.Queue[Any] | None = stream_queue
        self.entry_mode: EntryMode = entry_mode

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

        Items are buffered in an in-memory :class:`asyncio.Queue` and are
        **not** persisted. Each call unblocks the next ``async for`` iteration
        on the corresponding :class:`TaskRun`.

        :param item: The value to stream.
        :type item: Any
        """
        if self._stream_queue is not None:
            await self._stream_queue.put(item)
