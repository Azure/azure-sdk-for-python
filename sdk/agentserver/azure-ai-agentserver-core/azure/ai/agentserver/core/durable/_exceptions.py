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


class TaskSuspended(Exception):
    """Raised when awaiting the result of a suspended task.

    :param task_id: The identifier of the suspended task.
    :type task_id: str
    :param reason: Human-readable suspension reason, if provided.
    :type reason: str | None
    :param output: Optional output snapshot set at suspension time.
    :type output: Any | None
    """

    def __init__(
        self,
        task_id: str,
        reason: str | None = None,
        output: Any | None = None,
    ) -> None:
        self.task_id = task_id
        self.reason = reason
        self.output = output
        suffix = f": {reason}" if reason else ""
        super().__init__(f"Task {task_id!r} is suspended{suffix}")


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


class TaskTerminated(Exception):
    """Raised when a task is forcefully terminated via ``handle.terminate()``.

    Unlike :class:`TaskCancelled`, terminated tasks go through the failure
    path and do NOT stay ``in_progress`` for recovery.

    :param task_id: The identifier of the terminated task.
    :type task_id: str
    :param reason: Optional human-readable termination reason.
    :type reason: str | None
    """

    __slots__ = ("task_id", "reason")

    def __init__(self, task_id: str, reason: str | None = None) -> None:
        self.task_id = task_id
        self.reason = reason
        suffix = f": {reason}" if reason else ""
        super().__init__(f"Task {task_id!r} was terminated{suffix}")


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
