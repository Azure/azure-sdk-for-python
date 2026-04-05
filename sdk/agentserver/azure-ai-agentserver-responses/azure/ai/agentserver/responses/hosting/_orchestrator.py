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
from copy import deepcopy
from typing import Any, AsyncIterator

import anyio

from ..models import _generated as generated_models
from ..models.runtime import (
    ResponseExecution,
    ResponseModeFlags,
    build_cancelled_response as _build_cancelled_response,
    build_failed_response as _build_failed_response,
)
from ..streaming._sse import encode_keep_alive_comment, encode_sse_payload, new_stream_counter
from ..streaming._helpers import (
    EVENT_TYPE,
    _apply_stream_event_defaults,
    _build_events,
    _coerce_handler_event,
    _extract_response_snapshot_from_events,
)
from .._options import ResponsesServerOptions
from ..store._base import ResponseProviderProtocol, ResponseStreamProviderProtocol
from ._background import _run_background_non_stream
from ._event_subject import _ResponseEventSubject
from ._execution_context import _ExecutionContext
from ._runtime_state import _RuntimeState


def _check_first_event_contract(normalized: dict[str, Any], response_id: str) -> str | None:
    """Return an error message if the first handler event violates S-007/S-008/S-009, else None.

    - S-007: The first event MUST be ``response.created``.
    - S-008: The ``id`` in ``response.created`` MUST equal the library-assigned ``response_id``.
    - S-009: The ``status`` in ``response.created`` MUST be non-terminal.

    :param normalized: Normalised first event dict.
    :type normalized: dict[str, Any]
    :param response_id: Library-assigned response identifier.
    :type response_id: str
    :return: Violation message string, or ``None`` if no violation.
    :rtype: str | None
    """
    event_type = normalized.get("type")
    payload = normalized.get("payload") or {}
    if event_type != "response.created":
        return f"S-007: first event must be response.created, got '{event_type}'"
    emitted_id = payload.get("id")
    if emitted_id and emitted_id != response_id:
        return f"S-008: response.created id '{emitted_id}' != assigned id '{response_id}'"
    emitted_status = payload.get("status")
    if emitted_status in {"completed", "failed", "cancelled", "incomplete"}:
        return f"S-009: response.created status must be non-terminal, got '{emitted_status}'"
    return None


class _HandlerError(Exception):
    """Raised by :meth:`_ResponseOrchestrator.run_sync` when the handler raises.

    Callers should catch this to convert it into an appropriate HTTP error
    response without leaking orchestrator internals.
    """

    def __init__(self, original: Exception) -> None:
        self.original = original
        super().__init__(str(original))


class _PipelineState:
    """Mutable in-flight state for a single create-response invocation.

    Intentionally separate from :class:`_ExecutionContext` (which is a pure
    immutable per-request input value object).  Created locally inside
    :meth:`_ResponseOrchestrator._live_stream` and
    :meth:`_ResponseOrchestrator.run_sync`, then threaded through every
    internal helper so that the helpers are side-effect-free with respect
    to ``_ExecutionContext``.
    """

    __slots__ = ("handler_events", "bg_record", "captured_error")

    def __init__(self) -> None:
        self.handler_events: list[dict[str, Any]] = []
        self.bg_record: ResponseExecution | None = None
        self.captured_error: Exception | None = None


class _ResponseOrchestrator:  # pylint: disable=too-many-instance-attributes
    """Event-pipeline orchestrator for the Responses API.

    Handles the business logic for streaming, synchronous, and background
    create-response requests: driving the handler iterator, normalising events,
    managing the background execution record, and finalising persistent state.

    This class has no dependency on Starlette types.
    """

    _TERMINAL_SSE_TYPES: frozenset[str] = frozenset({
        EVENT_TYPE.RESPONSE_COMPLETED.value,
        EVENT_TYPE.RESPONSE_FAILED.value,
        EVENT_TYPE.RESPONSE_INCOMPLETE.value,
    })

    def __init__(
        self,
        *,
        create_fn: Any,
        runtime_state: _RuntimeState,
        runtime_options: ResponsesServerOptions,
        provider: ResponseProviderProtocol,
        stream_provider: ResponseStreamProviderProtocol | None = None,
    ) -> None:
        """Initialise the orchestrator.

        :param create_fn: The bound ``create_fn`` method from the registered handler.
        :type create_fn: Any
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
        self, ctx: _ExecutionContext, state: _PipelineState, handler_event: Any
    ) -> dict[str, Any]:
        """Coerce, normalise, and append a handler event to the pipeline state.

        Also propagates the event into the background record and its subject when active.

        :param ctx: Current execution context (immutable inputs).
        :type ctx: _ExecutionContext
        :param state: Mutable pipeline state for this invocation.
        :type state: _PipelineState
        :param handler_event: Raw event emitted by the handler.
        :type handler_event: Any
        :return: The normalised event dictionary.
        :rtype: dict[str, Any]
        """
        coerced = _coerce_handler_event(handler_event)
        normalized = _apply_stream_event_defaults(
            coerced,
            response_id=ctx.response_id,
            agent_reference=ctx.agent_reference,
            model=ctx.model,
            sequence_number=len(state.handler_events),
            agent_session_id=ctx.agent_session_id,
        )
        state.handler_events.append(normalized)
        if state.bg_record is not None:
            state.bg_record.apply_event(normalized, state.handler_events)
            if state.bg_record.subject is not None:
                await state.bg_record.subject.publish(normalized)
        return normalized

    @staticmethod
    def _has_terminal_event(handler_events: list[dict[str, Any]]) -> bool:
        """Return ``True`` if any terminal event has been emitted.

        :param handler_events: List of normalised handler events.
        :type handler_events: list[dict[str, Any]]
        :return: Whether a terminal event is present.
        :rtype: bool
        """
        return any(e["type"] in _ResponseOrchestrator._TERMINAL_SSE_TYPES for e in handler_events)

    async def _cancel_terminal_sse(self, ctx: _ExecutionContext, state: _PipelineState) -> str:
        """Build and record a ``response.failed`` cancel-terminal SSE string.

        :param ctx: Current execution context (immutable inputs).
        :type ctx: _ExecutionContext
        :param state: Mutable pipeline state for this invocation.
        :type state: _PipelineState
        :return: Encoded SSE string for the cancel-terminal event.
        :rtype: str
        """
        cancel_event: dict[str, Any] = {
            "type": EVENT_TYPE.RESPONSE_FAILED.value,
            "payload": _build_cancelled_response(ctx.response_id, ctx.agent_reference, ctx.model).as_dict(),
        }
        normalized = _apply_stream_event_defaults(
            cancel_event,
            response_id=ctx.response_id,
            agent_reference=ctx.agent_reference,
            model=ctx.model,
            sequence_number=len(state.handler_events),
            agent_session_id=ctx.agent_session_id,
        )
        state.handler_events.append(normalized)
        if state.bg_record is not None:
            state.bg_record.apply_event(normalized, state.handler_events)
            if state.bg_record.subject is not None:
                await state.bg_record.subject.publish(normalized)
        return encode_sse_payload(normalized["type"], normalized["payload"])

    async def _cancel_terminal_sse_dict(self, ctx: _ExecutionContext, state: _PipelineState) -> dict[str, Any]:
        """Build, normalise, append, and return a cancel-terminal event dict.

        Like :meth:`_cancel_terminal_sse` but returns the raw normalised event
        dictionary instead of an SSE-encoded string, so that it can be consumed
        by the shared :meth:`_process_handler_events` pipeline.

        :param ctx: Current execution context (immutable inputs).
        :type ctx: _ExecutionContext
        :param state: Mutable pipeline state for this invocation.
        :type state: _PipelineState
        :return: Normalised cancel-terminal event dictionary.
        :rtype: dict[str, Any]
        """
        cancel_event: dict[str, Any] = {
            "type": EVENT_TYPE.RESPONSE_FAILED.value,
            "payload": _build_cancelled_response(ctx.response_id, ctx.agent_reference, ctx.model).as_dict(),
        }
        return await self._normalize_and_append(ctx, state, cancel_event)

    async def _make_failed_event(self, ctx: _ExecutionContext, state: _PipelineState) -> dict[str, Any]:
        """Build, normalise, append, and return a ``response.failed`` event dict.

        Used for B-13 (handler exception after ``response.created``) and
        S-021 (handler completed without emitting a terminal event).

        :param ctx: Current execution context (immutable inputs).
        :type ctx: _ExecutionContext
        :param state: Mutable pipeline state for this invocation.
        :type state: _PipelineState
        :return: Normalised ``response.failed`` event dictionary.
        :rtype: dict[str, Any]
        """
        failed_event: dict[str, Any] = {
            "type": EVENT_TYPE.RESPONSE_FAILED.value,
            "payload": {
                "id": ctx.response_id,
                "object": "response",
                "status": "failed",
                "output": [],
                "error": {"code": "server_error", "message": "An internal server error occurred."},
            },
        }
        return await self._normalize_and_append(ctx, state, failed_event)

    async def _register_bg_execution(
        self, ctx: _ExecutionContext, state: _PipelineState, first_normalized: dict[str, Any]
    ) -> None:
        """Create, seed, and register the background+stream execution record.

        Called from :meth:`_process_handler_events` after the first event is
        received.  The record is seeded with ``first_normalized`` so that
        subscribers joining mid-stream receive the full history (matching
        :meth:`.NET`'s ``SeekableReplaySubject`` behaviour).

        :param ctx: Current execution context (immutable inputs).
        :type ctx: _ExecutionContext
        :param state: Mutable pipeline state for this invocation.
        :type state: _PipelineState
        :param first_normalized: The first normalised handler event.
        :type first_normalized: dict[str, Any]
        """
        initial_payload = _extract_response_snapshot_from_events(
            state.handler_events,
            response_id=ctx.response_id,
            agent_reference=ctx.agent_reference,
            model=ctx.model,
            agent_session_id=ctx.agent_session_id,
        )
        initial_status = initial_payload.get("status")
        if not isinstance(initial_status, str):
            initial_status = "in_progress"
        execution = ResponseExecution(
            response_id=ctx.response_id,
            mode_flags=ResponseModeFlags(stream=True, store=True, background=True),
            status=initial_status,
            input_items=deepcopy(ctx.input_items),
            previous_response_id=ctx.previous_response_id,
            cancel_signal=ctx.cancellation_signal,
        )
        execution.set_response_snapshot(generated_models.ResponseObject(initial_payload))
        execution.subject = _ResponseEventSubject()
        state.bg_record = execution
        await state.bg_record.subject.publish(first_normalized)
        await self._runtime_state.add(execution)
        if ctx.store:
            _initial_response_obj = generated_models.ResponseObject(initial_payload)
            _history_ids = (
                await self._provider.get_history_item_ids(ctx.previous_response_id, None, 10000)
                if ctx.previous_response_id
                else None
            )
            await self._provider.create_response(
                _initial_response_obj, ctx.input_items or None, _history_ids
            )

    async def _process_handler_events(
        self,
        ctx: _ExecutionContext,
        state: _PipelineState,
        handler_iterator: Any,
    ) -> AsyncIterator[dict[str, Any]]:
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
        - Post-creation handler exception (B-13): yields a ``response.failed`` event
          and sets ``state.captured_error``.
        - Missing terminal after successful handler completion (S-021): yields a
          ``response.failed`` event without setting ``state.captured_error`` so that
          synchronous callers can return HTTP 200 with a ``"failed"`` body.
        - Cancellation winddown (S-019): yields a cancel-terminal event when the
          cancellation signal is set and no terminal event was emitted.

        :param ctx: Current execution context (immutable inputs).
        :type ctx: _ExecutionContext
        :param state: Mutable pipeline state for this invocation.
        :type state: _PipelineState
        :param handler_iterator: Async generator returned by the handler's
            ``create_fn`` factory.
        :type handler_iterator: Any
        :return: Async iterator of normalised event dictionaries.
        :rtype: AsyncIterator[dict[str, Any]]
        """
        # --- First event ---
        try:
            first_raw = await handler_iterator.__anext__()
        except StopAsyncIteration:
            # Handler yielded nothing: synthesise fallback lifecycle events.
            fallback_events = _build_events(
                ctx.response_id,
                include_progress=True,
                agent_reference=ctx.agent_reference,
                model=ctx.model,
            )
            for event in fallback_events:
                state.handler_events.append(event)
                yield event
            return
        except Exception as exc:  # pylint: disable=broad-exception-caught
            # B8: Pre-creation error → emit a standalone `error` event only.
            # No response.created precedes it; this is the contract-mandated shape.
            state.captured_error = exc
            yield {
                "type": EVENT_TYPE.ERROR.value,
                "payload": {"message": "An internal server error occurred.", "param": None, "code": None},
            }
            return

        # Normalise the first event manually (before _normalize_and_append so we
        # can set up the bg record with the correct sequence number).
        first_normalized = _apply_stream_event_defaults(
            _coerce_handler_event(first_raw),
            response_id=ctx.response_id,
            agent_reference=ctx.agent_reference,
            model=ctx.model,
            sequence_number=len(state.handler_events),
            agent_session_id=ctx.agent_session_id,
        )

        # S-007/S-008/S-009: first-event contract validation.
        # Violations are treated the same as B8 pre-creation errors:
        # - streaming: yield a standalone 'error' event and return (no record created)
        # - sync: state.captured_error is set → run_sync raises _HandlerError → HTTP 500
        violation = _check_first_event_contract(first_normalized, ctx.response_id)
        if violation:
            state.captured_error = RuntimeError(violation)
            yield {
                "type": EVENT_TYPE.ERROR.value,
                "payload": {"message": "An internal server error occurred.", "param": None, "code": None},
            }
            return

        state.handler_events.append(first_normalized)

        # bg+store: create and register the execution record after the first event.
        if ctx.background and ctx.store:
            await self._register_bg_execution(ctx, state, first_normalized)

        yield first_normalized

        # --- Remaining events ---
        try:
            async for raw in handler_iterator:
                normalized = await self._normalize_and_append(ctx, state, raw)
                yield normalized
        except Exception as exc:  # pylint: disable=broad-exception-caught
            state.captured_error = exc
            # B-13: emit response.failed when handler raises after response.created.
            if not self._has_terminal_event(state.handler_events):
                yield await self._make_failed_event(ctx, state)
            return

        # S-019: cancellation winddown checked BEFORE S-021 so that a handler
        # stopped early by the cancellation signal receives a proper cancel
        # terminal event (response.failed with status == "cancelled") rather
        # than a generic S-021 failure terminal.
        if ctx.cancellation_signal.is_set() and not self._has_terminal_event(state.handler_events):
            yield await self._cancel_terminal_sse_dict(ctx, state)
            return

        # S-021: handler completed normally but never emitted a terminal event.
        # NOTE: state.captured_error intentionally left None so that synchronous
        # callers return HTTP 200 with a "failed" body rather than HTTP 500.
        if not self._has_terminal_event(state.handler_events):
            yield await self._make_failed_event(ctx, state)

    async def _finalize_bg_stream(self, ctx: _ExecutionContext, state: _PipelineState) -> None:
        """Persist state and complete the subject for a background+stream response.

        Called from the ``finally`` block of :meth:`_live_stream` when
        ``ctx.background and ctx.store`` is True.  The execution record may
        already exist (``state.bg_record``, created at ``response.created`` time)
        or may be absent (empty handler — fallback events were synthesised by
        :meth:`_process_handler_events`).  In the latter case the record is
        created here from the accumulated ``state.handler_events``.

        :param ctx: Current execution context (immutable inputs).
        :type ctx: _ExecutionContext
        :param state: Mutable pipeline state for this invocation.
        :type state: _PipelineState
        """
        # If the handler yielded nothing, _process_handler_events synthesised
        # fallback events but never called _register_bg_execution, so
        # state.bg_record is None.  Create the record here from the fallback events.
        if state.bg_record is None:
            events = state.handler_events if state.handler_events else _build_events(
                ctx.response_id,
                include_progress=True,
                agent_reference=ctx.agent_reference,
                model=ctx.model,
            )
            response_payload = _extract_response_snapshot_from_events(
                events,
                response_id=ctx.response_id,
                agent_reference=ctx.agent_reference,
                model=ctx.model,
                agent_session_id=ctx.agent_session_id,
            )
            resolved_status = response_payload.get("status")
            status = resolved_status if isinstance(resolved_status, str) else "completed"

            replay_subject = _ResponseEventSubject()
            for _evt in events:
                await replay_subject.publish(_evt)
            await replay_subject.complete()

            execution = ResponseExecution(
                response_id=ctx.response_id,
                mode_flags=ResponseModeFlags(stream=True, store=True, background=True),
                status=status,
                subject=replay_subject,
                input_items=deepcopy(ctx.input_items),
                previous_response_id=ctx.previous_response_id,
                cancel_signal=ctx.cancellation_signal,
            )
            execution.set_response_snapshot(generated_models.ResponseObject(response_payload))
            await self._runtime_state.add(execution)
            if ctx.store:
                try:
                    _history_ids = (
                        await self._provider.get_history_item_ids(ctx.previous_response_id, None, 10000)
                        if ctx.previous_response_id
                        else None
                    )
                    await self._provider.create_response(
                        generated_models.ResponseObject(response_payload), ctx.input_items or None, _history_ids
                    )
                except Exception:  # pylint: disable=broad-exception-caught
                    pass  # best effort
            ctx.span.end(state.captured_error)
            return

        record = state.bg_record

        if record.status != "cancelled":
            events = state.handler_events if state.handler_events else _build_events(
                ctx.response_id,
                include_progress=True,
                agent_reference=ctx.agent_reference,
                model=ctx.model,
            )
            if state.captured_error is not None:
                record.set_response_snapshot(
                    _build_failed_response(
                        ctx.response_id,
                        ctx.agent_reference,
                        ctx.model,
                        created_at=ctx.context.created_at,
                    )
                )
                record.transition_to("failed")
            else:
                response_payload = _extract_response_snapshot_from_events(
                    events,
                    response_id=ctx.response_id,
                    agent_reference=ctx.agent_reference,
                    model=ctx.model,
                    agent_session_id=ctx.agent_session_id,
                )
                resolved_status = response_payload.get("status")
                status = resolved_status if isinstance(resolved_status, str) else "in_progress"
                record.set_response_snapshot(generated_models.ResponseObject(response_payload))
                record.transition_to(status)  # type: ignore[arg-type]

            # Persist terminal state update via provider (bg+stream: initial create already done)
            if record.mode_flags.store and record.response is not None:
                try:
                    await self._provider.update_response(record.response)
                except Exception:  # pylint: disable=broad-exception-caught
                    pass  # best effort
                # Persist SSE events for replay after process restart
                if self._stream_provider is not None and state.handler_events:
                    try:
                        await self._stream_provider.save_stream_events(
                            ctx.response_id, state.handler_events
                        )
                    except Exception:  # pylint: disable=broad-exception-caught
                        pass  # best effort

        ctx.span.end(state.captured_error)
        # Complete the subject — signals all live SSE replay subscribers that the
        # stream has ended, matching .NET's publisher.OnCompletedAsync() call.
        if record.subject is not None:
            try:
                await record.subject.complete()
            except Exception:  # pylint: disable=broad-exception-caught
                pass  # best effort

    async def _finalize_non_bg_stream(self, ctx: _ExecutionContext, state: _PipelineState) -> None:
        """Persist the execution record for a non-background streaming response.

        Called from the ``finally`` block of :meth:`_live_stream` when
        ``ctx.background`` is False.  For ``store=True`` responses, this creates
        a new execution record and provider entry at terminal state (the stream
        is already complete).  A pre-filled replay subject is attached so that
        ``GET ?stream=true`` replay has a subject to subscribe to, though replay
        will be rejected (``replay_enabled=False``) because this is non-background.

        :param ctx: Current execution context (immutable inputs).
        :type ctx: _ExecutionContext
        :param state: Mutable pipeline state for this invocation.
        :type state: _PipelineState
        """
        events = state.handler_events if state.handler_events else _build_events(
            ctx.response_id,
            include_progress=True,
            agent_reference=ctx.agent_reference,
            model=ctx.model,
        )
        response_payload = _extract_response_snapshot_from_events(
            events,
            response_id=ctx.response_id,
            agent_reference=ctx.agent_reference,
            model=ctx.model,
            agent_session_id=ctx.agent_session_id,
        )
        resolved_status = response_payload.get("status")
        status = resolved_status if isinstance(resolved_status, str) else "completed"

        if ctx.store:
            # Pre-fill a completed subject so GET ?stream=true replay always has
            # a subject to subscribe to (non-bg: stream already finished here).
            replay_subject = _ResponseEventSubject()
            for _evt in events:
                await replay_subject.publish(_evt)
            await replay_subject.complete()
            stream_record = ResponseExecution(
                response_id=ctx.response_id,
                mode_flags=ResponseModeFlags(stream=True, store=True, background=False),
                status=status,
                subject=replay_subject,
                input_items=deepcopy(ctx.input_items),
                previous_response_id=ctx.previous_response_id,
            )
            stream_record.set_response_snapshot(generated_models.ResponseObject(response_payload))
            await self._runtime_state.add(stream_record)
            # Persist via provider (non-bg stream: single create at terminal state)
            try:
                _history_ids = (
                    await self._provider.get_history_item_ids(ctx.previous_response_id, None, 10000)
                    if ctx.previous_response_id
                    else None
                )
                await self._provider.create_response(
                    generated_models.ResponseObject(response_payload), ctx.input_items or None, _history_ids
                )
            except Exception:  # pylint: disable=broad-exception-caught
                pass  # best effort

        ctx.span.end(state.captured_error)

    # ------------------------------------------------------------------
    # Public execution methods
    # ------------------------------------------------------------------

    def run_stream(self, ctx: _ExecutionContext) -> AsyncIterator[str]:
        """Return an async iterator of SSE-encoded strings for a streaming request.

        The iterator handles:

        - Pre-creation errors (B8 contract: standalone ``error`` SSE event).
        - Empty handler (fallback synthesised events).
        - Mid-stream handler errors (``response.failed`` SSE event, B-13).
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
        bg record registration, B-13 / S-021 / S-019 terminal events) to
        :meth:`_process_handler_events`.  This method only encodes each event
        dict to SSE and handles keep-alive comment injection.

        :param ctx: Current execution context.
        :type ctx: _ExecutionContext
        :returns: Async iterator of SSE-encoded strings.
        :rtype: AsyncIterator[str]
        """
        new_stream_counter()
        state = _PipelineState()
        handler_iterator = self._create_fn(ctx.parsed, ctx.context, ctx.cancellation_signal)

        # Helper: route to the right finalize method based on the request semantics
        # (bg+store → bg_stream path; everything else → non_bg_stream path).
        # NOTE: state.bg_record may be None for bg+stream when the handler yields no
        # events (fallback path in _process_handler_events); _finalize_bg_stream
        # handles that case by creating the record itself.
        async def _finalize() -> None:
            if ctx.background and ctx.store:
                await self._finalize_bg_stream(ctx, state)
            else:
                await self._finalize_non_bg_stream(ctx, state)

        # --- Fast path: no keep-alive ---
        if not self._runtime_options.sse_keep_alive_enabled:
            if not (ctx.background and ctx.store):
                # Simple fast path for non-background streaming.
                try:
                    async for event in self._process_handler_events(ctx, state, handler_iterator):
                        yield encode_sse_payload(event["type"], event["payload"])
                finally:
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

            async def _bg_producer() -> None:
                try:
                    async for event in self._process_handler_events(ctx, state, handler_iterator):
                        await bg_queue.put(encode_sse_payload(event["type"], event["payload"]))
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    state.captured_error = exc
                finally:
                    # Always finalize (includes subject.complete()) — this runs even if
                    # the original POST SSE connection was dropped and _live_stream is
                    # never properly closed by Starlette.
                    await _finalize()
                    await bg_queue.put(_SENTINEL_BG)

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
                    await merge_queue.put(encode_sse_payload(event["type"], event["payload"]))
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

        try:
            while True:
                item = await merge_queue.get()
                if item is _SENTINEL:
                    break
                yield item  # type: ignore[misc]
        except Exception as exc:  # pylint: disable=broad-exception-caught
            state.captured_error = exc
        finally:
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

        Raises :class:`_HandlerError` if the handler raises (B8 or B-13) so
        the caller can map it to an HTTP 500 response.  S-021 (handler
        completed without emitting a terminal event) does *not* raise; instead
        the snapshot status is ``"failed"`` and HTTP 200 is returned.

        :param ctx: Current execution context.
        :type ctx: _ExecutionContext
        :return: Response snapshot dictionary.
        :rtype: dict[str, Any]
        :raises _HandlerError: If the handler raises during iteration.
        """
        state = _PipelineState()
        handler_iterator = self._create_fn(ctx.parsed, ctx.context, ctx.cancellation_signal)
        # _process_handler_events handles all error paths (B8, B-13, S-021, S-019).
        # run_sync only needs to exhaust the generator for state.handler_events side-effects.
        async for _ in self._process_handler_events(ctx, state, handler_iterator):
            pass

        if state.captured_error is not None:
            ctx.span.end(state.captured_error)
            raise _HandlerError(state.captured_error) from state.captured_error

        events = state.handler_events if state.handler_events else _build_events(
            ctx.response_id,
            include_progress=True,
            agent_reference=ctx.agent_reference,
            model=ctx.model,
        )
        response_payload = _extract_response_snapshot_from_events(
            events,
            response_id=ctx.response_id,
            agent_reference=ctx.agent_reference,
            model=ctx.model,
            remove_sequence_number=True,
            agent_session_id=ctx.agent_session_id,
        )
        resolved_status = response_payload.get("status")
        status = resolved_status if isinstance(resolved_status, str) else "completed"

        record = ResponseExecution(
            response_id=ctx.response_id,
            mode_flags=ResponseModeFlags(stream=False, store=ctx.store, background=False),
            status=status,
            input_items=deepcopy(ctx.input_items),
            previous_response_id=ctx.previous_response_id,
            response_context=ctx.context,
        )
        record.set_response_snapshot(generated_models.ResponseObject(response_payload))

        if ctx.store:
            await self._runtime_state.add(record)
            # Persist via provider (non-bg sync: single create at terminal state)
            try:
                _response_obj = generated_models.ResponseObject(response_payload)
                _history_ids = (
                    await self._provider.get_history_item_ids(ctx.previous_response_id, None, 10000)
                    if ctx.previous_response_id
                    else None
                )
                await self._provider.create_response(_response_obj, ctx.input_items or None, _history_ids)
            except Exception:  # pylint: disable=broad-exception-caught
                pass  # best effort

        ctx.span.end(None)
        return _RuntimeState.to_snapshot(record)

    async def run_background(self, ctx: _ExecutionContext) -> dict[str, Any]:
        """Handle a background (non-stream) create-response request.

        Immediately launches the handler as an asyncio task, waits up to 10 s
        for the first ``response.created`` event, then returns the current
        snapshot.  This ensures that the POST response body reflects the
        handler's real ``response.created`` payload (S-003).

        :param ctx: Current execution context.
        :type ctx: _ExecutionContext
        :return: Response snapshot dictionary (status: in_progress or queued on timeout).
        :rtype: dict[str, Any]
        :raises _HandlerError: If the handler fails before emitting any event.
        """
        record = ResponseExecution(
            response_id=ctx.response_id,
            mode_flags=ResponseModeFlags(stream=False, store=ctx.store, background=True),
            status="queued",
            input_items=deepcopy(ctx.input_items),
            previous_response_id=ctx.previous_response_id,
            response_context=ctx.context,
            cancel_signal=ctx.cancellation_signal,
        )

        # Always register so GET can observe in-flight state
        await self._runtime_state.add(record)

        # Best-effort persist initial queued state via provider
        if ctx.store:
            try:
                _initial_snapshot = _RuntimeState.to_snapshot(record)
                _response_obj = generated_models.ResponseObject(_initial_snapshot)
                _history_ids = (
                    await self._provider.get_history_item_ids(ctx.previous_response_id, None, 10000)
                    if ctx.previous_response_id
                    else None
                )
                await self._provider.create_response(_response_obj, ctx.input_items or None, _history_ids)
            except Exception:  # pylint: disable=broad-exception-caught
                pass  # best effort

        # Launch handler immediately (S-003: handler runs asynchronously)
        # Use anyio.CancelScope(shield=True) + suppress CancelledError so the
        # background task is NOT cancelled when the HTTP request scope exits
        # (anyio structured concurrency).  The shielded scope ensures the handler
        # runs to completion; catching CancelledError prevents the Task from being
        # marked as cancelled, so _refresh_background_status reads the real status.
        async def _shielded_runner() -> None:
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
                    )
            except asyncio.CancelledError:
                pass  # event-loop teardown in TestClient; background work already done

        record.execution_task = asyncio.create_task(_shielded_runner())

        # Wait for first event signal (or 10 s timeout) before returning POST response
        try:
            await asyncio.wait_for(record.response_created_signal.wait(), timeout=10.0)
        except asyncio.TimeoutError:
            pass  # Return current snapshot anyway; handler is still running

        if record.response_failed_before_events:
            raise _HandlerError(RuntimeError("Handler failed before emitting response.created"))

        ctx.span.end(None)
        return _RuntimeState.to_snapshot(record)
