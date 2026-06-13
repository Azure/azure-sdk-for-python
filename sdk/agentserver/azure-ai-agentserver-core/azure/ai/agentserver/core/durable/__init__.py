# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Durable task subsystem for crash-resilient long-running agents.

Provides the :func:`task` and :func:`multi_turn_task` decorators (spec 022)
plus supporting types for building Azure AI Hosted Agents that survive
container crashes, OOM kills, and redeployments.

Key features (spec 022):

- **Two decorators** — ``@task`` (one-shot, single run, ephemeral) and
  ``@multi_turn_task`` (chain — every ``return X`` is one turn; chain
  stays alive in ``suspended`` between turns).
- **Lifecycle automation** — ``.run()`` and ``.start()`` automatically
  start, resume, or recover tasks based on their current state.
- **Entry mode** — ``ctx.entry_mode`` tells the handler whether it was
  entered fresh, resumed from suspension, or recovered from a crash.
- **RetryPolicy** — configurable retry with exponential, fixed, or linear
  backoff (see :class:`RetryPolicy` presets).
- **Streaming** lives in :mod:`azure.ai.agentserver.core.streaming`
  (spec 017): handlers call ``stream = await streams.get_or_create(invocation_id)``
  to obtain a stream handle; ``TaskRun`` itself is NOT iterable.

Public API::

    from azure.ai.agentserver.core.durable import (
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
)
from ._metadata import JSONValue, TaskMetadata
from ._retry import (
    RetryPolicy,
    exponential_backoff,
    fixed_delay,
    linear_backoff,
    no_retry,
)
from ._run import TaskRun  # Suspended kept internal-only; reach via _run module directly

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
    # Decorators + task classes (spec 022 — class split per FR-069)
    "task",
    "multi_turn_task",
    "Task",
    "MultiTurnTask",
    # Context + metadata
    "TaskContext",
    "TaskMetadata",
    "EntryMode",
    # Type aliases + TypedDicts (spec 022 FR-070 / FR-071)
    "JSONValue",
    "TaskErrorDict",
    "TaskExhaustedRetriesErrorDict",
    # TaskRun (slim shape per spec 022 FR-047 lands in Phase 5)
    "TaskRun",
    # Retry
    "RetryPolicy",
    "exponential_backoff",
    "fixed_delay",
    "linear_backoff",
    "no_retry",
    # Public exceptions
    "TaskFailed",
    "TaskCancelled",
    "TaskDeferred",  # NEW spec 022 FR-039
    "TaskConflictError",
    "LastInputIdPreconditionFailed",
    "SteeringQueueFull",
    "InputTooLarge",
]
