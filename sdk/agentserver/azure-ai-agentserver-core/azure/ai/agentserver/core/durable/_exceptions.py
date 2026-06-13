# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Exception types for the durable task subsystem.

Spec 022 reshape (FR-074..077): public exceptions no longer carry
``task_id`` (caller has it via the run handle / call site). Constructors
ACCEPT legacy ``task_id`` positional args for back-compat during the
transition, but discard them (the attribute is never set).
"""

from typing import Any


class TaskFailed(Exception):
    """Raised when a durable task function raises an unhandled exception.

    Spec 022 FR-075: only ``error`` is carried. ``task_id`` is no longer
    on the exception (caller has it from the run handle).

    :keyword error: Structured error details (matches one of TaskErrorDict
        or TaskExhaustedRetriesErrorDict).
    :paramtype error: dict[str, Any]
    """

    error: "TaskErrorDict | TaskExhaustedRetriesErrorDict"

    def __init__(self, *args: Any, error: dict[str, Any] | None = None) -> None:
        # Legacy: TaskFailed(task_id, error_dict)
        if args:
            if len(args) == 2 and error is None:
                # Legacy positional (task_id, error_dict): discard task_id.
                error = args[1]
            elif len(args) == 1 and error is None:
                error = args[0]
        if not isinstance(error, dict):
            raise TypeError("TaskFailed: 'error' keyword (dict) is required")
        self.error = error  # type: ignore[assignment]
        super().__init__(error.get("message", "Task failed"))


class TaskCancelled(Exception):
    """Raised when a durable task is cancelled (spec 022 FR-077: bare)."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Accept and discard any legacy positional/keyword args (e.g.,
        # legacy ``TaskCancelled("t1")``); the exception is bare.
        msg = "Task was cancelled"
        if args and isinstance(args[0], str) and len(args) == 1:
            msg = f"Task {args[0]!r} was cancelled"
        super().__init__(msg)


class TaskNotFound(Exception):
    """Internal-only — not exported from public surface per spec 022 FR-074."""

    def __init__(self, task_id: str | None = None) -> None:
        self.task_id = task_id  # kept on this internal class for log messages
        super().__init__(f"Task {task_id!r} not found")


class TaskConflictError(RuntimeError):
    """Raised when a task lifecycle conflict cannot be resolved.

    Spec 022 FR-075: only ``current_status`` is carried.

    :keyword current_status: The task's current status.
    :paramtype current_status: str
    """

    __slots__ = ("current_status",)

    def __init__(self, *args: Any, current_status: str | None = None) -> None:
        # Legacy: TaskConflictError(task_id, current_status)
        if args:
            if len(args) == 2 and current_status is None:
                current_status = args[1]
            elif len(args) == 1 and current_status is None:
                current_status = args[0]
        if current_status is None:
            raise TypeError("TaskConflictError: 'current_status' is required")
        self.current_status = current_status
        super().__init__(f"Task is already {current_status}")


class EtagConflict(RuntimeError):
    """Raised when an optimistic concurrency (etag) check fails.

    Internal-leaning advanced API — not reshaped by spec 022.
    """

    __slots__ = ("task_id",)

    def __init__(self, task_id: str, message: str | None = None) -> None:
        self.task_id = task_id
        msg = message or f"Etag conflict on task '{task_id}'"
        super().__init__(msg)


class SteeringQueueFull(RuntimeError):
    """Raised when the steering pending-input queue is at capacity (spec 022 FR-077: bare)."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__("Steering queue is full")


class TaskPreconditionFailed(RuntimeError):
    """Internal-only base — not exported per spec 022 FR-074.

    Legacy subclass parent for :class:`LastInputIdPreconditionFailed`
    only. Developers MUST catch the specific subclass, not this base.
    """

    __slots__ = ("task_id",)

    def __init__(self, task_id: str = "", message: str = "") -> None:
        self.task_id = task_id
        super().__init__(message or "task precondition failed")


class LastInputIdPreconditionFailed(TaskPreconditionFailed):
    """Raised when ``Task.start``'s ``if_last_input_id`` precondition is not met.

    Spec 022 FR-076: only ``actual_last_input_id`` is carried.

    :keyword actual_last_input_id: The value the framework currently has stored
        for the chain's ``_last_input_id``.
    :paramtype actual_last_input_id: str | None
    """

    __slots__ = ("actual_last_input_id",)

    def __init__(
        self,
        *args: Any,
        actual_last_input_id: str | None = None,
        expected_last_input_id: str | None = None,  # accepted, discarded
        task_id: str | None = None,  # accepted, discarded for public attr
    ) -> None:
        # Legacy shapes supported during transition:
        #   - positional (task_id, expected, actual)  [3-arg]
        #   - mixed: positional task_id + keyword actual_last_input_id=
        legacy_task_id = task_id
        if args:
            if len(args) == 1:
                if actual_last_input_id is None and expected_last_input_id is None:
                    actual_last_input_id = args[0]
                else:
                    legacy_task_id = args[0]
            elif len(args) == 3:
                legacy_task_id = args[0]
                actual_last_input_id = args[2]
        self.actual_last_input_id = actual_last_input_id
        # NB: do NOT set self.task_id / self.expected_last_input_id —
        # spec 022 FR-076/077 says these aren't on the exception.
        msg = (
            f"if_last_input_id precondition failed: "
            f"actual last_input_id={actual_last_input_id!r}"
        )
        # Use legacy parent constructor with empty task_id (kept internal).
        super().__init__(legacy_task_id or "", msg)


class InputTooLarge(ValueError):
    """Raised when an input's serialized size exceeds the per-input cap (spec 022 FR-077: bare)."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__("Input exceeds the per-input cap")


# Spec 022 FR-074: OutputTooLarge is REMOVED from public surface. The
# class is kept as internal-only (no longer in __init__'s __all__).
class OutputTooLarge(ValueError):
    """Internal-only — not exported per spec 022 FR-074. Kept for legacy raise sites."""

    __slots__ = ("task_id", "size_bytes", "max_bytes")

    def __init__(self, task_id: str = "", size_bytes: int = 0, max_bytes: int = 0) -> None:
        self.task_id = task_id
        self.size_bytes = size_bytes
        self.max_bytes = max_bytes
        super().__init__(
            f"Output for task {task_id!r} exceeds the per-output cap: "
            f"{size_bytes} bytes > {max_bytes} byte cap."
        )


class _AttachmentTooLarge(ValueError):
    """Spec 019 FR-D-002 — provider-internal cap-violation signal."""

    __slots__ = ("task_id", "attachment_key", "size_bytes", "max_bytes")

    def __init__(
        self,
        task_id: str,
        attachment_key: str,
        size_bytes: int,
        max_bytes: int,
    ) -> None:
        self.task_id = task_id
        self.attachment_key = attachment_key
        self.size_bytes = size_bytes
        self.max_bytes = max_bytes
        super().__init__(
            f"Attachment {attachment_key!r} on task {task_id!r} is too large: "
            f"{size_bytes} bytes > {max_bytes} byte per-attachment cap."
        )


class _AttachmentLimitExceeded(ValueError):
    """Spec 019 FR-D-003 — provider-internal per-task attachment-count cap violation."""

    __slots__ = ("task_id", "current_count", "max_count")

    def __init__(self, task_id: str, current_count: int, max_count: int) -> None:
        self.task_id = task_id
        self.current_count = current_count
        self.max_count = max_count
        super().__init__(
            f"Task {task_id!r} already has {current_count} attachments; "
            f"per-task cap is {max_count}."
        )


# Backward-compatible aliases for any in-tree caller that still imports
# the pre-019 names.
AttachmentTooLarge = _AttachmentTooLarge
AttachmentLimitExceeded = _AttachmentLimitExceeded


# =========================================================================
# Spec 022 — additions to the exception taxonomy
# =========================================================================

try:
    from typing import Literal, TypedDict
except ImportError:  # pragma: no cover
    from typing_extensions import Literal, TypedDict  # type: ignore[assignment]


class TaskDeferred(Exception):
    """Raised when handler called ``ctx.exit_for_recovery()`` (spec 022 FR-039).

    Semantically DISTINCT from :class:`TaskCancelled` — the task stays
    ``in_progress`` and recovery re-invokes the handler in a future
    lifetime. Bare exception per FR-077.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__("Task deferred to next process lifetime")


class TaskErrorDict(TypedDict):
    """Shape of :attr:`TaskFailed.error` for a normal handler-raise failure (spec 022 FR-071)."""

    type: str
    message: str
    traceback: str


class TaskExhaustedRetriesErrorDict(TypedDict):
    """Shape of :attr:`TaskFailed.error` when the retry budget was exhausted (spec 022 FR-071)."""

    type: Literal["exhausted_retries"]
    attempts: int
    last_error: str
    last_error_type: str
    traceback: str

