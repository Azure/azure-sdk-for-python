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
- **Source tracking** — attach immutable provenance metadata at task
  creation time via the ``source`` parameter.

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
    EtagConflict,
    LastInputIdPreconditionFailed,
    SteeringQueueFull,
    TaskCancelled,
    TaskConflictError,
    TaskFailed,
    TaskNotFound,
    TaskPreconditionFailed,
    TaskTerminated,
)
from ._metadata import TaskMetadata
from ._models import TaskStatus
from ._result import TaskResult
from ._retry import RetryPolicy
from ._run import Suspended, TaskRun
from ._stream import QueueStreamHandler, StreamHandler, StreamHandlerFactory

# Spec 016 FR-022 (US6): TaskTerminated is being removed from the public
# surface. It is dropped from __all__ here as preparatory work; the
# class itself and the cancellation-branch plumbing in _manager.py /
# _run.py are removed by T082-T085 of spec 016. The import above is
# retained until those tasks land so any pre-existing internal call
# sites continue to function during the rollout window of the spec
# implementation PR.
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
