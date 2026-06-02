# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""TaskResult wrapper for durable task completion and suspension outcomes."""

from __future__ import annotations

from typing import Generic, Literal, TypeVar

Output = TypeVar("Output")


class TaskResult(Generic[Output]):
    """Result of a durable task execution.

    Wraps both completion and suspension outcomes. Failures, cancellation,
    and termination are still raised as exceptions.

    Spec 016 FR-010 (US5): ``TaskResult.status`` is the Literal
    ``"completed" | "suspended"`` — two values only. The legacy third
    value ``"superseded"`` is gone; steering is plain multi-turn (see
    the developer guide §4 Steering), so the first turn's caller
    observes whatever natural outcome the handler produced
    (``"suspended"`` if the handler suspended with an output, or
    ``"completed"`` if it returned; raised exceptions cover failure /
    cancel paths). The steerer's future resolves with the next turn's
    outcome or raises ``TaskConflictError`` if the handler ended the
    task before draining.

    :param task_id: The task identifier.
    :type task_id: str
    :param output: The task output value (typed for completion, optional for suspension).
    :type output: Output | None
    :param status: Whether the task completed or suspended.
    :type status: ~typing.Literal["completed", "suspended"]
    :param suspension_reason: Human-readable suspension reason, if suspended.
    :type suspension_reason: str | None
    """

    __slots__ = ("task_id", "output", "status", "suspension_reason")

    def __init__(
        self,
        *,
        task_id: str,
        output: Output | None = None,
        status: Literal["completed", "suspended"],
        suspension_reason: str | None = None,
    ) -> None:
        self.task_id = task_id
        self.output = output
        self.status: Literal["completed", "suspended"] = status
        self.suspension_reason = suspension_reason

    @property
    def is_completed(self) -> bool:
        """Whether the task completed successfully.

        :return: True if the task completed.
        :rtype: bool
        """
        return self.status == "completed"

    @property
    def is_suspended(self) -> bool:
        """Whether the task was suspended.

        :return: True if the task is suspended.
        :rtype: bool
        """
        return self.status == "suspended"

    @property
    def is_superseded(self) -> bool:
        """**DEPRECATED**: always returns False after spec 016 (US5 / FR-010).

        Steering is now plain multi-turn — the displaced caller observes
        the natural ``status="suspended"`` outcome with the handler's
        emitted output, not a separate ``"superseded"`` value. This
        property is retained as a compatibility shim that always returns
        False so existing callers do not crash on attribute access;
        callers MUST update to branch on ``is_suspended`` / ``is_completed``
        and inspect ``output`` directly. The property will be removed
        in a future release.

        :return: Always False.
        :rtype: bool
        """
        return False

    def __repr__(self) -> str:
        output_repr = repr(self.output)
        if len(output_repr) > 60:
            output_repr = output_repr[:57] + "..."
        parts = [
            f"TaskResult(task_id={self.task_id!r}, status={self.status!r}, output={output_repr}"
        ]
        if self.suspension_reason is not None:
            parts.append(f", suspension_reason={self.suspension_reason!r}")
        parts.append(")")
        return "".join(parts)
