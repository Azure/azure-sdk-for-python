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

from ..streaming._sse import encode_keep_alive_comment, encode_sse_payload, new_stream_counter
from ..streaming._helpers import (
    EVENT_TYPE,
    _RESPONSE_SNAPSHOT_EVENT_TYPES,
    _apply_stream_event_defaults,
    _build_events,
    _coerce_handler_event,
    _extract_response_snapshot_from_events,
)
from .._options import ResponsesServerOptions
from ._background import _run_background_non_stream
from ._execution_context import _ExecutionContext
from ._runtime_state import _ExecutionRecord, _RuntimeState


class _HandlerError(Exception):
    """Raised by :meth:`_ResponseOrchestrator.run_sync` when the handler raises.

    Callers should catch this to convert it into an appropriate HTTP error
    response without leaking orchestrator internals.
    """

    def __init__(self, original: Exception) -> None:
        self.original = original
        super().__init__(str(original))


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
        create_async: Any,
        runtime_state: _RuntimeState,
        runtime_options: ResponsesServerOptions,
    ) -> None:
        """Initialise the orchestrator.

        :param create_async: The bound ``create_async`` method from the registered handler.
        :type create_async: Any
        :param runtime_state: In-memory execution record store.
        :type runtime_state: _RuntimeState
        :param runtime_options: Server runtime options (keep-alive, etc.).
        :type runtime_options: ResponsesServerOptions
        """
        self._create_async = create_async
        self._runtime_state = runtime_state
        self._runtime_options = runtime_options

    # ------------------------------------------------------------------
    # Internal helpers (stream path)
    # ------------------------------------------------------------------

    def _normalize_and_append(self, ctx: _ExecutionContext, handler_event: Any) -> dict[str, Any]:
        """Coerce, normalise, and append a handler event to the context.

        Also propagates the event into the background record when one is active.

        :param ctx: Current execution context.
        :type ctx: _ExecutionContext
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
            sequence_number=len(ctx.handler_events),
        )
        ctx.handler_events.append(normalized)
        if ctx.bg_record is not None and ctx.bg_record.status != "cancelled":
            ctx.bg_record.events.append(deepcopy(normalized))
            event_type = normalized.get("type")
            payload = normalized.get("payload", {})
            if event_type in _RESPONSE_SNAPSHOT_EVENT_TYPES:
                # response.* lifecycle event: replace the entire snapshot (S-013)
                ctx.bg_record.response_payload = _extract_response_snapshot_from_events(
                    ctx.handler_events,
                    response_id=ctx.response_id,
                    agent_reference=ctx.agent_reference,
                    model=ctx.model,
                )
                resolved = ctx.bg_record.response_payload.get("status")
                if isinstance(resolved, str):
                    ctx.bg_record.status = resolved
            elif event_type == EVENT_TYPE.RESPONSE_OUTPUT_ITEM_ADDED.value:
                # Accumulate output items between response.* events (S-014)
                item = payload.get("item")
                if isinstance(item, dict) and isinstance(ctx.bg_record.response_payload, dict):
                    output = ctx.bg_record.response_payload.setdefault("output", [])
                    output.append(deepcopy(item))
            elif event_type == EVENT_TYPE.RESPONSE_OUTPUT_ITEM_DONE.value:
                # Update tracked output item at its index
                item = payload.get("item")
                output_index = payload.get("output_index")
                if (
                    isinstance(item, dict)
                    and isinstance(output_index, int)
                    and isinstance(ctx.bg_record.response_payload, dict)
                ):
                    output = ctx.bg_record.response_payload.get("output", [])
                    if 0 <= output_index < len(output):
                        output[output_index] = deepcopy(item)
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

    def _cancel_terminal_sse(self, ctx: _ExecutionContext) -> str:
        """Build and record a ``response.failed`` cancel-terminal SSE string.

        :param ctx: Current execution context.
        :type ctx: _ExecutionContext
        :return: Encoded SSE string for the cancel-terminal event.
        :rtype: str
        """
        cancel_event: dict[str, Any] = {
            "type": EVENT_TYPE.RESPONSE_FAILED.value,
            "payload": {
                "id": ctx.response_id,
                "object": "response",
                "status": "cancelled",
                "output": [],
            },
        }
        normalized = _apply_stream_event_defaults(
            cancel_event,
            response_id=ctx.response_id,
            agent_reference=ctx.agent_reference,
            model=ctx.model,
            sequence_number=len(ctx.handler_events),
        )
        ctx.handler_events.append(normalized)
        if ctx.bg_record is not None and ctx.bg_record.status != "cancelled":
            ctx.bg_record.events.append(deepcopy(normalized))
        return encode_sse_payload(normalized["type"], normalized["payload"])

    async def _finalize_stream(self, ctx: _ExecutionContext) -> None:
        """Persist the execution record and close the observability span.

        Called from the ``finally`` block of :meth:`_live_stream`.

        :param ctx: Current execution context.
        :type ctx: _ExecutionContext
        """
        if ctx.bg_record is not None:
            # Background+stream: record was created at response.created time.
            # Update terminal state unless cancel endpoint already set the final state.
            if ctx.bg_record.status != "cancelled":
                events = ctx.handler_events if ctx.handler_events else _build_events(
                    ctx.response_id,
                    include_progress=True,
                    agent_reference=ctx.agent_reference,
                    model=ctx.model,
                )
                if ctx.captured_error is not None:
                    ctx.bg_record.status = "failed"
                    ctx.bg_record.response_payload = {
                        "id": ctx.response_id,
                        "response_id": ctx.response_id,
                        "agent_reference": deepcopy(ctx.agent_reference),
                        "object": "response",
                        "status": "failed",
                        "model": ctx.model,
                        "output": [],
                        "created_at": ctx.context.created_at,
                        "error": {"code": "server_error", "message": "An internal server error occurred."},
                    }
                else:
                    response_payload = _extract_response_snapshot_from_events(
                        events,
                        response_id=ctx.response_id,
                        agent_reference=ctx.agent_reference,
                        model=ctx.model,
                    )
                    resolved_status = response_payload.get("status")
                    status = resolved_status if isinstance(resolved_status, str) else "in_progress"
                    ctx.bg_record.response_payload = response_payload
                    ctx.bg_record.status = status
                ctx.bg_record.events = deepcopy(ctx.handler_events) if ctx.handler_events else []
            ctx.span.end(ctx.captured_error)
            return

        events = ctx.handler_events if ctx.handler_events else _build_events(
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
        )
        resolved_status = response_payload.get("status")
        status = (
            resolved_status
            if isinstance(resolved_status, str)
            else ("in_progress" if ctx.background else "completed")
        )
        if ctx.store:
            stream_record = _ExecutionRecord(
                response_id=ctx.response_id,
                agent_reference=deepcopy(ctx.agent_reference),
                stream=True,
                store=True,
                background=ctx.background,
                replay_enabled=ctx.background,
                visible_via_get=True,
                status=status,
                model=ctx.model,
                response_payload=response_payload,
                events=deepcopy(events) if ctx.background else [],
                input_items=deepcopy(ctx.input_items),
                previous_response_id=ctx.previous_response_id,
            )
            await self._runtime_state.add(stream_record)
        ctx.span.end(ctx.captured_error)

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

    async def _live_stream(self, ctx: _ExecutionContext) -> AsyncIterator[str]:  # pylint: disable=too-many-statements
        new_stream_counter()
        handler_iterator = self._create_async(ctx.parsed, ctx.context, ctx.cancellation_signal)

        # --- Try to obtain the first event ---
        try:
            first_handler_event = await handler_iterator.__anext__()
        except StopAsyncIteration:
            # Handler yielded nothing: synthesise fallback events.
            fallback_events = _build_events(
                ctx.response_id,
                include_progress=True,
                agent_reference=ctx.agent_reference,
                model=ctx.model,
            )
            try:
                for event in fallback_events:
                    yield encode_sse_payload(event["type"], event["payload"])
            finally:
                await self._finalize_stream(ctx)
            return
        except Exception as exc:  # pylint: disable=broad-exception-caught
            ctx.captured_error = exc
            # B8: Pre-creation error → emit a standalone `error` SSE event only.
            # No response.created precedes it; this is the contract-mandated shape.
            # Note: do NOT include "type" in payload — encode_sse_payload uses the first
            # argument as the SSE event type; a "type" key in payload would override it.
            try:
                yield encode_sse_payload(
                    EVENT_TYPE.ERROR.value,
                    {"message": "An internal server error occurred.", "param": None, "code": None},
                )
            finally:
                await self._finalize_stream(ctx)
            return

        # --- Normalise the first event ---
        first_normalized = _apply_stream_event_defaults(
            _coerce_handler_event(first_handler_event),
            response_id=ctx.response_id,
            agent_reference=ctx.agent_reference,
            model=ctx.model,
            sequence_number=0,
        )
        ctx.handler_events.append(first_normalized)

        # --- For background+stream: create and store the initial record ---
        if ctx.background and ctx.store:
            initial_payload = _extract_response_snapshot_from_events(
                ctx.handler_events,
                response_id=ctx.response_id,
                agent_reference=ctx.agent_reference,
                model=ctx.model,
            )
            initial_status = initial_payload.get("status")
            if not isinstance(initial_status, str):
                initial_status = "in_progress"
            ctx.bg_record = _ExecutionRecord(
                response_id=ctx.response_id,
                agent_reference=deepcopy(ctx.agent_reference),
                stream=True,
                store=True,
                background=True,
                replay_enabled=True,
                visible_via_get=True,
                status=initial_status,
                model=ctx.model,
                response_payload=initial_payload,
                events=[deepcopy(first_normalized)],
                input_items=deepcopy(ctx.input_items),
                previous_response_id=ctx.previous_response_id,
                cancel_signal=ctx.cancellation_signal,
            )
            await self._runtime_state.add(ctx.bg_record)

        # --- Fast path: no keep-alive ---
        if not self._runtime_options.sse_keep_alive_enabled:
            try:
                yield encode_sse_payload(first_normalized["type"], first_normalized["payload"])
                async for handler_event in handler_iterator:
                    normalized = self._normalize_and_append(ctx, handler_event)
                    yield encode_sse_payload(normalized["type"], normalized["payload"])
                if ctx.cancellation_signal.is_set() and not self._has_terminal_event(ctx.handler_events):
                    yield self._cancel_terminal_sse(ctx)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                ctx.captured_error = exc
                # B-13: emit response.failed when handler raises after response.created
                if not self._has_terminal_event(ctx.handler_events):
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
                    normalized_failed = self._normalize_and_append(ctx, failed_event)
                    yield encode_sse_payload(normalized_failed["type"], normalized_failed["payload"])
                return
            finally:
                await self._finalize_stream(ctx)
            return

        # --- Keep-alive path: merge handler events with periodic keep-alive comments ---
        # via a shared queue so comments are sent even while the handler is idle.
        _SENTINEL = object()
        merge_queue: asyncio.Queue[str | object] = asyncio.Queue()
        handler_error: list[Exception] = []

        async def _handler_producer() -> None:
            try:
                async for handler_event in handler_iterator:
                    normalized = self._normalize_and_append(ctx, handler_event)
                    await merge_queue.put(encode_sse_payload(normalized["type"], normalized["payload"]))
            except Exception as exc:  # pylint: disable=broad-exception-caught
                handler_error.append(exc)
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
            yield encode_sse_payload(first_normalized["type"], first_normalized["payload"])
            while True:
                item = await merge_queue.get()
                if item is _SENTINEL:
                    break
                yield item  # type: ignore[misc]
            if handler_error:
                ctx.captured_error = handler_error[0]
                # B-13: emit response.failed when handler raises after response.created
                if not self._has_terminal_event(ctx.handler_events):
                    failed_event = {
                        "type": EVENT_TYPE.RESPONSE_FAILED.value,
                        "payload": {
                            "id": ctx.response_id,
                            "object": "response",
                            "status": "failed",
                            "output": [],
                            "error": {"code": "server_error", "message": "An internal server error occurred."},
                        },
                    }
                    normalized_failed = self._normalize_and_append(ctx, failed_event)
                    yield encode_sse_payload(normalized_failed["type"], normalized_failed["payload"])
            elif ctx.cancellation_signal.is_set() and not self._has_terminal_event(ctx.handler_events):
                yield self._cancel_terminal_sse(ctx)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            ctx.captured_error = exc
        finally:
            keep_alive_task.cancel()
            try:
                await keep_alive_task
            except asyncio.CancelledError:
                pass
            # Ensure the handler task has finished
            if not handler_task.done():
                handler_task.cancel()
                try:
                    await handler_task
                except asyncio.CancelledError:
                    pass

            await self._finalize_stream(ctx)

    async def run_sync(self, ctx: _ExecutionContext) -> dict[str, Any]:
        """Execute a synchronous (non-stream, non-background) create-response request.

        Collects all handler events, builds the response snapshot, optionally
        persists the record, closes the span, and returns the snapshot dict.

        Raises :class:`_HandlerError` if the handler raises so the caller can
        map it to an HTTP error response.

        :param ctx: Current execution context.
        :type ctx: _ExecutionContext
        :return: Response snapshot dictionary.
        :rtype: dict[str, Any]
        :raises _HandlerError: If the handler raises during iteration.
        """
        try:
            async for handler_event in self._create_async(ctx.parsed, ctx.context, ctx.cancellation_signal):
                coerced = _coerce_handler_event(handler_event)
                normalized = _apply_stream_event_defaults(
                    coerced,
                    response_id=ctx.response_id,
                    agent_reference=ctx.agent_reference,
                    model=ctx.model,
                    sequence_number=None,
                )
                ctx.handler_events.append(normalized)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            ctx.captured_error = exc
            ctx.span.end(ctx.captured_error)
            raise _HandlerError(exc) from exc

        events = ctx.handler_events if ctx.handler_events else _build_events(
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
        )
        resolved_status = response_payload.get("status")
        status = resolved_status if isinstance(resolved_status, str) else "completed"

        record = _ExecutionRecord(
            response_id=ctx.response_id,
            agent_reference=deepcopy(ctx.agent_reference),
            stream=False,
            store=ctx.store,
            background=False,
            replay_enabled=False,
            visible_via_get=ctx.store,
            status=status,
            model=ctx.model,
            response_payload=response_payload,
            input_items=deepcopy(ctx.input_items),
            previous_response_id=ctx.previous_response_id,
            response_context=ctx.context,
        )

        if ctx.store:
            await self._runtime_state.add(record)

        ctx.span.end(ctx.captured_error)
        return record.to_snapshot()

    async def run_background(self, ctx: _ExecutionContext) -> dict[str, Any]:
        """Handle a background (non-stream) create-response request.

        Creates a queued execution record with an attached background runner,
        stores it, and returns the initial snapshot dict immediately.

        :param ctx: Current execution context.
        :type ctx: _ExecutionContext
        :return: Initial queued response snapshot dictionary.
        :rtype: dict[str, Any]
        """
        record = _ExecutionRecord(
            response_id=ctx.response_id,
            agent_reference=deepcopy(ctx.agent_reference),
            stream=False,
            store=ctx.store,
            background=True,
            replay_enabled=False,
            visible_via_get=ctx.store,
            status="queued",
            model=ctx.model,
            input_items=deepcopy(ctx.input_items),
            previous_response_id=ctx.previous_response_id,
            response_context=ctx.context,
        )

        async def _background_runner() -> None:
            await _run_background_non_stream(
                create_async=self._create_async,
                parsed=ctx.parsed,
                context=ctx.context,
                cancellation_signal=ctx.cancellation_signal,
                record=record,
                response_id=ctx.response_id,
                agent_reference=ctx.agent_reference,
                model=ctx.model,
            )

        record.background_runner = _background_runner

        if ctx.store:
            await self._runtime_state.add(record)

        ctx.span.end(ctx.captured_error)
        return record.to_snapshot()
