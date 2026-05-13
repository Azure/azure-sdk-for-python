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

    :param task_id: The task identifier.
    :type task_id: str
    :param output: The task output value (typed for completion, optional for suspension).
    :type output: Output | None
    :param status: Whether the task completed, suspended, or was superseded.
    :type status: ~typing.Literal["completed", "suspended", "superseded"]
    :param suspension_reason: Human-readable suspension reason, if suspended.
    :type suspension_reason: str | None
    """

    __slots__ = ("task_id", "output", "status", "suspension_reason")

    def __init__(
        self,
        *,
        task_id: str,
        output: Output | None = None,
        status: Literal["completed", "suspended", "superseded"],
        suspension_reason: str | None = None,
    ) -> None:
        self.task_id = task_id
        self.output = output
        self.status: Literal["completed", "suspended", "superseded"] = status
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
        """Whether the generation was superseded by a steering input.

        :return: True if this generation was cancelled by a newer input.
        :rtype: bool
        """
        return self.status == "superseded"

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
