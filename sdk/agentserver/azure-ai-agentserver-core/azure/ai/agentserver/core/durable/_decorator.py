# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""``@task`` decorator — turns an async function into a crash-resilient
unit of work with automatic task lifecycle management.

Usage::

    from azure.ai.agentserver.core.durable import task, TaskContext

    @task
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

from ._client import TransportClassifiedError as _TransportClassifiedError
from ._context import TaskContext
from ._result import TaskResult
from ._retry import RetryPolicy
from ._run import TaskRun
from ._stream import StreamHandler, StreamHandlerFactory

if TYPE_CHECKING:
    from ._models import TaskStatus

Input = TypeVar("Input")
Output = TypeVar("Output")
F = TypeVar("F", bound=Callable[..., Any])

_VALID_TASK_ID_RE = re.compile(r"^[a-zA-Z0-9\-_.:]+$")
_MAX_TASK_ID_LENGTH = 256

#: Prefix for framework-reserved tags. Developer tags with this prefix are
#: silently stripped to prevent collisions with auto-stamped tags.
_RESERVED_TAG_PREFIX = "_task_"

_logger = _logging.getLogger("azure.ai.agentserver.durable")

# Global registry of durable task descriptors for recovery purposes.
# Populated at import time when @task decorates a function.
_REGISTERED_DESCRIPTORS: list[tuple[str, Callable[..., Any], "TaskOptions"]] = []


def _strip_reserved_tags(tags: dict[str, str]) -> dict[str, str]:
    """Remove framework-reserved tags from developer-provided tags.

    Tags prefixed with ``_task_`` are reserved for framework use.
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


def _in_progress_was_abandoned_legacy(task_updated_at: str, threshold: float) -> bool:
    """Transitional helper for the Phase-4 cohort of spec 016.

    Replaces the public ``_is_stale`` helper that was removed by FR-001
    (spec 016 US1 / T031). This intentionally non-stale-named function
    holds the in-process recovery decision until Phase 6 of spec 016
    lands the proper FR-002 / FR-004 lease-based reclaim path
    (``_lease_is_dead`` + ``_reclaim_one``) that supersedes this entire
    code path.

    The function MUST NOT be imported from outside ``_decorator.py`` —
    it is a transitional implementation detail with a planned
    deprecation in the same PR (Phase 6 of spec 016).

    :param task_updated_at: ISO 8601 timestamp of the task's last update.
    :type task_updated_at: str
    :param threshold: Internal threshold seconds (currently fixed; see
        ``_LEGACY_INPROCESS_STALE_THRESHOLD_SECONDS``).
    :type threshold: float
    :returns: True if the framework should treat the in-progress record
        as abandoned by a previous lifetime and recover it.
    :rtype: bool
    """
    if not task_updated_at:
        return False
    from datetime import datetime, timezone  # pylint: disable=import-outside-toplevel

    updated = datetime.fromisoformat(task_updated_at)
    now = datetime.now(timezone.utc)
    if updated.tzinfo is None:
        updated = updated.replace(tzinfo=timezone.utc)
    return (now - updated).total_seconds() > threshold


# Spec 016 transitional internal constant (FR-001).
#
# Replaces the per-task ``stale_timeout`` developer-facing knob that
# was removed in Phase 4 of spec 016 (US1, T028-T032). Tests that
# previously passed ``stale_timeout=0.1`` to deterministically trigger
# the recovered code path now monkeypatch this module-level constant
# instead. Phase 6 of spec 016 (US3, T053-T058) replaces both this
# constant AND the entire ``_in_progress_was_abandoned_legacy`` code
# path with the proper FR-002 / FR-004 framework-managed reclaim
# (``_reclaim_one`` + ``_lease_is_dead``) — at which point this
# constant becomes dead code and is removed.
_LEGACY_INPROCESS_STALE_THRESHOLD_SECONDS: float = 300.0


# Spec 015 Phase 5 (FR-004) — framework-reserved payload slot for the
# input-precondition primitive. Storage layout: top-level
# ``payload["_last_input_id"]: str`` (the ``_`` prefix is the framework-
# reserved convention; flat layout replaces the prior nested
# ``payload["_last_input_id"]`` namespace).
# Callers do not read or write this slot directly — it is managed by the
# framework on behalf of the ``input_id`` / ``if_last_input_id`` kwargs on
# :meth:`Task.start`.
_LAST_INPUT_ID_PAYLOAD_KEY = "_last_input_id"

# Spec 015 Phase 3 (FR-006) — these were previously developer-visible
# @task kwargs (lease_duration_seconds, max_pending) but had no real
# end-user knob value. Demoted to module-level internal constants. If a
# future need arises to tune them per-task, re-introduce a Sec-Privileged
# API rather than restoring the public surface.
_DEFAULT_LEASE_SECONDS = 60
_DEFAULT_MAX_PENDING_STEERING = 10


def _read_stored_last_input_id(task_info: Any) -> str | None:
    """Read the stored ``last_input_id`` from a task's payload, or ``None``.

    :param task_info: The persisted task record (or ``None`` for a fresh
        task that does not exist yet).
    :type task_info: TaskInfo | None
    :returns: The stored value, or ``None`` if no chain has been recorded.
    :rtype: str | None
    """
    if task_info is None or not task_info.payload:
        return None
    value = task_info.payload.get(_LAST_INPUT_ID_PAYLOAD_KEY)
    return value if isinstance(value, str) else None


def _check_input_precondition(
    *,
    existing: Any,
    task_id: str,
    input_id: str | None,
    if_last_input_id: str | None,
) -> None:
    """Validate the ``if_last_input_id`` precondition before any accept path.

    Spec 013 US2 semantic rules:

    - Both ``input_id`` and ``if_last_input_id`` ``None``: no precondition.
    - ``input_id`` set, ``if_last_input_id`` ``None``: caller asserts a fresh
      chain. Succeeds iff no stored ``last_input_id`` exists.
    - ``if_last_input_id`` set, stored ``last_input_id`` ``None``: the chain
      task is brand new (e.g., a steerable conversation's second turn lands
      on a freshly-created chain task). The precondition is vacuously
      satisfied — the framework cannot locally verify the predecessor's
      identity, but ``TaskConflictError`` on the create path protects
      against double-create races. We accept and seed.
    - Both set with stored: stored ``last_input_id`` must equal
      ``if_last_input_id``.

    :keyword existing: The persisted task record (or ``None`` for fresh).
    :keyword task_id: The task identifier.
    :keyword input_id: The new input's identity (caller-supplied).
    :keyword if_last_input_id: The precondition value (caller-supplied).
    :raises LastInputIdPreconditionFailed: If the precondition does not hold.
    """
    if input_id is None and if_last_input_id is None:
        return
    from ._exceptions import (  # pylint: disable=import-outside-toplevel
        LastInputIdPreconditionFailed,
    )

    stored = _read_stored_last_input_id(existing)
    if if_last_input_id is None:
        # Caller asserts fresh chain. Must not already exist.
        if stored is not None:
            raise LastInputIdPreconditionFailed(
                task_id,
                expected_last_input_id=None,
                actual_last_input_id=stored,
            )
        return
    # if_last_input_id is set.
    if stored is None:
        # No prior chain recorded. The chain task is brand new — accept
        # and let the seed write happen on the accept path.
        return
    # Both stored and if_last_input_id set — must match.
    if stored != if_last_input_id:
        raise LastInputIdPreconditionFailed(
            task_id,
            expected_last_input_id=if_last_input_id,
            actual_last_input_id=stored,
        )


def _build_framework_extras(input_id: str | None) -> dict[str, Any] | None:
    """Build the top-level ``payload["_last_input_id"]`` seed dict, or ``None``.

    Used at fresh-create and at suspended-resume to advance the stored
    ``last_input_id`` atomically with the input persist.

    :param input_id: The new input's identity, or ``None`` for callers not
        opting in to chain semantics.
    :type input_id: str | None
    :returns: ``{"_last_input_id": input_id}`` if ``input_id`` is set,
        else ``None``.
    :rtype: dict[str, Any] | None
    """
    if input_id is None:
        return None
    return {_LAST_INPUT_ID_PAYLOAD_KEY: input_id}


class TaskOptions:  # pylint: disable=too-many-instance-attributes
    """Internal task options bag.

    *Internal*: not part of the public ``durable`` surface as of Spec 015 Phase 3.
    Constructed by the ``@task`` decorator (and ``Task.options()``) from a small
    public kwarg set: ``name``, ``title``, ``tags``, ``timeout``, ``ephemeral``,
    ``retry``, ``steerable``, ``stream_handler_factory``.

    :param name: **Stable identity anchor.** Used for recovery routing and
        source stamping.  If you rename the Python function later, existing
        in-flight tasks are still recovered correctly because the framework
        matches on this name.
    :type name: str
    :param title: Human-readable title template.
    :type title: str | Callable[[Any, str], str] | None
    :param tags: Default tags (static dict or callable factory).
    :type tags: dict[str, str] | Callable[[Any, str], dict[str, str]]
    :param timeout: Execution timeout.
    :type timeout: timedelta | None
    :param ephemeral: Whether to delete on terminal exit.
    :type ephemeral: bool
    :param stream_handler_factory: Optional factory callable that receives a
        ``task_id`` and returns a :class:`StreamHandler`.  When set, crash-
        recovery and resume paths use this factory instead of defaulting to
        :class:`QueueStreamHandler`.
    :type stream_handler_factory: Callable[[str], StreamHandler] | None
    """

    __slots__ = (
        "name",
        "title",
        "tags",
        "timeout",
        "ephemeral",
        "retry",
        "steerable",
        "stream_handler_factory",
    )

    def __init__(
        self,
        name: str,
        title: str | Callable[[Any, str], str] | None = None,
        tags: dict[str, str] | Callable[[Any, str], dict[str, str]] | None = None,
        timeout: timedelta | None = None,
        ephemeral: bool = True,
        retry: RetryPolicy | None = None,
        steerable: bool = False,
        stream_handler_factory: StreamHandlerFactory | None = None,
    ) -> None:
        self.name = name
        self.title = title
        self.tags = tags if tags is not None else {}
        self.timeout = timeout
        self.ephemeral = ephemeral
        self.retry = retry
        self.steerable = steerable
        self.stream_handler_factory = stream_handler_factory

    def __repr__(self) -> str:
        return (
            f"TaskOptions(name={self.name!r}, "
            f"ephemeral={self.ephemeral}, retry={self.retry!r}, "
            f"timeout={self.timeout!r}, steerable={self.steerable})"
        )


class Task(Generic[Input, Output]):
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
        opts: TaskOptions,
        input_type: type[Input],
        output_type: type[Output],
    ) -> None:
        self._fn = fn
        self._opts = opts
        self._input_type = input_type
        self._output_type = output_type
        self.name = opts.name
        # Register for recovery — manager picks these up at startup
        _REGISTERED_DESCRIPTORS.append((opts.name, fn, opts))

    def _resolve_title(self, input_val: Input, task_id: str) -> str:
        if callable(self._opts.title):
            return self._opts.title(input_val, task_id)
        if isinstance(self._opts.title, str):
            return self._opts.title
        return f"{self.name}:{task_id[:8]}"

    def _resolve_tags(self, input_val: Input, task_id: str) -> dict[str, str]:
        """Resolve decorator-level tags (static dict or callable factory).

        Reserved tags (prefixed with ``_task_``) are stripped to
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
        input_id: str | None = None,
        if_last_input_id: str | None = None,
    ) -> TaskResult[Output]:
        """Run a lifecycle-aware durable task and return the result.

        Automatically starts, resumes, or recovers the task based on its
        current state:

        - No task / pending → create and start (``entry_mode="fresh"``)
        - Suspended → resume with new input (``entry_mode="resumed"``)
        - In-progress (stale) → recover (``entry_mode="recovered"``)
        - In-progress (not stale) → raise :class:`TaskConflictError`
        - Completed → raise :class:`TaskConflictError`

        .. note::

            ``title``, ``tags``, ``retry``, and ``stream_handler`` are
            configured on the ``@task(...)``
            decorator (or via :meth:`Task.options`), not per-call. This
            is enforced so the values survive crash recovery: after the
            container crashes and the framework re-enters the task, it
            has only the registered decorator's options to work with — a
            per-call override would silently disappear at the crash
            boundary. Session identity is platform-derived from the
            ``FOUNDRY_AGENT_SESSION_ID`` environment variable.

        :keyword task_id: Unique task identifier.
        :paramtype task_id: str
        :keyword input: Typed input value.
        :paramtype input: Input
        :keyword input_id: Optional identifier for the input being accepted. When
            supplied, the framework records it as the task's most-recently-accepted
            input id in a framework-reserved slot (``payload["_last_input_id"]``).
            Used together with ``if_last_input_id`` to implement HTTP If-Match-style
            optimistic concurrency on the input queue.
        :paramtype input_id: str | None
        :keyword if_last_input_id: Optional precondition. When supplied, the framework
            verifies that the task's currently-stored last input id equals this value
            before accepting the new input. If the precondition does not hold (a
            concurrent caller advanced the queue, or the caller's view is stale),
            raises :class:`LastInputIdPreconditionFailed` before any state mutation.
            Modelled on HTTP ``If-Match: <etag>`` semantics. Requires ``input_id``
            to also be supplied (raises :class:`TypeError` otherwise — invalid
            combination).
        :paramtype if_last_input_id: str | None
        :return: The task result wrapper with output, status, and suspension info.
        :rtype: ~azure.ai.agentserver.core.durable.TaskResult[Output]
        :raises TaskFailed: On unhandled exception.
        :raises ~azure.ai.agentserver.core.durable.TaskConflictError: If the
            task is already in-progress or completed.
        :raises ~azure.ai.agentserver.core.durable.LastInputIdPreconditionFailed: If
            the ``if_last_input_id`` precondition does not match the stored
            last input id.
        :raises TypeError: If ``if_last_input_id`` is supplied without ``input_id``.
        """
        _validate_task_id(task_id)
        if if_last_input_id is not None and input_id is None:
            raise TypeError(
                "if_last_input_id requires input_id (a precondition without an "
                "advancing id is not meaningful)"
            )
        handle = await self._lifecycle_start(
            task_id=task_id,
            input=input,
            input_id=input_id,
            if_last_input_id=if_last_input_id,
        )
        return await handle.result()

    async def start(
        self,
        *,
        task_id: str,
        input: Input,  # noqa: A002
        input_id: str | None = None,
        if_last_input_id: str | None = None,
    ) -> TaskRun[Output]:
        """Start a lifecycle-aware durable task and return a handle.

        Follows the same lifecycle rules as :meth:`run` but returns
        immediately with a :class:`TaskRun` handle instead of blocking.

        .. note::

            ``title``, ``tags``, ``retry``, and ``stream_handler`` are
            configured on the ``@task(...)``
            decorator (or via :meth:`Task.options`), not per-call —
            see :meth:`run` for the rationale. Session identity is
            platform-derived from the ``FOUNDRY_AGENT_SESSION_ID``
            environment variable.

        :keyword task_id: Unique task identifier.
        :paramtype task_id: str
        :keyword input: Typed input value.
        :paramtype input: Input
        :keyword input_id: Optional identifier for the input being accepted. When
            supplied, the framework records it as the task's most-recently-accepted
            input id in a framework-reserved slot (``payload["_last_input_id"]``).
            Used together with ``if_last_input_id`` to implement HTTP If-Match-style
            optimistic concurrency on the input queue.
        :paramtype input_id: str | None
        :keyword if_last_input_id: Optional precondition. When supplied, the framework
            verifies that the task's currently-stored last input id equals this value
            before accepting the new input. If the precondition does not hold (a
            concurrent caller advanced the queue, or the caller's view is stale),
            raises :class:`LastInputIdPreconditionFailed` before any state mutation.
            Modelled on HTTP ``If-Match: <etag>`` semantics. Requires ``input_id``
            to also be supplied (raises :class:`TypeError` otherwise — invalid
            combination).
        :paramtype if_last_input_id: str | None
        :return: A handle to the running task.
        :rtype: TaskRun[Output]
        :raises ~azure.ai.agentserver.core.durable.TaskConflictError: If the
            task is already in-progress or completed.
        :raises ~azure.ai.agentserver.core.durable.LastInputIdPreconditionFailed: If
            the ``if_last_input_id`` precondition does not match the stored
            last input id.
        :raises TypeError: If ``if_last_input_id`` is supplied without ``input_id``.
        """
        _validate_task_id(task_id)
        if if_last_input_id is not None and input_id is None:
            raise TypeError(
                "if_last_input_id requires input_id (a precondition without an "
                "advancing id is not meaningful)"
            )
        return await self._lifecycle_start(
            task_id=task_id,
            input=input,
            input_id=input_id,
            if_last_input_id=if_last_input_id,
        )

    async def _get(self, task_id: str) -> Any:
        """Return the full persisted task information (internal).

        .. note::
            *Internal* as of Spec 015 Phase 3 — public consumers should use
            ``manager.provider.get(task_id)`` directly.

        Works for any task state — running, suspended, completed, etc.
        Returns whatever is persisted. Returns ``None`` if no task exists.

        :param task_id: The task identifier.
        :type task_id: str
        :return: Task info or ``None`` if no task exists.
        :rtype: TaskInfo | None
        """
        from ._manager import (  # pylint: disable=import-outside-toplevel
            get_task_manager,
        )

        manager = get_task_manager()
        return await manager.provider.get(task_id)

    async def get_active_run(self, task_id: str) -> TaskRun[Output] | None:
        """Return a TaskRun handle for an active (in-progress) task.

        Spec 016 FR-005 (US3 / US4): consults the store, not only
        in-memory state. If the record is in-progress with a dead
        lease, performs inline reclaim as a hidden side effect and
        returns a usable :class:`TaskRun` bound to the new lifetime.
        Terminal records return ``None``. Eviction returns ``None``.

        Enables late-join consumers to iterate a running task's stream
        without being the original caller of ``start()``/``run()``,
        AND covers the orphan-resurrection case where the previous
        lifetime crashed without notice.

        :param task_id: The task identifier.
        :type task_id: str
        :return: A TaskRun bound to the active task's stream handler,
            or ``None`` if not active / terminal / evicted.
        :rtype: TaskRun[Output] | None

        Example::

            # In another coroutine or request handler:
            run = await my_task.get_active_run("task-123")
            if run is not None:
                async for chunk in run:
                    print(chunk, end="")
        """
        from ._manager import (  # pylint: disable=import-outside-toplevel
            get_task_manager,
        )

        manager = get_task_manager()
        return await manager.get_active_run(task_id)

    async def _list(
        self,
        *,
        session_id: str | None = None,
        status: TaskStatus | None = None,
    ) -> list[Any]:
        """List tasks created by this durable task function (internal).

        .. note::
            *Internal* as of Spec 015 Phase 3 — public consumers should use
            ``manager.list_tasks(fn_name=...)`` directly.

        Automatically scoped to this function's ``name`` via the
        ``_task_name`` tag (server-side) and ``source.type``
        (client-side). Only returns tasks created by this framework.

        :keyword session_id: Session scope override.  Defaults to the
            manager's configured session ID.
        :paramtype session_id: str | None
        :keyword status: Filter by task status (e.g., ``"in_progress"``,
            ``"suspended"``, ``"completed"``).
        :paramtype status: TaskStatus | None
        :return: Matching task records.
        :rtype: list[TaskInfo]
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
        input_id: str | None = None,
        if_last_input_id: str | None = None,
    ) -> None:
        """Append a steering input to the task's pending queue.

        :param manager: The task manager instance.
        :type manager: Any
        :keyword task_id: Target task identifier.
        :paramtype task_id: str
        :keyword input_val: The new steering input value.
        :paramtype input_val: Any
        :keyword existing: The previously-fetched task record (used for the
            first etag attempt; later attempts re-fetch internally).
        :paramtype existing: Any
        :keyword input_id: (Spec 013 US2) When set, the new input's identity.
            Used to advance ``payload["_last_input_id"]``
            atomically with the queue append.
        :paramtype input_id: str | None
        :keyword if_last_input_id: (Spec 013 US2) When set, the precondition
            value re-checked on each etag-conflict retry.
        :paramtype if_last_input_id: str | None
        """
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

            # (Spec 013 US2) Re-check the input precondition on each retry to
            # catch a concurrent steer that may have advanced `last_input_id`
            # since we last looked.
            if _attempt > 0:
                _check_input_precondition(
                    existing=task_info,
                    task_id=task_id,
                    input_id=input_id,
                    if_last_input_id=if_last_input_id,
                )

            payload = dict(task_info.payload) if task_info.payload else {}
            steering = dict(payload.get("_steering", {}))
            pending: list[Any] = list(steering.get("pending_inputs", []))

            if len(pending) >= _DEFAULT_MAX_PENDING_STEERING:
                raise SteeringQueueFull(task_id, _DEFAULT_MAX_PENDING_STEERING)

            pending.append(serialized)
            steering["pending_inputs"] = pending
            steering["cancel_requested"] = True
            if "generation" not in steering:
                steering["generation"] = 0
            payload["_steering"] = steering

            # (Spec 013 US2 / Spec 015 FR-004) When the caller opted in via
            # input_id, advance the framework-managed last_input_id slot
            # atomically with the queue append. The slot is a top-level
            # `_`-prefixed payload key (Spec 015: flat layout).
            if input_id is not None:
                payload[_LAST_INPUT_ID_PAYLOAD_KEY] = input_id

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

    async def _lifecycle_start(  # pylint: disable=too-many-locals
        self,
        *,
        task_id: str,
        input: Input,  # noqa: A002
        input_id: str | None = None,
        if_last_input_id: str | None = None,
    ) -> TaskRun[Output]:
        """Resolve lifecycle state and start/resume/recover accordingly.

        Title, tags, retry, stream handler, and stale timeout are all sourced
        from ``self._opts`` (the decorator-time configuration). This is
        deliberate: those settings must survive the crash boundary, and the
        framework can only rely on the registered decorator's view of the task
        on recovery.

        :keyword task_id: The task identifier.
        :paramtype task_id: str
        :keyword input: Typed input value.
        :paramtype input: Input
        :keyword input_id: (Spec 013 US2) When set, the new input's identity
            recorded in the framework-reserved
            ``payload["_last_input_id"]`` slot.
        :paramtype input_id: str | None
        :keyword if_last_input_id: (Spec 013 US2) Precondition value checked
            against the stored ``last_input_id`` before any accept path.
        :paramtype if_last_input_id: str | None
        :return: A handle to the running task.
        :rtype: TaskRun[Output]
        """
        from ._exceptions import (  # pylint: disable=import-outside-toplevel
            TaskConflictError,
        )
        from ._manager import (  # pylint: disable=import-outside-toplevel
            get_task_manager,
        )

        # Spec 016 FR-008 (US2): orphan-sandbox eviction at scheduling
        # entry points MUST surface as TaskConflictError(current_status=
        # "in_progress") — the same shape as the live-elsewhere case
        # per Invariant 1. Operator-facing WARNING logs (in _manager.py
        # and _lease.py) are the only differentiator.
        try:
            return await self._lifecycle_start_inner(
                task_id=task_id,
                input=input,
                input_id=input_id,
                if_last_input_id=if_last_input_id,
            )
        except _TransportClassifiedError as exc:
            if getattr(exc, "classification", None) == "evicted":
                # Pre-import only at the eviction site to avoid a cycle.
                raise TaskConflictError(task_id, "in_progress") from exc
            raise

    async def _lifecycle_start_inner(  # pylint: disable=too-many-locals
        self,
        *,
        task_id: str,
        input: Input,  # noqa: A002
        input_id: str | None = None,
        if_last_input_id: str | None = None,
    ) -> TaskRun[Output]:
        """Inner body of :meth:`_lifecycle_start`. See that method for docs.

        Split out so the outer wrapper can convert spec 016 FR-008 evictions
        to ``TaskConflictError`` without indenting the entire body.
        """
        from ._exceptions import (  # pylint: disable=import-outside-toplevel
            TaskConflictError,
        )
        from ._manager import (  # pylint: disable=import-outside-toplevel
            get_task_manager,
        )

        manager = get_task_manager()
        existing = await manager.provider.get(task_id)

        resolved_retry = self._opts.retry

        # (Spec 013 US2) Pre-acceptance check: if the caller supplied an
        # ``if_last_input_id`` precondition, verify the stored last input id
        # matches before proceeding to any accept path. The actual advance
        # (storing ``input_id`` into ``payload["_last_input_id"]``) is bundled
        # into the create/append/resume code paths below so it lands atomically
        # with the input persist.
        _check_input_precondition(
            existing=existing,
            task_id=task_id,
            input_id=input_id,
            if_last_input_id=if_last_input_id,
        )

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
                    stream_handler=None,
                )
            # No task exists — create new
            return await manager.create_and_start(
                fn=self._fn,
                fn_name=self.name,
                task_id=task_id,
                input_val=input,
                input_type=self._input_type,
                session_id=None,
                title=self._resolve_title(input, task_id),
                tags=self._merge_tags(input, task_id, None),
                opts=self._opts,
                retry=resolved_retry,
                entry_mode="fresh",
                stream_handler=None,
                initial_payload_extras=_build_framework_extras(input_id),
            )

        if existing.status == "suspended":
            # Resume — patch input onto task, then start.
            # (Spec 013 US4) Etag-protected retry loop so concurrent
            # suspended-resume POSTs race safely instead of silently
            # overwriting each other.
            # (Spec 013 US2) On the same atomic patch, advance the
            # framework's `payload["_last_input_id"]` slot when the caller
            # opted in via `input_id`. The precondition check already ran
            # at the top of `_lifecycle_start` against the read existing.
            serialized = _serialize_input(input)
            from ._models import (  # pylint: disable=import-outside-toplevel
                TaskPatchRequest,
            )

            max_resume_retries = 5
            current_info = existing
            for _attempt in range(max_resume_retries):
                etag = getattr(current_info, "etag", None) or None
                # Build the resume patch: input + (optionally) advance the
                # framework-managed last_input_id slot (Spec 015 flat layout).
                resume_payload: dict[str, Any] = {"input": serialized}
                if input_id is not None:
                    resume_payload[_LAST_INPUT_ID_PAYLOAD_KEY] = input_id
                try:
                    await manager.provider.update(
                        task_id,
                        TaskPatchRequest(payload=resume_payload, if_match=etag),
                    )
                    break
                except ValueError as exc:
                    # Etag conflict — re-fetch, re-check precondition, retry.
                    refreshed = await manager.provider.get(task_id)
                    if refreshed is None:
                        raise RuntimeError(
                            f"Task {task_id!r} disappeared during suspended-resume retry"
                        ) from exc
                    # Re-check the precondition against the now-refreshed view.
                    # On a precondition failure here, the exception propagates
                    # out (validation failure, not concurrency conflict).
                    _check_input_precondition(
                        existing=refreshed,
                        task_id=task_id,
                        input_id=input_id,
                        if_last_input_id=if_last_input_id,
                    )
                    current_info = refreshed
            else:
                raise RuntimeError(
                    f"Failed to apply suspended-resume input patch after "
                    f"{max_resume_retries} retries (task {task_id!r})"
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
                    stream_handler=None,
                )
            )

        if existing.status == "in_progress":
            if _in_progress_was_abandoned_legacy(
                existing.updated_at, _LEGACY_INPROCESS_STALE_THRESHOLD_SECONDS
            ):
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
                            stream_handler=None,
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
                    stream_handler=None,
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
                    input_id=input_id,
                    if_last_input_id=if_last_input_id,
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
        timeout: timedelta | None = None,
        ephemeral: bool | None = None,
        retry: RetryPolicy | None = None,
        steerable: bool | None = None,
    ) -> Task[Input, Output]:
        """Return a new Task with merged options.

        The original is unchanged.

        :keyword title: Title override.
        :paramtype title: str | Callable[[Any, str], str] | None
        :keyword tags: Tag overrides.
        :paramtype tags: dict[str, str] | Callable[[Any, str], dict[str, str]] | None
        :keyword timeout: Execution timeout override.
        :paramtype timeout: timedelta | None
        :keyword ephemeral: Whether to delete task on terminal exit.
        :paramtype ephemeral: bool | None
        :keyword retry: Retry policy override.
        :paramtype retry: RetryPolicy | None
        :keyword steerable: Whether this task accepts steering inputs.
        :paramtype steerable: bool | None
        :return: A new Task with overridden options.
        :rtype: Task[Input, Output]
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

        new_opts = TaskOptions(
            name=self._opts.name,
            title=title if title is not None else self._opts.title,
            tags=resolved_tags,
            timeout=timeout if timeout is not None else self._opts.timeout,
            ephemeral=(ephemeral if ephemeral is not None else self._opts.ephemeral),
            retry=retry if retry is not None else self._opts.retry,
            steerable=(steerable if steerable is not None else self._opts.steerable),
            stream_handler_factory=self._opts.stream_handler_factory,
        )
        return Task(
            fn=self._fn,
            opts=new_opts,
            input_type=self._input_type,
            output_type=self._output_type,
        )


@overload
def task(
    fn: Callable[[TaskContext[Input]], Awaitable[Output]],
) -> Task[Input, Output]: ...


@overload
def task(
    *,
    name: str | None = ...,
    title: str | Callable[[Any, str], str] | None = ...,
    tags: dict[str, str] | Callable[[Any, str], dict[str, str]] | None = ...,
    timeout: timedelta | None = ...,
    ephemeral: bool = ...,
    retry: RetryPolicy | None = ...,
    steerable: bool = ...,
    stream_handler_factory: StreamHandlerFactory | None = ...,
) -> Callable[
    [Callable[[TaskContext[Input]], Awaitable[Output]]],
    Task[Input, Output],
]: ...


def task(
    fn: Callable[..., Any] | None = None,
    *,
    name: str | None = None,
    title: str | Callable[[Any, str], str] | None = None,
    tags: dict[str, str] | Callable[[Any, str], dict[str, str]] | None = None,
    timeout: timedelta | None = None,
    ephemeral: bool = True,
    retry: RetryPolicy | None = None,
    steerable: bool = False,
    stream_handler_factory: StreamHandlerFactory | None = None,
) -> Any:
    """Turn an async function into a crash-resilient durable task.

    Can be used with or without arguments::

        @task
        async def my_task(ctx: TaskContext[MyInput]) -> MyOutput: ...

        @task(name="custom-name", ephemeral=False)
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
        ``(input, task_id)``).
    :keyword timeout: Per-turn, wall-clock, durable, cooperative-only
        execution budget. When the budget elapses for the current turn,
        ``ctx.timeout_exceeded`` is set then ``ctx.cancel`` is set; the
        handler decides whether to wind down. The watchdog does NOT
        force-stop the handler. See the developer guide §4 Timeout for
        the full mechanic (including the crash-mid-turn budget-preserving
        recovery semantics).
    :keyword ephemeral: Delete task on terminal exit (default True).
    :keyword retry: Default retry policy for this task. Recovery-safe: applied
        by the framework on every entry, including crash recovery.
    :keyword steerable: Whether this task accepts steering inputs. When True,
        calling ``start()`` on an ``in_progress`` task queues the input and
        signals cancel instead of raising ``TaskConflictError``. Default False.
    :keyword stream_handler_factory: Optional factory callable that receives a
        ``task_id`` and returns a :class:`StreamHandler`. When set, fresh
        starts, resumes, and crash-recovery all use this factory instead of
        defaulting to :class:`QueueStreamHandler`. The factory itself is the
        only supported configuration surface — there is no per-call override,
        so the handler stays consistent across the crash boundary.
    :return: A ``Task[Input, Output]`` wrapper.
    :rtype: Any
    """

    def _wrap(
        func: Callable[..., Any],
    ) -> Task[Any, Any]:
        if not asyncio.iscoroutinefunction(func):
            raise TypeError(
                f"@task requires an async function, "
                f"got {func.__qualname__!r}"
            )

        input_type, output_type = _extract_generic_args(func)

        # Preserve callable tags as-is (stripped at resolve time); strip static dicts now
        resolved_tags = (
            tags if callable(tags) else _strip_reserved_tags(dict(tags) if tags else {})
        )

        opts = TaskOptions(
            name=name or func.__qualname__,
            title=title,
            tags=resolved_tags,
            timeout=timeout,
            ephemeral=ephemeral,
            retry=retry,
            steerable=steerable,
            stream_handler_factory=stream_handler_factory,
        )

        result = Task(
            fn=func,
            opts=opts,
            input_type=input_type,
            output_type=output_type,
        )
        return result

    if fn is not None:
        return _wrap(fn)
    return _wrap
