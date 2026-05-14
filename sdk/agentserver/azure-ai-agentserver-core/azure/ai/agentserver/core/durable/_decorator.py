# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""``@durable_task`` decorator — turns an async function into a crash-resilient
unit of work with automatic task lifecycle management.

Usage::

    from azure.ai.agentserver.core.durable import durable_task, TaskContext

    @durable_task
    async def my_task(ctx: TaskContext[MyInput]) -> MyOutput:
        ...

    result = await my_task.run(task_id="t1", input=MyInput(...))
"""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import inspect
import logging as _logging
from collections.abc import Awaitable, Callable
from datetime import timedelta
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    TypeVar,
    get_args,
    get_type_hints,
    overload,
)

import re

from ._context import TaskContext
from ._result import TaskResult
from ._retry import RetryPolicy
from ._run import TaskRun
from ._stream import StreamHandler

if TYPE_CHECKING:
    from ._models import TaskStatus

Input = TypeVar("Input")
Output = TypeVar("Output")
F = TypeVar("F", bound=Callable[..., Any])

_VALID_TASK_ID_RE = re.compile(r"^[a-zA-Z0-9\-_.:]+$")
_MAX_TASK_ID_LENGTH = 256

#: Prefix for framework-reserved tags. Developer tags with this prefix are
#: silently stripped to prevent collisions with auto-stamped tags.
_RESERVED_TAG_PREFIX = "_durable_task_"

_logger = _logging.getLogger("azure.ai.agentserver.durable")


def _strip_reserved_tags(tags: dict[str, str]) -> dict[str, str]:
    """Remove framework-reserved tags from developer-provided tags.

    Tags prefixed with ``_durable_task_`` are reserved for framework use.
    If a developer provides them, they are silently dropped with a warning.

    :param tags: Developer-provided tags.
    :type tags: dict[str, str]
    :return: Tags with reserved keys removed.
    :rtype: dict[str, str]
    """
    reserved = [k for k in tags if k.startswith(_RESERVED_TAG_PREFIX)]
    if reserved:
        _logger.warning(
            "Ignoring reserved tag(s) %s — tags prefixed with %r are "
            "framework-owned and cannot be overridden",
            reserved,
            _RESERVED_TAG_PREFIX,
        )
        return {k: v for k, v in tags.items() if not k.startswith(_RESERVED_TAG_PREFIX)}
    return tags


def _validate_task_id(task_id: str) -> None:
    if not task_id or len(task_id) > _MAX_TASK_ID_LENGTH:
        raise ValueError(
            f"task_id must be 1-{_MAX_TASK_ID_LENGTH} characters, "
            f"got {len(task_id)}"
        )
    if not _VALID_TASK_ID_RE.match(task_id):
        raise ValueError(
            f"task_id contains invalid characters: {task_id!r}. "
            f"Allowed: [a-zA-Z0-9\\-_.:] "
        )


def _extract_generic_args(
    fn: Callable[..., Any],
) -> tuple[type[Any], type[Any]]:
    """Extract Input and Output types from a durable task function signature.

    The function must accept a single ``TaskContext[Input]`` parameter
    and return ``Output``.

    :param fn: The async function to inspect.
    :type fn: Callable[..., Any]
    :returns: ``(InputType, OutputType)`` tuple.
    :rtype: tuple[type[Any], type[Any]]
    :raises TypeError: If the signature doesn't match expectations.
    """
    hints = get_type_hints(fn)
    params = list(inspect.signature(fn).parameters.values())

    # Find the TaskContext parameter
    ctx_param = None
    for p in params:
        hint = hints.get(p.name)
        if hint is not None:
            origin = getattr(hint, "__origin__", None)
            if origin is TaskContext:
                ctx_param = p
                break

    if ctx_param is None:
        raise TypeError(
            f"Durable task function {fn.__qualname__!r} must accept a "
            f"TaskContext[Input] parameter"
        )

    ctx_hint = hints[ctx_param.name]
    args = get_args(ctx_hint)
    input_type: type[Any] = args[0] if args else Any

    return_hint = hints.get("return", Any)
    # Unwrap Optional, Awaitable, etc.
    output_type: type[Any] = return_hint if return_hint is not None else type(None)

    return input_type, output_type


def _serialize_input(value: Any) -> Any:
    """Serialize an input value for storage in the task payload.

    :param value: The input value to serialize.
    :type value: Any
    :return: The serialized form of the input.
    :rtype: Any
    """
    # Pydantic model
    if hasattr(value, "model_dump"):
        return value.model_dump()
    # Plain JSON-serializable
    return value


def _deserialize_input(value: Any, input_type: type[Any]) -> Any:
    """Deserialize an input value from the task payload.

    :param value: The serialized input value.
    :type value: Any
    :param input_type: The expected type to deserialize into.
    :type input_type: type[Any]
    :return: The deserialized input value.
    :rtype: Any
    """
    if value is None:
        return None
    # Pydantic model
    if hasattr(input_type, "model_validate"):
        return input_type.model_validate(value)
    # dict-constructable class
    if (
        isinstance(value, dict)
        and callable(input_type)
        and input_type not in (dict, str, int, float, bool, list)
    ):
        try:
            return input_type(**value)
        except TypeError:
            pass
    return value


def _is_stale(task_updated_at: str, timeout: float) -> bool:
    """Check if an in_progress task is stale based on its updated_at timestamp.

    :param task_updated_at: ISO 8601 timestamp of the task's last update.
    :type task_updated_at: str
    :param timeout: Seconds after which the task is considered stale.
    :type timeout: float
    :returns: True if the task is stale.
    :rtype: bool
    """
    if not task_updated_at:
        return False
    from datetime import datetime, timezone  # pylint: disable=import-outside-toplevel

    updated = datetime.fromisoformat(task_updated_at)
    now = datetime.now(timezone.utc)
    if updated.tzinfo is None:
        updated = updated.replace(tzinfo=timezone.utc)
    return (now - updated).total_seconds() > timeout


class DurableTaskOptions:  # pylint: disable=too-many-instance-attributes
    """Options for a durable task.

    :param name: **Stable identity anchor.** Used for recovery routing and
        source stamping.  If you rename the Python function later, existing
        in-flight tasks are still recovered correctly because the framework
        matches on this name.
    :type name: str
    :param title: Human-readable title template.
    :type title: str | Callable[[Any, str], str] | None
    :param tags: Default tags (static dict or callable factory).
    :type tags: dict[str, str] | Callable[[Any, str], dict[str, str]]
    :param description: Task description (static string or callable factory).
    :type description: str | Callable[[Any, str], str] | None
    :param timeout: Execution timeout.
    :type timeout: timedelta | None
    :param lease_duration_seconds: Lease TTL.
    :type lease_duration_seconds: int
    :param store_input: Whether to persist input on the task record.
    :type store_input: bool
    :param ephemeral: Whether to delete on terminal exit.
    :type ephemeral: bool
    """

    __slots__ = (
        "name",
        "title",
        "tags",
        "description",
        "timeout",
        "lease_duration_seconds",
        "store_input",
        "ephemeral",
        "retry",
        "steerable",
        "max_pending",
    )

    def __init__(
        self,
        name: str,
        title: str | Callable[[Any, str], str] | None = None,
        tags: dict[str, str] | Callable[[Any, str], dict[str, str]] | None = None,
        description: str | Callable[[Any, str], str | None] | None = None,
        timeout: timedelta | None = None,
        lease_duration_seconds: int = 60,
        store_input: bool = True,
        ephemeral: bool = True,
        retry: RetryPolicy | None = None,
        steerable: bool = False,
        max_pending: int = 10,
    ) -> None:
        self.name = name
        self.title = title
        self.tags = tags if tags is not None else {}
        self.description = description
        self.timeout = timeout
        self.lease_duration_seconds = lease_duration_seconds
        self.store_input = store_input
        self.ephemeral = ephemeral
        self.retry = retry
        self.steerable = steerable
        self.max_pending = max_pending

    def __repr__(self) -> str:
        return (
            f"DurableTaskOptions(name={self.name!r}, lease_duration_seconds={self.lease_duration_seconds}, "
            f"store_input={self.store_input}, ephemeral={self.ephemeral}, retry={self.retry!r}, "
            f"timeout={self.timeout!r}, "
            f"steerable={self.steerable}, max_pending={self.max_pending})"
        )


class DurableTask(Generic[Input, Output]):
    """A decorated durable task function. Not callable directly.

    Use :meth:`run` (invoke-and-wait), :meth:`start` (fire-and-forget),
    or :meth:`options` (per-call overrides).

    :param fn: The decorated async function.
    :param opts: Frozen task options.
    :param input_type: Extracted input type.
    :param output_type: Extracted output type.
    """

    __slots__ = ("_fn", "_opts", "_input_type", "_output_type", "name")

    def __init__(
        self,
        fn: Callable[[TaskContext[Input]], Awaitable[Output]],
        opts: DurableTaskOptions,
        input_type: type[Input],
        output_type: type[Output],
    ) -> None:
        self._fn = fn
        self._opts = opts
        self._input_type = input_type
        self._output_type = output_type
        self.name = opts.name

    def _resolve_title(self, input_val: Input, task_id: str) -> str:
        if callable(self._opts.title):
            return self._opts.title(input_val, task_id)
        if isinstance(self._opts.title, str):
            return self._opts.title
        return f"{self.name}:{task_id[:8]}"

    def _resolve_tags(self, input_val: Input, task_id: str) -> dict[str, str]:
        """Resolve decorator-level tags (static dict or callable factory).

        Reserved tags (prefixed with ``_durable_task_``) are stripped to
        prevent developer code from colliding with framework-stamped tags.

        :param input_val: The task input value.
        :type input_val: Input
        :param task_id: The task identifier.
        :type task_id: str
        :return: Resolved tags dictionary.
        :rtype: dict[str, str]
        """
        tags = self._opts.tags
        if callable(tags):
            result = tags(input_val, task_id)
            if not isinstance(result, dict):
                raise TypeError(
                    f"tags callable must return dict[str, str], "
                    f"got {type(result).__name__}"
                )
            return _strip_reserved_tags(result)
        return _strip_reserved_tags(dict(tags) if tags else {})

    def _resolve_description(self, input_val: Input, task_id: str) -> str | None:
        """Resolve decorator-level description (static or callable).

        :param input_val: The task input value.
        :type input_val: Input
        :param task_id: The task identifier.
        :type task_id: str
        :return: Resolved description string or None.
        :rtype: str | None
        """
        desc = self._opts.description
        if callable(desc):
            result = desc(input_val, task_id)
            if result is not None and not isinstance(result, str):
                raise TypeError(
                    f"description callable must return str or None, "
                    f"got {type(result).__name__}"
                )
            return result
        return desc

    def _merge_tags(
        self, input_val: Input, task_id: str, call_tags: dict[str, str] | None
    ) -> dict[str, str]:
        merged = self._resolve_tags(input_val, task_id)
        if call_tags:
            merged.update(_strip_reserved_tags(call_tags))
        return merged

    async def run(
        self,
        *,
        task_id: str,
        input: Input,  # noqa: A002
        session_id: str | None = None,
        title: str | None = None,
        tags: dict[str, str] | None = None,
        retry: RetryPolicy | None = None,
        stale_timeout: float = 300.0,
        stream_handler: StreamHandler | None = None,
    ) -> TaskResult[Output]:
        """Run a lifecycle-aware durable task and return the result.

        Automatically starts, resumes, or recovers the task based on its
        current state:

        - No task / pending → create and start (``entry_mode="fresh"``)
        - Suspended → resume with new input (``entry_mode="resumed"``)
        - In-progress (stale) → recover (``entry_mode="recovered"``)
        - In-progress (not stale) → raise :class:`TaskConflictError`
        - Completed → raise :class:`TaskConflictError`

        :keyword task_id: Unique task identifier.
        :paramtype task_id: str
        :keyword input: Typed input value.
        :paramtype input: Input
        :keyword session_id: Session scope override.
        :paramtype session_id: str | None
        :keyword title: Title override.
        :paramtype title: str | None
        :keyword tags: Per-call tag overrides.
        :paramtype tags: dict[str, str] | None
        :keyword retry: Retry policy override. Overrides decorator-level retry.
        :paramtype retry: ~azure.ai.agentserver.core.durable.RetryPolicy | None
        :keyword stale_timeout: Seconds before an in-progress task is considered
            stale and eligible for recovery. Default 300 (5 minutes).
        :paramtype stale_timeout: float
        :keyword stream_handler: Custom stream handler for pluggable streaming.
            If ``None``, a default :class:`QueueStreamHandler` is used.
        :paramtype stream_handler: ~azure.ai.agentserver.core.durable.StreamHandler | None
        :return: The task result wrapper with output, status, and suspension info.
        :rtype: ~azure.ai.agentserver.core.durable.TaskResult[Output]
        :raises TaskFailed: On unhandled exception.
        :raises ~azure.ai.agentserver.core.durable.TaskConflictError: If the
            task is already in-progress or completed.
        """
        _validate_task_id(task_id)
        handle = await self._lifecycle_start(
            task_id=task_id,
            input=input,
            session_id=session_id,
            title=title,
            tags=tags,
            retry=retry,
            stale_timeout=stale_timeout,
            stream_handler=stream_handler,
        )
        return await handle.result()

    async def start(
        self,
        *,
        task_id: str,
        input: Input,  # noqa: A002
        session_id: str | None = None,
        title: str | None = None,
        tags: dict[str, str] | None = None,
        retry: RetryPolicy | None = None,
        stale_timeout: float = 300.0,
        stream_handler: StreamHandler | None = None,
    ) -> TaskRun[Output]:
        """Start a lifecycle-aware durable task and return a handle.

        Follows the same lifecycle rules as :meth:`run` but returns
        immediately with a :class:`TaskRun` handle instead of blocking.

        :keyword task_id: Unique task identifier.
        :paramtype task_id: str
        :keyword input: Typed input value.
        :paramtype input: Input
        :keyword session_id: Session scope override.
        :paramtype session_id: str | None
        :keyword title: Title override.
        :paramtype title: str | None
        :keyword tags: Per-call tag overrides.
        :paramtype tags: dict[str, str] | None
        :keyword retry: Retry policy override. Overrides decorator-level retry.
        :paramtype retry: ~azure.ai.agentserver.core.durable.RetryPolicy | None
        :keyword stale_timeout: Seconds before an in-progress task is considered
            stale and eligible for recovery. Default 300 (5 minutes).
        :paramtype stale_timeout: float
        :keyword stream_handler: Custom stream handler for pluggable streaming.
            If ``None``, a default :class:`QueueStreamHandler` is used.
        :paramtype stream_handler: ~azure.ai.agentserver.core.durable.StreamHandler | None
        :return: A handle to the running task.
        :rtype: TaskRun[Output]
        :raises ~azure.ai.agentserver.core.durable.TaskConflictError: If the
            task is already in-progress or completed.
        """
        _validate_task_id(task_id)
        return await self._lifecycle_start(
            task_id=task_id,
            input=input,
            session_id=session_id,
            title=title,
            tags=tags,
            retry=retry,
            stale_timeout=stale_timeout,
            stream_handler=stream_handler,
        )

    async def get(self, task_id: str) -> Any:
        """Return the full persisted task information.

        Works for any task state — running, suspended, completed, etc.
        Returns whatever is persisted. Returns ``None`` if no task exists.

        :param task_id: The task identifier.
        :type task_id: str
        :return: Task info or ``None`` if no task exists.
        :rtype: ~azure.ai.agentserver.core.durable.TaskInfo | None
        """
        from ._manager import (  # pylint: disable=import-outside-toplevel
            get_task_manager,
        )

        manager = get_task_manager()
        return await manager.provider.get(task_id)

    async def list(
        self,
        *,
        session_id: str | None = None,
        status: TaskStatus | None = None,
    ) -> list[Any]:
        """List tasks created by this durable task function.

        Automatically scoped to this function's ``name`` via the
        ``_durable_task_name`` tag (server-side) and ``source.type``
        (client-side). Only returns tasks created by this framework.

        :keyword session_id: Session scope override.  Defaults to the
            manager's configured session ID.
        :paramtype session_id: str | None
        :keyword status: Filter by task status (e.g., ``"in_progress"``,
            ``"suspended"``, ``"completed"``).
        :paramtype status: ~azure.ai.agentserver.core.durable.TaskStatus | None
        :return: Matching task records.
        :rtype: list[~azure.ai.agentserver.core.durable.TaskInfo]

        Example::

            tasks = await my_task.list(status="suspended")
            for t in tasks:
                print(t.id, t.status)
        """
        from ._manager import (  # pylint: disable=import-outside-toplevel
            get_task_manager,
        )

        manager = get_task_manager()
        return await manager.list_tasks(
            fn_name=self.name,
            session_id=session_id,
            status=status,
        )

    async def _append_steering_input(  # pylint: disable=protected-access
        self,
        manager: Any,
        *,
        task_id: str,
        input_val: Any,
        existing: Any,
    ) -> None:
        """Append a steering input to the task's pending queue."""
        from ._exceptions import (  # pylint: disable=import-outside-toplevel
            SteeringQueueFull,
        )
        from ._models import (  # pylint: disable=import-outside-toplevel
            TaskPatchRequest,
        )

        max_retries = 5
        serialized = _serialize_input(input_val)

        for _attempt in range(max_retries):
            task_info = (
                existing if _attempt == 0 else await manager.provider.get(task_id)
            )
            if task_info is None:
                raise RuntimeError(
                    f"Task {task_id!r} disappeared during steering append"
                )

            payload = dict(task_info.payload) if task_info.payload else {}
            steering = dict(payload.get("_steering", {}))
            pending: list[Any] = list(steering.get("pending_inputs", []))

            if len(pending) >= self._opts.max_pending:
                raise SteeringQueueFull(task_id, self._opts.max_pending)

            pending.append(serialized)
            steering["pending_inputs"] = pending
            steering["cancel_requested"] = True
            if "generation" not in steering:
                steering["generation"] = 0
            payload["_steering"] = steering

            etag = getattr(task_info, "etag", None) or None
            try:
                await manager.provider.update(
                    task_id,
                    TaskPatchRequest(payload=payload, if_match=etag),
                )
                # Signal the running task's cancel event so it can short-circuit
                active = manager._active_tasks.get(
                    task_id
                )  # pylint: disable=protected-access  # noqa: SLF001
                if active and hasattr(active, "context") and active.context is not None:
                    active.context.cancel.set()
                return
            except ValueError:
                # Local provider etag conflict — retry
                continue

        raise RuntimeError(
            f"Failed to append steering input after {max_retries} retries"
        )

    def _create_steering_ack_run(
        self,
        manager: Any,
        task_id: str,
        future: Any,
    ) -> TaskRun[Output]:
        """Create a TaskRun for a queued steering input."""
        return TaskRun(
            task_id=task_id,
            provider=manager.provider,
            result_future=future,
        )

    async def _lifecycle_start(
        self,
        *,
        task_id: str,
        input: Input,  # noqa: A002
        session_id: str | None,
        title: str | None,
        tags: dict[str, str] | None,
        retry: RetryPolicy | None,
        stale_timeout: float,
        stream_handler: StreamHandler | None = None,
    ) -> TaskRun[Output]:
        """Resolve lifecycle state and start/resume/recover accordingly.

        :keyword task_id: The task identifier.
        :paramtype task_id: str
        :keyword input: Typed input value.
        :paramtype input: Input
        :keyword session_id: Session scope override.
        :paramtype session_id: str | None
        :keyword title: Title override.
        :paramtype title: str | None
        :keyword tags: Per-call tag overrides.
        :paramtype tags: dict[str, str] | None
        :keyword retry: Retry policy override.
        :paramtype retry: RetryPolicy | None
        :keyword stale_timeout: Stale timeout in seconds.
        :paramtype stale_timeout: float
        :keyword stream_handler: Custom stream handler. Defaults to
            :class:`QueueStreamHandler` when ``None``.
        :paramtype stream_handler: StreamHandler | None
        :return: A handle to the running task.
        :rtype: TaskRun[Output]
        """
        from ._exceptions import (  # pylint: disable=import-outside-toplevel
            TaskConflictError,
        )
        from ._manager import (  # pylint: disable=import-outside-toplevel
            get_task_manager,
        )

        manager = get_task_manager()
        existing = await manager.provider.get(task_id)

        resolved_retry = retry or self._opts.retry

        if existing is None or existing.status == "pending":
            # Fresh start
            if existing is not None and existing.status == "pending":
                # Pending task exists — patch to in_progress and execute
                return await manager._start_existing_task(  # pylint: disable=protected-access
                    fn=self._fn,
                    fn_name=self.name,
                    task_info=existing,
                    entry_mode="fresh",
                    input_val=input,
                    input_type=self._input_type,
                    opts=self._opts,
                    retry=resolved_retry,
                )
            # No task exists — create new
            return await manager.create_and_start(
                fn=self._fn,
                fn_name=self.name,
                task_id=task_id,
                input_val=input,
                input_type=self._input_type,
                session_id=session_id,
                title=title or self._resolve_title(input, task_id),
                tags=self._merge_tags(input, task_id, tags),
                description=self._resolve_description(input, task_id),
                opts=self._opts,
                retry=resolved_retry,
                entry_mode="fresh",
                stream_handler=stream_handler,
            )

        if existing.status == "suspended":
            # Resume — patch input onto task, then start
            serialized = _serialize_input(input)
            from ._models import (  # pylint: disable=import-outside-toplevel
                TaskPatchRequest,
            )

            await manager.provider.update(
                task_id,
                TaskPatchRequest(payload={"input": serialized}),
            )
            # Re-fetch after input patch
            updated_info = await manager.provider.get(task_id)
            if updated_info is None:
                raise RuntimeError(f"Task {task_id!r} disappeared after input patch")
            return (
                await manager._start_existing_task(  # pylint: disable=protected-access
                    fn=self._fn,
                    fn_name=self.name,
                    task_info=updated_info,
                    entry_mode="resumed",
                    input_val=input,
                    input_type=self._input_type,
                    opts=self._opts,
                    retry=resolved_retry,
                )
            )

        if existing.status == "in_progress":
            if _is_stale(existing.updated_at, stale_timeout):
                # Stale — check for steering recovery state first
                if self._opts.steerable and existing.payload:
                    steering = existing.payload.get("_steering", {})
                    if steering.get("drain_in_progress") or steering.get(
                        "pending_inputs"
                    ):
                        # Stale with steering state — recover via steered path
                        return await manager._start_existing_task(  # pylint: disable=protected-access
                            fn=self._fn,
                            fn_name=self.name,
                            task_info=existing,
                            entry_mode="recovered",
                            input_val=input,
                            input_type=self._input_type,
                            opts=self._opts,
                            retry=resolved_retry,
                        )
                # Normal stale recovery
                return await manager._start_existing_task(  # pylint: disable=protected-access
                    fn=self._fn,
                    fn_name=self.name,
                    task_info=existing,
                    entry_mode="recovered",
                    input_val=input,
                    input_type=self._input_type,
                    opts=self._opts,
                    retry=resolved_retry,
                )
            if self._opts.steerable:
                # Steering path: append input to queue, signal cancel, return ack
                ack_future = manager._register_steering_future(
                    task_id
                )  # pylint: disable=protected-access
                await self._append_steering_input(
                    manager,
                    task_id=task_id,
                    input_val=input,
                    existing=existing,
                )
                # Set cancel on in-memory context if task runs in this process
                active = manager._active_tasks.get(
                    task_id
                )  # pylint: disable=protected-access
                if active:
                    active.context.cancel.set()
                return self._create_steering_ack_run(manager, task_id, ack_future)
            raise TaskConflictError(task_id, "in_progress")

        # completed (or any other terminal status)
        raise TaskConflictError(task_id, existing.status)

    def options(
        self,
        *,
        title: str | Callable[[Any, str], str] | None = None,
        tags: dict[str, str] | Callable[[Any, str], dict[str, str]] | None = None,
        description: str | Callable[[Any, str], str | None] | None = None,
        timeout: timedelta | None = None,
        lease_duration_seconds: int | None = None,
        store_input: bool | None = None,
        ephemeral: bool | None = None,
        retry: RetryPolicy | None = None,
        steerable: bool | None = None,
        max_pending: int | None = None,
    ) -> DurableTask[Input, Output]:
        """Return a new DurableTask with merged options.

        The original is unchanged.

        :keyword timeout: Execution timeout override.
        :paramtype timeout: timedelta | None
        :keyword ephemeral: Whether to delete task on terminal exit.
        :paramtype ephemeral: bool | None
        :keyword tags: Tag overrides.
        :paramtype tags: dict[str, str] | Callable[[Any, str], dict[str, str]] | None
        :keyword store_input: Whether to persist input.
        :paramtype store_input: bool | None
        :keyword retry: Retry policy override.
        :paramtype retry: RetryPolicy | None
        :keyword title: Title override.
        :paramtype title: str | Callable[[Any, str], str] | None
        :keyword description: Description override.
        :paramtype description: str | Callable[[Any, str], str | None] | None
        :keyword lease_duration_seconds: Lease TTL override.
        :paramtype lease_duration_seconds: int | None
        :keyword steerable: Whether this task accepts steering inputs.
        :paramtype steerable: bool | None
        :keyword max_pending: Maximum queued steering inputs.
        :paramtype max_pending: int | None
        :return: A new DurableTask with overridden options.
        :rtype: DurableTask[Input, Output]
        """
        # For tags: if both old and new are dicts, merge them.
        # Mixing callable and dict is not supported — use one or the other.
        resolved_tags: dict[str, str] | Callable[[Any, str], dict[str, str]] | None
        if tags is not None:
            if callable(tags) != callable(self._opts.tags) and self._opts.tags:
                raise TypeError(
                    "Cannot mix callable and dict tags in options(). "
                    "Pass a callable to replace a callable, or a dict to merge with a dict."
                )
            if callable(tags):
                resolved_tags = tags
            else:
                existing = self._opts.tags if isinstance(self._opts.tags, dict) else {}
                resolved_tags = _strip_reserved_tags({**existing, **(tags or {})})
        else:
            resolved_tags = self._opts.tags

        new_opts = DurableTaskOptions(
            name=self._opts.name,
            title=title if title is not None else self._opts.title,
            tags=resolved_tags,
            description=(
                description if description is not None else self._opts.description
            ),
            timeout=timeout if timeout is not None else self._opts.timeout,
            lease_duration_seconds=(
                lease_duration_seconds
                if lease_duration_seconds is not None
                else self._opts.lease_duration_seconds
            ),
            store_input=(
                store_input if store_input is not None else self._opts.store_input
            ),
            ephemeral=(ephemeral if ephemeral is not None else self._opts.ephemeral),
            retry=retry if retry is not None else self._opts.retry,
            steerable=(steerable if steerable is not None else self._opts.steerable),
            max_pending=(
                max_pending if max_pending is not None else self._opts.max_pending
            ),
        )
        return DurableTask(
            fn=self._fn,
            opts=new_opts,
            input_type=self._input_type,
            output_type=self._output_type,
        )


@overload
def durable_task(
    fn: Callable[[TaskContext[Input]], Awaitable[Output]],
) -> DurableTask[Input, Output]: ...


@overload
def durable_task(
    *,
    name: str | None = ...,
    title: str | Callable[[Any, str], str] | None = ...,
    tags: dict[str, str] | Callable[[Any, str], dict[str, str]] | None = ...,
    description: str | Callable[[Any, str], str | None] | None = ...,
    timeout: timedelta | None = ...,
    lease_duration_seconds: int = ...,
    store_input: bool = ...,
    ephemeral: bool = ...,
    retry: RetryPolicy | None = ...,
    steerable: bool = ...,
    max_pending: int = ...,
) -> Callable[
    [Callable[[TaskContext[Input]], Awaitable[Output]]],
    DurableTask[Input, Output],
]: ...


def durable_task(
    fn: Callable[..., Any] | None = None,
    *,
    name: str | None = None,
    title: str | Callable[[Any, str], str] | None = None,
    tags: dict[str, str] | Callable[[Any, str], dict[str, str]] | None = None,
    description: str | Callable[[Any, str], str | None] | None = None,
    timeout: timedelta | None = None,
    lease_duration_seconds: int = 60,
    store_input: bool = True,
    ephemeral: bool = True,
    retry: RetryPolicy | None = None,
    steerable: bool = False,
    max_pending: int = 10,
) -> Any:
    """Turn an async function into a crash-resilient durable task.

    Can be used with or without arguments::

        @durable_task
        async def my_task(ctx: TaskContext[MyInput]) -> MyOutput: ...

        @durable_task(name="custom-name", ephemeral=False)
        async def my_task(ctx: TaskContext[MyInput]) -> MyOutput: ...

    :param fn: The async function to decorate (when used without parens).
    :type fn: Callable[..., Any] | None
    :keyword name: **Stable identity anchor.** Used for recovery routing and
        source stamping. Defaults to ``fn.__qualname__``. Always provide an
        explicit name for production tasks — if you rename the function later,
        existing in-flight tasks are still recovered correctly because the
        framework matches on this name, not the Python function name.
    :keyword title: Human-readable title (string or callable).
    :keyword tags: Default tags (static dict or callable factory receiving
        ``(input, task_id)``). Merged with per-call ``tags=`` overrides.
    :keyword description: Task description (static string or callable factory
        receiving ``(input, task_id)``).
    :keyword timeout: Execution timeout. When elapsed, ``ctx.cancel`` is set
        cooperatively. If the function does not exit, the lease eventually
        expires and the task is recovered.
    :keyword lease_duration_seconds: Lease TTL (default 60).
    :keyword store_input: Whether to persist input on the task record.
    :keyword ephemeral: Delete task on terminal exit (default True).
    :keyword retry: Default retry policy for this task.
    :keyword steerable: Whether this task accepts steering inputs. When True,
        calling ``start()`` on an ``in_progress`` task queues the input and
        signals cancel instead of raising ``TaskConflictError``. Default False.
    :keyword max_pending: Maximum number of queued steering inputs. Default 10.
    :return: A ``DurableTask[Input, Output]`` wrapper.
    :rtype: Any
    """

    def _wrap(
        func: Callable[..., Any],
    ) -> DurableTask[Any, Any]:
        if not asyncio.iscoroutinefunction(func):
            raise TypeError(
                f"@durable_task requires an async function, "
                f"got {func.__qualname__!r}"
            )

        if lease_duration_seconds < 1:
            raise ValueError(
                f"lease_duration_seconds must be >= 1, got {lease_duration_seconds}"
            )

        if max_pending < 1:
            raise ValueError(f"max_pending must be >= 1, got {max_pending}")

        input_type, output_type = _extract_generic_args(func)

        # Preserve callable tags as-is (stripped at resolve time); strip static dicts now
        resolved_tags = (
            tags if callable(tags) else _strip_reserved_tags(dict(tags) if tags else {})
        )

        opts = DurableTaskOptions(
            name=name or func.__qualname__,
            title=title,
            tags=resolved_tags,
            description=description,
            timeout=timeout,
            lease_duration_seconds=lease_duration_seconds,
            store_input=store_input,
            ephemeral=ephemeral,
            retry=retry,
            steerable=steerable,
            max_pending=max_pending,
        )

        task = DurableTask(
            fn=func,
            opts=opts,
            input_type=input_type,
            output_type=output_type,
        )
        return task

    if fn is not None:
        return _wrap(fn)
    return _wrap
