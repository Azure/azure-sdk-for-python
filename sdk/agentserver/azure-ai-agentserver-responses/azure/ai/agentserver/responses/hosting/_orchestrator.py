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

from azure.ai.agentserver.core._platform_headers import (
    PLATFORM_ERROR_TAG,
)  # pylint: disable=import-error,no-name-in-module
from azure.ai.agentserver.core.durable import (
    LastInputIdPreconditionFailed,
    TaskConflictError,
)

from .._options import ResponsesServerOptions
from ..models import _generated as generated_models
from ..models.runtime import (
    CancellationReason,
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
from ..store._base import ResponseAlreadyExistsError, ResponseProviderProtocol, ResponseStreamProviderProtocol
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
from ._event_subject import _ResponseEventSubject
from ._execution_context import _ExecutionContext
from ._runtime_state import _RuntimeState

if TYPE_CHECKING:
    from .._response_context import ResponseContext
    from ..models._generated import AgentReference, CreateResponse


logger = logging.getLogger("azure.ai.agentserver")


def _serialize_for_recovery(value: Any) -> Any:
    """Convert a model or list of models to a JSON-safe representation.

    The durable task input is serialized as JSON. Objects that pass through
    this helper survive a cross-process task re-fire — used by Spec 013 US1(a)
    reconstruction.

    :param value: Any object — typically a generated model with ``as_dict``,
        a list of such models, or a plain value.
    :type value: Any
    :returns: A JSON-safe representation (dict, list, str, None, etc.).
    :rtype: Any
    """
    if value is None:
        return None
    if isinstance(value, list):
        return [_serialize_for_recovery(item) for item in value]
    if isinstance(value, dict):
        return dict(value)
    if hasattr(value, "as_dict") and callable(value.as_dict):
        return value.as_dict()
    return value

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
            resolved = (
                await context._get_input_items_for_persistence()
            )  # pylint: disable=protected-access
            if resolved:
                return list(resolved)
            return None
        except Exception:  # pylint: disable=broad-exception-caught
            logger.debug(
                "item_reference resolution failed; falling back to pre-expanded items",
                exc_info=True,
            )
    return list(fallback_items) if fallback_items else None


def _check_first_event_contract(
    normalized: generated_models.ResponseStreamEvent, response_id: str
) -> str | None:
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
                # Client-initiated cancel (POST /cancel) → discard and force cancelled.
                # Steering cancel (new turn queued) → let handler wind down and
                # emit its own terminal status with output items preserved.
                if cancellation_signal.is_set() and record.cancel_requested:
                    if record.status not in (
                        "cancelled",
                        "completed",
                        "failed",
                        "incomplete",
                    ):
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
                    record.set_response_snapshot(
                        generated_models.ResponseObject(_initial_snapshot)
                    )
                    # Honour the handler's initial status (e.g. "queued") so the
                    # POST response body reflects what the handler actually set.
                    _handler_initial_status = _initial_snapshot.get("status")
                    if _handler_initial_status == "queued":
                        record.status = "queued"  # type: ignore[assignment]
                    # Persist at response.created time for bg+store (FR-003)
                    if store and provider is not None:
                        try:
                            _isolation = context.isolation if context else None
                            _response_obj = generated_models.ResponseObject(
                                _initial_snapshot
                            )
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
                            _resolved_items = (
                                await _resolve_input_items_for_persistence(
                                    context, record.input_items
                                )
                            )
                            await provider.create_response(
                                _response_obj,
                                _resolved_items,
                                _history_ids,
                                isolation=_isolation,
                            )
                            _provider_created = True
                        except ResponseAlreadyExistsError:
                            # Recovery: response was persisted by a prior attempt.
                            # The terminal update_response is the next write;
                            # nothing else to do here. (Spec 013 US1 deliverable (b).)
                            logger.info(
                                "Response %s already exists in store (recovery — swallowed by idempotent create).",
                                response_id,
                            )
                            _provider_created = True
                        except (
                            Exception
                        ) as persist_exc:  # pylint: disable=broad-exception-caught
                            # §3.3: Phase 1 create failure — mark persistence failed
                            # so the terminal update knows not to attempt update_response.
                            setattr(persist_exc, PLATFORM_ERROR_TAG, True)
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
                    _item_added = (
                        generated_models.ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_ADDED
                    )
                    if normalized.get("type") == _item_added.value:
                        output_item_count += 1

                    # FR-008a: detect direct Output manipulation on response.* events
                    n_type = normalized.get("type", "")
                    if n_type in _RESPONSE_SNAPSHOT_TYPES:
                        n_response = normalized.get("response") or {}
                        n_output = n_response.get("output")
                        if (
                            isinstance(n_output, list)
                            and len(n_output) > output_item_count
                        ):
                            raise ValueError(
                                f"Output item count mismatch "
                                f"({len(n_output)} vs {output_item_count} output_item.added events)"
                            )
        except asyncio.CancelledError:
            # S-024: Distinguish known cancellation (cancel_signal set) from
            # unknown.  Known cancellation → check reason to determine status.
            if cancellation_signal.is_set():
                _ctx_reason = context.cancellation_reason if context else None
                if record.status not in (
                    "cancelled",
                    "completed",
                    "failed",
                    "incomplete",
                ):
                    if _ctx_reason == CancellationReason.CLIENT_CANCELLED or record.cancel_requested:
                        record.transition_to("cancelled")
                    elif _ctx_reason == CancellationReason.SHUTTING_DOWN:
                        # Durable+bg: leave in_progress for re-entry.
                        # Non-durable: mark failed.
                        _is_durable_bg = (
                            runtime_options is not None
                            and runtime_options.durable_background
                            and record.mode_flags.store
                            and record.mode_flags.background
                        )
                        if not _is_durable_bg:
                            record.transition_to("failed")
                    else:
                        # STEERED or unknown — mark failed.
                        record.transition_to("failed")
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

        # Client-initiated cancel: force cancelled status.
        # Steering cancel: handler already emitted events with its chosen
        # terminal status — fall through to normal event extraction.
        if cancellation_signal.is_set() and record.cancel_requested:
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
            record.set_response_snapshot(
                generated_models.ResponseObject(response_payload)
            )
            target = (
                resolved_status if isinstance(resolved_status, str) else "completed"
            )
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
        if (
            store
            and provider is not None
            and record.status not in {"cancelled"}
            and record.response is not None
        ):
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
                        await provider.update_response(
                            record.response, isolation=_isolation
                        )
                    else:
                        # Response was never created (handler yielded nothing or
                        # failed before response.created) — create instead of update.
                        _resolved_items = await _resolve_input_items_for_persistence(
                            context, record.input_items
                        )
                        await provider.create_response(
                            record.response, _resolved_items, None, isolation=_isolation
                        )
                except (
                    Exception
                ) as persist_exc:  # pylint: disable=broad-exception-caught
                    setattr(persist_exc, PLATFORM_ERROR_TAG, True)
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
        if (
            runtime_state is not None
            and record.is_terminal
            and not record.persistence_failed
        ):
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


def _make_ephemeral_record(
    ctx: "_ExecutionContext", state: "_PipelineState"
) -> "ResponseExecution":
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
        mode_flags=ResponseModeFlags(
            stream=True, store=ctx.store, background=ctx.background
        ),
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
        "pre_subject",
    )

    def __init__(self) -> None:
        self.handler_events: list[generated_models.ResponseStreamEvent] = []
        self.bg_record: ResponseExecution | None = None
        self.captured_error: BaseException | None = None
        self.validator: EventStreamValidator = EventStreamValidator()
        self.stream_interrupted: bool = False
        self.pending_terminal: generated_models.ResponseStreamEvent | None = None
        self.provider_created: bool = False
        # (Spec 014 FR-002) Optional pre-allocated subject created by the
        # durable-streaming caller. When set, ``_register_bg_execution`` uses
        # this subject on the freshly created record instead of constructing
        # a new one, so the wire iterator (which subscribed to this exact
        # subject before the durable body started) receives every event.
        self.pre_subject: "_ResponseEventSubject | None" = None


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
        :param stream_provider: Optional provider for SSE stream event persistence and replay.
        :type stream_provider: ResponseStreamProviderProtocol | None
        """
        self._create_fn = create_fn
        self._runtime_state = runtime_state
        self._runtime_options = runtime_options
        self._provider = provider
        self._stream_provider = stream_provider
        self._acceptance_hook = acceptance_hook

        # If the stream provider supports incremental persistence (durable streaming),
        # keep a typed reference for the _normalize_and_append hot path.
        from ..store._base import (
            DurableStreamProviderProtocol,
        )  # pylint: disable=import-outside-toplevel

        self._durable_stream_provider: DurableStreamProviderProtocol | None = (
            stream_provider
            if runtime_options.durable_background
            and isinstance(stream_provider, DurableStreamProviderProtocol)
            else None
        )

        # Eagerly create the durable orchestrator so the @task function
        # is registered in _REGISTERED_DESCRIPTORS before TaskManager.startup()
        # runs recovery. Without this, stale tasks from a previous crash would
        # not be recovered until the first HTTP request triggers lazy creation.
        if runtime_options.durable_background:
            from ._durable_orchestrator import (
                DurableResponseOrchestrator,
            )  # pylint: disable=import-outside-toplevel

            self._durable_orchestrator = DurableResponseOrchestrator(
                create_fn=create_fn,
                options=runtime_options,
                provider=provider,
                runtime_state=runtime_state,
                parent_orchestrator=self,
            )

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
            if (
                state.bg_record.subject is not None
                and normalized.get("type") not in self._TERMINAL_SSE_TYPES
            ):
                await state.bg_record.subject.publish(normalized)
            # Incremental persist for durable streaming (FR-032a).
            # Append each event to the durable stream provider as it's produced,
            # enabling crash recovery without waiting for terminal batch save.
            if self._durable_stream_provider is not None:
                try:
                    _isolation = ctx.context.isolation if ctx.context else None
                    await self._durable_stream_provider.append_stream_event(
                        ctx.response_id, normalized, isolation=_isolation
                    )
                except Exception:  # pylint: disable=broad-exception-caught
                    logger.debug(
                        "Incremental stream persist failed (response_id=%s, seq=%s)",
                        ctx.response_id,
                        normalized.get("sequence_number"),
                        exc_info=True,
                    )
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
        return any(
            e["type"] in _ResponseOrchestrator._TERMINAL_SSE_TYPES
            for e in handler_events
        )

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
            "response": _build_cancelled_response(
                ctx.response_id, ctx.agent_reference, ctx.model
            ).as_dict(),
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
                "error": {
                    "code": "server_error",
                    "message": "An internal server error occurred.",
                },
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
            cast(ResponseStatus, resolved_status)
            if isinstance(resolved_status, str)
            else "completed"
        )

        # Guard: if the cancel endpoint already transitioned this record to a
        # terminal state (race between cancel endpoint and B11), skip the
        # transition and return the pending terminal event as-is.
        if record.is_terminal and record.cancel_requested:
            return state.pending_terminal  # type: ignore[return-value]

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
                        await self._provider.update_response(
                            record.response, isolation=_isolation
                        )
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
                        _resolved_items = await _resolve_input_items_for_persistence(
                            ctx.context, ctx.input_items
                        )
                        await self._provider.create_response(
                            generated_models.ResponseObject(response_payload),
                            _resolved_items,
                            _history_ids,
                            isolation=_isolation,
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
                        await self._provider.update_response(
                            record.response, isolation=_isolation
                        )
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
                except (
                    Exception
                ) as persist_exc:  # pylint: disable=broad-exception-caught
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

        # Publish the resolved terminal event to the subject for replay subscribers.
        # This is deferred from _normalize_and_append to ensure subscribers see the
        # correct terminal (original on success, storage_error replacement on failure).
        if (
            state.bg_record is not None
            and state.bg_record.subject is not None
            and state.pending_terminal is not None
        ):
            await state.bg_record.subject.publish(state.pending_terminal)

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

        (Spec 014 FR-002 — close divergence 1) When the durable streaming
        caller pre-allocated a ``_ResponseEventSubject`` (``state.pre_subject``
        is set), this method installs THAT subject on the new record rather
        than constructing a fresh one. The wire iterator in
        :meth:`_live_stream` subscribes to the pre-allocated subject before
        the durable body starts, so events published here must reach that
        exact subject for the live wire to see them.

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
            response_context=ctx.context,
            agent_session_id=ctx.agent_session_id,
            conversation_id=ctx.conversation_id,
            chat_isolation_key=ctx.chat_isolation_key,
        )
        execution.set_response_snapshot(
            generated_models.ResponseObject(initial_payload)
        )
        # (Spec 014 FR-002) Honour a pre-allocated subject from the durable
        # streaming caller so the live wire iterator sees published events.
        execution.subject = state.pre_subject or _ResponseEventSubject()
        state.bg_record = execution
        assert state.bg_record.subject is not None
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
            _resolved_items = await _resolve_input_items_for_persistence(
                ctx.context, ctx.input_items
            )
            try:
                await self._provider.create_response(
                    _initial_response_obj,
                    _resolved_items,
                    _history_ids,
                    isolation=_isolation,
                )
                state.provider_created = True
            except ResponseAlreadyExistsError:
                # Recovery: response was persisted by a prior attempt.
                # Swallow and proceed; terminal update_response will fire.
                logger.info(
                    "Response %s already exists in store (recovery — swallowed by idempotent create at bg+stream first-event).",
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
        # Publish the first event AFTER persistence has been attempted. This
        # ensures replay subscribers (and the live wire iterator on the
        # durable streaming path) never observe ``response.created`` when
        # Phase 1 create_response failed — matching the contract requirement
        # that no ``response.created`` precedes the standalone error event.
        if not execution.persistence_failed:
            await state.bg_record.subject.publish(first_normalized)

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
                # (Spec 014 FR-002) When a pre-allocated subject is present
                # (durable streaming path), publish fallback events to it so
                # the live wire iterator subscribed on the other side sees
                # them. Without this the synthesised lifecycle for an empty
                # handler would never reach the wire.
                if state.pre_subject is not None:
                    try:
                        await state.pre_subject.publish(event)
                    except Exception:  # pylint: disable=broad-exception-caught
                        pass  # best effort — subject is for replay, not transport
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
                state.captured_error = (
                    state.bg_record.persistence_exception
                    or RuntimeError("Phase 1 create failed")
                )
                # Evict the in-memory record so GET/replay cannot observe an
                # in-progress response when §3.3 requires no response.created.
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
                # (Spec 014 FR-002) Publish the storage_error event to
                # state.pre_subject when set so the live wire iterator on the
                # durable streaming path receives it. ``_register_bg_execution``
                # deliberately did NOT publish ``response.created`` when
                # persistence_failed is True, so this is the only event the
                # wire will see for the failed phase-1 create.
                if state.pre_subject is not None:
                    try:
                        await state.pre_subject.publish(error_event)
                    except Exception:  # pylint: disable=broad-exception-caught
                        pass
                yield error_event
                return

        yield first_normalized

        # --- Remaining events ---
        output_item_count = 0
        try:
            async for raw in _iter_with_winddown(
                handler_iterator, ctx.cancellation_signal
            ):
                # FR-008a: Pre-check for output manipulation BEFORE validation.
                # Must inspect the raw event first so that an offending terminal
                # event (e.g. response.completed with manipulated output) is NOT
                # appended to the state machine before we emit response.failed.
                _pre_coerced = _coerce_handler_event(raw)
                _pre_type = _pre_coerced.get("type", "")
                if (
                    _pre_type
                    == generated_models.ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_ADDED.value
                ):
                    output_item_count += 1
                if _pre_type in _RESPONSE_SNAPSHOT_TYPES:
                    _pre_response = _pre_coerced.get("response") or {}
                    _pre_output = _pre_response.get("output")
                    if (
                        isinstance(_pre_output, list)
                        and len(_pre_output) > output_item_count
                    ):
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
                        state.pending_terminal = await self._make_failed_event(
                            ctx, state
                        )
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
                    state.pending_terminal = await self._cancel_terminal_sse_dict(
                        ctx, state
                    )
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

        # B11: Handler returned without a terminal event while cancellation
        # signal is set. The terminal status depends on the cancellation reason:
        #
        # - SHUTTING_DOWN + durable+background: leave in_progress for re-entry
        #   on restart — do NOT emit a terminal event.
        # - SHUTTING_DOWN + other: emit response.failed.
        # - STEERED: emit response.failed (developer should have emitted
        #   terminal but didn't — framework prevents orphan responses).
        # - CLIENT_CANCELLED: emit response.cancelled (explicit cancel).
        # - None / client disconnect: emit response.failed.
        #
        # "cancelled" status is reserved exclusively for explicit /cancel API
        # calls or client disconnect on non-background create calls.
        if ctx.cancellation_signal.is_set() and not self._has_terminal_event(
            state.handler_events
        ):
            _reason = ctx.context.cancellation_reason if ctx.context else None
            if _reason == CancellationReason.SHUTTING_DOWN:
                # For durable+background, leave response in_progress for
                # re-entry. Don't emit terminal — just return.
                if ctx.background and ctx.store and self._runtime_options.durable_background:
                    return
                state.pending_terminal = await self._make_failed_event(ctx, state)
            elif _reason == CancellationReason.CLIENT_CANCELLED:
                state.pending_terminal = await self._cancel_terminal_sse_dict(ctx, state)
            else:
                # STEERED, client disconnect, or unknown — mark failed.
                state.pending_terminal = await self._make_failed_event(ctx, state)
            return

        # S-015: handler completed normally but never emitted a terminal event.
        # NOTE: state.captured_error intentionally left None so that synchronous
        # callers return HTTP 200 with a "failed" body rather than HTTP 500.
        if not self._has_terminal_event(state.handler_events):
            state.pending_terminal = await self._make_failed_event(ctx, state)

    async def _finalize_stream(
        self, ctx: _ExecutionContext, state: _PipelineState
    ) -> None:
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
            if (
                record.status != "cancelled"
                and self._stream_provider is not None
                and state.handler_events
            ):
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
                # Mark terminal on the durable stream provider — starts TTL countdown
                if self._durable_stream_provider is not None:
                    try:
                        await self._durable_stream_provider.mark_terminal(
                            ctx.response_id, isolation=_isolation
                        )
                    except Exception:  # pylint: disable=broad-exception-caught
                        logger.debug(
                            "mark_terminal failed (response_id=%s)",
                            ctx.response_id,
                            exc_info=True,
                        )
            elif (
                record.status == "cancelled"
                and self._durable_stream_provider is not None
            ):
                # Cancelled responses: clean up any incrementally-persisted events
                # so that SSE replay correctly returns 400 (no stream available).
                _isolation = ctx.context.isolation if ctx.context else None
                try:
                    await self._durable_stream_provider.delete_stream_events(
                        ctx.response_id, isolation=_isolation
                    )
                except Exception:  # pylint: disable=broad-exception-caught
                    logger.debug(
                        "Cancelled stream cleanup failed (response_id=%s)",
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

        # B17: Non-bg streaming cancelled by client disconnect.
        # Per container spec Rule B17: if store=true, the cancelled response
        # becomes retrievable once the cancellation completes. Build a cancelled
        # response and persist it directly.
        if not ctx.background and state.stream_interrupted:
            if not ctx.store:
                # store=false: nothing to persist, GET returns 404 per B17.
                ctx.span.end(state.captured_error)
                return
            # store=true: build and persist a cancelled response directly.
            response_payload: dict[str, Any] = {
                "id": ctx.response_id,
                "status": "cancelled",
                "output": [],
                "background": ctx.background,
            }
            if ctx.model:
                response_payload["model"] = ctx.model
            if ctx.conversation_id:
                response_payload["conversation_id"] = ctx.conversation_id
            if ctx.agent_session_id:
                response_payload["agent_session_id"] = ctx.agent_session_id

            # Persist via provider
            _isolation = ctx.context.isolation if ctx.context else None
            try:
                await self._provider.create_response(
                    response_payload,
                    input_items=ctx.parsed.input if isinstance(ctx.parsed.input, list) else [],
                    history_ids=None,
                    isolation=_isolation,
                )
            except Exception:  # pylint: disable=broad-exception-caught
                logger.warning(
                    "B17: Failed to persist cancelled foreground response (response_id=%s)",
                    ctx.response_id,
                    exc_info=True,
                )
                # Register in runtime state as fallback so GET returns correct status
                record = _make_ephemeral_record(ctx, state)
                record.transition_to("cancelled")
                record.set_response_snapshot(response_payload)
                await self._runtime_state.register_execution(ctx.response_id, record)
                ctx.span.end(state.captured_error)
                return

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
            cast(ResponseStatus, resolved_status)
            if isinstance(resolved_status, str)
            else "completed"
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
            mode_flags=ResponseModeFlags(
                stream=True, store=ctx.store, background=ctx.background
            ),
            status=final_status,
            subject=replay_subject,
            input_items=deepcopy(ctx.input_items),
            previous_response_id=ctx.previous_response_id,
            cancel_signal=ctx.cancellation_signal if ctx.background else None,
            agent_session_id=ctx.agent_session_id,
            conversation_id=ctx.conversation_id,
            chat_isolation_key=ctx.chat_isolation_key,
        )
        execution.set_response_snapshot(
            generated_models.ResponseObject(response_payload)
        )
        # Copy persistence_failed from the ephemeral record if one was used
        if state.bg_record is not None:
            execution.persistence_failed = state.bg_record.persistence_failed
            execution.persistence_exception = state.bg_record.persistence_exception
        await self._runtime_state.add(execution)

        # Persist SSE events for replay after eager eviction (bg+stream only).
        if (
            ctx.background
            and ctx.store
            and self._stream_provider is not None
            and events
        ):
            _isolation = ctx.context.isolation if ctx.context else None
            try:
                await self._stream_provider.save_stream_events(
                    ctx.response_id, events, isolation=_isolation
                )
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
        logger.info(
            "Invoking handler %s for response %s", _handler_name, ctx.response_id
        )
        handler_iterator = self._create_fn(
            ctx.parsed, ctx.context, ctx.cancellation_signal
        )

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
                    async for event in self._process_handler_events(
                        ctx, state, handler_iterator
                    ):
                        yield encode_sse_any_event(event)
                    _stream_completed = True
                    # Persist-then-yield: resolve the buffered terminal event
                    if state.pending_terminal is not None:
                        record = state.bg_record or _make_ephemeral_record(ctx, state)
                        resolved = await self._persist_and_resolve_terminal(
                            ctx, state, record
                        )
                        yield encode_sse_any_event(resolved)
                finally:
                    # B17: If the stream did not complete naturally (e.g. client
                    # disconnect → CancelledError), mark it as interrupted.
                    if not _stream_completed:
                        state.stream_interrupted = True
                    # B17: When store=true and stream was interrupted by client
                    # disconnect, we must persist the cancelled response. Use
                    # asyncio.shield so the finalize coroutine survives task
                    # cancellation (Hypercorn cancels the generator task on
                    # client disconnect).
                    if not _stream_completed and ctx.store:
                        try:
                            await asyncio.shield(_finalize())
                        except asyncio.CancelledError:
                            pass  # finalize continues in shielded task
                    else:
                        await _finalize()
                return

            # Background+stream without keep-alive: run the handler as an independent
            # asyncio.Task so that finalization (including subject.complete()) is
            # guaranteed to run even when the original SSE connection is dropped before
            # all events are delivered.  Without this, _live_stream can be abandoned
            # mid-iteration by Starlette (the async-generator finalizer may not fire
            # promptly), leaving GET-replay subscribers blocked on await q.get() forever.
            #
            # (Spec 014 FR-002 — close divergence 1)
            # When durable_background=True AND store=True AND background=True, route
            # the handler execution through _start_durable_background so the durable
            # task primitive wraps it (handler is re-invokable on crash). The wire
            # iterator subscribes to record.subject (created lazily inside
            # _process_handler_events as the durable body drives events through the
            # streaming pipeline). On crash recovery, the durable scanner re-invokes
            # the body; reconnecting clients see events via GET ?stream=true&starting_after=N.
            if self._runtime_options.durable_background and ctx.store:
                # (Spec 014 FR-002) Pre-allocate the subject the wire iterator
                # will subscribe to. The durable body's _register_bg_execution
                # will install this same subject on the freshly-created record
                # (via state.pre_subject), so events published there are
                # observed here in real time.
                #
                # We do NOT pre-register a record in runtime_state — that
                # would conflict with _finalize_stream's record-replacement
                # logic. Instead, we share only the subject; the record is
                # created exactly once, by _register_bg_execution, when the
                # first handler event arrives.
                wire_subject = _ResponseEventSubject()
                state.pre_subject = wire_subject

                async def _durable_stream_fallback() -> None:
                    # Non-durable fallback runner if _start_durable_background's
                    # internal try/except falls through. Uses the same
                    # _process_handler_events pipeline as the durable body so
                    # the events written to state.pre_subject still reach the
                    # live wire iterator on this side.
                    try:
                        async for _event in self._process_handler_events(
                            ctx, state, handler_iterator
                        ):
                            pass
                        if state.pending_terminal is not None:
                            had_bg_record = state.bg_record is not None
                            r = state.bg_record or _make_ephemeral_record(
                                ctx, state
                            )
                            resolved = await self._persist_and_resolve_terminal(
                                ctx, state, r
                            )
                            # Always publish the resolved terminal to the
                            # pre-allocated wire subject. _persist_and_resolve_terminal
                            # only publishes to state.bg_record.subject under
                            # certain conditions (cancel-race short-circuit
                            # skips it, and ephemeral records have no subject
                            # at all). The live wire iterator subscribed to
                            # ``wire_subject`` MUST receive the terminal
                            # before subject.complete() fires.
                            try:
                                # Avoid double-publish if r.subject IS the
                                # wire subject and _persist_and_resolve_terminal
                                # already published.
                                already_published = (
                                    had_bg_record
                                    and r.subject is wire_subject
                                    and not (r.is_terminal and r.cancel_requested)
                                )
                                if not already_published:
                                    await wire_subject.publish(resolved)
                            except Exception:  # pylint: disable=broad-exception-caught
                                pass
                    finally:
                        await self._finalize_stream(ctx, state)
                        # The pre-allocated wire_subject is independent of
                        # state.bg_record.subject. Always complete it so the
                        # wire iterator exits.
                        try:
                            await wire_subject.complete()
                        except Exception:  # pylint: disable=broad-exception-caught
                            pass  # best effort (idempotent if already completed)

                # Construct a minimal record only for _start_durable_background's
                # parameter shape. This record is NOT added to runtime_state —
                # the durable body (or fallback) will create the canonical
                # record via _register_bg_execution.
                start_record = ResponseExecution(
                    response_id=ctx.response_id,
                    mode_flags=ResponseModeFlags(
                        stream=True, store=True, background=True
                    ),
                    status="in_progress",
                    input_items=deepcopy(ctx.input_items),
                    previous_response_id=ctx.previous_response_id,
                    cancel_signal=ctx.cancellation_signal,
                    response_context=ctx.context,
                    agent_session_id=ctx.agent_session_id,
                    conversation_id=ctx.conversation_id,
                    chat_isolation_key=ctx.chat_isolation_key,
                    initial_model=ctx.model,
                    initial_agent_reference=ctx.agent_reference,
                )
                start_record.subject = wire_subject

                await self._start_durable_background(
                    ctx, start_record, _durable_stream_fallback
                )

                try:
                    async for event in wire_subject.subscribe(cursor=-1):
                        yield encode_sse_any_event(event)
                except Exception:  # pylint: disable=broad-exception-caught
                    pass  # wire dropped; durable body continues
                return

            _SENTINEL_BG = object()
            bg_queue: asyncio.Queue[object] = asyncio.Queue()

            async def _bg_producer_inner() -> None:
                try:
                    async for event in self._process_handler_events(
                        ctx, state, handler_iterator
                    ):
                        await bg_queue.put(encode_sse_any_event(event))
                    # Persist-then-yield: resolve the buffered terminal event
                    if state.pending_terminal is not None:
                        record = state.bg_record or _make_ephemeral_record(ctx, state)
                        resolved = await self._persist_and_resolve_terminal(
                            ctx, state, record
                        )
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
                async for event in self._process_handler_events(
                    ctx, state, handler_iterator
                ):
                    await merge_queue.put(encode_sse_any_event(event))
                # Persist-then-yield: resolve the buffered terminal event
                if state.pending_terminal is not None:
                    record = state.bg_record or _make_ephemeral_record(ctx, state)
                    resolved = await self._persist_and_resolve_terminal(
                        ctx, state, record
                    )
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
        logger.info(
            "Invoking handler %s for response %s", _handler_name, ctx.response_id
        )
        handler_iterator = self._create_fn(
            ctx.parsed, ctx.context, ctx.cancellation_signal
        )
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
        status = (
            cast(ResponseStatus, resolved_status)
            if isinstance(resolved_status, str)
            else "completed"
        )

        record = ResponseExecution(
            response_id=ctx.response_id,
            mode_flags=ResponseModeFlags(
                stream=False, store=ctx.store, background=False
            ),
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
                _resolved_items = await _resolve_input_items_for_persistence(
                    ctx.context, ctx.input_items
                )
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

        When ``durable_background=True`` in server options, execution is
        wrapped in the durable task primitive for crash recovery.

        :param ctx: Current execution context.
        :type ctx: _ExecutionContext
        :return: Response snapshot dictionary (status: in_progress).
        :rtype: dict[str, Any]
        :raises _HandlerError: If the handler fails before emitting ``response.created``.
        """
        record = ResponseExecution(
            response_id=ctx.response_id,
            mode_flags=ResponseModeFlags(
                stream=False, store=ctx.store, background=True
            ),
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
                        runtime_options=self._runtime_options,
                    )
            except asyncio.CancelledError:
                pass  # event-loop teardown; background work already done

        if self._runtime_options.durable_background and ctx.store:
            # Durable path: wrap execution in a task primitive for crash recovery.
            # The task body calls _run_background_non_stream with the same params.
            await self._start_durable_background(ctx, record, _shielded_runner)
        else:
            # Non-durable path: plain asyncio task (existing behavior)
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
                context=ctx.context,
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

    async def _run_durable_stream_body(
        self,
        *,
        parsed: "CreateResponse",
        context: "ResponseContext",
        cancellation_signal: asyncio.Event,
        record: ResponseExecution,
        response_id: str,
        agent_reference: Any,
        model: str | None,
        store: bool,
        agent_session_id: str | None,
        conversation_id: str | None,
    ) -> None:
        """Durable task body for streaming responses (Spec 014 FR-002 — divergence 1).

        Called from ``DurableResponseOrchestrator._execute_in_task`` when
        ``params["stream"]`` is True. Drives the handler through the streaming
        pipeline (``_process_handler_events``) which writes events to:

        - ``record.subject`` — the in-memory pub/sub the live wire iterator
          subscribes to.
        - ``self._durable_stream_provider`` — the persisted store used by
          GET ``/responses/{id}?stream=true&starting_after=N`` reconnect
          (incl. crash recovery).

        On fresh entry: a live wire connection exists; the wire iterator in
        ``_live_stream``'s bg+store branch subscribes to ``record.subject``
        and yields encoded SSE events as they arrive.

        On recovered entry: no wire connection (prior lifetime is dead). The
        handler still runs and events still get persisted; reconnecting
        clients see the events via the GET reconnect endpoint.

        :keyword parsed: The parsed ``CreateResponse`` for this request.
        :keyword context: The handler's :class:`ResponseContext`.
        :keyword cancellation_signal: Per-request cancellation event
            (already bridged from ``ctx.cancel`` / ``ctx.shutdown`` by the
            durable orchestrator).
        :keyword record: The :class:`ResponseExecution` (already registered
            with ``runtime_state`` by the orchestrator).
        :keyword response_id: The response identifier.
        :keyword agent_reference: Resolved agent reference for this request.
        :keyword model: The model name (or ``None``).
        :keyword store: Whether the response should be persisted (always
            True for the durable streaming path — we wouldn't be here
            otherwise).
        :keyword agent_session_id: Resolved agent session id.
        :keyword conversation_id: Optional conversation id.
        """
        # Build a minimal _ExecutionContext for the streaming pipeline. The
        # pipeline only reads a handful of fields from ctx; we don't need
        # the original span (which lived on the wire-request side and may
        # already be ended by the time the durable body runs).
        from ._observability import (  # pylint: disable=import-outside-toplevel
            CreateSpan,
        )

        synthetic_span = CreateSpan(
            name="responses.durable_stream_body",
            tags={"response.id": response_id},
        )
        ctx = _ExecutionContext(
            response_id=response_id,
            agent_reference=agent_reference,
            model=model,
            store=store,
            background=True,
            stream=True,
            input_items=list(record.input_items or []),
            previous_response_id=record.previous_response_id,
            conversation_id=conversation_id,
            cancellation_signal=cancellation_signal,
            span=synthetic_span,
            parsed=parsed,
            agent_session_id=agent_session_id,
            context=context,
        )

        state = _PipelineState()
        # (Spec 014 FR-002) The wire iterator on _live_stream's side
        # subscribed to ``record.subject`` BEFORE this body started. Pass it
        # through state.pre_subject so _register_bg_execution installs the
        # SAME subject on the canonical record it creates.
        state.pre_subject = record.subject
        handler_iterator = self._create_fn(parsed, context, cancellation_signal)

        # Drive the streaming pipeline. Events flow to record.subject (live
        # wire iterator subscribes to it) and to self._durable_stream_provider
        # (for GET reconnect). _process_handler_events handles terminal
        # events, fallback events, error signalling.
        try:
            async for _event in self._process_handler_events(
                ctx, state, handler_iterator
            ):
                # Events are published to subject + provider inside
                # _process_handler_events; we only need to drain the
                # generator. The wire iterator on _live_stream's side
                # consumes from record.subject independently.
                pass

            # Persist-then-yield resolution for the terminal event.
            if state.pending_terminal is not None:
                had_bg_record = state.bg_record is not None
                r = state.bg_record or _make_ephemeral_record(ctx, state)
                resolved = await self._persist_and_resolve_terminal(ctx, state, r)
                # Always publish the resolved terminal to the pre-allocated
                # wire subject. _persist_and_resolve_terminal only publishes
                # under specific conditions (skipped on cancel-race short
                # circuit; ephemeral records have no subject). The live wire
                # iterator on _live_stream's side MUST observe the terminal
                # before subject.complete fires.
                if record.subject is not None:
                    try:
                        already_published = (
                            had_bg_record
                            and r.subject is record.subject
                            and not (r.is_terminal and r.cancel_requested)
                        )
                        if not already_published:
                            await record.subject.publish(resolved)
                    except Exception:  # pylint: disable=broad-exception-caught
                        pass
        finally:
            # Ensure finalization runs on every exit path (handler error,
            # cancellation, normal completion). Same as _live_stream's
            # finally for bg+store path.
            try:
                await self._finalize_stream(ctx, state)
            except Exception:  # pylint: disable=broad-exception-caught
                logger.warning(
                    "_finalize_stream failed for durable streaming body "
                    "response_id=%s",
                    response_id,
                    exc_info=True,
                )
            # Always complete the pre-allocated wire subject so the live wire
            # iterator on _live_stream's side exits cleanly. Idempotent if
            # _finalize_stream already completed the same subject through
            # state.bg_record.
            pre_subject_ref = record.subject
            if pre_subject_ref is not None:
                try:
                    await pre_subject_ref.complete()
                except Exception:  # pylint: disable=broad-exception-caught
                    pass  # best effort

    async def _start_durable_background(
        self,
        ctx: _ExecutionContext,
        record: ResponseExecution,
        fallback_runner: Any,
    ) -> None:
        """Start the durable task-backed background execution.

        For Phase 1, this creates a DurableResponseOrchestrator and starts
        the task. The task body runs _run_background_non_stream inside the
        task primitive, providing crash recovery guarantees.

        Falls back to plain asyncio.create_task if the durable orchestrator
        is not available or the task conflicts (already running).

        :param ctx: Current execution context.
        :param record: The mutable execution record.
        :param fallback_runner: The shielded runner coroutine function to use
            as fallback if durable start fails.
        """
        from ._durable_orchestrator import (
            DurableResponseOrchestrator,
        )  # pylint: disable=import-outside-toplevel

        if not hasattr(self, "_durable_orchestrator"):
            self._durable_orchestrator = DurableResponseOrchestrator(
                create_fn=self._create_fn,
                options=self._runtime_options,
                provider=self._provider,
                runtime_state=self._runtime_state,
                parent_orchestrator=self,
            )

        # Build execution params dict for the task input
        ctx_params: dict[str, Any] = {
            "response_id": ctx.response_id,
            # Object references (not serialized — only valid in same process)
            "_record_ref": record,
            "_context_ref": ctx.context,
            "_parsed_ref": ctx.parsed,
            "_cancel_ref": ctx.cancellation_signal,
            "_runtime_state_ref": self._runtime_state,
            # Serializable params (these survive cross-process recovery)
            "agent_reference": ctx.agent_reference,
            "model": ctx.model,
            "store": ctx.store,
            "agent_session_id": ctx.agent_session_id,
            "conversation_id": ctx.conversation_id,
            "previous_response_id": ctx.previous_response_id,
            "history_limit": self._runtime_options.default_fetch_history_count,
            "agent_name": getattr(self._runtime_options, "agent_name", "default"),
            "session_id": ctx.agent_session_id or "",
            # Spec 013 US1(a) reconstruction support — fields needed to rebuild
            # ResponseExecution, ResponseContext, and the parsed request across
            # a cross-process recovery. None of these touches the existing
            # same-process path (which uses the _*_ref entries above).
            "user_isolation_key": ctx.user_isolation_key,
            "chat_isolation_key": ctx.chat_isolation_key,
            "prefetched_history_ids": ctx.prefetched_history_ids,
            "input_items": _serialize_for_recovery(ctx.input_items),
            "parsed_payload": _serialize_for_recovery(ctx.parsed),
            "stream": ctx.stream,
            "background": ctx.background,
        }

        try:
            freshly_started = await self._durable_orchestrator.start_durable(
                record=record,
                ctx_params=ctx_params,
            )
            if not freshly_started and self._runtime_options.steerable_conversations:
                # Input was queued on already-active steerable task.
                # Signal the record that it should return a "queued" response
                # instead of waiting for handler execution.
                record.input_queued = True  # type: ignore[attr-defined]
                record.response_created_signal.set()
        except TaskConflictError:
            # Conversation already locked — propagate so routing layer
            # can return HTTP 409 (steerable) or fallback (non-steerable).
            if self._runtime_options.steerable_conversations:
                raise
            # Non-steerable: shouldn't happen (distinct task IDs per fork),
            # but fall back gracefully just in case.
            logger.warning(
                "Unexpected TaskConflictError for non-steerable response %s; falling back",
                ctx.response_id,
            )
            record.execution_task = asyncio.create_task(fallback_runner())
        except LastInputIdPreconditionFailed:
            # (Spec 013 US2) Steerable conversations enforce sequential
            # `previous_response_id`. Propagate so the endpoint layer
            # surfaces HTTP 409 `conversation_fork_not_supported`.
            raise
        except Exception:  # pylint: disable=broad-exception-caught
            # Durable start failed — fall back to non-durable execution
            logger.warning(
                "Durable task start failed for response %s; falling back to asyncio.create_task",
                ctx.response_id,
                exc_info=True,
            )
            record.execution_task = asyncio.create_task(fallback_runner())
