# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Event-pipeline orchestration for the Responses server.

This module is intentionally free of Starlette imports: it operates purely on
``_ExecutionContext`` and produces plain Python data (dicts, async iterators of
strings). The HTTP layer (Starlette ``Request`` / ``Response``) lives in the
routing module which wraps these results.
"""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import json
import logging
from copy import deepcopy
from typing import TYPE_CHECKING, Any, AsyncIterator, Callable, cast

import anyio

from azure.ai.agentserver.core.platform_headers import (
    PLATFORM_ERROR_TAG,
)
from azure.ai.agentserver.core.tasks import (
    LastInputIdPreconditionFailed,
    TaskConflictError,
    TaskManagerNotInitialized,
)

from azure.ai.agentserver.core.streaming import (  # pylint: disable=import-error,no-name-in-module
    EventStream,
    EventStreamClosedError,
    EventStreamNotFoundError,
    streams,
)

from .._options import ResponsesServerOptions
from .._response_context import ResponseExitForRecovery
from ..models import _generated as generated_models
from ..models.runtime import (
    ResponseExecution,
    ResponseModeFlags,
    ResponseStatus,
    _apply_cancelled_terminal,
    _apply_failed_terminal,
    _resolve_cancelled_response,
    _resolve_failed_response,
)
from ..store._base import ResponseAlreadyExistsError, ResponseProviderProtocol
from ..streaming._checkpoint import ResponseCheckpointEvent
from ..streaming._helpers import (
    _apply_stream_event_defaults,
    _build_events,
    _coerce_handler_event,
    _extract_response_snapshot_from_events,
)
from ..streaming._internals import construct_event_model
from ..streaming._sse import (
    encode_keep_alive_comment,
    encode_sse_any_event,
    new_stream_counter,
)
from ..streaming._state_machine import EventStreamValidator
from ._execution_context import _ExecutionContext
from ._dispatch import decide_disposition
from ._runtime_state import _RuntimeState

if TYPE_CHECKING:
    from .._response_context import ResponseContext
    from ..models._generated import AgentReference, CreateResponse


logger = logging.getLogger("azure.ai.agentserver")


_STORAGE_ERROR_MESSAGE = (
    "An internal error occurred while storing the response. "
    "Subsequent retrieval is not guaranteed. Please retry the request."
)


async def _resolve_input_items_for_persistence(
    context: "ResponseContext | None",
    fallback_items: list[generated_models.OutputItem] | None,
) -> list[generated_models.OutputItem] | None:
    """Resolve ``item_reference`` inputs via the provider before persisting.

    When the caller's input includes ``ItemReferenceParam`` entries (references
    to previously-stored items), this function batch-resolves them through the
    provider and returns concrete :class:`OutputItem` instances suitable for
    storage.  If reference resolution is unavailable (no provider or failure),
    falls back to *fallback_items* — the pre-expanded list that already has
    references stripped.

    :param context: The :class:`ResponseContext` for this request.
    :type context: ResponseContext | None
    :param fallback_items: Pre-expanded input items (references dropped).
    :type fallback_items: list[OutputItem] | None
    :return: Resolved output items, or ``None`` if the list is empty.
    :rtype: list[OutputItem] | None
    """
    if context is not None:
        try:
            resolved = await context._get_input_items_for_persistence()  # pylint: disable=protected-access
            if resolved:
                return list(resolved)
            return None
        except Exception:  # pylint: disable=broad-exception-caught
            logger.debug(
                "item_reference resolution failed; falling back to pre-expanded items",
                exc_info=True,
            )
    return list(fallback_items) if fallback_items else None


def _check_first_event_contract(normalized: generated_models.ResponseStreamEvent, response_id: str) -> str | None:
    """Return an error message if the first handler event violates the contract, else None.

    -: The first event MUST be ``response.created`` with matching ``id``.
    -: The ``status`` in ``response.created`` MUST be non-terminal.

    :param normalized: Normalised first event (``ResponseStreamEvent`` model instance).
    :type normalized: ResponseStreamEvent
    :param response_id: Library-assigned response identifier.
    :type response_id: str
    :return: Violation message string, or ``None`` if no violation.
    :rtype: str | None
    """
    event_type = normalized.get("type")
    response = cast("dict[str, Any]", normalized.get("response") or {})
    if event_type != "response.created":
        return f"first event must be response.created, got '{event_type}'"
    emitted_id = response.get("id")
    if emitted_id and emitted_id != response_id:
        return f"response.created id '{emitted_id}' != assigned id '{response_id}'"
    emitted_status = response.get("status")
    if emitted_status in {"completed", "failed", "cancelled", "incomplete"}:
        return f"response.created status must be non-terminal, got '{emitted_status}'"
    return None


_CANCEL_WINDDOWN_TIMEOUT: float = 10.0


async def _iter_with_winddown(
    aiter: Any,
    cancel_signal: asyncio.Event,
    timeout: float = _CANCEL_WINDDOWN_TIMEOUT,
) -> AsyncIterator:
    """Yield items from *aiter*, enforcing a winddown timeout after cancellation.

    Once *cancel_signal* is set a countdown of *timeout* seconds begins.
    If the iterator does not stop within the budget, iteration is terminated
    so that the caller can finalise the response without hanging indefinitely.

    :param aiter: The async iterator to wrap.
    :type aiter: Any
    :param cancel_signal: Event signalling that cancellation was requested.
    :type cancel_signal: asyncio.Event
    :param timeout: Maximum seconds to wait after cancellation before forcing stop.
    :type timeout: float
    :return: Async iterator of items from *aiter*.
    :rtype: AsyncIterator
    """
    deadline: float | None = None
    while True:
        if cancel_signal.is_set() and deadline is None:
            deadline = asyncio.get_event_loop().time() + timeout

        try:
            if deadline is not None:
                remaining = deadline - asyncio.get_event_loop().time()
                if remaining <= 0:
                    return
                item = await asyncio.wait_for(aiter.__anext__(), timeout=remaining)
            else:
                item = await aiter.__anext__()
        except StopAsyncIteration:
            return
        except asyncio.TimeoutError:
            return

        yield item


_OUTPUT_ITEM_EVENT_TYPES: frozenset[str] = frozenset(
    {
        "response.output_item.added",
        "response.output_item.done",
    }
)

# Response-level lifecycle events whose ``response`` field carries a full Response snapshot.
# Used by  output manipulation detection.
_RESPONSE_SNAPSHOT_TYPES: frozenset[str] = frozenset(
    {
        "response.in_progress",
        "response.completed",
        "response.failed",
        "response.incomplete",
        "response.queued",
    }
)


def _validate_handler_event(
    coerced: generated_models.ResponseStreamEvent,
) -> str | None:
    """Return an error message if a coerced handler event has invalid structure, else None.

    Lightweight structural checks (B30):
    - For ``response.output_item.*`` events the model/dict must contain
      ``output_index`` and at least one of ``item_id`` or ``item``.

    :param coerced: Coerced event (``ResponseStreamEvent`` model instance).
    :type coerced: ResponseStreamEvent
    :return: Violation message string, or ``None`` if valid.
    :rtype: str | None
    """
    event_type = coerced.get("type", "")
    if event_type in _OUTPUT_ITEM_EVENT_TYPES:
        if coerced.get("output_index") is None:
            return f"{event_type} missing required field 'output_index'"
        if coerced.get("item_id") is None and coerced.get("item") is None:
            return f"{event_type} must include 'item_id' or 'item'"

    return None


def _is_resilient_background(
    runtime_options: "ResponsesServerOptions | None", *, store: bool, background: bool
) -> bool:
    """Return True for a resilient background response (the only checkpoint consumer).

    :param runtime_options: Server runtime options.
    :type runtime_options: ResponsesServerOptions | None
    :keyword store: Whether the response is stored.
    :paramtype store: bool
    :keyword background: Whether the response is background.
    :paramtype background: bool
    :returns: True iff ``resilient_background`` is enabled and the response is a
        stored background response.
    :rtype: bool
    """
    return bool(
        runtime_options is not None and getattr(runtime_options, "resilient_background", False) and store and background
    )


async def _do_checkpoint_persist(
    event: ResponseCheckpointEvent,
    *,
    provider: "ResponseProviderProtocol | None",
    runtime_options: "ResponsesServerOptions | None",
    store: bool,
    background: bool,
    context: Any,
    response_id: str,
    last_snapshot: "bytes | None",
    terminal_seen: bool,
) -> "bytes | None":
    """Persist a developer checkpoint snapshot (spec 025 §A.3).

    Shared by both handler-draining paths. Persists only for resilient background
    responses; idempotent (byte-compare); failures logged + tagged, never
    raised. Snapshots the response with its current status as-is.

    :param event: The checkpoint event carrying the response snapshot.
    :type event: ResponseCheckpointEvent
    :keyword provider: The storage provider (``None`` ⇒ no-op).
    :paramtype provider: ResponseProviderProtocol | None
    :keyword runtime_options: Server runtime options.
    :paramtype runtime_options: ResponsesServerOptions | None
    :keyword store: Whether the response is stored.
    :paramtype store: bool
    :keyword background: Whether the response is background.
    :paramtype background: bool
    :keyword context: Platform context for the provider write.
    :paramtype context: Any
    :keyword response_id: The response id (for logging).
    :paramtype response_id: str
    :keyword last_snapshot: Serialised bytes of the previously persisted snapshot.
    :paramtype last_snapshot: bytes | None
    :keyword terminal_seen: Whether a terminal event has already been processed.
    :paramtype terminal_seen: bool
    :returns: The new ``last_snapshot`` bytes (unchanged when nothing persisted).
    :rtype: bytes | None
    """
    if not _is_resilient_background(runtime_options, store=store, background=background):
        logger.debug("checkpoint() no-op (not a resilient background response) for %s", response_id)
        return last_snapshot
    if terminal_seen:
        logger.debug("checkpoint() after terminal dropped for %s", response_id)
        return last_snapshot
    response = event.response
    if response is None or provider is None:
        return last_snapshot
    try:
        snapshot_bytes = json.dumps(dict(response), sort_keys=True, default=str).encode("utf-8")
    except Exception:  # pylint: disable=broad-exception-caught
        logger.debug("checkpoint() snapshot serialisation failed for %s", response_id, exc_info=True)
        return last_snapshot
    if snapshot_bytes == last_snapshot:
        return last_snapshot  # idempotent — nothing changed since the last checkpoint
    result = last_snapshot
    try:
        await provider.update_response(response, context=context)
        result = snapshot_bytes
    except Exception as exc:  # pylint: disable=broad-exception-caught
        setattr(exc, PLATFORM_ERROR_TAG, True)
        logger.error("checkpoint persist failed (response_id=%s): %s", response_id, exc, exc_info=True)
    return result


def _bg_discard_on_client_cancel(record: ResponseExecution, cancellation_signal: asyncio.Event) -> bool:
    """Force ``cancelled`` mid-loop on a client-initiated cancel (Spec 033 §3.2).

    :param record: The execution record.
    :type record: ResponseExecution
    :param cancellation_signal: The cancellation event.
    :type cancellation_signal: asyncio.Event
    :returns: True if the caller should ``return`` (discard); False otherwise.
    :rtype: bool
    """
    if not (cancellation_signal.is_set() and record.cancel_requested):
        return False
    if record.status not in ("cancelled", "completed", "failed", "incomplete"):
        record.transition_to("cancelled")
    return True


def _bg_normalize_event(
    handler_event: Any,
    *,
    response_id: str,
    agent_reference: "AgentReference | dict[str, Any]",
    model: str | None,
    agent_session_id: str | None,
    conversation_id: str | None,
) -> "generated_models.ResponseStreamEvent":
    """Coerce, structurally validate, and default-normalise a handler event.

    (Spec 033 §3.2 extract)

    :param handler_event: The raw handler event.
    :type handler_event: Any
    :keyword response_id: The response id.
    :paramtype response_id: str
    :keyword agent_reference: The normalized agent reference.
    :paramtype agent_reference: AgentReference | dict[str, Any]
    :keyword model: The model name.
    :paramtype model: str | None
    :keyword agent_session_id: The resolved session id.
    :paramtype agent_session_id: str | None
    :keyword conversation_id: The conversation id.
    :paramtype conversation_id: str | None
    :returns: The normalised event.
    :rtype: generated_models.ResponseStreamEvent
    :raises ValueError: On a B30 structural violation.
    """
    coerced = _coerce_handler_event(handler_event)
    b30_err = _validate_handler_event(coerced)
    if b30_err:
        raise ValueError(b30_err)
    return _apply_stream_event_defaults(
        coerced,
        response_id=response_id,
        agent_reference=agent_reference,
        model=model,
        sequence_number=None,
        agent_session_id=agent_session_id,
        conversation_id=conversation_id,
    )


def _bg_track_output_count(normalized: "generated_models.ResponseStreamEvent", output_item_count: int) -> int:
    """Track ``output_item.added`` events and detect direct output manipulation.

    (Spec 033 §3.2 extract) Increments the count for ``output_item.added`` events
    and raises if a snapshot event reports more output items than were added via
    builder events.

    :param normalized: The normalised handler event.
    :type normalized: generated_models.ResponseStreamEvent
    :param output_item_count: The running count of added output items.
    :type output_item_count: int
    :returns: The updated output-item count.
    :rtype: int
    :raises ValueError: On an output-item count mismatch.
    """
    if normalized.get("type") == "response.output_item.added":
        output_item_count += 1
    n_type = normalized.get("type", "")
    if n_type in _RESPONSE_SNAPSHOT_TYPES:
        n_output = cast("dict[str, Any]", normalized.get("response") or {}).get("output")
        if isinstance(n_output, list) and len(n_output) > output_item_count:
            raise ValueError(
                "Output item count mismatch " + f"({len(n_output)} vs {output_item_count} output_item.added events)"
            )
    return output_item_count


async def _bg_handle_first_event(
    record: ResponseExecution,
    normalized: "generated_models.ResponseStreamEvent",
    handler_events: "list[generated_models.ResponseStreamEvent]",
    *,
    st: "_BgRunState",
    context: "ResponseContext | None",
    store: bool,
    provider: "ResponseProviderProtocol | None",
    response_id: str,
    agent_reference: "AgentReference | dict[str, Any]",
    model: str | None,
    agent_session_id: str | None,
    conversation_id: str | None,
    history_limit: int,
) -> "tuple[int, bool]":
    """Handle the first handler event of a bg non-stream run (Spec 033 §3.2).

    Guards against direct ``response.output`` manipulation (allowing recovery
    seeding), sets the initial ``response.created`` snapshot, honours a
    handler-set ``queued`` status, and persists at created time. Records the
    ``output_item_count`` seed and ``provider_created`` flag onto ``st`` **before**
    the cancellable ``await asyncio.sleep(0)`` checkpoint, so a ``CancelledError``
    delivered at that yield cannot lose the ``provider_created`` tracking (which
    would otherwise force the create branch in terminal persistence).

    :param record: The execution record.
    :type record: ResponseExecution
    :param normalized: The normalised first event.
    :type normalized: generated_models.ResponseStreamEvent
    :param handler_events: The accumulated events (first already appended).
    :type handler_events: list[generated_models.ResponseStreamEvent]
    :keyword st: The mutable bg-run state holder updated in place.
    :paramtype st: _BgRunState
    :keyword context: The response context.
    :paramtype context: ResponseContext | None
    :keyword store: Whether the response is stored.
    :paramtype store: bool
    :keyword provider: The persistence provider.
    :paramtype provider: ResponseProviderProtocol | None
    :keyword response_id: The response id.
    :paramtype response_id: str
    :keyword agent_reference: The normalized agent reference.
    :paramtype agent_reference: AgentReference | dict[str, Any]
    :keyword model: The model name.
    :paramtype model: str | None
    :keyword agent_session_id: The resolved session id.
    :paramtype agent_session_id: str | None
    :keyword conversation_id: The conversation id.
    :paramtype conversation_id: str | None
    :keyword history_limit: History fetch limit.
    :paramtype history_limit: int
    :raises ValueError: On direct output manipulation on a fresh entry.
    :return: The output-item count and provider-created flag after the first event.
    :rtype: tuple[int, bool]
    """
    output_item_count = 0
    #: output manipulation detection on response.created
    created_response = cast("dict[str, Any]", normalized.get("response") or {})
    created_output = created_response.get("output")
    if isinstance(created_output, list) and len(created_output) != 0:
        # §6 recovery seeding: on a recovered entry the handler legitimately
        # seeds the stream from context.persisted_response, so response.created
        # carries the already-persisted items. Treat them as the output baseline.
        # Only a FRESH entry must not pre-populate output.
        if context is not None and context.is_recovery:
            output_item_count = len(created_output)
        else:
            raise ValueError(
                f"Handler directly modified Response.Output "
                f"(found {len(created_output)} items, expected 0). "
                f"Use output builder events instead."
            )
    st.output_item_count = output_item_count

    # Set initial response snapshot for POST response body without changing
    # record.status (transition_to manages status lifecycle).
    _initial_snapshot = _extract_response_snapshot_from_events(
        handler_events,
        response_id=response_id,
        agent_reference=agent_reference,
        model=model,
        agent_session_id=agent_session_id,
        conversation_id=conversation_id,
    )
    record.set_response_snapshot(cast(generated_models.ResponseObject, _initial_snapshot))
    # Honour the handler's initial status (e.g. "queued").
    if _initial_snapshot.get("status") == "queued":
        record.status = "queued"  # type: ignore[assignment]
    # Record provider_created onto ``st`` BEFORE the cancellable sleep(0) below.
    # If a CancelledError is delivered at that yield, terminal persistence must
    # still see provider_created=True (the create already landed) and take the
    # update_response branch rather than re-creating (which would raise
    # ResponseAlreadyExistsError and diverge the in-memory record).
    st.provider_created = await _bg_persist_at_created(
        record,
        store=store,
        provider=provider,
        context=context,
        response_id=response_id,
        history_limit=history_limit,
        initial_snapshot=_initial_snapshot,
    )
    record.response_created_signal.set()
    # Yield to the event loop so run_background's ``await signal.wait()`` can
    # resume and capture the in_progress snapshot before the handler continues
    # to terminal state (otherwise a synchronous handler runs straight to
    # completion and the POST returns "completed" instead of "in_progress").
    await asyncio.sleep(0)
    return st.output_item_count, st.provider_created


def _bg_resolve_terminal_status(
    record: ResponseExecution,
    handler_events: "list[generated_models.ResponseStreamEvent]",
    *,
    response_id: str,
    agent_reference: "AgentReference | dict[str, Any]",
    model: str | None,
    agent_session_id: str | None,
    conversation_id: str | None,
) -> None:
    """Resolve and apply the terminal status after the handler loop (Spec 033 §3.2).

    Builds the response snapshot from the accumulated events (or a synthesised
    fallback) and transitions the record to its terminal status — unless the
    record was already moved to a terminal state concurrently (e.g. by the
    in-process shutdown marker), in which case that marker is authoritative.

    :param record: The execution record.
    :type record: ResponseExecution
    :param handler_events: The accumulated normalised handler events.
    :type handler_events: list[generated_models.ResponseStreamEvent]
    :keyword response_id: The response id.
    :paramtype response_id: str
    :keyword agent_reference: The normalized agent reference.
    :paramtype agent_reference: AgentReference | dict[str, Any]
    :keyword model: The model name.
    :paramtype model: str | None
    :keyword agent_session_id: The resolved session id.
    :paramtype agent_session_id: str | None
    :keyword conversation_id: The conversation id.
    :paramtype conversation_id: str | None
    """
    events = (
        handler_events
        if handler_events
        else _build_events(
            response_id,
            include_progress=True,
            agent_reference=agent_reference,
            model=model,
        )
    )
    response_payload = _extract_response_snapshot_from_events(
        events,
        response_id=response_id,
        agent_reference=agent_reference,
        model=model,
        remove_sequence_number=True,
        agent_session_id=agent_session_id,
        conversation_id=conversation_id,
    )
    # Stamp background so the provider fallback can enforce B1 checks
    # after eager eviction removes the in-memory record.
    response_payload["background"] = record.mode_flags.background

    resolved_status = response_payload.get("status")
    # (Spec 024 Phase 2 — bookkeeping unification) If the record was already
    # transitioned to a terminal status concurrently (e.g. by the in-process
    # shutdown marker), do NOT override it with the handler's partial event
    # sequence — that marker's persistence is authoritative.
    _TERMINAL_STATES = {"completed", "failed", "cancelled", "incomplete"}
    if record.status in _TERMINAL_STATES:
        return  # leave the marker's terminal state intact
    if record.status != "cancelled":
        record.set_response_snapshot(cast(generated_models.ResponseObject, response_payload))
        target = resolved_status if isinstance(resolved_status, str) else "completed"
        # If still queued, transition through in_progress first so the state
        # machine stays valid (queued can only reach terminal via in_progress).
        if record.status == "queued" and target != "in_progress":
            record.transition_to("in_progress")
        record.transition_to(cast(ResponseStatus, target))


async def _bg_persist_at_created(
    record: ResponseExecution,
    *,
    store: bool,
    provider: "ResponseProviderProtocol | None",
    context: "ResponseContext | None",
    response_id: str,
    history_limit: int,
    initial_snapshot: dict[str, Any],
) -> bool:
    """Persist (create) the response at ``response.created`` time (Spec 033 §3.2).

    Returns whether the create landed (or the response already existed — the
    idempotent-recovery case). On failure, marks ``record.persistence_failed`` so
    the terminal update knows not to attempt ``update_response``. A no-op
    (returns False) when not storing.

    :param record: The execution record.
    :type record: ResponseExecution
    :keyword store: Whether the response is stored.
    :paramtype store: bool
    :keyword provider: The persistence provider.
    :paramtype provider: ResponseProviderProtocol | None
    :keyword context: The response context (platform context / input items).
    :paramtype context: ResponseContext | None
    :keyword response_id: The response id.
    :paramtype response_id: str
    :keyword history_limit: History fetch limit.
    :paramtype history_limit: int
    :keyword initial_snapshot: The response.created snapshot dict.
    :paramtype initial_snapshot: dict[str, Any]
    :returns: ``_provider_created`` — True if the create landed or already existed.
    :rtype: bool
    """
    if not (store and provider is not None):
        return False
    _context = context.platform_context if context else None
    _response_obj = cast(generated_models.ResponseObject, initial_snapshot)
    try:
        _history_ids = (
            await provider.get_history_item_ids(
                record.previous_response_id,
                None,
                history_limit,
                context=_context,
            )
            if record.previous_response_id
            else None
        )
        _resolved_items = await _resolve_input_items_for_persistence(context, record.input_items)
        await provider.create_response(_response_obj, _resolved_items, _history_ids, context=_context)
        return True
    except ResponseAlreadyExistsError:
        # Recovery: response was persisted by a prior attempt. The terminal
        # update_response is the next write. (Spec 013 US1 deliverable (b).)
        logger.info(
            "Response %s already exists in store (recovery — swallowed by idempotent create).",
            response_id,
        )
        return True
    except Exception as persist_exc:  # pylint: disable=broad-exception-caught
        # §3.3: Phase 1 create failure — mark persistence failed so the terminal
        # update knows not to attempt update_response.
        setattr(persist_exc, PLATFORM_ERROR_TAG, True)
        logger.error(
            "Phase 1 create_response failed for bg non-stream (response_id=%s): %s",
            response_id,
            persist_exc,
            exc_info=True,
        )
        record.persistence_failed = True
        record.persistence_exception = persist_exc
        return False


def _bg_resolve_cancelled(
    record: ResponseExecution,
    *,
    cancellation_signal: asyncio.Event,
    context: "ResponseContext | None",
    first_event_processed: bool,
    runtime_options: "ResponsesServerOptions | None",
    response_id: str,
    agent_reference: "AgentReference | dict[str, Any]",
    model: str | None,
) -> bool:
    """Resolve a ``CancelledError`` raised during bg non-stream processing.

    (Spec 033 §3.2 extract — S-024) Known cancellation (signal set) maps the
    record's terminal status from the composing-cause flags (client cancel /
    shutdown / steering); a resilient+bg shutdown is left ``in_progress`` for
    re-entry. An unknown cancel before any events is treated as handler failure.

    :param record: The execution record.
    :type record: ResponseExecution
    :keyword cancellation_signal: The cancellation event.
    :paramtype cancellation_signal: asyncio.Event
    :keyword context: The response context.
    :paramtype context: ResponseContext | None
    :keyword first_event_processed: Whether any handler event was processed.
    :paramtype first_event_processed: bool
    :keyword runtime_options: Server runtime options.
    :paramtype runtime_options: ResponsesServerOptions | None
    :keyword response_id: The response id.
    :paramtype response_id: str
    :keyword agent_reference: The normalized agent reference.
    :paramtype agent_reference: AgentReference | dict[str, Any]
    :keyword model: The model name.
    :paramtype model: str | None
    :returns: True if the caller should ``return``; False if it should re-raise.
    :rtype: bool
    """
    if cancellation_signal.is_set():
        _client_cancelled = bool(context.client_cancelled) if context else False
        _shutdown = bool(context.shutdown.is_set()) if context else False
        if record.status not in ("cancelled", "completed", "failed", "incomplete"):
            if _client_cancelled or record.cancel_requested:
                record.transition_to("cancelled")
            elif _shutdown:
                # Resilient+bg: leave in_progress for re-entry. Non-resilient: fail.
                _is_resilient_bg = (
                    runtime_options is not None
                    and runtime_options.resilient_background
                    and record.mode_flags.store
                    and record.mode_flags.background
                )
                if not _is_resilient_bg:
                    record.transition_to("failed")
            else:
                # Steering or unknown — mark failed.
                record.transition_to("failed")
        if not first_event_processed:
            record.response_failed_before_events = True
        record.response_created_signal.set()
        return True
    # Unknown CancelledError before any events were yielded means the handler
    # itself raised it — treat as handler failure.
    if not first_event_processed:
        logger.error(
            "Unknown CancelledError during background processing (response_id=%s)",
            response_id,
        )
        record.set_response_snapshot(
            _resolve_failed_response(
                record.response,
                response_id,
                agent_reference,
                model,
                created_at=context.created_at if context else None,
            )
        )
        record.transition_to("failed")
        record.response_failed_before_events = True
        record.response_created_signal.set()
        return True
    return False


async def _bg_persist_terminal(
    record: ResponseExecution,
    *,
    store: bool,
    provider: "ResponseProviderProtocol | None",
    exit_for_recovery: bool,
    provider_created: bool,
    context: "ResponseContext | None",
    response_id: str,
    agent_reference: "AgentReference | dict[str, Any]",
    model: str | None,
    history_limit: int,
) -> None:
    """Persist the terminal state of a bg non-stream response (Spec 033 §3.2).

    Update-after-runner for ``store`` responses: updates the persisted snapshot
    (or creates it when the handler never reached ``response.created``). On a
    persist failure, marks ``record.persistence_failed`` and replaces the
    snapshot with a ``storage_error`` ``response.failed``. A no-op when not
    storing, when deferring to recovery, when cancelled, or with no snapshot.

    :param record: The execution record.
    :type record: ResponseExecution
    :keyword store: Whether the response is stored.
    :paramtype store: bool
    :keyword provider: The persistence provider.
    :paramtype provider: ResponseProviderProtocol | None
    :keyword exit_for_recovery: True when deferring to next-lifetime recovery.
    :paramtype exit_for_recovery: bool
    :keyword provider_created: True if ``create_response`` already ran at created.
    :paramtype provider_created: bool
    :keyword context: The response context (for platform context / created_at).
    :paramtype context: ResponseContext | None
    :keyword response_id: The response id.
    :paramtype response_id: str
    :keyword agent_reference: The normalized agent reference.
    :paramtype agent_reference: AgentReference | dict[str, Any]
    :keyword model: The model name.
    :paramtype model: str | None
    :keyword history_limit: History fetch limit for a late create.
    :paramtype history_limit: int
    """
    if not (
        store
        and provider is not None
        and not exit_for_recovery
        and record.status not in {"cancelled"}
        and record.response is not None
    ):
        return
    if record.persistence_failed:
        # Phase 1 already failed — skip update attempt and apply storage error.
        storage_error_response = _resolve_failed_response(
            record.response,
            response_id,
            agent_reference,
            model,
            created_at=context.created_at if context else None,
            error_code="storage_error",
            error_message=_STORAGE_ERROR_MESSAGE,
        )
        record.set_response_snapshot(storage_error_response)
        record.status = "failed"  # type: ignore[assignment]
        return
    _context = context.platform_context if context else None
    try:
        if provider_created:
            await provider.update_response(record.response, context=_context)
        else:
            # Response was never created (handler yielded nothing or failed
            # before response.created) — create instead of update. Load history
            # items if previous_response_id is set so the input_items endpoint
            # can return history + current.
            _history_ids = (
                await provider.get_history_item_ids(
                    record.previous_response_id,
                    None,
                    history_limit,
                    context=_context,
                )
                if record.previous_response_id
                else None
            )
            _resolved_items = await _resolve_input_items_for_persistence(context, record.input_items)
            await provider.create_response(record.response, _resolved_items, _history_ids, context=_context)
    except Exception as persist_exc:  # pylint: disable=broad-exception-caught
        setattr(persist_exc, PLATFORM_ERROR_TAG, True)
        logger.error(
            "Persistence failed at bg non-stream finalization (response_id=%s): %s",
            response_id,
            persist_exc,
            exc_info=True,
        )
        record.persistence_failed = True
        record.persistence_exception = persist_exc
        storage_error_response = _resolve_failed_response(
            record.response,
            response_id,
            agent_reference,
            model,
            created_at=context.created_at if context else None,
            error_code="storage_error",
            error_message=_STORAGE_ERROR_MESSAGE,
        )
        record.set_response_snapshot(storage_error_response)
        record.status = "failed"  # type: ignore[assignment]


class _BgRunState:
    """Mutable loop state for :func:`_run_background_non_stream` (Spec 033 §3.2).

    Bundles the cross-boundary state threaded through the event-drain helper and
    read by the finalization (handler_events, provider_created, exit_for_recovery)
    plus the loop-internal accumulators.
    """

    __slots__ = (
        "handler_events",
        "validator",
        "first_event_processed",
        "output_item_count",
        "checkpoint_snapshot",
        "terminal_seen",
        "exit_for_recovery",
        "provider_created",
    )

    def __init__(self) -> None:
        self.handler_events: list[generated_models.ResponseStreamEvent] = []
        self.validator: EventStreamValidator = EventStreamValidator()
        self.first_event_processed: bool = False
        self.output_item_count: int = 0
        self.checkpoint_snapshot: bytes | None = None
        self.terminal_seen: bool = False
        self.exit_for_recovery: bool = False
        self.provider_created: bool = False


async def _bg_drain_handler_events(
    st: "_BgRunState",
    record: ResponseExecution,
    create_fn: "Callable[..., AsyncIterator[generated_models.ResponseStreamEvent]]",
    parsed: CreateResponse,
    context: "ResponseContext | None",
    cancellation_signal: asyncio.Event,
    *,
    store: bool,
    provider: "ResponseProviderProtocol | None",
    response_id: str,
    agent_reference: "AgentReference | dict[str, Any]",
    model: str | None,
    agent_session_id: str | None,
    conversation_id: str | None,
    history_limit: int,
    runtime_options: "ResponsesServerOptions | None",
) -> bool:
    """Drive the handler event loop for a bg non-stream run (Spec 033 §3.2).

    Intercepts ``stream.checkpoint()`` events, normalises/validates each event,
    runs the first-event registration + persistence, and resolves the
    cancellation / handler-error winddown onto ``record`` / ``st``. Returns True
    when the caller should ``return`` (discarded / failed-before-events). An
    unknown ``CancelledError`` is re-raised; ``ResponseExitForRecovery``
    propagates to the caller.

    :param st: The mutable loop state.
    :type st: _BgRunState
    :param record: The execution record.
    :type record: ResponseExecution
    :param create_fn: The handler's async generator callable.
    :type create_fn: Callable[..., AsyncIterator[generated_models.ResponseStreamEvent]]
    :param parsed: The parsed request.
    :type parsed: CreateResponse
    :param context: The response context.
    :type context: ResponseContext | None
    :param cancellation_signal: The cancellation event.
    :type cancellation_signal: asyncio.Event
    :keyword store: Whether the response is stored.
    :paramtype store: bool
    :keyword provider: The persistence provider.
    :paramtype provider: ResponseProviderProtocol | None
    :keyword response_id: The response id.
    :paramtype response_id: str
    :keyword agent_reference: The normalized agent reference.
    :paramtype agent_reference: AgentReference | dict[str, Any]
    :keyword model: The model name.
    :paramtype model: str | None
    :keyword agent_session_id: The resolved session id.
    :paramtype agent_session_id: str | None
    :keyword conversation_id: The conversation id.
    :paramtype conversation_id: str | None
    :keyword history_limit: History fetch limit.
    :paramtype history_limit: int
    :keyword runtime_options: Server runtime options.
    :paramtype runtime_options: ResponsesServerOptions | None
    :returns: True if the caller should ``return`` immediately.
    :rtype: bool
    """
    try:
        async for handler_event in _iter_with_winddown(
            create_fn(parsed, context, cancellation_signal), cancellation_signal
        ):
            # Intercept developer ``stream.checkpoint()`` events (spec 025 §A.3):
            # persist (resilient background only) and never forward them.
            if isinstance(handler_event, ResponseCheckpointEvent):
                st.checkpoint_snapshot = await _do_checkpoint_persist(
                    handler_event,
                    provider=provider,
                    runtime_options=runtime_options,
                    store=store,
                    background=record.mode_flags.background,
                    context=context.platform_context if context else None,
                    response_id=response_id,
                    last_snapshot=st.checkpoint_snapshot,
                    terminal_seen=st.terminal_seen,
                )
                continue
            # Client-initiated cancel → discard and force cancelled.
            if _bg_discard_on_client_cancel(record, cancellation_signal):
                return True

            normalized = _bg_normalize_event(
                handler_event,
                response_id=response_id,
                agent_reference=agent_reference,
                model=model,
                agent_session_id=agent_session_id,
                conversation_id=conversation_id,
            )
            st.handler_events.append(normalized)
            st.validator.validate_next(normalized)
            if normalized.get("type") in _ResponseOrchestrator._TERMINAL_SSE_TYPES:  # pylint: disable=protected-access
                st.terminal_seen = True
            if not st.first_event_processed:
                st.first_event_processed = True
                await _bg_handle_first_event(
                    record,
                    normalized,
                    st.handler_events,
                    st=st,
                    context=context,
                    store=store,
                    provider=provider,
                    response_id=response_id,
                    agent_reference=agent_reference,
                    model=model,
                    agent_session_id=agent_session_id,
                    conversation_id=conversation_id,
                    history_limit=history_limit,
                )
            else:
                st.output_item_count = _bg_track_output_count(normalized, st.output_item_count)
    except asyncio.CancelledError:
        if _bg_resolve_cancelled(
            record,
            cancellation_signal=cancellation_signal,
            context=context,
            first_event_processed=st.first_event_processed,
            runtime_options=runtime_options,
            response_id=response_id,
            agent_reference=agent_reference,
            model=model,
        ):
            return True
        # After events the CancelledError is most likely event-loop / scope
        # teardown — re-raise so the shielded runner can absorb it.
        raise
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.error(
            "Handler raised during background processing (response_id=%s)",
            response_id,
            exc_info=exc,
        )
        if record.status != "cancelled":
            record.set_response_snapshot(
                _resolve_failed_response(
                    record.response,
                    response_id,
                    agent_reference,
                    model,
                    created_at=context.created_at if context else None,
                )
            )
            record.transition_to("failed")
        if not st.first_event_processed:
            # Mark failure before any events so run_background can return HTTP 500.
            record.response_failed_before_events = True
        record.response_created_signal.set()  # unblock run_background on failure
        return True
    return False


async def _run_background_non_stream(
    *,
    create_fn: Callable[..., AsyncIterator[generated_models.ResponseStreamEvent]],
    parsed: CreateResponse,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
    record: ResponseExecution,
    response_id: str,
    agent_reference: AgentReference | dict[str, Any],
    model: str | None,
    provider: ResponseProviderProtocol | None = None,
    store: bool = True,
    agent_session_id: str | None = None,
    conversation_id: str | None = None,
    history_limit: int = 100,
    runtime_state: _RuntimeState | None = None,
    runtime_options: ResponsesServerOptions | None = None,
) -> None:
    """Execute a non-stream handler in the background and update the execution record.

    Collects handler events, builds the response payload, and transitions the
    record status to ``completed``, ``failed``, or ``cancelled``.

    :keyword create_fn: The handler's async generator callable.
    :keyword type create_fn: Callable[..., AsyncIterator[ResponseStreamEvent]]
    :keyword parsed: Parsed ``CreateResponse`` model instance.
    :keyword type parsed: CreateResponse
    :keyword context: Runtime response context for this request.
    :keyword type context: ResponseContext
    :keyword cancellation_signal: Event signalling that cancellation was requested.
    :keyword type cancellation_signal: asyncio.Event
    :keyword record: The mutable execution record to update.
    :keyword type record: ResponseExecution
    :keyword response_id: The response ID for this execution.
    :keyword type response_id: str
    :keyword agent_reference: Normalized agent reference model or dictionary.
    :keyword type agent_reference: AgentReference | dict[str, Any]
    :keyword model: Model name, or ``None``.
    :keyword type model: str | None
    :keyword provider: Optional persistence provider; when set and ``store`` is ``True``,
        ``update_response`` is called after terminal state is reached.
    :keyword type provider: ResponseProviderProtocol | None
    :keyword store: Whether the response should be persisted via the provider.
    :keyword type store: bool
    :keyword agent_session_id: Resolved session ID (B39).
    :keyword type agent_session_id: str | None
    :keyword conversation_id: Optional conversation ID for multi-turn sessions.
    :keyword type conversation_id: str | None
    :keyword history_limit: Maximum number of history items to include.
    :keyword type history_limit: int
    :keyword runtime_state: Runtime state tracker for eager eviction after persist.
    :keyword type runtime_state: _RuntimeState | None
    :keyword runtime_options: Runtime options controlling response execution behavior.
    :keyword type runtime_options: ResponsesServerOptions | None
    :return: None
    :rtype: None
    """
    record.transition_to("in_progress")
    st = _BgRunState()
    try:
        try:
            if await _bg_drain_handler_events(
                st,
                record,
                create_fn,
                parsed,
                context,
                cancellation_signal,
                store=store,
                provider=provider,
                response_id=response_id,
                agent_reference=agent_reference,
                model=model,
                agent_session_id=agent_session_id,
                conversation_id=conversation_id,
                history_limit=history_limit,
                runtime_options=runtime_options,
            ):
                return
        except ResponseExitForRecovery:
            # Spec 025 §A.4: the handler deferred to next-lifetime recovery.
            # Leave the last checkpointed snapshot as the resilient state and
            # re-raise so the resilient task body performs the recovery
            # translation. The finally block must NOT persist the
            # (pre-terminal) record.response over the checkpoint.
            st.exit_for_recovery = True
            record.response_created_signal.set()
            raise

        # Client-initiated cancel: force cancelled status. Steering cancel:
        # the handler already emitted events — fall through to terminal extraction.
        if _bg_discard_on_client_cancel(record, cancellation_signal):
            record.response_created_signal.set()  # unblock run_background on cancellation
            return

        _bg_resolve_terminal_status(
            record,
            st.handler_events,
            response_id=response_id,
            agent_reference=agent_reference,
            model=model,
            agent_session_id=agent_session_id,
            conversation_id=conversation_id,
        )
    finally:
        # Always unblock run_background (idempotent if already set)
        record.response_created_signal.set()
        # Stamp mode flags so the provider fallback can enforce B1/B2 checks
        # after eager eviction removes the in-memory record.
        if record.response is not None:
            record.response["background"] = record.mode_flags.background
        # Persist terminal state update via provider (bg non-stream). §3.5:
        # persistence failure sets persistence_failed + storage_error; §A.4:
        # skip when deferring to recovery so the checkpoint is not clobbered.
        await _bg_persist_terminal(
            record,
            store=store,
            provider=provider,
            exit_for_recovery=st.exit_for_recovery,
            provider_created=st.provider_created,
            context=context,
            response_id=response_id,
            agent_reference=agent_reference,
            model=model,
            history_limit=history_limit,
        )
        # Eager eviction: free memory once terminal (or store=False). Skip when
        # persistence failed — the in-memory record is the only GET source.
        if runtime_state is not None and record.is_terminal and not record.persistence_failed:
            await runtime_state.try_evict(response_id)


def _refresh_background_status(record: ResponseExecution) -> None:
    """Refresh the status of a background execution record.

    Checks the execution task state and cancellation signal to update the
    record status. Called by GET/DELETE/cancel endpoints to reflect the
    current runner state without triggering execution.

    :param record: The execution record to refresh.
    :type record: ResponseExecution
    :return: None
    :rtype: None
    """
    if not record.mode_flags.background or record.is_terminal:
        return

    if record.cancel_signal.is_set() and not record.is_terminal:
        record.status = "cancelled"
        return

    # execution_task is started immediately in run_background (Task 3.1)
    if record.execution_task is not None and record.execution_task.done():
        if not record.is_terminal:
            if record.execution_task.cancelled():
                record.status = "cancelled"
            else:
                exc = record.execution_task.exception()
                if exc is not None:
                    record.status = "failed"


class _HandlerError(Exception):
    """Raised by :meth:`_ResponseOrchestrator.run_sync` when the handler raises.

    Callers should catch this to convert it into an appropriate HTTP error
    response without leaking orchestrator internals.
    """

    def __init__(self, original: BaseException) -> None:
        self.original = original
        super().__init__(str(original))


def _make_ephemeral_record(ctx: "_ExecutionContext", state: "_PipelineState") -> "ResponseExecution":
    """Create a transient ResponseExecution for non-bg streams needing persistence.

    Used by ``_persist_and_resolve_terminal`` when no ``state.bg_record`` exists
    (non-background streaming paths, empty-handler bg+stream fallback).  The
    record carries mode_flags and other metadata needed to drive the
    persistence attempt and track failure state.

    For background+store invocations the record's ``subject`` is bound to
    the per-response stream from the registry so that
    ``_persist_and_resolve_terminal`` emits the resolved terminal to the
    same fan-out target the live wire iterator is subscribed to. (Non-bg
    streams do not need this binding — ``replay_enabled`` is False and
    GET ?stream=true returns 400 for them.)

    :param ctx: Current execution context.
    :type ctx: _ExecutionContext
    :param state: Mutable pipeline state.
    :type state: _PipelineState
    :return: A new ResponseExecution suitable for persistence tracking.
    :rtype: ResponseExecution
    """
    record = ResponseExecution(
        response_id=ctx.response_id,
        mode_flags=ResponseModeFlags(stream=True, store=ctx.store, background=ctx.background),
        status="in_progress",
        input_items=deepcopy(ctx.input_items),
        previous_response_id=ctx.previous_response_id,
        agent_session_id=ctx.agent_session_id,
        conversation_id=ctx.conversation_id,
        user_id_key=ctx.user_id,
    )
    # Stash on state so _finalize_stream can access persistence_failed
    state.bg_record = record
    return record


class _PipelineState:
    """Mutable in-flight state for a single create-response invocation.

    Intentionally separate from :class:`_ExecutionContext` (which is a pure
    immutable per-request input value object).  Created locally inside
    :meth:`_ResponseOrchestrator._live_stream` and
    :meth:`_ResponseOrchestrator.run_sync`, then threaded through every
    internal helper so that the helpers are side-effect-free with respect
    to ``_ExecutionContext``.
    """

    __slots__ = (
        "handler_events",
        "bg_record",
        "captured_error",
        "validator",
        "stream_interrupted",
        "pending_terminal",
        "provider_created",
        "next_seq",
        "leave_stream_open_for_recovery",
        "last_persisted_snapshot",
    )

    def __init__(self) -> None:
        self.handler_events: list[generated_models.ResponseStreamEvent] = []
        self.bg_record: ResponseExecution | None = None
        self.captured_error: BaseException | None = None
        self.validator: EventStreamValidator = EventStreamValidator()
        self.stream_interrupted: bool = False
        self.pending_terminal: generated_models.ResponseStreamEvent | None = None
        self.provider_created: bool = False
        # Next sequence number to stamp on the outgoing event. Seeded
        # from the prior persisted event count on recovered entry so
        # the recovered attempt's events have seq numbers strictly
        # succeeding the pre-crash events — keeps the assembled
        # (cross-attempt) stream monotonic. On fresh entry this stays
        # 0 and the first event lands at seq=0.
        self.next_seq: int = 0
        # Set by the exception handler when SHUTTING_DOWN is detected
        # for a resilient_background+store response. Signals the resilient
        # stream body's ``finally`` to SKIP the finalize+close step so
        # the wire stream stays in OPEN state. The next lifetime's
        # recovered handler re-opens the same registry entry (file-
        # backed, rehydrated from disk) and appends its events from
        # next_seq — preserving cross-attempt continuity per spec 017
        # streaming.md. Without this flag, closing the stream flushes
        # a terminal marker and the rehydrated stream is in CLOSED
        # state — the recovered handler's emits silently no-op.
        self.leave_stream_open_for_recovery: bool = False
        # Serialised bytes of the last snapshot persisted via a developer
        # ``stream.checkpoint()`` (spec 025 §A.3). Used for the idempotency
        # byte-compare so a checkpoint that adds nothing is a no-op.
        self.last_persisted_snapshot: bytes | None = None


class _ResponseOrchestrator:
    """Event-pipeline orchestrator for the Responses API.

    Handles the business logic for streaming, synchronous, and background
    create-response requests: driving the handler iterator, normalising events,
    managing the background execution record, and finalising persistent state.

    This class has no dependency on Starlette types.
    """

    _TERMINAL_SSE_TYPES: frozenset[str] = frozenset(
        {
            "response.completed",
            "response.failed",
            "response.incomplete",
        }
    )

    def __init__(
        self,
        *,
        create_fn: Callable[..., AsyncIterator[generated_models.ResponseStreamEvent]],
        runtime_state: _RuntimeState,
        runtime_options: ResponsesServerOptions,
        provider: ResponseProviderProtocol,
        acceptance_hook: Any | None = None,
    ) -> None:
        """Initialise the orchestrator.

        :param create_fn: The bound ``create_fn`` method from the registered handler.
        :type create_fn: Callable[..., AsyncIterator[ResponseStreamEvent]]
        :param runtime_state: In-memory execution record store.
        :type runtime_state: _RuntimeState
        :param runtime_options: Server runtime options (keep-alive, etc.).
        :type runtime_options: ResponsesServerOptions
        :param provider: Persistence provider for response envelopes and input items.
        :type provider: ResponseProviderProtocol
        """
        self._create_fn = create_fn
        self._runtime_state = runtime_state
        self._runtime_options = runtime_options
        self._provider = provider
        self._acceptance_hook = acceptance_hook
        # Optional shutdown-signal handle, wired by the host's _routing.py
        # post-construction. When set, the cancellation/exception
        # handlers in the streaming pipeline can detect "server is in
        # graceful shutdown right now" — earlier than the resilient task
        # framework's ``ctx.shutdown`` event, which only fires once
        # ``TaskManager.shutdown()`` runs (after Hypercorn has begun
        # draining). The race matters for upstream-client failures
        # triggered by SIGTERM propagating through the server's process
        # group: without this signal, the orchestrator would treat them
        # as plain handler exceptions and bake a "failed" terminal,
        # contradicting the resilience contract (resilient_background
        # responses must remain in_progress for next-lifetime recovery).
        self._shutdown_event: "asyncio.Event | None" = None

        # Eagerly create the resilient orchestrator so the @task function
        # is registered in _REGISTERED_DESCRIPTORS before TaskManager.startup()
        # runs recovery. Without this, stale tasks from a previous crash would
        # not be recovered until the first HTTP request triggers lazy creation.
        # Eager creation is unconditional: Rows 2/3 also need recovery
        # dispatch even when ``resilient_background=False`` — they use the same
        # @task function with a ``disposition="mark-failed"`` payload that
        # the recovery body honours.
        from ._resilient_orchestrator import (
            ResilientResponseOrchestrator,
        )  # pylint: disable=import-outside-toplevel

        self._resilient_orchestrator = ResilientResponseOrchestrator(
            create_fn=create_fn,
            options=runtime_options,
            provider=provider,
            runtime_state=runtime_state,
            parent_orchestrator=self,
        )

    # ------------------------------------------------------------------
    # Internal helpers (stream path)
    # ------------------------------------------------------------------

    @staticmethod
    async def _safe_emit(
        stream: "EventStream | None",
        event: Any,
    ) -> None:
        """Emit ``event`` to ``stream`` tolerating closed/destroyed streams.

        The legacy publish-to-subject API was silent on a completed
        subject; the registry's ``emit`` raises ``EventStreamClosedError``
        / ``EventStreamNotFoundError`` instead. Some callsites (cleanup
        finally blocks, race-prone short-circuits) intentionally rely on
        the silent semantics — wrap them via this helper rather than
        sprinkling try/except.

        :param stream: The event stream to emit to, or ``None``.
        :type stream: EventStream | None
        :param event: The event to emit.
        :type event: Any
        :return: None
        :rtype: None
        """
        if stream is None:
            return
        try:
            await stream.emit(event)
        except (EventStreamClosedError, EventStreamNotFoundError):
            return
        except Exception:  # pylint: disable=broad-exception-caught
            # Best-effort fan-out — never let a stream backing failure
            # propagate into orchestration logic.
            logger.debug("stream emit failed", exc_info=True)

    @staticmethod
    async def _safe_close(stream: "EventStream | None") -> None:
        """Close ``stream`` tolerating already-closed / destroyed.

        :param stream: The event stream to close, or ``None``.
        :type stream: EventStream | None
        :return: None
        :rtype: None
        """
        if stream is None:
            return
        try:
            await stream.close()
        except Exception:  # pylint: disable=broad-exception-caught
            logger.debug("stream close failed", exc_info=True)

    async def _normalize_and_append(
        self,
        ctx: _ExecutionContext,
        state: _PipelineState,
        handler_event: generated_models.ResponseStreamEvent | dict[str, Any],
    ) -> generated_models.ResponseStreamEvent:
        """Coerce, validate, normalise, and append a handler event to the pipeline state.

        Also propagates the event into the background record and its stream when active.
        Raises ``ValueError`` on structural validation failure (B30) so that
        :meth:`_process_handler_events` can emit ``response.failed`` (streaming)
        or propagate as :class:`_HandlerError` (sync → HTTP 500).

        :param ctx: Current execution context (immutable inputs).
        :type ctx: _ExecutionContext
        :param state: Mutable pipeline state for this invocation.
        :type state: _PipelineState
        :param handler_event: Raw event emitted by the handler.
        :type handler_event: ResponseStreamEvent | dict[str, Any]
        :return: The normalised event (``ResponseStreamEvent`` model instance).
        :rtype: ResponseStreamEvent
        :raises ValueError: If the coerced event fails structural validation (B30).
        """
        coerced = _coerce_handler_event(handler_event)
        violation = _validate_handler_event(coerced)
        if violation:
            raise ValueError(violation)
        normalized = _apply_stream_event_defaults(
            coerced,
            response_id=ctx.response_id,
            agent_reference=ctx.agent_reference,
            model=ctx.model,
            sequence_number=state.next_seq,
            agent_session_id=ctx.agent_session_id,
            conversation_id=ctx.conversation_id,
        )
        state.handler_events.append(normalized)
        state.next_seq += 1
        state.validator.validate_next(normalized)
        if state.bg_record is not None:
            state.bg_record.apply_event(normalized, state.handler_events)
            # Defer emit for terminal events — the buffer-then-persist
            # pattern may replace the terminal event on persistence failure.
            # The resolved terminal is emitted by _persist_and_resolve_terminal.
            if state.bg_record.subject is not None and normalized.get("type") not in self._TERMINAL_SSE_TYPES:
                await self._safe_emit(state.bg_record.subject, normalized)
        return normalized

    @staticmethod
    def _has_terminal_event(
        handler_events: list[generated_models.ResponseStreamEvent],
    ) -> bool:
        """Return ``True`` if any terminal event has been emitted.

        :param handler_events: List of normalised handler events.
        :type handler_events: list[ResponseStreamEvent]
        :return: Whether a terminal event is present.
        :rtype: bool
        """
        return any(e["type"] in _ResponseOrchestrator._TERMINAL_SSE_TYPES for e in handler_events)

    async def _cancel_terminal_sse_dict(
        self, ctx: _ExecutionContext, state: _PipelineState
    ) -> generated_models.ResponseStreamEvent:
        """Build, normalise, append, and return a cancel-terminal event.

        Returns the normalised event (model instance) so that it can be consumed
        by the shared :meth:`_process_handler_events` pipeline.

        :param ctx: Current execution context (immutable inputs).
        :type ctx: _ExecutionContext
        :param state: Mutable pipeline state for this invocation.
        :type state: _PipelineState
        :return: Normalised cancel-terminal event.
        :rtype: ResponseStreamEvent
        """
        base = _extract_response_snapshot_from_events(
            state.handler_events,
            response_id=ctx.response_id,
            agent_reference=ctx.agent_reference,
            model=ctx.model,
            agent_session_id=ctx.agent_session_id,
            conversation_id=ctx.conversation_id,
        )
        cancel_event: dict[str, Any] = {
            "type": "response.failed",
            "response": _apply_cancelled_terminal(base),
        }
        return await self._normalize_and_append(ctx, state, cancel_event)

    async def _make_failed_event(
        self, ctx: _ExecutionContext, state: _PipelineState
    ) -> generated_models.ResponseStreamEvent:
        """Build, normalise, append, and return a ``response.failed`` event.

        Used for S-035 (handler exception after ``response.created``) and
        S-015 (handler completed without emitting a terminal event).

        :param ctx: Current execution context (immutable inputs).
        :type ctx: _ExecutionContext
        :param state: Mutable pipeline state for this invocation.
        :type state: _PipelineState
        :return: Normalised ``response.failed`` event.
        :rtype: ResponseStreamEvent
        """
        base = _extract_response_snapshot_from_events(
            state.handler_events,
            response_id=ctx.response_id,
            agent_reference=ctx.agent_reference,
            model=ctx.model,
            agent_session_id=ctx.agent_session_id,
            conversation_id=ctx.conversation_id,
        )
        failed_event: dict[str, Any] = {
            "type": "response.failed",
            "response": _apply_failed_terminal(
                base,
                error={"code": "server_error", "message": "An internal server error occurred."},
            ),
        }
        return await self._normalize_and_append(ctx, state, failed_event)

    def _apply_storage_error_replacement(
        self, ctx: _ExecutionContext, state: _PipelineState, record: ResponseExecution
    ) -> None:
        """Replace the pending terminal event with a storage_error response.failed.

        Mutates ``state.pending_terminal``, ``state.handler_events``, and
        ``record`` snapshot/status in place.

        :param ctx: Current execution context.
        :type ctx: _ExecutionContext
        :param state: Mutable pipeline state.
        :type state: _PipelineState
        :param record: The execution record to update.
        :type record: ResponseExecution
        """
        storage_error_response = _resolve_failed_response(
            record.response,
            ctx.response_id,
            ctx.agent_reference,
            ctx.model,
            created_at=ctx.context.created_at if ctx.context else None,
            error_code="storage_error",
            error_message=_STORAGE_ERROR_MESSAGE,
        )
        replacement_event: dict[str, Any] = {
            "type": "response.failed",
            "response": dict(storage_error_response),
        }

        # Determine the sequence_number: reuse the original pending terminal's
        # sequence_number (in-place replacement) to avoid gaps. Falls back
        # to ``state.next_seq`` (the next monotonic seq for this attempt —
        # accounts for prior persisted events on recovered entry).
        original_pending = state.pending_terminal
        replacement_index = -1
        replacement_seq = state.next_seq
        if original_pending is not None:
            for idx, evt in enumerate(state.handler_events):
                if evt is original_pending:
                    replacement_index = idx
                    replacement_seq = int(evt.get("sequence_number", idx))
                    break

        coerced = _coerce_handler_event(replacement_event)
        replacement_normalized = _apply_stream_event_defaults(
            coerced,
            response_id=ctx.response_id,
            agent_reference=ctx.agent_reference,
            model=ctx.model,
            sequence_number=replacement_seq,
            agent_session_id=ctx.agent_session_id,
            conversation_id=ctx.conversation_id,
        )
        if replacement_index >= 0:
            state.handler_events[replacement_index] = replacement_normalized
        else:
            state.handler_events.append(replacement_normalized)
            state.next_seq += 1
        state.pending_terminal = replacement_normalized
        record.set_response_snapshot(storage_error_response)
        # Force status to failed — bypass transition_to since the record may
        # already be in a terminal state (e.g. "completed") that doesn't allow
        # normal transitions.
        record.status = "failed"  # type: ignore[assignment]

    async def _maybe_override_to_cancelled(
        self,
        ctx: _ExecutionContext,
        state: _PipelineState,
        response_payload: dict[str, Any],
        status: "ResponseStatus",
    ) -> "tuple[dict[str, Any], ResponseStatus]":
        """Force a ``client_cancelled`` response's terminal to ``cancelled``.

        (Spec 033 §3.2 extract — B11/B17) Applies to both the ``/cancel`` API
        endpoint and non-bg POST client disconnect: without this override a
        handler that emits its own ``completed`` AFTER seeing the cancellation
        signal would have its terminal honored even though the framework promised
        ``cancelled`` to the client. Returns the (possibly overridden)
        ``(response_payload, status)`` and replaces ``state.pending_terminal``.

        :param ctx: Current execution context.
        :type ctx: _ExecutionContext
        :param state: Mutable pipeline state.
        :type state: _PipelineState
        :param response_payload: The resolved response snapshot dict.
        :type response_payload: dict[str, Any]
        :param status: The resolved terminal status.
        :type status: ResponseStatus
        :return: The (possibly overridden) ``(response_payload, status)``.
        :rtype: tuple[dict[str, Any], ResponseStatus]
        """
        _client_cancelled = bool(ctx.context.client_cancelled) if ctx.context else False
        if not (_client_cancelled and status != "cancelled"):
            return response_payload, status
        # Overlay ``cancelled`` onto the handler's resolved payload (preserving
        # its metadata/conversation/instructions/... — the handler owns those)
        # rather than rebuilding a bare-bones object. Output is cleared per B11.
        response_payload = _apply_cancelled_terminal(response_payload)
        response_payload["background"] = ctx.background
        # Replace state.pending_terminal with the cancel-terminal event so
        # the SSE wire and persistence see the overridden status.
        override_event: dict[str, Any] = {
            "type": "response.failed",
            "response": response_payload,
        }
        state.pending_terminal = await self._normalize_and_append(ctx, state, override_event)
        return response_payload, "cancelled"

    async def _persist_and_resolve_terminal(
        self, ctx: _ExecutionContext, state: _PipelineState, record: ResponseExecution
    ) -> generated_models.ResponseStreamEvent:
        """Attempt persistence and resolve the terminal event to yield.

        This method implements the buffer-then-persist-then-yield pattern:
        1. Builds the response snapshot from accumulated events.
        2. Attempts provider persistence (create or update).
        3. On success: returns the original ``state.pending_terminal``.
        4. On failure: replaces the terminal with a ``response.failed`` event
           carrying ``error_code="storage_error"`` and sets
           ``record.persistence_failed``.

        The caller must yield the returned event to the SSE stream.

        :param ctx: Current execution context (immutable inputs).
        :type ctx: _ExecutionContext
        :param state: Mutable pipeline state for this invocation.
        :type state: _PipelineState
        :param record: The execution record to update on failure.
        :type record: ResponseExecution
        :return: The resolved terminal event (original or storage-error replacement).
        :rtype: ResponseStreamEvent
        """
        assert state.pending_terminal is not None

        events = (
            state.handler_events
            if state.handler_events
            else _build_events(
                ctx.response_id,
                include_progress=True,
                agent_reference=ctx.agent_reference,
                model=ctx.model,
            )
        )
        response_payload = _extract_response_snapshot_from_events(
            events,
            response_id=ctx.response_id,
            agent_reference=ctx.agent_reference,
            model=ctx.model,
            agent_session_id=ctx.agent_session_id,
            conversation_id=ctx.conversation_id,
        )
        response_payload["background"] = ctx.background

        resolved_status = response_payload.get("status")
        status: ResponseStatus = (
            cast(ResponseStatus, resolved_status) if isinstance(resolved_status, str) else "completed"
        )

        # B11 + B17: client_cancelled overrides the handler's terminal to
        # ``cancelled`` regardless of what the handler ultimately emitted.
        response_payload, status = await self._maybe_override_to_cancelled(ctx, state, response_payload, status)

        # Guard: if the cancel endpoint already transitioned this record to a
        # terminal state (race between cancel endpoint and B11), skip the
        # transition. We still emit the pending terminal to the per-response
        # stream below so the live wire iterator (and replay subscribers)
        # see exactly one terminal event.
        cancel_race = bool(record.is_terminal and record.cancel_requested)

        if not cancel_race:
            # Update snapshot on record before persistence attempt
            record.set_response_snapshot(cast(generated_models.ResponseObject, response_payload))
            record.transition_to(status)

            # Attempt persistence
            if ctx.store and record.response is not None:
                if record.persistence_failed:
                    # Phase 1 already failed — skip persistence attempt, emit storage error directly.
                    self._apply_storage_error_replacement(ctx, state, record)
                else:
                    record.response["background"] = record.mode_flags.background
                    _context = ctx.context.platform_context if ctx.context else None
                    try:
                        if state.provider_created:
                            # bg+stream: initial create already done at response.created — use update
                            await self._provider.update_response(record.response, context=_context)
                        else:
                            # non-bg stream or bg stream where initial create was never registered:
                            # full create
                            _history_ids = (
                                await self._provider.get_history_item_ids(
                                    ctx.previous_response_id,
                                    None,
                                    self._runtime_options.default_fetch_history_count,
                                    context=_context,
                                )
                                if ctx.previous_response_id
                                else None
                            )
                            _resolved_items = await _resolve_input_items_for_persistence(ctx.context, ctx.input_items)
                            await self._provider.create_response(
                                cast(generated_models.ResponseObject, response_payload),
                                _resolved_items,
                                _history_ids,
                                context=_context,
                            )
                    except ResponseAlreadyExistsError:
                        # Recovery: response was persisted by a prior attempt. Convert
                        # this terminal-side create attempt into an update so the final
                        # state still lands in the store. (Spec 013 US1 deliverable (b).)
                        logger.info(
                            "Response %s already exists in store at terminal create (recovery — switching to update).",
                            ctx.response_id,
                        )
                        try:
                            await self._provider.update_response(record.response, context=_context)
                        except Exception as update_exc:  # pylint: disable=broad-exception-caught
                            setattr(update_exc, PLATFORM_ERROR_TAG, True)
                            logger.error(
                                "Terminal update_response after already-exists swallow failed (response_id=%s): %s",
                                ctx.response_id,
                                update_exc,
                                exc_info=True,
                            )
                            record.persistence_failed = True
                            record.persistence_exception = update_exc
                    except Exception as persist_exc:  # pylint: disable=broad-exception-caught
                        setattr(persist_exc, PLATFORM_ERROR_TAG, True)
                        logger.error(
                            "Persistence failed at terminal event (response_id=%s): %s",
                            ctx.response_id,
                            persist_exc,
                            exc_info=True,
                        )
                        record.persistence_failed = True
                        record.persistence_exception = persist_exc
                        self._apply_storage_error_replacement(ctx, state, record)

        # Emit the resolved terminal event to the per-response stream for
        # replay subscribers. This is deferred from _normalize_and_append
        # to ensure subscribers see the correct terminal (original on
        # success, storage_error replacement on failure).
        #
        # For bg+store paths the per-response stream is the only fan-out
        # target for GET ?stream=true replay — emit even if the in-memory
        # record has no subject bound (ephemeral records from the
        # empty-handler fallback path).
        if state.pending_terminal is not None:
            if state.bg_record is not None and state.bg_record.subject is not None:
                await self._safe_emit(state.bg_record.subject, state.pending_terminal)
            elif ctx.store and ctx.stream:
                # (Spec 024 Phase 2) For ALL store=True streaming responses
                # (Row 1/2/3 stream=T) — emit to the per-response stream so
                # the wire iterator subscribed in ``_live_stream`` receives
                # the terminal event. Pre-Phase-2 this was gated on
                # ``ctx.background and ctx.store`` because only Row 1 used
                # the wire_stream pattern; unified Row 2/3 stream now also
                # subscribe to wire_stream and need the terminal emit.
                _term_stream = await streams.get_or_create(ctx.response_id)
                await self._safe_emit(_term_stream, state.pending_terminal)

        # (Spec 024 Phase 2) Bookkeeping-task signal removed. The handler
        # now runs inside the resilient task body for all store=True rows
        # (Row 1/2/3) — the task body returns when the handler emits its
        # terminal, marking the task ``completed`` naturally. The
        # handler-in-task-body architecture removes the need for a
        # separate completion signal.

        return state.pending_terminal

    async def _register_bg_execution(
        self,
        ctx: _ExecutionContext,
        state: _PipelineState,
        first_normalized: generated_models.ResponseStreamEvent,
    ) -> None:
        """Create, seed, and register the background+stream execution record.

        Called from :meth:`_process_handler_events` after the first event is
        received.  The record is seeded with ``first_normalized`` so that
        subscribers joining mid-stream receive the full history.

        The record's ``subject`` is the per-response ``EventStream`` from the
        process-wide registry — the same instance is returned to any caller
        that does ``await streams.get_or_create(response_id)`` for this id
        (e.g. the live SSE wire iterator in :meth:`_live_stream`'s resilient
        branch, and the GET-replay endpoint after eager eviction).

        :param ctx: Current execution context (immutable inputs).
        :type ctx: _ExecutionContext
        :param state: Mutable pipeline state for this invocation.
        :type state: _PipelineState
        :param first_normalized: The first normalised handler event.
        :type first_normalized: ResponseStreamEvent
        """
        initial_payload = _extract_response_snapshot_from_events(
            state.handler_events,
            response_id=ctx.response_id,
            agent_reference=ctx.agent_reference,
            model=ctx.model,
            agent_session_id=ctx.agent_session_id,
            conversation_id=ctx.conversation_id,
        )
        # Stamp mode flags so the provider fallback can enforce B1/B2 checks
        # after eager eviction removes the in-memory record.
        # (Spec 024 Phase 2) Use ctx.background instead of hardcoded True so
        # Row 3 stream (fg+store+stream=T) registers with background=False
        # for correct B16 visibility + B11 cancel semantics.
        initial_payload["background"] = ctx.background
        initial_status = initial_payload.get("status")
        if not isinstance(initial_status, str):
            initial_status = "in_progress"
        execution = ResponseExecution(
            response_id=ctx.response_id,
            mode_flags=ResponseModeFlags(stream=True, store=True, background=ctx.background),
            status=cast(ResponseStatus, initial_status),
            input_items=deepcopy(ctx.input_items),
            previous_response_id=ctx.previous_response_id,
            cancel_signal=ctx.cancellation_signal,
            response_context=ctx.context,
            agent_session_id=ctx.agent_session_id,
            conversation_id=ctx.conversation_id,
            user_id_key=ctx.user_id,
        )
        execution.set_response_snapshot(cast(generated_models.ResponseObject, initial_payload))
        # Bind the per-response stream from the registry — the registry
        # guarantees the same instance for the same id, so any other caller
        # that does ``streams.get_or_create(response_id)`` for this id sees
        # the same fan-out target.
        execution.subject = await streams.get_or_create(ctx.response_id)
        state.bg_record = execution
        assert state.bg_record.subject is not None
        await self._runtime_state.add(execution)
        if ctx.store:
            _context = ctx.context.platform_context if ctx.context else None
            _initial_response_obj = cast(generated_models.ResponseObject, initial_payload)
            _history_ids = (
                await self._provider.get_history_item_ids(
                    ctx.previous_response_id,
                    None,
                    self._runtime_options.default_fetch_history_count,
                    context=_context,
                )
                if ctx.previous_response_id
                else None
            )
            _resolved_items = await _resolve_input_items_for_persistence(ctx.context, ctx.input_items)
            try:
                await self._provider.create_response(
                    _initial_response_obj,
                    _resolved_items,
                    _history_ids,
                    context=_context,
                )
                state.provider_created = True
            except ResponseAlreadyExistsError:
                # Recovery: response was persisted by a prior attempt.
                # Swallow and proceed; terminal update_response will fire.
                logger.info(
                    "Response %s already exists in store "
                    + "(recovery — swallowed by idempotent create at bg+stream first-event).",
                    ctx.response_id,
                )
                state.provider_created = True
            except Exception as persist_exc:  # pylint: disable=broad-exception-caught
                # §3.3: Phase 1 create failure for bg+stream — mark persistence
                # failed so the terminal event will carry storage_error.
                logger.error(
                    "Phase 1 create_response failed for bg+stream (response_id=%s): %s",
                    ctx.response_id,
                    persist_exc,
                    exc_info=True,
                )
                execution.persistence_failed = True
                execution.persistence_exception = persist_exc
                # Stamp the full storage-error response snapshot AND the
                # ``failed`` terminal status on the in-memory record so a
                # concurrent GET sees a consistent
                # ``status=failed error.code=storage_error`` envelope (not a
                # half-stamped record with status=failed and an in_progress
                # snapshot body). The downstream
                # ``_process_handler_events`` non-bg-stream branch re-stamps
                # the same snapshot — the early stamp here closes the
                # async window where GET could observe a
                # status/snapshot mismatch.
                execution.set_response_snapshot(
                    _resolve_failed_response(
                        execution.response,
                        ctx.response_id,
                        ctx.agent_reference,
                        ctx.model,
                        created_at=ctx.context.created_at if ctx.context else None,
                        error_code="storage_error",
                        error_message=_STORAGE_ERROR_MESSAGE,
                    )
                )
                execution.status = "failed"  # type: ignore[assignment]
        # Emit the first event AFTER persistence has been attempted. This
        # ensures replay subscribers (and the live wire iterator on the
        # resilient streaming path) never observe ``response.created`` when
        # Phase 1 create_response failed — matching the contract requirement
        # that no ``response.created`` precedes the standalone error event.
        #
        # (Spec 026 FR-026-1/2/2a) ``response.created`` is, by definition, the
        # first event of a resilient stream. On a recovered entry the resilient
        # stream already carries the pre-crash ``response.created``, so
        # re-appending it would make a reconnecting client observe
        # ``response.created`` twice. Gate the provider append on the stream
        # being EMPTY (no events ever appended): a fresh entry's stream is
        # empty -> append; a recovered entry's stream is non-empty -> suppress,
        # and the recovered handler's subsequent ``response.in_progress`` reset
        # becomes its first stream-visible event. Emptiness is read from the
        # cursor-capable resilient replay provider (``last_cursor() is None`` iff
        # empty). The persisted-but-stream-empty crash window (create_response
        # succeeded, crash before this emit) correctly re-appends
        # ``response.created`` because the stream is genuinely empty. Only the
        # provider append is gated; first-event validation, the seeded-output
        # baseline, and the in-memory snapshot already ran upstream.
        if not execution.persistence_failed:
            stream_is_empty = await state.bg_record.subject.last_cursor() is None
            if stream_is_empty:
                await self._safe_emit(state.bg_record.subject, first_normalized)

    async def _intercept_checkpoints(
        self,
        ctx: "_ExecutionContext",
        state: "_PipelineState",
        handler_iterator: AsyncIterator[generated_models.ResponseStreamEvent],
    ) -> AsyncIterator[generated_models.ResponseStreamEvent]:
        """Drain the handler, intercepting + persisting ``checkpoint()`` events.

        Checkpoint events are handled here (persistence) and are NOT
        re-yielded, so the downstream pipeline never coerces/validates/forwards
        them. All other events pass through unchanged.

        :param ctx: Current execution context.
        :type ctx: _ExecutionContext
        :param state: Mutable pipeline state.
        :type state: _PipelineState
        :param handler_iterator: The raw handler event iterator.
        :type handler_iterator: AsyncIterator[ResponseStreamEvent]
        :returns: The handler events with checkpoint events removed.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        async for raw in handler_iterator:
            if isinstance(raw, ResponseCheckpointEvent):
                await self._persist_checkpoint(ctx, state, raw)
                continue
            yield raw

    async def _persist_checkpoint(
        self,
        ctx: "_ExecutionContext",
        state: "_PipelineState",
        event: ResponseCheckpointEvent,
    ) -> None:
        """Persist a developer checkpoint snapshot (spec 025 §A.3).

        Persists only for resilient background responses; idempotent; failures are
        logged + tagged and never raised into the handler. Snapshots the
        response with whatever status it currently holds.

        :param ctx: Current execution context.
        :type ctx: _ExecutionContext
        :param state: Mutable pipeline state (holds the idempotency watermark).
        :type state: _PipelineState
        :param event: The checkpoint event carrying the response snapshot.
        :type event: ResponseCheckpointEvent
        :rtype: None
        """
        # Gate: only resilient background responses have a recovery re-invocation
        # path, so only they have a consumer for an in-flight checkpoint.
        state.last_persisted_snapshot = await _do_checkpoint_persist(
            event,
            provider=self._provider,
            runtime_options=self._runtime_options,
            store=ctx.store,
            background=ctx.background,
            context=ctx.context.platform_context if ctx.context is not None else None,
            response_id=ctx.response_id,
            last_snapshot=state.last_persisted_snapshot,
            terminal_seen=state.pending_terminal is not None,
        )

    async def _emit_standalone_error(
        self,
        ctx: _ExecutionContext,
        *,
        message: str = "An internal server error occurred.",
        code: str | None = None,
    ) -> generated_models.ResponseStreamEvent:
        """Build a standalone ``error`` event and emit it to the wire stream.

        Shared by the pre-creation error paths (B8 / B30 / first-event-contract):
        each constructs the same ``error`` event shape and, for store+stream
        rows, also publishes it to the per-response wire stream so the live
        iterator sees it. Returns the event for the caller to ``yield``.

        :param ctx: Current execution context.
        :type ctx: _ExecutionContext
        :keyword message: The client-facing error message.
        :paramtype message: str
        :keyword code: The optional error code.
        :paramtype code: str | None
        :returns: The constructed ``error`` event.
        :rtype: generated_models.ResponseStreamEvent
        """
        event = construct_event_model(
            {
                "type": "error",
                "message": message,
                "param": None,
                "code": code,
                "sequence_number": 0,
            }
        )
        if ctx.store and ctx.stream:
            _err_stream = await streams.get_or_create(ctx.response_id)
            await self._safe_emit(_err_stream, event)
        return event

    async def _acquire_first_event(
        self,
        ctx: _ExecutionContext,
        state: _PipelineState,
        handler_iterator: AsyncIterator[generated_models.ResponseStreamEvent],
    ) -> "tuple[generated_models.ResponseStreamEvent | None, list[generated_models.ResponseStreamEvent]]":
        """Acquire the handler's first event, handling the pre-creation paths.

        (Spec 033 §3.2 extract) Returns ``(first_raw, pre_events)``. On success
        ``first_raw`` is the first handler event and ``pre_events`` is empty. On an
        empty handler / pre-creation cancellation / pre-creation error
        (B8 / B17 / S-024) ``first_raw`` is ``None`` (the caller stops the
        pipeline) and ``pre_events`` holds the contract-mandated fallback /
        ``error`` events for the caller to yield; ``state.pending_terminal`` /
        ``state.captured_error`` may be set. An unknown ``CancelledError`` is
        re-raised.

        :param ctx: Current execution context.
        :type ctx: _ExecutionContext
        :param state: Mutable pipeline state.
        :type state: _PipelineState
        :param handler_iterator: The handler's event iterator.
        :type handler_iterator: AsyncIterator[ResponseStreamEvent]
        :returns: ``(first_raw_or_None, pre_events)``.
        :rtype: tuple[ResponseStreamEvent | None, list[ResponseStreamEvent]]
        """
        pre: list[generated_models.ResponseStreamEvent] = []
        try:
            return await handler_iterator.__anext__(), pre
        except StopAsyncIteration:
            # B17: Handler exited without yielding after cancellation — treat as
            # a cancellation (not an empty handler) so run_sync raises and the
            # response is never persisted.
            if ctx.cancellation_signal.is_set():
                state.captured_error = asyncio.CancelledError()
                return None, pre
            # Handler yielded nothing: synthesise fallback lifecycle events.
            fallback_events = _build_events(
                ctx.response_id,
                include_progress=True,
                agent_reference=ctx.agent_reference,
                model=ctx.model,
            )
            for event in fallback_events:
                # Re-stamp with the monotonic ``state.next_seq`` (defaults seq=0).
                event["sequence_number"] = state.next_seq
                state.handler_events.append(event)
                state.next_seq += 1
                # For store + (bg or stream) the canonical record isn't registered
                # yet — bind the per-response stream so the wire iterator sees the
                # fallback events. Skip terminal (the caller emits the resolved one).
                if ctx.store and (ctx.background or ctx.stream) and event.get("type") not in self._TERMINAL_SSE_TYPES:
                    _fallback_stream = await streams.get_or_create(ctx.response_id)
                    await self._safe_emit(_fallback_stream, event)
                if event.get("type") in self._TERMINAL_SSE_TYPES:
                    state.pending_terminal = event
                else:
                    pre.append(event)
            return None, pre
        except asyncio.CancelledError:
            # S-024: Known cancellation before first event.
            if ctx.cancellation_signal.is_set():
                state.captured_error = asyncio.CancelledError()
                pre.append(
                    construct_event_model(
                        {
                            "type": "error",
                            "message": "An internal server error occurred.",
                            "param": None,
                            "code": None,
                            "sequence_number": 0,
                        }
                    )
                )
                return None, pre
            # Unknown CancelledError (e.g. event-loop teardown) — re-raise.
            raise
        except Exception as exc:  # pylint: disable=broad-exception-caught
            # B8: Pre-creation error → standalone `error` event only.
            logger.error(
                "Handler raised before response.created (response_id=%s)",
                ctx.response_id,
                exc_info=exc,
            )
            state.captured_error = exc
            pre.append(await self._emit_standalone_error(ctx))
            return None, pre

    async def _process_handler_events(
        self,
        ctx: _ExecutionContext,
        state: _PipelineState,
        handler_iterator: AsyncIterator[generated_models.ResponseStreamEvent],
    ) -> AsyncIterator[generated_models.ResponseStreamEvent]:
        """Shared event pipeline: coerce → normalise → apply_event → subject publish.

        This async generator is the single authoritative event pipeline consumed by
        both :meth:`_live_stream` (streaming) and :meth:`run_sync` (synchronous).
        It handles:

        - Empty handler (``StopAsyncIteration`` before the first event): synthesises
          a full lifecycle event sequence and yields it.
        - Pre-creation handler exception (B8): yields a standalone ``error`` event
          and sets ``state.captured_error``.
        - First-event normalisation and bg+store record registration
          (:meth:`_register_bg_execution`).
        - Remaining events via :meth:`_normalize_and_append`.
        - Post-creation handler exception (S-035): yields a ``response.failed`` event
          and sets ``state.captured_error``.
        - Missing terminal after successful handler completion (S-015): yields a
          ``response.failed`` event without setting ``state.captured_error`` so that
          synchronous callers can return HTTP 200 with a ``"failed"`` body.
        - Cancellation winddown (B11): yields a cancel-terminal event when the
          cancellation signal is set and no terminal event was emitted.

        :param ctx: Current execution context (immutable inputs).
        :type ctx: _ExecutionContext
        :param state: Mutable pipeline state for this invocation.
        :type state: _PipelineState
        :param handler_iterator: Async generator returned by the handler's
            ``create_fn`` factory.
        :type handler_iterator: AsyncIterator[ResponseStreamEvent]
        :return: Async iterator of normalised events (``ResponseStreamEvent`` model instances).
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        # Intercept developer ``stream.checkpoint()`` events (spec 025 §A.3)
        # BEFORE any coercion/validation/forwarding: they are persisted
        # by the orchestrator and never reach the wire or the event taxonomy.
        handler_iterator = self._intercept_checkpoints(ctx, state, handler_iterator)
        # --- First event acquisition (StopAsyncIteration / cancel / B8) ---
        first_raw, _pre_events = await self._acquire_first_event(ctx, state, handler_iterator)
        for _ev in _pre_events:
            yield _ev
        if first_raw is None:
            return

        # Normalise the first event manually (before _normalize_and_append so we
        # can set up the bg record with the correct sequence number).
        first_coerced = _coerce_handler_event(first_raw)

        # B30: structural validation of the first event.
        b30_violation = _validate_handler_event(first_coerced)
        if b30_violation:
            logger.error(
                "Handler event structure violation (response_id=%s): %s",
                ctx.response_id,
                b30_violation,
            )
            state.captured_error = ValueError(b30_violation)
            yield await self._emit_standalone_error(ctx)
            return

        first_normalized = _apply_stream_event_defaults(
            first_coerced,
            response_id=ctx.response_id,
            agent_reference=ctx.agent_reference,
            model=ctx.model,
            sequence_number=state.next_seq,
            agent_session_id=ctx.agent_session_id,
            conversation_id=ctx.conversation_id,
        )

        # /: first-event contract validation.
        # Violations are treated the same as B8 pre-creation errors:
        # - streaming: yield a standalone 'error' event and return (no record created)
        # - sync: state.captured_error is set → run_sync raises _HandlerError → HTTP 500
        violation = _check_first_event_contract(first_normalized, ctx.response_id)
        if violation:
            logger.error(
                "First-event contract violation (response_id=%s): %s",
                ctx.response_id,
                violation,
            )
            state.captured_error = RuntimeError(violation)
            yield await self._emit_standalone_error(ctx)
            return

        state.handler_events.append(first_normalized)
        state.next_seq += 1
        state.validator.validate_next(first_normalized)

        #: output manipulation detection on response.created.
        # If the handler directly added items to response.output instead of
        # using builder events, the output list will be non-empty — EXCEPT on a
        # recovered entry, where the handler legitimately seeds the stream from
        # context.persisted_response (§6 one-item-per-phase recovery). The
        # seeded items become the output baseline (see output_item_count below).
        created_response = cast("dict[str, Any]", first_normalized.get("response") or {})
        created_output = created_response.get("output")
        _seeded_output_count = (
            len(created_output)
            if (isinstance(created_output, list) and ctx.context is not None and ctx.context.is_recovery)
            else 0
        )
        if isinstance(created_output, list) and len(created_output) != 0 and _seeded_output_count == 0:
            _fr008a_msg = (
                f"Handler directly modified Response.Output "
                f"(found {len(created_output)} items, expected 0). "
                f"Use output builder events instead."
            )
            logger.error(
                "Output manipulation detected (response_id=%s): %s",
                ctx.response_id,
                _fr008a_msg,
            )
            state.captured_error = ValueError(_fr008a_msg)
            state.pending_terminal = await self._make_failed_event(ctx, state)
            return

        _halt, _store_events = await self._register_and_handle_storage_failure(ctx, state, first_normalized)
        for _ev in _store_events:
            yield _ev
        if _halt:
            return

        yield first_normalized

        async for _event in self._drain_remaining_events(ctx, state, handler_iterator, _seeded_output_count):
            yield _event

    async def _register_and_handle_storage_failure(
        self,
        ctx: _ExecutionContext,
        state: _PipelineState,
        first_normalized: generated_models.ResponseStreamEvent,
    ) -> "tuple[bool, list[generated_models.ResponseStreamEvent]]":
        """Register the bg/stream execution record and handle a start-time
        persistence failure (Spec 033 §3.2 extract).

        For store + (background or stream) rows, registers the execution record
        then, if the start-time persist failed, builds the storage-error winddown
        (response.created→failed for non-bg streaming, or a standalone error for
        bg+stream). Returns ``(halt, events)`` — ``halt`` True means the caller
        stops the pipeline; ``events`` are for the caller to yield. A no-op
        ``(False, [])`` for other rows.

        :param ctx: Current execution context.
        :type ctx: _ExecutionContext
        :param state: Mutable pipeline state.
        :type state: _PipelineState
        :param first_normalized: The normalised first event.
        :type first_normalized: generated_models.ResponseStreamEvent
        :returns: ``(halt, winddown_events)``.
        :rtype: tuple[bool, list[ResponseStreamEvent]]
        """
        evs: list[generated_models.ResponseStreamEvent] = []
        if not (ctx.store and (ctx.background or ctx.stream)):
            return False, evs
        # Register the execution record after the first event so events fan out
        # to the per-response stream (wire_stream subscribers in _live_stream
        # see them). Pre-Phase-2 only bg+store used this path; unified Row 3
        # stream (fg+store+stream=T) also subscribes to wire_stream.
        await self._register_bg_execution(ctx, state, first_normalized)
        if state.bg_record is None or not state.bg_record.persistence_failed:
            return False, evs
        # Phase 1 (start) persistence failure splits two ways by request shape:
        #
        # 1. Non-bg streaming (Row 3 stream=true): emit response.created →
        #    response.failed so the SSE first-event invariant (B27) holds; the
        #    failed envelope carries the storage_error code for the GET fallback.
        # 2. Bg+stream (Row 1/2 stream=true): emit a standalone error event (no
        #    response.created) — the HTTP request has not yet returned the queued
        #    response, so a response.failed terminal would promise persistence
        #    the storage layer never delivered.
        state.captured_error = state.bg_record.persistence_exception or RuntimeError("Phase 1 create failed")
        if not ctx.background:
            # Non-bg streaming: emit response.created → response.failed.
            storage_error_response = _resolve_failed_response(
                state.bg_record.response,
                ctx.response_id,
                ctx.agent_reference,
                ctx.model,
                created_at=ctx.context.created_at if ctx.context else None,
                error_code="storage_error",
                error_message=_STORAGE_ERROR_MESSAGE,
            )
            _wire_stream = await streams.get_or_create(ctx.response_id)
            await self._safe_emit(_wire_stream, first_normalized)
            evs.append(first_normalized)
            # Build, validate, and APPEND the terminal BEFORE emitting it so a
            # generator-close after yield-but-before-append can't leave only
            # response.created (which _finalize_stream Path B would regress to
            # status=in_progress).
            failed_event = {
                "type": "response.failed",
                "response": dict(storage_error_response),
            }
            failed_normalized = await self._normalize_and_append(ctx, state, failed_event)
            if state.bg_record is not None:
                state.bg_record.set_response_snapshot(storage_error_response)
                state.bg_record.status = "failed"  # type: ignore[assignment]
            await self._safe_emit(_wire_stream, failed_normalized)
            evs.append(failed_normalized)
            return True, evs
        # Bg+stream: standalone error event (no response.created).
        await self._runtime_state.try_evict(ctx.response_id)
        error_event = construct_event_model(
            {
                "type": "error",
                "message": _STORAGE_ERROR_MESSAGE,
                "param": None,
                "code": "storage_error",
                "sequence_number": 0,
            }
        )
        _err_stream = await streams.get_or_create(ctx.response_id)
        await self._safe_emit(_err_stream, error_event)
        evs.append(error_event)
        return True, evs

    async def _drain_remaining_events(
        self,
        ctx: _ExecutionContext,
        state: _PipelineState,
        handler_iterator: AsyncIterator[generated_models.ResponseStreamEvent],
        seeded_output_count: int = 0,
    ) -> AsyncIterator[generated_models.ResponseStreamEvent]:
        """Drain the post-first-event handler stream (Spec 033 §3.2 extract).

        Yields normalised non-terminal events and resolves the terminal /
        cancellation / handler-error winddown onto ``state`` (the caller emits
        the resolved terminal via ``_persist_and_resolve_terminal``).

        :param ctx: Current execution context.
        :type ctx: _ExecutionContext
        :param state: Mutable pipeline state.
        :type state: _PipelineState
        :param handler_iterator: The handler's event iterator (post first event).
        :type handler_iterator: AsyncIterator[ResponseStreamEvent]
        :param seeded_output_count: The number of output items already seeded for recovery.
        :type seeded_output_count: int
        :return: Async iterator of normalised non-terminal events.
        :rtype: AsyncIterator[ResponseStreamEvent]
        """
        # --- Remaining events ---
        # On a recovered entry the handler seeded response.created with the
        # already-persisted items (§6); they form the output-count baseline so
        # subsequent snapshot events (which carry seeded + new items) don't trip
        # the count-mismatch guard.
        output_item_count = seeded_output_count
        try:
            async for raw in _iter_with_winddown(handler_iterator, ctx.cancellation_signal):
                # Pre-check for output manipulation BEFORE validation.
                # Must inspect the raw event first so that an offending terminal
                # event (e.g. response.completed with manipulated output) is NOT
                # appended to the state machine before we emit response.failed.
                _pre_coerced = _coerce_handler_event(raw)
                _pre_type = _pre_coerced.get("type", "")
                if _pre_type == "response.output_item.added":
                    output_item_count += 1
                if _pre_type in _RESPONSE_SNAPSHOT_TYPES:
                    _pre_response = cast("dict[str, Any]", _pre_coerced.get("response") or {})
                    _pre_output = _pre_response.get("output")
                    if isinstance(_pre_output, list) and len(_pre_output) > output_item_count:
                        _fr008a_msg = (
                            f"Output item count mismatch "
                            f"({len(_pre_output)} vs {output_item_count} output_item.added events)"
                        )
                        logger.error(
                            "Output manipulation detected (response_id=%s): %s",
                            ctx.response_id,
                            _fr008a_msg,
                        )
                        state.captured_error = ValueError(_fr008a_msg)
                        state.pending_terminal = await self._make_failed_event(ctx, state)
                        return

                normalized = await self._normalize_and_append(ctx, state, raw)
                # Buffer terminal events instead of yielding — the caller will
                # attempt persistence before emitting the terminal SSE.
                if normalized.get("type") in self._TERMINAL_SSE_TYPES:
                    state.pending_terminal = normalized
                else:
                    yield normalized
        except asyncio.CancelledError:
            # S-024: Known cancellation. The terminal type depends on
            # the cancellation reason — preserve the same per-reason
            # mapping the B11 (handler-returned-without-terminal) path
            # uses so we don't diverge based on whether the handler
            # raised CancelledError vs. just returned.
            #
            # - SHUTTING_DOWN + resilient+background: leave in_progress
            #   so the next-lifetime recovery scanner re-invokes the
            #   handler. Per user-facing contract: resilient_background
            #   responses survive a server restart (orphaning the
            #   response or failing queued steers is unacceptable when
            #   the upstream task could still complete on retry).
            # - SHUTTING_DOWN + any other shape: emit response.failed
            #   (server-side shutdown is recorded as a failure, not a
            #   cancellation, per the in-process shutdown contract).
            # - CLIENT_CANCELLED / STEERED / unknown reason: emit
            #   response.cancelled (B11+B17: cancellation cannot become
            #   "failed" or "completed").
            if ctx.cancellation_signal.is_set():
                _shutdown = bool(ctx.context.shutdown.is_set()) if ctx.context else False
                if _shutdown:
                    if ctx.background and ctx.store and self._runtime_options.resilient_background:
                        return
                    if not self._has_terminal_event(state.handler_events):
                        state.pending_terminal = await self._make_failed_event(ctx, state)
                    return
                if not self._has_terminal_event(state.handler_events):
                    state.pending_terminal = await self._cancel_terminal_sse_dict(ctx, state)
                return
            # Unknown CancelledError (e.g. event-loop teardown) — re-raise.
            raise
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error(
                "Handler raised after response.created (response_id=%s)",
                ctx.response_id,
                exc_info=exc,
            )
            state.captured_error = exc
            # If we are mid-shutdown and the response is a resilient+background
            # one, the handler exception is most likely a transient symptom
            # of the SIGTERM itself (e.g. an upstream LLM SDK subprocess
            # being killed in our process group before it could fully
            # start). Convert the exception into a cooperative-cancellation
            # of the resilient task body — raise asyncio.CancelledError so
            # the @task framework leaves the task ``status="in_progress"``
            # for next-lifetime recovery instead of writing a "failed"
            # terminal that would orphan any queued steering inputs and
            # prevent the response from making forward progress on a retry.
            #
            # "Mid-shutdown" detection prefers the resilient task's
            # composing-cancellation surface (``ctx.context.shutdown``
            # set by the _resilient_orchestrator's bridge once
            # ctx.shutdown fires), but ALSO checks the server-level
            # shutdown_event (set as Hypercorn's pre-shutdown callback
            # — fires as soon as the process receives SIGTERM, before
            # TaskManager.shutdown() propagates ctx.shutdown). The
            # server-level signal closes a race where the handler
            # raises in the gap between SIGTERM reaching the process
            # group (which also kills any upstream client subprocesses)
            # and the resilient framework's cooperative-shutdown
            # propagation.
            _shutdown = bool(ctx.context.shutdown.is_set()) if ctx.context else False
            _server_shutting_down = self._shutdown_event is not None and self._shutdown_event.is_set()
            if (
                (_shutdown or _server_shutting_down)
                and ctx.background
                and ctx.store
                and self._runtime_options.resilient_background
            ):
                # Stamp the shutdown cause so the resilient body's
                # FR-005a check (which also looks at ctx.shutdown)
                # routes consistently. Shutdown does NOT fire the
                # cancellation signal — handlers observe shutdown via
                # ``context.shutdown`` and respond with
                # ``exit_for_recovery()`` or a terminal emit.
                if ctx.context is not None and not ctx.context.shutdown.is_set():
                    ctx.context.shutdown.set()
                # Signal the resilient-stream-body finally to SKIP the
                # finalize+close step. Closing the wire stream now would
                # flush a terminal marker, putting the rehydrated stream
                # in CLOSED state for the next lifetime — emits from the
                # recovered handler would silently no-op and the GET
                # ?stream=true after recovery would deliver no terminal.
                # Leaving the stream open lets the next lifetime
                # re-open the same registry entry and append its events,
                # preserving cross-attempt continuity per spec 017
                # streaming.md.
                state.leave_stream_open_for_recovery = True
                # Raise CancelledError so the @task framework treats this
                # as a cooperative cancel and leaves the task in_progress
                # (see core resilient/_manager.py CancelledError branch:
                # "cancellation is never retried" but task stays
                # in_progress for recovery scanner to pick up).
                raise asyncio.CancelledError()
            # S-035: emit response.failed when handler raises after response.created.
            if not self._has_terminal_event(state.handler_events):
                state.pending_terminal = await self._make_failed_event(ctx, state)
            return

        await self._resolve_no_terminal_winddown(ctx, state)

    async def _resolve_no_terminal_winddown(self, ctx: _ExecutionContext, state: _PipelineState) -> None:
        """Resolve the terminal when the handler finished without emitting one.

        (Spec 033 §3.2 extract) Covers B11 (handler returned without a terminal
        under a set cancellation signal — terminal type depends on the cause) and
        S-015 (handler completed normally but emitted no terminal). Sets
        ``state.pending_terminal``; never yields.

        :param ctx: Current execution context.
        :type ctx: _ExecutionContext
        :param state: Mutable pipeline state.
        :type state: _PipelineState
        """
        # B11: Handler returned without a terminal event while cancellation
        # signal is set. The terminal status depends on the cancellation cause
        # (spec 024 Phase 5 Proposal #11):
        #
        # - shutdown=True + resilient+background: leave in_progress for re-entry
        #   on restart — do NOT emit a terminal event.
        # - shutdown=True + other: emit response.failed.
        # - client_cancelled=True: emit response.cancelled (explicit cancel
        #   or non-bg POST disconnect).
        # - Neither set (steering pressure): emit response.failed (developer
        #   should have emitted terminal but didn't — framework prevents
        #   orphan responses).
        #
        # "cancelled" status is reserved exclusively for explicit /cancel API
        # calls or client disconnect on non-background create calls.
        if ctx.cancellation_signal.is_set() and not self._has_terminal_event(state.handler_events):
            _shutdown = bool(ctx.context.shutdown.is_set()) if ctx.context else False
            _client_cancelled = bool(ctx.context.client_cancelled) if ctx.context else False
            if _shutdown:
                # For resilient+background, leave response in_progress for
                # re-entry. Don't emit terminal — just return.
                if ctx.background and ctx.store and self._runtime_options.resilient_background:
                    return
                state.pending_terminal = await self._make_failed_event(ctx, state)
            elif _client_cancelled:
                state.pending_terminal = await self._cancel_terminal_sse_dict(ctx, state)
            else:
                # Steering pressure or unknown — mark failed.
                state.pending_terminal = await self._make_failed_event(ctx, state)
            return

        # S-015: handler completed normally but never emitted a terminal event.
        # NOTE: state.captured_error intentionally left None so that synchronous
        # callers return HTTP 200 with a "failed" body rather than HTTP 500.
        if not self._has_terminal_event(state.handler_events):
            state.pending_terminal = await self._make_failed_event(ctx, state)

    async def _finalize_stream(self, ctx: _ExecutionContext, state: _PipelineState) -> None:
        """Close the stream and evict for a streaming response.

        Called from the ``finally`` block of :meth:`_live_stream` AFTER the
        terminal event has already been yielded (and possibly replaced by
        ``_persist_and_resolve_terminal``).

        Responsibilities (post-streams-registry refactoring):
        - Register the execution record in runtime state (non-bg paths).
        - Close the per-response stream so replay subscribers see stream-end.
        - Eager eviction (skipped when persistence_failed is set).

        The file-backed registry persists every emit to disk automatically,
        so there is no separate "save stream events" step. On a cancelled
        background+stream response we delete the stream so SSE replay
        correctly returns 404 / 410 instead of replaying mid-stream events.

        :param ctx: Current execution context (immutable inputs).
        :type ctx: _ExecutionContext
        :param state: Mutable pipeline state for this invocation.
        :type state: _PipelineState
        """
        # --- Path A: BG with pre-existing record (normal bg+stream completion) ---
        if ctx.background and ctx.store and state.bg_record is not None:
            record = state.bg_record

            # Cancelled bg+stream responses: drop any persisted replay so
            # ``GET ?stream=true`` correctly reports "no stream available".
            if record.status == "cancelled":
                try:
                    await streams.delete(ctx.response_id)
                except Exception:  # pylint: disable=broad-exception-caught
                    logger.debug(
                        "Cancelled stream cleanup failed (response_id=%s)",
                        ctx.response_id,
                        exc_info=True,
                    )

            ctx.span.end(state.captured_error)
            # Close the stream — signals all live SSE replay subscribers that
            # the stream has ended; flushes the terminal marker to disk for
            # the file-backed backing.
            await self._safe_close(record.subject)
            # Eager eviction: free memory once terminal state is reached.
            # Skip eviction when persistence failed — the in-memory record is
            # the only remaining source of truth for GET.
            if record.is_terminal and not record.persistence_failed:
                await self._runtime_state.try_evict(ctx.response_id)
            return

        # --- Path B: No pre-existing record ---
        # Covers non-background streams and background streams where no record
        # was created (empty handler fallback, pre-creation errors, first-event
        # contract violations).

        # Non-bg streaming interrupted mid-stream. The interrupt is either a
        # client disconnect (``client_cancelled=True``, treated as a
        # cancellation — we persist a cancelled terminal so a later GET
        # sees ``cancelled``, NOT a 404), or a server shutdown
        # (``shutdown.set()``, deferred to the next-lifetime recovery
        # scanner — we leave the response un-persisted in THIS lifetime
        # so the recovery scanner's ``_persist_crash_failed`` writes the
        # canonical terminal).
        if not ctx.background and state.stream_interrupted:
            _shutdown = bool(ctx.context.shutdown.is_set()) if ctx.context else False
            if _shutdown:
                # Defer to next-lifetime recovery scanner.
                ctx.span.end(state.captured_error)
                return
            # Client disconnect (or unknown cancellation): make sure we have
            # a terminal event so the persistence path can extract a
            # snapshot. If the cancel terminal wasn't already buffered
            # (e.g. cancellation_signal didn't reach the handler before its
            # task was torn down), build one now.
            if state.pending_terminal is None and not self._has_terminal_event(state.handler_events):
                try:
                    state.pending_terminal = await self._cancel_terminal_sse_dict(ctx, state)
                except Exception:  # pylint: disable=broad-exception-caught
                    logger.debug(
                        "Failed to synthesise cancel terminal on interrupted " + "foreground stream (response_id=%s)",
                        ctx.response_id,
                        exc_info=True,
                    )
            # Persist the cancelled response to the resilient provider so a
            # later GET retrieves status=cancelled instead of 404.
            # _persist_and_resolve_terminal handles create_response +
            # update_response and stamps the failure on the record if
            # persistence itself fails. Without this call the response
            # only lives in runtime_state and is lost on eager eviction.
            if ctx.store and state.pending_terminal is not None:
                record = state.bg_record or _make_ephemeral_record(ctx, state)
                try:
                    await self._persist_and_resolve_terminal(ctx, state, record)
                except Exception:  # pylint: disable=broad-exception-caught
                    logger.debug(
                        "Persistence of interrupted foreground stream failed "
                        "(response_id=%s) — falling through to in-memory-only "
                        "runtime_state record",
                        ctx.response_id,
                        exc_info=True,
                    )
            # Fall through to the normal Path B persistence below — the
            # cancelled snapshot will be written to runtime_state and
            # (for store=True) becomes retrievable via GET.

        events = (
            state.handler_events
            if state.handler_events
            else _build_events(
                ctx.response_id,
                include_progress=True,
                agent_reference=ctx.agent_reference,
                model=ctx.model,
            )
        )
        response_payload = _extract_response_snapshot_from_events(
            events,
            response_id=ctx.response_id,
            agent_reference=ctx.agent_reference,
            model=ctx.model,
            agent_session_id=ctx.agent_session_id,
            conversation_id=ctx.conversation_id,
        )
        # Stamp background so the provider fallback can enforce B1 checks
        # after eager eviction removes the in-memory record.
        response_payload["background"] = ctx.background
        resolved_status = response_payload.get("status")
        final_status: ResponseStatus = (
            cast(ResponseStatus, resolved_status) if isinstance(resolved_status, str) else "completed"
        )

        # Always register in runtime state so cancel/GET return correct status codes.
        # For background+store streams we close the per-response stream so
        # GET ?stream=true can replay the retained events after eager
        # eviction. Events were emitted live to the stream in the
        # fallback loop in ``_process_handler_events``; here we just bind
        # the stream onto the record and close it. Non-background streams
        # have ``replay_enabled=False`` — GET ?stream=true returns 400
        # for them, so no stream is needed.
        replay_subject: EventStream | None = None
        if ctx.store and ctx.background:
            replay_subject = await streams.get_or_create(ctx.response_id)
            await self._safe_close(replay_subject)

        execution = ResponseExecution(
            response_id=ctx.response_id,
            mode_flags=ResponseModeFlags(stream=True, store=ctx.store, background=ctx.background),
            status=final_status,
            subject=replay_subject,
            input_items=deepcopy(ctx.input_items),
            previous_response_id=ctx.previous_response_id,
            cancel_signal=ctx.cancellation_signal if ctx.background else None,
            agent_session_id=ctx.agent_session_id,
            conversation_id=ctx.conversation_id,
            user_id_key=ctx.user_id,
        )
        execution.set_response_snapshot(cast(generated_models.ResponseObject, response_payload))
        # Copy persistence_failed from the ephemeral record if one was used
        if state.bg_record is not None:
            execution.persistence_failed = state.bg_record.persistence_failed
            execution.persistence_exception = state.bg_record.persistence_exception
        await self._runtime_state.add(execution)

        ctx.span.end(state.captured_error)

        # Eager eviction: free memory once terminal state is reached (or store=False).
        # Skip eviction when persistence failed — the in-memory record is the
        # only remaining source of truth for GET.
        if execution.is_terminal and not execution.persistence_failed:
            await self._runtime_state.try_evict(ctx.response_id)

    # ------------------------------------------------------------------
    # Public execution methods
    # ------------------------------------------------------------------

    def run_stream(self, ctx: _ExecutionContext) -> AsyncIterator[str]:
        """Return an async iterator of SSE-encoded strings for a streaming request.

        The iterator handles:

        - Pre-creation errors (B8 contract: standalone ``error`` SSE event).
        - Empty handler (fallback synthesised events).
        - Mid-stream handler errors (``response.failed`` SSE event, S-035).
        - Cancellation terminal events.
        - Optional SSE keep-alive comments.

        :param ctx: Current execution context.
        :type ctx: _ExecutionContext
        :return: Async iterator of SSE strings.
        :rtype: AsyncIterator[str]
        """
        return self._live_stream(ctx)

    async def _relay_resilient_stream(self, wire_stream: EventStream) -> AsyncIterator[str]:
        """Relay a resilient response's per-response wire stream to the client.

        Subscribes to ``wire_stream`` and yields each event as an encoded SSE
        chunk. When SSE keep-alive is enabled, periodic keep-alive comments are
        interleaved (via a shared queue) so the connection stays warm while the
        resilient body runs.

        This relay is connection-scoped only: the resilient body executes in its
        own task, so a client / proxy disconnect that stops this relay does NOT
        cancel the resilient execution.

        :param wire_stream: The per-response stream the resilient body emits to.
        :type wire_stream: EventStream
        :returns: Async iterator of encoded SSE strings.
        :rtype: AsyncIterator[str]
        """
        if not self._runtime_options.sse_keep_alive_enabled:
            try:
                async for event in wire_stream.subscribe(after=None):
                    yield encode_sse_any_event(event)
            except Exception:  # pylint: disable=broad-exception-caught
                pass  # wire dropped; resilient body continues
            return

        sentinel = object()
        queue: asyncio.Queue[object] = asyncio.Queue()

        async def _pump_events() -> None:
            try:
                async for event in wire_stream.subscribe(after=None):
                    await queue.put(encode_sse_any_event(event))
            except Exception:  # pylint: disable=broad-exception-caught
                pass  # wire dropped; resilient body continues
            finally:
                await queue.put(sentinel)

        async def _pump_keep_alive(interval: int) -> None:
            try:
                while True:
                    await asyncio.sleep(interval)
                    await queue.put(encode_keep_alive_comment())
            except asyncio.CancelledError:
                return

        events_task = asyncio.create_task(_pump_events())
        keep_alive_task = asyncio.create_task(
            _pump_keep_alive(self._runtime_options.sse_keep_alive_interval_seconds)  # type: ignore[arg-type]
        )
        try:
            while True:
                item = await queue.get()
                if item is sentinel:
                    break
                yield item  # type: ignore[misc]
        finally:
            # Connection-scoped relay — stopping it does not affect the resilient
            # body, which runs in its own task.
            keep_alive_task.cancel()
            events_task.cancel()

    async def _live_stream(self, ctx: _ExecutionContext) -> AsyncIterator[str]:
        """Drive the SSE streaming pipeline using the shared event pipeline.

        Delegates all event processing (first-event handling, normalisation,
        bg record registration, S-035 / S-015 / B11 terminal events) to
        :meth:`_process_handler_events`.  This method only encodes each event
        dict to SSE and handles keep-alive comment injection.

        :param ctx: Current execution context.
        :type ctx: _ExecutionContext
        :returns: Async iterator of SSE-encoded strings.
        :rtype: AsyncIterator[str]
        """
        new_stream_counter()
        state = _PipelineState()
        _handler_name = getattr(self._create_fn, "__qualname__", None) or getattr(
            self._create_fn, "__name__", "unknown"
        )
        logger.info("Invoking handler %s for response %s", _handler_name, ctx.response_id)

        # (Spec 024 Phase 2) Bookkeeping pattern removed. The stream-path
        # unification follows the same shape as the existing Row 1
        # (resilient_bg+bg+store+stream=T) branch below — handler runs inside
        # the resilient task body via _start_resilient_background; the live wire
        # iterator subscribes to the per-response stream. The pre-existing
        # bookkeeping_record + bookkeeping_active + _complete_bookkeeping_task
        # mechanics are deleted. Disposition is selected per row:
        #   - resilient_bg=True + bg + store    → re-invoke   (Row 1 stream=T)
        #   - resilient_bg=False + bg + store   → mark-failed (Row 2 stream=T)
        #   - fg + store                      → mark-failed (Row 3 stream=T)
        # The downstream branches read ``_unified_disposition`` instead of
        # deriving the disposition independently.
        _unified_disposition = decide_disposition(
            background=ctx.background,
            resilient_background=self._runtime_options.resilient_background,
            store=ctx.store,
        )

        handler_iterator = self._create_fn(ctx.parsed, ctx.context, ctx.cancellation_signal)

        # Helper: route to the right finalize method based on the request semantics
        # (bg+store → bg_stream path; everything else → non_bg_stream path).
        # NOTE: state.bg_record may be None for bg+stream when the handler yields no
        # events (fallback path in _process_handler_events); _finalize_bg_stream
        # handles that case by creating the record itself.
        async def _finalize() -> None:
            await self._finalize_stream(ctx, state)

        # Stored responses (background / resilient) ALWAYS run via the resilient
        # task + per-response wire stream, regardless of SSE keep-alive. The
        # resilient body runs in its own task, independent of the client
        # connection, so the response survives a client / proxy disconnect and
        # stays recoverable.
        #
        # (Spec 024 Phase 2) Unified stream-path for ALL ``store=True`` streams:
        # Row 1 (resilient_bg+bg+store), Row 2 (non-resilient_bg+bg+store) and
        # Row 3 (fg+store) all run the handler inside the resilient task body and
        # subscribe the wire iterator to the per-response stream via the
        # registry. Disposition is selected per row (re-invoke for Row 1,
        # mark-failed for Row 2/3). ``_resilient_stream_fallback`` is the
        # in-process fallback if the resilient start cannot proceed (e.g. a test
        # client without a TaskManager).
        if ctx.store:
            # Bind the per-response stream up front. The registry returns the
            # same instance for the same id, so the resilient body's
            # ``_register_bg_execution`` gets back this exact stream — every
            # emit fans out to the wire iterator below.
            wire_stream = await streams.get_or_create(ctx.response_id)

            async def _resilient_stream_fallback() -> None:
                # In-process fallback if ``_start_resilient_background`` cannot
                # start a resilient task. Runs the same ``_process_handler_events``
                # pipeline as the resilient body so events still reach the
                # per-response wire stream this connection subscribes to.
                try:
                    async for _event in self._process_handler_events(ctx, state, handler_iterator):
                        pass
                    if state.pending_terminal is not None:
                        r = state.bg_record or _make_ephemeral_record(ctx, state)
                        await self._persist_and_resolve_terminal(ctx, state, r)
                finally:
                    await self._finalize_stream(ctx, state)
                    await self._safe_close(wire_stream)

            # Minimal record only for ``_start_resilient_background``'s parameter
            # shape. It is NOT added to runtime_state — the resilient body (or the
            # fallback) creates the canonical record via ``_register_bg_execution``.
            start_record = ResponseExecution(
                response_id=ctx.response_id,
                mode_flags=ResponseModeFlags(stream=True, store=True, background=ctx.background),
                status="in_progress",
                input_items=deepcopy(ctx.input_items),
                previous_response_id=ctx.previous_response_id,
                cancel_signal=ctx.cancellation_signal,
                response_context=ctx.context,
                agent_session_id=ctx.agent_session_id,
                conversation_id=ctx.conversation_id,
                user_id_key=ctx.user_id,
                initial_model=ctx.model,
                initial_agent_reference=ctx.agent_reference,
            )
            start_record.subject = wire_stream

            try:
                await self._start_resilient_background(
                    ctx,
                    start_record,
                    _resilient_stream_fallback,
                    disposition=_unified_disposition,
                )
            except Exception as exc:  # pylint: disable=broad-exception-caught
                if not getattr(exc, PLATFORM_ERROR_TAG, False):
                    # 409 conflicts (TaskConflictError / LastInputIdPreconditionFailed)
                    # and any non-platform error propagate unchanged.
                    raise
                # Resilient task start failed. HTTP headers are already sent
                # (200) for a streaming response, so an HTTP error-source header
                # is impossible; surface the failure the streaming-native way —
                # a standalone ``error`` SSE event (the same B8 pre-creation
                # contract used for every other streaming creation failure) —
                # then close the wire stream. The platform error is already
                # logged + tagged by ``_start_resilient_background``.
                yield encode_sse_any_event(await self._emit_standalone_error(ctx, code="server_error"))
                await self._safe_close(wire_stream)
                return

            # Relay the resilient wire stream to this client, interleaving
            # keep-alive comments when enabled. The resilient body runs in its own
            # task — dropping this client never cancels it.
            async for chunk in self._relay_resilient_stream(wire_stream):
                yield chunk
            return

        # --- Ephemeral (non-stored) responses: no resilient task ---
        if not self._runtime_options.sse_keep_alive_enabled:
            # Row 4 stream — no store, no resilient task. Inline pipeline.
            _stream_completed = False
            try:
                async for event in self._process_handler_events(ctx, state, handler_iterator):
                    yield encode_sse_any_event(event)
                _stream_completed = True
                # Persist-then-yield: resolve the buffered terminal event.
                if state.pending_terminal is not None:
                    record = state.bg_record or _make_ephemeral_record(ctx, state)
                    resolved = await self._persist_and_resolve_terminal(ctx, state, record)
                    yield encode_sse_any_event(resolved)
            finally:
                # If the stream did not complete naturally (e.g. client
                # disconnect -> CancelledError), mark it interrupted.
                if not _stream_completed:
                    state.stream_interrupted = True
                await _finalize()
            return

        # --- Keep-alive path: merge handler events with periodic keep-alive comments ---
        async for _chunk in self._live_stream_keep_alive(ctx, state, handler_iterator):
            yield _chunk

    async def _live_stream_keep_alive(
        self,
        ctx: _ExecutionContext,
        state: _PipelineState,
        handler_iterator: AsyncIterator[generated_models.ResponseStreamEvent],
    ) -> AsyncIterator[str]:
        """Ephemeral streaming with SSE keep-alive comments (Spec 033 §3.2 extract).

        Merges handler events with periodic keep-alive comments via a shared
        queue so comments are sent even while the handler is idle. Used by the
        non-stored streaming path when keep-alive is enabled.

        :param ctx: Current execution context.
        :type ctx: _ExecutionContext
        :param state: Mutable pipeline state.
        :type state: _PipelineState
        :param handler_iterator: The handler's event iterator.
        :type handler_iterator: AsyncIterator[ResponseStreamEvent]
        :return: Async iterator of SSE-encoded strings.
        :rtype: AsyncIterator[str]
        """
        # via a shared asyncio.Queue so comments are sent even while the handler is idle.
        _SENTINEL = object()
        merge_queue: asyncio.Queue[str | object] = asyncio.Queue()

        async def _handler_producer() -> None:
            try:
                async for event in self._process_handler_events(ctx, state, handler_iterator):
                    await merge_queue.put(encode_sse_any_event(event))
                # Persist-then-yield: resolve the buffered terminal event
                if state.pending_terminal is not None:
                    record = state.bg_record or _make_ephemeral_record(ctx, state)
                    resolved = await self._persist_and_resolve_terminal(ctx, state, record)
                    await merge_queue.put(encode_sse_any_event(resolved))
            finally:
                await merge_queue.put(_SENTINEL)

        async def _keep_alive_producer(interval: int) -> None:
            try:
                while True:
                    await asyncio.sleep(interval)
                    await merge_queue.put(encode_keep_alive_comment())
            except asyncio.CancelledError:
                return

        handler_task = asyncio.create_task(_handler_producer())
        keep_alive_task = asyncio.create_task(
            _keep_alive_producer(self._runtime_options.sse_keep_alive_interval_seconds)  # type: ignore[arg-type]
        )

        _ka_stream_completed = False
        try:
            while True:
                item = await merge_queue.get()
                if item is _SENTINEL:
                    _ka_stream_completed = True
                    break
                yield item  # type: ignore[misc]
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error(
                "Stream consumer failed (response_id=%s)",
                ctx.response_id,
                exc_info=exc,
            )
            state.captured_error = exc
        finally:
            if not _ka_stream_completed:
                state.stream_interrupted = True
            keep_alive_task.cancel()
            try:
                await keep_alive_task
            except asyncio.CancelledError:
                pass
            # Ensure the handler task has finished before finalising
            if not handler_task.done():
                handler_task.cancel()
                try:
                    await handler_task
                except asyncio.CancelledError:
                    pass
            await self._finalize_stream(ctx, state)

    async def _await_sync_resilient_terminal(self, ctx: _ExecutionContext, record: ResponseExecution) -> None:
        """Block until the sync resilient task / fallback execution reaches terminal.

        (Spec 033 §3.2 extract) Awaits ``record.resilient_task_run.result()`` (or
        the asyncio fallback ``record.execution_task``). On HTTP client disconnect
        (``CancelledError``) cancels the underlying task body, evicts the record
        so a later GET returns 404 (B17), ends the span, and re-raises.

        :param ctx: Current execution context.
        :type ctx: _ExecutionContext
        :param record: The sync execution record.
        :type record: ResponseExecution
        """
        task_run = getattr(record, "resilient_task_run", None)
        execution_task = getattr(record, "execution_task", None)
        try:
            if task_run is not None:
                try:
                    await task_run.result()
                except asyncio.CancelledError:  # pylint: disable=try-except-raise
                    # Cancellation must propagate untouched — never fold it into
                    # the task-failure handling below (CancelledError is a
                    # BaseException, so this guard is belt-and-suspenders).
                    raise
                except Exception as task_exc:  # pylint: disable=broad-exception-caught
                    # Resilient task body raised. If the handler had a pre-creation
                    # error (B8) → re-raise as _HandlerError below. Otherwise
                    # (post-creation error / persistence error) the record already
                    # reflects the failure state and the snapshot below carries
                    # the response.failed details.
                    if not getattr(record, "response_failed_before_events", False):
                        logger.warning(
                            "Resilient task for sync response %s raised: %s",
                            ctx.response_id,
                            task_exc,
                            exc_info=True,
                        )
            elif execution_task is not None:
                try:
                    await execution_task
                except asyncio.CancelledError:  # pylint: disable=try-except-raise
                    # Cancellation must propagate untouched (see above).
                    raise
                except Exception as task_exc:  # pylint: disable=broad-exception-caught
                    if not getattr(record, "response_failed_before_events", False):
                        logger.warning(
                            "Fallback execution_task for sync response %s raised: %s",
                            ctx.response_id,
                            task_exc,
                            exc_info=True,
                        )
        except asyncio.CancelledError:
            # HTTP client disconnected — per B17, the non-bg sync response is
            # discarded. Cancel the underlying task body (best-effort) so it
            # doesn't continue running after the HTTP request is gone. Remove
            # the record from runtime_state so subsequent GETs return 404.
            logger.info(
                "Non-bg sync response %s discarded due to HTTP client disconnect (B17)",
                ctx.response_id,
            )
            if task_run is not None:
                try:
                    await task_run.cancel()
                except Exception:  # pylint: disable=broad-exception-caught
                    pass
            if execution_task is not None and not execution_task.done():
                execution_task.cancel()
            # Try to remove the record so GET returns 404. Best-effort; the
            # record may already be evicted.
            try:
                await self._runtime_state.try_evict(ctx.response_id)
            except Exception:  # pylint: disable=broad-exception-caught
                pass
            ctx.span.end(None)
            raise

    async def _resolve_sync_client_disconnect(
        self, ctx: _ExecutionContext, record: ResponseExecution, *, is_shutdown: bool
    ) -> None:
        """Handle a sync response's client disconnect (B17/B11/B14).

        (Spec 033 §3.2 extract) When the cancellation signal is set due to a
        client disconnect (NOT a server shutdown) and the record was not
        explicitly cancelled: for ``store=true`` persist a ``cancelled`` terminal
        (GET 200 + cancelled); for ``store=false`` discard the record (GET 404).
        Either way raise ``CancelledError`` so the endpoint stops emitting a
        snapshot to the gone client. A no-op otherwise.

        :param ctx: Current execution context.
        :type ctx: _ExecutionContext
        :param record: The sync execution record.
        :type record: ResponseExecution
        :keyword is_shutdown: True when ``context.shutdown`` is set (server
            shutdown — preserve for recovery instead of discarding).
        :paramtype is_shutdown: bool
        """
        if not (ctx.cancellation_signal.is_set() and not record.cancel_requested and not is_shutdown):
            return
        if ctx.store:
            # B17 + B11: persist cancelled terminal so GET 200 + cancelled.
            logger.info(
                "Non-bg sync response %s cancelled on client disconnect (B17, store=true → cancelled retrievable)",
                ctx.response_id,
            )
            cancelled_response = _resolve_cancelled_response(
                record.response,
                ctx.response_id,
                ctx.agent_reference,
                ctx.model,
                created_at=ctx.context.created_at if ctx.context else None,
            )
            record.set_response_snapshot(cancelled_response)
            # Force terminal status — record may already be in a
            # non-terminal state that doesn't allow normal transitions.
            record.status = "cancelled"  # type: ignore[assignment]
            # Persist to the response store so the in-memory record
            # can be evicted later without losing the cancelled snapshot.
            try:
                await self._provider.update_response(
                    cancelled_response,
                    context=ctx.context.platform_context if ctx.context else None,
                )
            except Exception:  # pylint: disable=broad-exception-caught
                logger.debug(
                    "Provider cancelled-update failed on B17 disconnect "
                    "(response_id=%s) — leaving in-memory record as "
                    "authoritative source",
                    ctx.response_id,
                    exc_info=True,
                )
            ctx.span.end(None)
            # Raise CancelledError so the endpoint stops emitting a
            # snapshot to the (already-gone) client; the persisted
            # cancelled terminal is the GET-visible source of truth.
            raise asyncio.CancelledError()
        # B14 + B17 store=false: discard the in-flight record so
        # GET returns 404 (no persistence to honour).
        logger.info(
            "Non-bg sync response %s discarded on client disconnect (B17, store=false → GET 404)",
            ctx.response_id,
        )
        try:
            await self._runtime_state.try_evict(ctx.response_id)
        except Exception:  # pylint: disable=broad-exception-caught
            pass
        ctx.span.end(None)
        raise asyncio.CancelledError()

    async def run_sync(self, ctx: _ExecutionContext) -> dict[str, Any]:
        """Execute a synchronous (non-stream, non-background) create-response request.

        Delegates event processing to :meth:`_process_handler_events`, which
        handles all error paths.  This method collects the accumulated events,
        builds the response snapshot, optionally persists the record, closes
        the span, and returns the snapshot dict.

        Raises :class:`_HandlerError` if the handler raises (B8 or S-035) so
        the caller can map it to an HTTP 500 response.  S-015 (handler
        completed without emitting a terminal event) does *not* raise; instead
        the snapshot status is ``"failed"`` and HTTP 200 is returned.

        (Spec 024 Phase 2) For ``store=True`` (Row 3) the handler runs inside
        the resilient task body. The HTTP request awaits the task's terminal
        via ``await task_run.result()``. B8 (pre-creation error) is preserved
        by checking ``record.response_failed_before_events`` after the task
        completes — when True, an :class:`_HandlerError` is raised so the
        endpoint maps to HTTP 500. For ``store=False`` (no resilient task
        possible), the inline pipeline is used as before.

        :param ctx: Current execution context.
        :type ctx: _ExecutionContext
        :return: Response snapshot dictionary.
        :rtype: dict[str, Any]
        :raises _HandlerError: If the handler raises during iteration.
        """
        state = _PipelineState()
        _handler_name = getattr(self._create_fn, "__qualname__", None) or getattr(
            self._create_fn, "__name__", "unknown"
        )
        logger.info("Invoking handler %s for response %s", _handler_name, ctx.response_id)

        if not ctx.store:
            # No store ⇒ no resilient task possible. Run handler inline; the
            # response is ephemeral (not retrievable via GET).
            return await self._run_sync_inner(ctx, state)

        # (Spec 024 Phase 2 — bookkeeping unification) Row 3 unified path:
        # handler runs inside the resilient task body, HTTP request awaits the
        # task's terminal via ``await task_run.result()``. Crash recovery
        # uses the same mark-failed disposition as before — the next-lifetime
        # recovery scanner reclaims tasks that crashed mid-execution.
        record = ResponseExecution(
            response_id=ctx.response_id,
            mode_flags=ResponseModeFlags(stream=False, store=True, background=False),
            status="in_progress",
            input_items=deepcopy(ctx.input_items),
            previous_response_id=ctx.previous_response_id,
            response_context=ctx.context,
            cancel_signal=ctx.cancellation_signal,
            agent_session_id=ctx.agent_session_id,
            conversation_id=ctx.conversation_id,
            user_id_key=ctx.user_id,
            initial_model=ctx.model,
            initial_agent_reference=ctx.agent_reference,
        )
        await self._runtime_state.add(record)

        async def _runner() -> None:
            """Fallback runner if _start_resilient_background's resilient start fails.

            Runs the same handler-execution pipeline as the resilient body so
            in-test or test-client environments without a TaskManager still
            execute the handler.
            """
            await _run_background_non_stream(
                create_fn=self._create_fn,
                parsed=ctx.parsed,
                context=ctx.context,  # type: ignore[arg-type]
                cancellation_signal=ctx.cancellation_signal,
                record=record,
                response_id=ctx.response_id,
                agent_reference=ctx.agent_reference,
                model=ctx.model,
                provider=self._provider,
                store=ctx.store,
                agent_session_id=ctx.agent_session_id,
                conversation_id=ctx.conversation_id,
                history_limit=self._runtime_options.default_fetch_history_count,
                runtime_state=self._runtime_state,
                runtime_options=self._runtime_options,
            )

        await self._start_resilient_background(
            ctx,
            record,
            _runner,
            disposition=decide_disposition(
                background=ctx.background,
                resilient_background=self._runtime_options.resilient_background,
                store=ctx.store,
            ),
        )

        # Block until the handler emits its terminal:
        #   - If resilient start succeeded, ``record.resilient_task_run`` is set;
        #     await its ``.result()`` to block on the task body.
        #   - If resilient start fell back to asyncio (e.g. TestClient without
        #     TaskManager), ``record.execution_task`` is set; await it.
        # On HTTP client disconnect (CancelledError propagates here), cancel
        # the underlying resilient task / execution task and treat the response
        # as discarded — per B17, non-bg sync responses are not retrievable
        # after disconnect. The record is removed from runtime_state and the
        # store-side persistence is skipped (best-effort).
        await self._await_sync_resilient_terminal(ctx, record)

        # B8 detection: if the handler failed BEFORE emitting any terminal
        # event, surface as _HandlerError → HTTP 500. Today's run_sync_inner
        # has the same check via state.captured_error + _has_terminal_event;
        # the unified path uses record.response_failed_before_events which
        # is set by _run_background_non_stream's S-035 / B8 branches.
        if getattr(record, "response_failed_before_events", False):
            persistence_exc = getattr(record, "persistence_exception", None)
            if persistence_exc is None:
                # Fabricate a generic handler-failure exception so the endpoint
                # gets a non-None inner. The real exception was logged
                # inside _run_background_non_stream.
                persistence_exc = RuntimeError("Handler failed before emitting response.created")
            ctx.span.end(persistence_exc)
            raise _HandlerError(persistence_exc) from persistence_exc

        # B17 (per foundry behaviour-contract): non-bg + disconnect →
        # status="cancelled". If store=true, the cancelled response is
        # retrievable (GET 200 + status=cancelled). If store=false,
        # the cancelled response is not retrievable (GET 404 per Rule B14).
        #
        # IMPORTANT: distinguish "client disconnect" from "server shutdown".
        # During graceful shutdown the task body's ``exit_for_recovery``
        # leaves the resilient task in_progress so the next-lifetime recovery
        # scanner can mark the response failed. If we persisted/discarded
        # here on shutdown the recovery path would have nothing to find.
        # The ``context.shutdown`` event distinguishes the two: set means
        # server shutdown (preserve for recovery); not set means client
        # disconnect / explicit cancel (handled per B17 + B11).
        _is_shutdown = bool(ctx.context.shutdown.is_set()) if ctx.context else False
        await self._resolve_sync_client_disconnect(ctx, record, is_shutdown=_is_shutdown)

        # On graceful shutdown: leave the response in_progress so next-lifetime
        # recovery can mark it failed. The HTTP request may still be in-flight
        # (the client hasn't disconnected yet); raise CancelledError so the
        # HTTP layer responds with a server-shutdown signal rather than a
        # snapshot.
        if _is_shutdown:
            logger.info(
                "Non-bg sync response %s left in_progress for recovery (server shutdown)",
                ctx.response_id,
            )
            ctx.span.end(None)
            raise asyncio.CancelledError()

        # Persistence-failure detection: if `create_response` raised (B8 / §3.1
        # Default mode), surface as _HandlerError → HTTP 500. Pre-Phase-2
        # `_run_sync_inner` raised the same way; this preserves the behaviour.
        if getattr(record, "persistence_failed", False):
            persist_exc = getattr(record, "persistence_exception", None) or RuntimeError("Persistence failed")
            ctx.span.end(persist_exc)
            raise _HandlerError(persist_exc) from persist_exc

        # S-015: handler completed without emitting a terminal event. The
        # unified path uses ``_run_background_non_stream`` which does NOT
        # synthesise a failed terminal for empty/no-terminal sequences (only
        # the streaming pipeline's ``_process_handler_events`` does). For
        # foreground non-stream Row 3, synthesise here so the snapshot
        # carries status=failed (matches pre-Phase-2 behaviour). Sync
        # callers receive HTTP 200 with failed body per S-015 contract.
        if record.status == "in_progress":
            failed_response = _resolve_failed_response(
                record.response,
                ctx.response_id,
                ctx.agent_reference,
                ctx.model,
                created_at=ctx.context.created_at if ctx.context else None,
            )
            record.set_response_snapshot(failed_response)
            try:
                record.transition_to("failed")
            except Exception:  # pylint: disable=broad-exception-caught
                # If the state machine rejects the transition (already terminal),
                # leave the status as-is — the snapshot is already updated.
                pass

        # Read snapshot from the now-completed record. The resilient task body
        # persisted to the store; the record reflects the final state.
        ctx.span.end(None)
        return _RuntimeState.to_snapshot(record)

    async def _run_sync_inner(self, ctx: _ExecutionContext, state: _PipelineState) -> dict[str, Any]:
        """Inner body of :meth:`run_sync` — extracted so the bookkeeping
        task can be signalled in a ``try/finally`` wrapper in the caller.

        :param ctx: Current execution context.
        :type ctx: _ExecutionContext
        :param state: Pipeline state (populated by handler events).
        :type state: _PipelineState
        :return: Response snapshot dictionary.
        :rtype: dict[str, Any]
        """
        handler_iterator = self._create_fn(ctx.parsed, ctx.context, ctx.cancellation_signal)
        # _process_handler_events handles all error paths (B8, S-035, S-015, B11).
        # run_sync only needs to exhaust the generator for state.handler_events side-effects.
        async for _ in self._process_handler_events(ctx, state, handler_iterator):
            pass

        if state.captured_error is not None:
            # Only raise _HandlerError for pre-creation errors (B8) where no
            # terminal lifecycle event has been emitted.  Post-creation errors
            # (S-035,) emit response.failed and should complete as
            # HTTP 200 with failed status — not an HTTP 500.
            if not self._has_terminal_event(state.handler_events):
                ctx.span.end(state.captured_error)
                raise _HandlerError(state.captured_error) from state.captured_error

        events = (
            state.handler_events
            if state.handler_events
            else _build_events(
                ctx.response_id,
                include_progress=True,
                agent_reference=ctx.agent_reference,
                model=ctx.model,
            )
        )
        response_payload = _extract_response_snapshot_from_events(
            events,
            response_id=ctx.response_id,
            agent_reference=ctx.agent_reference,
            model=ctx.model,
            remove_sequence_number=True,
            agent_session_id=ctx.agent_session_id,
            conversation_id=ctx.conversation_id,
        )
        # Stamp background so the provider fallback can enforce B1 checks
        # after eager eviction removes the in-memory record.
        response_payload["background"] = ctx.background

        resolved_status = response_payload.get("status")
        status = cast(ResponseStatus, resolved_status) if isinstance(resolved_status, str) else "completed"

        record = ResponseExecution(
            response_id=ctx.response_id,
            mode_flags=ResponseModeFlags(stream=False, store=ctx.store, background=False),
            status=status,
            input_items=deepcopy(ctx.input_items),
            previous_response_id=ctx.previous_response_id,
            response_context=ctx.context,
            agent_session_id=ctx.agent_session_id,
            conversation_id=ctx.conversation_id,
            user_id_key=ctx.user_id,
        )
        record.set_response_snapshot(cast(generated_models.ResponseObject, response_payload))

        # Always register in runtime state so that cancel/GET can find the record
        # and return the correct status code (e.g., 400 for non-bg cancel).
        # Always register so cancel/GET can find this record.
        await self._runtime_state.add(record)

        if ctx.store:
            # Persist via provider (non-bg sync: single create at terminal state).
            # §3.1: Persistence failure replaces the response body with storage_error.
            try:
                _context = ctx.context.platform_context if ctx.context else None
                _response_obj = cast(generated_models.ResponseObject, response_payload)
                _history_ids = (
                    await self._provider.get_history_item_ids(
                        ctx.previous_response_id,
                        None,
                        self._runtime_options.default_fetch_history_count,
                        context=_context,
                    )
                    if ctx.previous_response_id
                    else None
                )
                _resolved_items = await _resolve_input_items_for_persistence(ctx.context, ctx.input_items)
                await self._provider.create_response(
                    _response_obj,
                    _resolved_items,
                    _history_ids,
                    context=_context,
                )
                state.provider_created = True
                # Bookkeeping signal is fired in run_sync's finally block
                # — no need to repeat here.
            except Exception as persist_exc:  # pylint: disable=broad-exception-caught
                logger.error(
                    "Persistence failed in sync path (response_id=%s): %s",
                    ctx.response_id,
                    persist_exc,
                    exc_info=True,
                )
                record.persistence_failed = True
                record.persistence_exception = persist_exc
                # Replace snapshot with storage_error response.failed
                storage_error_response = _resolve_failed_response(
                    record.response,
                    ctx.response_id,
                    ctx.agent_reference,
                    ctx.model,
                    created_at=ctx.context.created_at if ctx.context else None,
                    error_code="storage_error",
                    error_message=_STORAGE_ERROR_MESSAGE,
                )
                record.set_response_snapshot(storage_error_response)
                record.status = "failed"  # type: ignore[assignment]

        # Eager eviction: free memory once terminal state is persisted (or store=False).
        # Skip eviction when persistence failed — sync failures are handled below
        # where we evict before raising HTTP 500.
        if record.is_terminal and not record.persistence_failed:
            await self._runtime_state.try_evict(ctx.response_id)

        # §3.1: For sync mode, persistence failure surfaces as HTTP 500.
        # The client never receives a response_id on 500, so evict the record
        # to avoid unbounded memory growth during storage outages.
        if record.persistence_failed:
            await self._runtime_state.try_evict(ctx.response_id)
            ctx.span.end(record.persistence_exception)
            raise _HandlerError(
                record.persistence_exception or RuntimeError("Persistence failed")
            ) from record.persistence_exception

        ctx.span.end(None)
        return _RuntimeState.to_snapshot(record)

    async def run_background(self, ctx: _ExecutionContext) -> dict[str, Any]:
        """Handle a background (non-stream) create-response request.

        Launches the handler as an asyncio task, waits for the handler to
        emit ``response.created``, then returns the in_progress snapshot.
        The POST blocks until the handler's first event is processed
        (the ``ResponseCreatedSignal`` pattern).

        When ``resilient_background=True`` in server options, execution is
        wrapped in the resilient task primitive for crash recovery.

        :param ctx: Current execution context.
        :type ctx: _ExecutionContext
        :return: Response snapshot dictionary (status: in_progress).
        :rtype: dict[str, Any]
        :raises _HandlerError: If the handler fails before emitting ``response.created``.
        """
        record = ResponseExecution(
            response_id=ctx.response_id,
            mode_flags=ResponseModeFlags(stream=False, store=ctx.store, background=True),
            status="in_progress",
            input_items=deepcopy(ctx.input_items),
            previous_response_id=ctx.previous_response_id,
            response_context=ctx.context,
            cancel_signal=ctx.cancellation_signal,
            initial_model=ctx.model,
            initial_agent_reference=ctx.agent_reference,
            agent_session_id=ctx.agent_session_id,
            conversation_id=ctx.conversation_id,
            user_id_key=ctx.user_id,
        )

        # Register so GET can observe in-flight state
        await self._runtime_state.add(record)

        # Launch handler immediately (S-003: handler runs asynchronously)
        # Use anyio.CancelScope(shield=True) + suppress CancelledError so the
        # background task is NOT cancelled when the HTTP request scope exits
        # (anyio structured concurrency).  The shielded scope ensures the handler
        # runs to completion; catching CancelledError prevents the Task from being
        # marked as cancelled, so _refresh_background_status reads the real status.
        async def _shielded_runner() -> None:
            assert ctx.context is not None
            try:
                with anyio.CancelScope(shield=True):
                    await _run_background_non_stream(
                        create_fn=self._create_fn,
                        parsed=ctx.parsed,
                        context=ctx.context,
                        cancellation_signal=ctx.cancellation_signal,
                        record=record,
                        response_id=ctx.response_id,
                        agent_reference=ctx.agent_reference,
                        model=ctx.model,
                        provider=self._provider,
                        store=ctx.store,
                        agent_session_id=ctx.agent_session_id,
                        conversation_id=ctx.conversation_id,
                        history_limit=self._runtime_options.default_fetch_history_count,
                        runtime_state=self._runtime_state,
                        runtime_options=self._runtime_options,
                    )
            except asyncio.CancelledError:
                pass  # event-loop teardown; background work already done

        if ctx.store:
            # (Spec 024 Phase 2) Unified path for Row 1 + Row 2 (bg+store):
            # the handler ALWAYS runs inside the resilient task body. The
            # disposition determines recovery behaviour only:
            #   - resilient_background=True  → re-invoke (Row 1: handler
            #     re-runs on next-lifetime recovery).
            #   - resilient_background=False → mark-failed (Row 2: response
            #     is marked failed on next-lifetime recovery).
            # The legacy ``asyncio.create_task(_shielded_runner)`` path
            # for Row 2 + the separate bookkeeping task are deleted —
            # one resilient task per response covers both rows.
            disposition = decide_disposition(
                background=ctx.background,
                resilient_background=self._runtime_options.resilient_background,
                store=ctx.store,
            )
            await self._start_resilient_background(ctx, record, _shielded_runner, disposition=disposition)
        else:
            # Row 4 — no store, no resilient task. Plain asyncio.
            record.execution_task = asyncio.create_task(_shielded_runner())

        # Wait for handler to emit response.created (or fail).
        await record.response_created_signal.wait()

        # If input was queued on an already-active steerable task,
        # return the acceptance hook response (status: queued).
        if getattr(record, "input_queued", False):
            from ._acceptance import (
                dispatch_acceptance_hook,
            )  # pylint: disable=import-outside-toplevel

            acceptance_hook = getattr(self, "_acceptance_hook", None)
            queued_response = dispatch_acceptance_hook(
                hook=acceptance_hook,
                request=ctx.parsed,
                context=ctx.context,  # type: ignore[arg-type]
                model=ctx.model,
            )
            ctx.span.end(None)
            return queued_response

        # If handler failed before emitting any events, return the failed
        # snapshot (status: failed).  Background POST always returns 200 —
        # the failure is reflected in the response status, not the HTTP code.
        if record.response_failed_before_events:
            ctx.span.end(RuntimeError("Handler failed before response.created"))
            return _RuntimeState.to_snapshot(record)

        ctx.span.end(None)
        return _RuntimeState.to_snapshot(record)

    async def _run_resilient_stream_body(
        self,
        *,
        parsed: "CreateResponse",
        context: "ResponseContext",
        cancellation_signal: asyncio.Event,
        record: ResponseExecution,
        response_id: str,
        agent_reference: "AgentReference | dict[str, Any]",
        model: str | None,
        store: bool,
        agent_session_id: str | None,
        conversation_id: str | None,
        background: bool = True,
    ) -> None:
        """Resilient task body for streaming responses.

        Called from ``ResilientResponseOrchestrator._execute_in_task`` when
        ``params["stream"]`` is True. Drives the handler through the streaming
        pipeline (``_process_handler_events``) which emits events to the
        per-response stream from the registry (``streams.get_or_create(
        response_id)``). The live wire iterator on ``_live_stream``'s side
        is subscribed to the same registry stream; the file-backed backing
        also persists each event to disk for the GET reconnect endpoint.

        On fresh entry: a live wire connection exists; the wire iterator in
        ``_live_stream``'s bg+store branch consumes events as they arrive.

        On recovered entry: no wire connection (prior lifetime is dead). The
        handler still runs and events still get persisted; reconnecting
        clients see the events via the GET reconnect endpoint.

        :keyword parsed: Parsed create-response request.
        :paramtype parsed: CreateResponse
        :keyword context: Runtime response context for this request.
        :paramtype context: ResponseContext
        :keyword cancellation_signal: Event signalling cancellation.
        :paramtype cancellation_signal: asyncio.Event
        :keyword record: The mutable execution record.
        :paramtype record: ResponseExecution
        :keyword response_id: The response ID for this execution.
        :paramtype response_id: str
        :keyword agent_reference: Normalized agent reference model or dictionary.
        :paramtype agent_reference: AgentReference | dict[str, Any]
        :keyword model: Model name, or ``None``.
        :paramtype model: str | None
        :keyword store: Whether the response should be persisted.
        :paramtype store: bool
        :keyword agent_session_id: Resolved session ID.
        :paramtype agent_session_id: str | None
        :keyword conversation_id: Optional conversation ID.
        :paramtype conversation_id: str | None
        :keyword background: Whether the request is a background response.
        :paramtype background: bool
        :return: None
        :rtype: None

        :keyword parsed: The parsed ``CreateResponse`` for this request.
        :keyword context: The handler's :class:`ResponseContext`.
        :keyword cancellation_signal: Per-request cancellation event
            (already bridged from ``ctx.cancel`` / ``ctx.shutdown`` by the
            resilient orchestrator).
        :keyword record: The :class:`ResponseExecution` (already registered
            with ``runtime_state`` by the orchestrator).
        :keyword response_id: The response identifier.
        :keyword agent_reference: Resolved agent reference for this request.
        :keyword model: The model name (or ``None``).
        :keyword store: Whether the response should be persisted (always
            True for the resilient streaming path — we wouldn't be here
            otherwise).
        :keyword agent_session_id: Resolved agent session id.
        :keyword conversation_id: Optional conversation id.
        """
        # Build a minimal _ExecutionContext for the streaming pipeline. The
        # pipeline only reads a handful of fields from ctx; we don't need
        # the original span (which lived on the wire-request side and may
        # already be ended by the time the resilient body runs).
        from ._observability import (  # pylint: disable=import-outside-toplevel
            CreateSpan,
        )

        # Protocol 2.0.0: stamp the record's ``user_id_key`` AND ``call_id`` (via
        # ``ctx.user_id`` / ``ctx.call_id``) so in-process isolation enforcement
        # is not bypassed and every storage operation from the resilient body
        # replays the SAME ``(user_id, call_id)`` identity pair the response was
        # created with. Both are durable input persisted on the resilient task
        # (survives cross-process recovery), sourced here from the reconstructed
        # ``platform_context``.
        _user_id_key = context.platform_context.user_id_key if context is not None else None
        _call_id = context.platform_context.call_id if context is not None else None

        synthetic_span = CreateSpan(
            name="responses.resilient_stream_body",
            tags={"response.id": response_id},
        )
        ctx = _ExecutionContext(
            response_id=response_id,
            agent_reference=agent_reference,
            model=model,
            store=store,
            background=background,
            stream=True,
            input_items=list(record.input_items or []),
            previous_response_id=record.previous_response_id,
            conversation_id=conversation_id,
            cancellation_signal=cancellation_signal,
            span=synthetic_span,
            parsed=parsed,
            agent_session_id=agent_session_id,
            context=context,
            user_id=_user_id_key,
            call_id=_call_id,
        )

        state = _PipelineState()
        # The wire iterator on _live_stream's side subscribed to the
        # per-response stream BEFORE this body started. Looking it up from
        # the registry returns the SAME instance — every emit fans out to
        # the wire iterator. Bind it on ``record`` so the helpers that read
        # ``record.subject`` (publish, close) target this stream.
        wire_stream = await streams.get_or_create(response_id)
        record.subject = wire_stream
        # Seed the per-attempt sequence counter from the prior persisted
        # event count. On fresh entry the persisted log is empty →
        # next_seq=0 (no behaviour change). On recovered entry the
        # persisted log already has lifetime-1's events → next_seq = last
        # cursor + 1 so the recovered handler's events have seq numbers
        # strictly succeeding the pre-crash events, keeping the assembled
        # (cross-attempt) stream monotonic. Best-effort: any backing error
        # falls back to 0 rather than blocking the body.
        try:
            _last = await wire_stream.last_cursor()
            state.next_seq = (_last + 1) if _last is not None else 0
        except EventStreamNotFoundError:
            # The previous run completed AND every persisted event has
            # since expired. Start fresh.
            await streams.delete(response_id)
            wire_stream = await streams.get_or_create(response_id)
            record.subject = wire_stream
            state.next_seq = 0
        except Exception:  # pylint: disable=broad-exception-caught
            logger.debug(
                "Could not load last cursor for response_id=%s — seeding " + "next_seq=0",
                response_id,
                exc_info=True,
            )
            state.next_seq = 0
        handler_iterator = self._create_fn(parsed, context, cancellation_signal)

        # Drive the streaming pipeline. Events flow to the per-response
        # stream — the wire iterator on _live_stream's side consumes from
        # the same registry stream independently, and the file-backed
        # backing (when configured) persists every emit to disk for the
        # GET reconnect endpoint.
        try:
            async for _event in self._process_handler_events(ctx, state, handler_iterator):
                # Events are emitted to record.subject inside
                # _process_handler_events; we only need to drain the
                # generator.
                pass

            # Persist-then-yield resolution for the terminal event.
            if state.pending_terminal is not None:
                r = state.bg_record or _make_ephemeral_record(ctx, state)
                await self._persist_and_resolve_terminal(ctx, state, r)
                # ``_persist_and_resolve_terminal`` emits the resolved
                # terminal to the per-response stream (the same instance
                # as ``wire_stream`` by registry identity) when
                # ``ctx.background and ctx.store``, so we do not re-emit.
        finally:
            # Detect "leave in_progress for next-lifetime recovery" — set
            # by the exception handler in _process_handler_events when
            # SHUTTING_DOWN is detected for a resilient_background+store
            # response. In that case we MUST NOT close the wire stream:
            # closing flushes a terminal marker, which puts the stream
            # in CLOSED state. The recovered handler on the next
            # lifetime would then see a CLOSED stream and its emits
            # would silently no-op (closed-stream contract), leaving
            # GET ?stream=true post-recovery without a terminal event
            # even though the recovered handler ran to completion. The
            # finalize_stream / close steps are skipped — the next
            # lifetime's _run_resilient_stream_body will re-open the same
            # registry entry (file-backed; rehydrated from on-disk
            # state) and append its events from next_seq (cross-attempt
            # continuity per spec 017 streaming.md).
            _leave_for_recovery = state.leave_stream_open_for_recovery
            if not _leave_for_recovery:
                # Ensure finalization runs on every exit path (handler error,
                # cancellation, normal completion). Same as _live_stream's
                # finally for bg+store path.
                try:
                    await self._finalize_stream(ctx, state)
                except Exception:  # pylint: disable=broad-exception-caught
                    logger.warning(
                        "_finalize_stream failed for resilient streaming body " + "response_id=%s",
                        response_id,
                        exc_info=True,
                    )
                # Always close the per-response stream so the live wire
                # iterator exits cleanly. Idempotent if _finalize_stream
                # already closed the same stream through state.bg_record.
                await self._safe_close(wire_stream)

    # (Spec 024 Phase 2) `_complete_bookkeeping_task` deleted. The
    # bookkeeping pattern is gone — handler now runs inside the resilient
    # task body for Rows 1/2/3 and the task completes when the handler
    # returns. No external completion signal is needed.

    async def _start_resilient_background(
        self,
        ctx: _ExecutionContext,
        record: ResponseExecution,
        fallback_runner: Any,
        *,
        disposition: str = "re-invoke",
    ) -> None:
        """Start the resilient task-backed background execution.

        Creates a ResilientResponseOrchestrator and starts the task. The task
        body runs the handler inside the task primitive, providing crash
        recovery guarantees.

        Two outcomes when the resilient start cannot proceed:

        - **No manager installed** — the start raises
          :class:`~azure.ai.agentserver.core.tasks.TaskManagerNotInitialized`.
          Because ``AgentServerHost`` fails the lifespan when resilient tasks are
          ENABLED but construction/startup fails, a missing manager in a running
          deployment means resilient tasks are DISABLED (opt-out) — durability
          was not requested (this also covers in-process test clients whose
          lifespan never ran). The signal is **swallowed** and the handler runs
          in-process via ``fallback_runner`` — the response still executes and
          persists (GET works); it is simply not crash-recoverable. NOT a
          failure.
        - **Subsystem present but the start fails**: fail immediately. The
          exception is tagged as a platform infrastructure error and re-raised
          (no silent degradation to a non-durable task — that would hide a real
          durability failure behind a healthy-looking response).

        :param ctx: Current execution context.
        :type ctx: _ExecutionContext
        :param record: The mutable execution record.
        :type record: ResponseExecution
        :param fallback_runner: The shielded runner coroutine function to run
            in-process when resilient tasks are disabled.
        :type fallback_runner: Any
        :keyword disposition: One of ``"re-invoke"`` (Row 1: resilient_bg+bg+store
            — task body re-runs handler on recovery) or ``"mark-failed"``
            (Rows 2/3: bg+store with resilient_bg=False, or fg+store — task body
            is bookkeeping-only on fresh entry and marks the response failed on
            recovery). Stamped into task framework metadata so recovery dispatch
            can route without re-deriving the gate from request params.
        :paramtype disposition: str
        :raises Exception: If the task subsystem is present and the resilient
            start fails (e.g. the task-store write is rejected). The exception is
            tagged with ``PLATFORM_ERROR_TAG`` so the endpoint surfaces
            ``x-platform-error-source: platform``. A missing subsystem
            (``TaskManagerNotInitialized``) is NOT raised — it is swallowed and
            handled via the in-process fallback (see above).
        """
        from ._resilient_orchestrator import (
            ResilientResponseOrchestrator,
        )  # pylint: disable=import-outside-toplevel

        if not hasattr(self, "_resilient_orchestrator"):
            self._resilient_orchestrator = ResilientResponseOrchestrator(
                create_fn=self._create_fn,
                options=self._runtime_options,
                provider=self._provider,
                runtime_state=self._runtime_state,
                parent_orchestrator=self,
            )

        # (Spec 033 §3.4) Resilient-task construction — the typed boundary + the
        # process-local refs — is owned by the resilience orchestrator; the
        # response pipeline only supplies the per-request context and disposition.
        resilient_input, refs = self._resilient_orchestrator.build_resilient_input(ctx, record, disposition=disposition)

        try:
            freshly_started = await self._resilient_orchestrator.start_resilient(
                record=record,
                resilient_input=resilient_input,
                refs=refs,
            )
            if not freshly_started:
                # Input was queued on already-active multi-turn steerable
                # chain. The downstream `start_resilient` already detected
                # this via the TaskRun's queued-cancel callback. Signal
                # the record that it should return a "queued" envelope
                # via the acceptance hook instead of waiting for handler
                # execution.
                record.input_queued = True  # type: ignore[attr-defined]
                record.response_created_signal.set()
        except TaskConflictError:
            # Spec 023 — concurrent conflict on a shared task_id (Row 5
            # concurrent overlap for `conv_id + steerable=False`, or the
            # legacy steerable-chain in-progress conflict). Propagate so
            # the endpoint handler maps it to HTTP 409 `conversation_locked`.
            # All shared-task-id rows (5, 6, 7) hit this path; the only
            # rows that DON'T are the one-shot rows (1-4) which use
            # unique task_ids per request and shouldn't conflict.
            raise
        except LastInputIdPreconditionFailed:
            # (Spec 013 US2) Steerable conversations enforce sequential
            # `previous_response_id`. Propagate so the endpoint layer
            # surfaces HTTP 409 `conversation_fork_not_supported`.
            raise
        except TaskManagerNotInitialized:
            # No manager is installed. Because ``AgentServerHost`` fails the
            # lifespan when resilient tasks are ENABLED but construction/startup
            # fails, a missing manager in a running deployment means resilient
            # tasks are simply DISABLED (opt-out) — recovery/durability was not
            # requested. (It also covers in-process test clients whose lifespan
            # never ran.) SWALLOW and run the handler in-process: the response
            # still executes and persists (GET works), it is simply not
            # crash-recoverable. This is the deliberate non-durable path, NOT a
            # failure.
            logger.info(
                "Resilient task subsystem not enabled for response %s; running handler "
                "in-process (non-durable). Enable via set_resilient_tasks_enabled(True) "
                "(or resilient_background) for crash recovery.",
                ctx.response_id,
            )
            record.execution_task = asyncio.create_task(fallback_runner())
        except Exception as exc:  # pylint: disable=broad-exception-caught
            # The resilient-task subsystem IS present but starting the task
            # failed (e.g. the task-store write was rejected). Do NOT silently
            # degrade to a non-durable, connection-scoped asyncio task — that
            # hides a real durability failure behind a healthy-looking response.
            # Fail loudly, tagged as a platform infrastructure error so the
            # endpoint surfaces ``x-platform-error-source: platform`` (the same
            # way Foundry storage failures are surfaced).
            logger.error(
                "Resilient task start failed for response %s; failing the request",
                ctx.response_id,
                exc_info=True,
            )
            setattr(exc, PLATFORM_ERROR_TAG, True)
            # Best-effort cleanup of the in-flight record so a later GET does not
            # observe a phantom ``in_progress`` response (no-op for callers that
            # never registered the record, e.g. the streaming path).
            await self._runtime_state.delete(ctx.response_id)
            raise
