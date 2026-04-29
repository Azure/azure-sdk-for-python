# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
# pylint: disable=too-many-statements
"""Event-pipeline orchestration for the Responses server.

This module is intentionally free of Starlette imports: it operates purely on
``_ExecutionContext`` and produces plain Python data (dicts, async iterators of
strings). The HTTP layer (Starlette ``Request`` / ``Response``) lives in the
routing module which wraps these results.
"""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import logging
from copy import deepcopy
from typing import TYPE_CHECKING, Any, AsyncIterator, Callable, cast

import anyio

from .._options import ResponsesServerOptions
from ..models import _generated as generated_models
from ..models.runtime import (
    ResponseExecution,
    ResponseModeFlags,
    ResponseStatus,
)
from ..models.runtime import (
    build_cancelled_response as _build_cancelled_response,
)
from ..models.runtime import (
    build_failed_response as _build_failed_response,
)
from ..store._base import ResponseProviderProtocol, ResponseStreamProviderProtocol
from ..streaming._helpers import (
    _apply_stream_event_defaults,
    _build_events,
    _coerce_handler_event,
    _extract_response_snapshot_from_events,
)
from ..streaming._internals import construct_event_model
from ..streaming._sse import encode_keep_alive_comment, encode_sse_any_event, new_stream_counter
from ..streaming._state_machine import EventStreamValidator
from ._event_subject import _ResponseEventSubject
from ._execution_context import _ExecutionContext
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
    """Return an error message if the first handler event violates FR-006/FR-007, else None.

    - FR-006: The first event MUST be ``response.created`` with matching ``id``.
    - FR-007: The ``status`` in ``response.created`` MUST be non-terminal.

    :param normalized: Normalised first event (``ResponseStreamEvent`` model instance).
    :type normalized: ResponseStreamEvent
    :param response_id: Library-assigned response identifier.
    :type response_id: str
    :return: Violation message string, or ``None`` if no violation.
    :rtype: str | None
    """
    event_type = normalized.get("type")
    response = normalized.get("response") or {}
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
        generated_models.ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_ADDED.value,
        generated_models.ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_DONE.value,
    }
)

# Response-level lifecycle events whose ``response`` field carries a full Response snapshot.
# Used by FR-008a output manipulation detection.
_RESPONSE_SNAPSHOT_TYPES: frozenset[str] = frozenset(
    {
        generated_models.ResponseStreamEventType.RESPONSE_IN_PROGRESS.value,
        generated_models.ResponseStreamEventType.RESPONSE_COMPLETED.value,
        generated_models.ResponseStreamEventType.RESPONSE_FAILED.value,
        generated_models.ResponseStreamEventType.RESPONSE_INCOMPLETE.value,
        generated_models.ResponseStreamEventType.RESPONSE_QUEUED.value,
    }
)


def _validate_handler_event(coerced: generated_models.ResponseStreamEvent) -> str | None:
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


async def _run_background_non_stream(  # pylint: disable=too-many-locals,too-many-branches
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
    :return: None
    :rtype: None
    """
    record.transition_to("in_progress")
    handler_events: list[generated_models.ResponseStreamEvent] = []
    validator = EventStreamValidator()
    output_item_count = 0
    _provider_created = False  # tracks whether create_response was called
    # Track whether the handler set queued status so we can honour it
    _handler_initial_status: str | None = None
    first_event_processed = False

    try:
        try:
            async for handler_event in _iter_with_winddown(
                create_fn(parsed, context, cancellation_signal), cancellation_signal
            ):
                if cancellation_signal.is_set():
                    if record.status not in ("cancelled", "completed", "failed", "incomplete"):
                        record.transition_to("cancelled")
                    return

                coerced = _coerce_handler_event(handler_event)
                b30_err = _validate_handler_event(coerced)
                if b30_err:
                    raise ValueError(b30_err)
                normalized = _apply_stream_event_defaults(
                    coerced,
                    response_id=response_id,
                    agent_reference=agent_reference,
                    model=model,
                    sequence_number=None,
                    agent_session_id=agent_session_id,
                    conversation_id=conversation_id,
                )
                handler_events.append(normalized)
                validator.validate_next(normalized)
                if not first_event_processed:
                    first_event_processed = True

                    # FR-008a: output manipulation detection on response.created
                    created_response = normalized.get("response") or {}
                    created_output = created_response.get("output")
                    if isinstance(created_output, list) and len(created_output) != 0:
                        raise ValueError(
                            f"Handler directly modified Response.Output "
                            f"(found {len(created_output)} items, expected 0). "
                            f"Use output builder events instead."
                        )

                    # Set initial response snapshot for POST response body without
                    # changing record.status (transition_to manages status lifecycle)
                    _initial_snapshot = _extract_response_snapshot_from_events(
                        handler_events,
                        response_id=response_id,
                        agent_reference=agent_reference,
                        model=model,
                        agent_session_id=agent_session_id,
                        conversation_id=conversation_id,
                    )
                    record.set_response_snapshot(generated_models.ResponseObject(_initial_snapshot))
                    # Honour the handler's initial status (e.g. "queued") so the
                    # POST response body reflects what the handler actually set.
                    _handler_initial_status = _initial_snapshot.get("status")
                    if _handler_initial_status == "queued":
                        record.status = "queued"  # type: ignore[assignment]
                    # Persist at response.created time for bg+store (FR-003)
                    if store and provider is not None:
                        try:
                            _isolation = context.isolation if context else None
                            _response_obj = generated_models.ResponseObject(_initial_snapshot)
                            _history_ids = (
                                await provider.get_history_item_ids(
                                    record.previous_response_id,
                                    None,
                                    history_limit,
                                    isolation=_isolation,
                                )
                                if record.previous_response_id
                                else None
                            )
                            _resolved_items = await _resolve_input_items_for_persistence(context, record.input_items)
                            await provider.create_response(
                                _response_obj, _resolved_items, _history_ids, isolation=_isolation
                            )
                            _provider_created = True
                        except Exception as persist_exc:  # pylint: disable=broad-exception-caught
                            # §3.3: Phase 1 create failure — mark persistence failed
                            # so the terminal update knows not to attempt update_response.
                            logger.error(
                                "Phase 1 create_response failed for bg non-stream (response_id=%s): %s",
                                response_id,
                                persist_exc,
                                exc_info=True,
                            )
                            record.persistence_failed = True
                            record.persistence_exception = persist_exc
                    record.response_created_signal.set()
                    # Yield to the event loop so run_background's
                    # ``await signal.wait()`` can resume and capture the
                    # in_progress snapshot *before* the handler continues
                    # to terminal state.  Without this, handlers that yield
                    # events synchronously (no await between yields) can
                    # run to completion — including transition_to("completed"),
                    # persistence, and eager eviction — in a single
                    # uninterrupted coroutine run, causing the POST response
                    # to return "completed" instead of "in_progress".
                    await asyncio.sleep(0)
                else:
                    # Track output_item.added events for FR-008a
                    _item_added = generated_models.ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_ADDED
                    if normalized.get("type") == _item_added.value:
                        output_item_count += 1

                    # FR-008a: detect direct Output manipulation on response.* events
                    n_type = normalized.get("type", "")
                    if n_type in _RESPONSE_SNAPSHOT_TYPES:
                        n_response = normalized.get("response") or {}
                        n_output = n_response.get("output")
                        if isinstance(n_output, list) and len(n_output) > output_item_count:
                            raise ValueError(
                                f"Output item count mismatch "
                                f"({len(n_output)} vs {output_item_count} output_item.added events)"
                            )
        except asyncio.CancelledError:
            # S-024: Distinguish known cancellation (cancel_signal set) from
            # unknown.  Known cancellation → transition to "cancelled".
            if cancellation_signal.is_set():
                if record.status not in ("cancelled", "completed", "failed", "incomplete"):
                    record.transition_to("cancelled")
                if not first_event_processed:
                    record.response_failed_before_events = True
                record.response_created_signal.set()
                return
            # S-024: Unknown CancelledError before any events were yielded
            # means the handler itself raised it — treat as handler failure.
            if not first_event_processed:
                logger.error(
                    "Unknown CancelledError during background processing (response_id=%s)",
                    response_id,
                )
                record.set_response_snapshot(
                    _build_failed_response(
                        response_id,
                        agent_reference,
                        model,
                        created_at=context.created_at,
                    )
                )
                record.transition_to("failed")
                record.response_failed_before_events = True
                record.response_created_signal.set()
                return
            # After events have been processed the CancelledError is most
            # likely from event-loop / scope teardown — re-raise so the
            # shielded runner can absorb it.
            raise
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error(
                "Handler raised during background processing (response_id=%s)",
                response_id,
                exc_info=exc,
            )
            if record.status != "cancelled":
                record.set_response_snapshot(
                    _build_failed_response(
                        response_id,
                        agent_reference,
                        model,
                        created_at=context.created_at,
                    )
                )
                record.transition_to("failed")
            if not first_event_processed:
                # Mark failure before any events so run_background can return HTTP 500
                record.response_failed_before_events = True
            record.response_created_signal.set()  # unblock run_background on failure
            return

        if cancellation_signal.is_set():
            if record.status not in ("cancelled", "completed", "failed", "incomplete"):
                record.transition_to("cancelled")
            record.response_created_signal.set()  # unblock run_background on cancellation
            return

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
        if record.status != "cancelled":
            record.set_response_snapshot(generated_models.ResponseObject(response_payload))
            target = resolved_status if isinstance(resolved_status, str) else "completed"
            # If still queued, transition through in_progress first so the
            # state machine stays valid (queued can only reach terminal
            # states via in_progress).
            if record.status == "queued" and target != "in_progress":
                record.transition_to("in_progress")
            record.transition_to(cast(ResponseStatus, target))
    finally:
        # Always unblock run_background (idempotent if already set)
        record.response_created_signal.set()
        # Stamp mode flags so the provider fallback can enforce B1/B2 checks
        # after eager eviction removes the in-memory record.  This covers
        # all code paths (normal completion, handler failure, cancellation).
        if record.response is not None:
            record.response.background = record.mode_flags.background
        # Persist terminal state update via provider (bg non-stream: update after runner completes)
        # §3.5: Persistence failure sets persistence_failed on the record and
        # replaces the snapshot with storage_error so GET returns the failure.
        if store and provider is not None and record.status not in {"cancelled"} and record.response is not None:
            if record.persistence_failed:
                # Phase 1 already failed — skip update attempt and apply storage error.
                storage_error_response = _build_failed_response(
                    response_id,
                    agent_reference,
                    model,
                    created_at=context.created_at if context else None,
                    error_code="storage_error",
                    error_message=_STORAGE_ERROR_MESSAGE,
                )
                record.set_response_snapshot(storage_error_response)
                record.status = "failed"  # type: ignore[assignment]
            else:
                _isolation = context.isolation if context else None
                try:
                    if _provider_created:
                        await provider.update_response(record.response, isolation=_isolation)
                    else:
                        # Response was never created (handler yielded nothing or
                        # failed before response.created) — create instead of update.
                        _resolved_items = await _resolve_input_items_for_persistence(context, record.input_items)
                        await provider.create_response(record.response, _resolved_items, None, isolation=_isolation)
                except Exception as persist_exc:  # pylint: disable=broad-exception-caught
                    logger.error(
                        "Persistence failed at bg non-stream finalization (response_id=%s): %s",
                        response_id,
                        persist_exc,
                        exc_info=True,
                    )
                    record.persistence_failed = True
                    record.persistence_exception = persist_exc
                    # Replace snapshot with storage_error response.failed
                    storage_error_response = _build_failed_response(
                        response_id,
                        agent_reference,
                        model,
                        created_at=context.created_at if context else None,
                        error_code="storage_error",
                        error_message=_STORAGE_ERROR_MESSAGE,
                    )
                    record.set_response_snapshot(storage_error_response)
                    record.status = "failed"  # type: ignore[assignment]
        # Eager eviction: free memory once terminal state is reached (or store=False).
        # Skip eviction when persistence failed — the in-memory record is the
        # only remaining source of truth for GET.
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
    (non-background streaming paths).  The record carries mode_flags and other
    metadata needed to drive the persistence attempt and track failure state.

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
        chat_isolation_key=ctx.chat_isolation_key,
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
    )

    def __init__(self) -> None:
        self.handler_events: list[generated_models.ResponseStreamEvent] = []
        self.bg_record: ResponseExecution | None = None
        self.captured_error: BaseException | None = None
        self.validator: EventStreamValidator = EventStreamValidator()
        self.stream_interrupted: bool = False
        self.pending_terminal: generated_models.ResponseStreamEvent | None = None
        self.provider_created: bool = False


class _ResponseOrchestrator:  # pylint: disable=too-many-instance-attributes
    """Event-pipeline orchestrator for the Responses API.

    Handles the business logic for streaming, synchronous, and background
    create-response requests: driving the handler iterator, normalising events,
    managing the background execution record, and finalising persistent state.

    This class has no dependency on Starlette types.
    """

    _TERMINAL_SSE_TYPES: frozenset[str] = frozenset(
        {
            generated_models.ResponseStreamEventType.RESPONSE_COMPLETED.value,
            generated_models.ResponseStreamEventType.RESPONSE_FAILED.value,
            generated_models.ResponseStreamEventType.RESPONSE_INCOMPLETE.value,
        }
    )

    def __init__(
        self,
        *,
        create_fn: Callable[..., AsyncIterator[generated_models.ResponseStreamEvent]],
        runtime_state: _RuntimeState,
        runtime_options: ResponsesServerOptions,
        provider: ResponseProviderProtocol,
        stream_provider: ResponseStreamProviderProtocol | None = None,
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
        :param stream_provider: Optional provider for SSE stream event persistence and replay.
        :type stream_provider: ResponseStreamProviderProtocol | None
        """
        self._create_fn = create_fn
        self._runtime_state = runtime_state
        self._runtime_options = runtime_options
        self._provider = provider
        self._stream_provider = stream_provider

    # ------------------------------------------------------------------
    # Internal helpers (stream path)
    # ------------------------------------------------------------------

    async def _normalize_and_append(
        self,
        ctx: _ExecutionContext,
        state: _PipelineState,
        handler_event: generated_models.ResponseStreamEvent | dict[str, Any],
    ) -> generated_models.ResponseStreamEvent:
        """Coerce, validate, normalise, and append a handler event to the pipeline state.

        Also propagates the event into the background record and its subject when active.
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
            sequence_number=len(state.handler_events),
            agent_session_id=ctx.agent_session_id,
            conversation_id=ctx.conversation_id,
        )
        state.handler_events.append(normalized)
        state.validator.validate_next(normalized)
        if state.bg_record is not None:
            state.bg_record.apply_event(normalized, state.handler_events)
            # Defer subject.publish for terminal events — the buffer-then-persist
            # pattern may replace the terminal event on persistence failure.  The
            # resolved terminal is published by _persist_and_resolve_terminal.
            if state.bg_record.subject is not None and normalized.get("type") not in self._TERMINAL_SSE_TYPES:
                await state.bg_record.subject.publish(normalized)
        return normalized

    @staticmethod
    def _has_terminal_event(handler_events: list[generated_models.ResponseStreamEvent]) -> bool:
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
        cancel_event: dict[str, Any] = {
            "type": generated_models.ResponseStreamEventType.RESPONSE_FAILED.value,
            "response": _build_cancelled_response(ctx.response_id, ctx.agent_reference, ctx.model).as_dict(),
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
        failed_event: dict[str, Any] = {
            "type": generated_models.ResponseStreamEventType.RESPONSE_FAILED.value,
            "response": {
                "id": ctx.response_id,
                "object": "response",
                "status": "failed",
                "output": [],
                "error": {"code": "server_error", "message": "An internal server error occurred."},
            },
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
        storage_error_response = _build_failed_response(
            ctx.response_id,
            ctx.agent_reference,
            ctx.model,
            created_at=ctx.context.created_at if ctx.context else None,
            error_code="storage_error",
            error_message=_STORAGE_ERROR_MESSAGE,
        )
        replacement_event: dict[str, Any] = {
            "type": generated_models.ResponseStreamEventType.RESPONSE_FAILED.value,
            "response": storage_error_response.as_dict(),
        }

        # Determine the sequence_number: reuse the original pending terminal's
        # sequence_number (in-place replacement) to avoid gaps.
        original_pending = state.pending_terminal
        replacement_index = -1
        replacement_seq = len(state.handler_events)
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
        state.pending_terminal = replacement_normalized
        record.set_response_snapshot(storage_error_response)
        # Force status to failed — bypass transition_to since the record may
        # already be in a terminal state (e.g. "completed") that doesn't allow
        # normal transitions.
        record.status = "failed"  # type: ignore[assignment]

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

        # Update snapshot on record before persistence attempt
        record.set_response_snapshot(generated_models.ResponseObject(response_payload))
        record.transition_to(status)

        # Attempt persistence
        if ctx.store and record.response is not None:
            if record.persistence_failed:
                # Phase 1 already failed — skip persistence attempt, emit storage error directly.
                self._apply_storage_error_replacement(ctx, state, record)
            else:
                record.response.background = record.mode_flags.background
                _isolation = ctx.context.isolation if ctx.context else None
                try:
                    if state.provider_created:
                        # bg+stream: initial create already done at response.created — use update
                        await self._provider.update_response(record.response, isolation=_isolation)
                    else:
                        # non-bg stream or bg stream where initial create was never registered:
                        # full create
                        _history_ids = (
                            await self._provider.get_history_item_ids(
                                ctx.previous_response_id,
                                None,
                                self._runtime_options.default_fetch_history_count,
                                isolation=_isolation,
                            )
                            if ctx.previous_response_id
                            else None
                        )
                        _resolved_items = await _resolve_input_items_for_persistence(ctx.context, ctx.input_items)
                        await self._provider.create_response(
                            generated_models.ResponseObject(response_payload),
                            _resolved_items,
                            _history_ids,
                            isolation=_isolation,
                        )
                except Exception as persist_exc:  # pylint: disable=broad-exception-caught
                    logger.error(
                        "Persistence failed at terminal event (response_id=%s): %s",
                        ctx.response_id,
                        persist_exc,
                        exc_info=True,
                    )
                    record.persistence_failed = True
                    record.persistence_exception = persist_exc
                    self._apply_storage_error_replacement(ctx, state, record)

        # Publish the resolved terminal event to the subject for replay subscribers.
        # This is deferred from _normalize_and_append to ensure subscribers see the
        # correct terminal (original on success, storage_error replacement on failure).
        if state.bg_record is not None and state.bg_record.subject is not None and state.pending_terminal is not None:
            await state.bg_record.subject.publish(state.pending_terminal)

        return state.pending_terminal

    async def _register_bg_execution(
        self, ctx: _ExecutionContext, state: _PipelineState, first_normalized: generated_models.ResponseStreamEvent
    ) -> None:
        """Create, seed, and register the background+stream execution record.

        Called from :meth:`_process_handler_events` after the first event is
        received.  The record is seeded with ``first_normalized`` so that
        subscribers joining mid-stream receive the full history.

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
        initial_payload["background"] = True
        initial_status = initial_payload.get("status")
        if not isinstance(initial_status, str):
            initial_status = "in_progress"
        execution = ResponseExecution(
            response_id=ctx.response_id,
            mode_flags=ResponseModeFlags(stream=True, store=True, background=True),
            status=cast(ResponseStatus, initial_status),
            input_items=deepcopy(ctx.input_items),
            previous_response_id=ctx.previous_response_id,
            cancel_signal=ctx.cancellation_signal,
            agent_session_id=ctx.agent_session_id,
            conversation_id=ctx.conversation_id,
            chat_isolation_key=ctx.chat_isolation_key,
        )
        execution.set_response_snapshot(generated_models.ResponseObject(initial_payload))
        execution.subject = _ResponseEventSubject()
        state.bg_record = execution
        assert state.bg_record.subject is not None
        await state.bg_record.subject.publish(first_normalized)
        await self._runtime_state.add(execution)
        if ctx.store:
            _isolation = ctx.context.isolation if ctx.context else None
            _initial_response_obj = generated_models.ResponseObject(initial_payload)
            _history_ids = (
                await self._provider.get_history_item_ids(
                    ctx.previous_response_id,
                    None,
                    self._runtime_options.default_fetch_history_count,
                    isolation=_isolation,
                )
                if ctx.previous_response_id
                else None
            )
            _resolved_items = await _resolve_input_items_for_persistence(ctx.context, ctx.input_items)
            try:
                await self._provider.create_response(
                    _initial_response_obj, _resolved_items, _history_ids, isolation=_isolation
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

    async def _process_handler_events(  # pylint: disable=too-many-return-statements,too-many-branches
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
        # --- First event ---
        try:
            first_raw = await handler_iterator.__anext__()
        except StopAsyncIteration:
            # B17: Handler exited without yielding after cancellation — treat
            # as a cancellation (not an empty handler) so that run_sync raises
            # _HandlerError and the response is never persisted.
            if ctx.cancellation_signal.is_set():
                state.captured_error = asyncio.CancelledError()
                return
            # Handler yielded nothing: synthesise fallback lifecycle events.
            fallback_events = _build_events(
                ctx.response_id,
                include_progress=True,
                agent_reference=ctx.agent_reference,
                model=ctx.model,
            )
            for event in fallback_events:
                state.handler_events.append(event)
                if event.get("type") in self._TERMINAL_SSE_TYPES:
                    state.pending_terminal = event
                else:
                    yield event
            return
        except asyncio.CancelledError:
            # S-024: Known cancellation before first event.
            if ctx.cancellation_signal.is_set():
                state.captured_error = asyncio.CancelledError()
                yield construct_event_model(
                    {
                        "type": "error",
                        "message": "An internal server error occurred.",
                        "param": None,
                        "code": None,
                        "sequence_number": 0,
                    }
                )
                return
            # Unknown CancelledError (e.g. event-loop teardown) — re-raise.
            raise
        except Exception as exc:  # pylint: disable=broad-exception-caught
            # B8: Pre-creation error → emit a standalone `error` event only.
            # No response.created precedes it; this is the contract-mandated shape.
            logger.error(
                "Handler raised before response.created (response_id=%s)",
                ctx.response_id,
                exc_info=exc,
            )
            state.captured_error = exc
            yield construct_event_model(
                {
                    "type": "error",
                    "message": "An internal server error occurred.",
                    "param": None,
                    "code": None,
                    "sequence_number": 0,
                }
            )
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
            yield construct_event_model(
                {
                    "type": "error",
                    "message": "An internal server error occurred.",
                    "param": None,
                    "code": None,
                    "sequence_number": 0,
                }
            )
            return

        first_normalized = _apply_stream_event_defaults(
            first_coerced,
            response_id=ctx.response_id,
            agent_reference=ctx.agent_reference,
            model=ctx.model,
            sequence_number=len(state.handler_events),
            agent_session_id=ctx.agent_session_id,
            conversation_id=ctx.conversation_id,
        )

        # FR-006/FR-007: first-event contract validation.
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
            yield construct_event_model(
                {
                    "type": "error",
                    "message": "An internal server error occurred.",
                    "param": None,
                    "code": None,
                    "sequence_number": 0,
                }
            )
            return

        state.handler_events.append(first_normalized)
        state.validator.validate_next(first_normalized)

        # FR-008a: output manipulation detection on response.created.
        # If the handler directly added items to response.output instead of
        # using builder events, the output list will be non-empty.
        created_response = first_normalized.get("response") or {}
        created_output = created_response.get("output")
        if isinstance(created_output, list) and len(created_output) != 0:
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

        # bg+store: create and register the execution record after the first event.
        if ctx.background and ctx.store:
            await self._register_bg_execution(ctx, state, first_normalized)
            # §3.3: If Phase 1 create failed, abort with standalone error event
            # (same shape as B8 pre-creation errors) — no response.created is yielded.
            if state.bg_record is not None and state.bg_record.persistence_failed:
                state.captured_error = state.bg_record.persistence_exception or RuntimeError("Phase 1 create failed")
                # Evict the in-memory record so GET/replay cannot observe an
                # in-progress response when §3.3 requires no response.created.
                await self._runtime_state.try_evict(ctx.response_id)
                yield construct_event_model(
                    {
                        "type": "error",
                        "message": _STORAGE_ERROR_MESSAGE,
                        "param": None,
                        "code": "storage_error",
                        "sequence_number": 0,
                    }
                )
                return

        yield first_normalized

        # --- Remaining events ---
        output_item_count = 0
        try:
            async for raw in _iter_with_winddown(handler_iterator, ctx.cancellation_signal):
                # FR-008a: Pre-check for output manipulation BEFORE validation.
                # Must inspect the raw event first so that an offending terminal
                # event (e.g. response.completed with manipulated output) is NOT
                # appended to the state machine before we emit response.failed.
                _pre_coerced = _coerce_handler_event(raw)
                _pre_type = _pre_coerced.get("type", "")
                if _pre_type == generated_models.ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_ADDED.value:
                    output_item_count += 1
                if _pre_type in _RESPONSE_SNAPSHOT_TYPES:
                    _pre_response = _pre_coerced.get("response") or {}
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
            # S-024: Known cancellation — emit cancel terminal.
            if ctx.cancellation_signal.is_set():
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
            # S-035: emit response.failed when handler raises after response.created.
            if not self._has_terminal_event(state.handler_events):
                state.pending_terminal = await self._make_failed_event(ctx, state)
            return

        # B11: cancellation winddown checked BEFORE S-015 so that a handler
        # stopped early by the cancellation signal receives a proper cancel
        # terminal event (response.failed with status == "cancelled") rather
        # than a generic S-015 failure terminal.
        if ctx.cancellation_signal.is_set() and not self._has_terminal_event(state.handler_events):
            state.pending_terminal = await self._cancel_terminal_sse_dict(ctx, state)
            return

        # S-015: handler completed normally but never emitted a terminal event.
        # NOTE: state.captured_error intentionally left None so that synchronous
        # callers return HTTP 200 with a "failed" body rather than HTTP 500.
        if not self._has_terminal_event(state.handler_events):
            state.pending_terminal = await self._make_failed_event(ctx, state)

    async def _finalize_stream(self, ctx: _ExecutionContext, state: _PipelineState) -> None:
        """Complete the subject, persist stream events, and evict for a streaming response.

        Called from the ``finally`` block of :meth:`_live_stream` AFTER the
        terminal event has already been yielded (and possibly replaced by
        ``_persist_and_resolve_terminal``).

        Responsibilities (post-persistence-resilience refactoring):
        - Register the execution record in runtime state (non-bg paths).
        - Persist SSE stream events for bg replay.
        - Complete the subject so replay subscribers see stream-end.
        - Eager eviction (skipped when persistence_failed is set).

        :param ctx: Current execution context (immutable inputs).
        :type ctx: _ExecutionContext
        :param state: Mutable pipeline state for this invocation.
        :type state: _PipelineState
        """
        # --- Path A: BG with pre-existing record (normal bg+stream completion) ---
        if ctx.background and ctx.store and state.bg_record is not None:
            record = state.bg_record

            # Persist SSE events for replay after process restart (not needed for cancelled).
            if record.status != "cancelled" and self._stream_provider is not None and state.handler_events:
                _isolation = ctx.context.isolation if ctx.context else None
                try:
                    await self._stream_provider.save_stream_events(
                        ctx.response_id, state.handler_events, isolation=_isolation
                    )
                except Exception:  # pylint: disable=broad-exception-caught
                    logger.warning(
                        "Best-effort stream event persistence failed (response_id=%s)",
                        ctx.response_id,
                        exc_info=True,
                    )

            ctx.span.end(state.captured_error)
            # Complete the subject — signals all live SSE replay subscribers that
            # the stream has ended.
            if record.subject is not None:
                try:
                    await record.subject.complete()
                except Exception:  # pylint: disable=broad-exception-caught
                    pass  # best effort
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

        # B17: Non-bg streaming cancelled by disconnect → do not persist.
        # The response was never committed to the store or runtime state,
        # so GET must return 404.
        if not ctx.background and state.stream_interrupted:
            ctx.span.end(state.captured_error)
            return

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
        replay_subject: _ResponseEventSubject | None = None
        if ctx.store:
            replay_subject = _ResponseEventSubject()
            for _evt in events:
                await replay_subject.publish(_evt)
            await replay_subject.complete()

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
            chat_isolation_key=ctx.chat_isolation_key,
        )
        execution.set_response_snapshot(generated_models.ResponseObject(response_payload))
        # Copy persistence_failed from the ephemeral record if one was used
        if state.bg_record is not None:
            execution.persistence_failed = state.bg_record.persistence_failed
            execution.persistence_exception = state.bg_record.persistence_exception
        await self._runtime_state.add(execution)

        # Persist SSE events for replay after eager eviction (bg+stream only).
        if ctx.background and ctx.store and self._stream_provider is not None and events:
            _isolation = ctx.context.isolation if ctx.context else None
            try:
                await self._stream_provider.save_stream_events(ctx.response_id, events, isolation=_isolation)
            except Exception:  # pylint: disable=broad-exception-caught
                logger.warning(
                    "Best-effort stream event persistence failed (response_id=%s)",
                    ctx.response_id,
                    exc_info=True,
                )

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
        handler_iterator = self._create_fn(ctx.parsed, ctx.context, ctx.cancellation_signal)

        # Helper: route to the right finalize method based on the request semantics
        # (bg+store → bg_stream path; everything else → non_bg_stream path).
        # NOTE: state.bg_record may be None for bg+stream when the handler yields no
        # events (fallback path in _process_handler_events); _finalize_bg_stream
        # handles that case by creating the record itself.
        async def _finalize() -> None:
            await self._finalize_stream(ctx, state)

        # --- Fast path: no keep-alive ---
        if not self._runtime_options.sse_keep_alive_enabled:
            if not (ctx.background and ctx.store):
                # Simple fast path for non-background streaming.
                _stream_completed = False
                try:
                    async for event in self._process_handler_events(ctx, state, handler_iterator):
                        yield encode_sse_any_event(event)
                    _stream_completed = True
                    # Persist-then-yield: resolve the buffered terminal event
                    if state.pending_terminal is not None:
                        record = state.bg_record or _make_ephemeral_record(ctx, state)
                        resolved = await self._persist_and_resolve_terminal(ctx, state, record)
                        yield encode_sse_any_event(resolved)
                finally:
                    # B17: If the stream did not complete naturally (e.g. client
                    # disconnect → CancelledError), mark it as interrupted so
                    # _finalize_stream skips persistence for non-bg streams.
                    if not _stream_completed:
                        state.stream_interrupted = True
                    await _finalize()
                return

            # Background+stream without keep-alive: run the handler as an independent
            # asyncio.Task so that finalization (including subject.complete()) is
            # guaranteed to run even when the original SSE connection is dropped before
            # all events are delivered.  Without this, _live_stream can be abandoned
            # mid-iteration by Starlette (the async-generator finalizer may not fire
            # promptly), leaving GET-replay subscribers blocked on await q.get() forever.
            _SENTINEL_BG = object()
            bg_queue: asyncio.Queue[object] = asyncio.Queue()

            async def _bg_producer_inner() -> None:
                try:
                    async for event in self._process_handler_events(ctx, state, handler_iterator):
                        await bg_queue.put(encode_sse_any_event(event))
                    # Persist-then-yield: resolve the buffered terminal event
                    if state.pending_terminal is not None:
                        record = state.bg_record or _make_ephemeral_record(ctx, state)
                        resolved = await self._persist_and_resolve_terminal(ctx, state, record)
                        await bg_queue.put(encode_sse_any_event(resolved))
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    logger.error(
                        "Background stream producer failed (response_id=%s)",
                        ctx.response_id,
                        exc_info=exc,
                    )
                    state.captured_error = exc
                finally:
                    # Always finalize (includes subject.complete()) — this runs even if
                    # the original POST SSE connection was dropped and _live_stream is
                    # never properly closed by Starlette.
                    await _finalize()
                    await bg_queue.put(_SENTINEL_BG)

            async def _bg_producer() -> None:
                try:
                    # FR-013: Shield the inner producer via asyncio.shield so
                    # that Starlette's anyio cancel-scope cancellation (triggered
                    # by client disconnect) does NOT propagate into the handler.
                    # asyncio.shield() creates a new inner Task whose cancellation
                    # is independent of the outer task.
                    await asyncio.shield(_bg_producer_inner())
                except asyncio.CancelledError:
                    pass  # outer task cancelled by scope; inner task continues

            bg_task = asyncio.create_task(_bg_producer())
            try:
                while True:
                    item = await bg_queue.get()
                    if item is _SENTINEL_BG:
                        break
                    yield item  # type: ignore[misc]
            except Exception:  # pylint: disable=broad-exception-caught
                pass  # SSE connection dropped; bg_task continues independently
            finally:
                # Wait for the handler task so _finalize() has run before we exit.
                # Do NOT cancel it — background+stream must reach a terminal state
                # regardless of client connectivity.
                if not bg_task.done():
                    try:
                        await bg_task
                    except Exception:  # pylint: disable=broad-exception-caught
                        pass
            return

        # --- Keep-alive path: merge handler events with periodic keep-alive comments ---
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
            await _finalize()

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
        handler_iterator = self._create_fn(ctx.parsed, ctx.context, ctx.cancellation_signal)
        # _process_handler_events handles all error paths (B8, S-035, S-015, B11).
        # run_sync only needs to exhaust the generator for state.handler_events side-effects.
        async for _ in self._process_handler_events(ctx, state, handler_iterator):
            pass

        if state.captured_error is not None:
            # Only raise _HandlerError for pre-creation errors (B8) where no
            # terminal lifecycle event has been emitted.  Post-creation errors
            # (S-035, FR-008a) emit response.failed and should complete as
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
            chat_isolation_key=ctx.chat_isolation_key,
        )
        record.set_response_snapshot(generated_models.ResponseObject(response_payload))

        # Always register in runtime state so that cancel/GET can find the record
        # and return the correct status code (e.g., 400 for non-bg cancel).
        # Always register so cancel/GET can find this record.
        await self._runtime_state.add(record)

        if ctx.store:
            # Persist via provider (non-bg sync: single create at terminal state).
            # §3.1: Persistence failure replaces the response body with storage_error.
            try:
                _isolation = ctx.context.isolation if ctx.context else None
                _response_obj = generated_models.ResponseObject(response_payload)
                _history_ids = (
                    await self._provider.get_history_item_ids(
                        ctx.previous_response_id,
                        None,
                        self._runtime_options.default_fetch_history_count,
                        isolation=_isolation,
                    )
                    if ctx.previous_response_id
                    else None
                )
                _resolved_items = await _resolve_input_items_for_persistence(ctx.context, ctx.input_items)
                await self._provider.create_response(
                    _response_obj,
                    _resolved_items,
                    _history_ids,
                    isolation=_isolation,
                )
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
                storage_error_response = _build_failed_response(
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
            chat_isolation_key=ctx.chat_isolation_key,
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
                    )
            except asyncio.CancelledError:
                pass  # event-loop teardown; background work already done

        record.execution_task = asyncio.create_task(_shielded_runner())

        # Wait for handler to emit response.created (or fail).
        # Wait for handler to signal response.created (or fail).
        await record.response_created_signal.wait()

        # If handler failed before emitting any events, return the failed
        # snapshot (status: failed).  Background POST always returns 200 —
        # the failure is reflected in the response status, not the HTTP code.
        if record.response_failed_before_events:
            ctx.span.end(RuntimeError("Handler failed before response.created"))
            return _RuntimeState.to_snapshot(record)

        ctx.span.end(None)
        return _RuntimeState.to_snapshot(record)
