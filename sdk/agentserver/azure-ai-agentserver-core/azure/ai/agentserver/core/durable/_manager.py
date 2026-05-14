# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""DurableTaskManager — lifecycle orchestration for durable tasks.

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
from typing import Any, TypeVar

from .._config import AgentConfig
from ._context import EntryMode, TaskContext
from ._decorator import DurableTaskOptions, _deserialize_input, _serialize_input
from ._exceptions import TaskFailed, TaskNotFound
from ._lease import derive_lease_owner, generate_instance_id, lease_renewal_loop
from ._metadata import TaskMetadata
from ._models import TaskCreateRequest, TaskInfo, TaskPatchRequest, TaskStatus
from ._provider import DurableTaskProvider
from ._result import TaskResult
from ._retry import RetryPolicy
from ._run import Suspended, TaskRun
from ._stream import QueueStreamHandler, StreamHandler
from .._version import VERSION as _CORE_VERSION
from .._server_version import build_server_version as _build_server_version

logger = logging.getLogger("azure.ai.agentserver.durable")

#: Auto-stamped source type for all tasks created by this framework.
_SOURCE_TYPE = "agentserver.durable_task"

#: Reserved tag key for task name filtering via the LIST API.
_TAG_TASK_NAME = "_durable_task_name"

#: Pre-computed server version segment for source stamps.
_SOURCE_SERVER_VERSION = _build_server_version(
    "azure-ai-agentserver-core", _CORE_VERSION
)

Input = TypeVar("Input")
Output = TypeVar("Output")

# Module-level manager singleton
_manager: DurableTaskManager | None = None


def get_task_manager() -> DurableTaskManager:
    """Return the active DurableTaskManager singleton.

    :raises RuntimeError: If no manager has been initialized.
    :return: The active manager.
    :rtype: DurableTaskManager
    """
    if _manager is None:
        raise RuntimeError(
            "DurableTaskManager not initialized. Ensure durable tasks "
            "are enabled on the AgentServerHost."  # pylint: disable=implicit-str-concat
        )
    return _manager


def set_task_manager(manager: DurableTaskManager | None) -> None:
    """Set the module-level DurableTaskManager singleton.

    Called by ``AgentServerHost`` during startup/shutdown.

    :param manager: The manager to set, or ``None`` to clear.
    :type manager: DurableTaskManager | None
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
        opts: DurableTaskOptions | None = None,
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


class DurableTaskManager:
    """Lifecycle orchestrator for durable tasks.

    Manages provider selection, task creation, lease management,
    execution dispatch, crash recovery, and graceful shutdown.

    :param config: Resolved agent configuration.
    :type config: AgentConfig
    :param provider: Optional explicit provider (for testing).
    :type provider: DurableTaskProvider | None
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
        provider: DurableTaskProvider | None = None,
        shutdown_event: asyncio.Event | None = None,
        shutdown_grace_seconds: float = 25.0,
    ) -> None:
        self._config = config
        self._provider = provider or self._create_provider(config)
        self._active_tasks: dict[str, _ActiveTask] = {}
        self._resume_callbacks: dict[str, Callable[..., Any]] = {}
        self._lease_owner = derive_lease_owner(config.session_id or "local")
        self._instance_id = generate_instance_id()
        self._shutdown_event = shutdown_event or asyncio.Event()
        self._shutdown_grace_seconds = shutdown_grace_seconds
        self._active_generation_future: dict[str, asyncio.Future[Any]] = {}
        self._pending_steering_futures: dict[str, list[asyncio.Future[Any]]] = {}

    @staticmethod
    def _build_source(fn_name: str) -> dict[str, str]:
        """Build the framework-owned source stamp for a task.

        The ``fn_name`` is the developer-provided ``name`` from the decorator
        (or ``fn.__qualname__`` when omitted).  It serves as the **stable
        identity anchor** — recovery routing matches ``source.name`` against
        registered callbacks to dispatch recovered tasks back to the correct
        function.

        :param fn_name: The task name (from ``@durable_task(name=...)``).
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
    def _create_provider(config: AgentConfig) -> DurableTaskProvider:
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
        :rtype: DurableTaskProvider
        """
        import os  # pylint: disable=import-outside-toplevel

        task_api_enabled = os.environ.get("FOUNDRY_TASK_API_ENABLED", "").strip()

        if config.is_hosted and task_api_enabled in ("1", "true", "yes"):
            from ._client import (  # pylint: disable=import-outside-toplevel
                HostedDurableTaskProvider,
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
                "using HostedDurableTaskProvider"
            )
            return HostedDurableTaskProvider(
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
            LocalFileDurableTaskProvider,
        )

        return LocalFileDurableTaskProvider(base_dir=Path.home() / ".durable-tasks")

    @property
    def provider(self) -> DurableTaskProvider:
        """The storage provider.

        :return: The active provider.
        :rtype: DurableTaskProvider
        """
        return self._provider

    def register_resume_callback(
        self,
        fn_name: str,
        fn: Callable[..., Any],
    ) -> None:
        """Register a function as a resume callback.

        :param fn_name: The durable task function name.
        :type fn_name: str
        :param fn: The async function to call on resume.
        :type fn: Callable[..., Any]
        """
        self._resume_callbacks[fn_name] = fn

        self._resume_callbacks[fn_name] = fn

    async def list_tasks(
        self,
        *,
        fn_name: str,
        session_id: str | None = None,
        status: TaskStatus | None = None,
    ) -> list[TaskInfo]:
        """List tasks scoped to a specific durable task function.

        Uses server-side filtering (``agent_name``, ``session_id``,
        ``_durable_task_name`` tag, ``status``) and client-side filtering
        (``source.type``) to return only tasks created by this framework
        for the given function.

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

        # Server-side filters: agent_name, session_id, tag, status
        results = await self._provider.list(
            agent_name=agent_name,
            session_id=resolved_session,
            status=status,
            tag={_TAG_TASK_NAME: fn_name},
        )

        # Client-side filter: source.type (until source_type server filter exists)
        return [
            task
            for task in results
            if task.source and task.source.get("type") == _SOURCE_TYPE
        ]

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
            "DurableTaskManager starting (owner=%s, instance=%s, hosted=%s)",
            self._lease_owner,
            self._instance_id,
            self._config.is_hosted,
        )
        await self._recover_stale_tasks()

    async def shutdown(self) -> None:
        """Signal shutdown on all active tasks and force-expire leases.

        Called by ``AgentServerHost`` during lifespan shutdown.
        """
        logger.info("DurableTaskManager shutting down")
        self._shutdown_event.set()

        # Signal shutdown on all active contexts
        for active in self._active_tasks.values():
            active.context.shutdown.set()

        # Wait for tasks to checkpoint before force-expiring leases
        if self._active_tasks:
            await asyncio.sleep(self._shutdown_grace_seconds)

        # Force-expire all leases
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

        # Cancel all renewal and execution tasks
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
        opts: DurableTaskOptions,
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
        :paramtype opts: DurableTaskOptions
        :keyword entry_mode: Entry mode.
        :paramtype entry_mode: EntryMode
        :keyword retry: Retry policy.
        :paramtype retry: RetryPolicy | None
        :keyword title: Human-readable title.
        :paramtype title: str
        :returns: The function's return value.
        :rtype: Any
        :raises TaskFailed: On unhandled exception.
        :raises TaskSuspended: If the function suspends.
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
        description: str | None = None,
        opts: DurableTaskOptions,
        retry: RetryPolicy | None = None,
        entry_mode: EntryMode = "fresh",
        stream_handler: StreamHandler | None = None,
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
        :keyword description: Optional task description.
        :paramtype description: str | None
        :keyword opts: Task options.
        :paramtype opts: DurableTaskOptions
        :keyword retry: Retry policy.
        :paramtype retry: RetryPolicy | None
        :keyword entry_mode: Why this execution is starting.
        :paramtype entry_mode: EntryMode
        :keyword stream_handler: Custom stream handler. If ``None``,
            a default :class:`QueueStreamHandler` is created.
        :paramtype stream_handler: StreamHandler | None
        :return: A ``TaskRun`` handle.
        :rtype: TaskRun
        """
        resolved_session = session_id or self._config.session_id or "local"
        agent_name = self._config.agent_name or "default"

        # Build payload
        payload: dict[str, Any] = {}
        if opts.store_input:
            payload["input"] = _serialize_input(input_val)
        payload["metadata"] = {}

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
                description=description,
                payload=payload,
                tags=tags or None,
                source=source,
                lease_owner=self._lease_owner,
                lease_instance_id=self._instance_id,
                lease_duration_seconds=opts.lease_duration_seconds,
            )
        )

        logger.info("Created durable task %s (%s)", task_id, fn_name)

        # Register resume callback
        self._resume_callbacks[fn_name] = fn

        # Build context
        cancel_event = asyncio.Event()
        handler = stream_handler or QueueStreamHandler()
        metadata = TaskMetadata(
            flush_callback=self._make_metadata_flush(task_id),
            flush_interval=5.0,
        )

        lease_gen = task_info.lease.generation if task_info.lease else 0

        ctx: TaskContext[Any] = TaskContext(
            task_id=task_id,
            title=title,
            description=description,
            session_id=resolved_session,
            agent_name=agent_name,
            tags=tags,
            input=input_val,
            metadata=metadata,
            run_attempt=0,
            lease_generation=lease_gen,
            cancel=cancel_event,
            shutdown=self._shutdown_event,
            stream_handler=handler,
            entry_mode=entry_mode,
            generation=0,
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
                lease_duration_seconds=opts.lease_duration_seconds,
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

        # Start metadata auto-flush
        metadata.start_auto_flush()

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

    def get_active_run(self, task_id: str) -> TaskRun[Any] | None:
        """Return a TaskRun handle for an active (in-progress) task.

        Enables late-join consumers to get a handle to a running task's
        stream without being the original caller of ``start()``/``run()``.
        Returns ``None`` if the task is not currently active in this process.

        :param task_id: The task identifier.
        :type task_id: str
        :return: A TaskRun bound to the active task's stream handler,
            or ``None`` if not active.
        :rtype: TaskRun[Any] | None
        """
        active = self._active_tasks.get(task_id)
        if active is None:
            return None
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

    async def _start_existing_task(  # pylint: disable=too-many-locals,too-many-statements
        self,
        *,
        fn: Callable[..., Awaitable[Any]],
        fn_name: str,
        task_info: TaskInfo,
        entry_mode: EntryMode,
        input_val: Any | None = None,
        input_type: type[Any] | None = None,
        opts: DurableTaskOptions | None = None,
        retry: RetryPolicy | None = None,
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
        :paramtype opts: DurableTaskOptions | None
        :keyword retry: Retry policy.
        :paramtype retry: RetryPolicy | None
        :return: A TaskRun handle.
        :rtype: TaskRun[Any]
        """
        task_id = task_info.id
        resolved_opts = opts or DurableTaskOptions(name=fn_name, ephemeral=False)
        lease_duration = resolved_opts.lease_duration_seconds

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
        handler = QueueStreamHandler()
        existing_metadata = (
            task_info.payload.get("metadata", {}) if task_info.payload else {}
        )
        metadata = TaskMetadata(
            initial=existing_metadata,
            flush_callback=self._make_metadata_flush(task_id),
            flush_interval=5.0,
        )

        lease_gen = task_info.lease.generation if task_info.lease else 0

        # Extract steering context from payload
        steering = (task_info.payload or {}).get("_steering", {})
        # Detect steering context from payload (covers recovered-mid-drain)
        was_steered = bool(
            steering.get("drain_in_progress")
            or steering.get("pending_inputs")
            or steering.get("generation", 0) > 0
        )

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

        prev_input_raw = steering.get("previous_input")
        previous_input = None
        if prev_input_raw is not None and input_type is not None:
            previous_input = _deserialize_input(prev_input_raw, input_type)
        elif prev_input_raw is not None:
            previous_input = prev_input_raw
        pending_snapshot = tuple(steering.get("pending_inputs", ()))
        generation = steering.get("generation", 0)

        # Pre-set cancel if cancel_requested is True (steering short-circuit)
        if steering.get("cancel_requested"):
            cancel_event.set()

        ctx: TaskContext[Any] = TaskContext(
            task_id=task_id,
            title=task_info.title or "",
            description=task_info.description,
            session_id=task_info.session_id,
            agent_name=task_info.agent_name,
            tags=task_info.tags or {},
            input=resolved_input,
            metadata=metadata,
            run_attempt=0,
            lease_generation=lease_gen,
            cancel=cancel_event,
            shutdown=self._shutdown_event,
            stream_handler=handler,
            entry_mode=entry_mode,
            was_steered=was_steered,
            pending_inputs=pending_snapshot,
            generation=generation,
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
        metadata.start_auto_flush()

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
    ) -> None:
        """Background watchdog that enforces execution timeout.

        After *timeout_seconds*, sets *cancel_event* (cooperative).
        The function is expected to check ``ctx.cancel`` and exit
        gracefully.  If it doesn't, the lease will eventually expire
        and the task will be recovered.

        :param timeout_seconds: Seconds before cooperative cancel.
        :type timeout_seconds: float
        :param cancel_event: Event to set for cooperative cancel.
        :type cancel_event: asyncio.Event
        """
        await asyncio.sleep(timeout_seconds)
        cancel_event.set()
        logger.info(
            "Timeout watchdog fired cooperative cancel after %.1fs", timeout_seconds
        )

    async def _execute_task(
        self,
        *,
        fn: Callable[..., Awaitable[Any]],
        ctx: TaskContext[Any],
        task_id: str,
        opts: DurableTaskOptions,
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
        :paramtype opts: DurableTaskOptions
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
        opts: DurableTaskOptions,
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
        :paramtype opts: DurableTaskOptions
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
        attempt = 0
        # Mutable ref: steering drain may swap the active result_future
        current_result_future = result_future
        while True:
            ctx.run_attempt = attempt
            try:
                result = await fn(ctx)

                if isinstance(result, Suspended):
                    # STEERING: check for pending inputs BEFORE persisting suspend
                    if opts.steerable:
                        new_ctx = await self._try_drain_steering(
                            task_id=task_id,
                            ctx=ctx,
                            opts=opts,
                            result_future=current_result_future,
                        )
                        if new_ctx is not None:
                            # Drain found pending input — loop with new context
                            ctx = new_ctx
                            attempt = 0
                            # Update result future to the new generation's future
                            active = self._active_tasks.get(task_id)
                            if (
                                active
                                and active.result_future is not current_result_future
                            ):
                                current_result_future = active.result_future
                            continue

                    # No pending steering — normal suspend flow
                    renewal_cancel.set()
                    await ctx.metadata.stop_auto_flush()
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
                else:
                    # Guard: task functions must return raw output, not TaskResult
                    if isinstance(result, TaskResult):
                        raise TypeError(
                            "Task function returned TaskResult directly. "
                            "Return raw output instead — the framework wraps "
                            "it in TaskResult automatically."
                        )

                    # STEERING: check for pending before completing
                    if opts.steerable:
                        new_ctx = await self._try_drain_steering(
                            task_id=task_id,
                            ctx=ctx,
                            opts=opts,
                            result_future=current_result_future,
                            partial_output=result,
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

                    # Success flow
                    renewal_cancel.set()
                    await ctx.metadata.stop_auto_flush()
                    completed = await self._handle_success(
                        task_id=task_id,
                        result=result,
                        metadata=ctx.metadata,
                        opts=opts,
                    )
                    if not completed:
                        # Etag conflict on steerable completion — re-drain
                        renewal_cancel = asyncio.Event()  # reset for next iteration
                        new_ctx = await self._try_drain_steering(
                            task_id=task_id,
                            ctx=ctx,
                            opts=opts,
                            result_future=current_result_future,
                            partial_output=result,
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
                        # No pending found despite conflict — complete anyway
                    if not current_result_future.done():
                        current_result_future.set_result(
                            TaskResult(
                                task_id=task_id,
                                output=result,
                                status="completed",
                            )
                        )

                break  # exit retry loop on success or suspend

            except asyncio.CancelledError:
                renewal_cancel.set()
                await ctx.metadata.stop_auto_flush()
                if resolved_terminate.is_set():
                    # Forced termination (timeout or explicit terminate())
                    from ._exceptions import (  # pylint: disable=import-outside-toplevel
                        TaskTerminated,
                    )

                    await self._handle_failure(
                        task_id=task_id,
                        exc=TaskTerminated(task_id, reason=reason_ref[0]),
                        metadata=ctx.metadata,
                        opts=opts,
                    )
                    if not current_result_future.done():
                        current_result_future.set_exception(
                            TaskTerminated(task_id, reason=reason_ref[0])
                        )
                else:
                    # Cooperative cancellation (suspend or caller cancel)
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
                    # Update error field so observers see intermediate failures
                    try:
                        await self._provider.update(
                            task_id,
                            TaskPatchRequest(
                                error={
                                    "type": type(exc).__name__,
                                    "message": str(exc),
                                    "attempt": attempt,
                                }
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
                await ctx.metadata.stop_auto_flush()

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
        opts: DurableTaskOptions,
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
        :keyword partial_output: Output from the completed generation (for race recovery).
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
        previous_input_raw = steering.get("active_input")

        # Update steering state
        steering["active_input"] = next_input_raw
        if previous_input_raw is not None:
            steering["previous_input"] = previous_input_raw
        steering["pending_inputs"] = pending
        old_generation = steering.get("generation", 0)
        steering["generation"] = old_generation + 1
        steering["cancel_requested"] = len(pending) > 0
        steering["drain_in_progress"] = True

        # Save partial output if function completed (race recovery)
        if partial_output is not None:
            gen_results = dict(steering.get("generation_results", {}))
            gen_results[str(old_generation)] = _serialize_input(partial_output)
            steering["generation_results"] = gen_results

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

        # Resolve the superseded generation's future (only for external steer callers)
        if had_registered_future and not result_future.done():
            result_future.set_result(
                TaskResult(task_id=task_id, output=partial_output, status="superseded")
            )

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

        # Deserialize previous input
        previous_input = None
        if previous_input_raw is not None and input_type is not None:
            previous_input = _deserialize_input(previous_input_raw, input_type)
        elif previous_input_raw is not None:
            previous_input = previous_input_raw

        # Build new context, reusing metadata and shutdown event
        cancel_event = asyncio.Event()
        if steering["cancel_requested"]:
            cancel_event.set()

        new_ctx: TaskContext[Any] = TaskContext(
            task_id=task_id,
            title=ctx.title,
            description=ctx.description,
            session_id=ctx.session_id,
            agent_name=ctx.agent_name,
            tags=ctx.tags,
            input=resolved_input,
            metadata=ctx.metadata,
            run_attempt=0,
            lease_generation=ctx.lease_generation,
            cancel=cancel_event,
            shutdown=ctx.shutdown,
            stream_handler=ctx._stream_handler,  # pylint: disable=protected-access
            entry_mode="resumed",
            was_steered=True,
            previous_input=previous_input,
            pending_inputs=tuple(pending),
            generation=old_generation + 1,
        )

        # Update active task tracking
        if active_task is not None:
            active_task.context = new_ctx
            if new_future is not None:
                active_task.result_future = new_future

        # Clear drain_in_progress
        steering["drain_in_progress"] = False
        payload["_steering"] = steering
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
        opts: DurableTaskOptions,
    ) -> bool:
        """Handle successful task completion.

        :keyword task_id: The task identifier.
        :paramtype task_id: str
        :keyword result: The task result value.
        :paramtype result: Any
        :keyword metadata: The task metadata.
        :paramtype metadata: TaskMetadata
        :keyword opts: The task options.
        :paramtype opts: DurableTaskOptions
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
        opts: DurableTaskOptions,
    ) -> None:
        """Handle task failure.

        :keyword task_id: The task identifier.
        :paramtype task_id: str
        :keyword exc: The exception that caused the failure.
        :paramtype exc: Exception
        :keyword metadata: The task metadata.
        :paramtype metadata: TaskMetadata
        :keyword opts: The task options.
        :paramtype opts: DurableTaskOptions
        """
        error_dict = {
            "type": type(exc).__name__,
            "message": str(exc),
            "traceback": traceback.format_exc(),
        }

        if opts.ephemeral:
            try:
                await self._provider.delete(task_id, force=True)
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
        opts: DurableTaskOptions,  # pylint: disable=unused-argument
    ) -> None:
        """Handle task suspension.

        :keyword task_id: The task identifier.
        :paramtype task_id: str
        :keyword reason: Optional suspension reason.
        :paramtype reason: str | None
        :keyword output: Optional output snapshot.
        :paramtype output: Any | None
        :keyword metadata: The task metadata.
        :paramtype metadata: TaskMetadata
        :keyword opts: The task options.
        :paramtype opts: DurableTaskOptions
        """
        payload_patch: dict[str, Any] = {
            "metadata": metadata.to_dict(),
        }
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
                        lease_duration_seconds=60,
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
                    await self.handle_resume(task_info.id)
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
    ) -> Callable[[dict[str, Any]], Awaitable[None]]:
        """Create a flush callback for metadata persistence.

        :param task_id: The task identifier.
        :type task_id: str
        :return: An async callback that flushes metadata.
        :rtype: Callable[[dict[str, Any]], Awaitable[None]]
        """

        async def _flush(data: dict[str, Any]) -> None:
            await self._provider.update(
                task_id,
                TaskPatchRequest(payload={"metadata": data}),
            )

        return _flush
