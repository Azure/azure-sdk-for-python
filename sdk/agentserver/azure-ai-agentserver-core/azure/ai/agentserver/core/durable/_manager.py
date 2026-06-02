# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""TaskManager — lifecycle orchestration for durable tasks.

Manages task creation, lease acquisition, execution, recovery, and
shutdown. One instance per ``AgentServerHost``, accessed via the
module-level ``get_task_manager()`` function.
"""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import logging
import traceback
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any, Optional, TypeVar

from .._config import AgentConfig
from ._client import TransportClassifiedError
from ._context import EntryMode, TaskContext
from ._decorator import TaskOptions, _deserialize_input, _serialize_input
from ._exceptions import TaskConflictError, TaskFailed, TaskNotFound
from ._lease import derive_lease_owner, generate_instance_id, lease_renewal_loop
from ._metadata import TaskMetadata
from ._models import TaskCreateRequest, TaskInfo, TaskPatchRequest, TaskStatus
from ._provider import TaskProvider
from ._result import TaskResult
from ._retry import RetryPolicy
from ._run import Suspended, TaskRun
from ._stream import QueueStreamHandler, StreamHandler
from .._version import VERSION as _CORE_VERSION
from .._server_version import build_server_version as _build_server_version

logger = logging.getLogger("azure.ai.agentserver.durable")

#: Auto-stamped source type for all tasks created by this framework.
_SOURCE_TYPE = "agentserver.task"

#: Reserved tag key for task name filtering via the LIST API.
_TAG_TASK_NAME = "_task_name"

#: Spec 015 Phase 3 (FR-006) — default lease TTL. The per-task
#: ``lease_duration_seconds`` knob was demoted (no developer use case justified
#: exposing it on ``@task``). This constant is the framework's choice.
_DEFAULT_LEASE_SECONDS = 60

#: Pre-computed server version segment for source stamps.
_SOURCE_SERVER_VERSION = _build_server_version(
    "azure-ai-agentserver-core", _CORE_VERSION
)

Input = TypeVar("Input")
Output = TypeVar("Output")

# Module-level manager singleton
_manager: TaskManager | None = None


def _is_evicted(exc: BaseException) -> bool:
    """Return True if ``exc`` is the FR-006 eviction-classified rejection.

    Spec 016 helper used by every store-write call site that must
    funnel through the FR-007 / FR-008 local-cleanup sequence on
    orphan-sandbox eviction. The HostedTaskProvider raises
    ``TransportClassifiedError(classification="evicted")`` after the
    pipeline classifier maps an HTTP 409 + ``binding_mismatch`` body;
    in-test stubs raise the same typed exception so the framework's
    cleanup runs identically against both.
    """
    return (
        isinstance(exc, TransportClassifiedError)
        and getattr(exc, "classification", None) == "evicted"
    )


# Spec 016 FR-002 Layer 2 / FR-009 / gap-list §FR-009:
# periodic background scan interval. Module-level constant so tests
# can monkey-patch it to a small value for deterministic exercise
# without adding a public surface to TaskManager. Default ~300s
# matches the spec's "internal-only interval" requirement.
_PERIODIC_RECOVERY_INTERVAL_SECONDS: float = 300.0

# Spec 016 §FR-002-retries (gap-list): bounded retry budget for the
# transient-error path in the startup scan / inline reclaim.
# Exponential backoff: 0.2 → 0.4 → 0.8 across attempts 1..3.
_RECLAIM_MAX_RETRIES: int = 3
_RECLAIM_BACKOFF_BASE_SECONDS: float = 0.2


def _resolve_queued_steerers_on_terminal(
    pending_steering_futures: dict[str, list["asyncio.Future[Any]"]],
    task_id: str,
    *,
    current_status: str,
) -> None:
    """Spec 016 FR-012 (US5) helper.

    When a steerable task terminates (handler returned a value or
    raised), any callers that queued a steering input via
    ``.start()`` (and got back a TaskRun bound to a future from
    ``_pending_steering_futures``) MUST receive ``TaskConflictError``
    on their ``.result()`` — the same shape a fresh ``.start()``
    against an already-terminal task would raise.

    Pops every queued steerer future for ``task_id`` and resolves
    each with ``TaskConflictError(current_status=current_status)``.
    """
    from ._exceptions import TaskConflictError  # local to avoid cycle

    queued = pending_steering_futures.pop(task_id, [])
    for fut in queued:
        if not fut.done():
            fut.set_exception(TaskConflictError(task_id, current_status))


def _lease_is_dead(
    task_info: Any,
    *,
    this_lease_owner: str,
    active_locally: bool,
) -> bool:
    """Determine whether an in-progress record's lease is dead per FR-004.

    Spec 016 FR-004: a lease is "live" only if EITHER ownership matches
    this process AND an in-memory active entry tracks it (so we know
    the local execution is running), OR the lease ownership belongs to
    this process AND the expiry has not passed. A lease is "dead"
    otherwise — i.e., the previous lifetime is no longer authoritative
    and the record is eligible for reclaim.

    For the LocalFileTaskProvider used in tests (no real expiry
    tracking), absence of a local in-memory entry combined with a
    backdated ``updated_at`` suffices.

    :param task_info: The persisted record.
    :keyword this_lease_owner: This process's lease-owner string
        (from :class:`TaskManager`).
    :keyword active_locally: True if this process has an in-memory
        ``_ActiveTask`` entry tracking the record.
    :return: True if the lease is dead.
    """
    if active_locally:
        # We are actively executing it; lease is definitely live in
        # this process.
        return False
    # Ownership mismatch: previous lifetime owned the record.
    owner = getattr(task_info, "lease_owner", None) or ""
    if owner and owner != this_lease_owner:
        return True
    # Same owner but no local in-memory entry → previous lifetime
    # crashed; lease is dead by inference (no live executor).
    if owner == this_lease_owner and not active_locally:
        return True
    # No owner recorded → dead by definition.
    return True


def get_task_manager() -> TaskManager:
    """Return the active TaskManager singleton.

    :raises RuntimeError: If no manager has been initialized.
    :return: The active manager.
    :rtype: TaskManager
    """
    if _manager is None:
        raise RuntimeError(
            "TaskManager not initialized. Ensure durable tasks "
            "are enabled on the AgentServerHost."  # pylint: disable=implicit-str-concat
        )
    return _manager


def set_task_manager(manager: TaskManager | None) -> None:
    """Set the module-level TaskManager singleton.

    Called by ``AgentServerHost`` during startup/shutdown.

    :param manager: The manager to set, or ``None`` to clear.
    :type manager: TaskManager | None
    """
    global _manager  # pylint: disable=global-statement
    _manager = manager


class _ActiveTask:  # pylint: disable=too-many-instance-attributes
    """In-memory tracking for a running task."""

    __slots__ = (
        "task_id",
        "fn_name",
        "context",
        "execution_task",
        "renewal_task",
        "renewal_cancel",
        "result_future",
        "terminate_event",
        "fn",
        "input_type",
        "opts",
        "retry",
    )

    def __init__(
        self,
        task_id: str,
        fn_name: str,
        context: TaskContext[Any],
        execution_task: asyncio.Task[Any],
        renewal_task: asyncio.Task[None] | None,
        renewal_cancel: asyncio.Event,
        result_future: asyncio.Future[Any],
        terminate_event: asyncio.Event | None = None,
        fn: Callable[..., Awaitable[Any]] | None = None,
        input_type: type[Any] | None = None,
        opts: TaskOptions | None = None,
        retry: RetryPolicy | None = None,
    ) -> None:
        self.task_id = task_id
        self.fn_name = fn_name
        self.context = context
        self.execution_task = execution_task
        self.renewal_task = renewal_task
        self.renewal_cancel = renewal_cancel
        self.result_future = result_future
        self.terminate_event = terminate_event or asyncio.Event()
        self.fn = fn
        self.input_type = input_type
        self.opts = opts
        self.retry = retry


class TaskManager:
    """Lifecycle orchestrator for durable tasks.

    Manages provider selection, task creation, lease management,
    execution dispatch, crash recovery, and graceful shutdown.

    :param config: Resolved agent configuration.
    :type config: AgentConfig
    :param provider: Optional explicit provider (for testing).
    :type provider: TaskProvider | None
    :param shutdown_event: Shared shutdown event from the host.
    :type shutdown_event: asyncio.Event | None
    :param shutdown_grace_seconds: Seconds to wait for tasks to checkpoint
        before force-expiring leases during shutdown. Defaults to 25.0.
    :type shutdown_grace_seconds: float
    """

    def __init__(
        self,
        config: AgentConfig,
        *,
        provider: TaskProvider | None = None,
        shutdown_event: asyncio.Event | None = None,
        shutdown_grace_seconds: float = 25.0,
    ) -> None:
        self._config = config
        self._provider = provider or self._create_provider(config)
        self._active_tasks: dict[str, _ActiveTask] = {}
        self._resume_callbacks: dict[str, Callable[..., Any]] = {}
        self._resume_opts: dict[str, TaskOptions] = {}
        self._lease_owner = derive_lease_owner(
            config.agent_name or "unknown-agent",
            config.session_id or "local",
        )
        self._instance_id = generate_instance_id()
        self._shutdown_event = shutdown_event or asyncio.Event()
        self._shutdown_grace_seconds = shutdown_grace_seconds
        self._active_generation_future: dict[str, asyncio.Future[Any]] = {}
        self._pending_steering_futures: dict[str, list[asyncio.Future[Any]]] = {}
        # Spec 016 FR-002 Layer 2: periodic recovery scan task. Created
        # at startup() time; cancelled at shutdown().
        self._periodic_recovery_task: asyncio.Task[None] | None = None

    @staticmethod
    def _build_source(fn_name: str) -> dict[str, str]:
        """Build the framework-owned source stamp for a task.

        The ``fn_name`` is the developer-provided ``name`` from the decorator
        (or ``fn.__qualname__`` when omitted).  It serves as the **stable
        identity anchor** — recovery routing matches ``source.name`` against
        registered callbacks to dispatch recovered tasks back to the correct
        function.

        :param fn_name: The task name (from ``@task(name=...)``).
        :type fn_name: str
        :return: Source metadata dict.
        :rtype: dict[str, str]
        """
        return {
            "type": _SOURCE_TYPE,
            "name": fn_name,
            "server_version": _SOURCE_SERVER_VERSION,
        }

    @staticmethod
    def _create_provider(config: AgentConfig) -> TaskProvider:
        """Auto-select provider based on hosting environment.

        The Task Storage API is not yet generally available. To avoid
        failures in hosted environments, the local file-based provider
        is used by default even when ``FOUNDRY_HOSTING_ENVIRONMENT`` is
        set.  Set the ``FOUNDRY_TASK_API_ENABLED=1`` environment variable
        to opt in to the HTTP-backed provider for testing once the APIs
        are lit up.

        :param config: The agent configuration.
        :type config: AgentConfig
        :return: The storage provider instance.
        :rtype: TaskProvider
        """
        import os  # pylint: disable=import-outside-toplevel

        task_api_enabled = os.environ.get("FOUNDRY_TASK_API_ENABLED", "").strip()

        if config.is_hosted and task_api_enabled in ("1", "true", "yes"):
            from ._client import (  # pylint: disable=import-outside-toplevel
                HostedTaskProvider,
            )

            try:
                from azure.identity.aio import (  # type: ignore[import-untyped]
                    DefaultAzureCredential,
                )
            except ImportError as exc:
                raise ImportError(
                    "azure-identity is required for hosted mode. "
                    "Install with: pip install azure-ai-agentserver-core[hosted]"
                ) from exc

            logger.info(
                "Task Storage API enabled via FOUNDRY_TASK_API_ENABLED; "  # pylint: disable=implicit-str-concat
                "using HostedTaskProvider"
            )
            return HostedTaskProvider(
                project_endpoint=config.project_endpoint,
                credential=DefaultAzureCredential(),
            )

        if config.is_hosted and not task_api_enabled:
            logger.info(
                "Hosted environment detected but Task Storage API not yet enabled. "
                "Using local file provider. Set FOUNDRY_TASK_API_ENABLED=1 to use "
                "the HTTP-backed provider when the APIs are available."
            )

        from ._local_provider import (  # pylint: disable=import-outside-toplevel
            LocalFileTaskProvider,
        )

        # (Spec 013 US1(c)) Operator/test override: when
        # ``AGENTSERVER_DURABLE_TASKS_PATH`` is set, root the local provider
        # at that directory instead of the user's home. Enables the crash
        # harness to point durable state at a per-test tmp_path.
        base_dir_env = os.environ.get("AGENTSERVER_DURABLE_TASKS_PATH")
        if base_dir_env:
            return LocalFileTaskProvider(base_dir=Path(base_dir_env))
        return LocalFileTaskProvider(base_dir=Path.home() / ".durable-tasks")

    @property
    def provider(self) -> TaskProvider:
        """The storage provider.

        :return: The active provider.
        :rtype: TaskProvider
        """
        return self._provider

    def register_resume_callback(
        self,
        fn_name: str,
        fn: Callable[..., Any],
        opts: TaskOptions | None = None,
    ) -> None:
        """Register a function as a resume callback.

        :param fn_name: The durable task function name.
        :type fn_name: str
        :param fn: The async function to call on resume.
        :type fn: Callable[..., Any]
        :param opts: The task options (for stream_handler_factory etc.).
        :type opts: TaskOptions | None
        """
        self._resume_callbacks[fn_name] = fn
        if opts is not None:
            self._resume_opts[fn_name] = opts

    async def list_tasks(
        self,
        *,
        fn_name: str,
        session_id: str | None = None,
        status: TaskStatus | None = None,
    ) -> list[TaskInfo]:
        """List tasks scoped to a specific task function.

        Uses server-side filtering (``agent_name``, ``session_id``,
        ``_task_name`` tag, ``status``, ``source_type``) to return only
        tasks created by this framework for the given function.

        :keyword fn_name: The task function name (stable identity anchor).
        :paramtype fn_name: str
        :keyword session_id: Session scope override. Defaults to config.
        :paramtype session_id: str | None
        :keyword status: Filter by task status.
        :paramtype status: ~azure.ai.agentserver.core.durable.TaskStatus | None
        :return: Matching task records.
        :rtype: list[TaskInfo]
        """
        resolved_session = session_id or self._config.session_id or "local"
        agent_name = self._config.agent_name or "default"

        # All filters are now server-side
        return await self._provider.list(
            agent_name=agent_name,
            session_id=resolved_session,
            status=status,
            tag={_TAG_TASK_NAME: fn_name},
            source_type=_SOURCE_TYPE,
        )

    def _register_steering_future(self, task_id: str) -> asyncio.Future[Any]:
        """Create and register a future for a queued steering input.

        Must be called BEFORE ``_append_steering_input()`` to avoid a race
        where the drain pops the queue before the future exists.

        :param task_id: The task identifier.
        :type task_id: str
        :return: The registered future.
        :rtype: asyncio.Future[Any]
        """
        loop = asyncio.get_event_loop()
        future: asyncio.Future[Any] = loop.create_future()
        if task_id not in self._pending_steering_futures:
            self._pending_steering_futures[task_id] = []
        self._pending_steering_futures[task_id].append(future)
        return future

    async def startup(self) -> None:
        """Initialize the manager and recover stale tasks.

        Called by ``AgentServerHost`` during lifespan startup.
        """
        logger.info(
            "TaskManager starting (owner=%s, instance=%s, hosted=%s)",
            self._lease_owner,
            self._instance_id,
            self._config.is_hosted,
        )
        # Pick up descriptors registered at import time (for recovery)
        from ._decorator import (  # pylint: disable=import-outside-toplevel
            _REGISTERED_DESCRIPTORS,
        )

        for fn_name, fn, opts in _REGISTERED_DESCRIPTORS:
            self._resume_callbacks[fn_name] = fn
            self._resume_opts[fn_name] = opts

        await self._recover_stale_tasks()

        # Spec 016 FR-002 Layer 2: start the periodic recovery task.
        # Reads _PERIODIC_RECOVERY_INTERVAL_SECONDS at spawn time;
        # tests monkey-patch the constant to drive the scan
        # deterministically (FR-009).
        try:
            loop = asyncio.get_running_loop()
            self._periodic_recovery_task = loop.create_task(
                self._periodic_recovery_loop()
            )
        except RuntimeError:
            # No running loop (called from outside async context); skip
            # — the layer-1 startup scan above still covered the
            # initial reclaim pass.
            pass

    async def _periodic_recovery_loop(self) -> None:
        """Spec 016 FR-002 Layer 2: periodic background recovery scan.

        Runs at the interval defined by ``_PERIODIC_RECOVERY_INTERVAL_SECONDS``
        (monkey-patchable for tests per FR-009). Each iteration calls
        :meth:`_recover_stale_tasks` and tolerates exceptions per
        per-record so a single failed reclaim does not break the
        scan. Exits cleanly when ``_shutdown_event`` is set or the
        task is cancelled.
        """
        while not self._shutdown_event.is_set():
            try:
                await asyncio.wait_for(
                    self._shutdown_event.wait(),
                    timeout=_PERIODIC_RECOVERY_INTERVAL_SECONDS,
                )
                # shutdown_event was set — exit
                return
            except asyncio.TimeoutError:
                pass
            except asyncio.CancelledError:
                return
            try:
                await self._recover_stale_tasks()
            except Exception:  # pylint: disable=broad-exception-caught
                logger.warning(
                    "Periodic recovery scan iteration failed", exc_info=True
                )

    async def shutdown(self) -> None:
        """Signal shutdown on all active tasks and force-expire leases.

        Called by ``AgentServerHost`` during lifespan shutdown.
        """
        logger.info("TaskManager shutting down")
        self._shutdown_event.set()

        # Spec 016 FR-002 Layer 2: stop the periodic recovery scan task.
        # Cancel cleanly so the shutdown event in its sleep wakes
        # immediately and the task exits.
        if self._periodic_recovery_task is not None:
            self._periodic_recovery_task.cancel()
            try:
                await self._periodic_recovery_task
            except (asyncio.CancelledError, Exception):  # pylint: disable=broad-exception-caught
                pass
            self._periodic_recovery_task = None

        # Signal shutdown on all active contexts. Yield once so the bridge
        # tasks (running in the event loop) get a chance to observe the
        # shutdown event and notify their handlers before we proceed —
        # otherwise on a fast lifespan teardown the shutdown grace sleep
        # may be cancelled before the bridge has had a chance to fire.
        for active in self._active_tasks.values():
            active.context.shutdown.set()
        if self._active_tasks:
            await asyncio.sleep(0)

        # Wait for tasks to checkpoint before force-expiring leases.
        # On a forced lifespan teardown (e.g., HTTP test client closing) the
        # sleep can be cancelled — that's fine, fall through to force-expire
        # and execution_task.cancel() below so handlers wind down.
        #
        # (Spec 014) Poll for ``_active_tasks`` becoming empty rather than
        # an unconditional sleep so the shutdown returns promptly when
        # all task bodies have checkpointed. The grace value is the
        # MAXIMUM wait, not the minimum — without polling, a 25s default
        # blocks every shutdown for the full window even when tasks are
        # already done.
        if self._active_tasks:
            deadline = (
                asyncio.get_event_loop().time() + self._shutdown_grace_seconds
            )
            try:
                while self._active_tasks:
                    if asyncio.get_event_loop().time() >= deadline:
                        break
                    # Drop entries whose execution_task already completed
                    # so we don't keep waiting for them.
                    self._active_tasks = {
                        task_id: active
                        for task_id, active in self._active_tasks.items()
                        if not active.execution_task.done()
                    }
                    if not self._active_tasks:
                        break
                    await asyncio.sleep(0.05)
            except asyncio.CancelledError:
                logger.info("TaskManager shutdown grace period interrupted")

        # Force-expire all leases. Tolerate cancellation here too.
        try:
            for active in list(self._active_tasks.values()):
                try:
                    await self._provider.update(
                        active.task_id,
                        TaskPatchRequest(
                            lease_owner=self._lease_owner,
                            lease_instance_id=self._instance_id,
                            lease_duration_seconds=0,
                        ),
                    )
                except Exception:  # pylint: disable=broad-exception-caught
                    logger.warning(
                        "Failed to force-expire lease for task %s",
                        active.task_id,
                        exc_info=True,
                    )
        except asyncio.CancelledError:
            logger.info(
                "TaskManager shutdown lease-expire interrupted; "
                "continuing to in-process task cancellation"
            )

        # Cancel all renewal and execution tasks. Always do this so handlers
        # listening on the cancellation signal wake up and exit cleanly.
        for active in self._active_tasks.values():
            active.renewal_cancel.set()
            if active.renewal_task and not active.renewal_task.done():
                active.renewal_task.cancel()
            if not active.execution_task.done():
                active.execution_task.cancel()

        self._active_tasks.clear()
        set_task_manager(None)

    async def create_and_run(
        self,
        *,
        fn: Callable[..., Awaitable[Any]],
        fn_name: str,
        task_id: str,
        input_val: Any,
        input_type: type[Any],
        session_id: str | None,
        title: str,
        tags: dict[str, str],
        opts: TaskOptions,
        retry: RetryPolicy | None = None,
        entry_mode: EntryMode = "fresh",
    ) -> Any:
        """Create a task, run the function, and return the result.

        :keyword fn: The async function to execute.
        :paramtype fn: Callable[..., Awaitable[Any]]
        :keyword fn_name: The registered function name.
        :paramtype fn_name: str
        :keyword task_id: Unique task identifier.
        :paramtype task_id: str
        :keyword input_val: The input value.
        :paramtype input_val: Any
        :keyword input_type: The input type.
        :paramtype input_type: type[Any]
        :keyword session_id: Session scope.
        :paramtype session_id: str | None
        :keyword tags: Task tags.
        :paramtype tags: dict[str, str]
        :keyword opts: Task options.
        :paramtype opts: TaskOptions
        :keyword entry_mode: Entry mode.
        :paramtype entry_mode: EntryMode
        :keyword retry: Retry policy.
        :paramtype retry: RetryPolicy | None
        :keyword title: Human-readable title.
        :paramtype title: str
        :returns: The function's return value.
        :rtype: Any
        :raises TaskFailed: On unhandled exception.
        """
        handle = await self.create_and_start(
            fn=fn,
            fn_name=fn_name,
            task_id=task_id,
            input_val=input_val,
            input_type=input_type,
            session_id=session_id,
            title=title,
            tags=tags,
            opts=opts,
            retry=retry,
            entry_mode=entry_mode,
        )
        return await handle.result()

    async def create_and_start(  # pylint: disable=too-many-locals
        self,
        *,
        fn: Callable[..., Awaitable[Any]],
        fn_name: str,
        task_id: str,
        input_val: Any,
        input_type: type[Any],  # pylint: disable=unused-argument
        session_id: str | None,
        title: str,
        tags: dict[str, str],
        opts: TaskOptions,
        retry: RetryPolicy | None = None,
        entry_mode: EntryMode = "fresh",
        stream_handler: StreamHandler | None = None,
        initial_payload_extras: dict[str, Any] | None = None,
    ) -> TaskRun[Any]:
        """Create a task, start the function, and return a handle.

        Source provenance is auto-stamped by the framework using
        ``fn_name`` and the core SDK version.

        :keyword fn: The async task function.
        :paramtype fn: Callable[..., Awaitable[Any]]
        :keyword fn_name: Function name for logging.
        :paramtype fn_name: str
        :keyword task_id: The task identifier.
        :paramtype task_id: str
        :keyword input_val: The task input value.
        :paramtype input_val: Any
        :keyword input_type: Type for deserializing input.
        :paramtype input_type: type[Any]
        :keyword session_id: Session scope identifier.
        :paramtype session_id: str | None
        :keyword title: Human-readable task title.
        :paramtype title: str
        :keyword tags: Merged decorator + call-site tags.
        :paramtype tags: dict[str, str]
        :keyword opts: Task options.
        :paramtype opts: TaskOptions
        :keyword retry: Retry policy.
        :paramtype retry: RetryPolicy | None
        :keyword entry_mode: Why this execution is starting.
        :paramtype entry_mode: EntryMode
        :keyword stream_handler: Custom stream handler. If ``None``,
            a default :class:`QueueStreamHandler` is created.
        :paramtype stream_handler: StreamHandler | None
        :keyword initial_payload_extras: (Spec 013 US2 / Spec 015 FR-004)
            Framework-reserved top-level payload slots (e.g.,
            ``{"_last_input_id": "msg-1"}``) merged into the initial
            payload alongside ``input`` and ``metadata``. Reserved keys
            ``input`` and ``metadata`` cannot be overridden via this
            channel.
        :paramtype initial_payload_extras: dict[str, Any] | None
        :return: A ``TaskRun`` handle.
        :rtype: TaskRun
        """
        resolved_session = session_id or self._config.session_id or "local"
        agent_name = self._config.agent_name or "default"

        # Build payload — input is always persisted (Spec 015 Phase 3 FR-006:
        # the per-task `store_input` knob is dropped).
        payload: dict[str, Any] = {"input": _serialize_input(input_val)}
        payload["metadata"] = {}

        # (Spec 013 US2 / Spec 015 FR-004) Framework-reserved top-level slots
        # (e.g., `_last_input_id`) supplied by `Task.start(input_id=...)`.
        # Merged shallowly so callers cannot clobber `input` or `metadata`.
        if initial_payload_extras:
            for k, v in initial_payload_extras.items():
                if k in ("input", "metadata"):
                    continue
                payload[k] = v

        # Auto-stamp source provenance (framework-owned, not user-overridable)
        source = self._build_source(fn_name)

        # Auto-stamp task name tag for LIST filtering
        if tags is None:
            tags = {}
        tags[_TAG_TASK_NAME] = fn_name

        # Create task with lease
        task_info = await self._provider.create(
            TaskCreateRequest(
                id=task_id,
                agent_name=agent_name,
                session_id=resolved_session,
                status="in_progress",
                title=title,
                payload=payload,
                tags=tags or None,
                source=source,
                lease_owner=self._lease_owner,
                lease_instance_id=self._instance_id,
                lease_duration_seconds=_DEFAULT_LEASE_SECONDS,
            )
        )

        logger.info("Created durable task %s (%s)", task_id, fn_name)

        # Register resume callback
        self._resume_callbacks[fn_name] = fn
        self._resume_opts[fn_name] = opts

        # Build context
        cancel_event = asyncio.Event()
        # Resolve handler: call-site > factory > default
        if stream_handler is not None:
            handler = stream_handler
        elif opts.stream_handler_factory is not None:
            handler = opts.stream_handler_factory(task_id)
        else:
            handler = QueueStreamHandler()
        metadata = TaskMetadata(
            flush_callback=self._make_metadata_flush(task_id),
        )

        lease_gen = task_info.lease.generation if task_info.lease else 0

        ctx: TaskContext[Any] = TaskContext(
            task_id=task_id,
            session_id=resolved_session,
            input=input_val,
            metadata=metadata,
            retry_attempt=0,
            recovery_count=lease_gen,
            cancel=cancel_event,
            shutdown=self._shutdown_event,
            stream_handler=handler,
            entry_mode=entry_mode,
            pending_count_provider=self._make_pending_count_provider(task_id),
        )
        loop = asyncio.get_event_loop()
        result_future: asyncio.Future[Any] = loop.create_future()

        # Start lease renewal
        renewal_cancel = asyncio.Event()

        # Build steering poll callback for steerable tasks
        steering_poll_cb_cs: Callable[[], Awaitable[None]] | None = None
        if opts.steerable:

            async def _steering_poll_cs() -> None:
                active = self._active_tasks.get(task_id)
                if active is None or active.context.cancel.is_set():
                    return
                info = await self._provider.get(task_id)
                if info is None or not info.payload:
                    return
                st = info.payload.get("_steering", {})
                if st.get("pending_inputs"):
                    active.context.cancel.set()

            steering_poll_cb_cs = _steering_poll_cs

        renewal_task = asyncio.create_task(
            lease_renewal_loop(
                self._provider,
                task_id,
                lease_owner=self._lease_owner,
                lease_instance_id=self._instance_id,
                lease_duration_seconds=_DEFAULT_LEASE_SECONDS,
                cancel_event=renewal_cancel,
                on_cancel_callback=cancel_event,
                steering_poll_callback=steering_poll_cb_cs,
            )
        )

        # Start execution
        terminate_event = asyncio.Event()
        terminate_reason_ref: list[str | None] = [None]
        execution_task = asyncio.create_task(
            self._execute_task(
                fn=fn,
                ctx=ctx,
                task_id=task_id,
                opts=opts,
                result_future=result_future,
                renewal_cancel=renewal_cancel,
                retry=retry,
                terminate_event=terminate_event,
                terminate_reason_ref=terminate_reason_ref,
            )
        )

        # Track active task
        active = _ActiveTask(
            task_id=task_id,
            fn_name=fn_name,
            context=ctx,
            execution_task=execution_task,
            renewal_task=renewal_task,
            renewal_cancel=renewal_cancel,
            result_future=result_future,
            terminate_event=terminate_event,
            fn=fn,
            input_type=input_type,
            opts=opts,
            retry=retry,
        )
        self._active_tasks[task_id] = active

        # Spec 015 Phase 5 (FR-003): metadata is flushed explicitly at
        # lifecycle boundaries via ``flush_all()``. There is no auto-
        # flush loop.

        return TaskRun(
            task_id=task_id,
            provider=self._provider,
            result_future=result_future,
            metadata=metadata,
            cancel_event=cancel_event,
            stream_handler=handler,
            terminate_event=terminate_event,
            execution_task=execution_task,
            terminate_reason_ref=terminate_reason_ref,
        )

    async def handle_resume(self, task_id: str) -> None:
        """Resume a suspended task.

        :param task_id: The task to resume.
        :type task_id: str
        :raises TaskNotFound: If the task doesn't exist.
        :raises ValueError: If the task is not suspended or no callback.
        """
        task_info = await self._provider.get(task_id)
        if task_info is None:
            raise TaskNotFound(task_id)

        if task_info.status != "suspended":
            raise ValueError(
                f"Task {task_id!r} is {task_info.status!r}, not 'suspended'"
            )

        # Find the resume callback by scanning registered names
        fn = self._find_resume_callback(task_info)
        if fn is None:
            raise ValueError(f"No resume callback registered for task {task_id!r}")

        await self._start_existing_task(
            fn=fn,
            fn_name=task_info.agent_name,
            task_info=task_info,
            entry_mode="resumed",
        )

        logger.info("Resumed task %s", task_id)

    async def get_active_run(self, task_id: str) -> TaskRun[Any] | None:
        """Return a TaskRun handle for an active (in-progress) task.

        Spec 016 FR-005 (US3 / US4): consults the store, not only
        in-memory state. If the record is in-progress with a dead
        lease (per :func:`_lease_is_dead`), performs inline reclaim as
        a hidden side effect and returns a usable :class:`TaskRun`
        bound to the new lifetime. Terminal records return ``None``.
        Eviction (FR-008) also returns ``None`` — same shape as
        "not active in this process" per Invariant 1.

        :param task_id: The task identifier.
        :type task_id: str
        :return: A TaskRun bound to the active task's stream handler,
            or ``None`` if not active / terminal / evicted.
        :rtype: TaskRun[Any] | None
        """
        # Fast path: locally-tracked active execution.
        active = self._active_tasks.get(task_id)
        if active is not None:
            return TaskRun(
                task_id=task_id,
                provider=self._provider,
                result_future=active.result_future,
                metadata=active.context.metadata,
                cancel_event=active.context.cancel,
                stream_handler=active.context._stream_handler,  # pylint: disable=protected-access
                terminate_event=active.terminate_event,
                execution_task=active.execution_task,
            )

        # Spec 016 FR-005: consult the store for tasks not active in
        # this process. Reads are not rejected for orphan sandboxes
        # per the spec's assumptions.
        try:
            task_info = await self._provider.get(task_id)
        except TransportClassifiedError as exc:
            if _is_evicted(exc):
                # Even reads classified as evicted (unexpected per
                # assumption but defensive) map to "not active".
                return None
            raise
        if task_info is None or task_info.status in ("completed", "suspended", "pending"):
            return None
        # Status is in_progress. Check whether the lease is dead per
        # FR-004. If so, perform inline reclaim and re-enter as
        # recovered. If reclaim fails (race lost / evicted), return None
        # per Invariant 1.
        if task_info.status == "in_progress" and _lease_is_dead(
            task_info,
            this_lease_owner=self._lease_owner,
            active_locally=False,
        ):
            fn = self._find_resume_callback(task_info)
            if fn is None:
                return None
            fn_name = (task_info.source or {}).get("name", task_info.agent_name)
            opts = self._resume_opts.get(fn_name)
            try:
                await self._reclaim_one(task_info)
            except TransportClassifiedError as exc:
                if _is_evicted(exc):
                    logger.warning(
                        "get_active_run: reclaim of %s rejected with eviction; "
                        "returning None (same shape as 'not active here')",
                        task_id,
                    )
                    return None
                raise
            await self._start_existing_task(
                fn=fn,
                fn_name=task_info.agent_name,
                task_info=task_info,
                entry_mode="recovered",
                opts=opts,
            )
            # Re-check the active-tasks table now that reclaim is done.
            active = self._active_tasks.get(task_id)
            if active is not None:
                return TaskRun(
                    task_id=task_id,
                    provider=self._provider,
                    result_future=active.result_future,
                    metadata=active.context.metadata,
                    cancel_event=active.context.cancel,
                    stream_handler=active.context._stream_handler,  # pylint: disable=protected-access
                    terminate_event=active.terminate_event,
                    execution_task=active.execution_task,
                )
        return None

    async def _reclaim_one(self, task_info: TaskInfo) -> None:
        """Spec 016 FR-003: CAS-protected lease reclaim helper.

        Updates the lease ownership to this process's owner+instance
        with ``If-Match: <etag>`` so two concurrent reclaims produce
        exactly one winner. Tolerates the LocalFileTaskProvider
        (which ignores ``if_match``) — race protection is best-effort
        in tests, deterministic against the hosted client.

        :param task_info: The task to reclaim.
        :type task_info: TaskInfo
        :raises TransportClassifiedError: With classification='evicted'
            on orphan-sandbox rejection; with other classifications on
            transient / conflict / permanent outcomes.
        """
        etag = getattr(task_info, "etag", None) or None
        await self._provider.update(
            task_info.id,
            TaskPatchRequest(
                lease_owner=self._lease_owner,
                lease_instance_id=self._instance_id,
                lease_duration_seconds=_DEFAULT_LEASE_SECONDS,
                if_match=etag,
            ),
        )

    async def _start_existing_task(  # pylint: disable=too-many-locals,too-many-statements
        self,
        *,
        fn: Callable[..., Awaitable[Any]],
        fn_name: str,
        task_info: TaskInfo,
        entry_mode: EntryMode,
        input_val: Any | None = None,
        input_type: type[Any] | None = None,
        opts: TaskOptions | None = None,
        retry: RetryPolicy | None = None,
        stream_handler: StreamHandler | None = None,
    ) -> TaskRun[Any]:
        """Transition an existing task to in_progress and execute it.

        Used by lifecycle-aware ``.run()``/``.start()`` for suspended,
        pending, and stale in_progress tasks.

        :keyword fn: The durable task function.
        :paramtype fn: Callable[..., Awaitable[Any]]
        :keyword fn_name: Function name for logging.
        :paramtype fn_name: str
        :keyword task_info: The current task record.
        :paramtype task_info: TaskInfo
        :keyword entry_mode: Why this execution is starting.
        :paramtype entry_mode: EntryMode
        :keyword input_val: New input (overrides persisted input).
        :paramtype input_val: Any | None
        :keyword input_type: Type for deserializing persisted input.
        :paramtype input_type: type[Any] | None
        :keyword opts: Task options (uses defaults if not provided).
        :paramtype opts: TaskOptions | None
        :keyword retry: Retry policy.
        :paramtype retry: RetryPolicy | None
        :keyword stream_handler: Custom stream handler. If ``None``, falls
            back to ``opts.stream_handler_factory`` or :class:`QueueStreamHandler`.
        :paramtype stream_handler: StreamHandler | None
        :return: A TaskRun handle.
        :rtype: TaskRun[Any]
        """
        task_id = task_info.id
        resolved_opts = opts or TaskOptions(name=fn_name, ephemeral=False)
        lease_duration = _DEFAULT_LEASE_SECONDS

        # Transition to in_progress with new lease
        await self._provider.update(
            task_id,
            TaskPatchRequest(
                status="in_progress",
                lease_owner=self._lease_owner,
                lease_instance_id=self._instance_id,
                lease_duration_seconds=lease_duration,
            ),
        )

        # Re-fetch updated task
        updated_info: TaskInfo | None = await self._provider.get(task_id)
        if updated_info is None:
            raise TaskNotFound(task_id)
        task_info = updated_info

        # Resolve input: prefer caller-provided, fall back to persisted
        if input_val is not None:
            resolved_input = input_val
        elif task_info.payload and "input" in task_info.payload:
            raw_input = task_info.payload["input"]
            if input_type is not None:
                resolved_input = _deserialize_input(raw_input, input_type)
            else:
                resolved_input = raw_input
        else:
            resolved_input = None

        # Build context for execution
        cancel_event = asyncio.Event()
        # Resolve handler: call-site > factory > default
        if stream_handler is not None:
            handler = stream_handler
        elif resolved_opts.stream_handler_factory is not None:
            handler = resolved_opts.stream_handler_factory(task_id)
        else:
            handler = QueueStreamHandler()
        # Spec 015 Phase 5 (FR-003): restore ALL namespaces, not just default.
        # ``from_payload`` decodes ``payload["metadata"]`` into the default
        # namespace and every ``payload["metadata:<name>"]`` into its named
        # sibling, all sharing the same flush_callback so the framework can
        # flush_all() at lifecycle boundaries.
        metadata = TaskMetadata.from_payload(
            task_info.payload,
            flush_callback=self._make_metadata_flush(task_id),
        )

        lease_gen = task_info.lease.generation if task_info.lease else 0

        # Extract steering context from payload
        steering = (task_info.payload or {}).get("_steering", {})
        # Spec 016 FR-020 (US6): is_steered_turn is True if and only if
        # THIS invocation was constructed by the steering-drain code
        # path. For initial entry from a recovered drain (the
        # crash-mid-drain case), drain_in_progress signals that the
        # previous lifetime was mid-drain, so this entry IS the
        # continuation of a steered turn. Sticky-True is avoided
        # because pending_inputs / generation > 0 alone do NOT imply
        # this entry was constructed by the drain.
        is_steered_turn = bool(steering.get("drain_in_progress"))

        # For steerable recovery with drain_in_progress, use active_input
        if (
            entry_mode == "recovered"
            and steering.get("drain_in_progress")
            and "active_input" in steering
        ):
            raw_active = steering["active_input"]
            if input_type is not None:
                resolved_input = _deserialize_input(raw_active, input_type)
            else:
                resolved_input = raw_active

        # Pre-set cancel if cancel_requested is True (steering short-circuit)
        if steering.get("cancel_requested"):
            cancel_event.set()

        # Spec 015 Phase 4 FR-001: restore the persisted retry_attempt so the
        # recovered (or developer-resumed) handler observes the correct
        # cross-lifetime budget on its first invocation. ``_retry_attempt`` is
        # written by ``_execute_task_loop`` on every handler-raised exception
        # and cleared by the steering-drain path; default 0 covers fresh and
        # never-failed tasks.
        persisted_retry_attempt = (task_info.payload or {}).get(
            "_retry_attempt", 0
        )

        ctx: TaskContext[Any] = TaskContext(
            task_id=task_id,
            session_id=task_info.session_id,
            input=resolved_input,
            metadata=metadata,
            retry_attempt=persisted_retry_attempt,
            recovery_count=lease_gen,
            cancel=cancel_event,
            shutdown=self._shutdown_event,
            stream_handler=handler,
            entry_mode=entry_mode,
            is_steered_turn=is_steered_turn,
            pending_count_provider=self._make_pending_count_provider(task_id),
        )

        loop = asyncio.get_event_loop()
        result_future: asyncio.Future[Any] = loop.create_future()

        renewal_cancel = asyncio.Event()

        # Build steering poll callback for steerable tasks
        steering_poll_cb: Callable[[], Awaitable[None]] | None = None
        if resolved_opts.steerable:

            async def _steering_poll() -> None:
                """Poll provider for new steering inputs and signal cancel."""
                active = self._active_tasks.get(task_id)
                if active is None or active.context.cancel.is_set():
                    return
                info = await self._provider.get(task_id)
                if info is None or not info.payload:
                    return
                st = info.payload.get("_steering", {})
                if st.get("pending_inputs"):
                    active.context.cancel.set()

            steering_poll_cb = _steering_poll

        renewal_task = asyncio.create_task(
            lease_renewal_loop(
                self._provider,
                task_id,
                lease_owner=self._lease_owner,
                lease_instance_id=self._instance_id,
                lease_duration_seconds=lease_duration,
                cancel_event=renewal_cancel,
                on_cancel_callback=cancel_event,
                steering_poll_callback=steering_poll_cb,
            )
        )

        terminate_event = asyncio.Event()
        terminate_reason_ref: list[str | None] = [None]
        execution_task = asyncio.create_task(
            self._execute_task(
                fn=fn,
                ctx=ctx,
                task_id=task_id,
                opts=resolved_opts,
                result_future=result_future,
                renewal_cancel=renewal_cancel,
                retry=retry,
                terminate_event=terminate_event,
                terminate_reason_ref=terminate_reason_ref,
            )
        )

        active = _ActiveTask(
            task_id=task_id,
            fn_name=fn_name,
            context=ctx,
            execution_task=execution_task,
            renewal_task=renewal_task,
            renewal_cancel=renewal_cancel,
            result_future=result_future,
            terminate_event=terminate_event,
            fn=fn,
            input_type=input_type,
            opts=resolved_opts,
            retry=retry,
        )
        self._active_tasks[task_id] = active

        return TaskRun(
            task_id=task_id,
            provider=self._provider,
            result_future=result_future,
            metadata=metadata,
            cancel_event=cancel_event,
            stream_handler=handler,
            terminate_event=terminate_event,
            execution_task=execution_task,
            terminate_reason_ref=terminate_reason_ref,
            lease_expiry_count=task_info.lease.expiry_count if task_info.lease else 0,
        )

    async def _timeout_watchdog(
        self,
        timeout_seconds: float,
        cancel_event: asyncio.Event,
        ctx: "TaskContext[Any] | None" = None,
    ) -> None:
        """Spec 016 FR-025 / FR-026 (US7): per-turn timeout watchdog.

        Cooperative-only. On firing, sets ``ctx.timeout_exceeded = True``
        then sets ``cancel_event`` and exits. Does NOT cancel the lease
        renewal or force-stop the handler. An ignoring handler runs
        until process death or external :meth:`TaskRun.cancel`.

        The misleading legacy claim "the lease will eventually expire
        and the task will be recovered" was wrong and is removed per
        spec 016 FR-026: the watchdog never expires the lease.

        :param timeout_seconds: Seconds before cooperative cancel.
        :type timeout_seconds: float
        :param cancel_event: Event to set for cooperative cancel.
        :type cancel_event: asyncio.Event
        :param ctx: The task context whose ``timeout_exceeded`` is set
            BEFORE ``cancel_event`` (FR-018 ordering invariant). If
            None (e.g., during a refactor transition), only the
            cancel_event is set.
        :type ctx: TaskContext | None
        """
        await asyncio.sleep(timeout_seconds)
        # Spec 016 FR-018 ordering: cause boolean FIRST, then cancel.
        if ctx is not None:
            ctx.timeout_exceeded = True
        cancel_event.set()
        logger.info(
            "Timeout watchdog fired cooperative cancel after %.1fs (cooperative-only; "
            "handler must check ctx.cancel.is_set() and ctx.timeout_exceeded to wind down)",
            timeout_seconds,
        )

    async def _execute_task(
        self,
        *,
        fn: Callable[..., Awaitable[Any]],
        ctx: TaskContext[Any],
        task_id: str,
        opts: TaskOptions,
        result_future: asyncio.Future[Any],
        renewal_cancel: asyncio.Event,
        retry: RetryPolicy | None = None,
        terminate_event: asyncio.Event | None = None,
        terminate_reason_ref: list[str | None] | None = None,
    ) -> None:
        """Run the task function and handle completion/failure/suspend.

        When a ``RetryPolicy`` is provided, failed attempts are retried
        with the configured delay and backoff. Suspend and cancellation
        always exit immediately — they are not retried.

        :keyword fn: The async task function.
        :paramtype fn: Callable[..., Awaitable[Any]]
        :keyword ctx: The task context.
        :paramtype ctx: TaskContext[Any]
        :keyword task_id: The task identifier.
        :paramtype task_id: str
        :keyword opts: The task options.
        :paramtype opts: TaskOptions
        :keyword result_future: Future to resolve with the result.
        :paramtype result_future: asyncio.Future[Any]
        :keyword renewal_cancel: Event to cancel lease renewal.
        :paramtype renewal_cancel: asyncio.Event
        :keyword retry: Optional retry policy.
        :paramtype retry: RetryPolicy | None
        :keyword terminate_event: Optional terminate event.
        :paramtype terminate_event: asyncio.Event | None
        :keyword terminate_reason_ref: Mutable ref for terminate reason.
        :paramtype terminate_reason_ref: list[str | None] | None
        """
        resolved_terminate = terminate_event or asyncio.Event()

        # Start timeout watchdog if configured
        watchdog_task: asyncio.Task[None] | None = None
        if opts.timeout is not None:
            watchdog_task = asyncio.create_task(
                self._timeout_watchdog(
                    timeout_seconds=opts.timeout.total_seconds(),
                    cancel_event=ctx.cancel,
                    ctx=ctx,
                )
            )

        attempt = 0  # pylint: disable=unused-variable
        try:
            await self._execute_task_loop(
                fn=fn,
                ctx=ctx,
                task_id=task_id,
                opts=opts,
                result_future=result_future,
                renewal_cancel=renewal_cancel,
                retry=retry,
                terminate_event=resolved_terminate,
                terminate_reason_ref=terminate_reason_ref,
            )
        finally:
            if watchdog_task is not None and not watchdog_task.done():
                watchdog_task.cancel()
                try:
                    await watchdog_task
                except asyncio.CancelledError:
                    pass

    async def _execute_task_loop(  # pylint: disable=too-many-statements,too-many-branches,too-many-nested-blocks
        self,
        *,
        fn: Callable[..., Awaitable[Any]],
        ctx: TaskContext[Any],
        task_id: str,
        opts: TaskOptions,
        result_future: asyncio.Future[Any],
        renewal_cancel: asyncio.Event,
        retry: RetryPolicy | None = None,
        terminate_event: asyncio.Event | None = None,
        terminate_reason_ref: list[str | None] | None = None,
    ) -> None:
        """Inner execution loop — separated from watchdog management.

        :keyword fn: The async task function.
        :paramtype fn: Callable[..., Awaitable[Any]]
        :keyword ctx: The task context.
        :paramtype ctx: TaskContext[Any]
        :keyword task_id: The task identifier.
        :paramtype task_id: str
        :keyword opts: The task options.
        :paramtype opts: TaskOptions
        :keyword result_future: Future to resolve with the result.
        :paramtype result_future: asyncio.Future[Any]
        :keyword renewal_cancel: Event to cancel lease renewal.
        :paramtype renewal_cancel: asyncio.Event
        :keyword retry: Optional retry policy.
        :paramtype retry: RetryPolicy | None
        :keyword terminate_event: Optional terminate event.
        :paramtype terminate_event: asyncio.Event | None
        :keyword terminate_reason_ref: Mutable ref for terminate reason.
        :paramtype terminate_reason_ref: list[str | None] | None
        """
        resolved_terminate = terminate_event or asyncio.Event()
        reason_ref = (
            terminate_reason_ref if terminate_reason_ref is not None else [None]
        )
        # Spec 015 Phase 4 FR-001: honor the persisted retry_attempt so the
        # cross-lifetime budget is respected. ``_start_existing_task`` and
        # ``create_and_start`` populate ``ctx.retry_attempt`` from
        # ``payload["_retry_attempt"]`` (default 0 for fresh tasks).
        attempt = ctx.retry_attempt
        # Mutable ref: steering drain may swap the active result_future
        current_result_future = result_future
        while True:
            ctx.retry_attempt = attempt
            try:
                result = await fn(ctx)

                if isinstance(result, Suspended):
                    # Spec 016 FR-011 (US5): the current turn's caller's
                    # result_future MUST be set to TaskResult(status="suspended",
                    # output=X, suspension_reason=R) UNCONDITIONALLY — whether
                    # or not a steering input is queued. The handler's emitted
                    # output is delivered unchanged. The framework auto-flushes
                    # metadata at this terminal-of-turn boundary (FR-015).
                    renewal_cancel.set()
                    await ctx.metadata.flush_all()
                    await self._handle_suspend(
                        task_id=task_id,
                        reason=result.reason,
                        output=result.output,
                        metadata=ctx.metadata,
                        opts=opts,
                    )
                    if not current_result_future.done():
                        current_result_future.set_result(
                            TaskResult(
                                task_id=task_id,
                                output=result.output,
                                status="suspended",
                                suspension_reason=result.reason,
                            )
                        )

                    # Spec 016 FR-014 (US5): after the suspend is durably
                    # persisted AND the current caller's future is resolved,
                    # check for a queued steering input and re-enter the
                    # handler for it. The steerer's future (if any) gets
                    # rotated in as the new current_result_future for the
                    # next turn.
                    if opts.steerable:
                        renewal_cancel = asyncio.Event()  # reset for next turn
                        new_ctx = await self._try_drain_steering(
                            task_id=task_id,
                            ctx=ctx,
                            opts=opts,
                            result_future=current_result_future,
                        )
                        if new_ctx is not None:
                            ctx = new_ctx
                            attempt = 0
                            active = self._active_tasks.get(task_id)
                            if (
                                active
                                and active.result_future is not current_result_future
                            ):
                                current_result_future = active.result_future
                            continue
                else:
                    # Guard: task functions must return raw output, not TaskResult
                    if isinstance(result, TaskResult):
                        raise TypeError(
                            "Task function returned TaskResult directly. "
                            "Return raw output instead — the framework wraps "
                            "it in TaskResult automatically."
                        )

                    # Spec 016 FR-012 (US5): when the handler returns a
                    # value, the task transitions to terminal in a single
                    # store write that clears the queued steering inputs.
                    # The handler chose to finish (strategy C from §4
                    # Steering); the queued steerers all receive
                    # TaskConflictError. There is NO drain on the
                    # completion path — that was the legacy behavior
                    # before spec 016.

                    # Success flow
                    renewal_cancel.set()
                    await ctx.metadata.flush_all()
                    completed = await self._handle_success(
                        task_id=task_id,
                        result=result,
                        metadata=ctx.metadata,
                        opts=opts,
                    )
                    # Spec 016 FR-012 (US5): set the current turn's caller's
                    # result_future to the completion outcome FIRST, then
                    # resolve any queued steerers with TaskConflictError
                    # (since the task has now terminated). The handler's
                    # return value is delivered unchanged to the current
                    # caller; the queued steerers see the "task is busy /
                    # terminal" shape per Invariant 1.
                    if not current_result_future.done():
                        current_result_future.set_result(
                            TaskResult(
                                task_id=task_id,
                                output=result,
                                status="completed",
                            )
                        )
                    # Spec 016 FR-012: queued steerers (registered via
                    # _register_steering_future) get TaskConflictError on
                    # terminal completion since the task is now done.
                    _resolve_queued_steerers_on_terminal(
                        self._pending_steering_futures,
                        task_id,
                        current_status="completed",
                    )
                    if not completed:
                        # Etag conflict on steerable completion — but the
                        # caller's future is now resolved with the completion
                        # outcome (per FR-012), so we don't re-drain; the
                        # next .start() will pick up any queued state.
                        pass

                break  # exit retry loop on success or suspend

            except asyncio.CancelledError:
                renewal_cancel.set()
                await ctx.metadata.flush_all()
                # Spec 016 FR-022 (US6): the terminate/TaskTerminated
                # pathway is removed. asyncio.CancelledError is now
                # exclusively the cooperative-cancel path — the handler
                # chose to raise it (or the framework signalled cancel
                # via ctx.cancel and the handler did not catch). Result
                # future receives TaskCancelled.
                if not current_result_future.done():
                    from ._exceptions import (  # pylint: disable=import-outside-toplevel
                        TaskCancelled,
                    )

                    current_result_future.set_exception(TaskCancelled(task_id))
                break  # cancellation is never retried

            except Exception as exc:  # pylint: disable=broad-exception-caught
                if retry and retry.should_retry(attempt, exc):
                    delay = retry.compute_delay(attempt)
                    logger.warning(
                        "Task %s attempt %d failed (%s: %s), retrying in %.1fs",
                        task_id,
                        attempt,
                        type(exc).__name__,
                        exc,
                        delay,
                    )
                    # Spec 015 Phase 4 FR-001 / FR-002: persist the post-bump
                    # retry_attempt alongside the error field in a single
                    # patch. A subsequent crash + recover will restore this
                    # counter via ``_start_existing_task`` so the durable
                    # max_attempts budget is honored across lifetimes.
                    try:
                        await self._provider.update(
                            task_id,
                            TaskPatchRequest(
                                error={
                                    "type": type(exc).__name__,
                                    "message": str(exc),
                                    "attempt": attempt,
                                },
                                payload={"_retry_attempt": attempt + 1},
                            ),
                        )
                    except Exception:  # pylint: disable=broad-exception-caught
                        logger.debug(
                            "Failed to update error field for retry", exc_info=True
                        )
                    await asyncio.sleep(delay)
                    attempt += 1
                    continue

                # Exhausted or non-retryable — terminal failure
                renewal_cancel.set()
                await ctx.metadata.flush_all()

                if retry and attempt > 0:
                    # Retries were attempted but exhausted
                    error_dict: dict[str, Any] = {
                        "type": "exhausted_retries",
                        "attempts": attempt + 1,
                        "last_error": str(exc),
                        "last_error_type": type(exc).__name__,
                        "traceback": traceback.format_exc(),
                    }
                else:
                    error_dict = {
                        "type": type(exc).__name__,
                        "message": str(exc),
                        "traceback": traceback.format_exc(),
                    }

                await self._handle_failure(
                    task_id=task_id,
                    exc=exc,
                    metadata=ctx.metadata,
                    opts=opts,
                )
                if not current_result_future.done():
                    current_result_future.set_exception(TaskFailed(task_id, error_dict))
                # Spec 016 FR-012 (US5): queued steerers see TaskConflictError
                # on terminal failure since the task is now done.
                _resolve_queued_steerers_on_terminal(
                    self._pending_steering_futures,
                    task_id,
                    current_status="failed",
                )
                break

        self._active_tasks.pop(task_id, None)
        # Signal end of streaming via handler.close()
        if ctx._stream_handler is not None:  # pylint: disable=protected-access
            try:
                await ctx._stream_handler.close()  # pylint: disable=protected-access
            except Exception:  # pylint: disable=broad-exception-caught
                logger.warning(
                    "Stream handler close() failed for task %s",
                    task_id,
                    exc_info=True,
                )

    async def _try_drain_steering(  # pylint: disable=too-many-branches
        self,
        *,
        task_id: str,
        ctx: TaskContext[Any],
        opts: TaskOptions,
        result_future: asyncio.Future[Any],
        partial_output: Any | None = None,
    ) -> TaskContext[Any] | None:
        """Check for pending steering inputs and drain the next one.

        Called BEFORE persisting suspend/complete to avoid lease/status conflicts.
        Returns a new ``TaskContext`` if a drain occurred, or ``None`` if no
        pending inputs exist.

        :keyword task_id: The task identifier.
        :keyword ctx: Current task context.
        :keyword opts: Task options.
        :keyword result_future: The current generation's result future.
        :keyword partial_output: Output from the previously-running generation,
            delivered in-process via ``TaskResult(output=..., status="superseded")``
            to whoever was awaiting the steered-out turn's result_future
            (see ``_manager.py`` line ~1386). NOT durably persisted — if the
            process crashes between completion and delivery, this output is
            lost. (Spec 013 US4 scenario 11: the previously-existing durable
            backup write at ``_steering["generation_results"]`` was removed
            because no consumer existed.)
        :return: New context for the drained generation, or None.
        """
        task_info = await self._provider.get(task_id)
        if task_info is None:
            return None

        payload = dict(task_info.payload) if task_info.payload else {}
        steering = dict(payload.get("_steering", {}))
        pending: list[Any] = list(steering.get("pending_inputs", []))

        if not pending:
            return None

        # Pop the next input from the queue
        next_input_raw = pending.pop(0)

        # Update steering state. (Spec 015 Phase 3 FR-006: previous_input is
        # no longer mirrored into _steering; only the active input + queue
        # state need to survive a crash mid-drain.)
        steering["active_input"] = next_input_raw
        steering["pending_inputs"] = pending
        old_generation = steering.get("generation", 0)
        steering["generation"] = old_generation + 1
        steering["cancel_requested"] = len(pending) > 0
        steering["drain_in_progress"] = True

        # (Spec 013 US4 scenario 11) Previously this site captured handler output
        # into `_steering["generation_results"]` as forward-compat durable backup
        # for in-process superseded-result delivery (see `_manager.py:1386`
        # `TaskResult(output=partial_output, status="superseded")`). Removed
        # because no consumer existed anywhere in the codebase — `partial_output`
        # is consumed at line 1386 for in-process delivery only. If durable
        # replay of superseded results becomes a requirement in the future,
        # restore the write here with a corresponding recovery-side read path
        # that pumps stored output into the in-memory result_futures.

        payload["_steering"] = steering

        try:
            etag = getattr(task_info, "etag", None) or None
            await self._provider.update(
                task_id,
                TaskPatchRequest(payload=payload, if_match=etag),
            )
        except ValueError:
            # Etag conflict — re-read and retry once
            logger.warning(
                "Etag conflict during steering drain for %s, retrying", task_id
            )
            return await self._try_drain_steering(
                task_id=task_id,
                ctx=ctx,
                opts=opts,
                result_future=result_future,
                partial_output=partial_output,
            )

        # Pop and bind the next pending steering future (if any)
        new_future: asyncio.Future[Any] | None = None
        had_registered_future = False
        steering_futures = self._pending_steering_futures.get(task_id, [])
        if steering_futures:
            new_future = steering_futures.pop(0)
            had_registered_future = True

        # Resolve the queued steerer's future binding for the new turn.
        # Spec 016 FR-013 / FR-014 (US5): the OLD result_future is NOT
        # set to "superseded" here — the suspend path (or completion
        # path) above has ALREADY set it to the natural multi-turn
        # outcome before this drain runs. The drain just rotates the
        # active result_future so the next turn's handler invocation
        # is bound to the steerer's future (the caller that queued the
        # input via .start()) if one was registered.
        if new_future is None:
            # No registered steerer for this drain — reuse the OLD
            # result_future as the new turn's future. This is the rare
            # case where the drain was triggered by a poll-based
            # backlog rather than a fresh .start() call. The future
            # may already be done (from the suspend resolution above);
            # if so, leave it.
            new_future = result_future

        # Update active generation future
        if new_future is not None:
            self._active_generation_future[task_id] = new_future

        # Deserialize input
        active_task = self._active_tasks.get(task_id)
        input_type = active_task.input_type if active_task else None
        if input_type is not None:
            resolved_input = _deserialize_input(next_input_raw, input_type)
        else:
            resolved_input = next_input_raw

        # Build new context, reusing metadata and shutdown event
        cancel_event = asyncio.Event()
        if steering["cancel_requested"]:
            cancel_event.set()

        new_ctx: TaskContext[Any] = TaskContext(
            task_id=task_id,
            session_id=ctx._session_id,  # pylint: disable=protected-access
            input=resolved_input,
            metadata=ctx.metadata,
            retry_attempt=0,
            recovery_count=ctx.recovery_count,
            cancel=cancel_event,
            shutdown=ctx.shutdown,
            stream_handler=ctx._stream_handler,  # pylint: disable=protected-access
            entry_mode="resumed",
            is_steered_turn=True,
            pending_count_provider=self._make_pending_count_provider(task_id),
        )

        # Update active task tracking
        if active_task is not None:
            active_task.context = new_ctx
            if new_future is not None:
                active_task.result_future = new_future

        # Clear drain_in_progress
        steering["drain_in_progress"] = False
        payload["_steering"] = steering
        # Spec 015 Phase 4 FR-001: a steering input is a new logical request
        # from the developer; the retry budget resets. Persist the reset so a
        # subsequent crash does not resurrect the prior counter from
        # ``payload["_retry_attempt"]``.
        payload["_retry_attempt"] = 0
        try:
            await self._provider.update(
                task_id,
                TaskPatchRequest(payload=payload),
            )
        except Exception:  # pylint: disable=broad-exception-caught
            logger.debug("Failed to clear drain_in_progress for %s", task_id)

        logger.info(
            "Steering drain: task %s generation %d → %d",
            task_id,
            old_generation,
            old_generation + 1,
        )
        return new_ctx

    async def _handle_success(
        self,
        *,
        task_id: str,
        result: Any,
        metadata: TaskMetadata,
        opts: TaskOptions,
    ) -> bool:
        """Handle successful task completion.

        :keyword task_id: The task identifier.
        :paramtype task_id: str
        :keyword result: The task result value.
        :paramtype result: Any
        :keyword metadata: The task metadata.
        :paramtype metadata: TaskMetadata
        :keyword opts: The task options.
        :paramtype opts: TaskOptions
        :return: True if completion succeeded, False if etag conflict
            detected (steerable tasks only — caller should re-drain).
        :rtype: bool
        """
        if opts.ephemeral:
            # Delete immediately — no intermediate PATCH
            try:
                await self._provider.delete(task_id, force=True)
            except Exception:  # pylint: disable=broad-exception-caught
                logger.warning(
                    "Failed to delete ephemeral task %s", task_id, exc_info=True
                )
        else:
            # PATCH to completed with output
            payload_patch: dict[str, Any] = {
                "metadata": metadata.to_dict(),
                "output": _serialize_input(result),
            }

            # For steerable tasks, use etag to detect concurrent steering
            if opts.steerable:
                try:
                    task_info = await self._provider.get(task_id)
                    etag = getattr(task_info, "etag", None) if task_info else None
                    await self._provider.update(
                        task_id,
                        TaskPatchRequest(
                            status="completed",
                            payload=payload_patch,
                            if_match=etag,
                        ),
                    )
                except ValueError:
                    # Etag conflict — another process may have steered
                    logger.info(
                        "Etag conflict completing task %s — re-checking for steers",
                        task_id,
                    )
                    return False
                except TransportClassifiedError as exc:
                    if _is_evicted(exc):
                        # Spec 016 FR-007: orphan-sandbox eviction at the
                        # terminal-write site. Suppress this terminal write
                        # (already done — the call raised) and signal awaiters
                        # via TaskConflictError. Caller-observable shape is
                        # identical to the live-elsewhere case per Invariant 1.
                        logger.warning(
                            "Eviction (binding_mismatch) on terminal write for "
                            "task %s (session=%s) — suppressing terminal write, "
                            "signalling awaiters with TaskConflictError",
                            task_id,
                            self._config.session_id or "local",
                        )
                        raise TaskConflictError(task_id, "in_progress") from exc
                    raise
                except Exception:  # pylint: disable=broad-exception-caught
                    logger.warning("Failed to complete task %s", task_id, exc_info=True)
            else:
                try:
                    await self._provider.update(
                        task_id,
                        TaskPatchRequest(
                            status="completed",
                            payload=payload_patch,
                        ),
                    )
                except TransportClassifiedError as exc:
                    if _is_evicted(exc):
                        logger.warning(
                            "Eviction (binding_mismatch) on terminal write for "
                            "task %s (session=%s) — suppressing terminal write, "
                            "signalling awaiters with TaskConflictError",
                            task_id,
                            self._config.session_id or "local",
                        )
                        raise TaskConflictError(task_id, "in_progress") from exc
                    raise
                except Exception:  # pylint: disable=broad-exception-caught
                    logger.warning("Failed to complete task %s", task_id, exc_info=True)

        logger.info("Task %s completed successfully", task_id)
        return True

    async def _handle_failure(
        self,
        *,
        task_id: str,
        exc: Exception,
        metadata: TaskMetadata,
        opts: TaskOptions,
    ) -> None:
        """Handle task failure.

        :keyword task_id: The task identifier.
        :paramtype task_id: str
        :keyword exc: The exception that caused the failure.
        :paramtype exc: Exception
        :keyword metadata: The task metadata.
        :paramtype metadata: TaskMetadata
        :keyword opts: The task options.
        :paramtype opts: TaskOptions
        """
        error_dict = {
            "type": type(exc).__name__,
            "message": str(exc),
            "traceback": traceback.format_exc(),
        }

        if opts.ephemeral:
            try:
                await self._provider.delete(task_id, force=True)
            except TransportClassifiedError as exc:
                if _is_evicted(exc):
                    logger.warning(
                        "Eviction (binding_mismatch) on failed-task delete for "
                        "task %s (session=%s) — suppressing delete, signalling "
                        "awaiters with TaskConflictError",
                        task_id,
                        self._config.session_id or "local",
                    )
                    raise TaskConflictError(task_id, "in_progress") from exc
                raise
            except Exception:  # pylint: disable=broad-exception-caught
                logger.warning(
                    "Failed to delete failed ephemeral task %s",
                    task_id,
                    exc_info=True,
                )
        else:
            try:
                await self._provider.update(
                    task_id,
                    TaskPatchRequest(
                        status="completed",
                        error=error_dict,
                        payload={"metadata": metadata.to_dict()},
                    ),
                )
            except TransportClassifiedError as exc:
                if _is_evicted(exc):
                    logger.warning(
                        "Eviction (binding_mismatch) on terminal failure write "
                        "for task %s (session=%s) — suppressing terminal write, "
                        "signalling awaiters with TaskConflictError",
                        task_id,
                        self._config.session_id or "local",
                    )
                    raise TaskConflictError(task_id, "in_progress") from exc
                raise
            except Exception:  # pylint: disable=broad-exception-caught
                logger.warning(
                    "Failed to record error for task %s",
                    task_id,
                    exc_info=True,
                )

        logger.error("Task %s failed: %s", task_id, exc)

    async def _handle_suspend(
        self,
        *,
        task_id: str,
        reason: str | None,
        output: Any | None,
        metadata: TaskMetadata,
        opts: TaskOptions,  # pylint: disable=unused-argument
    ) -> None:
        """Handle task suspension.

        Per spec 013 US4 + spec 015 Phase 3: clears the input-bearing payload
        slots at the suspend transition — ``payload["input"]`` and
        ``_steering["active_input"]``. These hold mirror copies of the consumed
        input that are no longer needed once the handler returns. ``_steering``
        mechanism state (``generation``, ``cancel_requested``,
        ``drain_in_progress``, ``pending_inputs``) is preserved.

        Safe with respect to the race-recovery contract: that contract only
        consumes ``active_input`` when ``drain_in_progress`` is True, which is
        impossible at suspend by construction (drain check runs first; if
        pending was non-empty the task would drain, not suspend).

        :keyword task_id: The task identifier.
        :paramtype task_id: str
        :keyword reason: Optional suspension reason.
        :paramtype reason: str | None
        :keyword output: Optional output snapshot.
        :paramtype output: Any | None
        :keyword metadata: The task metadata.
        :paramtype metadata: TaskMetadata
        :keyword opts: The task options.
        :paramtype opts: TaskOptions
        """
        # Read current payload so we can clear input-bearing slots while
        # preserving _steering mechanism state (Spec 013 US4 scenarios 1, 2).
        task_info = await self._provider.get(task_id)
        steering_patch: dict[str, Any] = {}
        if task_info is not None and task_info.payload:
            existing_steering = task_info.payload.get("_steering") or {}
            if existing_steering:
                steering_patch = dict(existing_steering)
                steering_patch["active_input"] = None

        payload_patch: dict[str, Any] = {
            "metadata": metadata.to_dict(),
            "input": None,
        }
        if steering_patch:
            payload_patch["_steering"] = steering_patch
        if output is not None:
            payload_patch["output"] = _serialize_input(output)

        try:
            await self._provider.update(
                task_id,
                TaskPatchRequest(
                    status="suspended",
                    suspension_reason=reason,
                    payload=payload_patch,
                ),
            )
        except TransportClassifiedError as exc:
            if _is_evicted(exc):
                logger.warning(
                    "Eviction (binding_mismatch) on suspend write for task %s "
                    "(session=%s) — suppressing suspend write, signalling "
                    "awaiters with TaskConflictError",
                    task_id,
                    self._config.session_id or "local",
                )
                raise TaskConflictError(task_id, "in_progress") from exc
            raise
        except Exception:  # pylint: disable=broad-exception-caught
            logger.warning("Failed to suspend task %s", task_id, exc_info=True)

        logger.info("Task %s suspended: %s", task_id, reason)

    async def _recover_stale_tasks(self) -> None:
        """Recover stale in-progress tasks from previous instances."""
        agent_name = self._config.agent_name or "default"
        session_id = self._config.session_id or "local"

        try:
            stale_tasks = await self._provider.list(
                agent_name=agent_name,
                session_id=session_id,
                status="in_progress",
                lease_owner=self._lease_owner,
            )
        except Exception:  # pylint: disable=broad-exception-caught
            logger.warning("Failed to query stale tasks for recovery", exc_info=True)
            return

        for task_info in stale_tasks:
            # Skip if we're already tracking this task
            if task_info.id in self._active_tasks:
                continue

            # Reclaim the lease with our new instance ID
            try:
                await self._provider.update(
                    task_info.id,
                    TaskPatchRequest(
                        lease_owner=self._lease_owner,
                        lease_instance_id=self._instance_id,
                        lease_duration_seconds=_DEFAULT_LEASE_SECONDS,
                    ),
                )
                logger.info(
                    "Reclaimed stale task %s (generation will increment)",
                    task_info.id,
                )
            except Exception:  # pylint: disable=broad-exception-caught
                logger.warning("Failed to reclaim task %s", task_info.id, exc_info=True)
                continue

            # Find resume callback and dispatch
            fn = self._find_resume_callback(task_info)
            if fn is not None:
                try:
                    # Look up stored opts for stream_handler_factory etc.
                    fn_name = (task_info.source or {}).get("name", "")
                    opts = self._resume_opts.get(fn_name)
                    await self._start_existing_task(
                        fn=fn,
                        fn_name=task_info.agent_name,
                        task_info=task_info,
                        entry_mode="recovered",
                        opts=opts,
                    )
                    logger.info("Recovered task %s is now active", task_info.id)
                except Exception:  # pylint: disable=broad-exception-caught
                    logger.warning(
                        "Failed to resume recovered task %s",
                        task_info.id,
                        exc_info=True,
                    )

    def _find_resume_callback(self, task_info: TaskInfo) -> Callable[..., Any] | None:
        """Find a registered resume callback for a task.

        Matches by ``source.name`` (auto-stamped function name) first,
        then falls back to title prefix match or single-callback default.

        :param task_info: The task record to match.
        :type task_info: TaskInfo
        :return: A matching resume callback, or None.
        :rtype: Callable[..., Any] | None
        """
        # Preferred: match by source.name (framework auto-stamped fn name)
        if task_info.source and "name" in task_info.source:
            source_name = task_info.source["name"]
            if source_name in self._resume_callbacks:
                return self._resume_callbacks[source_name]

        # Fallback: title prefix match
        for name, fn in self._resume_callbacks.items():
            if task_info.title and task_info.title.startswith(name):
                return fn

        # Last resort: single registered callback
        if len(self._resume_callbacks) == 1:
            return next(iter(self._resume_callbacks.values()))
        return None

    def _make_metadata_flush(
        self, task_id: str
    ) -> Callable[[Optional[str], dict[str, Any]], Awaitable[None]]:
        """Create a per-namespace flush callback for metadata persistence.

        The callback persists each namespace into its dedicated payload
        slot (Spec 015 FR-003 layout): ``payload["metadata"]`` for the
        default namespace and ``payload["metadata:<name>"]`` for named
        namespaces. Patches are shallow-merged by the provider so
        flushing one namespace does NOT clobber another.

        :param task_id: The task identifier.
        :type task_id: str
        :return: An async callback that flushes one namespace.
        :rtype: Callable[[Optional[str], dict[str, Any]], Awaitable[None]]
        """

        async def _flush(namespace: Optional[str], data: dict[str, Any]) -> None:
            slot = "metadata" if namespace is None else f"metadata:{namespace}"
            await self._provider.update(
                task_id,
                TaskPatchRequest(payload={slot: data}),
            )

        return _flush

    def _make_pending_count_provider(self, task_id: str) -> Callable[[], int]:
        """Spec 016 FR-019 (US6): factory for the live pending-input-count
        callable bound onto :class:`TaskContext`.

        The returned callable reads the in-memory steering state for
        ``task_id`` on each access so ``ctx.pending_input_count``
        reflects the current backlog including inputs queued
        mid-handler (as opposed to a snapshot frozen at handler entry).

        Returns 0 for tasks that are not steerable or have no pending
        inputs.
        """

        def _provider() -> int:
            active = self._active_tasks.get(task_id)
            if active is None:
                return 0
            # Read live count from the persisted-but-cached steering
            # tracker. The fastest place is the in-memory _ActiveTask
            # entry; we annotate it via a side-channel below. Default
            # to 0 if not yet populated.
            count = getattr(active, "_pending_input_count", 0)
            try:
                return int(count)
            except Exception:  # noqa: BLE001
                return 0

        return _provider
