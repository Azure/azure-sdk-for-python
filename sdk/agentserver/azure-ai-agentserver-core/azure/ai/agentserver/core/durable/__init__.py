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
    InputTooLarge,
    LastInputIdPreconditionFailed,
    OutputTooLarge,
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

# Spec 016 FR-022 + SC-014 (US6): TaskTerminated is fully removed from
# the public surface — importing it from this package now raises
# ImportError as the spec requires. The class itself is deleted from
# `_exceptions.py`. Internal call sites that previously raised it have
# been switched to TaskCancelled (`_manager.py` cancelled-error path).
#
# Spec 017 FR-014/FR-015: The old StreamHandler/QueueStreamHandler/
# StreamHandlerFactory surface (formerly in `_stream.py`) is removed.
# Streaming now lives in `azure.ai.agentserver.core.streaming` as a
# peer subpackage with a registry-based lifecycle model. `@task`
# accepts no streaming-related kwarg; `TaskContext` has no streaming
# attribute. Handlers explicitly do
# ``stream = await streams.get_or_create(invocation_id)`` (per-turn id
# from ``ctx.input``).
#
# Spec 019 FR-D-002 / FR-D-003: AttachmentTooLarge and
# AttachmentLimitExceeded are NOT exported. They were renamed to
# leading-underscore internal exceptions (_AttachmentTooLarge,
# _AttachmentLimitExceeded). The framework catches the internal form
# at write sites and re-raises the developer-facing equivalent
# (InputTooLarge / OutputTooLarge) based on the attachment-key prefix
# (_attachments._remap_attachment_error).
__all__ = [
    "task",
    "Task",
    "RetryPolicy",
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
    "InputTooLarge",
    "OutputTooLarge",
]
