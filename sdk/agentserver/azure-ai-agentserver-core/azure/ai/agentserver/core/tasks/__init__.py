# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Task subsystem for crash-resilient long-running agents.

Provides the :func:`task` and :func:`multi_turn_task` decorators
plus supporting types for building Azure AI Hosted Agents that survive
container crashes, OOM kills, and redeployments.

Key features:

- **Two decorators** — ``@task`` (one-shot, single run, ephemeral) and
  ``@multi_turn_task`` (chain — every ``return X`` is one turn; chain
  stays alive in ``suspended`` between turns).
- **Lifecycle automation** — ``.run()`` and ``.start()`` automatically
  start, resume, or recover tasks based on their current state.
- **Entry mode** — ``ctx.entry_mode`` tells the handler whether it was
  entered fresh, resumed from suspension, or recovered from a crash.
- **RetryPolicy** — configurable retry with exponential, fixed, or linear
  backoff (see :class:`RetryPolicy` presets).
- **Streaming** lives in :mod:`azure.ai.agentserver.core.streaming`;
  handlers call ``stream = await streams.get_or_create(invocation_id)``
  to obtain a stream handle; ``TaskRun`` itself is NOT iterable.

Public API::

    from azure.ai.agentserver.core.tasks import (
        task,
        multi_turn_task,
        Task,
        MultiTurnTask,
        RetryPolicy,
        TaskContext,
        TaskMetadata,
        TaskRun,
        TaskFailed,
        TaskCancelled,
        TaskDeferred,
        TaskConflictError,
        LastInputIdPreconditionFailed,
        SteeringQueueFull,
        InputTooLarge,
        JSONValue,
        TaskErrorDict,
        TaskExhaustedRetriesErrorDict,
        EntryMode,
    )
"""

from ._context import EntryMode, TaskContext
from ._decorator import MultiTurnTask, Task, multi_turn_task, task
from ._enablement import resilient_tasks_enabled, set_resilient_tasks_enabled
from ._exceptions import (
    InputTooLarge,
    LastInputIdPreconditionFailed,
    SteeringQueueFull,
    TaskCancelled,
    TaskConflictError,
    TaskDeferred,
    TaskErrorDict,
    TaskExhaustedRetriesErrorDict,
    TaskFailed,
    TaskManagerNotInitialized,
)
from ._metadata import JSONValue, TaskMetadata
from ._retry import RetryPolicy
from ._run import TaskRun

# Streaming lives in `azure.ai.agentserver.core.streaming` as a peer
# subpackage with a registry-based lifecycle model. The resilient task
# decorators accept no streaming-related kwarg; ``TaskContext`` has
# no streaming attribute. Handlers explicitly do
# ``stream = await streams.get_or_create(invocation_id)`` to obtain a
# stream handle for the current turn.
#
# Attachment-vocabulary errors (``_AttachmentTooLarge``,
# ``_AttachmentLimitExceeded``) are framework-internal — they are
# caught at attachment-write sites and re-raised as the developer-
# facing ``InputTooLarge`` based on the attachment-key prefix.
__all__ = [
    # Decorators + task classes
    "task",
    "multi_turn_task",
    "Task",
    "MultiTurnTask",
    # Enablement switch
    "set_resilient_tasks_enabled",
    "resilient_tasks_enabled",
    # Context + metadata
    "TaskContext",
    "TaskMetadata",
    "EntryMode",
    # Type aliases + TypedDicts
    "JSONValue",
    "TaskErrorDict",
    "TaskExhaustedRetriesErrorDict",
    # TaskRun
    "TaskRun",
    # Retry
    "RetryPolicy",
    # Public exceptions
    "TaskFailed",
    "TaskCancelled",
    "TaskDeferred",
    "TaskConflictError",
    "LastInputIdPreconditionFailed",
    "SteeringQueueFull",
    "InputTooLarge",
    "TaskManagerNotInitialized",
]
