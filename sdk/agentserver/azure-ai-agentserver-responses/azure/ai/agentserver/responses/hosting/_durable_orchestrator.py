# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Durable orchestrator — wraps existing response execution in the task primitive.

This module bridges the Responses API and the durable tasks system. It creates
a ``@task``-decorated function whose body calls ``_run_background_non_stream``
(the existing pipeline). The developer's handler is unchanged — the task wrapping
is a transparent infrastructure concern.

Architecture (post-spec-024 unification):
  POST /responses → _ResponseOrchestrator.run_background()
    → durable task body → _run_background_non_stream(...)
       (handler runs INSIDE the task body for every store=true row;
        disposition selects re-invoke vs mark-failed recovery).
    → (store=false) → asyncio.create_task(...) fallback for Row 4.
"""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import logging
from typing import TYPE_CHECKING, Any, Callable

from azure.ai.agentserver.core.durable import (
    MultiTurnTask,
    Task,
    TaskContext,
    TaskConflictError,
    multi_turn_task,
    task,
)

from .._options import ResponsesServerOptions
from .._response_context import ResponseExitForRecovery
from ._task_id import derive_task_id

if TYPE_CHECKING:
    from .._response_context import ResponseContext
    from ..models._generated import CreateResponse
    from ..models.runtime import ResponseExecution
    from ..store._base import ResponseProviderProtocol
    from ._orchestrator import _ResponseOrchestrator
    from ._runtime_state import _RuntimeState

logger = logging.getLogger("azure.ai.agentserver.responses.durable")

# Framework-internal metadata namespace (spec 015 FR-005)
_RESPONSES_NS = "_responses"


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
        history_limit=int(params.get("history_limit", runtime_options.default_fetch_history_count)),
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


_RESP_RESPONSE_ID = "response_id"
_RESP_BACKGROUND = "background"
# (Spec 014 FR-003 / FR-004 — Phase 4) Per-task disposition tells the recovery
# scanner what to do on the next-lifetime recovered entry:
#   - "re-invoke": re-run the handler (Row 1: durable_background+bg+store).
#   - "mark-failed": persist a server_error terminal to the response store and
#     complete the task without re-invoking (Rows 2, 3: bg+store with
#     durable_background=False, and fg+store).
_RESP_DISPOSITION = "disposition"
DISPOSITION_REINVOKE = "re-invoke"
DISPOSITION_MARK_FAILED = "mark-failed"


# (Spec 024 Phase 2) `_BOOKKEEPING_EVENTS` module-level registry deleted —
# the bookkeeping pattern is gone. Handlers run inside the task body for
# all rows (Row 1 + Row 2 + Row 3); see SOT §6.4 unified handler-execution
# model.


def _read_disposition(responses_ns: Any) -> str:
    """Read the task disposition from the ``_responses`` framework namespace.

    Defaults to ``DISPOSITION_REINVOKE`` for backward compatibility with
    Phase 3 (Row 1) tasks created before this metadata key existed.

    :param responses_ns: The ``_responses`` namespace (a TaskMetadata
        namespace facade or a plain dict).
    :returns: One of ``DISPOSITION_REINVOKE`` or ``DISPOSITION_MARK_FAILED``.
    :rtype: str
    """
    raw = responses_ns.get(_RESP_DISPOSITION) if responses_ns else None
    if raw in (DISPOSITION_REINVOKE, DISPOSITION_MARK_FAILED):
        return raw
    return DISPOSITION_REINVOKE


def _is_recovered_entry(task_entry_mode: str) -> bool:
    """Return True when the task primitive is re-entering after a crash.

    (Spec 024 Phase 5 — Proposal #10) Task ``resumed`` (new turn
    arriving) is NOT a recovery entry — from the handler developer's
    perspective, a resume is just a new turn. Only ``recovered`` (the
    task body re-entering after the previous lifetime crashed mid-run)
    flips ``context.is_recovery``.
    """
    return task_entry_mode == "recovered"


class DurableResponseOrchestrator:
    """Wraps the existing response execution pipeline in the durable task primitive.

    When ``durable_background=True``, the normal ``asyncio.create_task()`` path
    is replaced by ``task_fn.start()``. The task body reconstructs the execution
    context and calls ``_run_background_non_stream`` — the same function the
    non-durable path uses. This ensures:
    - Zero handler code changes (same create_fn, same ResponseContext)
    - Crash recovery via task primitive lease + re-entry
    - Recovery + steering classifiers flattened directly onto
      :class:`ResponseContext` (spec 024 Phase 5 — Proposal #10/#13)

    :param create_fn: The handler factory (bound ``create_fn`` method).
    :param options: Server options (steerable, etc.).
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

        # Spec 023 — per-request primitive dispatch (SOT §6.6).
        # Two task primitives are registered per deployment; ``_pick_primitive``
        # selects per request based on (conversation_id, previous_response_id,
        # steerable_conversations).
        #
        # Per Constitution Principle V (fail-fast), both registrations happen
        # at __init__ time. If the core wheel does not expose both ``@task``
        # and ``@multi_turn_task`` symbols, the failure surfaces at server
        # startup instead of per-request.
        one_shot, multi_turn = self._create_task_fns()
        self._one_shot_task_fn: Task[dict[str, Any], None] = one_shot
        self._multi_turn_task_fn: MultiTurnTask[dict[str, Any], None] = multi_turn

    @property
    def task_fn(self) -> Task[dict[str, Any], None]:
        """Deprecated single-task accessor — use ``_one_shot_task_fn`` /
        ``_multi_turn_task_fn`` or the ``_pick_primitive`` dispatch instead.

        Kept for backward-compatible introspection by existing unit tests
        that pre-date the spec 023 per-request dispatch refactor; returns
        the one-shot primitive (the registration with the
        ``"responses_durable_background"`` legacy name).
        """
        return self._one_shot_task_fn

    def _create_task_fns(
        self,
    ) -> tuple[
        Task[dict[str, Any], None],
        MultiTurnTask[dict[str, Any], None],
    ]:
        """Register both task primitives this orchestrator dispatches between.

        Returns a tuple ``(one_shot, multi_turn)``:

        - ``one_shot`` is a ``@task``-decorated function used for single-turn
          requests (no ``conversation_id``, no ``previous_response_id`` in
          steerable mode). Auto-deleted on terminal exit (one-shot
          primitives are always ephemeral).
        - ``multi_turn`` is a ``@multi_turn_task``-decorated function used
          for multi-turn / chain requests. Suspends between turns (chain
          persists in ``status="suspended"`` until the next turn arrives).
          Its ``steerable=`` flag matches ``options.steerable_conversations``.

        The task body in both cases delegates to ``_execute_in_task`` —
        the routing branches inside the body handle the disposition / row
        dispatch.
        """
        orchestrator = self

        # ── One-shot primitive ──────────────────────────────────────────
        # Used for rows where the request has neither a conversation_id
        # nor a steerable previous_response_id (SOT §6.6 rows 1-2 / 3).
        # On terminal exit the durable record is auto-deleted (one-shot
        # primitives are always ephemeral). Recovery branches that need
        # to mark the response failed do so via the response store.
        @task(name="responses_durable_one_shot")
        async def _one_shot_response_task(
            ctx: TaskContext[dict[str, Any]],
        ) -> None:
            """One-shot task body — runs the response pipeline once and returns.

            On terminal exit, the durable record is deleted (one-shot
            primitives are always ephemeral). Recovery branches that need
            to mark the response failed do so via the response store
            (which is the authoritative failure record per SOT §7.2)
            and return ``None``; the deleted bookkeeping record is fine
            because the failure marker lives in the response store.
            """
            return await orchestrator._execute_in_task(ctx)  # noqa: RET504

        # ── Multi-turn primitive ────────────────────────────────────────
        # Used for rows where the request has a conversation_id OR a
        # steerable previous_response_id (SOT §6.6 rows 4-7). The chain
        # transitions to ``status="suspended"`` between turns; the next
        # turn's start() resumes the same task. The steerable= flag
        # gates whether mid-turn input is queued (steerable=True) or
        # rejected with TaskConflictError(in_progress) (steerable=False).
        @multi_turn_task(
            name="responses_durable_multi_turn",
            steerable=self._options.steerable_conversations,
        )
        async def _multi_turn_response_task(
            ctx: TaskContext[dict[str, Any]],
        ) -> None:
            """Multi-turn task body — runs one turn of the chain.

            Returning ``None`` is the implicit-suspend signal — the
            framework transitions the chain to ``status="suspended"`` so
            the next turn can resume the same task. Recovery branches
            that need to mark the response failed do so via the response
            store and ``return None`` (a normal end-of-turn signal that
            keeps the chain alive for subsequent turns).
            """
            return await orchestrator._execute_in_task(ctx)  # noqa: RET504

        return _one_shot_response_task, _multi_turn_response_task

    def _pick_primitive(
        self,
        ctx_params: dict[str, Any],
    ) -> "Task[dict[str, Any], None] | MultiTurnTask[dict[str, Any], None]":
        """Select the underlying durable-task primitive for this request.

        Implements the SOT §6.6 / spec-021 §7.3 matrix:

        - ``conversation_id`` present → multi-turn primitive (chain
          semantics regardless of ``steerable_conversations``).
        - ``previous_response_id`` present AND
          ``steerable_conversations=True`` → multi-turn primitive
          (steerable chain extension).
        - Otherwise → one-shot primitive (no chain semantics needed).

        :param ctx_params: The orchestrator's combined params dict.
        :returns: One of ``self._one_shot_task_fn`` /
            ``self._multi_turn_task_fn``.
        """
        conv_id = ctx_params.get("conversation_id")
        prev_id = ctx_params.get("previous_response_id")
        if conv_id is not None:
            return self._multi_turn_task_fn
        if prev_id is not None and self._options.steerable_conversations:
            return self._multi_turn_task_fn
        return self._one_shot_task_fn

    async def _execute_in_task(self, ctx: TaskContext[dict[str, Any]]) -> None:
        """Execute the response pipeline inside the task body.

        This is the re-entrant function. On each entry:
        1. Flattens recovery + steering classifiers onto the response context.
        2. Bridges task primitive cancellation surface
           (``ctx.cancel`` / ``ctx.shutdown``) onto the per-request
           handler-facing ``cancellation_signal`` Event and the
           ``context.shutdown`` Event respectively. The two surfaces
           are independent — shutdown does not fire the cancel signal.
        3. Delegates to _run_background_non_stream (existing pipeline).
        4. Suspends (task stays alive for next turn).
        """
        # Import here to avoid circular imports
        from ._orchestrator import (
            _run_background_non_stream,
        )  # pylint: disable=import-outside-toplevel

        params = ctx.input
        is_recovery = _is_recovered_entry(ctx.entry_mode)

        # The _responses namespace holds all framework-internal state for
        # this conversation (response_id, background, disposition, etc.).
        # Per spec 015 FR-005, this namespace is reserved (the `_` prefix
        # indicates framework-only). The handler-facing
        # ``conversation_chain_metadata`` facade rejects access to it; framework
        # code (this orchestrator) uses the underlying
        # ``TaskContext.metadata`` directly which has no such restriction.
        responses_ns = ctx.metadata(_RESPONSES_NS)

        # Track response_id in framework metadata
        response_id = params["response_id"]
        if responses_ns.get(_RESP_RESPONSE_ID) is None:
            responses_ns[_RESP_RESPONSE_ID] = response_id

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
        if _RESP_BACKGROUND not in responses_ns:
            responses_ns[_RESP_BACKGROUND] = params.get("background", True)

        # (Spec 014 FR-003 / FR-004) Stamp the disposition on first entry so
        # next-lifetime recovery can dispatch correctly without needing to
        # reconstruct the routing decisions from input params.
        if _RESP_DISPOSITION not in responses_ns:
            responses_ns[_RESP_DISPOSITION] = params.get("disposition", DISPOSITION_REINVOKE)
            # Force-flush so the disposition is durable BEFORE the body
            # could be killed — without an explicit flush the recovered
            # task would default to ``re-invoke`` and skip the mark-failed
            # branch.
            try:
                await responses_ns.flush()
            except (AttributeError, Exception):  # noqa: BLE001
                pass  # best-effort — backend may not support explicit flush
        disposition = _read_disposition(responses_ns)

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
            # Spec 023: implicit-suspend via bare ``return None`` (the
            # framework records the suspend transition automatically for
            # multi_turn_task bodies). The response store's ``failed``
            # terminal that we just persisted is the authoritative failure
            # record per SOT §7.2.
            return None

        # Backward-compat: the pre-disposition non-background recovery branch.
        # Tasks created before the disposition key existed default to
        # DISPOSITION_REINVOKE; for those, preserve the prior behaviour of
        # marking foreground responses failed on recovery without re-invoking.
        if is_recovery and not responses_ns.get(_RESP_BACKGROUND, True):
            logger.info(
                "Non-background task recovered (response_id=%s) — marking failed",
                response_id,
            )
            await self._persist_crash_failed(response_id, params)
            # Spec 023: implicit-suspend via bare ``return None`` (see above).
            return None

        # (Spec 024 Phase 2 — bookkeeping unification) On fresh entry, the
        # handler ALWAYS runs inside the task body, regardless of disposition.
        # The disposition only affects RECOVERY behaviour:
        #   - re-invoke: recovery re-runs the handler (already returned above
        #     via the fresh-entry path, but with is_recovery=True).
        #   - mark-failed: recovery persists server_error + returns (handled
        #     above at the `if is_recovery and disposition == DISPOSITION_MARK_FAILED`
        #     branch).
        # The legacy `if not is_recovery and disposition == DISPOSITION_MARK_FAILED:`
        # branch that ran `_run_bookkeeping_body` is deleted — the handler
        # now executes inside the task body for all rows. SOT §6.5 (the
        # bookkeeping pre-registration pattern) is gone.

        # (Spec 024 Phase 5 — Proposal #10/#13) Flatten recovery +
        # steering classifiers onto the handler-facing response context.
        # The pre-Phase-5 ``DurabilityContext`` indirection is deleted;
        # handlers read these fields directly off ``context``.
        context: ResponseContext | None = _ref("_context_ref")

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
            assert record is not None, "_reconstruct_from_params guarantees non-None record"
            assert self._runtime_state is not None, "runtime_state always wired at orchestrator init"
            await self._runtime_state.add(record)

        # After the reconstruction block, context and record are both
        # guaranteed non-None (either set from refs in the same-process
        # case, or built from serialized params in the cross-process
        # recovery case). Narrow for the type checker.
        assert context is not None, "context is non-None after reconstruction"
        assert record is not None, "record is non-None after reconstruction"

        if context is not None:
            context.is_recovery = is_recovery
            context.is_steered_turn = ctx.is_steered_turn
            context.pending_input_count = ctx.pending_input_count
            # Swap in the handler-facing metadata facade backed by the
            # task primitive's metadata wrapper. The facade rejects keys
            # starting with ``_`` so handlers cannot collide with the
            # framework-reserved ``_responses`` namespace; framework
            # code reaches that namespace via ``ctx.metadata`` directly.
            from .._durability_context import (  # pylint: disable=import-outside-toplevel
                _DeveloperMetadataFacade,
            )

            context.conversation_chain_metadata = _DeveloperMetadataFacade(ctx.metadata)
            # (Spec 024 Phase 5 — Proposal #11) Expose the task context
            # so ``context.exit_for_recovery()`` can delegate to the
            # framework's recovery sentinel.
            context._task_context = ctx  # pylint: disable=protected-access

            # (Spec 025 §A.3) On a recovered entry, pre-fetch the persisted
            # response so the handler can seed its stream from already-
            # persisted items + the response-level watermark. Entry-only:
            # never refreshed mid-execution.
            #
            # (Spec 026 FR-026-4/5/6) Recovery is only meaningful when the
            # response was durably created in the store. If it is DEFINITIVELY
            # absent (typed not-found), the original POST disconnected without
            # ever returning a response id, so no client can fetch it — drop
            # the durable execution (do NOT re-invoke the handler). Returning
            # here settles the task (the recovery scan selects ``in_progress``
            # records; a settled record is not re-selected), so this is not
            # retried indefinitely. A transient/ambiguous error is NOT a
            # definitive absence and MUST NOT drop — proceed with
            # ``persisted_response=None``.
            if is_recovery:
                from ..store._foundry_errors import (  # pylint: disable=import-outside-toplevel
                    FoundryResourceNotFoundError,
                )

                try:
                    _isolation = context.isolation
                    context.persisted_response = await self._provider.get_response(
                        context.response_id, isolation=_isolation
                    )
                except (KeyError, FoundryResourceNotFoundError):
                    logger.info(
                        "Recovery dropped for %s: response was never durably "
                        "created (definitive not-found); abandoning durable "
                        "execution without re-invoking the handler.",
                        context.response_id,
                    )
                    return
                except Exception:  # pylint: disable=broad-exception-caught
                    logger.debug(
                        "persisted_response pre-fetch failed for %s " "(recovery, transient — not dropping)",
                        context.response_id,
                        exc_info=True,
                    )
                    context.persisted_response = None

        # Bridge task cancellation → response cancellation surface.
        # ``ctx.cancel`` (steering / explicit cancel) and ``ctx.shutdown``
        # (graceful TaskManager shutdown) are mapped to DISTINCT
        # surfaces on the handler-facing ``ResponseContext``:
        #
        # - ``ctx.shutdown`` fires → ``context.shutdown.set()`` ONLY.
        #   The cancellation signal is NOT fired; shutdown demands a
        #   different handler response (``exit_for_recovery()`` or
        #   terminal emit), so it must be observed via
        #   ``context.shutdown`` independently.
        # - ``ctx.cancel`` fires from steering pressure →
        #   ``cancellation_signal.set()`` with NO cause boolean
        #   (handlers see only the wake-up; matches task primitive
        #   contract where steering pressure has no named cause).
        # - ``ctx.cancel`` fires from an explicit /cancel API call or
        #   from non-bg POST disconnect → those mutate
        #   ``context.client_cancelled`` at the HTTP boundary, BEFORE
        #   propagating through ``ctx.cancel`` here. The bridge below
        #   does NOT clobber an existing ``client_cancelled=True``.
        cancellation_signal: asyncio.Event = _ref("_cancel_ref") or asyncio.Event()
        cancel_bridge: asyncio.Task[None] | None = None
        if ctx.shutdown.is_set():
            if context is not None:
                context.shutdown.set()
        elif ctx.cancel.is_set():
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
                    for t in pending:
                        t.cancel()
                    if shutdown_task in done and cancel_task not in done:
                        if context is not None:
                            context.shutdown.set()
                    else:
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
                    background=bool(params.get("background", True)),
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

            # Spec 023 — If the handler returned without emitting a
            # terminal event AND graceful shutdown is in progress,
            # explicitly signal the framework to leave the task
            # ``status="in_progress"`` for next-lifetime recovery.
            #
            # We use ``ctx.exit_for_recovery()`` (the framework's
            # graceful-shutdown primitive) rather than raising
            # ``CancelledError`` because:
            # - For multi-turn primitives both work, but
            #   ``exit_for_recovery`` is the documented public API.
            # - For one-shot (ephemeral) primitives, ``CancelledError``
            #   triggers the cancel-delete branch in the core manager
            #   — the record gets DELETED, and the recovery scanner
            #   finds nothing. ``exit_for_recovery`` releases the lease
            #   without deleting, so the recovery scanner can re-fire
            #   the task on the next process startup.
            #
            # Without this distinction, Row 1 Path B (graceful shutdown
            # mid-handler with grace exhausted) silently loses the
            # response because the one-shot ephemeral record is deleted
            # on cancel.
            if ctx.shutdown.is_set() and record is not None and record.status in {"queued", "in_progress"}:
                logger.info(
                    "Response %s handler returned during shutdown without "
                    "terminal; calling ctx.exit_for_recovery() so task stays "
                    "in_progress for next-lifetime recovery.",
                    response_id,
                )
                return await ctx.exit_for_recovery()
        except ResponseExitForRecovery:
            # Spec 025 §A.4 — the handler called
            # ``await context.exit_for_recovery()`` (any handler shape),
            # which raises ``ResponseExitForRecovery``. Translate it to the
            # framework's task-level recovery primitive so the task stays
            # ``in_progress`` for next-lifetime recovery (same disposition as
            # the implicit shutdown bare-return fallback above).
            logger.info(
                "Response %s handler invoked context.exit_for_recovery(); "
                "calling ctx.exit_for_recovery() so task stays in_progress "
                "for next-lifetime recovery.",
                response_id,
            )
            return await ctx.exit_for_recovery()
        finally:
            if cancel_bridge is not None and not cancel_bridge.done():
                cancel_bridge.cancel()
            # (Spec 013 US1(c)) On terminal exit of the task body (handler
            # returned), drop the runtime-refs entry to release memory. On
            # suspend the entry would still be useful for in-process resume,
            # but it'll be rebuilt at the next `start_durable` from the
            # accept path, so dropping unconditionally is safe.
            _RUNTIME_REFS.pop(response_id, None)

        # Spec 023: implicit-suspend via bare ``return None``. For
        # multi_turn_task bodies the framework records the suspend
        # transition automatically; for one-shot @task bodies the
        # framework marks the task ``completed`` and deletes the record
        # (ephemeral). The per-request primitive dispatch in
        # ``start_durable`` picks the correct primitive so the lifecycle
        # transition matches the row's expected behaviour without any
        # explicit ``ctx.suspend(reason=...)`` call here.
        return None

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

        # Spec 023 — per-request primitive dispatch (SOT §6.6).
        # Selects between the one-shot ``@task`` primitive (auto-deleted
        # on terminal exit; no chain semantics) and the multi-turn
        # ``@multi_turn_task`` primitive (suspends between turns; chain
        # semantics) based on the request's conversation_id /
        # previous_response_id / steerable_conversations tuple.
        picked_primitive = self._pick_primitive(ctx_params)
        is_multi_turn = picked_primitive is self._multi_turn_task_fn

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
        # Multi-turn chain primitives carry per-turn ``input_id`` for
        # idempotency on response_id, and ``if_last_input_id`` for the
        # chain-extension precondition (forks rejected as
        # ``LastInputIdPreconditionFailed``). One-shot primitives need
        # neither — they have no chain to extend; the task_id IS the
        # identifier and the request fork model produces a distinct
        # task_id per request.
        if is_multi_turn:
            if response_id is not None:
                start_kwargs["input_id"] = response_id
            previous_response_id = ctx_params.get("previous_response_id")
            if previous_response_id is not None:
                start_kwargs["if_last_input_id"] = previous_response_id

        # ``TaskConflictError`` from the underlying primitive ALWAYS signals
        # a real conflict (concurrent overlap on a multi-turn-non-steerable
        # chain, OR a duplicate task_id collision). It propagates up to the
        # endpoint handler which maps it to HTTP 409 ``conversation_locked``.
        # Under the new model the steerable-input-queuing case does NOT
        # raise TaskConflictError — ``MultiTurnTask(steerable=True).start()``
        # auto-queues against an in-flight chain and returns a TaskRun
        # whose ``_queued_cancel_callback`` is set (the public-surface
        # detection signal). See the queued-vs-fresh check below.
        task_run = await picked_primitive.start(**start_kwargs)
        # Store the task run reference on the record for observability
        record.durable_task_run = task_run  # type: ignore[attr-defined]

        # Detect "queued steering input" via the TaskRun's queued-cancel
        # callback. The framework installs this callback ONLY when the
        # returned handle represents a queued (not-yet-promoted) input on
        # a steerable chain — i.e. the caller's request landed mid-turn
        # and is awaiting drain. Returning False here signals the caller
        # to dispatch the acceptance hook and return a ``status="queued"``
        # response envelope to the HTTP caller.
        # NOTE: this reads a private TaskRun attribute. If the core ever
        # adds a public ``is_queued`` property, switch to that.
        is_queued = getattr(task_run, "_queued_cancel_callback", None) is not None
        return not is_queued  # True = freshly started, False = queued

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
        durable task body could return. In that case the
        ``server_error`` marker would corrupt a valid completed response,
        so we skip the overwrite and return cleanly. The next-lifetime
        recovery scanner still marks the task as completed when the body
        returns, removing it from future recovery scans.

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
            existing = await self._provider.get_response(response_id, isolation=isolation)
            existing_status = getattr(existing, "status", None) or (
                existing.get("status") if isinstance(existing, dict) else None
            )
            if isinstance(existing_status, str) and existing_status in _TERMINAL_STATUSES:
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
            await self._provider.update_response(ResponseObject(failed_response), isolation=isolation)
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
