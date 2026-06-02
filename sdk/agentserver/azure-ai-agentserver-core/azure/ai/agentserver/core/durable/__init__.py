# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Durable task subsystem for crash-resilient long-running agents.

Provides the :func:`task` decorator and supporting types for
building Azure AI Hosted Agents that survive container crashes,
OOM kills, and redeployments.

Key features:

- **Lifecycle automation** — ``.run()`` and ``.start()`` automatically
  start, resume, or recover tasks based on their current state.
- **Entry mode** — ``ctx.entry_mode`` tells the function whether it was
  entered fresh, resumed from suspension, or recovered from a crash.
- **RetryPolicy** — configurable retry with exponential, fixed, or linear
  backoff (see :class:`RetryPolicy` presets).
- **Streaming** — emit incremental output via ``ctx.stream()`` and consume
  with ``async for chunk in task_run``.

Public API::

    from azure.ai.agentserver.core.durable import (
        task,
        Task,
        RetryPolicy,
        TaskContext,
        TaskMetadata,
        TaskResult,
        TaskRun,
        Suspended,
        TaskStatus,
        TaskFailed,
        TaskCancelled,
        TaskNotFound,
        TaskConflictError,
        EntryMode,
    )
"""

from ._context import EntryMode, TaskContext
from ._decorator import Task, task
from ._exceptions import (
    LastInputIdPreconditionFailed,
    SteeringQueueFull,
    TaskCancelled,
    TaskConflictError,
    TaskFailed,
    TaskNotFound,
    TaskPreconditionFailed,
)
from ._metadata import TaskMetadata
from ._models import TaskStatus
from ._result import TaskResult
from ._retry import RetryPolicy
from ._run import Suspended, TaskRun
from ._stream import QueueStreamHandler, StreamHandler, StreamHandlerFactory

# Spec 016 FR-022 + SC-014 (US6): TaskTerminated is fully removed from
# the public surface — importing it from this package now raises
# ImportError as the spec requires. The class itself is deleted from
# `_exceptions.py`. Internal call sites that previously raised it have
# been switched to TaskCancelled (`_manager.py` cancelled-error path).
__all__ = [
    "task",
    "Task",
    "QueueStreamHandler",
    "RetryPolicy",
    "StreamHandler",
    "StreamHandlerFactory",
    "TaskContext",
    "TaskMetadata",
    "TaskResult",
    "TaskRun",
    "Suspended",
    "TaskStatus",
    "TaskFailed",
    "TaskCancelled",
    "TaskNotFound",
    "TaskConflictError",
    "LastInputIdPreconditionFailed",
    "SteeringQueueFull",
    "TaskPreconditionFailed",
    "EntryMode",
]
