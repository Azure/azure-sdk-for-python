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
from ._attachments import (
    _FUNCTION_INPUT_KEY,
    _INPUT_THRESHOLD_BYTES,
    _MAX_ATTACHMENT_SIZE_BYTES,
    _OUTPUT_KEY,
    _is_ref,
    _make_ref,
    _read_input_value,
    _ref_key,
    _remap_attachment_error,
    _resolve_input_storage,
    _serialized_size_bytes,
)
from ._decorator import TaskOptions, _deserialize_input, _serialize_input
from ._exceptions import (
    EtagConflict,
    OutputTooLarge,
    TaskConflictError,
    TaskFailed,
    TaskNotFound,
    _AttachmentTooLarge,
)
from ._exceptions_internal import _HostedConflict, _translate_hosted_conflict
from ._lease import derive_lease_owner, generate_instance_id, lease_renewal_loop
from ._metadata import TaskMetadata
from ._models import TaskCreateRequest, TaskInfo, TaskPatchRequest, TaskStatus
from ._provider import TaskProvider
from ._retry import RetryPolicy
from ._run import Suspended, TaskRun
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
_SOURCE_SERVER_VERSION = _build_server_version("azure-ai-agentserver-core", _CORE_VERSION)

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

    :param exc: The exception to classify.
    :type exc: BaseException
    :return: True if the exception is an eviction-classified rejection.
    :rtype: bool
    """
    return isinstance(exc, TransportClassifiedError) and getattr(exc, "classification", None) == "evicted"


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

# Spec 016 FR-023 (US7) + gap-list §FR-023: top-level payload field
# storing the ISO-8601 UTC timestamp of when the current turn started.
# Persisted at every turn-start boundary (fresh entry,
# suspended-to-in_progress resume, steering drain re-entry); NOT
# re-stamped on crash recovery so the watchdog can compute remaining
# budget = max(0, opts.timeout - (now - _turn_started_at)).
_TURN_STARTED_AT_KEY: str = "_turn_started_at"


def _utc_now_iso() -> str:
    """Return current UTC time as an ISO-8601 string with Z suffix.

    Spec 016 FR-023: persisted turn-start timestamps use this format.
    Z suffix matches `datetime.fromisoformat`'s expectations from
    Python 3.11+ (older Pythons need the `+00:00` form).

    :return: An ISO-8601 UTC timestamp ending in ``Z``.
    :rtype: str
    """
    from datetime import datetime, timezone  # pylint: disable=import-outside-toplevel

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"


def _parse_turn_started_at(value: Any) -> float | None:
    """Parse a persisted ``_turn_started_at`` value to a POSIX timestamp.

    Returns ``None`` if the value is missing, malformed, or empty —
    the caller falls back to "spawn watchdog with full budget" in
    that case (graceful degradation during the rollout window where
    pre-spec-016 records may not have the field yet).

    :param value: Raw persisted value (typically a string).
    :type value: Any
    :return: POSIX timestamp, or ``None`` if the value is invalid.
    :rtype: float | None
    """
    from datetime import datetime, timezone  # pylint: disable=import-outside-toplevel

    if not value or not isinstance(value, str):
        return None
    try:
        normalized = value.replace("Z", "+00:00") if value.endswith("Z") else value
        dt = datetime.fromisoformat(normalized)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except (ValueError, TypeError):
        return None


def _legacy_output_terminal_patch(
    *,
    task_id: str,
    metadata_dict: dict[str, Any],
    output: Any,
    extra_payload: dict[str, Any] | None = None,
    extra_attachments: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Spec 019 FR-C-005/-006/-007 — build the (payload_patch,
    attachments_patch) pair for a terminal write whose output is
    persisted via the ``_output`` attachment.

    Rules:

    - Output is ALWAYS attachment-backed when non-null (no inline
      threshold; FR-C-005 / SC-8b). ``payload["output"]`` carries a
      ref, ``attachments["_output"]`` carries the serialized value.
    - Output ``None`` writes explicit ``null`` to ``payload["output"]``
      AND deletes any existing ``_output`` attachment in the same
      PATCH (FR-C-007 / SC-10).
    - Output > 2 MB raises :class:`OutputTooLarge` BEFORE the PATCH
      is constructed (FR-C-006 / SC-9). The framework does the
      pre-check here so the developer-facing exception is raised at
      the suspend/complete site, not buried in the provider layer.

    Returns ``(payload_patch, attachments_patch)``. The
    ``attachments_patch`` is never None — it always carries the
    ``_output`` key (either the value or ``None`` for delete).

    :raises OutputTooLarge: when the serialized output exceeds 2 MB.
    """
    payload_patch: dict[str, Any] = dict(extra_payload or {})
    payload_patch["metadata"] = metadata_dict

    attachments_patch: dict[str, Any] = dict(extra_attachments or {})

    if output is None:
        payload_patch["output"] = None
        attachments_patch[_OUTPUT_KEY] = None
        return payload_patch, attachments_patch

    serialized = _serialize_input(output)
    size = _serialized_size_bytes(serialized)
    if size > _MAX_ATTACHMENT_SIZE_BYTES:
        raise OutputTooLarge(
            task_id=task_id,
            size_bytes=size,
            max_bytes=_MAX_ATTACHMENT_SIZE_BYTES,
        )
    payload_patch["output"] = _make_ref(_OUTPUT_KEY, serialized)
    attachments_patch[_OUTPUT_KEY] = serialized
    return payload_patch, attachments_patch


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

    :param pending_steering_futures: Per-task list of pending steerer
        futures (mutated in-place — emptied for the given ``task_id``).
    :type pending_steering_futures: dict[str, list[asyncio.Future[Any]]]
    :param task_id: The task whose queued steerers should be resolved.
    :type task_id: str
    :keyword current_status: Status string to carry on
        ``TaskConflictError`` so callers can branch.
    :paramtype current_status: str
    """
    # TaskConflictError is already imported at module top-level (line 24).

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

    Spec 016 FR-004 + FR-004a: a lease is "live" only if EITHER ownership
    matches this process AND an in-memory active entry tracks it (so we
    know the local execution is running), OR the lease ownership belongs
    to this process AND the expiry has not passed.

    "Dead" means the framework should reclaim. "Live" means the record
    is either currently being executed (here or elsewhere) and the
    caller should observe the conflict shape.

    Per FR-004a (lease owner includes agent_name + session_id), a record
    whose owner differs from ours belongs to a different agent — the
    framework MUST NOT reclaim it (that would steal another agent's
    work). Such records appear "dead from this process's perspective"
    but should NOT be subject to reclaim; the scheduling primitive
    raises TaskConflictError instead.

    For the LocalFileTaskProvider used in tests (no real expiry
    tracking), absence of a local in-memory entry combined with
    matching ownership suffices to detect a previous-lifetime crash.

    :param task_info: The persisted task record (any object exposing
        ``lease.owner`` and ``lease.expires_at``).
    :type task_info: Any
    :keyword this_lease_owner: Lease-owner string for this process.
    :paramtype this_lease_owner: str
    :keyword active_locally: True if this process has an in-memory
        ``_ActiveTask`` entry tracking the record.
    :paramtype active_locally: bool
    :return: True if the lease is dead AND eligible for reclaim by us.
    :rtype: bool
    """
    if active_locally:
        # We are actively executing it; lease is definitely live in
        # this process.
        return False
    # TaskInfo carries lease state as a nested LeaseInfo object.
    lease = getattr(task_info, "lease", None)
    owner = getattr(lease, "owner", None) if lease is not None else None
    owner = owner or ""
    # Owner matches ours but no local in-memory entry → previous
    # lifetime owned by THIS (agent, session) pair crashed; lease
    # is dead and eligible for reclaim.
    if owner and owner == this_lease_owner:
        return True
    # Foreign owner: this record belongs to a different agent OR a
    # different session. We MUST NOT reclaim it (FR-004a). Caller
    # observes the live-elsewhere conflict shape.
    if owner and owner != this_lease_owner:
        return False
    # No owner recorded — treat as dead since no live executor
    # claims it. (Empty owner happens for freshly-created records
    # before lease assignment.)
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
        "lease_last_refresh_monotonic",
        # Spec 019 FR-A-001 / FR-A-003 — latest known etag for this task.
        # Refreshed from every GET/CREATE/PATCH response. Used as
        # ``if_match`` on every subsequent PATCH.
        "current_etag",
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
        # ``asyncio.get_event_loop().time()`` value at the last successful
        # lease refresh -- updated by the renewal loop AND by every
        # payload PATCH that piggybacks lease ownership (see
        # ``_lease_ext_kwargs`` / ``_note_lease_refreshed``). The
        # renewal loop reads this to push out its next scheduled tick
        # so it doesn't issue a redundant heartbeat the moment after a
        # payload PATCH already refreshed the lease.
        self.lease_last_refresh_monotonic: float = 0.0
        # Spec 019 FR-A-001/-003 — latest known etag, refreshed on every
        # store interaction (create response, get response, update response).
        # Used as ``if_match`` on subsequent PATCHes.
        self.current_etag: str | None = None


class TaskManager:  # pylint: disable=too-many-instance-attributes
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
        # Spec 019 FR-A-006/-007 / C-WQ-1..3 — per-task write-queue
        # registry. A single asyncio.Lock per task_id serializes all
        # in-process PATCHes against that task so etag conflicts become
        # rare (only cross-process). Lazy-created on first use; dropped
        # in ``_active_tasks_pop`` (no leaks).
        # Spec 019 FR-A-001/-003 — also tracks the latest known etag
        # per task_id outside the _ActiveTask entry, so reclaim/scan
        # paths (which have no _ActiveTask yet) can still benefit.
        self._task_write_locks: dict[str, asyncio.Lock] = {}
        self._task_etag_cache: dict[str, str] = {}

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

        In hosted environments (``FOUNDRY_HOSTING_ENVIRONMENT`` is set),
        the HTTP-backed ``HostedTaskProvider`` is used unconditionally —
        the hosted task-storage API is what makes durable recovery,
        cross-instance lease handoff, and the platform's lease/readiness
        keep-alive path work.

        In non-hosted environments (local dev, tests), the
        ``LocalFileTaskProvider`` is used — file-backed under
        ``~/.durable-tasks/`` (or ``AGENTSERVER_DURABLE_TASKS_PATH`` if
        set). This keeps the local development loop self-contained with
        no external dependencies.

        :param config: The agent configuration.
        :type config: AgentConfig
        :return: The storage provider instance.
        :rtype: TaskProvider
        """
        import os  # pylint: disable=import-outside-toplevel

        if config.is_hosted:
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

            logger.info("Hosted environment detected; using HostedTaskProvider")
            return HostedTaskProvider(
                project_endpoint=config.project_endpoint,
                credential=DefaultAzureCredential(),
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
        :param opts: The task options (opts subset).
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
        try:
            return await self._provider.list(
                agent_name=agent_name,
                session_id=resolved_session,
                status=status,
                tag={_TAG_TASK_NAME: fn_name},
                source_type=_SOURCE_TYPE,
            )
        except _HostedConflict as exc:
            translated = _translate_hosted_conflict(exc)
            if translated is None:
                raise RuntimeError("Task list did not converge after retryable conflict") from exc
            raise translated from exc

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
            self._periodic_recovery_task = loop.create_task(self._periodic_recovery_loop())
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
                logger.warning("Periodic recovery scan iteration failed", exc_info=True)

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
            except (
                asyncio.CancelledError,
                Exception,
            ):  # pylint: disable=broad-exception-caught
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
            deadline = asyncio.get_event_loop().time() + self._shutdown_grace_seconds
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
            logger.info("TaskManager shutdown lease-expire interrupted; " "continuing to in-process task cancellation")

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
        # the per-task `store_input` knob is dropped). Spec 018: route the
        # input through the promotion helper so > 200 KiB inputs spill into
        # ``attachments["_input"]`` and ``payload["input"]`` becomes a ref
        # slot. The single create-PATCH carries payload + attachments
        # together (atomic).
        serialized_input = _serialize_input(input_val)
        input_mode, input_value = _resolve_input_storage(
            serialized_input,
            threshold_bytes=_INPUT_THRESHOLD_BYTES,
            key_for_attachment=_FUNCTION_INPUT_KEY,
            task_id=task_id,
        )
        payload: dict[str, Any] = {"input": input_value}
        attachments: dict[str, Any] | None = None
        if input_mode == "attachment":
            attachments = {_FUNCTION_INPUT_KEY: serialized_input}
        payload["metadata"] = {}
        # Spec 016 FR-023 (US7): persist a turn-start timestamp at every
        # turn-start boundary so the per-turn watchdog can compute
        # remaining = max(0, opts.timeout - (now - turn_started_at))
        # across crashes. Field name + format chosen per
        # conformance-gap-list.md §FR-023: top-level _turn_started_at,
        # ISO-8601 UTC with Z suffix.
        payload[_TURN_STARTED_AT_KEY] = _utc_now_iso()

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
        try:
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
                    attachments=attachments,
                    lease_owner=self._lease_owner,
                    lease_instance_id=self._instance_id,
                    lease_duration_seconds=_DEFAULT_LEASE_SECONDS,
                )
            )
        except _HostedConflict as exc:
            observed_status: str | None = None
            if exc._code == "task_already_exists":
                try:
                    observed = await self._provider.get(task_id)
                    observed_status = getattr(observed, "status", None) if observed else None
                except Exception:  # pylint: disable=broad-exception-caught
                    observed_status = None
            translated = _translate_hosted_conflict(exc, task_id=task_id, observed_status=observed_status)
            if translated is None:
                if exc._code == "lease_ownership_changed":
                    raise TaskConflictError(task_id, "in_progress") from exc
                raise RuntimeError(f"Task {task_id!r} create did not converge after retryable conflict") from exc
            raise translated from exc
        # Spec 019 FR-A-003 — track the etag from the create response
        # so the next PATCH carries it as if_match (FR-A-001).
        self._track_etag(task_id, getattr(task_info, "etag", None))

        logger.info("Created durable task %s (%s)", task_id, fn_name)

        # Register resume callback
        self._resume_callbacks[fn_name] = fn
        self._resume_opts[fn_name] = opts

        # Build context
        cancel_event = asyncio.Event()
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
            entry_mode=entry_mode,
            pending_count_provider=self._make_pending_count_provider(task_id),
            input_id=(initial_payload_extras or {}).get("_last_input_id"),
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
                info = await self._provider_get_tracked(task_id)
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
                last_refresh_provider=lambda tid=task_id: (
                    self._active_tasks[tid].lease_last_refresh_monotonic if tid in self._active_tasks else 0.0
                ),
                # Spec 019 FR-A-006 — heartbeat PATCH MUST be routed
                # through the per-task write queue so it serializes
                # with metadata flushes / steering / suspend / fail.
                update_via_queue=self._provider_update_locked,
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
        # lifecycle boundaries via ``_flush_all()``. There is no auto-
        # flush loop.

        return TaskRun(
            task_id=task_id,
            provider=self._provider,
            result_future=result_future,
            metadata=metadata,
            cancel_event=cancel_event,
            terminate_event=terminate_event,
            execution_task=execution_task,
            terminate_reason_ref=terminate_reason_ref,
            input_id=ctx.input_id,
        )

    # Spec 022 FR-049: TaskManager.handle_resume + _resume_route are removed.
    # Resume happens via .start()/.run() against a suspended task; the lifecycle
    # state machine in _lifecycle_start_inner handles the resume transition.

    async def get_active_run(self, task_id: str) -> TaskRun[Any] | None:  # pylint: disable=too-many-return-statements
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
                terminate_event=active.terminate_event,
                execution_task=active.execution_task,
                input_id=getattr(active.context, "input_id", None),
            )

        # Spec 016 FR-005: consult the store for tasks not active in
        # this process. Reads are not rejected for orphan sandboxes
        # per the spec's assumptions.
        try:
            task_info = await self._provider_get_tracked(task_id)
        except _HostedConflict as exc:
            translated = _translate_hosted_conflict(exc, task_id=task_id)
            if translated is None or getattr(translated, "current_status", None) == "in_progress":
                return None
            raise translated from exc
        except TransportClassifiedError as exc:
            if _is_evicted(exc):
                # Even reads classified as evicted (unexpected per
                # assumption but defensive) map to "not active".
                return None
            raise
        if task_info is None or task_info.status in (
            "completed",
            "suspended",
            "pending",
        ):
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
            except _HostedConflict as exc:
                translated = _translate_hosted_conflict(exc, task_id=task_id)
                if translated is None or getattr(translated, "current_status", None) == "in_progress":
                    logger.warning(
                        "get_active_run: reclaim of %s lost a provider race; "
                        "returning None (same shape as 'not active here')",
                        task_id,
                    )
                    return None
                raise translated from exc
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
        await self._provider_update_locked(
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
        :return: A TaskRun handle.
        :rtype: TaskRun[Any]
        """
        task_id = task_info.id
        resolved_opts = opts or TaskOptions(name=fn_name, ephemeral=False)
        lease_duration = _DEFAULT_LEASE_SECONDS

        # Spec 016 FR-023 (US7): write a new turn-start timestamp for
        # every NEW turn boundary — fresh entry from suspended/pending
        # and developer-initiated resume. EXCEPTION: do NOT re-stamp
        # on recovery (entry_mode == "recovered") so the watchdog's
        # remaining-budget computation honors the original turn-start.
        turn_start_payload: dict[str, Any] = {}
        if entry_mode != "recovered":
            turn_start_payload[_TURN_STARTED_AT_KEY] = _utc_now_iso()

        # Spec 019 FR-C-004 / SC-7 / C-OUT-4 — every suspended →
        # in_progress transition MUST clear the prior turn's output.
        # Recovery (entry_mode == "recovered") does NOT re-stamp turn-
        # start AND does NOT clear output — it's a continuation of the
        # SAME turn, not a new one.
        resume_clears_output = entry_mode != "recovered" and task_info.status == "suspended"
        if resume_clears_output:
            turn_start_payload["output"] = None
        # Decide whether this PATCH is actually necessary, and whether
        # the status field belongs in it.
        #
        # On the recovery path the immediately-prior ``_reclaim_one``
        # call already wrote the new lease against the stale
        # in_progress task, AND we explicitly do NOT re-stamp
        # ``_turn_started_at`` on recovery (FR-023 exception above)
        # AND the existing task status is already ``in_progress``.
        # In that case the PATCH would re-write the same status +
        # same lease + an empty payload — a full network round-trip
        # against the same record, with no observable change. Skip
        # the call (and the follow-up re-fetch) entirely.
        #
        # For other entries (suspended/pending/queued -> in_progress)
        # the PATCH is required for the status flip and/or turn-start
        # write. The ``status`` field is only sent when the current
        # status differs from in_progress, so we never re-write the
        # same status onto a record that already carries it.
        needs_status_flip = task_info.status != "in_progress"
        needs_turn_start_write = bool(turn_start_payload)
        if not needs_status_flip and not needs_turn_start_write:
            # No-op PATCH would be sent — skip it. The reclaim has
            # already established our lease; nothing else to write.
            # The in-memory ``task_info`` already reflects the
            # post-reclaim state we observed when ``_reclaim_one``
            # returned, so the re-fetch is also unnecessary.
            updated_info: TaskInfo | None = task_info
        else:
            # PATCH returns the full updated TaskInfo -- no follow-up
            # GET needed. (Saves one network round-trip per call.)
            # When this is a resume of a suspended task, the same PATCH
            # also deletes any prior _output attachment.
            attachments_for_resume: dict[str, Any] | None = None
            if resume_clears_output:
                attachments_for_resume = {_OUTPUT_KEY: None}
            updated_info = await self._provider_update_locked(
                task_id,
                TaskPatchRequest(
                    status="in_progress" if needs_status_flip else None,
                    lease_owner=self._lease_owner,
                    lease_instance_id=self._instance_id,
                    lease_duration_seconds=lease_duration,
                    payload=turn_start_payload if turn_start_payload else None,
                    attachments=attachments_for_resume,
                ),
            )
            if updated_info is None:
                raise TaskNotFound(task_id)
        task_info = updated_info

        # Resolve input: prefer caller-provided, fall back to persisted.
        # Spec 018: ``payload["input"]`` may be a raw inline value OR a
        # ref slot pointing into ``task_info.attachments``. Route the
        # read through ``_read_input_value`` to handle both shapes
        # uniformly.
        if input_val is not None:
            resolved_input = input_val
        elif task_info.payload and "input" in task_info.payload:
            raw_input = _read_input_value(task_info.payload["input"], task_info.attachments)
            if input_type is not None:
                resolved_input = _deserialize_input(raw_input, input_type)
            else:
                resolved_input = raw_input
        else:
            resolved_input = None

        # Build context for execution
        cancel_event = asyncio.Event()
        # Spec 015 Phase 5 (FR-003): restore ALL namespaces, not just default.
        # ``from_payload`` decodes ``payload["metadata"]`` into the default
        # namespace and every ``payload["metadata:<name>"]`` into its named
        # sibling, all sharing the same flush_callback so the framework can
        # _flush_all() at lifecycle boundaries.
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
        if entry_mode == "recovered" and steering.get("drain_in_progress") and "active_input" in steering:
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
        persisted_retry_attempt = (task_info.payload or {}).get("_retry_attempt") or 0

        ctx: TaskContext[Any] = TaskContext(
            task_id=task_id,
            session_id=task_info.session_id,
            input=resolved_input,
            metadata=metadata,
            retry_attempt=persisted_retry_attempt,
            recovery_count=lease_gen,
            cancel=cancel_event,
            shutdown=self._shutdown_event,
            entry_mode=entry_mode,
            is_steered_turn=is_steered_turn,
            pending_count_provider=self._make_pending_count_provider(task_id),
            input_id=(task_info.payload or {}).get("_last_input_id"),
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
                info = await self._provider_get_tracked(task_id)
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
                last_refresh_provider=lambda tid=task_id: (
                    self._active_tasks[tid].lease_last_refresh_monotonic if tid in self._active_tasks else 0.0
                ),
                # Spec 019 FR-A-006 — route through the per-task write queue.
                update_via_queue=self._provider_update_locked,
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
        *,
        remaining_seconds: float | None = None,
    ) -> None:
        """Spec 016 FR-025 / FR-026 (US7): per-turn timeout watchdog.

        Cooperative-only. On firing, sets ``ctx.timeout_exceeded = True``
        then sets ``cancel_event`` and exits. Does NOT cancel the lease
        renewal or force-stop the handler. An ignoring handler runs
        until process death or external :meth:`TaskRun.cancel`.

        :param timeout_seconds: Total per-turn timeout budget (used as
            the clock-skew clamp ceiling).
        :type timeout_seconds: float
        :param cancel_event: Event to set for cooperative cancel.
        :type cancel_event: asyncio.Event
        :param ctx: TaskContext to set ``timeout_exceeded`` on BEFORE
            ``cancel_event`` (FR-018 ordering invariant).
        :type ctx: TaskContext[Any] | None
        :keyword remaining_seconds: Optional override for "time left in
            this turn" — used on recovery to honor the persisted
            turn-start timestamp per FR-023. Clamped to
            ``[0, timeout_seconds]`` for clock-skew safety (FR-023).
            When ``None``, the watchdog uses ``timeout_seconds`` directly
            (fresh-entry / drain-re-entry case).
        :paramtype remaining_seconds: float | None
        """
        if remaining_seconds is None:
            sleep_for = timeout_seconds
        else:
            # FR-023: clamp to [0, timeout_seconds] in both directions.
            sleep_for = max(0.0, min(remaining_seconds, timeout_seconds))

        # FR-025: if remaining == 0 (recovered watchdog with budget
        # already exceeded), fire IMMEDIATELY so the recovered handler
        # sees the cause from its first checkpoint.
        if sleep_for > 0:
            await asyncio.sleep(sleep_for)
        # Spec 016 FR-018 ordering: cause boolean FIRST, then cancel.
        if ctx is not None:
            ctx.timeout_exceeded = True
        cancel_event.set()
        logger.info(
            "Timeout watchdog fired cooperative cancel (slept %.3fs of "
            "%.3fs budget; cooperative-only — handler must check "
            "ctx.cancel.is_set() and ctx.timeout_exceeded to wind down)",
            sleep_for,
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

        # Spec 016 FR-023/FR-024 (US7): per-turn watchdog with durable
        # budget. Read the persisted _turn_started_at to compute the
        # remaining budget for THIS turn. On recovery this gives the
        # correct "time left since the original turn started"; on fresh
        # entry / drain re-entry the timestamp was just written so
        # remaining ≈ full budget.
        watchdog_task: asyncio.Task[None] | None = None
        if opts.timeout is not None:
            timeout_seconds = opts.timeout.total_seconds()
            remaining = await self._compute_remaining_for_watchdog(task_id, timeout_seconds, ctx)
            watchdog_task = asyncio.create_task(
                self._timeout_watchdog(
                    timeout_seconds=timeout_seconds,
                    cancel_event=ctx.cancel,
                    ctx=ctx,
                    remaining_seconds=remaining,
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

    async def _compute_remaining_for_watchdog(
        self,
        task_id: str,
        timeout_seconds: float,
        ctx: "TaskContext[Any]",
    ) -> float:
        """Spec 016 FR-023 (US7): compute the remaining per-turn budget.

        Reads the persisted ``_turn_started_at`` for ``task_id`` and
        returns ``max(0, timeout_seconds - (now - turn_started_at))``
        clamped to ``[0, timeout_seconds]``. If the timestamp is
        missing or unparseable (e.g., a pre-spec-016 record during
        rollout), returns ``timeout_seconds`` so the watchdog spawns
        with a fresh budget (graceful degradation).

        FR-025 immediate-fire-on-recovery: if remaining == 0, also
        pre-set ``ctx.timeout_exceeded = True`` and ``ctx.cancel`` so
        the recovered handler sees the cause from its first checkpoint.

        :param task_id: The task identifier.
        :type task_id: str
        :param timeout_seconds: The per-turn budget configured on the
            decorator (also the clock-skew clamp ceiling).
        :type timeout_seconds: float
        :param ctx: TaskContext used to surface the recovered cause when
            the remaining budget is zero.
        :type ctx: TaskContext[Any]
        :return: Remaining seconds clamped to ``[0, timeout_seconds]``.
        :rtype: float
        """
        try:
            task_info = await self._provider_get_tracked(task_id)
        except Exception:  # pylint: disable=broad-exception-caught
            return timeout_seconds
        if task_info is None or not task_info.payload:
            return timeout_seconds
        started_ts = _parse_turn_started_at(task_info.payload.get(_TURN_STARTED_AT_KEY))
        if started_ts is None:
            return timeout_seconds
        import time  # pylint: disable=import-outside-toplevel

        elapsed = time.time() - started_ts
        # FR-023 clock-skew clamping: clamp to [0, timeout_seconds] in
        # both directions (backward skew → elapsed negative → remaining
        # > timeout; forward skew → elapsed huge → remaining < 0).
        remaining = max(0.0, min(timeout_seconds - elapsed, timeout_seconds))

        # FR-025 immediate-fire: if recovered watchdog computes
        # remaining == 0, pre-set the cause boolean + cancel before
        # the handler even runs its first checkpoint.
        if remaining == 0.0:
            ctx.timeout_exceeded = True
            ctx.cancel.set()
        return remaining

    async def _execute_task_loop(  # pylint: disable=too-many-statements,too-many-branches,too-many-nested-blocks,unused-argument
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
        :keyword terminate_event: Optional terminate event (currently unused).
        :paramtype terminate_event: asyncio.Event | None
        :keyword terminate_reason_ref: Mutable ref for terminate reason
            (currently unused).
        :paramtype terminate_reason_ref: list[str | None] | None
        """
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

                # Spec 016 FR-027 (US8): the handler returned the
                # _ExitForRecovery sentinel via ``ctx.exit_for_recovery()``.
                # Flush metadata, release the lease, leave the stored
                # status as 'in_progress' (do NOT write terminal),
                # preserve queued steering inputs (FR-028), and signal
                # awaiters with TaskCancelled.
                from ._context import (
                    _ExitForRecovery as _ExitSentinel,
                )  # pylint: disable=import-outside-toplevel

                if isinstance(result, _ExitSentinel):
                    # Spec 022 FR-039 / FR-058 — `ctx.exit_for_recovery()`
                    # raises `TaskDeferred` (NOT `TaskCancelled`). The task
                    # stays `in_progress`; the recovery scanner re-invokes
                    # the handler in the next process lifetime.
                    from ._exceptions import (  # pylint: disable=import-outside-toplevel
                        TaskCancelled,
                        TaskDeferred,
                    )

                    renewal_cancel.set()
                    # (a) Flush metadata (FR-015 auto-flush).
                    await ctx.metadata._flush_all()
                    # (b) Release the lease: clear ownership claim. The
                    #     CAS write may fail with eviction — in that
                    #     case the local cleanup sequence already
                    #     handled it; just log and proceed.
                    try:
                        await self._provider_update_locked(
                            task_id,
                            TaskPatchRequest(
                                lease_owner="",
                                lease_instance_id="",
                                lease_duration_seconds=0,
                            ),
                        )
                    except _HostedConflict as exc:
                        translated = _translate_hosted_conflict(exc, task_id=task_id)
                        logger.warning(
                            "exit_for_recovery: lease release for task %s "
                            "failed with provider conflict %s; the next "
                            "process startup recovery will reclaim",
                            task_id,
                            type(translated).__name__ if translated else "retryable",
                            exc_info=True,
                        )
                    except TransportClassifiedError as exc:
                        if not _is_evicted(exc):
                            logger.warning(
                                "exit_for_recovery: lease release for task "
                                "%s failed with classification=%s; the next "
                                "process startup recovery will reclaim",
                                task_id,
                                getattr(exc, "classification", None),
                            )
                    except Exception:  # pylint: disable=broad-exception-caught
                        logger.warning(
                            "exit_for_recovery: lease release for task %s "
                            "failed; the next process startup recovery will "
                            "reclaim",
                            task_id,
                            exc_info=True,
                        )
                    # (c) Do NOT write a terminal record — status MUST
                    #     remain 'in_progress' so the recovery scan picks
                    #     it up next process start.
                    # (d) Signal awaiters with TaskDeferred per spec 022
                    #     FR-039 / FR-058 (NOT TaskCancelled — the task
                    #     is deferring to next lifetime, not terminating).
                    if not current_result_future.done():
                        current_result_future.set_exception(TaskDeferred())
                    # (e) Queued steerers (per FR-028): preserved in
                    #     persisted state — already untouched here, so
                    #     no action needed.
                    break

                if isinstance(result, Suspended):
                    # Spec 016 FR-011 (US5): the current turn's caller's
                    # result_future MUST be set to TaskResult(status="suspended",
                    # output=X, suspension_reason=R) UNCONDITIONALLY — whether
                    # or not a steering input is queued. The handler's emitted
                    # output is delivered unchanged. The framework auto-flushes
                    # metadata at this terminal-of-turn boundary (FR-015).
                    renewal_cancel.set()
                    await ctx.metadata._flush_all()
                    try:
                        await self._handle_suspend(
                            task_id=task_id,
                            reason=result.reason,
                            output=result.output,
                            metadata=ctx.metadata,
                            opts=opts,
                        )
                    except OutputTooLarge as exc:
                        # Spec 019 FR-C-006 / SC-9 — surface OutputTooLarge
                        # to the caller directly, NOT wrapped in TaskFailed.
                        # Mirrors the success-arm handling above. The
                        # handler called ctx.suspend(output=...) with a
                        # value over the 2 MB cap; this is a developer-
                        # facing precondition violation, not a handler bug.
                        if not current_result_future.done():
                            current_result_future.set_exception(exc)
                        _resolve_queued_steerers_on_terminal(
                            self._pending_steering_futures,
                            task_id,
                            current_status="failed",
                        )
                        break
                    if not current_result_future.done():
                        # Spec 022 FR-052: resolve with raw output (the value
                        # the handler emitted via ctx.suspend(output=...)).
                        current_result_future.set_result(result.output)

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
                            if active and active.result_future is not current_result_future:
                                current_result_future = active.result_future
                            continue
                else:
                    # Spec 022 FR-018 / FR-052: TaskResult deleted; handler
                    # returns raw output directly (no wrapper). No guard needed.

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
                    await ctx.metadata._flush_all()
                    try:
                        completed = await self._handle_success(
                            task_id=task_id,
                            result=result,
                            metadata=ctx.metadata,
                            opts=opts,
                        )
                    except TaskConflictError as exc:
                        if not current_result_future.done():
                            current_result_future.set_exception(exc)
                        _resolve_queued_steerers_on_terminal(
                            self._pending_steering_futures,
                            task_id,
                            current_status=exc.current_status,
                        )
                        break
                    except OutputTooLarge as exc:
                        # Spec 019 FR-C-006 / SC-9 — surface OutputTooLarge
                        # to the caller directly, NOT wrapped in TaskFailed.
                        # The handler succeeded; the framework's persistence
                        # step rejected the output as too large. This is a
                        # developer-facing precondition violation, not a
                        # handler bug.
                        if not current_result_future.done():
                            current_result_future.set_exception(exc)
                        _resolve_queued_steerers_on_terminal(
                            self._pending_steering_futures,
                            task_id,
                            current_status="failed",
                        )
                        break
                    # Spec 016 FR-012 (US5): set the current turn's caller's
                    # result_future to the completion outcome FIRST, then
                    # resolve any queued steerers with TaskConflictError
                    # (since the task has now terminated). The handler's
                    # return value is delivered unchanged to the current
                    # caller; the queued steerers see the "task is busy /
                    # terminal" shape per Invariant 1.
                    is_multi_turn_success = getattr(opts, "_is_multi_turn", False)
                    if not current_result_future.done():
                        if is_multi_turn_success:
                            # Spec 022 FR-007/052 — multi-turn chains return
                            # the raw Output unwrapped; chain stays alive.
                            current_result_future.set_result(result)
                        else:
                            # Spec 022 FR-052 — one-shot also returns raw Output.
                            current_result_future.set_result(result)
                    if not is_multi_turn_success:
                        # Spec 016 FR-012: legacy one-shot path — queued
                        # steerers get TaskConflictError on terminal completion.
                        _resolve_queued_steerers_on_terminal(
                            self._pending_steering_futures,
                            task_id,
                            current_status="completed",
                        )
                    else:
                        # Spec 022 FR-013 — multi-turn path: try drain
                        # promotes queued head as a new turn.
                        try:
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
                                if active and active.result_future is not current_result_future:
                                    current_result_future = active.result_future
                                continue
                        except Exception:  # noqa: BLE001
                            logger.warning(
                                "Failed to drain steering queue after multi-turn success for task %s",
                                task_id,
                                exc_info=True,
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
                await ctx.metadata._flush_all()
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

                    current_result_future.set_exception(TaskCancelled())
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
                        # Spec 022 FR-027: NO interim error PATCH between retries.
                        # Only the _retry_attempt counter is persisted across retries.
                        await self._provider_update_locked(
                            task_id,
                            TaskPatchRequest(
                                payload={"_retry_attempt": attempt + 1},
                            ),
                        )
                    except Exception:  # pylint: disable=broad-exception-caught
                        logger.debug("Failed to update _retry_attempt counter", exc_info=True)
                    await asyncio.sleep(delay)
                    attempt += 1
                    continue

                # Exhausted or non-retryable — terminal failure
                renewal_cancel.set()
                await ctx.metadata._flush_all()

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
                # Spec 022 FR-012 / FR-053 step 5 — caller's future resolution:
                # CancelledError → bare TaskCancelled() else TaskFailed.
                is_multi_turn_failure = getattr(opts, "_is_multi_turn", False)
                if not current_result_future.done():
                    if isinstance(exc, asyncio.CancelledError):
                        # Spec 022 FR-012/077 — bare TaskCancelled (no fields).
                        current_result_future.set_exception(TaskCancelled())
                    else:
                        current_result_future.set_exception(TaskFailed(task_id, error_dict))
                    # Spec 022 FR-015 — discard callback so "Future exception
                    # was never retrieved" doesn't fire when no caller awaits
                    # (multi-turn: caller may have already moved on / GC'd).
                    if is_multi_turn_failure:
                        def _discard(fut: asyncio.Future[Any]) -> None:
                            try:
                                fut.exception()  # retrieve to silence asyncio
                            except Exception:  # noqa: BLE001
                                pass
                        current_result_future.add_done_callback(_discard)
                # Spec 016 FR-012 (US5) — legacy one-shot path: queued steerers
                # see TaskConflictError on terminal failure since the task is done.
                # Spec 022 FR-013 — multi-turn path: queued steerers PROMOTE
                # (chain stays alive); do NOT reject them here.
                if not is_multi_turn_failure:
                    _resolve_queued_steerers_on_terminal(
                        self._pending_steering_futures,
                        task_id,
                        current_status="failed",
                    )
                else:
                    # Multi-turn: chain stays in suspended; try drain steering
                    # queue per FR-013. Promoted turn dispatches with
                    # ctx.entry_mode="resumed" per the existing _try_drain_steering
                    # mechanics. If no queued steerers, chain remains suspended.
                    try:
                        new_ctx = await self._try_drain_steering(
                            task_id=task_id,
                            ctx=ctx,
                            opts=opts,
                            result_future=current_result_future,
                        )
                        if new_ctx is not None:
                            # Queued head promoted; new turn dispatching.
                            # _execute_task continues into next attempt with new ctx.
                            ctx = new_ctx
                            attempt = 0
                            # Refresh current_result_future from rotated
                            # active.result_future per FR-013 / FR-014.
                            active = self._active_tasks.get(task_id)
                            if active and active.result_future is not current_result_future:
                                current_result_future = active.result_future
                            continue
                    except Exception:  # noqa: BLE001
                        logger.warning(
                            "Failed to drain steering queue after multi-turn raise for task %s",
                            task_id,
                            exc_info=True,
                        )
                break

        self._active_tasks_pop(task_id)

    async def _try_drain_steering(  # pylint: disable=too-many-branches,too-many-statements,too-many-locals
        self,
        *,
        task_id: str,
        ctx: TaskContext[Any],
        opts: TaskOptions,
        result_future: asyncio.Future[Any],
        partial_output: Any | None = None,
        _conflict_attempt: int = 0,
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
        :keyword _conflict_attempt: Internal recursion-depth counter
            for etag-conflict retries. Bounded so the hosted task
            store's etag-comparator pre-fix behaviour cannot loop
            forever.
        :return: New context for the drained generation, or None.
        """
        task_info = await self._provider_get_tracked(task_id)
        if task_info is None:
            return None

        payload = dict(task_info.payload) if task_info.payload else {}
        steering = dict(payload.get("_steering", {}))
        pending: list[Any] = list(steering.get("pending_inputs", []))

        if not pending:
            return None

        # Pop the next input from the queue. Spec 018: the entry may be
        # either a raw inline value (≤ 20 KiB at append) or a ref slot
        # pointing into ``task_info.attachments``. Resolve uniformly via
        # ``_read_input_value``; if it was a ref, the same drain PATCH
        # MUST also delete the attachment (C-9 / FR-003d).
        next_entry = pending.pop(0)
        attachments_patch: dict[str, Any] = {}
        if _is_ref(next_entry):
            attachments_patch[_ref_key(next_entry)] = None
        next_input_raw = _read_input_value(next_entry, task_info.attachments)

        # Update steering state. (Spec 015 Phase 3 FR-006: previous_input is
        # no longer mirrored into _steering; only the active input + queue
        # state need to survive a crash mid-drain.)
        steering["active_input"] = next_input_raw
        steering["pending_inputs"] = pending
        # Spec 016 FR-021 + gap-list §FR-021-internal (US6): internal
        # _steering["generation"] writes removed. The drain transition
        # IS the generation advance — no separate counter needed.
        steering["cancel_requested"] = len(pending) > 0
        steering["drain_in_progress"] = True
        # Spec 016 FR-023 (US7): the steering drain re-entry is a NEW
        # turn-start boundary — write a fresh _turn_started_at so the
        # respawned watchdog computes a full per-turn budget.
        payload[_TURN_STARTED_AT_KEY] = _utc_now_iso()

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
        # Spec 019 FR-C-004 / C-OUT-5 — drain Phase 1 MUST clear the
        # prior turn's output in the same co-PATCH so the resumed-by-
        # drain turn never inherits stale output. Always set explicit
        # null + delete the _output attachment regardless of whether
        # one existed (delete-of-absent-key is a no-op on both providers).
        payload["output"] = None
        attachments_patch[_OUTPUT_KEY] = None

        try:
            etag = getattr(task_info, "etag", None) or None
            await self._provider_update_locked(
                task_id,
                TaskPatchRequest(
                    payload=payload,
                    attachments=attachments_patch,
                    if_match=etag,
                    **self._lease_ext_kwargs(task_id),
                ),
            )
        except _HostedConflict as exc:
            translated = _translate_hosted_conflict(exc, task_id=task_id)
            if translated is None:
                if _conflict_attempt >= 5:
                    raise RuntimeError(
                        f"Steering drain for {task_id!r} did not converge " "after 5 etag-conflict retries"
                    ) from exc
                logger.warning(
                    "Provider write conflict during steering drain for %s, retrying " "(attempt %d)",
                    task_id,
                    _conflict_attempt + 1,
                )
                return await self._try_drain_steering(
                    task_id=task_id,
                    ctx=ctx,
                    opts=opts,
                    _conflict_attempt=_conflict_attempt + 1,
                )
            raise translated from exc
        except (ValueError, TransportClassifiedError) as exc:
            if isinstance(exc, TransportClassifiedError) and getattr(exc, "classification", None) != "conflict":
                raise
            if _conflict_attempt >= 5:
                raise RuntimeError(
                    f"Steering drain for {task_id!r} did not converge " "after 5 etag-conflict retries"
                ) from exc
            logger.warning(
                "Etag conflict during steering drain for %s, retrying " "(attempt %d)",
                task_id,
                _conflict_attempt + 1,
            )
            return await self._try_drain_steering(
                task_id=task_id,
                ctx=ctx,
                opts=opts,
                result_future=result_future,
                partial_output=partial_output,
                _conflict_attempt=_conflict_attempt + 1,
            )

        # Pop and bind the next pending steering future (if any)
        new_future: asyncio.Future[Any] | None = None
        steering_futures = self._pending_steering_futures.get(task_id, [])
        if steering_futures:
            new_future = steering_futures.pop(0)

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
            entry_mode="resumed",
            is_steered_turn=True,
            pending_count_provider=self._make_pending_count_provider(task_id),
            input_id=(task_info.payload or {}).get("_last_input_id"),
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
            await self._provider_update_locked(
                task_id,
                TaskPatchRequest(
                    payload=payload,
                    **self._lease_ext_kwargs(task_id),
                ),
            )
        except Exception:  # pylint: disable=broad-exception-caught
            logger.debug("Failed to clear drain_in_progress for %s", task_id)

        logger.info(
            "Steering drain: task %s drained next input",
            task_id,
        )
        return new_ctx

    async def _handle_multi_turn_success(
        self,
        *,
        task_id: str,
        metadata: TaskMetadata,
        opts: TaskOptions,
    ) -> bool:
        """Multi-turn return handler (spec 022 FR-007/025/028).

        Per spec 022:
        - Multi-turn ``return X`` is implicit suspend. Chain transitions to
          ``suspended`` (NOT ``completed``) so it accepts the next input.
        - NO ``payload["output"]`` is written (FR-025).
        - ``payload["input"]`` cleared at the transition (FR-028).
        - ``payload["_retry_attempt"]`` cleared too (FR-030).
        - ``payload["_last_input_id"]`` preserved (FR-029) for the
          ``if_last_input_id`` precondition.
        - ``suspension_reason="run_completion"`` stamped internally.

        Returns True (terminal write succeeded). False is reserved for
        the legacy etag-conflict-retry-drain pattern; the multi-turn
        path raises TaskConflictError on 412 instead.
        """
        # Auto-flush metadata BEFORE the chain PATCH (FR-045).
        try:
            await metadata._flush_all()  # noqa: SLF001 — framework-internal fence
        except Exception:  # noqa: BLE001
            logger.warning(
                "Failed to auto-flush metadata before multi-turn success PATCH for task %s",
                task_id,
                exc_info=True,
            )

        try:
            await self._terminal_write_locked(
                task_id,
                TaskPatchRequest(
                    status="suspended",
                    suspension_reason="run_completion",
                    payload={
                        "metadata": metadata.to_dict(),
                        "input": None,            # FR-028
                        "_retry_attempt": None,   # FR-030
                        # NO "output" (FR-025), NO "error" (FR-027)
                    },
                ),
            )
        except TaskConflictError:
            raise
        except _HostedConflict as hosted_exc:
            translated = _translate_hosted_conflict(hosted_exc, task_id=task_id)
            if translated is None:
                if hosted_exc._code == "lease_ownership_changed":
                    raise TaskConflictError(task_id, "in_progress") from hosted_exc
                raise EtagConflict(task_id) from hosted_exc
            raise translated from hosted_exc
        except TransportClassifiedError as transport_exc:
            if _is_evicted(transport_exc):
                logger.warning(
                    "Eviction on multi-turn return PATCH for task %s — "
                    "signalling awaiters with TaskConflictError",
                    task_id,
                )
                raise TaskConflictError(task_id, "in_progress") from transport_exc
            raise
        return True

    async def _handle_success(
        self,
        *,
        task_id: str,
        result: Any,
        metadata: TaskMetadata,
        opts: TaskOptions,
    ) -> bool:
        """Handle successful task completion.

        Spec 022 FR-007 / FR-025 / FR-028: multi-turn handlers (decorated
        with @multi_turn_task — TaskOptions._is_multi_turn=True) treat
        ``return X`` as the implicit-suspend signal. The framework
        transitions the chain to ``suspended`` with
        ``suspension_reason="run_completion"``, NO ``payload["output"]``
        is written (FR-025), and ``payload["input"]`` is cleared (FR-028).
        The caller's ``.result()`` future will be resolved with ``X``
        directly by the caller path (preserving the return value).

        Legacy one-shot (ephemeral) and non-ephemeral-non-multi-turn paths
        keep their existing behavior during the transition window.

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
        # Spec 022 FR-007/025/028 — multi-turn success → suspended (NOT completed),
        # no payload['output'] written, payload['input'] cleared.
        is_multi_turn = getattr(opts, "_is_multi_turn", False)
        if is_multi_turn:
            return await self._handle_multi_turn_success(
                task_id=task_id,
                metadata=metadata,
                opts=opts,
            )

        if opts.ephemeral:
            # Delete immediately — no intermediate PATCH
            try:
                await self._provider.delete(task_id, force=True)
            except Exception:  # pylint: disable=broad-exception-caught
                logger.warning("Failed to delete ephemeral task %s", task_id, exc_info=True)
        else:
            # Spec 019 FR-C-005 — output is ALWAYS persisted via the
            # _output attachment (never inline in payload). FR-C-006
            # caps it at 2 MB serialized; over-cap raises OutputTooLarge
            # BEFORE the PATCH lands.
            payload_patch, attachments_patch = _legacy_output_terminal_patch(
                task_id=task_id,
                metadata_dict=metadata.to_dict(),
                output=result,
            )

            # Spec 019 FR-A-008 — terminal write follows RE-READ-AND-DECIDE
            # uniformly for both steerable and non-steerable tasks. The
            # pre-019 steerable path returned False on 412 so the outer
            # drain loop would re-check for steers; with the spec-019
            # rule, queued steerers learn via TaskConflictError(completed)
            # per the C-STR-6 cross-process steering-after-terminate
            # contract, and the terminal write proceeds uniformly.
            try:
                await self._terminal_write_locked(
                    task_id,
                    TaskPatchRequest(
                        status="completed",
                        payload=payload_patch,
                        attachments=attachments_patch,
                    ),
                )
            except TaskConflictError:
                # 412 RE-READ decided ABANDON.
                raise
            except _AttachmentTooLarge as exc:
                # FR-D-004 — translate to OutputTooLarge for the developer.
                raise _remap_attachment_error(exc) from exc
            except _HostedConflict as exc:
                translated = _translate_hosted_conflict(exc, task_id=task_id)
                if translated is None:
                    if exc._code == "lease_ownership_changed":
                        raise TaskConflictError(task_id, "in_progress") from exc
                    raise EtagConflict(task_id) from exc
                raise translated from exc
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

    async def _handle_multi_turn_failure(
        self,
        *,
        task_id: str,
        exc: Exception,
        metadata: TaskMetadata,
        opts: TaskOptions,
        error_dict: dict[str, Any],
    ) -> None:
        """Multi-turn raise handler (spec 022 FR-010/011/027/053).

        Per spec 022 FR-053 7-step ordering:
        1. (caller) Run the failure handler (this method).
        2. Auto-flush ctx.metadata BEFORE the chain-PATCH (load-bearing per FR-045).
        3. Clear payload["input"] and payload["_retry_attempt"].
        4. PATCH chain record to ``suspended`` (NOT ``completed``) with
           ``suspension_reason="run_completion"``. No ``payload["error"]``
           is written (FR-027). ``payload["_last_input_id"]`` MUST be
           preserved. Steering queue MUST be preserved.
        5. (caller) Resolve current caller's .result() future per FR-012:
           ``CancelledError`` → bare ``TaskCancelled()`` else
           ``TaskFailed(error_dict)``.
        6. (caller) If queued steerers exist, promote head per FR-013.
        7. (caller) Else leave chain in ``suspended`` awaiting future
           ``.run()`` / ``.start()``.

        Steps 5/6/7 are handled by the caller (`_execute_task`) after this
        method returns; this method owns steps 2/3/4.
        """
        # Step 2: auto-flush metadata BEFORE the chain-PATCH (FR-045).
        try:
            await metadata._flush_all()  # noqa: SLF001 — framework-internal fence
        except Exception:  # noqa: BLE001
            logger.warning(
                "Failed to auto-flush metadata before multi-turn failure PATCH for task %s",
                task_id,
                exc_info=True,
            )

        # Step 3 + 4: PATCH to suspended (NOT completed); clear input + _retry_attempt;
        # NO payload["error"] written; _last_input_id preserved.
        try:
            await self._terminal_write_locked(
                task_id,
                TaskPatchRequest(
                    status="suspended",
                    suspension_reason="run_completion",
                    payload={
                        "metadata": metadata.to_dict(),
                        "input": None,            # FR-028
                        "_retry_attempt": None,   # FR-030
                        # NO "output" (FR-025), NO "error" (FR-027)
                    },
                ),
            )
        except TaskConflictError:
            # 412 RE-READ decided ABANDON; propagate so the active caller
            # receives the eviction-shape exception.
            raise
        except _HostedConflict as hosted_exc:
            translated = _translate_hosted_conflict(hosted_exc, task_id=task_id)
            if translated is None:
                if hosted_exc._code == "lease_ownership_changed":
                    raise TaskConflictError(task_id, "in_progress") from hosted_exc
                raise EtagConflict(task_id) from hosted_exc
            raise translated from hosted_exc
        except TransportClassifiedError as transport_exc:
            if _is_evicted(transport_exc):
                logger.warning(
                    "Eviction on multi-turn raise PATCH for task %s — "
                    "signalling awaiters with TaskConflictError",
                    task_id,
                )
                raise TaskConflictError(task_id, "in_progress") from transport_exc
            raise
        except Exception:  # noqa: BLE001
            logger.warning(
                "Failed to PATCH multi-turn suspended-on-raise for task %s",
                task_id,
                exc_info=True,
            )
        # Spec 022 FR-015 — structured failure log/telemetry for every handler
        # failure, independent of listener presence. Logged at ERROR per
        # FR-015 (the chain has just lost a turn).
        active = self._active_tasks.get(task_id)
        input_id = None
        if active is not None:
            input_id = getattr(active.context, "input_id", None)
        logger.error(
            "durable_task_handler_failure: task=%s exc_type=%s",
            task_id,
            type(exc).__name__,
            extra={
                "event": "durable_task_handler_failure",
                "event_name": "durable_task_handler_failure",
                "task_id": task_id,
                "input_id": input_id,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "primitive": "multi_turn_task",
            },
        )

    async def _handle_failure(
        self,
        *,
        task_id: str,
        exc: Exception,
        metadata: TaskMetadata,
        opts: TaskOptions,
    ) -> None:
        """Handle task failure.

        Spec 022 FR-010 / FR-011 / FR-053 — multi-turn handlers (decorated
        with @multi_turn_task — TaskOptions._is_multi_turn=True) transition
        to ``suspended`` (chain stays alive) on raise, NOT ``completed``.
        Per FR-027 NO ``payload["error"]`` is written for multi-turn
        failures. Per FR-028/030 ``payload["input"]`` and
        ``payload["_retry_attempt"]`` are cleared.

        Legacy one-shot (ephemeral) and non-ephemeral-non-multi-turn paths
        keep their existing behavior during the transition window.

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

        # Spec 022 FR-010/011/027/053 — multi-turn raise → suspended (NOT completed).
        # Auto-flush metadata BEFORE the chain-PATCH (step 2 of FR-053).
        is_multi_turn = getattr(opts, "_is_multi_turn", False)
        if is_multi_turn:
            await self._handle_multi_turn_failure(
                task_id=task_id,
                exc=exc,
                metadata=metadata,
                opts=opts,
                error_dict=error_dict,
            )
            return

        if opts.ephemeral:
            try:
                await self._provider.delete(task_id, force=True)
            except _HostedConflict as hosted_exc:
                translated = _translate_hosted_conflict(hosted_exc, task_id=task_id)
                if translated is None:
                    raise TaskConflictError(task_id, "in_progress") from hosted_exc
                raise translated from hosted_exc
            except TransportClassifiedError as transport_exc:
                if _is_evicted(transport_exc):
                    logger.warning(
                        "Eviction (binding_mismatch) on failed-task delete for "
                        "task %s (session=%s) — suppressing delete, signalling "
                        "awaiters with TaskConflictError",
                        task_id,
                        self._config.session_id or "local",
                    )
                    raise TaskConflictError(task_id, "in_progress") from transport_exc
                raise
            except Exception:  # pylint: disable=broad-exception-caught
                logger.warning(
                    "Failed to delete failed ephemeral task %s",
                    task_id,
                    exc_info=True,
                )
        else:
            try:
                # Spec 019 FR-A-008 — failure terminal write follows
                # RE-READ-AND-DECIDE policy on 412.
                # Spec 019 C-OUT-6 / US-C2.C2.3 — _handle_failure MUST
                # clear payload['output'] + _output attachment so the
                # failure-terminal record never carries a stale
                # prior-success output.
                await self._terminal_write_locked(
                    task_id,
                    TaskPatchRequest(
                        status="completed",
                        error=error_dict,
                        payload={"metadata": metadata.to_dict(), "output": None},
                        attachments={_OUTPUT_KEY: None},
                    ),
                )
            except TaskConflictError:
                # 412 RE-READ decided ABANDON; propagate as the
                # eviction-shape exception for awaiters.
                raise
            except _HostedConflict as hosted_exc:
                translated = _translate_hosted_conflict(hosted_exc, task_id=task_id)
                if translated is None:
                    if hosted_exc._code == "lease_ownership_changed":
                        raise TaskConflictError(task_id, "in_progress") from hosted_exc
                    raise EtagConflict(task_id) from hosted_exc
                raise translated from hosted_exc
            except TransportClassifiedError as transport_exc:
                if _is_evicted(transport_exc):
                    logger.warning(
                        "Eviction (binding_mismatch) on terminal failure write "
                        "for task %s (session=%s) — suppressing terminal write, "
                        "signalling awaiters with TaskConflictError",
                        task_id,
                        self._config.session_id or "local",
                    )
                    raise TaskConflictError(task_id, "in_progress") from transport_exc
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
        task_info = await self._provider_get_tracked(task_id)
        # Spec 019 FR-A-003 — refresh tracked etag from the GET so the
        # subsequent PATCH's if_match (filled in by _terminal_write_locked)
        # matches the just-read state.
        if task_info is not None:
            self._track_etag(task_id, getattr(task_info, "etag", None))
        steering_patch: dict[str, Any] = {}
        extra_attachments: dict[str, Any] = {}
        if task_info is not None and task_info.payload:
            existing_steering = task_info.payload.get("_steering") or {}
            if existing_steering:
                steering_patch = dict(existing_steering)
                steering_patch["active_input"] = None
            # Spec 018: if payload["input"] is a ref, the attachment it
            # points at must be deleted atomically with the ref clearing.
            # This is the C-8 conformance item.
            existing_input_slot = task_info.payload.get("input")
            if _is_ref(existing_input_slot):
                extra_attachments[_ref_key(existing_input_slot)] = None

        # Spec 019 FR-C-005/-007 / US-C4 — output is ALWAYS written
        # to attachments['_output'] (never inline). When None, both
        # payload['output'] and attachments['_output'] are explicitly
        # set to None (clearing any prior turn's output).
        extra_payload: dict[str, Any] = {"input": None}
        if steering_patch:
            extra_payload["_steering"] = steering_patch

        try:
            payload_patch, attachments_patch = _legacy_output_terminal_patch(
                task_id=task_id,
                metadata_dict=metadata.to_dict(),
                output=output,
                extra_payload=extra_payload,
                extra_attachments=extra_attachments,
            )
        except OutputTooLarge:
            # FR-C-006 / SC-9 — output too large, raised pre-PATCH.
            # Surface to the suspend()'s caller via the result_future
            # mechanism. The handler's `return await ctx.suspend(...)`
            # propagates this up.
            raise

        try:
            # Spec 019 FR-A-008 — suspend terminal write follows
            # RE-READ-AND-DECIDE policy on 412.
            await self._terminal_write_locked(
                task_id,
                TaskPatchRequest(
                    status="suspended",
                    suspension_reason=reason,
                    payload=payload_patch,
                    attachments=attachments_patch,
                ),
            )
        except TaskConflictError:
            raise
        except _AttachmentTooLarge as exc:
            # FR-D-004 — translate to OutputTooLarge for the developer.
            raise _remap_attachment_error(exc) from exc
        except _HostedConflict as exc:
            translated = _translate_hosted_conflict(exc, task_id=task_id)
            if translated is None:
                if exc._code == "lease_ownership_changed":
                    raise TaskConflictError(task_id, "in_progress") from exc
                raise EtagConflict(task_id) from exc
            raise translated from exc
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

    async def _steering_cleanup_orphan_attachments(self, task_info: TaskInfo) -> None:
        """Spec 018 — delete orphaned ``_steering_input_*`` attachments.

        On startup-scan / recovery, walk ``task_info.attachments`` for
        ``_steering_input_*`` keys whose corresponding ref slot is no
        longer present in ``pending_inputs``. Delete them via a single
        PATCH.

        This is defense-in-depth: the steering-append PATCH and the
        steering-drain PATCH each carry payload + attachments in one
        atomic write, so the happy path never produces orphans. But a
        crash window between an attachment add and a queue append
        (across separate PATCHes in some future code path) could
        theoretically leave one — this cleanup costs ~one extra PATCH
        per recovery and closes that window.

        :param task_info: The recovered ``TaskInfo`` (pre-reclaim).
        :type task_info: TaskInfo
        """
        if not task_info.attachments:
            return
        from ._attachments import (  # pylint: disable=import-outside-toplevel
            _STEERING_INPUT_KEY_PREFIX,
        )

        steering_keys = {k for k in task_info.attachments if k.startswith(_STEERING_INPUT_KEY_PREFIX)}
        if not steering_keys:
            return
        pending: list[Any] = (task_info.payload or {}).get("_steering", {}).get("pending_inputs", [])
        referenced = {
            _ref_key(entry)
            for entry in pending
            if _is_ref(entry) and _ref_key(entry).startswith(_STEERING_INPUT_KEY_PREFIX)
        }
        orphans = steering_keys - referenced
        if not orphans:
            return
        logger.info(
            "Deleting %d orphan steering attachment(s) on task %s: %s",
            len(orphans),
            task_info.id,
            sorted(orphans),
        )
        await self._provider_update_locked(
            task_info.id,
            TaskPatchRequest(
                attachments={k: None for k in orphans},
                if_match=getattr(task_info, "etag", None) or None,
            ),
        )

    async def _recover_stale_tasks(self) -> None:
        """Recover stale in-progress tasks from previous instances."""
        agent_name = self._config.agent_name or "default"
        session_id = self._config.session_id or "local"

        try:
            # Spec 019 FR-B-001 / C-FLT-1 — scope the recovery scan to
            # framework-owned tasks via source_type. Tasks created by
            # other systems sharing the same (agent, session,
            # lease_owner) triple MUST NOT be enumerated by the
            # framework's reclaim path.
            stale_tasks = await self._provider.list(
                agent_name=agent_name,
                session_id=session_id,
                status="in_progress",
                lease_owner=self._lease_owner,
                source_type=_SOURCE_TYPE,
            )
        except Exception:  # pylint: disable=broad-exception-caught
            logger.warning("Failed to query stale tasks for recovery", exc_info=True)
            return

        for task_info in stale_tasks:
            # Skip if we're already tracking this task
            if task_info.id in self._active_tasks:
                continue

            # Spec 018 — opportunistic orphan attachment cleanup. If a prior
            # lifetime crashed between a steering-append attachment PATCH
            # and the queue update (cannot happen in the happy path
            # because Phase 4 makes them a single atomic PATCH, but
            # defense-in-depth is cheap), delete any
            # ``_steering_input_*`` attachment that no live ref in
            # ``pending_inputs`` references.
            try:
                await self._steering_cleanup_orphan_attachments(task_info)
            except Exception:  # pylint: disable=broad-exception-caught
                logger.warning(
                    "Orphan attachment cleanup failed for %s",
                    task_info.id,
                    exc_info=True,
                )

            # Reclaim the lease with our new instance ID
            try:
                # Spec 019 FR-A-009 / C-LSE-2 — both reclaim sites
                # (inline AND cold-start/periodic) carry if_match. On
                # 412, ABANDON per §25.3 — another process beat us;
                # let the next scan re-evaluate.
                reclaim_etag = getattr(task_info, "etag", None)
                self._track_etag(task_info.id, reclaim_etag)
                await self._provider.update(
                    task_info.id,
                    TaskPatchRequest(
                        lease_owner=self._lease_owner,
                        lease_instance_id=self._instance_id,
                        lease_duration_seconds=_DEFAULT_LEASE_SECONDS,
                        if_match=reclaim_etag,
                    ),
                )
                logger.info(
                    "Reclaimed stale task %s (generation will increment)",
                    task_info.id,
                )
            except _HostedConflict as exc:
                translated = _translate_hosted_conflict(exc, task_id=task_info.id)
                if translated is None or getattr(translated, "current_status", None) == "in_progress":
                    logger.info(
                        "Reclaim conflict for task %s — another process beat us; " "letting next scan re-evaluate.",
                        task_info.id,
                    )
                    continue
                logger.warning("Failed to reclaim task %s", task_info.id, exc_info=True)
                continue
            except (EtagConflict, ValueError) as exc:
                # 412 ABANDON for reclaim per §25.3.
                if isinstance(exc, ValueError) and "etag" not in str(exc).lower():
                    logger.warning("Failed to reclaim task %s", task_info.id, exc_info=True)
                    continue
                logger.info(
                    "Reclaim 412 for task %s — another process beat us; "
                    "letting next scan re-evaluate (FR-A-009 / §25.3 ABANDON).",
                    task_info.id,
                )
                continue
            except Exception:  # pylint: disable=broad-exception-caught
                logger.warning("Failed to reclaim task %s", task_info.id, exc_info=True)
                continue

            # Find resume callback and dispatch
            fn = self._find_resume_callback(task_info)
            if fn is not None:
                try:
                    # Look up stored opts for resumed-task configuration.
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

    # --------------------------------------------------------------- #
    # Spec 019 — Per-task write queue + etag tracking
    # --------------------------------------------------------------- #

    def _get_task_write_lock(self, task_id: str) -> asyncio.Lock:
        """Spec 019 FR-A-006 / C-WQ-1 — return the per-task write lock.

        Lazily creates the lock on first use. All in-process PATCH-
        issuing code paths MUST acquire this lock before reading
        state + computing the PATCH + applying it.

        Reads do NOT call this method (FR-A-006 — reads are lock-free).

        The lock entry is dropped by :meth:`_active_tasks_pop` when
        the local active-entry is torn down (FR-A-007).
        """
        lock = self._task_write_locks.get(task_id)
        if lock is None:
            lock = asyncio.Lock()
            self._task_write_locks[task_id] = lock
        return lock

    def _track_etag(self, task_id: str, etag: str | None) -> None:
        """Spec 019 FR-A-003 — refresh the latest known etag for a task.

        Called by every store-interaction site after a successful
        response carries an etag. Stored in two places: the per-task
        etag cache (so reclaim/scan paths without an _ActiveTask can
        still benefit) AND, if present, on the _ActiveTask entry
        itself.
        """
        if etag is None:
            return
        self._task_etag_cache[task_id] = etag
        active = self._active_tasks.get(task_id)
        if active is not None:
            active.current_etag = etag

    def _get_tracked_etag(self, task_id: str) -> str | None:
        """Spec 019 FR-A-001 — read the latest tracked etag for a task.

        Returns ``None`` if no PATCH/GET response has been observed
        yet (this can happen on the very first write — typically a
        ``create`` where ``if_match`` is intentionally absent).
        """
        active = self._active_tasks.get(task_id)
        if active is not None and active.current_etag is not None:
            return active.current_etag
        return self._task_etag_cache.get(task_id)

    def _active_tasks_pop(self, task_id: str) -> None:
        """Spec 019 FR-A-007 — pop the active task entry AND drop its
        per-task write lock + etag cache so the registries do not
        leak across many task lifetimes.
        """
        self._active_tasks.pop(task_id, None)
        self._task_write_locks.pop(task_id, None)
        self._task_etag_cache.pop(task_id, None)

    async def _provider_get_tracked(self, task_id: str) -> Any:
        """Spec 019 FR-A-003 — read a task AND refresh the tracked etag.

        Thin wrapper around ``self._provider.get(task_id)`` that calls
        ``_track_etag`` on the response's etag. Use at every read site
        where a subsequent PATCH may rely on the latest etag (the
        normal read-then-PATCH pattern across the framework).
        """
        try:
            info = await self._provider.get(task_id)
        except _HostedConflict as exc:
            translated = _translate_hosted_conflict(exc, task_id=task_id)
            if translated is None:
                if exc._code == "lease_ownership_changed":
                    raise TaskConflictError(task_id, "in_progress") from exc
                raise EtagConflict(task_id) from exc
            raise translated from exc
        if info is not None:
            self._track_etag(task_id, getattr(info, "etag", None))
        return info

    async def _provider_update_locked(
        self,
        task_id: str,
        patch: TaskPatchRequest,
        *,
        force_if_match: bool = True,
    ) -> Any:
        """Spec 019 FR-A-001 / C-WQ-3 — apply a PATCH under the per-task
        write lock with the tracked etag as ``if_match``.

        - Acquires the per-task write lock (FR-A-006).
        - Populates ``patch.if_match`` from the tracked etag when the
          caller hasn't set one and ``force_if_match=True`` (FR-A-001).
        - Calls ``self._provider.update(task_id, patch)``.
        - Refreshes the tracked etag from the response (FR-A-003).
        - Bumps lease-last-refresh if the PATCH carried lease ext
          kwargs (FR-A-005 — dynamic cadence shadows next heartbeat).

        Does NOT implement the FR-A-008 RE-READ-AND-DECIDE policy —
        that lives in :meth:`_terminal_write_locked` for the terminal
        suspend/complete/fail sites.
        """
        async with self._get_task_write_lock(task_id):
            if force_if_match and patch.if_match is None:
                patch.if_match = self._get_tracked_etag(task_id)
            result = await self._provider.update(task_id, patch)
            etag = getattr(result, "etag", None)
            if etag:
                self._track_etag(task_id, etag)
            # If the PATCH piggybacked the lease, the renewal loop's
            # next tick is pushed out (FR-A-005).
            if patch.lease_owner is not None:
                self._note_lease_refreshed(task_id)
            return result

    async def _terminal_write_locked(
        self,
        task_id: str,
        patch: TaskPatchRequest,
        *,
        max_attempts: int = 5,
    ) -> Any:
        """Spec 019 FR-A-008 / C-WQ-3 / SC-3b — terminal-write 412
        RE-READ-AND-DECIDE.

        On 412 (EtagConflict from the provider, OR a hosted-provider
        TransportClassifiedError(classification='conflict')), the
        framework re-reads the record and decides:

        - (a) Lease no longer ours (owner / instance_id differ, or
          ``expiry_count`` bumped past our cached value) → ABANDON
          and raise ``TaskConflictError(current_status='in_progress')``.
          The new owner is mid-recovery; clobbering their state would
          silently cancel their execution.
        - (b) ``status`` already ``completed`` → ABANDON. Another
          actor already wrote the terminal; raise
          ``TaskConflictError(current_status='completed')``.
        - (c) Lease still ours, status still ``in_progress`` → retry
          the terminal PATCH against the new etag, up to
          ``max_attempts`` times. Steering inputs another process
          appended in the racing window are silently superseded —
          the steerer's ``.result()`` then raises
          ``TaskConflictError(current_status='completed')`` per the
          C-STR-6 cross-process steering-after-terminate contract.

        Default budget is 5 attempts.
        """
        prior_lease_owner = patch.lease_owner
        prior_lease_instance = patch.lease_instance_id
        async with self._get_task_write_lock(task_id):
            attempts = 0
            cached_expiry_count = self._cached_expiry_count(task_id)
            while True:
                attempts += 1
                if patch.if_match is None:
                    patch.if_match = self._get_tracked_etag(task_id)
                try:
                    result = await self._provider.update(task_id, patch)
                    etag = getattr(result, "etag", None)
                    if etag:
                        self._track_etag(task_id, etag)
                    return result
                except _HostedConflict as exc:
                    translated = _translate_hosted_conflict(exc, task_id=task_id)
                    if translated is not None:
                        raise translated from exc
                    if attempts >= max_attempts:
                        if exc._code == "lease_ownership_changed":
                            raise TaskConflictError(task_id, "in_progress") from exc
                        raise EtagConflict(task_id) from exc
                    decision = await self._terminal_412_decide(
                        task_id,
                        prior_lease_owner=prior_lease_owner,
                        prior_lease_instance=prior_lease_instance,
                        cached_expiry_count=cached_expiry_count,
                    )
                    if decision == "abandon_lease_lost":
                        raise TaskConflictError(task_id, "in_progress") from exc
                    if decision == "abandon_already_terminal":
                        raise TaskConflictError(task_id, "completed") from exc
                    patch.if_match = None
                except (EtagConflict, ValueError) as exc:
                    # The local provider raises ValueError on etag
                    # mismatch; the hosted provider raises
                    # TransportClassifiedError(classification="conflict")
                    # which the caller translates to EtagConflict at
                    # the boundary. Both arrive here as either type.
                    if isinstance(exc, ValueError) and "etag" not in str(exc).lower():
                        raise
                    if attempts >= max_attempts:
                        raise
                    decision = await self._terminal_412_decide(
                        task_id,
                        prior_lease_owner=prior_lease_owner,
                        prior_lease_instance=prior_lease_instance,
                        cached_expiry_count=cached_expiry_count,
                    )
                    if decision == "abandon_lease_lost":
                        raise TaskConflictError(task_id, "in_progress") from exc
                    if decision == "abandon_already_terminal":
                        raise TaskConflictError(task_id, "completed") from exc
                    # decision == "retry" — clear if_match and loop.
                    patch.if_match = None
                except TransportClassifiedError as exc:
                    # Hosted-provider conflict (412 etag) or eviction
                    # (binding_mismatch). Eviction goes to the eviction
                    # path — fall through to the existing handler shape.
                    if getattr(exc, "classification", "") == "conflict":
                        if attempts >= max_attempts:
                            raise
                        decision = await self._terminal_412_decide(
                            task_id,
                            prior_lease_owner=prior_lease_owner,
                            prior_lease_instance=prior_lease_instance,
                            cached_expiry_count=cached_expiry_count,
                        )
                        if decision == "abandon_lease_lost":
                            raise TaskConflictError(task_id, "in_progress") from exc
                        if decision == "abandon_already_terminal":
                            raise TaskConflictError(task_id, "completed") from exc
                        patch.if_match = None
                        continue
                    raise

    def _cached_expiry_count(self, task_id: str) -> int:
        """Best-effort cache of the prior lease.expiry_count for FR-A-008
        branch (a) detection. Not authoritative; absence means "no
        cached value" and the decision falls back on lease owner /
        instance_id comparison.
        """
        return getattr(self, "_expiry_count_cache", {}).get(task_id, 0)

    async def _terminal_412_decide(
        self,
        task_id: str,
        *,
        prior_lease_owner: str | None,
        prior_lease_instance: str | None,
        cached_expiry_count: int,
    ) -> str:
        """Spec 019 FR-A-008 — decide what to do after a terminal-write 412.

        Returns one of:

        - ``"abandon_lease_lost"`` — RE-READ shows lease no longer ours
          (owner or instance_id differ). New owner is authoritative;
          do not retry.
        - ``"abandon_already_terminal"`` — RE-READ shows status already
          terminal (``completed``).
        - ``"retry"`` — Lease still ours, status still ``in_progress``;
          safe to retry against the new etag.

        Note: per C-LSE-3, every real expiry-driven handoff bumps the
        ``lease_instance_id``, so instance-id comparison alone is
        sufficient to detect lease loss. An additional ``expiry_count``
        leg would require populating a snapshot cache at every write
        site (otherwise the default ``cached_expiry_count=0`` causes
        any reclaimed task with `expiry_count >= 1` to spuriously
        abandon on legitimate retry-able 412s). We rely on instance-id
        comparison and intentionally do NOT consult ``expiry_count``
        in this decision.
        """
        _ = cached_expiry_count  # retained for binary-compat / future use
        try:
            fresh = await self._provider_get_tracked(task_id)
        except Exception:  # pylint: disable=broad-exception-caught
            # Can't re-read — be conservative; treat as lost.
            return "abandon_lease_lost"
        if fresh is None:
            # Record vanished — treat as terminal.
            return "abandon_already_terminal"
        # Refresh tracked etag from the re-read.
        etag = getattr(fresh, "etag", None)
        if etag:
            self._track_etag(task_id, etag)
        # Branch (b): already terminal.
        if getattr(fresh, "status", None) == "completed":
            return "abandon_already_terminal"
        # Branch (a): lease no longer ours (owner or instance_id differ).
        if (
            fresh.lease is None
            or fresh.lease.owner != (prior_lease_owner or self._lease_owner)
            or fresh.lease.instance_id != (prior_lease_instance or self._instance_id)
        ):
            return "abandon_lease_lost"
        # Branch (c): retry.
        return "retry"

    def _lease_ext_kwargs(self, task_id: str) -> dict[str, Any]:
        """Return lease-ownership kwargs for piggyback on a payload PATCH.

        Every framework-issued PATCH that mutates payload (metadata
        flush, steering-queue append, steering drain, terminal complete
        on a steerable task) can refresh the lease as a side effect by
        including the lease ownership query params on the request. This
        eliminates the once-per-30-second redundant heartbeat PATCH for
        an active task and pushes the renewal-loop tick out via
        ``_note_lease_refreshed`` below. Zero extra network round-trips:
        the lease params land on the same PATCH that was already going
        out for the payload mutation.

        Returns the kwargs only when ``task_id`` is currently tracked
        as an active local task. Otherwise returns an empty dict
        (caller writes a plain payload-only PATCH; this is what
        recovery/reclaim/restart paths want before they have bound a
        new lease).

        :param task_id: The task identifier.
        :type task_id: str
        :return: kwargs for ``TaskPatchRequest`` carrying lease params,
            or ``{}`` if this task is not active locally.
        :rtype: dict[str, Any]
        """
        if self._active_tasks.get(task_id) is None:
            return {}
        return {
            "lease_owner": self._lease_owner,
            "lease_instance_id": self._instance_id,
            "lease_duration_seconds": _DEFAULT_LEASE_SECONDS,
        }

    def _note_lease_refreshed(self, task_id: str) -> None:
        """Record that the lease for ``task_id`` was just refreshed.

        Called by every PATCH path that piggybacks lease ownership
        (see :meth:`_lease_ext_kwargs`) AND by the renewal loop itself
        on a successful renewal. The renewal loop reads this timestamp
        to push its next scheduled tick out -- so a payload PATCH that
        already refreshed the lease delays the heartbeat by the same
        margin, avoiding a redundant network round-trip.

        :param task_id: The task identifier.
        :type task_id: str
        """
        active = self._active_tasks.get(task_id)
        if active is None:
            return
        try:
            active.lease_last_refresh_monotonic = asyncio.get_event_loop().time()
        except RuntimeError:  # no running loop (sync context)
            pass

    def _make_metadata_flush(self, task_id: str) -> Callable[[Optional[str], dict[str, Any]], Awaitable[None]]:
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
            # Spec 019 FR-A-001 / FR-A-006 — route through the per-task
            # write queue and use the tracked etag as if_match. The
            # helper refreshes the etag from the response and bumps
            # lease-last-refresh (FR-A-005 cadence shadow).
            await self._provider_update_locked(
                task_id,
                TaskPatchRequest(
                    payload={slot: data},
                    **self._lease_ext_kwargs(task_id),
                ),
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

        :param task_id: The task identifier the callable should track.
        :type task_id: str
        :return: A callable returning the current pending-input count.
        :rtype: Callable[[], int]
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
            except Exception:  # pylint: disable=broad-exception-caught  # noqa: BLE001
                return 0

        return _provider
