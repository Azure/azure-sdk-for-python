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
from ._models import TaskCreateRequest, TaskInfo, TaskPatchRequest
from ._provider import DurableTaskProvider
from ._result import TaskResult
from ._retry import RetryPolicy
from ._run import Suspended, TaskRun

logger = logging.getLogger("azure.ai.agentserver.durable")

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
            "are enabled on the AgentServerHost."
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


class _ActiveTask:
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
    ) -> None:
        self.task_id = task_id
        self.fn_name = fn_name
        self.context = context
        self.execution_task = execution_task
        self.renewal_task = renewal_task
        self.renewal_cancel = renewal_cancel
        self.result_future = result_future
        self.terminate_event = terminate_event or asyncio.Event()


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
    """

    def __init__(
        self,
        config: AgentConfig,
        *,
        provider: DurableTaskProvider | None = None,
        shutdown_event: asyncio.Event | None = None,
    ) -> None:
        self._config = config
        self._provider = provider or self._create_provider(config)
        self._active_tasks: dict[str, _ActiveTask] = {}
        self._resume_callbacks: dict[str, Callable[..., Any]] = {}
        self._lease_owner = derive_lease_owner(config.session_id or "local")
        self._instance_id = generate_instance_id()
        self._shutdown_event = shutdown_event or asyncio.Event()

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
                "Task Storage API enabled via FOUNDRY_TASK_API_ENABLED; "
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

        # Wait briefly for tasks to checkpoint
        if self._active_tasks:
            await asyncio.sleep(2)

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
        source: dict[str, Any] | None = None,
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
        :keyword source: Provenance metadata.
        :paramtype source: dict[str, Any] | None
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
            source=source,
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
        source: dict[str, Any] | None = None,
        entry_mode: EntryMode = "fresh",
    ) -> TaskRun[Any]:
        """Create a task, start the function, and return a handle.

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
        :keyword source: Source provenance metadata.
        :paramtype source: dict[str, Any] | None
        :keyword entry_mode: Why this execution is starting.
        :paramtype entry_mode: EntryMode
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
        stream_queue: asyncio.Queue[Any] = asyncio.Queue()
        metadata = TaskMetadata(
            flush_callback=self._make_metadata_flush(task_id),
            flush_interval=5.0,
        )

        lease_gen = task_info.lease.generation if task_info.lease else 0

        ctx: TaskContext[Any] = TaskContext(
            task_id=task_id,
            title=title,
            session_id=resolved_session,
            agent_name=agent_name,
            tags=tags,
            input=input_val,
            metadata=metadata,
            run_attempt=0,
            lease_generation=lease_gen,
            cancel=cancel_event,
            shutdown=self._shutdown_event,
            stream_queue=stream_queue,
            entry_mode=entry_mode,
        )
        loop = asyncio.get_event_loop()
        result_future: asyncio.Future[Any] = loop.create_future()

        # Start lease renewal
        renewal_cancel = asyncio.Event()
        renewal_task = asyncio.create_task(
            lease_renewal_loop(
                self._provider,
                task_id,
                lease_owner=self._lease_owner,
                lease_instance_id=self._instance_id,
                lease_duration_seconds=opts.lease_duration_seconds,
                cancel_event=renewal_cancel,
                on_cancel_callback=cancel_event,
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
            stream_queue=stream_queue,
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

    async def _start_existing_task(  # pylint: disable=too-many-locals
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
        stream_queue: asyncio.Queue[Any] = asyncio.Queue()
        existing_metadata = (
            task_info.payload.get("metadata", {}) if task_info.payload else {}
        )
        metadata = TaskMetadata(
            initial=existing_metadata,
            flush_callback=self._make_metadata_flush(task_id),
            flush_interval=5.0,
        )

        lease_gen = task_info.lease.generation if task_info.lease else 0

        ctx: TaskContext[Any] = TaskContext(
            task_id=task_id,
            title=task_info.title or "",
            session_id=task_info.session_id,
            agent_name=task_info.agent_name,
            tags=task_info.tags or {},
            input=resolved_input,
            metadata=metadata,
            run_attempt=0,
            lease_generation=lease_gen,
            cancel=cancel_event,
            shutdown=self._shutdown_event,
            stream_queue=stream_queue,
            entry_mode=entry_mode,
        )

        loop = asyncio.get_event_loop()
        result_future: asyncio.Future[Any] = loop.create_future()

        renewal_cancel = asyncio.Event()
        renewal_task = asyncio.create_task(
            lease_renewal_loop(
                self._provider,
                task_id,
                lease_owner=self._lease_owner,
                lease_instance_id=self._instance_id,
                lease_duration_seconds=lease_duration,
                cancel_event=renewal_cancel,
                on_cancel_callback=cancel_event,
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
        )
        self._active_tasks[task_id] = active
        metadata.start_auto_flush()

        return TaskRun(
            task_id=task_id,
            provider=self._provider,
            result_future=result_future,
            metadata=metadata,
            cancel_event=cancel_event,
            stream_queue=stream_queue,
            terminate_event=terminate_event,
            execution_task=execution_task,
            terminate_reason_ref=terminate_reason_ref,
        )

    async def _timeout_watchdog(
        self,
        timeout_seconds: float,
        cancel_event: asyncio.Event,
        grace_seconds: float,
        execution_task: asyncio.Task[Any],
        terminate_event: asyncio.Event,
    ) -> None:
        """Background watchdog that enforces execution timeout.

        Phase 1: After *timeout_seconds*, sets *cancel_event* (cooperative).
        Phase 2: After *grace_seconds* more, sets *terminate_event* and
                 hard-cancels *execution_task*.

        :param timeout_seconds: Seconds before cooperative cancel.
        :type timeout_seconds: float
        :param cancel_event: Event to set for cooperative cancel.
        :type cancel_event: asyncio.Event
        :param grace_seconds: Grace period before hard cancel.
        :type grace_seconds: float
        :param execution_task: The task to hard-cancel.
        :type execution_task: asyncio.Task[Any]
        :param terminate_event: Event to set for hard cancel.
        :type terminate_event: asyncio.Event
        """
        await asyncio.sleep(timeout_seconds)
        cancel_event.set()
        logger.info(
            "Timeout watchdog fired cooperative cancel after %.1fs", timeout_seconds
        )
        await asyncio.sleep(grace_seconds)
        if not execution_task.done():
            terminate_event.set()
            execution_task.cancel()
            logger.warning(
                "Timeout watchdog escalated to hard cancel after %.1fs grace",
                grace_seconds,
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
            # We need a reference to the execution asyncio.Task, but we ARE
            # inside it. Get it from the running loop.
            current_task = asyncio.current_task()
            if current_task is not None:
                watchdog_task = asyncio.create_task(
                    self._timeout_watchdog(
                        timeout_seconds=opts.timeout.total_seconds(),
                        cancel_event=ctx.cancel,
                        grace_seconds=opts.cancel_grace_seconds,
                        execution_task=current_task,
                        terminate_event=resolved_terminate,
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

    async def _execute_task_loop(  # pylint: disable=too-many-statements
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
        reason_ref = terminate_reason_ref if terminate_reason_ref is not None else [None]
        attempt = 0
        while True:
            ctx.run_attempt = attempt
            try:
                result = await fn(ctx)

                # Stop lease renewal
                renewal_cancel.set()
                await ctx.metadata.stop_auto_flush()

                if isinstance(result, Suspended):
                    # Suspend flow — never retried
                    await self._handle_suspend(
                        task_id=task_id,
                        reason=result.reason,
                        output=result.output,
                        metadata=ctx.metadata,
                        opts=opts,
                    )
                    if not result_future.done():
                        result_future.set_result(
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
                    # Success flow
                    await self._handle_success(
                        task_id=task_id,
                        result=result,
                        metadata=ctx.metadata,
                        opts=opts,
                    )
                    if not result_future.done():
                        result_future.set_result(
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
                    if not result_future.done():
                        result_future.set_exception(
                            TaskTerminated(task_id, reason=reason_ref[0])
                        )
                else:
                    # Cooperative cancellation (suspend or caller cancel)
                    if not result_future.done():
                        from ._exceptions import (  # pylint: disable=import-outside-toplevel
                            TaskCancelled,
                        )

                        result_future.set_exception(TaskCancelled(task_id))
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
                if not result_future.done():
                    result_future.set_exception(TaskFailed(task_id, error_dict))
                break

        self._active_tasks.pop(task_id, None)
        # Signal end of streaming to any async-for consumers
        if ctx._stream_queue is not None:  # pylint: disable=protected-access
            from ._run import (
                _STREAM_SENTINEL,
            )  # pylint: disable=import-outside-toplevel

            await ctx._stream_queue.put(_STREAM_SENTINEL)  # pylint: disable=protected-access

    async def _handle_success(
        self,
        *,
        task_id: str,
        result: Any,
        metadata: TaskMetadata,
        opts: DurableTaskOptions,
    ) -> None:
        """Handle successful task completion.

        :keyword task_id: The task identifier.
        :paramtype task_id: str
        :keyword result: The task result value.
        :paramtype result: Any
        :keyword metadata: The task metadata.
        :paramtype metadata: TaskMetadata
        :keyword opts: The task options.
        :paramtype opts: DurableTaskOptions
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

        :param task_info: The task record to match.
        :type task_info: TaskInfo
        :return: A matching resume callback, or None.
        :rtype: Callable[..., Any] | None
        """
        # Try to find by title prefix or any registered callback
        for name, fn in self._resume_callbacks.items():
            if task_info.title and task_info.title.startswith(name):
                return fn
        # Fall back to the first registered callback if only one exists
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
