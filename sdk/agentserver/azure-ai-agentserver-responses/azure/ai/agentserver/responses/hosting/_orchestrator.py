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
import json
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
)
from ..models.runtime import (
    build_cancelled_response as _build_cancelled_response,
)
from ..models.runtime import (
    build_failed_response as _build_failed_response,
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
# Used by  output manipulation detection.
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


def _is_durable_background(runtime_options: "ResponsesServerOptions | None", *, store: bool, background: bool) -> bool:
    """Return True for a durable background response (the only checkpoint consumer).

    :param runtime_options: Server runtime options.
    :type runtime_options: ResponsesServerOptions | None
    :keyword store: Whether the response is stored.
    :paramtype store: bool
    :keyword background: Whether the response is background.
    :paramtype background: bool
    :returns: True iff ``durable_background`` is enabled and the response is a
        stored background response.
    :rtype: bool
    """
    return bool(
        runtime_options is not None and getattr(runtime_options, "durable_background", False) and store and background
    )


async def _do_checkpoint_persist(
    event: ResponseCheckpointEvent,
    *,
    provider: "ResponseProviderProtocol | None",
    runtime_options: "ResponsesServerOptions | None",
    store: bool,
    background: bool,
    isolation: Any,
    response_id: str,
    last_snapshot: "bytes | None",
    terminal_seen: bool,
) -> "bytes | None":
    """Durably persist a developer checkpoint snapshot (spec 025 §A.3).

    Shared by both handler-draining paths. Persists only for durable background
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
    :keyword isolation: Tenant isolation context for the provider write.
    :paramtype isolation: Any
    :keyword response_id: The response id (for logging).
    :paramtype response_id: str
    :keyword last_snapshot: Serialised bytes of the previously persisted snapshot.
    :paramtype last_snapshot: bytes | None
    :keyword terminal_seen: Whether a terminal event has already been processed.
    :paramtype terminal_seen: bool
    :returns: The new ``last_snapshot`` bytes (unchanged when nothing persisted).
    :rtype: bytes | None
    """
    if not _is_durable_background(runtime_options, store=store, background=background):
        logger.debug("checkpoint() no-op (not a durable background response) for %s", response_id)
        return last_snapshot
    if terminal_seen:
        logger.debug("checkpoint() after terminal dropped for %s", response_id)
        return last_snapshot
    response = event.response
    if response is None or provider is None:
        return last_snapshot
    try:
        snapshot_bytes = json.dumps(response.as_dict(), sort_keys=True, default=str).encode("utf-8")
    except Exception:  # pylint: disable=broad-exception-caught
        logger.debug("checkpoint() snapshot serialisation failed for %s", response_id, exc_info=True)
        return last_snapshot
    if snapshot_bytes == last_snapshot:
        return last_snapshot  # idempotent — nothing changed since the last checkpoint
    try:
        await provider.update_response(response, isolation=isolation)
        return snapshot_bytes
    except Exception as exc:  # pylint: disable=broad-exception-caught
        setattr(exc, PLATFORM_ERROR_TAG, True)
        logger.error("checkpoint persist failed (response_id=%s): %s", response_id, exc, exc_info=True)
        return last_snapshot


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
    # Spec 025 §A.3: developer checkpoint state for this background execution.
    _checkpoint_last_snapshot: bytes | None = None
    _terminal_seen = False
    # Spec 025 §A.4: when the handler defers to next-lifetime recovery via
    # ``await context.exit_for_recovery()``, the last checkpoint snapshot is
    # the durable state — the finalization persistence below MUST NOT
    # overwrite it with the pre-terminal ``record.response``.
    _exit_for_recovery = False

    try:
        try:
            async for handler_event in _iter_with_winddown(
                create_fn(parsed, context, cancellation_signal), cancellation_signal
            ):
                # Intercept developer ``stream.checkpoint()`` events (spec 025
                # §A.3): durably persist (durable background only) and never
                # forward them into the event pipeline.
                if isinstance(handler_event, ResponseCheckpointEvent):
                    _checkpoint_last_snapshot = await _do_checkpoint_persist(
                        handler_event,
                        provider=provider,
                        runtime_options=runtime_options,
                        store=store,
                        background=record.mode_flags.background,
                        isolation=context.isolation,
                        response_id=response_id,
                        last_snapshot=_checkpoint_last_snapshot,
                        terminal_seen=_terminal_seen,
                    )
                    continue
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
                if normalized.get("type") in _ResponseOrchestrator._TERMINAL_SSE_TYPES:
                    _terminal_seen = True
                if not first_event_processed:
                    first_event_processed = True

                    #: output manipulation detection on response.created
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
                    # Persist at response.created time for bg+store
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
                        except Exception as persist_exc:  # pylint: disable=broad-exception-caught
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
                    # Track output_item.added events
                    _item_added = generated_models.ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_ADDED
                    if normalized.get("type") == _item_added.value:
                        output_item_count += 1

                    #: detect direct Output manipulation on response.* events
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
            # unknown.  Known cancellation → inspect the new
            # composing-cause flags on ``context`` (spec 024 Phase 5
            # Proposal #11) to determine status.
            if cancellation_signal.is_set():
                _client_cancelled = bool(context.client_cancelled) if context else False
                _shutdown = bool(context.shutdown.is_set()) if context else False
                if record.status not in (
                    "cancelled",
                    "completed",
                    "failed",
                    "incomplete",
                ):
                    if _client_cancelled or record.cancel_requested:
                        record.transition_to("cancelled")
                    elif _shutdown:
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
                        # Steering or unknown — mark failed.
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
        except ResponseExitForRecovery:
            # Spec 025 §A.4: the handler deferred to next-lifetime recovery.
            # Leave the last checkpointed snapshot as the durable state and
            # re-raise so the durable task body performs the recovery
            # translation. The finally block must NOT persist the
            # (pre-terminal) record.response over the checkpoint.
            _exit_for_recovery = True
            record.response_created_signal.set()
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
        # (Spec 024 Phase 2 — bookkeeping unification) If the record was
        # already transitioned to a terminal status concurrently (e.g.
        # by the in-process shutdown marker in
        # ``_endpoint_handler.handle_shutdown``), do NOT override that
        # terminal with the handler's partial event sequence. Attempting
        # ``record.transition_to("in_progress")`` from "failed" raises
        # ``InvalidStatusTransition`` and surfaces as a TaskFailed in
        # the durable task framework. Skip the transition; the shutdown
        # marker's persistence is authoritative.
        _TERMINAL_STATES = {"completed", "failed", "cancelled", "incomplete"}
        if record.status in _TERMINAL_STATES:
            pass  # leave the marker's terminal state intact
        elif record.status != "cancelled":
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
        # Spec 025 §A.4: skip when deferring to recovery — the last checkpoint
        # snapshot is authoritative and must not be clobbered.
        if (
            store
            and provider is not None
            and not _exit_for_recovery
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
                        await provider.update_response(record.response, isolation=_isolation)
                    else:
                        # Response was never created (handler yielded nothing or
                        # failed before response.created) — create instead of update.
                        # Load history items if previous_response_id is set so the
                        # input_items endpoint can return history + current.
                        # (Spec 024 Phase 2 — pre-existing bug surfaced by the
                        # unified Row 3 path which exercises this no-events branch
                        # for handlers like _noop_response_handler.)
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
                            record.response, _resolved_items, _history_ids, isolation=_isolation
                        )
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
        # for a durable_background+store response. Signals the durable
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
        # graceful shutdown right now" — earlier than the durable task
        # framework's ``ctx.shutdown`` event, which only fires once
        # ``TaskManager.shutdown()`` runs (after Hypercorn has begun
        # draining). The race matters for upstream-client failures
        # triggered by SIGTERM propagating through the server's process
        # group: without this signal, the orchestrator would treat them
        # as plain handler exceptions and bake a "failed" terminal,
        # contradicting the durability contract (durable_background
        # responses must remain in_progress for next-lifetime recovery).
        self._shutdown_event: "asyncio.Event | None" = None

        # Eagerly create the durable orchestrator so the @task function
        # is registered in _REGISTERED_DESCRIPTORS before TaskManager.startup()
        # runs recovery. Without this, stale tasks from a previous crash would
        # not be recovered until the first HTTP request triggers lazy creation.
        # Eager creation is unconditional: Rows 2/3 also need recovery
        # dispatch even when ``durable_background=False`` — they use the same
        # @task function with a ``disposition="mark-failed"`` payload that
        # the recovery body honours.
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
        """Close ``stream`` tolerating already-closed / destroyed."""
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
        # Applies to both the ``/cancel`` API endpoint (sets client_cancelled
        # via the cancel handler) and non-bg POST client disconnect (sets
        # client_cancelled via the disconnect monitor). Without this
        # override a handler that emits its own ``completed`` AFTER seeing
        # the cancellation signal would have its terminal honored even
        # though the framework promised ``cancelled`` to the client.
        _client_cancelled = bool(ctx.context.client_cancelled) if ctx.context else False
        if _client_cancelled and status != "cancelled":
            cancelled_response = _build_cancelled_response(
                ctx.response_id,
                ctx.agent_reference,
                ctx.model,
                created_at=ctx.context.created_at if ctx.context else None,
            )
            response_payload = cancelled_response.as_dict()
            response_payload["background"] = ctx.background
            status = "cancelled"
            # Replace state.pending_terminal with the cancel-terminal event so
            # the SSE wire and persistence see the overridden status.
            override_event: dict[str, Any] = {
                "type": generated_models.ResponseStreamEventType.RESPONSE_FAILED.value,
                "response": response_payload,
            }
            state.pending_terminal = await self._normalize_and_append(ctx, state, override_event)

        # Guard: if the cancel endpoint already transitioned this record to a
        # terminal state (race between cancel endpoint and B11), skip the
        # transition. We still emit the pending terminal to the per-response
        # stream below so the live wire iterator (and replay subscribers)
        # see exactly one terminal event.
        cancel_race = bool(record.is_terminal and record.cancel_requested)

        if not cancel_race:
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
                    except ResponseAlreadyExistsError:
                        # Recovery: response was persisted by a prior attempt. Convert
                        # this terminal-side create attempt into an update so the final
                        # state still lands in the store. (Spec 013 US1 deliverable (b).)
                        logger.info(
                            "Response %s already exists in store at terminal create (recovery — switching to update).",
                            ctx.response_id,
                        )
                        try:
                            await self._provider.update_response(record.response, isolation=_isolation)
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
        # now runs inside the durable task body for all store=True rows
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
        (e.g. the live SSE wire iterator in :meth:`_live_stream`'s durable
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
            chat_isolation_key=ctx.chat_isolation_key,
        )
        execution.set_response_snapshot(generated_models.ResponseObject(initial_payload))
        # Bind the per-response stream from the registry — the registry
        # guarantees the same instance for the same id, so any other caller
        # that does ``streams.get_or_create(response_id)`` for this id sees
        # the same fan-out target.
        execution.subject = await streams.get_or_create(ctx.response_id)
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
            _resolved_items = await _resolve_input_items_for_persistence(ctx.context, ctx.input_items)
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
                    _build_failed_response(
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
        # durable streaming path) never observe ``response.created`` when
        # Phase 1 create_response failed — matching the contract requirement
        # that no ``response.created`` precedes the standalone error event.
        if not execution.persistence_failed:
            await self._safe_emit(state.bg_record.subject, first_normalized)

    async def _intercept_checkpoints(
        self,
        ctx: "_ExecutionContext",
        state: "_PipelineState",
        handler_iterator: AsyncIterator[generated_models.ResponseStreamEvent],
    ) -> AsyncIterator[generated_models.ResponseStreamEvent]:
        """Drain the handler, intercepting + persisting ``checkpoint()`` events.

        Checkpoint events are handled here (durable persistence) and are NOT
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
        """Durably persist a developer checkpoint snapshot (spec 025 §A.3).

        Persists only for durable background responses; idempotent; failures are
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
        # Gate: only durable background responses have a recovery re-invocation
        # path, so only they have a consumer for an in-flight checkpoint.
        state.last_persisted_snapshot = await _do_checkpoint_persist(
            event,
            provider=self._provider,
            runtime_options=self._runtime_options,
            store=ctx.store,
            background=ctx.background,
            isolation=ctx.context.isolation if ctx.context is not None else None,
            response_id=ctx.response_id,
            last_snapshot=state.last_persisted_snapshot,
            terminal_seen=state.pending_terminal is not None,
        )

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
        # Intercept developer ``stream.checkpoint()`` events (spec 025 §A.3)
        # BEFORE any coercion/validation/forwarding: they are durably persisted
        # by the orchestrator and never reach the wire or the event taxonomy.
        handler_iterator = self._intercept_checkpoints(ctx, state, handler_iterator)
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
                # Re-stamp with the monotonic ``state.next_seq`` —
                # _build_events stamps seq=0 for every event by default,
                # which breaks the streaming contract that seq must
                # monotonically increase. The ResponseStreamEvent model
                # supports item assignment so we mutate in-place without
                # breaking model identity.
                event["sequence_number"] = state.next_seq
                state.handler_events.append(event)
                state.next_seq += 1
                # For bg+store paths AND unified Row 3 stream (fg+store+stream=T),
                # the canonical record (and its ``subject``) hasn't been
                # registered yet — the synthesised lifecycle bypasses
                # ``_register_bg_execution``. Bind the per-response stream
                # directly so the live wire iterator (subscribed via
                # ``streams.get_or_create(response_id)``) sees the fallback
                # events. Skip terminal here — the caller emits the resolved
                # terminal via _persist_and_resolve_terminal so on persistence
                # failure the storage_error replacement lands instead of the
                # original terminal.
                # (Spec 024 Phase 2) Condition broadened from
                # `ctx.background and ctx.store` to `ctx.store and ctx.stream`
                # so Row 3 stream gets fallback events on wire_stream too.
                if ctx.store and (ctx.background or ctx.stream) and event.get("type") not in self._TERMINAL_SSE_TYPES:
                    _fallback_stream = await streams.get_or_create(ctx.response_id)
                    await self._safe_emit(_fallback_stream, event)
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
            _b8_event = construct_event_model(
                {
                    "type": "error",
                    "message": "An internal server error occurred.",
                    "param": None,
                    "code": None,
                    "sequence_number": 0,
                }
            )
            # (Spec 024 Phase 2) For unified store-stream paths the live
            # wire iterator subscribes to wire_stream, not to the yielded
            # events from this method — also emit the error to wire_stream
            # so the wire iterator sees it.
            if ctx.store and ctx.stream:
                _err_stream = await streams.get_or_create(ctx.response_id)
                await self._safe_emit(_err_stream, _b8_event)
            yield _b8_event
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
            _b30_event = construct_event_model(
                {
                    "type": "error",
                    "message": "An internal server error occurred.",
                    "param": None,
                    "code": None,
                    "sequence_number": 0,
                }
            )
            if ctx.store and ctx.stream:
                _err_stream = await streams.get_or_create(ctx.response_id)
                await self._safe_emit(_err_stream, _b30_event)
            yield _b30_event
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
            _fec_event = construct_event_model(
                {
                    "type": "error",
                    "message": "An internal server error occurred.",
                    "param": None,
                    "code": None,
                    "sequence_number": 0,
                }
            )
            if ctx.store and ctx.stream:
                _err_stream = await streams.get_or_create(ctx.response_id)
                await self._safe_emit(_err_stream, _fec_event)
            yield _fec_event
            return

        state.handler_events.append(first_normalized)
        state.next_seq += 1
        state.validator.validate_next(first_normalized)

        #: output manipulation detection on response.created.
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

        # (Spec 024 Phase 2) bg+store OR fg+store+stream: create and register
        # the execution record after the first event so events fan out to the
        # per-response stream (wire_stream subscribers in _live_stream see
        # them). Pre-Phase-2 only bg+store used this path; unified Row 3
        # stream (fg+store+stream=T) also subscribes to wire_stream and
        # needs the registration.
        if ctx.store and (ctx.background or ctx.stream):
            await self._register_bg_execution(ctx, state, first_normalized)
            # Phase 1 (start) persistence failure splits two ways by
            # request shape:
            #
            # 1. Non-bg streaming (Row 3 stream=true): emit the standard
            #    response.created → response.failed sequence so the SSE
            #    contract (B27 first-event invariant) is respected. The
            #    response.failed envelope carries the storage_error code
            #    so the GET fallback path can synthesise the same shape.
            #
            # 2. Bg+stream (Row 1/2 stream=true): emit a standalone error
            #    event (no response.created). The HTTP request has not
            #    yet returned the queued response object, so swallowing
            #    the failure into a response.failed terminal would
            #    promise persistence the storage layer never delivered.
            #    Clients see the error event and stop; subsequent GETs
            #    return 404.
            if state.bg_record is not None and state.bg_record.persistence_failed:
                state.captured_error = state.bg_record.persistence_exception or RuntimeError("Phase 1 create failed")
                if not ctx.background:
                    # Non-bg streaming: emit response.created → response.failed.
                    storage_error_response = _build_failed_response(
                        ctx.response_id,
                        ctx.agent_reference,
                        ctx.model,
                        created_at=ctx.context.created_at if ctx.context else None,
                        error_code="storage_error",
                        error_message=_STORAGE_ERROR_MESSAGE,
                    )
                    _wire_stream = await streams.get_or_create(ctx.response_id)
                    await self._safe_emit(_wire_stream, first_normalized)
                    yield first_normalized
                    # Build, validate, and APPEND the terminal to
                    # ``state.handler_events`` BEFORE emitting/yielding it.
                    # This closes the window where a generator close after
                    # yield-but-before-append would leave the event list
                    # holding only ``response.created`` —
                    # ``_finalize_stream`` Path B rebuilds the snapshot
                    # from the event list, and would regress
                    # ``status="failed"`` back to ``status="in_progress"``.
                    failed_event = {
                        "type": generated_models.ResponseStreamEventType.RESPONSE_FAILED.value,
                        "response": storage_error_response.as_dict(),
                    }
                    failed_normalized = await self._normalize_and_append(ctx, state, failed_event)
                    # Stamp the in-memory record with the terminal snapshot
                    # + status BEFORE emitting the wire/yield, so a GET that
                    # races the post-yield finalize observes a consistent
                    # ``status=failed error.code=storage_error`` envelope.
                    if state.bg_record is not None:
                        state.bg_record.set_response_snapshot(storage_error_response)
                        state.bg_record.status = "failed"  # type: ignore[assignment]
                    await self._safe_emit(_wire_stream, failed_normalized)
                    yield failed_normalized
                    return
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
                yield error_event
                return

        yield first_normalized

        # --- Remaining events ---
        output_item_count = 0
        try:
            async for raw in _iter_with_winddown(handler_iterator, ctx.cancellation_signal):
                # Pre-check for output manipulation BEFORE validation.
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
            # S-024: Known cancellation. The terminal type depends on
            # the cancellation reason — preserve the same per-reason
            # mapping the B11 (handler-returned-without-terminal) path
            # uses so we don't diverge based on whether the handler
            # raised CancelledError vs. just returned.
            #
            # - SHUTTING_DOWN + durable+background: leave in_progress
            #   so the next-lifetime recovery scanner re-invokes the
            #   handler. Per user-facing contract: durable_background
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
                    if ctx.background and ctx.store and self._runtime_options.durable_background:
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
            # If we are mid-shutdown and the response is a durable+background
            # one, the handler exception is most likely a transient symptom
            # of the SIGTERM itself (e.g. an upstream LLM SDK subprocess
            # being killed in our process group before it could fully
            # start). Convert the exception into a cooperative-cancellation
            # of the durable task body — raise asyncio.CancelledError so
            # the @task framework leaves the task ``status="in_progress"``
            # for next-lifetime recovery instead of writing a "failed"
            # terminal that would orphan any queued steering inputs and
            # prevent the response from making forward progress on a retry.
            #
            # "Mid-shutdown" detection prefers the durable task's
            # composing-cancellation surface (``ctx.context.shutdown``
            # set by the _durable_orchestrator's bridge once
            # ctx.shutdown fires), but ALSO checks the server-level
            # shutdown_event (set as Hypercorn's pre-shutdown callback
            # — fires as soon as the process receives SIGTERM, before
            # TaskManager.shutdown() propagates ctx.shutdown). The
            # server-level signal closes a race where the handler
            # raises in the gap between SIGTERM reaching the process
            # group (which also kills any upstream client subprocesses)
            # and the durable framework's cooperative-shutdown
            # propagation.
            _shutdown = bool(ctx.context.shutdown.is_set()) if ctx.context else False
            _server_shutting_down = self._shutdown_event is not None and self._shutdown_event.is_set()
            if (
                (_shutdown or _server_shutting_down)
                and ctx.background
                and ctx.store
                and self._runtime_options.durable_background
            ):
                # Stamp the shutdown cause so the durable body's
                # FR-005a check (which also looks at ctx.shutdown)
                # routes consistently. Shutdown does NOT fire the
                # cancellation signal — handlers observe shutdown via
                # ``context.shutdown`` and respond with
                # ``exit_for_recovery()`` or a terminal emit.
                if ctx.context is not None and not ctx.context.shutdown.is_set():
                    ctx.context.shutdown.set()
                # Signal the durable-stream-body finally to SKIP the
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
                # (see core durable/_manager.py CancelledError branch:
                # "cancellation is never retried" but task stays
                # in_progress for recovery scanner to pick up).
                raise asyncio.CancelledError()
            # S-035: emit response.failed when handler raises after response.created.
            if not self._has_terminal_event(state.handler_events):
                state.pending_terminal = await self._make_failed_event(ctx, state)
            return

        # B11: Handler returned without a terminal event while cancellation
        # signal is set. The terminal status depends on the cancellation cause
        # (spec 024 Phase 5 Proposal #11):
        #
        # - shutdown=True + durable+background: leave in_progress for re-entry
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
                # For durable+background, leave response in_progress for
                # re-entry. Don't emit terminal — just return.
                if ctx.background and ctx.store and self._runtime_options.durable_background:
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
                        "Failed to synthesise cancel terminal on interrupted " "foreground stream (response_id=%s)",
                        ctx.response_id,
                        exc_info=True,
                    )
            # Persist the cancelled response to the durable provider so a
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
            chat_isolation_key=ctx.chat_isolation_key,
        )
        execution.set_response_snapshot(generated_models.ResponseObject(response_payload))
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
        # (durable_bg+bg+store+stream=T) branch below — handler runs inside
        # the durable task body via _start_durable_background; the live wire
        # iterator subscribes to the per-response stream. The pre-existing
        # bookkeeping_record + bookkeeping_active + _complete_bookkeeping_task
        # mechanics are deleted. Disposition is selected per row:
        #   - durable_bg=True + bg + store    → re-invoke   (Row 1 stream=T)
        #   - durable_bg=False + bg + store   → mark-failed (Row 2 stream=T)
        #   - fg + store                      → mark-failed (Row 3 stream=T)
        # The downstream branches read ``_unified_disposition`` instead of
        # deriving the disposition independently.
        _unified_disposition = (
            "re-invoke"
            if (ctx.background and self._runtime_options.durable_background and ctx.store)
            else "mark-failed"
        )

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
            if not ctx.store:
                # Row 4 stream — no store, no durable task. Inline pipeline.
                # (Spec 024 Phase 2) — pre-Phase-2 this branch also covered
                # Row 3 stream via inline handler; that's now part of the
                # unified durable+wire_stream path below.
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
            # asyncio.Task so that finalization (including subject.close()) is
            # guaranteed to run even when the original SSE connection is dropped before
            # all events are delivered.  Without this, _live_stream can be abandoned
            # mid-iteration by Starlette (the async-generator finalizer may not fire
            # promptly), leaving GET-replay subscribers blocked on await forever.
            #
            # (Spec 024 Phase 2) Unified stream-path for ALL store=True
            # streams. Row 1 (durable_bg+bg+store), Row 2 (non-durable_bg+bg+store),
            # and Row 3 (fg+store) all run the handler inside the durable
            # task body; the wire iterator subscribes to the per-response
            # stream via the registry. Disposition is selected per row
            # (re-invoke for Row 1, mark-failed for Row 2/3). The
            # downstream `_durable_stream_fallback` is the in-process
            # fallback if the durable start can't proceed (e.g. test
            # client without a TaskManager).
            if ctx.store:
                # Bind the per-response stream up front. The registry guarantees
                # the same instance for the same id, so the durable body's
                # ``_register_bg_execution`` (and any future caller) gets back
                # this exact stream — every emit fans out to the wire iterator
                # below.
                wire_stream = await streams.get_or_create(ctx.response_id)

                async def _durable_stream_fallback() -> None:
                    # Non-durable fallback runner if _start_durable_background's
                    # internal try/except falls through. Uses the same
                    # _process_handler_events pipeline as the durable body so
                    # events still reach the per-response stream the live wire
                    # iterator on this side is subscribed to.
                    try:
                        async for _event in self._process_handler_events(ctx, state, handler_iterator):
                            pass
                        if state.pending_terminal is not None:
                            r = state.bg_record or _make_ephemeral_record(ctx, state)
                            await self._persist_and_resolve_terminal(ctx, state, r)
                            # ``_persist_and_resolve_terminal`` emits the
                            # resolved terminal to the per-response stream
                            # (the same instance as ``wire_stream`` by
                            # registry identity) when ``ctx.background
                            # and ctx.store``, so we do not re-emit here.
                    finally:
                        await self._finalize_stream(ctx, state)
                        # The wire stream may already be closed via
                        # state.bg_record (record.subject is wire_stream).
                        # ``_safe_close`` is idempotent.
                        await self._safe_close(wire_stream)

                # Construct a minimal record only for _start_durable_background's
                # parameter shape. This record is NOT added to runtime_state —
                # the durable body (or fallback) will create the canonical
                # record via _register_bg_execution.
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
                    chat_isolation_key=ctx.chat_isolation_key,
                    initial_model=ctx.model,
                    initial_agent_reference=ctx.agent_reference,
                )
                start_record.subject = wire_stream

                await self._start_durable_background(
                    ctx,
                    start_record,
                    _durable_stream_fallback,
                    disposition=_unified_disposition,
                )

                try:
                    async for event in wire_stream.subscribe(after=None):
                        yield encode_sse_any_event(event)
                except Exception:  # pylint: disable=broad-exception-caught
                    pass  # wire dropped; durable body continues
                return

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
                    # Always finalize (includes subject.close()) — this runs even if
                    # the original POST SSE connection was dropped and _live_stream is
                    # never properly closed by Starlette.
                    await _finalize()
                    await bg_queue.put(_SENTINEL_BG)

            async def _bg_producer() -> None:
                try:
                    #: Shield the inner producer via asyncio.shield so
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

        (Spec 024 Phase 2) For ``store=True`` (Row 3) the handler runs inside
        the durable task body. The HTTP request awaits the task's terminal
        via ``await task_run.result()``. B8 (pre-creation error) is preserved
        by checking ``record.response_failed_before_events`` after the task
        completes — when True, an :class:`_HandlerError` is raised so the
        endpoint maps to HTTP 500. For ``store=False`` (no durable task
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
            # No store ⇒ no durable task possible. Run handler inline; the
            # response is ephemeral (not retrievable via GET).
            return await self._run_sync_inner(ctx, state)

        # (Spec 024 Phase 2 — bookkeeping unification) Row 3 unified path:
        # handler runs inside the durable task body, HTTP request awaits the
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
            chat_isolation_key=ctx.chat_isolation_key,
            initial_model=ctx.model,
            initial_agent_reference=ctx.agent_reference,
        )
        await self._runtime_state.add(record)

        async def _runner() -> None:
            """Fallback runner if _start_durable_background's durable start fails.

            Runs the same handler-execution pipeline as the durable body so
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

        await self._start_durable_background(ctx, record, _runner, disposition="mark-failed")

        # Block until the handler emits its terminal:
        #   - If durable start succeeded, ``record.durable_task_run`` is set;
        #     await its ``.result()`` to block on the task body.
        #   - If durable start fell back to asyncio (e.g. TestClient without
        #     TaskManager), ``record.execution_task`` is set; await it.
        # On HTTP client disconnect (CancelledError propagates here), cancel
        # the underlying durable task / execution task and treat the response
        # as discarded — per B17, non-bg sync responses are not retrievable
        # after disconnect. The record is removed from runtime_state and the
        # store-side persistence is skipped (best-effort).
        task_run = getattr(record, "durable_task_run", None)
        execution_task = getattr(record, "execution_task", None)
        try:
            if task_run is not None:
                try:
                    await task_run.result()
                except asyncio.CancelledError:
                    raise
                except Exception as task_exc:  # pylint: disable=broad-exception-caught
                    # Durable task body raised. If the handler had a pre-creation
                    # error (B8) → re-raise as _HandlerError below. Otherwise
                    # (post-creation error / persistence error) the record already
                    # reflects the failure state and the snapshot below carries
                    # the response.failed details.
                    if not getattr(record, "response_failed_before_events", False):
                        logger.warning(
                            "Durable task for sync response %s raised: %s",
                            ctx.response_id,
                            task_exc,
                            exc_info=True,
                        )
            elif execution_task is not None:
                try:
                    await execution_task
                except asyncio.CancelledError:
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
        # leaves the durable task in_progress so the next-lifetime recovery
        # scanner can mark the response failed. If we persisted/discarded
        # here on shutdown the recovery path would have nothing to find.
        # The ``context.shutdown`` event distinguishes the two: set means
        # server shutdown (preserve for recovery); not set means client
        # disconnect / explicit cancel (handled per B17 + B11).
        _is_shutdown = bool(ctx.context.shutdown.is_set()) if ctx.context else False
        if ctx.cancellation_signal.is_set() and not record.cancel_requested and not _is_shutdown:
            if ctx.store:
                # B17 + B11: persist cancelled terminal so GET 200 + cancelled.
                logger.info(
                    "Non-bg sync response %s cancelled on client disconnect (B17, store=true → cancelled retrievable)",
                    ctx.response_id,
                )
                cancelled_response = _build_cancelled_response(
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
                # can be evicted later without losing the cancelled
                # snapshot.
                try:
                    await self._provider.update_response(
                        cancelled_response,
                        isolation=ctx.context.isolation if ctx.context else None,
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
            failed_response = _build_failed_response(
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

        # Read snapshot from the now-completed record. The durable task body
        # persisted to the store; the record reflects the final state.
        ctx.span.end(None)
        return _RuntimeState.to_snapshot(record)

    async def _run_sync_inner(self, ctx: _ExecutionContext, state: _PipelineState) -> dict[str, Any]:
        """Inner body of :meth:`run_sync` — extracted so the bookkeeping
        task can be signalled in a ``try/finally`` wrapper in the caller.

        :param ctx: Current execution context.
        :param state: Pipeline state (populated by handler events).
        :return: Response snapshot dictionary.
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
                        runtime_options=self._runtime_options,
                    )
            except asyncio.CancelledError:
                pass  # event-loop teardown; background work already done

        if ctx.store:
            # (Spec 024 Phase 2) Unified path for Row 1 + Row 2 (bg+store):
            # the handler ALWAYS runs inside the durable task body. The
            # disposition determines recovery behaviour only:
            #   - durable_background=True  → re-invoke (Row 1: handler
            #     re-runs on next-lifetime recovery).
            #   - durable_background=False → mark-failed (Row 2: response
            #     is marked failed on next-lifetime recovery).
            # The legacy ``asyncio.create_task(_shielded_runner)`` path
            # for Row 2 + the separate bookkeeping task are deleted —
            # one durable task per response covers both rows.
            disposition = "re-invoke" if self._runtime_options.durable_background else "mark-failed"
            await self._start_durable_background(ctx, record, _shielded_runner, disposition=disposition)
        else:
            # Row 4 — no store, no durable task. Plain asyncio.
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

    async def _run_durable_stream_body(
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
        """Durable task body for streaming responses.

        Called from ``DurableResponseOrchestrator._execute_in_task`` when
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
                "Could not load last cursor for response_id=%s — seeding " "next_seq=0",
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
            # SHUTTING_DOWN is detected for a durable_background+store
            # response. In that case we MUST NOT close the wire stream:
            # closing flushes a terminal marker, which puts the stream
            # in CLOSED state. The recovered handler on the next
            # lifetime would then see a CLOSED stream and its emits
            # would silently no-op (closed-stream contract), leaving
            # GET ?stream=true post-recovery without a terminal event
            # even though the recovered handler ran to completion. The
            # finalize_stream / close steps are skipped — the next
            # lifetime's _run_durable_stream_body will re-open the same
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
                        "_finalize_stream failed for durable streaming body " "response_id=%s",
                        response_id,
                        exc_info=True,
                    )
                # Always close the per-response stream so the live wire
                # iterator exits cleanly. Idempotent if _finalize_stream
                # already closed the same stream through state.bg_record.
                await self._safe_close(wire_stream)

    # (Spec 024 Phase 2) `_complete_bookkeeping_task` deleted. The
    # bookkeeping pattern is gone — handler now runs inside the durable
    # task body for Rows 1/2/3 and the task completes when the handler
    # returns. No external completion signal is needed.

    async def _start_durable_background(
        self,
        ctx: _ExecutionContext,
        record: ResponseExecution,
        fallback_runner: Any,
        *,
        disposition: str = "re-invoke",
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
        :keyword disposition: One of ``"re-invoke"`` (Row 1: durable_bg+bg+store
            — task body re-runs handler on recovery) or ``"mark-failed"``
            (Rows 2/3: bg+store with durable_bg=False, or fg+store — task body
            is bookkeeping-only on fresh entry and marks the response failed on
            recovery). Stamped into task framework metadata so recovery dispatch
            can route without re-deriving the gate from request params.
        :paramtype disposition: str
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

        # (Spec 024 Phase 2) `ensure_bookkeeping_event` pre-registration
        # deleted. The bookkeeping pattern is gone — handler now runs
        # inside the durable task body for all rows; no separate event
        # registry is consulted by anyone.

        # Build execution params dict for the task input
        ctx_params: dict[str, Any] = {
            "response_id": ctx.response_id,
            # (Spec 014 FR-003 / FR-004) Disposition stamped into params
            # at start so _execute_in_task can copy it into framework
            # metadata on first entry; recovery dispatch reads from
            # metadata thereafter (survives cross-process recovery).
            "disposition": disposition,
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
            if not freshly_started:
                # Input was queued on already-active multi-turn steerable
                # chain. The downstream `start_durable` already detected
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
        except Exception:  # pylint: disable=broad-exception-caught
            # Durable start failed — fall back to non-durable execution
            logger.warning(
                "Durable task start failed for response %s; falling back to asyncio.create_task",
                ctx.response_id,
                exc_info=True,
            )
            record.execution_task = asyncio.create_task(fallback_runner())
