# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Durable task subsystem for crash-resilient long-running agents.

Provides the :func:`durable_task` decorator and supporting types for
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
- **Source tracking** — attach immutable provenance metadata at task
  creation time via the ``source`` parameter.

Public API::

    from azure.ai.agentserver.core.durable import (
        durable_task,
        DurableTask,
        RetryPolicy,
        TaskContext,
        TaskMetadata,
        TaskResult,
        TaskRun,
        Suspended,
        TaskStatus,
        TaskFailed,
        TaskSuspended,
        TaskCancelled,
        TaskNotFound,
        TaskConflictError,
        TaskTerminated,
        EntryMode,
        TaskInfo,
    )
"""

from ._context import EntryMode, TaskContext
from ._decorator import DurableTask, DurableTaskOptions, durable_task
from ._exceptions import (
    EtagConflict,
    SteeringQueueFull,
    TaskCancelled,
    TaskConflictError,
    TaskFailed,
    TaskNotFound,
    TaskSuspended,
    TaskTerminated,
)
from ._metadata import TaskMetadata
from ._models import TaskInfo, TaskStatus
from ._result import TaskResult
from ._retry import RetryPolicy
from ._run import Suspended, TaskRun
from ._stream import QueueStreamHandler, StreamHandler

__all__ = [
    "durable_task",
    "DurableTask",
    "DurableTaskOptions",
    "QueueStreamHandler",
    "RetryPolicy",
    "StreamHandler",
    "TaskContext",
    "TaskMetadata",
    "TaskResult",
    "TaskRun",
    "Suspended",
    "TaskStatus",
    "TaskFailed",
    "TaskSuspended",
    "TaskCancelled",
    "TaskNotFound",
    "TaskConflictError",
    "TaskTerminated",
    "EtagConflict",
    "SteeringQueueFull",
    "EntryMode",
    "TaskInfo",
]
