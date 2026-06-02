# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Exception types for the durable task subsystem."""

from typing import Any


class TaskFailed(Exception):
    """Raised when a durable task function raises an unhandled exception.

    :param task_id: The identifier of the failed task.
    :type task_id: str
    :param error: Structured error details captured from the exception.
    :type error: dict[str, Any]
    """

    def __init__(self, task_id: str, error: dict[str, Any]) -> None:
        self.task_id = task_id
        self.error = error
        message = error.get("message", "Task failed")
        super().__init__(f"Task {task_id!r} failed: {message}")


class TaskCancelled(Exception):
    """Raised when a durable task is cancelled.

    Inherits from :class:`Exception` rather than :class:`asyncio.CancelledError`
    to prevent unintentional suppression by generic ``CancelledError`` handlers
    in the asyncio event loop.

    :param task_id: The identifier of the cancelled task.
    :type task_id: str
    """

    def __init__(self, task_id: str) -> None:
        self.task_id = task_id
        super().__init__(f"Task {task_id!r} was cancelled")


class TaskNotFound(Exception):
    """Raised when a task ID is not found in the store.

    :param task_id: The identifier that was not found.
    :type task_id: str
    """

    def __init__(self, task_id: str) -> None:
        self.task_id = task_id
        super().__init__(f"Task {task_id!r} not found")


# Spec 016 FR-022 + SC-014 (US6): TaskTerminated removed.
#
# The legacy ``TaskTerminated`` exception and its corresponding
# ``TaskRun.terminate()`` pathway are fully removed. Use
# ``TaskRun.cancel()`` and let the handler choose the terminal shape
# via its reaction to ``ctx.cancel.is_set()`` (raise to fail, return
# to complete, ctx.suspend() to suspend).


class TaskConflictError(RuntimeError):
    """Raised when a task lifecycle conflict cannot be resolved.

    Raised by ``.run()`` or ``.start()`` when the task is already
    ``in_progress`` (non-stale) or ``completed``. The lifecycle is
    deterministic: create if none, start if pending, resume if suspended,
    throw if in-progress or completed.

    :param task_id: The conflicting task's ID.
    :type task_id: str
    :param current_status: The task's current status.
    :type current_status: str
    """

    __slots__ = ("task_id", "current_status")

    def __init__(
        self,
        task_id: str,
        current_status: str,
    ) -> None:
        self.task_id = task_id
        self.current_status = current_status
        super().__init__(f"Task '{task_id}' is already {current_status}")


class EtagConflict(RuntimeError):
    """Raised when an optimistic concurrency (etag) check fails.

    .. note::
       **Advanced / internal.** Most application code does not need to
       handle this exception. The framework retries internally on optimistic
       concurrency conflicts; ``EtagConflict`` only escapes when a low-level
       caller manipulates etags directly (e.g., custom storage adapters or
       admin tools).

    The task record was modified between read and write. Callers should
    retry the operation with the updated etag.

    :param task_id: The task ID where the conflict occurred.
    :type task_id: str
    :param message: Optional detail message.
    :type message: str | None
    """

    __slots__ = ("task_id",)

    def __init__(self, task_id: str, message: str | None = None) -> None:
        self.task_id = task_id
        msg = message or f"Etag conflict on task '{task_id}'"
        super().__init__(msg)


class SteeringQueueFull(RuntimeError):
    """Raised when the steering pending-input queue is at capacity.

    The caller should retry later or increase ``max_pending``.

    :param task_id: The task whose queue is full.
    :type task_id: str
    :param max_pending: The configured queue capacity.
    :type max_pending: int
    """

    __slots__ = ("task_id", "max_pending")

    def __init__(self, task_id: str, max_pending: int) -> None:
        self.task_id = task_id
        self.max_pending = max_pending
        super().__init__(
            f"Steering queue full for task '{task_id}' " f"(max_pending={max_pending})"
        )


class TaskPreconditionFailed(RuntimeError):
    """Base class for task primitive precondition failures.

    Raised by :meth:`Task.start` (and possibly other primitives in future)
    when a caller-supplied precondition is not met by the task's current
    state. Subclasses identify which specific precondition failed; catch
    this base class to handle any precondition failure uniformly.

    :param task_id: The task identifier.
    :type task_id: str
    :param message: Human-readable description of the precondition failure.
    :type message: str
    """

    __slots__ = ("task_id",)

    def __init__(self, task_id: str, message: str) -> None:
        self.task_id = task_id
        super().__init__(message)


class LastInputIdPreconditionFailed(TaskPreconditionFailed):
    """Raised when :meth:`Task.start`'s ``if_last_input_id`` precondition is not met.

    The task's most-recently-accepted input has a different id than the
    caller expected. Typically caused by a concurrent caller advancing the
    queue before this one's read-then-write completed, or by a programming
    error in which the caller's view of the chain is stale.

    :param task_id: The task identifier.
    :type task_id: str
    :param expected_last_input_id: What the caller passed as ``if_last_input_id``.
    :type expected_last_input_id: str | None
    :param actual_last_input_id: What the framework currently has stored.
    :type actual_last_input_id: str | None
    """

    __slots__ = ("expected_last_input_id", "actual_last_input_id")

    def __init__(
        self,
        task_id: str,
        expected_last_input_id: str | None,
        actual_last_input_id: str | None,
    ) -> None:
        self.expected_last_input_id = expected_last_input_id
        self.actual_last_input_id = actual_last_input_id
        super().__init__(
            task_id,
            f"Task {task_id!r}: if_last_input_id precondition failed — "
            f"expected last_input_id={expected_last_input_id!r}, "
            f"actual={actual_last_input_id!r}",
        )
