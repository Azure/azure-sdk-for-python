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
from collections.abc import Awaitable, Callable
from datetime import timedelta
from typing import Any, Generic, TypeVar, get_args, get_type_hints, overload

import re

from ._context import TaskContext
from ._result import TaskResult
from ._retry import RetryPolicy
from ._run import TaskRun

Input = TypeVar("Input")
Output = TypeVar("Output")
F = TypeVar("F", bound=Callable[..., Any])

_VALID_TASK_ID_RE = re.compile(r"^[a-zA-Z0-9\-_.:]+$")
_MAX_TASK_ID_LENGTH = 256


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

    :param name: Task function name.
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
        "source",
        "cancel_grace_seconds",
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
        source: dict[str, Any] | None = None,
        cancel_grace_seconds: float = 5.0,
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
        self.source = source
        self.cancel_grace_seconds = cancel_grace_seconds

    def __repr__(self) -> str:
        return (
            f"DurableTaskOptions(name={self.name!r}, lease_duration_seconds={self.lease_duration_seconds}, "
            f"store_input={self.store_input}, ephemeral={self.ephemeral}, retry={self.retry!r}, "
            f"timeout={self.timeout!r}, cancel_grace_seconds={self.cancel_grace_seconds})"
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

    def _resolve_tags(
        self, input_val: Input, task_id: str
    ) -> dict[str, str]:
        """Resolve decorator-level tags (static dict or callable factory).

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
            return result
        return dict(tags) if tags else {}

    def _resolve_description(
        self, input_val: Input, task_id: str
    ) -> str | None:
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
            merged.update(call_tags)
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
        source: dict[str, Any] | None = None,
        stale_timeout: float = 300.0,
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
        :keyword source: Provenance metadata override. Overrides decorator-level source.
        :paramtype source: dict[str, Any] | None
        :keyword stale_timeout: Seconds before an in-progress task is considered
            stale and eligible for recovery. Default 300 (5 minutes).
        :paramtype stale_timeout: float
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
            source=source,
            stale_timeout=stale_timeout,
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
        source: dict[str, Any] | None = None,
        stale_timeout: float = 300.0,
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
        :keyword source: Provenance metadata override. Overrides decorator-level source.
        :paramtype source: dict[str, Any] | None
        :keyword stale_timeout: Seconds before an in-progress task is considered
            stale and eligible for recovery. Default 300 (5 minutes).
        :paramtype stale_timeout: float
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
            source=source,
            stale_timeout=stale_timeout,
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

    async def _lifecycle_start(
        self,
        *,
        task_id: str,
        input: Input,  # noqa: A002
        session_id: str | None,
        title: str | None,
        tags: dict[str, str] | None,
        retry: RetryPolicy | None,
        source: dict[str, Any] | None,
        stale_timeout: float,
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
        :keyword source: Provenance metadata override.
        :paramtype source: dict[str, Any] | None
        :keyword stale_timeout: Stale timeout in seconds.
        :paramtype stale_timeout: float
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
        resolved_source = source or self._opts.source

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
                source=resolved_source,
                entry_mode="fresh",
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
            return await manager._start_existing_task(  # pylint: disable=protected-access
                fn=self._fn,
                fn_name=self.name,
                task_info=updated_info,
                entry_mode="resumed",
                input_val=input,
                input_type=self._input_type,
                opts=self._opts,
                retry=resolved_retry,
            )

        if existing.status == "in_progress":
            if _is_stale(existing.updated_at, stale_timeout):
                # Stale — recover
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
        source: dict[str, Any] | None = None,
        cancel_grace_seconds: float | None = None,
    ) -> DurableTask[Input, Output]:
        """Return a new DurableTask with merged options.

        The original is unchanged.

        :keyword timeout: Execution timeout override.
        :paramtype timeout: timedelta | None
        :keyword ephemeral: Whether to delete task on terminal exit.
        :paramtype ephemeral: bool | None
        :keyword cancel_grace_seconds: Grace period override.
        :paramtype cancel_grace_seconds: float | None
        :keyword tags: Tag overrides.
        :paramtype tags: dict[str, str] | Callable[[Any, str], dict[str, str]] | None
        :keyword store_input: Whether to persist input.
        :paramtype store_input: bool | None
        :keyword source: Provenance metadata override.
        :paramtype source: dict[str, Any] | None
        :keyword retry: Retry policy override.
        :paramtype retry: RetryPolicy | None
        :keyword title: Title override.
        :paramtype title: str | Callable[[Any, str], str] | None
        :keyword description: Description override.
        :paramtype description: str | Callable[[Any, str], str | None] | None
        :keyword lease_duration_seconds: Lease TTL override.
        :paramtype lease_duration_seconds: int | None
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
                resolved_tags = {**existing, **(tags or {})}
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
            source=source if source is not None else self._opts.source,
            cancel_grace_seconds=(
                cancel_grace_seconds
                if cancel_grace_seconds is not None
                else self._opts.cancel_grace_seconds
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
    source: dict[str, Any] | None = ...,
    cancel_grace_seconds: float = ...,
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
    source: dict[str, Any] | None = None,
    cancel_grace_seconds: float = 5.0,
) -> Any:
    """Turn an async function into a crash-resilient durable task.

    Can be used with or without arguments::

        @durable_task
        async def my_task(ctx: TaskContext[MyInput]) -> MyOutput: ...

        @durable_task(name="custom-name", ephemeral=False)
        async def my_task(ctx: TaskContext[MyInput]) -> MyOutput: ...

    :param fn: The async function to decorate (when used without parens).
    :type fn: Callable[..., Any] | None
    :keyword name: Task name for logging. Defaults to ``fn.__qualname__``.
    :keyword title: Human-readable title (string or callable).
    :keyword tags: Default tags (static dict or callable factory receiving
        ``(input, task_id)``). Merged with per-call ``tags=`` overrides.
    :keyword description: Task description (static string or callable factory
        receiving ``(input, task_id)``).
    :keyword timeout: Execution timeout. When elapsed, ``ctx.cancel`` is set,
        followed by hard cancellation after ``cancel_grace_seconds``.
    :keyword lease_duration_seconds: Lease TTL (default 60).
    :keyword store_input: Whether to persist input on the task record.
    :keyword ephemeral: Delete task on terminal exit (default True).
    :keyword retry: Default retry policy for this task.
    :keyword source: Default provenance metadata for this task.
    :keyword cancel_grace_seconds: Seconds to wait between cooperative cancel
        (``ctx.cancel``) and hard cancellation (``asyncio.Task.cancel()``).
        Default 5.0.
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

        input_type, output_type = _extract_generic_args(func)

        # Preserve callable tags as-is; only copy static dicts
        resolved_tags = tags if callable(tags) else (dict(tags) if tags else {})

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
            source=source,
            cancel_grace_seconds=cancel_grace_seconds,
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
