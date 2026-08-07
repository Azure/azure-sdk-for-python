# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""TaskContext — the single parameter to a resilient task function.

Provides identity, typed input, mutable metadata, cancellation signals,
and the ``suspend()`` method for pausing execution.

  introduces the cancel-cause boolean surface
(``timeout_exceeded``, ``cancel_requested``, ``pending_input_count``,
``is_steered_turn``) and the ``exit_for_recovery()`` graceful-shutdown
shape. The legacy fields ``was_steered`` / ``pending_inputs`` /
``steering_generation`` are removed.
"""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
from typing import Any, Callable, Generic, Literal, TypeVar

from azure.ai.agentserver.core._experimental import experimental

from ._metadata import TaskMetadata

Input = TypeVar("Input")
Output = TypeVar("Output")

EntryMode = Literal["fresh", "resumed", "recovered"]
"""Why the resilient function was entered.

- ``"fresh"`` — First execution. Task was just created or started from pending.
- ``"resumed"`` — Re-entered after suspension. On developer-initiated resume
  (via ``.run()``), ``ctx.input`` contains the new input. On platform-initiated
  resume (via ``/tasks/{task_id}/resume``), ``ctx.input`` contains the task's
  persisted input. Also used when a steering input drains from the queue —
  check ``ctx.is_steered_turn`` to distinguish steering re-entry from normal
  resume.
- ``"recovered"`` — Re-entered after stale task detection. The previous execution
  crashed or timed out. ``ctx.input`` contains the task's persisted input.
  If a steerable task crashed mid-drain, ``ctx.is_steered_turn`` will be
  ``True``.
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


class _ExitForRecovery:
    """: internal sentinel returned by
    :meth:`TaskContext.exit_for_recovery` to signal the framework to
    flush metadata, release the lease, and leave the stored status
    as ``in_progress``.
    """

    __slots__ = ()


@experimental
class TaskContext(Generic[Input]):  # pylint: disable=too-many-instance-attributes
    """The single parameter to a resilient task function.

    Provides access to the task's identity, typed input, mutable metadata
    for progress tracking, cancellation signals (with cause booleans),
    and the ability to suspend or exit-for-recovery.

    :param task_id: Unique task identifier.
    :type task_id: str
    :param input: Typed, validated input value.
    :type input: Input
    :param metadata: Mutable progress metadata.
    :type metadata: TaskMetadata
    :param retry_attempt: Resilient retry attempt counter. Survives crashes;
        increments only on failure-retries, never on crash recovery.
    :type retry_attempt: int
    :param recovery_count: Crash-recovery counter. Increments each time the
        framework re-enters this task after a lease loss or stale detection.
    :type recovery_count: int
    :param cancel: Request-level cancellation event. The framework sets
        this from multiple causes; observe ``timeout_exceeded``,
        ``cancel_requested``, ``pending_input_count`` to disambiguate.
    :type cancel: asyncio.Event
    :param shutdown: Container-level shutdown event. Precondition for
        :meth:`exit_for_recovery`.
    :type shutdown: asyncio.Event
    """

    __slots__ = (
        "task_id",
        "input_id",  #   /
        "_session_id",
        "input",
        "metadata",
        "retry_attempt",
        "recovery_count",
        "cancel",
        "shutdown",
        "_suspend_callback",
        "entry_mode",
        # ..  public cancel-cause / steering surface.
        "timeout_exceeded",
        "cancel_requested",
        "is_steered_turn",
        # Internal callable for the live pending_input_count property
        # . The framework sets this when constructing the
        # TaskContext; the property reads it on each access so the
        # count reflects the current backlog including inputs queued
        # mid-handler.
        "_pending_count_provider",
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
        entry_mode: EntryMode = "fresh",
        is_steered_turn: bool = False,
        pending_count_provider: Callable[[], int] | None = None,
        input_id: str | None = None,
    ) -> None:
        self.task_id = task_id
        #   /: input_id is part of the public TaskContext
        # surface. Defaults to task_id (one-shot 1:1 invariant).
        self.input_id = input_id if input_id is not None else task_id
        self._session_id = session_id
        self.input = input
        self.metadata = metadata
        self.retry_attempt = retry_attempt
        self.recovery_count = recovery_count
        self.cancel = cancel or asyncio.Event()
        self.shutdown = shutdown or asyncio.Event()
        self._suspend_callback: Any = None
        self.entry_mode: EntryMode = entry_mode
        # ..: public surface fields. Defaults are
        # framework-controlled at construction; framework setters update
        # them in place. No public setters.
        self.timeout_exceeded: bool = False
        self.cancel_requested: bool = False
        self.is_steered_turn: bool = is_steered_turn
        self._pending_count_provider = pending_count_provider

    @property
    def pending_input_count(self) -> int:
        """: live count of queued steering inputs.

        Reflects the current backlog including inputs queued mid-handler.
        Reads as ``0`` for non-steerable tasks (where the provider
        returns 0). Replaces the legacy ``ctx.pending_inputs: Sequence[Any]``
        snapshot.

        :return: Number of queued steering inputs.
        :rtype: int
        """
        if self._pending_count_provider is None:
            return 0
        try:
            return int(self._pending_count_provider())
        except Exception:  # pylint: disable=broad-exception-caught  # noqa: BLE001
            return 0

    async def exit_for_recovery(self) -> Any:
        """: graceful-shutdown shape.

                Callable ONLY when ``ctx.shutdown.is_set() == True``. Calling it
                outside shutdown raises ``RuntimeError`` at the call site
                (visible in user-code tracebacks; the task ends in ``failed``).

                When called during shutdown, the framework:

                1. Flushes ``ctx.metadata`` (auto-flush invariant).
                2. Releases the lease on the persisted record.
                3. Leaves the stored ``status`` as ``in_progress`` (NOT
                   transitions to ``suspended``).
                4. Signals in-process awaiters with the standard cooperative-
                   cancel ``TaskCancelled`` result.
                5. Preserves any queued steering inputs in the persisted state.

                The recovery scan on the next process startup re-enters the
                handler with ``ctx.entry_mode == "recovered"``.

                Use as ``return await ctx.exit_for_recovery()``.

                :return: The :class:`_ExitForRecovery` sentinel.
                :rtype: Any
                :raises RuntimeError: If called outside ``ctx.shutdown.is_set() == True``.
        """
        if not self.shutdown.is_set():
            raise RuntimeError(
                "ctx.exit_for_recovery() may only be called when "
                "ctx.shutdown.is_set() is true. The misuse-as-failed "
                "semantic exists so operator logs surface accidental "
                "calls loudly."
            )
        return _ExitForRecovery()
