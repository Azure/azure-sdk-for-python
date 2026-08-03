# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Resilient orchestrator — wraps existing response execution in the task primitive.

This module bridges the Responses API and the resilient tasks system. It creates
a ``@task``-decorated function whose body calls ``_run_background_non_stream``
(the existing pipeline). The developer's handler is unchanged — the task wrapping
is a transparent infrastructure concern.

Architecture (post-spec-024 unification):
  POST /responses → _ResponseOrchestrator.run_background()
    → resilient task body → _run_background_non_stream(...)
       (handler runs INSIDE the task body for every store=true row;
        disposition selects re-invoke vs mark-failed recovery).
    → (store=false) → asyncio.create_task(...) fallback for Row 4.
"""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import logging
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Callable, cast

from azure.ai.agentserver.core.tasks import (
    MultiTurnTask,
    Task,
    TaskContext,
    multi_turn_task,
    task,
)

from .._options import ResponsesServerOptions
from .._response_context import ResponseExitForRecovery
from ._dispatch import DISPOSITION_MARK_FAILED
from ._task_id import derive_task_id

if TYPE_CHECKING:
    from .._response_context import ConversationChainMetadataNamespace, ResponseContext
    from ..models._generated import CreateResponse, ResponseObject
    from ..models.runtime import ResponseExecution
    from ..store._base import ResponseProviderProtocol
    from ._orchestrator import _ResponseOrchestrator
    from ._runtime_state import _RuntimeState
    from ._resilient_input import ResilientResponseInput, RuntimeRefs

logger = logging.getLogger("azure.ai.agentserver.responses.agentserver")


def _server_error_message(shutdown_reason: str) -> str:
    """Return the canonical user-visible ``error.message`` for a shutdown/crash
    marker, keyed by ``shutdown_reason``.

    Single source of truth so the overlay path and the synthesize path emit an
    identical message (and match ``docs/responses-resilience-spec.md`` §7.3).

    :param shutdown_reason: ``"crash_recovery"`` or ``"grace_exhausted"``.
    :type shutdown_reason: str
    :returns: The human-readable error message.
    :rtype: str
    """
    if shutdown_reason == "crash_recovery":
        return "Server interrupted before completing this response"
    if shutdown_reason == "grace_exhausted":
        return "Server stopped before this response completed"
    return "Server failed to complete this response"


def _build_server_error_payload(
    response_id: str,
    *,
    shutdown_reason: str,
    message: str | None = None,
    agent_reference: dict[str, Any] | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    """Build the response-failed payload for crash / shutdown markers.

    Single source of truth for the failure payload format. The ``error`` object
    matches the SOT ``ResponseError`` shape exactly — ``code`` (the generic
    ``"server_error"``, as used elsewhere in the codebase) + ``message`` (the
    path-specific human-readable cause). No ``type`` or ``additionalInfo`` is
    set: the SOT ``ResponseError`` (unlike the HTTP error envelope) carries only
    ``code`` and ``message``, and the internal ``shutdown_reason`` is not
    surfaced to customers (it selects the message and is available in logs).

    :param response_id: The response identifier.
    :type response_id: str
    :keyword shutdown_reason: One of ``"crash_recovery"`` (next-lifetime
        marker for SIGKILL / lost-process recovery) or ``"grace_exhausted"``
        (in-process marker fired during graceful shutdown). Selects the
        default ``message`` (internal-only; not surfaced on the payload).
    :paramtype shutdown_reason: str
    :keyword message: Optional override for the human-readable
        ``error.message``. If omitted, a path-specific default is used.
    :paramtype message: str | None
    :keyword agent_reference: The persisted agent reference (``name`` +
        ``version``). The Foundry storage API validates that every
        ``update_response`` / ``create_response`` body carries an agent
        reference and rejects the write when it is missing, so the crash
        marker MUST stamp it or the failed terminal never persists and the
        response stays ``in_progress`` forever.
    :paramtype agent_reference: dict[str, Any] | None
    :keyword model: Optional model identifier, mirrored onto the marker for
        parity with the canonical ``build_failed_response`` shape.
    :paramtype model: str | None
    :returns: A response-failed dict suitable for persisting via
        ``ResponseProviderProtocol.update_response``.
    :rtype: dict[str, Any]
    """
    if message is None:
        message = _server_error_message(shutdown_reason)
    return {
        "id": response_id,
        "response_id": response_id,
        "agent_reference": deepcopy(agent_reference) if agent_reference else {},
        "object": "response",
        "status": "failed",
        "model": model,
        "output": [],
        "error": {
            "code": "server_error",
            "message": message,
        },
    }


def _agent_reference_from_params(params: dict[str, Any]) -> dict[str, Any] | None:
    """Extract the persisted agent reference (``name`` + ``version``) from the
    resilient task input.

    The Foundry storage API validates that every write carries an agent
    reference, so the crash-failed marker must stamp it. The value is the
    normalized ``{type, name, version}`` dict persisted under
    ``_K_AGENT_REFERENCE``.

    :param params: The persisted task input params.
    :type params: dict[str, Any]
    :returns: The agent-reference dict, or ``None`` when absent.
    :rtype: dict[str, Any] | None
    """
    agent_reference = params.get("agent_reference")
    if isinstance(agent_reference, dict) and agent_reference:
        return agent_reference
    return None


def _model_from_params(params: dict[str, Any]) -> str | None:
    """Extract the model identifier from the persisted request, for parity with
    the canonical failed-response shape.

    :param params: The persisted task input params.
    :type params: dict[str, Any]
    :returns: The model string, or ``None`` when absent.
    :rtype: str | None
    """
    request = params.get("request")
    if isinstance(request, dict):
        model = request.get("model")
        if isinstance(model, str):
            return model
    return None


def _overlay_failed_terminal(
    snapshot: "ResponseObject",
    *,
    shutdown_reason: str,
    message: str | None = None,
) -> "ResponseObject":
    """Overlay a ``failed`` terminal onto a persisted response snapshot.

    Per ``docs/responses-resilience-spec.md`` §7.2/§7.3 the crash-failed
    marker MUST preserve the developer's persisted response object — its
    ``agent_reference``, ``model``, the ``output`` accumulated and durably
    persisted before the crash, ``created_at``, and any other fields — and
    only set ``status="failed"`` with the ``server_error`` error attached.
    The persisted snapshot is the authoritative record of what was durably
    accomplished; the failure is layered on top of it rather than discarding
    it. Preserving the snapshot also satisfies the store's mandatory
    ``agent_reference`` requirement by construction.

    :param snapshot: The persisted (non-terminal) response snapshot.
    :type snapshot: ResponseObject
    :keyword shutdown_reason: Selects the default ``error.message``
        (internal-only; not surfaced on the payload).
    :paramtype shutdown_reason: str
    :keyword message: Optional override for ``error.message``. Defaults to the
        canonical message for ``shutdown_reason``.
    :paramtype message: str | None
    :returns: A copy of the snapshot transitioned to ``failed``.
    :rtype: ResponseObject
    """
    from ..models._runtime import apply_failed_terminal  # pylint: disable=import-outside-toplevel
    from ..models._generated import ResponseObject  # pylint: disable=import-outside-toplevel

    error = {
        "code": "server_error",
        "message": message if message is not None else _server_error_message(shutdown_reason),
    }
    return cast(ResponseObject, apply_failed_terminal(snapshot, error=error))


# (Spec 033 §3.1) Process-local cache of typed :class:`RuntimeRefs` (record,
# context, parsed request, cancellation signal, runtime state), keyed by
# response_id. These object references cannot be JSON-serialized for
# cross-process recovery, so they live here out-of-band and are NEVER part of
# the persisted resilient-task input (which is the typed
# :class:`ResilientResponseInput` alone). The task body fetches refs from this
# cache on same-process re-entry; on cross-process recovery the entry is absent
# and the body rebuilds state from the persisted ``ResilientResponseInput``.
_RUNTIME_REFS: dict[str, "RuntimeRefs"] = {}


def _reconstruct_parsed_from_params(params: dict[str, Any]) -> Any:
    """Re-parse the persisted request back to a ``CreateResponse`` model.

    Used on cross-process recovery when the in-process ``_parsed_ref`` is
    unavailable. Routes through the single :class:`ResilientResponseInput`
    deserializer (Spec 033 §3.1) — the request is persisted once, under the
    ``request`` key, inside the typed resilient-task input.

    :param params: The resilient task input dict.
    :type params: dict[str, Any]
    :returns: The re-hydrated ``CreateResponse`` request model.
    :rtype: Any
    :raises ValueError: If the persisted input is missing the required request.
    """
    from ._resilient_input import (
        ResilientResponseInput,
    )  # pylint: disable=import-outside-toplevel

    return ResilientResponseInput.from_task_input(params).request


def _reconstruct_from_params(
    *,
    params: dict[str, Any],
    response_id: str,
    provider: "ResponseProviderProtocol | None",
    runtime_state: "_RuntimeState | None",  # pylint: disable=unused-argument
    runtime_options: ResponsesServerOptions,
) -> tuple["ResponseExecution", "ResponseContext"]:
    """Rebuild ResponseExecution and ResponseContext from the resilient task input.

    Called on cross-process recovery when ``_record_ref`` is missing.
    All inputs are derived from the serialized ``params`` dict that the
    orchestrator stamped at fresh-entry time.

    :keyword params: The resilient task input.
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
    from .._response_context import (
        ResponseContext,
    )  # pylint: disable=import-outside-toplevel
    from ..models.runtime import (
        ResponseExecution,
        ResponseModeFlags,
    )  # pylint: disable=import-outside-toplevel
    from ..models._helpers import (
        get_input_expanded,
        to_output_item,
    )  # pylint: disable=import-outside-toplevel
    from ._request_parsing import (
        _extract_agent_identity,
        _resolve_conversation_id,
    )  # pylint: disable=import-outside-toplevel
    from ._resilient_input import (
        ResilientResponseInput,
    )  # pylint: disable=import-outside-toplevel

    # Single deserializer (Spec 033 FR-001): the persisted boundary is read in
    # exactly one place. Raises if the persisted input is malformed (FR-002f).
    resilient = ResilientResponseInput.from_task_input(params)
    request = resilient.request

    # Re-derive the request-scoped scalars from the persisted request — these are
    # pure sync functions of the request, identical to fresh entry
    # (``_endpoint_handler._build_execution_context`` / ``_resolve_conversation_id``).
    # No parallel persisted scalars to drift (Spec 033 §3.1).
    stream = bool(request.get("stream", False))
    store = True if request.get("store") is None else bool(request.get("store"))
    background = bool(request.get("background", False))
    model = request.get("model") or ""
    previous_response_id = (
        request.get("previous_response_id")
        if isinstance(request.get("previous_response_id"), str) and request.get("previous_response_id")
        else None
    )
    conversation_id = _resolve_conversation_id(request)
    # Input is embedded once, in the request; reconstruct the resolved input
    # items from it exactly as fresh entry does (Spec 033 FR-002).
    input_items = [
        out for item in get_input_expanded(request) if (out := to_output_item(item, response_id)) is not None
    ]

    record = ResponseExecution(
        response_id=response_id,
        mode_flags=ResponseModeFlags(
            stream=stream,
            store=store,
            background=background,
        ),
        status="in_progress",
        input_items=input_items,
        previous_response_id=previous_response_id,
        initial_model=model,
        initial_agent_reference=resilient.agent_reference,
        agent_session_id=resilient.agent_session_id,
        conversation_id=conversation_id,
        user_id_key=resilient.user_id_key,
    )

    context = ResponseContext(
        response_id=response_id,
        mode_flags=record.mode_flags,
        request=request,
        provider=provider,
        input_items=record.input_items,
        previous_response_id=record.previous_response_id,
        conversation_id=record.conversation_id,
        history_limit=int(runtime_options.default_fetch_history_count),
        # (Spec 033 FR-002b) Request metadata MUST survive recovery so the
        # recovered handler observes the identical headers/query it would on
        # fresh entry. Previously hard-set to ``{}`` — a latent drop bug.
        client_headers=dict(resilient.client_headers),
        query_parameters=dict(resilient.query_parameters),
        platform_context=resilient.platform_context(),
        # History is a prefetch optimization; re-derived on demand via the
        # existing ``get_history_item_ids`` read (Spec 033 §3.1).
        prefetched_history_ids=None,
        # (Spec 036) Recovery must reconstruct the SAME chain identity as fresh
        # entry: pass steerable + agent/session so ``conversation_chain_id`` is
        # stable across crash recovery. Previously ``steerable`` defaulted to
        # False here, diverging the chain id for previous_response_id chains.
        steerable=bool(getattr(runtime_options, "steerable_conversations", False)),
        agent_name=_extract_agent_identity(resilient.agent_reference)[0],
        session_id=resilient.agent_session_id or "",
    )
    record.response_context = context
    return record, context


# (Spec 014 FR-003 / FR-004 — Phase 4) Per-task disposition tells the recovery
# scanner what to do on the next-lifetime recovered entry:
#   - "re-invoke": re-run the handler (Row 1: resilient_background+bg+store).
#   - "mark-failed": persist a server_error terminal to the response store and
#     complete the task without re-invoking (Rows 2, 3: bg+store with
#     resilient_background=False, and fg+store).
# (Spec 039 R1) The disposition, background flag, and response_id are sourced
# directly from the durable task INPUT (``ResilientResponseInput``, persisted at
# task ``.start()`` — strictly before the body runs), which is the single source
# of truth (matching the .NET port). The former ``_responses`` framework
# metadata namespace that mirrored these three values has been removed.


# (Spec 024 Phase 2) `_BOOKKEEPING_EVENTS` module-level registry deleted —
# the bookkeeping pattern is gone. Handlers run inside the task body for
# all rows (Row 1 + Row 2 + Row 3); see SOT §6.4 unified handler-execution
# model.


def _is_recovered_entry(task_entry_mode: str) -> bool:
    """Return True when the task primitive is re-entering after a crash.

    (Spec 024 Phase 5 — Proposal #10) Task ``resumed`` (new turn
    arriving) is NOT a recovery entry — from the handler developer's
    perspective, a resume is just a new turn. Only ``recovered`` (the
    task body re-entering after the previous lifetime crashed mid-run)
    flips ``context.is_recovery``.

    :param task_entry_mode: The task primitive entry mode.
    :type task_entry_mode: str
    :return: ``True`` when the entry mode represents crash recovery.
    :rtype: bool
    """
    return task_entry_mode == "recovered"


class ResilientResponseOrchestrator:
    """Wraps the existing response execution pipeline in the resilient task primitive.

    When ``resilient_background=True``, the normal ``asyncio.create_task()`` path
    is replaced by ``task_fn.start()``. The task body reconstructs the execution
    context and calls ``_run_background_non_stream`` — the same function the
    non-resilient path uses. This ensures:
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
        # Back-reference to the parent _ResponseOrchestrator so the resilient
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
        ``"responses_resilient_background"`` legacy name).

        :return: The one-shot resilient task primitive.
        :rtype: Task[dict[str, Any], None]
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

        :return: The registered one-shot and multi-turn task primitives.
        :rtype: tuple[Task[dict[str, Any], None], MultiTurnTask[dict[str, Any], None]]
        """
        orchestrator = self

        # ── One-shot primitive ──────────────────────────────────────────
        # Used for rows where the request has neither a conversation_id
        # nor a steerable previous_response_id (SOT §6.6 rows 1-2 / 3).
        # On terminal exit the resilient record is auto-deleted (one-shot
        # primitives are always ephemeral). Recovery branches that need
        # to mark the response failed do so via the response store.
        @task(name="responses_resilient_one_shot")
        async def _one_shot_response_task(
            ctx: TaskContext[dict[str, Any]],
        ) -> None:
            """One-shot task body — runs the response pipeline once and returns.

            On terminal exit, the resilient record is deleted (one-shot
            primitives are always ephemeral). Recovery branches that need
            to mark the response failed do so via the response store
            (which is the authoritative failure record per SOT §7.2)
            and return ``None``; the deleted bookkeeping record is fine
            because the failure marker lives in the response store.

            :param ctx: The resilient task context.
            :type ctx: TaskContext[dict[str, Any]]
            :return: None
            :rtype: None
            """
            return await orchestrator._execute_in_task(ctx)  # noqa: RET504  # pylint: disable=protected-access

        # ── Multi-turn primitive ────────────────────────────────────────
        # Used for rows where the request has a conversation_id OR a
        # steerable previous_response_id (SOT §6.6 rows 4-7). The chain
        # transitions to ``status="suspended"`` between turns; the next
        # turn's start() resumes the same task. The steerable= flag
        # gates whether mid-turn input is queued (steerable=True) or
        # rejected with TaskConflictError(in_progress) (steerable=False).
        @multi_turn_task(
            name="responses_resilient_multi_turn",
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

            :param ctx: The resilient task context.
            :type ctx: TaskContext[dict[str, Any]]
            :return: None
            :rtype: None
            """
            return await orchestrator._execute_in_task(ctx)  # noqa: RET504  # pylint: disable=protected-access

        return _one_shot_response_task, _multi_turn_response_task

    def _pick_primitive(
        self,
        *,
        conversation_id: str | None,
        previous_response_id: str | None,  # pylint: disable=unused-argument
    ) -> "Task[dict[str, Any], None] | MultiTurnTask[dict[str, Any], None]":
        """Select the underlying resilient-task primitive for this request.

        Implements the SOT §6.4 / spec-021 §7.3 matrix:

        - ``conversation_id`` present → multi-turn primitive (chain
          semantics regardless of ``steerable_conversations``).
        - ``steerable_conversations=True`` → multi-turn primitive for
          EVERY turn, including the first (no ``conversation_id``, no
          ``previous_response_id``). The stable ``conversation_chain_id``
          (SOT §4.1) makes the first turn's ``task_id`` SHARED with any
          later steered turn, so the first turn's task must be the
          suspendable chain host that drains queued steering inputs. A
          one-shot here would auto-delete on terminal exit and orphan the
          queued steered turn (SOT §6.1).
        - Otherwise (non-steerable) → one-shot primitive (no chain
          semantics needed; each non-steerable request keeps a distinct
          ``task_id`` via the ``fork:`` / ``resp:`` partition).

        :keyword conversation_id: The request's conversation id, if any.
        :paramtype conversation_id: str | None
        :keyword previous_response_id: The request's previous-response id, if any.
        :paramtype previous_response_id: str | None
        :returns: One of ``self._one_shot_task_fn`` /
            ``self._multi_turn_task_fn``.
        :rtype: Task[dict[str, Any], None] | MultiTurnTask[dict[str, Any], None]
        """
        if conversation_id is not None:
            return self._multi_turn_task_fn
        if self._options.steerable_conversations:
            return self._multi_turn_task_fn
        return self._one_shot_task_fn

    async def _handle_recovery_disposition(
        self,
        *,
        disposition: str,
        is_recovery: bool,
        response_id: str,
        params: dict[str, Any],
        background: bool,
    ) -> bool:
        """Dispatch the mark-failed recovery branch from the durable task input.

        (Spec 033 §3.2 extract; Spec 039 R1) The ``disposition`` and
        ``background`` flag are sourced from the durable task **input**
        (``ResilientResponseInput``), which is persisted at task ``.start()`` —
        strictly before the body's first entry — so no framework metadata mirror
        or explicit flush is needed (the input is the single source of truth,
        matching the .NET port). On a recovered entry with a ``mark-failed``
        disposition (Rows 2/3), persists the ``server_error`` terminal to the
        store **without re-invoking the handler** and signals the caller to
        return.

        :keyword disposition: The task disposition from the input
            (``re-invoke`` / ``mark-failed``).
        :paramtype disposition: str
        :keyword is_recovery: Whether this is a recovered re-entry.
        :paramtype is_recovery: bool
        :keyword response_id: The response id.
        :paramtype response_id: str
        :keyword params: The raw resilient-task input (for platform-context routing on the failed write).
        :paramtype params: dict[str, Any]
        :keyword background: The request's background flag.
        :paramtype background: bool
        :returns: True if the caller should return (mark-failed handled).
        :rtype: bool
        """
        # (Spec 014 FR-003 / FR-004) Recovery dispatch via disposition. mark-failed:
        # the handler does NOT re-run; persist a server_error terminal and complete
        # the task. Covers Rows 2 (bg+store, resilient_background=False) and 3 (fg+store).
        if is_recovery and disposition == DISPOSITION_MARK_FAILED:
            logger.info(
                "Resilient task recovered (response_id=%s, disposition=mark-failed) — marking failed",
                response_id,
            )
            await self._persist_crash_failed(response_id, params)
            return True

        # Non-background recovery — mark foreground responses failed on recovery
        # without re-invoking (no live HTTP connection to stream to).
        if is_recovery and not background:
            logger.info(
                "Non-background task recovered (response_id=%s) — marking failed",
                response_id,
            )
            await self._persist_crash_failed(response_id, params)
            return True

        return False

    async def _flatten_recovery_context(
        self,
        ctx: "TaskContext[dict[str, Any]]",
        context: "ResponseContext",
        is_recovery: bool,
    ) -> bool:
        """Flatten recovery/steering classifiers onto the context + prefetch.

        (Spec 033 §3.2 extract) Sets ``is_recovery`` / ``is_steered_turn`` /
        ``pending_input_count``, swaps in the developer metadata facade, exposes
        the task context, and on a recovered entry pre-fetches the persisted
        response. Returns True when the resilient execution should be **dropped**
        (Spec 026: the response was never resiliently created — definitive not-found).

        :param ctx: The resilient task context.
        :type ctx: TaskContext[dict[str, Any]]
        :param context: The handler-facing response context.
        :type context: ResponseContext
        :param is_recovery: Whether this is a recovered re-entry.
        :type is_recovery: bool
        :returns: True if the caller should drop (return) without re-invoking.
        :rtype: bool
        """
        context.is_recovery = is_recovery
        context.is_steered_turn = ctx.is_steered_turn
        context.pending_input_count = ctx.pending_input_count
        # Swap in the handler-facing metadata facade backed by the task
        # primitive's metadata wrapper (rejects ``_``-prefixed keys so handlers
        # cannot invent framework-reserved namespaces — kept as a defensive
        # guard even though the framework no longer creates a ``_responses``
        # namespace itself, per Spec 039 R1).
        from .._resilience_context import (  # pylint: disable=import-outside-toplevel
            _DeveloperMetadataFacade,
        )

        context.conversation_chain_metadata = cast(
            "ConversationChainMetadataNamespace", _DeveloperMetadataFacade(ctx.metadata)
        )
        # (Spec 024 Phase 5 — Proposal #11) Expose the task context so
        # ``context.exit_for_recovery()`` can delegate to the recovery sentinel.
        context._task_context = ctx  # pylint: disable=protected-access

        if not is_recovery:
            return False

        # (Spec 025 §A.3) Pre-fetch the persisted response so the handler can seed
        # its stream. (Spec 026 FR-026-4/5/6) If the response is DEFINITIVELY
        # absent (typed not-found), the original POST disconnected without
        # returning a response id, so no client can fetch it — drop the resilient
        # execution. A transient/ambiguous error is NOT a definitive absence.
        from ..store._foundry_errors import (  # pylint: disable=import-outside-toplevel
            FoundryResourceNotFoundError,
        )

        try:
            context.persisted_response = await self._provider.get_response(
                context.response_id, context=context.platform_context
            )
        except (KeyError, FoundryResourceNotFoundError):
            logger.info(
                "Recovery dropped for %s: response was never resiliently created "
                "(definitive not-found); abandoning without re-invoking the handler.",
                context.response_id,
            )
            return True
        except Exception:  # pylint: disable=broad-exception-caught
            logger.debug(
                "persisted_response pre-fetch failed for %s (recovery, transient — not dropping)",
                context.response_id,
                exc_info=True,
            )
            context.persisted_response = None
        return False

    def _setup_cancel_bridge(
        self,
        ctx: "TaskContext[dict[str, Any]]",
        context: "ResponseContext | None",
        cancellation_signal: asyncio.Event,
    ) -> "asyncio.Task[None] | None":
        """Bridge the task cancellation surface onto the response context.

        (Spec 033 §3.2 extract) ``ctx.shutdown`` maps to ``context.shutdown`` ONLY
        (no cancel signal); ``ctx.cancel`` maps to ``cancellation_signal``. When
        neither is set yet, spawns a bridge task that races the two and applies
        whichever fires first. Returns the bridge task (or None when already
        resolved at entry).

        :param ctx: The resilient task context.
        :type ctx: TaskContext[dict[str, Any]]
        :param context: The handler-facing response context.
        :type context: ResponseContext | None
        :param cancellation_signal: The per-request cancellation event.
        :type cancellation_signal: asyncio.Event
        :returns: The bridge task, or None.
        :rtype: asyncio.Task[None] | None
        """
        if ctx.shutdown.is_set():
            if context is not None:
                context.shutdown.set()
            return None
        if ctx.cancel.is_set():
            cancellation_signal.set()
            return None

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

        return asyncio.create_task(_bridge())

    async def _run_handler_in_task(
        self,
        ctx: "TaskContext[dict[str, Any]]",
        record: "ResponseExecution | None",
        context: "ResponseContext | None",
        *,
        cancellation_signal: asyncio.Event,
        cancel_bridge: "asyncio.Task[None] | None",
        parsed_ref: Any,
        response_id: str,
        stream: bool,
        agent_reference: Any,
        model: str | None,
        store: bool,
        agent_session_id: str | None,
        conversation_id: str | None,
        background: bool,
        history_limit: int,
        runtime_state: Any,
    ) -> None:
        """Run the handler body inside the resilient task (Spec 033 §3.2 extract).

        Dispatches to the streaming runner (``stream=True``) or the non-stream
        background pipeline, translates a graceful-shutdown-without-terminal and a
        handler ``exit_for_recovery()`` into the framework's task-level recovery
        sentinel, and always tears down the cancel bridge + process-local refs.

        :param ctx: The resilient task context.
        :type ctx: TaskContext[dict[str, Any]]
        :param record: The execution record.
        :type record: ResponseExecution | None
        :param context: The handler-facing response context.
        :type context: ResponseContext | None
        :keyword cancellation_signal: The per-request cancellation event.
        :paramtype cancellation_signal: asyncio.Event
        :keyword cancel_bridge: The cancel-bridge task to tear down.
        :paramtype cancel_bridge: asyncio.Task[None] | None
        :keyword parsed_ref: The parsed request.
        :paramtype parsed_ref: Any
        :keyword response_id: The response id.
        :paramtype response_id: str
        :keyword stream: Whether the request is streaming.
        :paramtype stream: bool
        :keyword agent_reference: The normalized agent reference.
        :paramtype agent_reference: Any
        :keyword model: The model name.
        :paramtype model: str | None
        :keyword store: Whether the response is stored.
        :paramtype store: bool
        :keyword agent_session_id: The resolved session id.
        :paramtype agent_session_id: str | None
        :keyword conversation_id: The conversation id.
        :paramtype conversation_id: str | None
        :keyword background: Whether the request is background.
        :paramtype background: bool
        :keyword history_limit: History fetch limit.
        :paramtype history_limit: int
        :keyword runtime_state: The runtime-state tracker.
        :paramtype runtime_state: Any
        :return: None
        :rtype: None
        """
        from ._orchestrator import (  # pylint: disable=import-outside-toplevel
            _run_background_non_stream,
        )

        try:
            # Dispatch on the request's stream flag: the streaming pipeline goes
            # through the parent orchestrator's streaming runner (events flow to
            # record.subject AND the resilient stream provider); the non-stream
            # path drives the response-snapshot-on-terminal pipeline.
            if stream and self._parent_orchestrator is not None:
                assert record is not None  # reconstruction guarantees this
                assert context is not None  # reconstruction guarantees this
                await self._parent_orchestrator._run_resilient_stream_body(  # pylint: disable=protected-access
                    parsed=parsed_ref,
                    context=context,
                    cancellation_signal=cancellation_signal,
                    record=record,
                    response_id=response_id,
                    agent_reference=agent_reference,
                    model=model,
                    store=store,
                    agent_session_id=agent_session_id,
                    conversation_id=conversation_id,
                    background=background,
                )
            else:
                assert context is not None  # reconstruction guarantees this
                assert record is not None  # reconstruction guarantees this
                await _run_background_non_stream(
                    create_fn=self._create_fn,
                    parsed=parsed_ref,
                    context=context,
                    cancellation_signal=cancellation_signal,
                    record=record,
                    response_id=response_id,
                    agent_reference=agent_reference,
                    model=model,
                    provider=self._provider,
                    store=store,
                    agent_session_id=agent_session_id,
                    conversation_id=conversation_id,
                    history_limit=history_limit,
                    runtime_state=runtime_state,
                    runtime_options=self._options,
                )

            # Spec 023 — handler returned without a terminal AND graceful shutdown
            # is in progress: use ``ctx.exit_for_recovery()`` so the task stays
            # ``in_progress`` for next-lifetime recovery (a CancelledError would
            # delete a one-shot ephemeral record and the recovery scanner would
            # find nothing).
            if ctx.shutdown.is_set() and record is not None and record.status in {"queued", "in_progress"}:
                logger.info(
                    "Response %s handler returned during shutdown without terminal; "
                    "calling ctx.exit_for_recovery() so task stays in_progress for recovery.",
                    response_id,
                )
                return await ctx.exit_for_recovery()
        except ResponseExitForRecovery:
            # Spec 025 §A.4 — the handler called ``await context.exit_for_recovery()``;
            # translate to the framework's task-level recovery primitive.
            logger.info(
                "Response %s handler invoked context.exit_for_recovery(); calling "
                "ctx.exit_for_recovery() so task stays in_progress for recovery.",
                response_id,
            )
            return await ctx.exit_for_recovery()
        finally:
            if cancel_bridge is not None and not cancel_bridge.done():
                cancel_bridge.cancel()
            # (Spec 013 US1(c)) Drop the runtime-refs entry on terminal exit.
            _RUNTIME_REFS.pop(response_id, None)

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

        :param ctx: The resilient task context.
        :type ctx: TaskContext[dict[str, Any]]
        :return: None
        :rtype: None
        """
        # Import here to avoid circular imports
        from ._resilient_input import (
            ResilientResponseInput,
        )  # pylint: disable=import-outside-toplevel
        from ._request_parsing import (
            _resolve_conversation_id,
        )  # pylint: disable=import-outside-toplevel

        params = ctx.input
        is_recovery = _is_recovered_entry(ctx.entry_mode)

        # Single deserializer of the persisted boundary (Spec 033 FR-001).
        # Fail-closed (FR-002f): a malformed / incomplete persisted input MUST
        # NOT re-invoke the handler with partial state. Rather than letting the
        # body raise (which could leave a poison, re-firing task and never
        # settle the client's response), fail-close to a terminal: if we can
        # still address the client's response (response_id + platform context are in
        # the raw input), mark it failed in the store; then settle the task.
        try:
            resilient = ResilientResponseInput.from_task_input(params)
        except ValueError:
            rid = params.get("response_id") if isinstance(params, dict) else None
            logger.warning(
                "Resilient input failed validation for task %s (response_id=%s); "
                "failing closed without re-invoking the handler.",
                getattr(ctx, "task_id", "?"),
                rid,
            )
            if rid:
                await self._persist_crash_failed(rid, params if isinstance(params, dict) else {})
            return None
        request = resilient.request

        # Request-scoped scalars re-derived from the persisted request — pure
        # sync functions identical to fresh entry; no parallel persisted scalars
        # to drift (Spec 033 §3.1).
        _store = True if request.get("store") is None else bool(request.get("store"))
        _stream = bool(request.get("stream", False))
        _background = bool(request.get("background", False))
        _model = request.get("model") or ""
        _conversation_id = _resolve_conversation_id(request)
        _agent_reference = resilient.agent_reference
        _agent_session_id = resilient.agent_session_id

        # (Spec 039 R1) The response_id / disposition / background flag come from
        # the durable task input (``resilient`` / ``request``) — the single
        # source of truth, persisted at task ``.start()`` before the body runs.
        # No framework metadata namespace is created (matches the .NET port).
        response_id = resilient.response_id

        # (Spec 033 §3.1) Process-local refs live in a typed ``RuntimeRefs``
        # cache, never in the serialized input. Build a small key→ref map so the
        # existing ``_ref("_..._ref")`` call sites stay unchanged. Test-injected
        # refs passed via ``ctx.input`` are honored as a fallback.
        _runtime_refs = _RUNTIME_REFS.get(response_id)
        _ref_map: dict[str, Any] = {}
        if _runtime_refs is not None:
            _ref_map = {
                "_record_ref": _runtime_refs.record,
                "_context_ref": _runtime_refs.context,
                "_parsed_ref": _runtime_refs.parsed,
                "_cancel_ref": _runtime_refs.cancel,
                "_runtime_state_ref": _runtime_refs.runtime_state,
            }

        def _ref(key: str) -> Any:
            value = _ref_map.get(key)
            if value is None:
                value = params.get(key)
            return value

        if await self._handle_recovery_disposition(
            disposition=resilient.disposition,
            is_recovery=is_recovery,
            response_id=response_id,
            params=params,
            background=_background,
        ):
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
        # The pre-Phase-5 ``ResilienceContext`` indirection is deleted;
        # handlers read these fields directly off ``context``.
        context: ResponseContext | None = _ref("_context_ref")

        record: ResponseExecution | None = _ref("_record_ref")
        if record is None:
            # Cross-process recovery: in-memory references were lost when the
            # task input was serialized to the task store. Reconstruct from
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

        if await self._flatten_recovery_context(ctx, context, is_recovery):
            return

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
        cancel_bridge = self._setup_cancel_bridge(ctx, context, cancellation_signal)

        # Return the handler-body result so a graceful-shutdown / handler
        # ``exit_for_recovery()`` sentinel propagates as the task-body result
        # (rather than being replaced by a bare implicit-suspend ``None``).
        return await self._run_handler_in_task(
            ctx,
            record,
            context,
            cancellation_signal=cancellation_signal,
            cancel_bridge=cancel_bridge,
            parsed_ref=_ref("_parsed_ref") or request,
            response_id=response_id,
            stream=_stream,
            agent_reference=_agent_reference,
            model=_model,
            store=_store,
            agent_session_id=_agent_session_id,
            conversation_id=_conversation_id,
            background=_background,
            history_limit=int(self._options.default_fetch_history_count),
            runtime_state=_ref("_runtime_state_ref") or self._runtime_state,
        )

    def build_resilient_input(
        self,
        ctx: Any,
        record: "ResponseExecution",
        *,
        disposition: str,
    ) -> "tuple[ResilientResponseInput, RuntimeRefs]":
        """Build the typed resilient boundary + process-local refs for a request.

        (Spec 033 §3.4) Resilient-task construction lives on the resilience
        orchestrator, not the response pipeline. The full request is persisted
        once (it carries ``.input``); request-scoped scalars are re-derived from
        it on recovery. ``client_headers`` / ``query_parameters`` are persisted so
        a recovered handler observes the identical request metadata as fresh
        entry (FR-002b).

        :param ctx: The per-request execution context (``_ExecutionContext``).
        :type ctx: Any
        :param record: The mutable execution record.
        :type record: ResponseExecution
        :keyword disposition: The recovery disposition (``decide_disposition``).
        :paramtype disposition: str
        :returns: ``(resilient_input, refs)``.
        :rtype: tuple[ResilientResponseInput, RuntimeRefs]
        """
        from ._resilient_input import (
            ResilientResponseInput,
            RuntimeRefs,
        )  # pylint: disable=import-outside-toplevel

        resilient_input = ResilientResponseInput(
            request=ctx.parsed,
            response_id=ctx.response_id,
            # (Spec 039 R1) Disposition rides the durable input, which is the
            # single source of truth for recovery routing (persisted at
            # ``.start()`` and read on every recovered entry — matching .NET).
            disposition=disposition,
            agent_reference=ctx.agent_reference,
            agent_session_id=ctx.agent_session_id,
            user_id_key=ctx.user_id,
            call_id=ctx.call_id,
            client_headers=dict(ctx.context.client_headers) if ctx.context is not None else {},
            query_parameters=dict(ctx.context.query_parameters) if ctx.context is not None else {},
        )
        refs = RuntimeRefs(
            record=record,
            context=ctx.context,
            parsed=ctx.parsed,
            cancel=ctx.cancellation_signal,
            runtime_state=self._runtime_state,
        )
        return resilient_input, refs

    async def start_resilient(
        self,
        *,
        record: "ResponseExecution",
        resilient_input: "ResilientResponseInput",
        refs: "RuntimeRefs",
    ) -> bool:
        """Start the resilient task for a background response.

        Called by ``_ResponseOrchestrator._start_resilient_background`` when
        ``resilient_background=True``. The task takes over responsibility for
        execution and crash recovery.

        :keyword record: The mutable execution record (same as non-resilient path).
        :paramtype record: ResponseExecution
        :keyword resilient_input: The typed resilient boundary — the ONLY value
            persisted as resilient-task input (Spec 033 §3.1).
        :paramtype resilient_input: ResilientResponseInput
        :keyword refs: The process-local object references for this response,
            cached out-of-band (never serialized).
        :paramtype refs: RuntimeRefs
        :returns: True if task was freshly started, False if input was queued
            on an already-active steerable task.
        :rtype: bool
        """
        from ._request_parsing import (
            _extract_agent_identity,
            _resolve_conversation_id,
        )  # pylint: disable=import-outside-toplevel

        request = resilient_input.request
        response_id = resilient_input.response_id
        conversation_id = _resolve_conversation_id(request)
        previous_response_id = (
            request.get("previous_response_id")
            if isinstance(request.get("previous_response_id"), str) and request.get("previous_response_id")
            else None
        )

        task_id = derive_task_id(
            agent_name=_extract_agent_identity(resilient_input.agent_reference)[0],
            session_id=resilient_input.agent_session_id or "",
            conversation_id=conversation_id,
            previous_response_id=previous_response_id,
            response_id=response_id,
            steerable=self._options.steerable_conversations,
        )

        # Spec 023 — per-request primitive dispatch (SOT §6.6).
        # Selects between the one-shot ``@task`` primitive (auto-deleted
        # on terminal exit; no chain semantics) and the multi-turn
        # ``@multi_turn_task`` primitive (suspends between turns; chain
        # semantics) based on the request's conversation_id /
        # previous_response_id / steerable_conversations tuple.
        picked_primitive = self._pick_primitive(
            conversation_id=conversation_id,
            previous_response_id=previous_response_id,
        )
        is_multi_turn = picked_primitive is self._multi_turn_task_fn

        # (Spec 033 §3.1) The process-local refs are cached out-of-band keyed by
        # response_id; the resilient task input is EXACTLY the typed boundary's
        # serialization — the single producer (FR-001).
        _RUNTIME_REFS[response_id] = refs

        start_kwargs: dict[str, Any] = {
            "task_id": task_id,
            "input": resilient_input.to_task_input(),
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
            if previous_response_id is not None:
                start_kwargs["if_last_input_id"] = previous_response_id

        # ``TaskConflictError`` from the underlying primitive ALWAYS signals
        # a real conflict (concurrent overlap on a multi-turn-non-steerable
        # chain, OR a duplicate task_id collision). It propagates up to the
        # endpoint handler which maps it to HTTP 409 ``conversation_locked``.
        # Under the new model the steerable-input-queuing case does NOT
        # raise TaskConflictError — ``MultiTurnTask(steerable=True).start()``
        # auto-queues against an in-flight chain and returns a TaskRun
        # whose ``is_queued`` is True (the public-surface detection signal).
        # See the queued-vs-fresh check below.
        task_run = await picked_primitive.start(**start_kwargs)
        # Store the task run reference on the record for observability
        record.resilient_task_run = task_run  # type: ignore[attr-defined]

        # Detect "queued steering input" via the public ``TaskRun.is_queued``
        # predicate. The framework marks the returned handle as queued ONLY when
        # it represents a not-yet-promoted input on a steerable chain — i.e. the
        # caller's request landed mid-turn and is awaiting drain. Returning False
        # here signals the caller to dispatch the acceptance hook and return a
        # ``status="queued"`` response envelope to the HTTP caller.
        is_queued = task_run.is_queued
        return not is_queued  # True = freshly started, False = queued

    async def _persist_crash_failed(
        self,
        response_id: str,
        params: dict[str, Any],
    ) -> None:
        """Persist a response as ``failed`` after crash recovery.

        Used by the next-lifetime recovery path for tasks with
        ``disposition="mark-failed"`` (Rows 2 and 3 of the resilience
        matrix). Both rows cannot be re-invoked on recovery —
        Row 2 (bg+store, resilient_background=False) opted out of crash
        recovery; Row 3 (fg+store) has no live HTTP request to stream
        events back to. The recovered task body marks the response
        ``failed`` via the generic ``server_error`` code (path-specific
        cause in ``message``, per ``resilience-contract.md`` § Glossary).

        Idempotent against a completed-response race (T-066): if the
        response already exists in the store with a terminal status, the
        crash happened AFTER terminal persistence and BEFORE the
        resilient task body could return. In that case the
        ``server_error`` marker would corrupt a valid completed response,
        so we skip the overwrite and return cleanly. The next-lifetime
        recovery scanner still marks the task as completed when the body
        returns, removing it from future recovery scans.

        Handles both create (response was never persisted — handler
        crashed before terminal) and update (response was persisted at
        ``response.created`` for bg+stream but the terminal never landed)
        cases.

        :param response_id: The response identifier.
        :type response_id: str
        :param params: The task input params (used to extract
            platform context for storage routing).
        :type params: dict[str, Any]
        """
        from ..models._generated import (
            ResponseObject,
        )  # pylint: disable=import-outside-toplevel
        from ._resilient_input import (
            platform_context_from_params,
        )  # pylint: disable=import-outside-toplevel
        from ..store._foundry_errors import (
            FoundryResourceNotFoundError,
        )  # pylint: disable=import-outside-toplevel

        _TERMINAL_STATUSES = {"completed", "failed", "cancelled", "incomplete"}

        # Runtime-only object references never reach the persisted task input
        # (Spec 033 §3.1 — they live in ``RuntimeRefs``), so the platform context is rebuilt
        # from the persisted user_id_key via the single derivation site
        # (Spec 033 FR-003) — same partition the client reads. Otherwise the
        # failed marker would land in the default/unscoped partition.
        platform_context = platform_context_from_params(params)

        # (Spec 014 T-066) Race-safe idempotent check. If the store already
        # holds a terminal response for this id, leave it alone — the crash
        # happened after terminal persistence, and overwriting would corrupt
        # the result. A non-terminal snapshot is captured for reuse: the
        # failed terminal is overlaid onto it so the developer's persisted
        # response object (agent_reference, model, output-so-far, ...) is
        # preserved rather than discarded (§7.2 step 3).
        #
        # ``response_known_absent`` distinguishes a *confirmed* missing response
        # (``KeyError`` — handler crashed before ``response.created``) from an
        # *unknown* store state (some other read error). The read is retried
        # once so a transient failure does not force the destructive synthesize
        # path below — synthesizing carries ``agent_reference``, so an
        # ``update`` would now succeed and overwrite a progressed snapshot with
        # empty output.
        existing_snapshot: "ResponseObject | None" = None
        response_known_absent = False
        for _attempt in range(2):
            try:
                existing = await self._provider.get_response(response_id, context=platform_context)
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
                existing_snapshot = existing
                break
            except (KeyError, FoundryResourceNotFoundError):
                # Response confirmed not in store (crash before terminal). The
                # file/memory stores raise KeyError; the Foundry store raises
                # FoundryResourceNotFoundError for a missing response.
                response_known_absent = True
                break
            except Exception:  # pylint: disable=broad-exception-caught
                # Unknown/transient store error — retry once, then fall through
                # to the conservative create-only path below.
                continue

        if existing_snapshot is not None:
            # Preserve the persisted snapshot; overlay only status + error.
            failed_response = _overlay_failed_terminal(
                existing_snapshot,
                shutdown_reason="crash_recovery",
            )
        else:
            # No readable snapshot — synthesize a minimal failed object,
            # carrying agent_reference + model from the persisted task input so
            # the write still satisfies the store's agent-reference requirement.
            # Output is empty (no progress could be preserved).
            failed_response = cast(
                ResponseObject,
                _build_server_error_payload(
                    response_id,
                    shutdown_reason="crash_recovery",
                    agent_reference=_agent_reference_from_params(params),
                    model=_model_from_params(params),
                ),
            )

        if existing_snapshot is not None or response_known_absent:
            # Safe to write: either we preserve the snapshot (overlay) or the
            # response is confirmed absent (a create lands a fresh terminal).
            try:
                await self._provider.update_response(failed_response, context=platform_context)
            except (KeyError, FoundryResourceNotFoundError):
                # Response was never persisted at response.created — try
                # create instead so the failed terminal still lands. The Foundry
                # store raises FoundryResourceNotFoundError (NOT a KeyError) for
                # the missing-response case, so both must be caught here or the
                # create fallback would be skipped on the production store.
                try:
                    await self._provider.create_response(
                        failed_response,
                        input_items=[],
                        history_item_ids=None,
                        context=platform_context,
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
        else:
            # Unknown store state (read failed and the response was never
            # confirmed absent): a progressed snapshot may still exist. NEVER
            # ``update`` here — it would clobber that progress with empty
            # output. Best-effort ``create`` only: it lands a terminal iff the
            # response truly does not exist; if it already exists, the store
            # rejects the create and the existing progress is left intact.
            try:
                await self._provider.create_response(
                    failed_response,
                    input_items=[],
                    history_item_ids=None,
                    context=platform_context,
                )
            except Exception as exc:  # pylint: disable=broad-exception-caught
                logger.error(
                    "_persist_crash_failed: create-only (unknown store state) failed for %s: %s",
                    response_id,
                    exc,
                )
