# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Durable orchestrator — wraps existing response execution in the task primitive.

This module bridges the Responses API and the durable tasks system. It creates
a ``@task``-decorated function whose body calls ``_run_background_non_stream``
(the existing pipeline). The developer's handler is unchanged — the task wrapping
is a transparent infrastructure concern.

Architecture:
  POST /responses → _ResponseOrchestrator.run_background()
    → (durable=True)  → DurableResponseOrchestrator.start_durable(...)
        → task_fn.start(task_id=derived_id, input=execution_params)
          → task body → _run_background_non_stream(...)  [existing pipeline]
    → (durable=False) → asyncio.create_task(_shielded_runner())  [unchanged]
"""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import logging
from typing import TYPE_CHECKING, Any, Callable

from azure.ai.agentserver.core.durable import (
    Task,
    TaskContext,
    TaskConflictError,
    task,
)

from .._durability_context import (
    DurabilityContext,
    DurabilityEntryMode,
    _FilteredMetadata,
)
from .._options import ResponsesServerOptions
from ..models.runtime import CancellationReason
from ._task_id import derive_task_id

if TYPE_CHECKING:
    from .._response_context import ResponseContext
    from ..models._generated import CreateResponse
    from ..models.runtime import ResponseExecution
    from ..store._base import ResponseProviderProtocol
    from ._orchestrator import _ResponseOrchestrator
    from ._runtime_state import _RuntimeState

logger = logging.getLogger("azure.ai.agentserver.responses.durable")

# Framework-internal metadata key prefix
_FW_PREFIX = "_framework."


def _build_server_error_payload(
    response_id: str,
    *,
    shutdown_reason: str,
    message: str | None = None,
) -> dict[str, Any]:
    """Build the response-failed payload for crash / shutdown markers.

    Single source of truth for the failure payload format per
    ``sdk/agentserver/specs/durability-contract.md`` § Glossary —
    the user-visible ``code`` is the generic ``"server_error"`` (the
    same code used elsewhere in the codebase, e.g. ``_orchestrator.py``).
    Path-specific cause goes in ``message`` and in
    ``error.additionalInfo.shutdown_reason`` for operator diagnostics.

    :param response_id: The response identifier.
    :type response_id: str
    :keyword shutdown_reason: One of ``"crash_recovery"`` (next-lifetime
        marker for SIGKILL / lost-process recovery) or ``"grace_exhausted"``
        (in-process marker fired during graceful shutdown). Surfaces in
        ``error.additionalInfo.shutdown_reason``.
    :paramtype shutdown_reason: str
    :keyword message: Optional override for the human-readable
        ``error.message``. If omitted, a path-specific default is used.
    :paramtype message: str | None
    :returns: A response-failed dict suitable for persisting via
        ``ResponseProviderProtocol.update_response``.
    :rtype: dict[str, Any]
    """
    if message is None:
        if shutdown_reason == "crash_recovery":
            message = "Server interrupted before completing this response"
        elif shutdown_reason == "grace_exhausted":
            message = "Server stopped before this response completed"
        else:
            message = "Server failed to complete this response"
    return {
        "id": response_id,
        "object": "response",
        "status": "failed",
        "output": [],
        "error": {
            "type": "server_error",
            "code": "server_error",
            "message": message,
            "additionalInfo": {"shutdown_reason": shutdown_reason},
        },
    }


# (Spec 013 US1(a/c)) Process-local cache of in-memory refs (record, context,
# parsed request, cancellation signal, runtime state). These cannot be JSON-
# serialized for cross-process recovery, so we keep them in memory keyed by
# response_id and pass only the serializable params through the durable task
# input. The task body fetches refs from this cache when re-entered in the
# same process; on cross-process recovery the entry is absent and the body
# reconstructs from the serialized params instead.
_RUNTIME_REFS: dict[str, dict[str, Any]] = {}

# Keys in ctx_params that are runtime-only object references (kept in
# ``_RUNTIME_REFS`` and stripped before persisting as task input).
_REF_KEYS = frozenset(
    {
        "_record_ref",
        "_context_ref",
        "_parsed_ref",
        "_cancel_ref",
        "_runtime_state_ref",
    }
)


def _split_runtime_refs(ctx_params: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Split ``ctx_params`` into refs (memory-only) and persisted params.

    :param ctx_params: The orchestrator's combined params dict.
    :type ctx_params: dict[str, Any]
    :returns: ``(refs, persisted)`` — ``refs`` contains object references
        to keep in process memory; ``persisted`` contains the JSON-
        serializable subset for the durable task input.
    :rtype: tuple[dict[str, Any], dict[str, Any]]
    """
    refs: dict[str, Any] = {}
    persisted: dict[str, Any] = {}
    for k, v in ctx_params.items():
        if k in _REF_KEYS:
            refs[k] = v
        else:
            persisted[k] = v
    return refs, persisted


def _reconstruct_parsed_from_params(params: dict[str, Any]) -> Any:
    """Re-parse the serialized raw payload back to a CreateResponse model.

    Used on cross-process recovery when the in-process ``_parsed_ref`` is
    unavailable. The original request payload was serialized to
    ``params["parsed_payload"]`` at fresh-entry time (Spec 013 US1 deliverable (a)).

    :param params: The durable task input dict.
    :type params: dict[str, Any]
    :returns: A re-hydrated request model, or the raw dict if parsing fails.
    :rtype: Any
    :raises RuntimeError: If parsed_payload is missing from params.
    """
    payload = params.get("parsed_payload")
    if payload is None:
        raise RuntimeError(
            "Cannot reconstruct parsed request — params['parsed_payload'] is "
            "missing. Ensure the orchestrator stamps it at fresh-entry."
        )
    # Late import to avoid circular dependency on hosting/_request_parsing.
    from ..models._generated import CreateResponse  # pylint: disable=import-outside-toplevel

    if isinstance(payload, dict):
        return CreateResponse(payload)
    return payload


def _reconstruct_from_params(
    *,
    params: dict[str, Any],
    response_id: str,
    provider: "ResponseProviderProtocol | None",
    runtime_state: "_RuntimeState | None",
    runtime_options: ResponsesServerOptions,
) -> tuple["ResponseExecution", "ResponseContext"]:
    """Rebuild ResponseExecution and ResponseContext from the durable task input.

    Called on cross-process recovery when ``_record_ref`` is missing.
    All inputs are derived from the serialized ``params`` dict that the
    orchestrator stamped at fresh-entry time.

    :keyword params: The durable task input.
    :paramtype params: dict[str, Any]
    :keyword response_id: The stable response id from ``params["response_id"]``.
    :paramtype response_id: str
    :keyword provider: The response-store provider.
    :paramtype provider: ResponseProviderProtocol | None
    :keyword runtime_state: The per-process runtime state tracker.
    :paramtype runtime_state: _RuntimeState | None
    :keyword runtime_options: Server options.
    :paramtype runtime_options: ResponsesServerOptions
    :returns: ``(record, context)`` tuple — both ready for use by the existing
        pipeline.
    :rtype: tuple[ResponseExecution, ResponseContext]
    """
    # Late imports to avoid module-level circular dependencies.
    from .._response_context import IsolationContext, ResponseContext  # pylint: disable=import-outside-toplevel
    from ..models.runtime import ResponseExecution, ResponseModeFlags  # pylint: disable=import-outside-toplevel

    parsed = _reconstruct_parsed_from_params(params)

    record = ResponseExecution(
        response_id=response_id,
        mode_flags=ResponseModeFlags(
            stream=bool(params.get("stream", False)),
            store=bool(params.get("store", True)),
            background=bool(params.get("background", True)),
        ),
        status="in_progress",
        input_items=list(params.get("input_items") or []),
        previous_response_id=params.get("previous_response_id"),
        initial_model=params.get("model"),
        initial_agent_reference=params.get("agent_reference"),
        agent_session_id=params.get("agent_session_id"),
        conversation_id=params.get("conversation_id"),
        chat_isolation_key=params.get("chat_isolation_key"),
    )

    context = ResponseContext(
        response_id=response_id,
        mode_flags=record.mode_flags,
        request=parsed,
        provider=provider,
        input_items=record.input_items,
        previous_response_id=record.previous_response_id,
        conversation_id=record.conversation_id,
        history_limit=int(
            params.get("history_limit", runtime_options.default_fetch_history_count)
        ),
        # Client headers / query params are not preserved across recovery
        # — they were specific to the original HTTP request and are not
        # meaningful for the recovered handler.
        client_headers={},
        query_parameters={},
        isolation=IsolationContext(
            user_key=params.get("user_isolation_key"),
            chat_key=params.get("chat_isolation_key"),
        ),
        prefetched_history_ids=params.get("prefetched_history_ids"),
    )
    record.response_context = context
    return record, context
_FW_RESPONSE_ID = f"{_FW_PREFIX}response_id"
_FW_LAST_SEQ = f"{_FW_PREFIX}last_sequence_number"
_FW_BACKGROUND = f"{_FW_PREFIX}background"
# (Spec 014 FR-003 / FR-004 — Phase 4) Per-task disposition tells the recovery
# scanner what to do on the next-lifetime recovered entry:
#   - "re-invoke": re-run the handler (Row 1: durable_background+bg+store).
#   - "mark-failed": persist a server_error terminal to the response store and
#     complete the task without re-invoking (Rows 2, 3: bg+store with
#     durable_background=False, and fg+store).
_FW_DISPOSITION = f"{_FW_PREFIX}disposition"
DISPOSITION_REINVOKE = "re-invoke"
DISPOSITION_MARK_FAILED = "mark-failed"

# Per-process registry of pending bookkeeping-task completion events.
# Keyed by response_id. Set by ``DurableResponseOrchestrator.complete_bookkeeping_task``
# from the orchestrator's terminal-persist hook so the bookkeeping task body
# (which is awaiting this event) exits cleanly and the task is marked completed.
# In-memory only — survives only for the current process. On crash before the
# event fires, the task stays in_progress and the next-lifetime recovery
# scanner reclaims it (mark-failed disposition then runs).
_BOOKKEEPING_EVENTS: dict[str, asyncio.Event] = {}


def _read_disposition(metadata: "_FilteredMetadata | dict[str, Any]") -> str:
    """Read the task disposition from framework metadata.

    Defaults to ``DISPOSITION_REINVOKE`` for backward compatibility with
    Phase 3 (Row 1) tasks created before this metadata key existed.

    :param metadata: The task's framework metadata dict.
    :returns: One of ``DISPOSITION_REINVOKE`` or ``DISPOSITION_MARK_FAILED``.
    :rtype: str
    """
    raw = metadata.get(_FW_DISPOSITION) if metadata else None
    if raw in (DISPOSITION_REINVOKE, DISPOSITION_MARK_FAILED):
        return raw
    return DISPOSITION_REINVOKE


def _map_entry_mode(task_entry_mode: str) -> DurabilityEntryMode:
    """Map task primitive entry_mode to DurabilityContext entry_mode.

    Task 'resumed' (new turn arriving) maps to 'fresh' for the handler —
    from the handler developer's perspective, a resume is just a new turn.
    """
    if task_entry_mode == "recovered":
        return "recovered"
    return "fresh"  # "fresh" and "resumed" both → "fresh"


class DurableResponseOrchestrator:
    """Wraps the existing response execution pipeline in the durable task primitive.

    When ``durable_background=True``, the normal ``asyncio.create_task()`` path
    is replaced by ``task_fn.start()``. The task body reconstructs the execution
    context and calls ``_run_background_non_stream`` — the same function the
    non-durable path uses. This ensures:
    - Zero handler code changes (same create_fn, same ResponseContext)
    - Crash recovery via task primitive lease + re-entry
    - DurabilityContext populated before handler invocation

    :param create_fn: The handler factory (bound ``create_fn`` method).
    :param options: Server options (steerable, max_pending, etc.).
    :param provider: Response persistence provider.
    """

    def __init__(
        self,
        *,
        create_fn: Callable[..., Any],
        options: ResponsesServerOptions,
        provider: "ResponseProviderProtocol",
        runtime_state: "_RuntimeState | None" = None,
        parent_orchestrator: "_ResponseOrchestrator | None" = None,
    ) -> None:
        self._create_fn = create_fn
        self._options = options
        self._provider = provider
        self._runtime_state = runtime_state
        # (Spec 014 FR-002 — close divergence 1)
        # Back-reference to the parent _ResponseOrchestrator so the durable
        # task body can call into the streaming pipeline
        # (_process_handler_events, _finalize_stream) for stream=True paths.
        # The non-stream path (_run_background_non_stream) is a module-level
        # function and does not need this reference.
        self._parent_orchestrator = parent_orchestrator

        # Create the internal task function
        self._task_fn: Task[dict[str, Any], None] = self._create_task_fn()

    @property
    def task_fn(self) -> Task[dict[str, Any], None]:
        """The underlying durable task descriptor."""
        return self._task_fn

    def _create_task_fn(self) -> Task[dict[str, Any], None]:
        """Create the @task-decorated function that wraps _run_background_non_stream."""
        orchestrator = self

        @task(
            name="responses_durable_background",
            steerable=self._options.steerable_conversations,
            max_pending=self._options.max_pending,
            ephemeral=False,  # Task lives for conversation lifetime
            store_input=True,
        )
        async def _durable_response_task(ctx: TaskContext[dict[str, Any]]) -> None:
            """Task body: executes the response pipeline with durability context.

            On fresh entry: runs the full pipeline via _run_background_non_stream.
            On recovery: re-runs the pipeline (handler is re-invoked from scratch).
            After completion: suspends awaiting the next turn.
            """
            await orchestrator._execute_in_task(ctx)

        return _durable_response_task

    async def _execute_in_task(self, ctx: TaskContext[dict[str, Any]]) -> None:
        """Execute the response pipeline inside the task body.

        This is the re-entrant function. On each entry:
        1. Builds DurabilityContext from TaskContext
        2. Attaches it to the ResponseContext
        3. Delegates to _run_background_non_stream (existing pipeline)
        4. Persists last_sequence_number to metadata
        5. Suspends (task stays alive for next turn)
        """
        # Import here to avoid circular imports
        from ._orchestrator import (
            _run_background_non_stream,
        )  # pylint: disable=import-outside-toplevel

        params = ctx.input
        entry_mode = _map_entry_mode(ctx.entry_mode)
        is_recovery = entry_mode == "recovered"

        # Track response_id in framework metadata
        response_id = params["response_id"]
        if ctx.metadata.get(_FW_RESPONSE_ID) is None:
            ctx.metadata[_FW_RESPONSE_ID] = response_id

        # (Spec 013 US1(c)) Look up in-memory refs cached at start_durable
        # time. Present for same-process execution; absent on cross-process
        # recovery (the reconstruction path picks up the slack below). For
        # backward compat with tests that inject refs directly via
        # ``ctx.input``, fall back to ``params`` for each ref key.
        cached_refs = _RUNTIME_REFS.get(response_id, {})

        def _ref(key: str) -> Any:
            value = cached_refs.get(key)
            if value is None:
                value = params.get(key)
            return value

        # Store background flag on first entry for recovery decisions
        if _FW_BACKGROUND not in ctx.metadata:
            ctx.metadata[_FW_BACKGROUND] = params.get("background", True)

        # (Spec 014 FR-003 / FR-004) Stamp the disposition on first entry so
        # next-lifetime recovery can dispatch correctly without needing to
        # reconstruct the routing decisions from input params.
        if _FW_DISPOSITION not in ctx.metadata:
            ctx.metadata[_FW_DISPOSITION] = params.get(
                "disposition", DISPOSITION_REINVOKE
            )
            # Force-flush so the disposition is durable BEFORE the body
            # could be killed (the default 5s debounce window is too long
            # to rely on for crash-recovery correctness — without an
            # explicit flush the recovered task would default to
            # ``re-invoke`` and skip the mark-failed branch).
            try:
                await ctx.metadata.flush()
            except (AttributeError, Exception):  # noqa: BLE001
                pass  # best-effort — backend may not support explicit flush
        disposition = _read_disposition(ctx.metadata)

        # (Spec 014 FR-003 / FR-004) Recovery dispatch via disposition.
        # mark-failed: handler doesn't re-run; persist server_error to the
        # response store and complete the task. Covers Rows 2 (bg+store with
        # durable_background=False) and 3 (fg+store).
        if is_recovery and disposition == DISPOSITION_MARK_FAILED:
            logger.info(
                "Bookkeeping task recovered (response_id=%s, disposition=mark-failed) — marking failed",
                response_id,
            )
            await self._persist_crash_failed(response_id, params)
            if self._options.steerable_conversations:
                return await ctx.suspend(reason="crash_failed")
            return

        # Backward-compat: the pre-disposition non-background recovery branch.
        # Tasks created before the disposition key existed default to
        # DISPOSITION_REINVOKE; for those, preserve the prior behaviour of
        # marking foreground responses failed on recovery without re-invoking.
        if is_recovery and not ctx.metadata.get(_FW_BACKGROUND, True):
            logger.info(
                "Non-background task recovered (response_id=%s) — marking failed",
                response_id,
            )
            await self._persist_crash_failed(response_id, params)
            if self._options.steerable_conversations:
                return await ctx.suspend(reason="non_bg_crash_failed")
            return

        # (Spec 014 FR-003 / FR-004) Fresh-entry bookkeeping mode. The
        # handler is running externally (Row 2: asyncio.create_task in
        # run_background; Row 3: synchronously in run_sync / _live_stream).
        # This task body just keeps the task in_progress until the
        # orchestrator signals completion via complete_bookkeeping_task.
        # On crash / shutdown before signal, the task stays in_progress and
        # the next-lifetime recovery scanner reclaims it (mark-failed branch
        # above runs).
        if not is_recovery and disposition == DISPOSITION_MARK_FAILED:
            await self._run_bookkeeping_body(ctx, response_id)
            return

        # Build DurabilityContext for the handler.
        # Note: `last_snapshot` was intentionally removed — the response object is
        # only persisted at `response.created` and at terminal events, so
        # a between-states snapshot is never useful. Handlers build their
        # resumption response from upstream framework state.
        durability_ctx = DurabilityContext(
            entry_mode=entry_mode,
            run_attempt=ctx.run_attempt,
            was_steered=ctx.was_steered,
            pending_inputs=len(ctx.pending_inputs),
            metadata=ctx.metadata,
        )

        # The execution params contain everything _run_background_non_stream needs.
        # The record and context are reconstructed from serialized state.
        # For Phase 1, we pass the durability_ctx through the response_context
        # which is already attached to the record.
        context: ResponseContext | None = _ref("_context_ref")
        if context is not None:
            context._durability = durability_ctx  # pylint: disable=protected-access

        record: ResponseExecution | None = _ref("_record_ref")
        if record is None:
            # Cross-process recovery: in-memory references were lost when the
            # task input was serialized to the durable store. Reconstruct from
            # the serialized params (Spec 013 US1 deliverable (a)).
            record, context = _reconstruct_from_params(
                params=params,
                response_id=response_id,
                provider=self._provider,
                runtime_state=self._runtime_state,
                runtime_options=self._options,
            )
            await self._runtime_state.add(record)
            if context is not None:
                context._durability = durability_ctx  # pylint: disable=protected-access

        # Bridge task cancellation → response cancellation signal.
        # We bridge BOTH ctx.cancel (steering / explicit cancel) and
        # ctx.shutdown (graceful TaskManager shutdown) so handlers that
        # listen on the response context's cancellation_signal are notified
        # in either case. The bridge stamps the appropriate
        # cancellation_reason so downstream policy (e.g., "leave in_progress
        # for re-entry on shutdown") can route correctly.
        cancellation_signal: asyncio.Event = _ref("_cancel_ref") or asyncio.Event()
        cancel_bridge: asyncio.Task[None] | None = None
        if ctx.cancel.is_set():
            if context is not None and context.cancellation_reason is None:
                context.cancellation_reason = CancellationReason.STEERED
            cancellation_signal.set()
        elif ctx.shutdown.is_set():
            if context is not None and context.cancellation_reason is None:
                context.cancellation_reason = CancellationReason.SHUTTING_DOWN
            cancellation_signal.set()
        else:

            async def _bridge() -> None:
                # Race ctx.cancel vs ctx.shutdown — whichever fires first wins.
                cancel_task = asyncio.create_task(ctx.cancel.wait())
                shutdown_task = asyncio.create_task(ctx.shutdown.wait())
                try:
                    done, pending = await asyncio.wait(
                        {cancel_task, shutdown_task},
                        return_when=asyncio.FIRST_COMPLETED,
                    )
                    for task in pending:
                        task.cancel()
                    if shutdown_task in done and cancel_task not in done:
                        reason = CancellationReason.SHUTTING_DOWN
                    else:
                        reason = CancellationReason.STEERED
                    if context is not None and context.cancellation_reason is None:
                        context.cancellation_reason = reason
                    cancellation_signal.set()
                except asyncio.CancelledError:
                    cancel_task.cancel()
                    shutdown_task.cancel()
                    raise

            cancel_bridge = asyncio.create_task(_bridge())

        try:
            parsed_ref = _ref("_parsed_ref")
            if parsed_ref is None:
                # Cross-process recovery: re-parse the serialized payload.
                parsed_ref = _reconstruct_parsed_from_params(params)

            # (Spec 014 FR-002 — close divergence 1)
            # Dispatch on params["stream"]: the streaming pipeline goes
            # through the parent orchestrator's streaming runner so events
            # flow to record.subject (live wire iterator subscribes to it)
            # AND to the durable stream provider (for GET reconnect after
            # crash). The non-stream path (existing, default) drives the
            # response-snapshot-on-terminal pipeline.
            if params.get("stream") and self._parent_orchestrator is not None:
                assert record is not None  # reconstruction guarantees this
                assert context is not None  # reconstruction guarantees this
                await self._parent_orchestrator._run_durable_stream_body(
                    parsed=parsed_ref,
                    context=context,
                    cancellation_signal=cancellation_signal,
                    record=record,
                    response_id=response_id,
                    agent_reference=params.get("agent_reference"),
                    model=params.get("model"),
                    store=bool(params.get("store", True)),
                    agent_session_id=params.get("agent_session_id"),
                    conversation_id=params.get("conversation_id"),
                )
            else:
                await _run_background_non_stream(
                    create_fn=self._create_fn,
                    parsed=parsed_ref,
                    context=context,
                    cancellation_signal=cancellation_signal,
                    record=record,
                    response_id=response_id,
                    agent_reference=params.get("agent_reference"),
                    model=params.get("model"),
                    provider=self._provider,
                    store=params.get("store", True),
                    agent_session_id=params.get("agent_session_id"),
                    conversation_id=params.get("conversation_id"),
                    history_limit=params.get("history_limit", 100),
                    runtime_state=_ref("_runtime_state_ref") or self._runtime_state,
                    runtime_options=self._options,
                )

            # (Spec 014 FR-005a — close divergence 4)
            # If the handler returned without emitting a terminal event AND
            # graceful shutdown is in progress, raise CancelledError so the
            # core durable-task primitive's cooperative-cancel branch
            # (_manager.py:1241-1268) leaves the task `status="in_progress"`
            # for next-lifetime recovery. Without this, _handle_success runs
            # (_manager.py:1200-1208), marks the task `completed`, and the
            # recovery scanner skips it. See
            # `azure-ai-agentserver-core/docs/durable-task-developer-guide.md`
            # § Graceful Shutdown (`ctx.shutdown`).
            if (
                ctx.shutdown.is_set()
                and record is not None
                and record.status in {"queued", "in_progress"}
            ):
                logger.info(
                    "Response %s handler returned during shutdown without "
                    "terminal; raising CancelledError so task stays "
                    "in_progress for next-lifetime recovery (FR-005a).",
                    response_id,
                )
                raise asyncio.CancelledError()
        finally:
            if cancel_bridge is not None and not cancel_bridge.done():
                cancel_bridge.cancel()
            # (Spec 013 US1(c)) On terminal exit of the task body (handler
            # returned), drop the runtime-refs entry to release memory. On
            # suspend the entry would still be useful for in-process resume,
            # but it'll be rebuilt at the next `start_durable` from the
            # accept path, so dropping unconditionally is safe.
            _RUNTIME_REFS.pop(response_id, None)

        # Suspend — task stays alive for next turn in steerable mode
        if self._options.steerable_conversations:
            return await ctx.suspend(reason="awaiting_next_turn")

    async def start_durable(
        self,
        *,
        record: "ResponseExecution",
        ctx_params: dict[str, Any],
    ) -> bool:
        """Start the durable task for a background response.

        Called by _ResponseOrchestrator.run_background() when durable_background=True.
        The task takes over responsibility for execution and crash recovery.

        :param record: The mutable execution record (same as non-durable path).
        :param ctx_params: Execution parameters dict containing all values needed
            by _run_background_non_stream plus object references.
        :returns: True if task was freshly started, False if input was queued
            on an already-active steerable task.
        """
        task_id = derive_task_id(
            agent_name=ctx_params.get("agent_name", "default"),
            session_id=ctx_params.get("session_id", ""),
            conversation_id=ctx_params.get("conversation_id"),
            previous_response_id=ctx_params.get("previous_response_id"),
            response_id=ctx_params["response_id"],
            steerable=self._options.steerable_conversations,
        )

        try:
            # (Spec 013 US1(c)) Split ctx_params into in-memory refs and
            # JSON-serializable persisted params. The durable task input only
            # contains the persisted subset; the refs live in the process-
            # local cache and are looked up by response_id in the task body.
            response_id = ctx_params["response_id"]
            refs, persisted = _split_runtime_refs(ctx_params)
            _RUNTIME_REFS[response_id] = refs

            start_kwargs: dict[str, Any] = {
                "task_id": task_id,
                "input": persisted,
            }
            # (Spec 013 US2) Steerable conversations: forbid forks via the
            # input-precondition primitive. The current input id is the
            # caller-supplied response_id; the precondition is the
            # previous_response_id the caller claims to be branching from.
            # The Responses API contract is "previous_response_id must be the
            # most recent turn" — wire this directly to the input-precondition
            # primitive so the framework enforces it atomically with the
            # accept path. Maps to FR-***/SC-021 in spec 013.
            if self._options.steerable_conversations:
                if response_id is not None:
                    start_kwargs["input_id"] = response_id
                    previous_response_id = ctx_params.get("previous_response_id")
                    if previous_response_id is not None:
                        start_kwargs["if_last_input_id"] = previous_response_id
            task_run = await self._task_fn.start(**start_kwargs)
            # Store the task run reference on the record for observability
            record.durable_task_run = task_run  # type: ignore[attr-defined]
            return True  # Freshly started
        except TaskConflictError:
            # Task already running (e.g. steerable conversation in progress)
            # This is expected for steerable mode — the input is queued
            logger.debug(
                "Task %s already active — input queued for steering",
                task_id,
            )
            return False  # Input queued on existing task

    async def _run_bookkeeping_body(
        self,
        ctx: "TaskContext[dict[str, Any]]",
        response_id: str,
    ) -> None:
        """Run the fresh-entry bookkeeping body for Row 2 / Row 3 tasks.

        The handler is running externally (Row 2: ``asyncio.create_task`` in
        ``run_background``; Row 3: synchronously inside ``run_sync`` /
        ``_live_stream``). This body just keeps the durable task in the
        ``in_progress`` state until one of:

        - ``complete_bookkeeping_task(response_id)`` is called after the
          handler emits its terminal and the response store write
          completes — the task body returns cleanly and the task is
          marked ``completed``.
        - ``ctx.shutdown`` fires (graceful shutdown) — the body proactively
          calls ``_persist_crash_failed`` (idempotent — skips overwrite if
          terminal already persisted) then returns, marking the task
          ``completed`` so it doesn't block shutdown.
        - The process is SIGKILL'd — no chance to clean up. Task stays
          ``in_progress`` and the next-lifetime recovery scanner reclaims
          it (the ``mark-failed`` branch of ``_execute_in_task`` runs).

        :param ctx: The durable task context (provides ``cancel`` /
            ``shutdown`` events).
        :param response_id: The response identifier (key into the
            module-level completion event registry).
        """
        completion_event = asyncio.Event()
        _BOOKKEEPING_EVENTS[response_id] = completion_event
        try:
            completion_task = asyncio.create_task(completion_event.wait())
            cancel_task = asyncio.create_task(ctx.cancel.wait())
            shutdown_task = asyncio.create_task(ctx.shutdown.wait())
            try:
                done, pending = await asyncio.wait(
                    {completion_task, cancel_task, shutdown_task},
                    return_when=asyncio.FIRST_COMPLETED,
                )
                for task in pending:
                    task.cancel()
            except asyncio.CancelledError:
                completion_task.cancel()
                cancel_task.cancel()
                shutdown_task.cancel()
                raise

            if completion_task in done:
                # Handler emitted terminal + store write completed.
                # Return cleanly; task marked completed.
                return

            # ctx.cancel or ctx.shutdown fired before completion. Proactively
            # mark the response failed via the idempotent
            # _persist_crash_failed helper.
            await self._persist_crash_failed(response_id, ctx.input)
            return
        finally:
            _BOOKKEEPING_EVENTS.pop(response_id, None)

    def complete_bookkeeping_task(self, response_id: str) -> None:
        """Signal the bookkeeping task body for ``response_id`` to complete.

        Called by the orchestrator from the handler's terminal-persist hook
        once the response is durably written to the response store. If no
        bookkeeping task is registered for this response_id (e.g. Row 1
        which uses the re-invoke disposition, or any non-store path), this
        is a no-op.

        :param response_id: The response identifier.
        """
        event = _BOOKKEEPING_EVENTS.get(response_id)
        if event is not None:
            event.set()

    async def _persist_crash_failed(
        self,
        response_id: str,
        params: dict[str, Any],
    ) -> None:
        """Persist a response as ``failed`` after crash recovery.

        Used by the next-lifetime recovery path for tasks with
        ``disposition="mark-failed"`` (Rows 2 and 3 of the durability
        matrix). Both rows cannot be re-invoked on recovery —
        Row 2 (bg+store, durable_background=False) opted out of crash
        recovery; Row 3 (fg+store) has no live HTTP request to stream
        events back to. The recovered task body marks the response
        ``failed`` via the generic ``server_error`` code (path-specific
        cause in ``message``, per ``durability-contract.md`` § Glossary).

        Idempotent against a completed-response race (T-066): if the
        response already exists in the store with a terminal status, the
        crash happened AFTER terminal persistence and BEFORE the
        bookkeeping task could be marked complete. In that case the
        ``server_error`` marker would corrupt a valid completed response,
        so we skip the overwrite and return cleanly. The next-lifetime
        recovery scanner still marks the bookkeeping task as completed
        when the body returns, removing it from future recovery scans.

        Handles both create (response was never persisted — handler
        crashed before terminal) and update (response was persisted at
        ``response.created`` for bg+stream but the terminal never landed)
        cases.

        :param response_id: The response identifier.
        :param params: The task input params (used to extract
            isolation context for storage routing).
        """
        from ..models._generated import (
            ResponseObject,
        )  # pylint: disable=import-outside-toplevel

        _TERMINAL_STATUSES = {"completed", "failed", "cancelled", "incomplete"}

        isolation = None
        context = params.get("_context_ref")
        if context is not None:
            isolation = getattr(context, "isolation", None)

        # (Spec 014 T-066) Race-safe idempotent check. If the store already
        # holds a terminal response for this id, leave it alone — the crash
        # happened after terminal persistence, and overwriting would corrupt
        # the result.
        try:
            existing = await self._provider.get_response(
                response_id, isolation=isolation
            )
            existing_status = getattr(existing, "status", None) or (
                existing.get("status") if isinstance(existing, dict) else None
            )
            if (
                isinstance(existing_status, str)
                and existing_status in _TERMINAL_STATUSES
            ):
                logger.info(
                    "_persist_crash_failed: response %s already terminal "
                    "(status=%s) — skipping overwrite (race avoidance)",
                    response_id,
                    existing_status,
                )
                return
        except KeyError:
            # Response not yet in store (handler crashed before terminal).
            pass
        except Exception:  # pylint: disable=broad-exception-caught
            # Other store errors — swallow and try the write below; the
            # write will report its own error.
            pass

        failed_response = _build_server_error_payload(
            response_id,
            shutdown_reason="crash_recovery",
            message="Server crashed during response execution",
        )

        try:
            await self._provider.update_response(
                ResponseObject(failed_response), isolation=isolation
            )
        except KeyError:
            # Response was never persisted at response.created — try
            # create instead so the failed terminal still lands.
            try:
                await self._provider.create_response(
                    ResponseObject(failed_response),
                    input_items=[],
                    history_item_ids=None,
                    isolation=isolation,
                )
            except Exception as exc:  # pylint: disable=broad-exception-caught
                logger.error(
                    "_persist_crash_failed: create after update-not-found failed for %s: %s",
                    response_id,
                    exc,
                )
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error(
                "_persist_crash_failed: failed to persist crash-failure for %s: %s",
                response_id,
                exc,
            )
