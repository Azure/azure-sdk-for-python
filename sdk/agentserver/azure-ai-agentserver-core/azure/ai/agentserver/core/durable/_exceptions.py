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

    Spec 022 FR-076: the canonical shape carries only ``actual_last_input_id``
    (the value persisted on the record at the time of the precondition check).
    The caller already knows what they passed via ``if_last_input_id=`` so
    ``expected_last_input_id`` is redundant; ``task_id`` is omitted too per
    FR-077 (caller has it from the call site / run handle).

    Backward-compatible positional / keyword construction is preserved during
    the transition window — both shapes work; the legacy form emits a
    DeprecationWarning.

    :param actual_last_input_id: The value the framework currently has stored
        for the chain's ``_last_input_id``.
    :type actual_last_input_id: str | None
    """

    __slots__ = ("expected_last_input_id", "actual_last_input_id")

    def __init__(
        self,
        *args: Any,
        actual_last_input_id: str | None = None,
        expected_last_input_id: str | None = None,
        task_id: str | None = None,
    ) -> None:
        # Spec 022 FR-076 shape: (actual_last_input_id) only.
        # Legacy shape: (task_id, expected_last_input_id, actual_last_input_id).
        if args:
            if len(args) == 1 and actual_last_input_id is None:
                # New shape positional: LastInputIdPreconditionFailed("xx")
                actual_last_input_id = args[0]
            elif len(args) == 3:
                # Legacy shape positional: LastInputIdPreconditionFailed(task_id, expected, actual)
                import warnings
                warnings.warn(
                    "LastInputIdPreconditionFailed(task_id, expected, actual) "
                    "is deprecated per spec 022 FR-076; use the keyword-only "
                    "actual_last_input_id= form.",
                    DeprecationWarning,
                    stacklevel=2,
                )
                task_id = args[0]
                expected_last_input_id = args[1]
                actual_last_input_id = args[2]
            else:
                raise TypeError(
                    f"LastInputIdPreconditionFailed: invalid positional args {args}; "
                    f"use LastInputIdPreconditionFailed(actual_last_input_id=...)"
                )
        self.expected_last_input_id = expected_last_input_id
        self.actual_last_input_id = actual_last_input_id
        # Build a message that works for both legacy and new shapes.
        if task_id is not None:
            msg = (
                f"Task {task_id!r}: if_last_input_id precondition failed — "
                f"expected last_input_id={expected_last_input_id!r}, "
                f"actual={actual_last_input_id!r}"
            )
            # Legacy super-init takes task_id.
            super().__init__(task_id, msg)
        else:
            msg = (
                f"if_last_input_id precondition failed: "
                f"actual last_input_id={actual_last_input_id!r}"
            )
            # New super-init: task_id-less.
            # TaskPreconditionFailed currently requires task_id; pass empty.
            super().__init__("", msg)


# --- Spec 018 (task attachments) — input + attachment size/count errors ----


class InputTooLarge(ValueError):
    """Raised when an input's serialized size exceeds the per-input cap.

    The framework supports per-input payloads up to 2 MB (after JSON
    serialization), for both the initial function input and each
    queued steering input. An input whose serialized size exceeds
    this cap is rejected client-side before any network call, with
    this exception.

    If you have a use case that needs > 2 MB per input, externalize
    it (write to blob storage, pass a reference) and treat the
    reference as your input.

    :param task_id: The task identifier this input was bound for.
    :type task_id: str
    :param size_bytes: The observed serialized size of the input.
    :type size_bytes: int
    :param max_bytes: The per-input cap (2 MB).
    :type max_bytes: int
    """

    __slots__ = ("task_id", "size_bytes", "max_bytes")

    def __init__(self, task_id: str, size_bytes: int, max_bytes: int) -> None:
        self.task_id = task_id
        self.size_bytes = size_bytes
        self.max_bytes = max_bytes
        super().__init__(
            f"Input for task {task_id!r} exceeds the per-input cap: "
            f"{size_bytes} bytes > {max_bytes} byte cap. Externalize the "
            f"value (e.g., to blob storage) and pass a reference instead."
        )


# Spec 019 FR-D-001 — public output-size violation (developer-facing).
class OutputTooLarge(ValueError):
    """Raised when an output's serialized size exceeds the per-output cap.

    The framework supports per-output values up to 2 MB (after JSON
    serialization). Outputs are stored entirely in
    ``attachments["_output"]`` (the always-attachment rule) — they
    never consume the shared payload budget — but they share the
    per-attachment 2 MB cap. An output whose serialized form
    exceeds the cap is rejected client-side before any network call,
    with this exception.

    If you need to return more than 2 MB per call, externalize the
    value (write to blob storage) and return a reference instead.

    :param task_id: The task identifier this output was bound for.
    :type task_id: str
    :param size_bytes: The observed serialized size of the output.
    :type size_bytes: int
    :param max_bytes: The per-output cap (2 MB).
    :type max_bytes: int
    """

    __slots__ = ("task_id", "size_bytes", "max_bytes")

    def __init__(self, task_id: str, size_bytes: int, max_bytes: int) -> None:
        self.task_id = task_id
        self.size_bytes = size_bytes
        self.max_bytes = max_bytes
        super().__init__(
            f"Output for task {task_id!r} exceeds the per-output cap: "
            f"{size_bytes} bytes > {max_bytes} byte cap. Externalize the "
            f"value (e.g., to blob storage) and return a reference instead."
        )


class _AttachmentTooLarge(ValueError):
    """Spec 019 FR-D-002 — provider-internal cap-violation signal.

    Renamed from the previously-public ``AttachmentTooLarge``. The
    framework catches this at attachment-write sites and re-raises a
    developer-facing exception (``InputTooLarge`` for ``_input`` /
    ``_steering_input_<seq>`` keys; ``OutputTooLarge`` for ``_output``)
    based on the attachment-key prefix dispatcher in ``_attachments.py``.

    Developers MUST NOT import this directly — it is leading-
    underscored, absent from ``durable/__init__.py``'s ``__all__``,
    and represents a framework implementation concept (the storage-
    layer attachment) developers never name.

    :param task_id: The task identifier this attachment was bound for.
    :type task_id: str
    :param attachment_key: The attachment key that exceeded the cap.
    :type attachment_key: str
    :param size_bytes: The observed serialized size of the attachment value.
    :type size_bytes: int
    :param max_bytes: The per-attachment cap (default 2 MB).
    :type max_bytes: int
    """

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
    """Spec 019 FR-D-003 — provider-internal per-task attachment-count
    cap violation.

    Renamed from the previously-public ``AttachmentLimitExceeded``.
    Unreachable in normal framework operation (worst-case framework
    attachment usage is 1 ``_input`` + 9 ``_steering_input_*`` + 1
    ``_output`` = 11 of 20 slots; see design spec §23.2). If it
    propagates from a provider, the framework converts it to
    ``RuntimeError`` at the boundary.

    Developers MUST NOT import this directly.

    :param task_id: The task identifier.
    :type task_id: str
    :param current_count: The number of attachments currently on the task.
    :type current_count: int
    :param max_count: The per-task attachment count cap (default 20).
    :type max_count: int
    """

    __slots__ = ("task_id", "current_count", "max_count")

    def __init__(self, task_id: str, current_count: int, max_count: int) -> None:
        self.task_id = task_id
        self.current_count = current_count
        self.max_count = max_count
        super().__init__(
            f"Task {task_id!r} already has {current_count} attachments; "
            f"per-task cap is {max_count}. Cannot add another."
        )


# Backward-compatible aliases for any in-tree caller that still
# imports the pre-019 names. These are intentionally NOT exported
# from ``durable/__init__.py``; the rename is the public-surface
# change, and all framework call sites are migrated. Removing the
# aliases is safe once any out-of-tree dependents have updated.
AttachmentTooLarge = _AttachmentTooLarge
AttachmentLimitExceeded = _AttachmentLimitExceeded


# =========================================================================
# Spec 022 — additions to the exception taxonomy
# =========================================================================
#
# Per spec 022 FR-039 / FR-058 / FR-070 / FR-071 / FR-077.
# - `TaskDeferred` is a NEW exception for `ctx.exit_for_recovery()`
#   (semantically distinct from `TaskCancelled` — task stays in_progress).
# - `TaskErrorDict` + `TaskExhaustedRetriesErrorDict` are public TypedDicts
#   for `TaskFailed.error`.

try:
    from typing import Literal, TypedDict
except ImportError:  # pragma: no cover  -- Python 3.8 doesn't have TypedDict at typing
    from typing_extensions import Literal, TypedDict  # type: ignore[assignment]


class TaskDeferred(Exception):
    """Raised when handler called ``ctx.exit_for_recovery()`` (spec 022 FR-039).

    Semantically DISTINCT from :class:`TaskCancelled`:

    - ``TaskCancelled`` means the task / turn is terminated.
    - ``TaskDeferred`` means THIS lifetime is deferring to the next; the
      task stays ``in_progress`` and the recovery scanner re-invokes the
      handler in a future process lifetime.

    A future caller can attach to the deferred task via
    ``multi_turn_task.get_active_run(task_id, input_id)`` once the scanner
    has reclaimed (the ``input_id`` remains the same — recovery uses the
    persisted input per spec 021 Q13).

    Bare exception — no fields (FR-077). Caller has ``task_id`` / ``input_id``
    from the run handle that raised this.
    """


class TaskErrorDict(TypedDict):
    """Shape of :attr:`TaskFailed.error` for a normal handler-raise failure (spec 022 FR-071).

    :param type: The exception class name (e.g., ``"ValueError"``).
    :param message: ``str(exc)``.
    :param traceback: Formatted traceback via ``traceback.format_exc()``.
    """

    type: str
    message: str
    traceback: str


class TaskExhaustedRetriesErrorDict(TypedDict):
    """Shape of :attr:`TaskFailed.error` when the retry budget was exhausted (spec 022 FR-071).

    :param type: Always ``"exhausted_retries"``.
    :param attempts: Number of attempts made (``>= max_attempts``).
    :param last_error: ``str(last_exc)``.
    :param last_error_type: ``type(last_exc).__name__``.
    :param traceback: Formatted traceback of the last attempt.
    """

    type: Literal["exhausted_retries"]
    attempts: int
    last_error: str
    last_error_type: str
    traceback: str
