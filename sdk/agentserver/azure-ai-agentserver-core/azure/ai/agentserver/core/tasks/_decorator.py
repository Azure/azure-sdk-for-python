# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""``@task`` decorator — turns an async function into a crash-resilient
unit of work with automatic task lifecycle management.

Usage::

    from azure.ai.agentserver.core.tasks import task, TaskContext

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
from ._exceptions_internal import _HostedConflict, _translate_hosted_conflict
from ._retry import RetryPolicy
from ._run import TaskRun

if TYPE_CHECKING:
    from ._models import TaskStatus

Input = TypeVar("Input")
Output = TypeVar("Output")
F = TypeVar("F", bound=Callable[..., Any])

_VALID_TASK_ID_RE = re.compile(r"^[a-zA-Z0-9\-_.:]+$")
_MAX_TASK_ID_LENGTH = 256

#: Spec 037 #8 — per-turn execution timeout: default to 1 day when unset and
# treat 1 day as a HARD ceiling. A developer-supplied timeout may lower the
# budget, but a larger (or negative) value is rejected at registration
# (fail-fast, not clamped). This is a PER-TURN cap, not a task-lifetime bound:
# a multi-turn chain can live indefinitely (the timeout resets every turn); the
# task's overall lifetime is governed by the platform's 30-day sliding TTL.
# Mirrors the .NET port's ``TaskEngineConstants.ResolveTaskTimeout``.
_DEFAULT_TASK_TIMEOUT = timedelta(days=1)
_MAX_TASK_TIMEOUT = timedelta(days=1)


def _validate_task_name(name: str | None) -> None:
    """Spec 037 #7 — ``name`` is a required, explicit, stable identity anchor.

    The task ``name`` is the durable recovery / identity anchor — it must survive
    process restarts and source refactors so in-flight tasks are re-routed to the
    right handler. Deriving it from ``func.__qualname__`` silently rebinds identity
    whenever the developer renames or moves the function, orphaning in-flight
    tasks on the next deploy. It is therefore required and must be non-empty after
    trimming.

    :param name: The task name supplied to ``@task`` / ``@multi_turn_task``.
    :type name: str | None
    :raises ValueError: When ``name`` is missing or whitespace-only.
    """
    if name is None or not name.strip():
        raise ValueError(
            "@task / @multi_turn_task requires an explicit non-empty `name=` "
            "(the stable recovery/identity anchor). Deriving it from the function "
            "name would silently rebind task identity on rename/move."
        )
    if len(name) > _MAX_TASK_ID_LENGTH:
        raise ValueError(f"task name must be {_MAX_TASK_ID_LENGTH} characters or fewer, got {len(name)}")


def _validate_timeout(timeout: timedelta | None) -> None:
    """Spec 037 #8 — reject a per-turn timeout that is negative or exceeds the
    1-day hard ceiling (fail-fast at registration, not clamped).

    :param timeout: The developer-supplied per-turn timeout, or ``None``.
    :type timeout: ~datetime.timedelta | None
    :raises ValueError: When ``timeout`` is negative or greater than 1 day.
    """
    if timeout is None:
        return
    if timeout.total_seconds() < 0:
        raise ValueError(f"timeout must be >= 0, got {timeout}")
    if timeout > _MAX_TASK_TIMEOUT:
        raise ValueError(f"timeout must be <= 1 day (the per-turn hard ceiling), got {timeout}")


def _resolve_effective_timeout(timeout: timedelta | None) -> timedelta:
    """Resolve the effective per-turn timeout budget (Spec 037 #8).

    An unset timeout defaults to 1 day; a supplied value is used as-is (already
    validated at registration by :func:`_validate_timeout`).

    :param timeout: The task's configured per-turn timeout, or ``None``.
    :type timeout: ~datetime.timedelta | None
    :return: The effective per-turn timeout budget.
    :rtype: ~datetime.timedelta
    """
    return timeout if timeout is not None else _DEFAULT_TASK_TIMEOUT


def _validate_input_id(input_id: str) -> None:
    """Spec 037 #12 — validate a caller-supplied ``input_id`` against the same
    charset/length pattern as ``task_id``.

    :param input_id: The caller-supplied input id.
    :type input_id: str
    :raises ValueError: When ``input_id`` is empty, too long, or contains
        characters outside the task-id charset.
    """
    if not input_id or len(input_id) > _MAX_TASK_ID_LENGTH:
        raise ValueError(f"input_id must be 1-{_MAX_TASK_ID_LENGTH} characters, got {len(input_id)}")
    if not _VALID_TASK_ID_RE.match(input_id):
        raise ValueError(f"input_id contains invalid characters: {input_id!r}. Allowed: [a-zA-Z0-9\\-_.:]")


#: Framework-reserved tag keys. Developer tags using these exact keys are
#: silently stripped to prevent collisions with auto-stamped tags. (Spec 038:
#: exact-key set replacing the former ``_task_`` prefix, since the reserved tag
#: is now the un-prefixed ``task_name``.)
_RESERVED_TAG_KEYS = frozenset({"task_name"})

_logger = _logging.getLogger("azure.ai.agentserver.tasks")

# Global registry of resilient task descriptors for recovery purposes.
# Populated at import time when @task decorates a function.
_REGISTERED_DESCRIPTORS: list[tuple[str, Callable[..., Any], "TaskOptions"]] = []


def _strip_reserved_tags(tags: dict[str, str]) -> dict[str, str]:
    """Remove framework-reserved tags from developer-provided tags.

    The exact keys in :data:`_RESERVED_TAG_KEYS` (e.g. ``task_name``) are
    reserved for framework use. If a developer provides them, they are silently
    dropped with a warning.

    :param tags: Developer-provided tags.
    :type tags: dict[str, str]
    :return: Tags with reserved keys removed.
    :rtype: dict[str, str]
    """
    reserved = [k for k in tags if k in _RESERVED_TAG_KEYS]
    if reserved:
        _logger.warning(
            "Ignoring reserved tag(s) %s — these keys are framework-owned and cannot be overridden",
            reserved,
        )
        return {k: v for k, v in tags.items() if k not in _RESERVED_TAG_KEYS}
    return tags


def _validate_task_id(task_id: str) -> None:
    if not task_id or len(task_id) > _MAX_TASK_ID_LENGTH:
        raise ValueError(f"task_id must be 1-{_MAX_TASK_ID_LENGTH} characters, " f"got {len(task_id)}")
    if not _VALID_TASK_ID_RE.match(task_id):
        raise ValueError(f"task_id contains invalid characters: {task_id!r}. " f"Allowed: [a-zA-Z0-9\\-_.:] ")


def _extract_generic_args(
    fn: Callable[..., Any],
) -> tuple[type[Any], type[Any]]:
    """Extract Input and Output types from a resilient task function signature.

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
        raise TypeError(f"Resilient task function {fn.__qualname__!r} must accept a " f"TaskContext[Input] parameter")

    ctx_hint = hints[ctx_param.name]
    args = get_args(ctx_hint)
    input_type: type[Any] = args[0] if args else Any  # type: ignore[assignment]

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
    if isinstance(value, dict) and callable(input_type) and input_type not in (dict, str, int, float, bool, list):
        try:
            return input_type(**value)
        except TypeError:
            pass
    return value


#   — framework-reserved payload slot for the
# input-precondition primitive. Storage layout: top-level
# ``payload["last_input_id"]: str`` (the ``_`` prefix is the framework-
# reserved convention; flat layout replaces the prior nested
# ``payload["last_input_id"]`` namespace).
# Callers do not read or write this slot directly — it is managed by the
# framework on behalf of the ``input_id`` / ``if_last_input_id`` kwargs on
# :meth:`Task.start`.
_LAST_INPUT_ID_PAYLOAD_KEY = "last_input_id"

#   — these were previously developer-visible
# @task kwargs (lease_duration_seconds, max_pending) but had no real
# end-user knob value. Demoted to module-level internal constants. If a
# future need arises to tune them per-task, re-introduce a Sec-Privileged
# API rather than restoring the public surface.
_DEFAULT_LEASE_SECONDS = 60
#  (task-attachments) §3.3 — the steering queue is hard-capped
# at 9 entries. This reserves at most 10 of the 20 attachment slots for
# framework use (9 steering + 1 function input); the other 10 remain
# free for future features. Replaces the prior 10-cap.
_DEFAULT_MAX_PENDING_STEERING = 9


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


def _check_input_precondition(  # pylint: disable=unused-argument
    *,
    existing: Any,
    task_id: str,
    input_id: str | None,
    if_last_input_id: str | None,
) -> None:
    """Validate the ``if_last_input_id`` precondition before any accept path.

    Semantic rules:

    - Both ``input_id`` and ``if_last_input_id`` ``None``: no precondition.
    - ``input_id`` set, ``if_last_input_id`` ``None``: idempotency-only mode
      — the caller wants the chain head advanced to ``input_id`` but is
      NOT asserting any predecessor. Always succeeds; the chain head is
      overwritten on the accept path. Use this for per-turn idempotency
      identifiers (e.g. a response_id) when chain-ordering is enforced
      externally (e.g. by task_id collapse + TaskConflictError
      sequencing for conversation-grouped multi-turn).
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
    if if_last_input_id is None:
        # Either no precondition at all, or idempotency-only mode where
        # the caller advances the chain head without asserting any
        # predecessor. Both cases succeed unconditionally.
        return
    from ._exceptions import (  # pylint: disable=import-outside-toplevel
        LastInputIdPreconditionFailed,
    )

    stored = _read_stored_last_input_id(existing)
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
    """Build the top-level ``payload["last_input_id"]`` seed dict, or ``None``.

    Used at fresh-create and at suspended-resume to advance the stored
    ``last_input_id`` atomically with the input persist.

    :param input_id: The new input's identity, or ``None`` for callers not
        opting in to chain semantics.
    :type input_id: str | None
    :returns: ``{"last_input_id": input_id}`` if ``input_id`` is set,
        else ``None``.
    :rtype: dict[str, Any] | None
    """
    if input_id is None:
        return None
    return {_LAST_INPUT_ID_PAYLOAD_KEY: input_id}


def _generate_input_id() -> str:
    """Mint a fresh per-turn ``input_id`` for a multi-turn turn.

    The task/streaming identity rule: ``input_id`` defaults to ``task_id`` for a
    one-shot task (1:1), but each turn of a multi-turn chain gets its OWN unique
    id when the caller does not supply one. Prefixed for readability; stays within
    the ``input_id`` charset/length validated by :func:`_validate_input_id`.

    :returns: A unique input id of the form ``input-<uuid4-hex>``.
    :rtype: str
    """
    import uuid as _uuid  # pylint: disable=import-outside-toplevel

    return f"input-{_uuid.uuid4().hex}"


class TaskOptions:  # pylint: disable=too-many-instance-attributes
    """Internal task options bag.

    *Internal*: not part of the public ``resilient`` surface as of.
    Constructed by the ``@task`` decorator (and ``Task.options()``) from a small
    public kwarg set: ``name``, ``title``, ``tags``, ``timeout``, ``ephemeral``,
    ``retry``, ``steerable``, .

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
    """

    __slots__ = (
        "name",
        "title",
        "tags",
        "timeout",
        "ephemeral",
        "retry",
        "steerable",
        "_is_multi_turn",  #  — True when wrapped by @multi_turn_task
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
        _is_multi_turn: bool = False,
    ) -> None:
        self.name = name
        self.title = title
        self.tags = tags if tags is not None else {}
        self.timeout = timeout
        self.ephemeral = ephemeral
        self.retry = retry
        self.steerable = steerable
        self._is_multi_turn = _is_multi_turn

    def __repr__(self) -> str:
        return (
            f"TaskOptions(name={self.name!r}, "
            f"ephemeral={self.ephemeral}, retry={self.retry!r}, "
            f"timeout={self.timeout!r}, steerable={self.steerable})"
        )


class Task(Generic[Input, Output]):
    """A decorated resilient task function. Not callable directly.

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
        #  — if a TaskManager is already initialised (decorators
        # declared after startup, e.g. in tests), eagerly push into its
        # resume tables so _recover_stale_tasks / get_active_run can pick
        # up the multi-turn opts (_is_multi_turn).
        try:
            from ._manager import _manager as _live_manager  # pylint: disable=import-outside-toplevel
        except ImportError:  # pragma: no cover
            _live_manager = None  # type: ignore[assignment]
        if _live_manager is not None:
            try:
                _live_manager._resume_callbacks[opts.name] = fn  # noqa: SLF001
                _live_manager._resume_opts[opts.name] = opts  # noqa: SLF001
            except Exception:  # noqa: BLE001  # pylint: disable=broad-except
                pass

    def _resolve_title(self, input_val: Input, task_id: str) -> str:
        if callable(self._opts.title):
            return self._opts.title(input_val, task_id)
        if isinstance(self._opts.title, str):
            return self._opts.title
        return f"{self.name}:{task_id[:8]}"

    def _resolve_tags(self, input_val: Input, task_id: str) -> dict[str, str]:
        """Resolve decorator-level tags (static dict or callable factory).

        Reserved tags (the exact key ``task_name``) are stripped to
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
                raise TypeError(f"tags callable must return dict[str, str], " f"got {type(result).__name__}")
            return _strip_reserved_tags(result)
        return _strip_reserved_tags(dict(tags) if tags else {})

    def _merge_tags(self, input_val: Input, task_id: str, call_tags: dict[str, str] | None) -> dict[str, str]:
        merged = self._resolve_tags(input_val, task_id)
        if call_tags:
            merged.update(_strip_reserved_tags(call_tags))
        return merged

    async def run(
        self,
        *,
        task_id: str | None = None,
        input: Input,  # noqa: A002
        input_id: str | None = None,
        if_last_input_id: str | None = None,
    ) -> Output:
        """Run a lifecycle-aware resilient task and return the result.

        Automatically starts, resumes, or recovers the task based on its
        current state:

        - No task / pending → create and start (``entry_mode="fresh"``)
        - Suspended → resume with new input (``entry_mode="resumed"``)
        - In-progress (stale) → recover (``entry_mode="recovered"``)
        - In-progress (not stale) → raise :class:`TaskConflictError`
        - Completed → raise :class:`TaskConflictError`

        .. note::

            ``title``, ``tags``, ``retry``, are
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
            input id in a framework-reserved slot (``payload["last_input_id"]``).

            Two modes:

            - **Idempotency-only** (``input_id`` set, ``if_last_input_id`` unset):
              advances the stored chain head unconditionally. Always succeeds; no
              precondition check. Use this when chain ordering is enforced by
              another mechanism (e.g. ``task_id`` collapse + ``TaskConflictError``
              / steering-queue sequencing for conversation-grouped multi-turn).
            - **Chain-extension** (paired with ``if_last_input_id``):
              implements HTTP If-Match-style optimistic concurrency on the
              input queue — see ``if_last_input_id`` below.
        :paramtype input_id: str | None
        :keyword if_last_input_id: Optional precondition. When supplied, the framework
            verifies that the task's currently-stored last input id equals this value
            before accepting the new input. If the precondition does not hold (a
            concurrent caller advanced the queue, or the caller's view is stale),
            raises :class:`LastInputIdPreconditionFailed` before any state mutation.
            Modelled on HTTP ``If-Match: <etag>`` semantics. Requires ``input_id``
            to also be supplied (raises :class:`TypeError` otherwise — a
            precondition without an advancing id is not meaningful).
        :paramtype if_last_input_id: str | None
        :return: The task result wrapper with output, status, and suspension info.
        :rtype: ~azure.ai.agentserver.core.tasks.TaskResult[Output]
        :raises TaskFailed: On unhandled exception.
        :raises ~azure.ai.agentserver.core.tasks.TaskConflictError: If the
            task is already in-progress or completed.
        :raises ~azure.ai.agentserver.core.tasks.LastInputIdPreconditionFailed: If
            the ``if_last_input_id`` precondition does not match the stored
            last input id.
        :raises TypeError: If ``if_last_input_id`` is supplied without ``input_id``.
        """
        #: one-shot Task.start/.run — task_id is OPTIONAL,
        # auto-generated as a GUID when not supplied.
        if task_id is None:
            import uuid as _uuid  # pylint: disable=import-outside-toplevel

            task_id = _uuid.uuid4().hex
        _validate_task_id(task_id)
        if input_id is not None:
            _validate_input_id(input_id)
        if if_last_input_id is not None and input_id is None:
            raise TypeError(
                "if_last_input_id requires input_id (a precondition without an advancing id is not meaningful)"
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
        task_id: str | None = None,
        input: Input,  # noqa: A002
        input_id: str | None = None,
        if_last_input_id: str | None = None,
    ) -> TaskRun[Output]:
        """Start a lifecycle-aware resilient task and return a handle.

        Follows the same lifecycle rules as :meth:`run` but returns
        immediately with a :class:`TaskRun` handle instead of blocking.

        .. note::

            ``title``, ``tags``, ``retry``, are
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
            input id in a framework-reserved slot (``payload["last_input_id"]``).

            Two modes:

            - **Idempotency-only** (``input_id`` set, ``if_last_input_id`` unset):
              advances the stored chain head unconditionally. Always succeeds; no
              precondition check. Use this when chain ordering is enforced by
              another mechanism (e.g. ``task_id`` collapse + ``TaskConflictError``
              / steering-queue sequencing for conversation-grouped multi-turn).
            - **Chain-extension** (paired with ``if_last_input_id``):
              implements HTTP If-Match-style optimistic concurrency on the
              input queue — see ``if_last_input_id`` below.
        :paramtype input_id: str | None
        :keyword if_last_input_id: Optional precondition. When supplied, the framework
            verifies that the task's currently-stored last input id equals this value
            before accepting the new input. If the precondition does not hold (a
            concurrent caller advanced the queue, or the caller's view is stale),
            raises :class:`LastInputIdPreconditionFailed` before any state mutation.
            Modelled on HTTP ``If-Match: <etag>`` semantics. Requires ``input_id``
            to also be supplied (raises :class:`TypeError` otherwise — a
            precondition without an advancing id is not meaningful).
        :paramtype if_last_input_id: str | None
        :return: A handle to the running task.
        :rtype: TaskRun[Output]
        :raises ~azure.ai.agentserver.core.tasks.TaskConflictError: If the
            task is already in-progress or completed.
        :raises ~azure.ai.agentserver.core.tasks.LastInputIdPreconditionFailed: If
            the ``if_last_input_id`` precondition does not match the stored
            last input id.
        :raises TypeError: If ``if_last_input_id`` is supplied without ``input_id``.
        """
        #: one-shot Task.start/.run — task_id is OPTIONAL,
        # auto-generated as a GUID when not supplied.
        if task_id is None:
            import uuid as _uuid  # pylint: disable=import-outside-toplevel

            task_id = _uuid.uuid4().hex
        _validate_task_id(task_id)
        if input_id is not None:
            _validate_input_id(input_id)
        if if_last_input_id is not None and input_id is None:
            raise TypeError(
                "if_last_input_id requires input_id (a precondition without an advancing id is not meaningful)"
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
            *Internal* as of  — public consumers should use
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
        return await manager._provider_get_tracked(task_id)  # noqa: SLF001  # pylint: disable=protected-access

    async def get_active_run(self, task_id: str) -> TaskRun[Output] | None:
        """Return a TaskRun handle for an active (in-progress) task.

        : consults the store, not only
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

    #: Task.get is removed. TaskSnapshot is gone.
    # Use manager.provider.get(task_id) directly for read-only inspection
    # (returns TaskInfo, not a Snapshot wrapper).

    async def _list(
        self,
        *,
        session_id: str | None = None,
        status: TaskStatus | None = None,
    ) -> list[Any]:
        """List tasks created by this resilient task function (internal).

        .. note::
            *Internal* as of  — public consumers should use
            ``manager.list_tasks(fn_name=...)`` directly.

        Automatically scoped to this function's ``name`` via the
        ``task_name`` tag (server-side) and ``source.type``
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

    async def _append_steering_input(  # pylint: disable=protected-access,too-many-locals,too-many-statements
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
        :keyword input_id:  When set, the new input's identity.
                    Used to advance ``payload["last_input_id"]``
                    atomically with the queue append.
                :paramtype input_id: str | None
        :keyword if_last_input_id:  When set, the precondition
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
                existing
                if _attempt == 0
                else await manager._provider_get_tracked(task_id)  # pylint: disable=protected-access
            )
            if task_info is None:
                raise RuntimeError(f"Task {task_id!r} disappeared during steering append")

            #  Re-check the input precondition on each retry to
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
            steering = dict(payload.get("steering", {}))
            pending: list[Any] = list(steering.get("pending_inputs", []))

            if len(pending) >= _DEFAULT_MAX_PENDING_STEERING:
                raise SteeringQueueFull(task_id, _DEFAULT_MAX_PENDING_STEERING)

            #  — route through the promotion helper. Small steering
            # inputs (≤ 20 KiB serialized) stay as raw values in
            # ``pending_inputs``; larger ones are written to
            # ``attachments["_steering_input_<seq>"]`` with a ref slot in
            # the queue. The seq counter is monotonic (never reused) so
            # other entries' attachment keys are stable across drains.
            from ._attachments import (  # pylint: disable=import-outside-toplevel
                _STEERING_INPUT_KEY_PREFIX,
                _STEERING_THRESHOLD_BYTES,
                _resolve_input_storage,
            )

            next_seq = int(steering.get("next_input_seq", 0))
            steering_key = f"{_STEERING_INPUT_KEY_PREFIX}{next_seq}"
            store_mode, queue_entry = _resolve_input_storage(
                serialized,
                threshold_bytes=_STEERING_THRESHOLD_BYTES,
                key_for_attachment=steering_key,
                task_id=task_id,
            )
            attachments_patch: dict[str, Any] | None = None
            if store_mode == "attachment":
                attachments_patch = {steering_key: serialized}
                steering["next_input_seq"] = next_seq + 1

            pending.append(queue_entry)
            steering["pending_inputs"] = pending
            steering["cancel_requested"] = True
            #   SOT: the
            # internal _steering["generation"] payload field is removed
            # alongside the public ctx.steering_generation surface.
            payload["steering"] = steering

            #  When the caller opted in via
            # input_id, advance the framework-managed last_input_id slot
            # atomically with the queue append. The slot is a top-level
            # `_`-prefixed payload key (: flat layout).
            if input_id is not None:
                payload[_LAST_INPUT_ID_PAYLOAD_KEY] = input_id

            etag = getattr(task_info, "etag", None) or None
            # Piggyback lease ownership on the steering-append PATCH so
            # the lease is refreshed as a side effect (see
            # ``TaskManager._lease_ext_kwargs``). Zero extra round-
            # trips: lease params land on the same PATCH that's
            # already going out for the payload mutation. No-op when
            # the caller is not the active owner of the task (the
            # ``_lease_ext_kwargs`` helper returns ``{}`` in that
            # case, so the wire format is unchanged).
            lease_kwargs = manager._lease_ext_kwargs(task_id)  # pylint: disable=protected-access
            try:
                await manager.provider.update(
                    task_id,
                    TaskPatchRequest(
                        payload=payload,
                        attachments=attachments_patch,
                        if_match=etag,
                        **lease_kwargs,
                    ),
                )
                manager._note_lease_refreshed(task_id)  # pylint: disable=protected-access
                # Signal the running task's cancel event so it can short-circuit.
                # Spec 031 / FR-001a + SOT §13 ordering invariant: record the
                # live pending count BEFORE setting cancel, so a handler that
                # observes ``ctx.cancel.is_set()`` already sees
                # ``ctx.pending_input_count >= 1``.
                active = manager._active_tasks.get(task_id)  # pylint: disable=protected-access  # noqa: SLF001
                if active and hasattr(active, "context") and active.context is not None:
                    active._pending_input_count = len(pending)  # pylint: disable=protected-access  # noqa: SLF001
                    active.context.cancel.set()
                return
            except _HostedConflict as exc:
                translated = _translate_hosted_conflict(exc, task_id=task_id)
                if translated is None:
                    continue
                raise translated from exc
            except ValueError:
                # Local provider etag conflict -- retry with the new etag
                continue
            except _TransportClassifiedError as exc:
                # Hosted task store etag conflict (412 / 409) -- retry.
                if getattr(exc, "classification", None) == "conflict":
                    continue
                raise

        raise RuntimeError(f"Failed to append steering input after {max_retries} retries")

    def _create_steering_ack_run(
        self,
        manager: Any,
        task_id: str,
        future: Any,
        input_id: str | None = None,
        input_val: Any = None,
    ) -> TaskRun[Output]:
        """Create a TaskRun for a queued steering input.

        :param manager: The task manager owning the active execution.
        :type manager: Any
        :param task_id: Stable task identifier.
        :type task_id: str
        :param future: Future that will resolve with the next-turn outcome.
        :type future: Any
        :param input_id: The input_id stamped on the queued input (if any).
        :type input_id: str | None
        :param input_val: The raw queued input value (used to identify the
            slot when ``cancel()`` is invoked on the returned handle).
        :type input_val: Any
        :return: A :class:`TaskRun` whose result resolves with the queued turn.
        :rtype: TaskRun[Output]
        """

        async def _queued_cancel_cb() -> None:
            await manager._cancel_queued_steering_input(  # pylint: disable=protected-access
                task_id=task_id,
                future=future,
                input_id=input_id,
                input_val=input_val,
            )

        return TaskRun(
            task_id=task_id,
            provider=manager.provider,
            result_future=future,
            input_id=input_id,
            queued_cancel_callback=_queued_cancel_cb,
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
        :keyword input_id:  When set, the new input's identity
                    recorded in the framework-reserved
                    ``payload["last_input_id"]`` slot.
                :paramtype input_id: str | None
        :keyword if_last_input_id:  Precondition value checked
                    against the stored ``last_input_id`` before any accept path.
                :paramtype if_last_input_id: str | None
                :return: A handle to the running task.
                :rtype: TaskRun[Output]
        """
        from ._exceptions import (  # pylint: disable=import-outside-toplevel
            TaskConflictError,
        )

        #: orphan-sandbox eviction at scheduling
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
        except _HostedConflict as exc:
            translated = _translate_hosted_conflict(exc, task_id=task_id)
            if translated is None:
                if exc._code == "lease_ownership_changed":  # pylint: disable=protected-access
                    raise TaskConflictError(task_id, "in_progress") from exc
                raise RuntimeError(f"Task {task_id!r} operation did not converge after retryable conflict") from exc
            raise translated from exc
        except _TransportClassifiedError as exc:
            if getattr(exc, "classification", None) == "evicted":
                # Pre-import only at the eviction site to avoid a cycle.
                raise TaskConflictError(task_id, "in_progress") from exc
            raise

    async def _lifecycle_start_inner(  # pylint: disable=too-many-locals,too-many-statements,too-many-branches
        self,
        *,
        task_id: str,
        input: Input,  # noqa: A002
        input_id: str | None = None,
        if_last_input_id: str | None = None,
    ) -> TaskRun[Output]:
        """Inner body of :meth:`_lifecycle_start`. See that method for docs.

        Split out so the outer wrapper can convert   evictions
        to ``TaskConflictError`` without indenting the entire body.

        :keyword task_id: Stable task identifier (same as outer method).
        :paramtype task_id: str
        :keyword input: Input value for the task (same as outer method).
        :paramtype input: Input
        :keyword input_id: Optional input identifier for sequential-input
            acceptance preconditions (same as outer method).
        :paramtype input_id: str | None
        :keyword if_last_input_id: Optional if-match precondition on the
            last persisted ``input_id`` (same as outer method).
        :paramtype if_last_input_id: str | None
        :return: A :class:`TaskRun` handle for the started task.
        :rtype: TaskRun[Output]
        """
        from ._exceptions import (  # pylint: disable=import-outside-toplevel
            TaskConflictError,
        )
        from ._manager import (  # pylint: disable=import-outside-toplevel
            get_task_manager,
        )

        manager = get_task_manager()
        existing = await manager._provider_get_tracked(task_id)  # pylint: disable=protected-access

        resolved_retry = self._opts.retry

        #  Pre-acceptance check: if the caller supplied an
        # ``if_last_input_id`` precondition, verify the stored last input id
        # matches before proceeding to any accept path. The actual advance
        # (storing ``input_id`` into ``payload["last_input_id"]``) is bundled
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
                initial_payload_extras=_build_framework_extras(input_id),
            )

        if existing.status == "suspended":
            # Resume — patch input onto task, then start.
            #  Etag-protected retry loop so concurrent
            # suspended-resume POSTs race safely instead of silently
            # overwriting each other.
            #  On the same atomic patch, advance the
            # framework's `payload["last_input_id"]` slot when the caller
            # opted in via `input_id`. The precondition check already ran
            # at the top of `_lifecycle_start` against the read existing.
            serialized = _serialize_input(input)
            from ._attachments import (  # pylint: disable=import-outside-toplevel
                _FUNCTION_INPUT_KEY,
                _INPUT_THRESHOLD_BYTES,
                _resolve_input_storage,
            )
            from ._models import (  # pylint: disable=import-outside-toplevel
                TaskPatchRequest,
            )

            #  — promotion: route the resume input through the
            # same helper as the create path. Inline stays raw in payload;
            # > 200 KiB spills into ``attachments["input"]`` with a ref
            # in payload. Single PATCH carries both.
            input_mode, input_value = _resolve_input_storage(
                serialized,
                threshold_bytes=_INPUT_THRESHOLD_BYTES,
                key_for_attachment=_FUNCTION_INPUT_KEY,
                task_id=task_id,
            )
            attachments_patch: dict[str, Any] | None = None
            if input_mode == "attachment":
                attachments_patch = {_FUNCTION_INPUT_KEY: serialized}

            max_resume_retries = 5
            current_info = existing
            for _attempt in range(max_resume_retries):
                etag = getattr(current_info, "etag", None) or None
                # Build the resume patch: input + (optionally) advance the
                # framework-managed last_input_id slot (flat layout).
                resume_payload: dict[str, Any] = {"input": input_value}
                if input_id is not None:
                    resume_payload[_LAST_INPUT_ID_PAYLOAD_KEY] = input_id
                try:
                    # PATCH returns the updated TaskInfo -- capture it
                    # to skip the post-patch refetch below.
                    #   /  — route through the
                    # manager's per-task write queue so the etag cache
                    # is refreshed from the response (otherwise the
                    # subsequent _start_existing_task PATCH would carry
                    # a stale if_match and 412 against itself).
                    updated_info = await manager._provider_update_locked(  # pylint: disable=protected-access
                        task_id,
                        TaskPatchRequest(
                            payload=resume_payload,
                            attachments=attachments_patch,
                            if_match=etag,
                        ),
                    )
                    break
                except _HostedConflict as exc:
                    translated = _translate_hosted_conflict(exc, task_id=task_id)
                    if translated is not None:
                        raise translated from exc
                    refreshed = await manager._provider_get_tracked(task_id)  # pylint: disable=protected-access
                    if refreshed is None:
                        raise RuntimeError(f"Task {task_id!r} disappeared during suspended-resume retry") from exc
                    _check_input_precondition(
                        existing=refreshed,
                        task_id=task_id,
                        input_id=input_id,
                        if_last_input_id=if_last_input_id,
                    )
                    current_info = refreshed
                except (ValueError, _TransportClassifiedError) as exc:
                    # Etag conflict -- re-fetch, re-check precondition, retry.
                    # Local provider raises ValueError; hosted task store
                    # raises TransportClassifiedError with classification=
                    # "conflict" (412 etag mismatch or 409). Both are
                    # the same logical concurrency outcome.
                    if (
                        isinstance(exc, _TransportClassifiedError)
                        and getattr(exc, "classification", None) != "conflict"
                    ):
                        raise
                    refreshed = await manager._provider_get_tracked(task_id)  # pylint: disable=protected-access
                    if refreshed is None:
                        raise RuntimeError(f"Task {task_id!r} disappeared during suspended-resume retry") from exc
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
            # PATCH already returned the updated TaskInfo -- no GET needed.
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
            #   Layer 3 +: consult the lease
            # state to decide recovery vs. conflict. The legacy
            # _LEGACY_INPROCESS_STALE_THRESHOLD_SECONDS wall-clock
            # heuristic over updated_at is replaced by the proper
            # lease-state determination via _lease_is_dead. If the
            # lease is dead, inline-reclaim via _reclaim_one and
            # re-enter as recovered (Layer 3); if alive,
            # either queue the steering input or raise TaskConflictError.
            from ._manager import (  # pylint: disable=import-outside-toplevel
                _lease_is_dead,
            )

            active_locally = manager._active_tasks.get(task_id) is not None  # pylint: disable=protected-access
            lease_dead = _lease_is_dead(
                existing,
                this_lease_owner=manager._lease_owner,  # pylint: disable=protected-access
                active_locally=active_locally,
            )

            if lease_dead:
                # Inline reclaim per  layer (c). On race-lost /
                # eviction the TransportClassifiedError propagates and
                # the outer _lifecycle_start wrapper converts it to
                # TaskConflictError (Invariant 1 shape).
                try:
                    await manager._reclaim_one(existing)  # pylint: disable=protected-access
                except _HostedConflict as exc:
                    translated = _translate_hosted_conflict(exc, task_id=task_id)
                    if translated is None or getattr(translated, "current_status", None) == "in_progress":
                        raise TaskConflictError(task_id, "in_progress") from exc
                    raise translated from exc
                except _TransportClassifiedError as exc:
                    if getattr(exc, "classification", None) == "evicted":
                        raise TaskConflictError(task_id, "in_progress") from exc
                    raise

                # Stale with steering recovery state — recover via steered path
                if self._opts.steerable and existing.payload:
                    steering = existing.payload.get("steering", {})
                    if steering.get("drain_in_progress") or steering.get("pending_inputs"):
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
                # Normal recovery
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
                # pylint: disable=protected-access
                ack_future = manager._register_steering_future(task_id)
                await self._append_steering_input(
                    manager,
                    task_id=task_id,
                    input_val=input,
                    existing=existing,
                    input_id=input_id,
                    if_last_input_id=if_last_input_id,
                )
                # Set cancel on in-memory context if task runs in this process
                active = manager._active_tasks.get(task_id)
                # pylint: enable=protected-access
                if active:
                    active.context.cancel.set()
                return self._create_steering_ack_run(manager, task_id, ack_future, input_id=input_id, input_val=input)
            raise TaskConflictError(task_id, "in_progress")

        # completed (or any other terminal status)
        raise TaskConflictError(task_id, existing.status)


@overload
def task(
    fn: Callable[[TaskContext[Input]], Awaitable[Output]],
    *,
    name: str,
    title: str | None = ...,
    timeout: timedelta | None = ...,
    retry: RetryPolicy | None = ...,
) -> Task[Input, Output]: ...


@overload
def task(
    *,
    name: str,
    title: str | None = ...,
    timeout: timedelta | None = ...,
    retry: RetryPolicy | None = ...,
) -> Callable[
    [Callable[[TaskContext[Input]], Awaitable[Output]]],
    Task[Input, Output],
]: ...


def task(
    fn: Callable[..., Any] | None = None,
    *,
    name: str | None = None,
    title: str | None = None,
    timeout: timedelta | None = None,
    retry: RetryPolicy | None = None,
    **_extra_kwargs: Any,
) -> Any:
    """Turn an async function into a crash-resilient one-shot resilient task.

    One-shot tasks are always ephemeral — the persisted record is
    deleted on terminal exit. ``task_id`` is optional on the resulting
    handle's ``.start`` / ``.run`` calls; the framework auto-generates
    a GUID and defaults ``input_id`` to ``task_id`` (1:1 invariant).

    ``name`` is required — always use the parameterized form::

        @task(name="my-task")
        async def my_task(ctx: TaskContext[MyInput]) -> MyOutput: ...

    :param fn: The async function to decorate (parameterized form only; the
        bare ``@task`` form is rejected because it cannot supply a ``name``).
    :type fn: Callable[..., Any] | None
    :keyword name: **Required stable identity anchor.** Used for recovery routing
        and source stamping. There is no function-derived default: deriving it
        from ``fn.__qualname__`` would silently rebind task identity whenever the
        function is renamed or moved, orphaning in-flight tasks on the next
        deploy. Omitting it (or passing whitespace) raises ``ValueError`` at
        decoration.
    :keyword title: Static human-readable string.
    :keyword timeout: Per-turn, wall-clock, resilient, cooperative-only
        execution budget. Defaults to 1 day when unset; a supplied value may
        lower the budget but 1 day is a hard ceiling (a larger or negative value
        raises ``ValueError`` at decoration). This caps a single handler
        invocation only — it is NOT a task-lifetime bound. When the budget
        elapses for the current turn, ``ctx.timeout_exceeded`` is set then
        ``ctx.cancel`` is set; the handler decides whether to wind down. The
        watchdog does NOT force-stop the handler. See the developer guide
        §4 Timeout for the full mechanic (including the crash-mid-turn
        budget-preserving recovery semantics).
    :keyword retry: Default retry policy for this task. Recovery-safe: applied
        by the framework on every entry, including crash recovery.
    :return: A ``Task[Input, Output]`` wrapper.
    :rtype: Any

    .. note::
       Use ``@multi_turn_task`` for steerable chains. Passing
       ``ephemeral=`` or ``steerable=`` to ``@task`` raises
       ``TypeError`` at decoration time.
    """
    # Reject unknown / unsupported kwargs at decoration time.
    # ``steerable=`` and ``ephemeral=`` are NOT accepted on @task; use
    # @multi_turn_task for steerable chains.
    _validate_task_kwargs(**_extra_kwargs)
    _validate_title(title)
    _validate_task_name(name)
    _validate_timeout(timeout)

    def _wrap(func: Callable[..., Any]) -> Task[Any, Any]:
        if not asyncio.iscoroutinefunction(func):
            raise TypeError(f"@task requires an async def function (an async function), " f"got {func.__qualname__!r}")
        _validate_handler_signature(func, "task")

        input_type, output_type = _extract_generic_args(func)

        opts = TaskOptions(
            name=name,  # type: ignore[arg-type]  # _validate_task_name guarantees non-None
            title=title,
            tags={},
            timeout=timeout,
            ephemeral=True,
            retry=retry,
            steerable=False,
        )

        return Task(
            fn=func,
            opts=opts,
            input_type=input_type,
            output_type=output_type,
        )

    if fn is not None:
        return _wrap(fn)
    return _wrap


# =========================================================================
#  — Phase 2: class split + identifier supply + handler-sig validation
# =========================================================================
#
# /  /  /  /  /.
#
# - `MultiTurnTask` is a DISTINCT public class from `Task` (— not a
#   subclass; type checker enforces "no .delete() on one-shot").
# - `@multi_turn_task(steerable=...)` decorator returns MultiTurnTask.
# - Both decorators validate kwargs at decoration time  and accept
#   only static-string `title`.
# - Handler signature validation.


def _validate_title(title: object) -> None:
    """/  — title must be `str | None`. Callable form REMOVED.

    :param title: The title value to validate.
    :type title: object
    """
    if title is not None and not isinstance(title, str):
        raise TypeError(
            f"@task / @multi_turn_task `title=` must be `str | None`; "
            f"callable-factory form is not supported (got {type(title).__name__}: {title!r})"
        )


def _validate_handler_signature(func: Callable[..., Any], decorator_name: str) -> None:
    """— handler must be `async def fn(ctx: TaskContext[Input]) -> Output`.

    :param func: The handler function to validate.
    :type func: Callable[..., Any]
    :param decorator_name: The decorator name used in error messages.
    :type decorator_name: str
    """
    if not asyncio.iscoroutinefunction(func):
        raise TypeError(
            f"@{decorator_name} requires an `async def` (async function) handler, "
            f"got synchronous {func.__qualname__!r}"
        )
    try:
        sig = inspect.signature(func)
    except (ValueError, TypeError):
        return  # builtins / C-level callables — let downstream binding catch it
    params = list(sig.parameters.values())
    if not params:
        raise TypeError(
            f"@{decorator_name} handler must accept a `ctx: TaskContext[Input]` "
            f"first positional argument; got zero-arg signature in "
            f"{func.__qualname__!r}"
        )
    first = params[0]
    if first.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
        raise TypeError(
            f"@{decorator_name} handler must accept a `ctx: TaskContext[Input]` "
            f"as first positional argument; got *{first.name} / **{first.name} in "
            f"{func.__qualname__!r}"
        )
    if first.name != "ctx":
        #: first parameter MUST be named ``ctx``.
        raise TypeError(
            f"@{decorator_name} handler first argument must be named `ctx` "
            f"(found {first.name!r} in {func.__qualname__!r})"
        )
    # The remaining positional/keyword args must all have defaults (the
    # framework calls handler(ctx) with no extra args).
    for p in params[1:]:
        if p.default is inspect.Parameter.empty and p.kind in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        ):
            raise TypeError(
                f"@{decorator_name} handler must accept only `ctx`; extra "
                f"required argument {p.name!r} in {func.__qualname__!r} has no default"
            )


_ALLOWED_TASK_KWARGS = frozenset({"name", "title", "timeout", "retry"})
_ALLOWED_MULTI_TURN_TASK_KWARGS = frozenset({"name", "title", "timeout", "retry", "steerable"})


def _validate_task_kwargs(**kwargs: Any) -> None:
    """@task allow-list: name / title / timeout / retry only.

    Unknown kwargs raise ``TypeError`` at decoration time. ``steerable=``
    and ``ephemeral=`` are explicitly NOT accepted — use
    ``@multi_turn_task`` for steerable chains; one-shot tasks are always
    ephemeral.
    """
    unknown = set(kwargs) - _ALLOWED_TASK_KWARGS
    if unknown:
        msg = f"@task got unexpected kwargs: {sorted(unknown)}. Allowed: {sorted(_ALLOWED_TASK_KWARGS)}."
        if "steerable" in unknown or "ephemeral" in unknown:
            msg += (
                " Use @multi_turn_task for steerable chains; one-shot "
                "@task is always ephemeral (the record is deleted on "
                "terminal exit)."
            )
        raise TypeError(msg)


def _validate_multi_turn_task_kwargs(**kwargs: Any) -> None:
    """— @multi_turn_task allow-list."""
    unknown = set(kwargs) - _ALLOWED_MULTI_TURN_TASK_KWARGS
    if unknown:
        if "ephemeral" in unknown:
            raise TypeError("@multi_turn_task does not accept `ephemeral=` (chains are never ephemeral)")
        if "tags" in unknown:
            raise TypeError("@multi_turn_task does not accept `tags=` (tags surface is not part of)")
        raise TypeError(
            f"@multi_turn_task got unexpected kwargs: {sorted(unknown)}. "
            f"Allowed: {sorted(_ALLOWED_MULTI_TURN_TASK_KWARGS)}"
        )


class MultiTurnTask(Generic[Input, Output]):  # pylint: disable=protected-access
    """A decorated multi-turn resilient task chain.

    Distinct public class:class:`Task` — NOT a subclass.
    The type checker enforces "no ``.delete()`` on one-shot" and
    "multi-turn ``get_active_run`` takes both ``task_id`` AND ``input_id``"
    statically.

    Returned by the :func:`multi_turn_task` decorator.

    This class wraps an internal :class:`Task` (same execution model) but
    exposes a strictly-typed multi-turn surface. The wrapped Task carries
    ``ephemeral=False`` so the framework knows the chain semantics.
    """

    # Internal flag — multi-turn chains never auto-delete on suspend.
    _is_multi_turn = True

    def __init__(
        self,
        fn: Callable[..., Any],
        opts: TaskOptions,
        input_type: type | None = None,
        output_type: type | None = None,
    ) -> None:
        self._inner = Task(
            fn=fn,
            opts=opts,
            input_type=input_type,  # type: ignore[arg-type]  # None defaults handled by Task
            output_type=output_type,  # type: ignore[arg-type]
        )

    @property
    def _fn(self) -> Callable[..., Any]:
        return self._inner._fn  # noqa: SLF001  # pylint: disable=protected-access

    @property
    def _opts(self) -> TaskOptions:
        return self._inner._opts  # noqa: SLF001  # pylint: disable=protected-access

    @property
    def _input_type(self) -> Any:
        return self._inner._input_type  # noqa: SLF001  # pylint: disable=protected-access

    @property
    def _output_type(self) -> Any:
        return self._inner._output_type  # noqa: SLF001  # pylint: disable=protected-access

    @property
    def name(self) -> str:
        """The registered task name (proxy of the wrapped Task).

        :return: The registered task name.
        :rtype: str
        """
        return self._inner.name

    async def run(
        self,
        *,
        task_id: str,
        input: Any,  # noqa: A002
        input_id: str | None = None,
        if_last_input_id: str | None = None,
    ) -> Output:
        """Run one turn on the chain identified by ``task_id``.

        :keyword task_id: The chain identifier (mandatory).
        :keyword input: The turn's input value.
        :keyword input_id: Optional per-turn identifier; auto-generated
            when omitted.
        :keyword if_last_input_id: Optional ``If-Match``-style
            precondition on the chain's last-accepted ``input_id``.
        :return: The handler's return value for this turn.
        :rtype: Output
        """
        # Multi-turn identity rule: each turn gets its OWN unique input_id.
        # When the caller omits one (and isn't running an If-Match precondition,
        # which requires an explicit advancing id), mint a fresh per-turn id so
        # it is persisted as the chain head (``last_input_id``) and surfaced on
        # the turn's ``TaskContext.input_id`` — matching the spec + this method's
        # docstring + the .NET port. One-shot tasks still default to ``task_id``.
        if input_id is None and if_last_input_id is None:
            input_id = _generate_input_id()
        return await self._inner.run(
            task_id=task_id,
            input=input,
            input_id=input_id,
            if_last_input_id=if_last_input_id,
        )

    async def start(
        self,
        *,
        task_id: str,
        input: Any,  # noqa: A002
        input_id: str | None = None,
        if_last_input_id: str | None = None,
    ) -> "TaskRun[Output]":
        """Start one turn on the chain identified by ``task_id`` and
        return a :class:`TaskRun` handle for that turn.

        :keyword task_id: The chain identifier (mandatory).
        :keyword input: The turn's input value.
        :keyword input_id: Optional per-turn identifier.
        :keyword if_last_input_id: Optional ``If-Match``-style precondition.
        :return: A :class:`TaskRun` handle bound to the turn.
        :rtype: TaskRun[Output]
        """
        # See MultiTurnTask.run — mint a fresh per-turn input_id when omitted.
        if input_id is None and if_last_input_id is None:
            input_id = _generate_input_id()
        return await self._inner.start(
            task_id=task_id,
            input=input,
            input_id=input_id,
            if_last_input_id=if_last_input_id,
        )

    async def get_active_run(
        self,
        task_id: str,
        input_id: str,
    ) -> "TaskRun[Output] | None":
        """Multi-turn variant of ``get_active_run`` — REQUIRES ``input_id``.

        The current turn's input_id is the match key; mismatch returns
        ``None``.

        :param task_id: The chain task_id.
        :type task_id: str
        :param input_id: The exact input_id of the currently in-flight turn.
        :type input_id: str
        :return: The TaskRun handle bound to the currently in-flight turn
            iff ``(task_id, input_id)`` exactly matches; ``None`` otherwise.
        :rtype: TaskRun[Output] | None
        """
        run = await self._inner.get_active_run(task_id)
        if run is None:
            return None
        if getattr(run, "input_id", None) != input_id:
            return None
        return run

    async def delete(self, task_id: str) -> None:
        """Force-delete the chain record + any queued inputs.

        , removes the chain record and all queued
                steerers; resolves active + queued callers' ``.result()`` futures
                with :class:`TaskCancelled`. Idempotent (no-op when the chain is
                already gone).

                :param task_id: The chain task_id to delete.
                :type task_id: str
        """
        from ._manager import get_task_manager  # pylint: disable=import-outside-toplevel
        from ._exceptions import TaskCancelled  # pylint: disable=import-outside-toplevel

        try:
            mgr = get_task_manager()
        except RuntimeError:
            return  # no manager -> nothing to delete

        # 1. Resolve any active in-process caller's future with TaskCancelled.
        active = getattr(mgr, "_active_tasks", {}).get(task_id)
        if active is not None:
            fut = getattr(active, "result_future", None)
            if fut is not None and not fut.done():
                fut.set_exception(TaskCancelled())
            # Signal the handler's cancel event so the running coroutine
            # winds down cooperatively.
            cancel_evt = getattr(active.context, "cancel", None)
            if cancel_evt is not None:
                cancel_evt.set()
            # Force-cancel the running execution_task so handlers blocked
            # on awaits that don't check ctx.cancel still exit.
            exec_task = getattr(active, "execution_task", None)
            if exec_task is not None and not exec_task.done():
                exec_task.cancel()

        # 2. Resolve all queued steerer futures with TaskCancelled.
        pending = getattr(mgr, "_pending_steering_futures", {}).pop(task_id, [])
        for queued_fut in pending:
            if not queued_fut.done():
                queued_fut.set_exception(TaskCancelled())

        # 3. Force-delete the record (idempotent — only swallow the
        # "already-gone" classes).
        provider = getattr(mgr, "_provider", None)
        if provider is not None:
            from ._exceptions_internal import TaskNotFound  # pylint: disable=import-outside-toplevel

            try:
                await provider.delete(task_id, force=True)
            except TaskNotFound:
                pass  # idempotent: already gone


@overload
def multi_turn_task(
    fn: Callable[[TaskContext[Input]], Awaitable[Output]],
    *,
    name: str,
    title: str | None = ...,
    timeout: timedelta | None = ...,
    retry: RetryPolicy | None = ...,
    steerable: bool = ...,
) -> MultiTurnTask[Input, Output]: ...


@overload
def multi_turn_task(
    *,
    name: str,
    title: str | None = ...,
    timeout: timedelta | None = ...,
    retry: RetryPolicy | None = ...,
    steerable: bool = ...,
) -> Callable[
    [Callable[[TaskContext[Input]], Awaitable[Output]]],
    MultiTurnTask[Input, Output],
]: ...


def multi_turn_task(
    fn: Callable[..., Any] | None = None,
    *,
    name: str | None = None,
    title: str | None = None,
    timeout: timedelta | None = None,
    retry: RetryPolicy | None = None,
    steerable: bool = False,
    **_extra_kwargs: Any,
) -> Any:
    """Decorator producing a multi-turn resilient chain.

        Multi-turn chains accept inputs across many turns against the same
        ``task_id``. The handler's ``return X`` is the implicit-suspend
        signal — there is no ``ctx.suspend``. The chain stays
        alive across handler raises.

        :param fn: The handler to decorate (parameterized form only; the bare
            ``@multi_turn_task`` form is rejected because it cannot supply a
            ``name``).
        :type fn: Callable[..., Any] | None
        :keyword name: **Required** stable chain-identity anchor (no
            function-derived default; omitting it raises ``ValueError``).
        :keyword title: Static human-readable string. Callable-factory form is
            not supported.
        :keyword timeout: Per-turn cooperative timeout. Defaults to 1 day when
            unset; 1 day is a hard ceiling (larger/negative rejected at
            decoration). This is a per-turn cap, not a chain-lifetime bound.
        :keyword retry: Default retry policy.
        :keyword steerable: When True, ``start()`` against an in-flight chain
            queues the new input instead of raising ``TaskConflictError``.
        :return: A :class:`MultiTurnTask` instance (distinct public class from
            :class:`Task`).
        :rtype: Any
    """
    #  — reject unknown kwargs at decoration time
    _validate_multi_turn_task_kwargs(**_extra_kwargs)
    #  /  — title must be str | None
    _validate_title(title)
    _validate_task_name(name)
    _validate_timeout(timeout)

    def _wrap(func: Callable[..., Any]) -> MultiTurnTask[Any, Any]:
        #  — handler-signature validation
        _validate_handler_signature(func, "multi_turn_task")

        input_type, output_type = _extract_generic_args(func)

        opts = TaskOptions(
            name=name,  # type: ignore[arg-type]  # _validate_task_name guarantees non-None
            title=title,
            tags={},
            timeout=timeout,
            ephemeral=False,  # multi-turn chains are NEVER ephemeral
            retry=retry,
            steerable=steerable,
            _is_multi_turn=True,  #  — signals new raise/persistence semantics
        )

        return MultiTurnTask(
            fn=func,
            opts=opts,
            input_type=input_type,
            output_type=output_type,
        )

    if fn is not None:
        return _wrap(fn)
    return _wrap
