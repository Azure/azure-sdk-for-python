# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""HTTP endpoint handler for the Responses server.

This module owns all Starlette I/O: ``Request`` parsing, route-level
validation, header propagation, and ``Response`` construction.  Business
logic lives in :class:`_ResponseOrchestrator`.
"""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
from copy import deepcopy
from typing import TYPE_CHECKING, Any

from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from azure.ai.agentserver.hosting import AgentLogger

from .._response_context import ResponseContext
from .._options import ResponsesServerOptions
from ..models import ResponseModeFlags
from ..streaming._helpers import _encode_sse
from ..streaming._sse import encode_sse_payload
from ..streaming._state_machine import LifecycleStateMachineError, normalize_lifecycle_events
from ._background import _refresh_background_status
from ._execution_context import _ExecutionContext
from ..models.runtime import build_cancelled_response
from ._http_errors import (
    _deleted_response,
    _error_response,
    _invalid_mode,
    _invalid_request,
    _not_found,
    _service_unavailable,
)
from ._observability import build_create_span_tags, start_create_span
from ._orchestrator import _HandlerError, _ResponseOrchestrator
from ._request_parsing import (
    _apply_item_cursors,
    _extract_item_id,
    _prevalidate_identity_payload,
    _resolve_conversation_id,
    _resolve_identity_fields,
)
from ._runtime_state import _RuntimeState
from ._validation import parse_and_validate_create_response
from ..store._base import ResponseProviderProtocol, ResponseStreamProviderProtocol
from ..streaming._helpers import EVENT_TYPE

if TYPE_CHECKING:
    from azure.ai.agentserver.hosting import TracingHelper

logger = AgentLogger.get()


class _ResponseEndpointHandler:  # pylint: disable=too-many-instance-attributes
    """HTTP-layer handler for all Responses API endpoints.

    Owns all Starlette ``Request``/``Response`` concerns.  Delegates
    event-pipeline logic to :class:`_ResponseOrchestrator`.

    Mutable shutdown state (``_is_draining``, ``_shutdown_requested``) lives
    here so every route method shares consistent drain/cancel semantics without
    needing a ``nonlocal`` closure variable.
    """

    def __init__(
        self,
        *,
        orchestrator: _ResponseOrchestrator,
        runtime_state: _RuntimeState,
        runtime_options: ResponsesServerOptions,
        response_headers: dict[str, str],
        sse_headers: dict[str, str],
        tracing: "TracingHelper | None" = None,
        provider: ResponseProviderProtocol,
        stream_provider: ResponseStreamProviderProtocol | None = None,
    ) -> None:
        """Initialise the endpoint handler.

        :param orchestrator: Event-pipeline orchestrator.
        :type orchestrator: _ResponseOrchestrator
        :param runtime_state: In-memory execution record store.
        :type runtime_state: _RuntimeState
        :param runtime_options: Server runtime options.
        :type runtime_options: ResponsesServerOptions
        :param response_headers: Headers to include on all responses.
        :type response_headers: dict[str, str]
        :param sse_headers: SSE-specific headers (e.g. connection, cache-control).
        :type sse_headers: dict[str, str]
        :param tracing: Optional tracing helper from hosting's AgentServer.
        :type tracing: TracingHelper | None
        :param provider: Persistence provider for response envelopes and input items.
        :type provider: ResponseProviderProtocol
        :param stream_provider: Optional provider for SSE stream event persistence and replay.
        :type stream_provider: ResponseStreamProviderProtocol | None
        """
        self._orchestrator = orchestrator
        self._runtime_state = runtime_state
        self._runtime_options = runtime_options
        self._response_headers = response_headers
        self._sse_headers = sse_headers
        self._tracing = tracing
        self._provider = provider
        self._stream_provider = stream_provider
        self._shutdown_requested: asyncio.Event = asyncio.Event()
        self._is_draining: bool = False

        # Validate the lifecycle event state machine on startup so
        # misconfigured state machines surface immediately.
        try:
            normalize_lifecycle_events(
                response_id="resp_validation",
                events=[
                    {"type": EVENT_TYPE.RESPONSE_CREATED.value, "payload": {"status": "queued"}},
                    {"type": EVENT_TYPE.RESPONSE_COMPLETED.value, "payload": {"status": "completed"}},
                ],
            )
        except LifecycleStateMachineError as exc:
            raise RuntimeError(f"Invalid lifecycle event state machine configuration: {exc}") from exc

    # ------------------------------------------------------------------
    # Span attribute helper
    # ------------------------------------------------------------------

    @staticmethod
    def _safe_set_attrs(span: Any, attrs: dict[str, str]) -> None:
        """Safely set attributes on an OTel span.

        :param span: The OTel span, or *None*.
        :type span: Any
        :param attrs: Key-value attributes to set.
        :type attrs: dict[str, str]
        """
        if span is None:
            return
        try:
            for key, value in attrs.items():
                span.set_attribute(key, value)
        except Exception:  # pylint: disable=broad-exception-caught
            logger.debug("Failed to set span attributes: %s", list(attrs.keys()), exc_info=True)

    # ------------------------------------------------------------------
    # Streaming response helpers
    # ------------------------------------------------------------------

    def _wrap_streaming_response(
        self,
        response: StreamingResponse,
        otel_span: Any,
        baggage_token: Any,
    ) -> StreamingResponse:
        """Wrap a streaming response's body iterator with tracing and baggage cleanup.

        Two layers of wrapping are applied in order:

        1. **Inner (tracing):** ``trace_stream`` wraps the body iterator so
           the OTel span covers the full streaming duration and records any
           errors that occur while yielding chunks.
        2. **Outer (baggage cleanup):** A second async generator detaches the
           W3C Baggage context *after* all chunks have been sent (or an
           error occurs).

        :param response: The ``StreamingResponse`` to wrap.
        :type response: StreamingResponse
        :param otel_span: The OTel span (or *None* when tracing is disabled).
        :type otel_span: Any
        :param baggage_token: Token from ``set_baggage`` (or *None*).
        :type baggage_token: Any
        :return: The same response object, with its body_iterator replaced.
        :rtype: StreamingResponse
        """
        if self._tracing is None:
            return response

        # Inner wrap: trace_stream ends the span when iteration completes.
        response.body_iterator = self._tracing.trace_stream(response.body_iterator, otel_span)

        # Outer wrap: detach baggage after all chunks are sent.
        original_iterator = response.body_iterator
        tracing = self._tracing  # capture for the closure

        async def _cleanup_iter():  # type: ignore[return-value]
            try:
                async for chunk in original_iterator:
                    yield chunk
            finally:
                tracing.detach_baggage(baggage_token)

        response.body_iterator = _cleanup_iter()
        return response

    # ------------------------------------------------------------------
    # ResponseContext factory
    # ------------------------------------------------------------------

    def _create_response_context(
        self,
        *,
        response_id: str,
        raw_body: Any,
        parsed: Any,
        request: Request,
    ) -> ResponseContext:
        """Build a :class:`ResponseContext` from the incoming HTTP request.

        Extracts mode flags, input items, conversation threading fields,
        ``x-client-*`` headers, and query parameters from the raw and
        parsed request objects.

        :param response_id: The assigned response identifier.
        :param raw_body: The raw JSON payload dict.
        :param parsed: The validated :class:`CreateResponse` model.
        :param request: The Starlette HTTP request.
        :return: A fully-populated :class:`ResponseContext`.
        """
        stream = bool(getattr(parsed, "stream", False))
        store = True if getattr(parsed, "store", None) is None else bool(parsed.store)
        background = bool(getattr(parsed, "background", False))
        input_items = [deepcopy(item) for item in (parsed.input or []) if isinstance(item, dict)]
        previous_response_id: str | None = (
            parsed.previous_response_id
            if isinstance(parsed.previous_response_id, str) and parsed.previous_response_id
            else None
        )
        mode_flags = ResponseModeFlags(stream=stream, store=store, background=background)
        client_headers = {
            k: v for k, v in request.headers.items()
            if k.lower().startswith("x-client-")
        }
        query_parameters = dict(request.query_params)

        context = ResponseContext(
            response_id=response_id,
            mode_flags=mode_flags,
            raw_body=raw_body,
            request=parsed,
            provider=self._provider,
            input_items=input_items,
            previous_response_id=previous_response_id,
            conversation_id=_resolve_conversation_id(parsed),
            history_limit=self._runtime_options.default_fetch_history_count,
            client_headers=client_headers,
            query_parameters=query_parameters,
        )
        context.is_shutdown_requested = self._shutdown_requested.is_set()
        return context

    # ------------------------------------------------------------------
    # Route handlers
    # ------------------------------------------------------------------

    async def handle_create(self, request: Request) -> Response:  # pylint: disable=too-many-return-statements
        """Route handler for ``POST /responses``.

        Parses and validates the create request, builds an
        :class:`_ExecutionContext`, then dispatches to the appropriate
        orchestrator method (stream / sync / background).

        :param request: Incoming Starlette request.
        :type request: Request
        :return: HTTP response for the create operation.
        :rtype: Response
        """
        if self._is_draining:
            return _service_unavailable("Server is shutting down.", {})

        # Start tracing span using hosting's TracingHelper
        otel_span = None
        baggage_token = None
        streaming_wrapped = False

        # Also maintain CreateSpanHook for backward compat (tests etc.)
        span = start_create_span(
            "create_response",
            build_create_span_tags(
                response_id=None,
                model=None,
                agent_reference=None,
                service_name="azure-ai-agentserver-responses",
            ),
            hook=self._runtime_options.create_span_hook,
        )
        captured_error: Exception | None = None

        try:
            payload = await request.json()
            _prevalidate_identity_payload(payload)
            parsed = parse_and_validate_create_response(payload, options=self._runtime_options)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            captured_error = exc
            span.end(captured_error)
            if self._tracing is not None:
                self._tracing.end_span(otel_span, exc=exc)
            return _error_response(exc, {})

        try:
            response_id, agent_reference = _resolve_identity_fields(parsed)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            captured_error = exc
            span.end(captured_error)
            if self._tracing is not None:
                self._tracing.end_span(otel_span, exc=exc)
            return _error_response(exc, {})

        stream = bool(getattr(parsed, "stream", False))
        store = True if getattr(parsed, "store", None) is None else bool(parsed.store)
        background = bool(getattr(parsed, "background", False))
        model = getattr(parsed, "model", None)
        input_items = [deepcopy(item) for item in (parsed.input or []) if isinstance(item, dict)]
        previous_response_id: str | None = (
            parsed.previous_response_id
            if isinstance(parsed.previous_response_id, str) and parsed.previous_response_id
            else None
        )
        context = self._create_response_context(
            response_id=response_id,
            raw_body=payload,
            parsed=parsed,
            request=request,
        )

        cancellation_signal = asyncio.Event()
        if context.is_shutdown_requested:
            cancellation_signal.set()

        # Start OTel request span now that we have the response_id
        if self._tracing is not None:
            otel_span = self._tracing.start_request_span(
                request.headers,
                response_id,
                span_operation="create_response",
                operation_name="create_response",
            )
            self._safe_set_attrs(otel_span, {
                "gen_ai.response.id": response_id,
                "gen_ai.request.model": model or "",
            })
            baggage_token = self._tracing.set_baggage({
                "response_id": response_id,
            })

        span.set_tags(
            build_create_span_tags(
                response_id=response_id,
                model=model,
                agent_reference=agent_reference,
                service_name="azure-ai-agentserver-responses",
            )
        )

        ctx = _ExecutionContext(
            response_id=response_id,
            agent_reference=agent_reference,
            model=model,
            store=store,
            background=background,
            stream=stream,
            input_items=input_items,
            previous_response_id=previous_response_id,
            cancellation_signal=cancellation_signal,
            context=context,
            span=span,
            parsed=parsed,
        )

        try:
            if stream:
                sse_response = StreamingResponse(
                    self._orchestrator.run_stream(ctx),
                    media_type="text/event-stream",
                    headers=self._sse_headers,
                )
                wrapped = self._wrap_streaming_response(sse_response, otel_span, baggage_token)
                streaming_wrapped = True
                return wrapped

            if not background:
                try:
                    snapshot = await self._orchestrator.run_sync(ctx)
                    # End OTel span for non-streaming success
                    if self._tracing is not None:
                        self._tracing.end_span(otel_span)
                    return JSONResponse(snapshot, status_code=200)
                except _HandlerError as exc:
                    if self._tracing is not None:
                        self._tracing.end_span(otel_span, exc=exc.original)
                    return _error_response(exc.original, {})

            snapshot = await self._orchestrator.run_background(ctx)
            if self._tracing is not None:
                self._tracing.end_span(otel_span)
            return JSONResponse(snapshot, status_code=200, headers=self._response_headers)
        except _HandlerError as exc:
            if self._tracing is not None:
                self._tracing.end_span(otel_span, exc=exc)
            return _error_response(exc.original, self._response_headers)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            if self._tracing is not None:
                self._tracing.end_span(otel_span, exc=exc)
            raise
        finally:
            # For non-streaming responses (or error paths that returned
            # before reaching _wrap_streaming_response), detach baggage
            # immediately.  Streaming responses handle this in
            # _wrap_streaming_response's cleanup iterator instead.
            if not streaming_wrapped:
                if self._tracing is not None:
                    self._tracing.detach_baggage(baggage_token)

    async def handle_get(self, request: Request) -> Response:  # pylint: disable=too-many-return-statements
        """Route handler for ``GET /responses/{response_id}``.

        Returns the response snapshot or replays SSE events if
        ``stream=true`` is in the query parameters.

        :param request: Incoming Starlette request.
        :type request: Request
        :return: JSON snapshot or SSE replay streaming response.
        :rtype: Response
        """
        response_id = request.path_params["response_id"]
        record = await self._runtime_state.get(response_id)
        if record is None:
            if await self._runtime_state.is_deleted(response_id):
                return _deleted_response(response_id, {})

            stream_replay = request.query_params.get("stream", "false").lower() == "true"
            if not stream_replay:
                # Provider fallback: serve completed responses that are no longer in runtime state
                # (e.g., after a process restart).
                try:
                    response_obj = await self._provider.get_response_async(response_id)
                    snapshot = response_obj.as_dict()
                    return JSONResponse(snapshot, status_code=200)
                except Exception:  # pylint: disable=broad-exception-caught
                    pass
            else:
                # Stream provider fallback: replay persisted SSE events when runtime state is gone.
                if self._stream_provider is not None:
                    try:
                        replay_events = await self._stream_provider.get_stream_events_async(response_id)
                        if replay_events is not None:
                            cursor_raw = request.query_params.get("starting_after")
                            starting_after = -1
                            if cursor_raw is not None:
                                try:
                                    starting_after = int(cursor_raw)
                                except ValueError:
                                    return _invalid_request(
                                        "starting_after must be an integer",
                                        {},
                                        param="starting_after",
                                    )
                            filtered = [
                                e for e in replay_events
                                if e["payload"]["sequence_number"] > starting_after
                            ]
                            return StreamingResponse(
                                _encode_sse(filtered),
                                media_type="text/event-stream",
                                headers=self._sse_headers,
                            )
                    except Exception:  # pylint: disable=broad-exception-caught
                        pass

            return _not_found(response_id, {})

        _refresh_background_status(record)

        stream_replay = request.query_params.get("stream", "false").lower() == "true"
        if stream_replay:
            if not record.replay_enabled:
                return _invalid_mode(
                    "stream replay is not available for this response; to enable SSE replay, "
                    + "create the response with background=true",
                    {},
                    param="stream",
                )

            cursor_raw = request.query_params.get("starting_after")
            starting_after = -1
            if cursor_raw is not None:
                try:
                    starting_after = int(cursor_raw)
                except ValueError:
                    return _invalid_request(
                        "starting_after must be an integer",
                        {},
                        param="starting_after",
                    )

            # Live subscription: delivers buffered history + ongoing live events,
            # then exits when the stream completes.
            _cursor = starting_after

            async def _stream_from_subject():
                async for event in record.subject.subscribe(cursor=_cursor):  # type: ignore[union-attr]
                    yield encode_sse_payload(event["type"], event["payload"])

            return StreamingResponse(
                _stream_from_subject(), media_type="text/event-stream", headers=self._sse_headers
            )

        if not record.visible_via_get:
            return _not_found(response_id, {})

        return JSONResponse(_RuntimeState.to_snapshot(record), status_code=200, headers=self._response_headers)

    async def handle_delete(self, request: Request) -> Response:
        """Route handler for ``DELETE /responses/{response_id}``.

        :param request: Incoming Starlette request.
        :type request: Request
        :return: Deletion confirmation or error response.
        :rtype: Response
        """
        response_id = request.path_params["response_id"]
        record = await self._runtime_state.get(response_id)
        if record is None:
            return _not_found(response_id, {})

        _refresh_background_status(record)

        if record.mode_flags.background and record.status in {"queued", "in_progress"}:
            return _invalid_request(
                "Cannot delete an in-flight response.",
                {},
                param="response_id",
            )

        deleted = await self._runtime_state.delete(response_id)
        if not deleted:
            return _not_found(response_id, {})

        if record.mode_flags.store:
            try:
                await self._provider.delete_response_async(response_id)
            except Exception:  # pylint: disable=broad-exception-caught
                pass  # best effort: provider may not have the record if response was not persisted

        return JSONResponse(
            {"id": response_id, "object": "response.deleted", "deleted": True},
            status_code=200,
        )

    async def handle_cancel(self, request: Request) -> Response:  # pylint: disable=too-many-return-statements
        """Route handler for ``POST /responses/{response_id}/cancel``.

        :param request: Incoming Starlette request.
        :type request: Request
        :return: Cancelled snapshot or error response.
        :rtype: Response
        """
        response_id = request.path_params["response_id"]
        record = await self._runtime_state.get(response_id)
        if record is None:
            return _not_found(response_id, {})

        _refresh_background_status(record)

        if not record.mode_flags.background:
            return _invalid_request(
                "Cannot cancel a synchronous response.",
                {},
                param="response_id",
            )

        if record.status == "cancelled":
            # Idempotent: ensure the response snapshot reflects cancelled state
            record.set_response_snapshot(
                build_cancelled_response(record.response_id, record.agent_reference, record.model)
            )
            return JSONResponse(_RuntimeState.to_snapshot(record), status_code=200, headers=self._response_headers)

        if record.status == "completed":
            return _invalid_request(
                "Cannot cancel a completed response.",
                {},
                param="response_id",
            )

        if record.status == "failed":
            return _invalid_request(
                "Cannot cancel a failed response.",
                {},
                param="response_id",
            )

        if record.status == "incomplete":
            return _invalid_request(
                "Cannot cancel an incomplete response.",
                {},
                param="response_id",
            )

        record.set_response_snapshot(
            build_cancelled_response(record.response_id, record.agent_reference, record.model)
        )
        record.cancel_signal.set()
        record.transition_to("cancelled")
        return JSONResponse(_RuntimeState.to_snapshot(record), status_code=200, headers=self._response_headers)

    async def handle_input_items(self, request: Request) -> Response:
        """Route handler for ``GET /responses/{response_id}/input_items``.

        Returns a paginated list of input items for the given response.

        :param request: Incoming Starlette request.
        :type request: Request
        :return: Paginated input items list.
        :rtype: Response
        """
        response_id = request.path_params["response_id"]

        limit_raw = request.query_params.get("limit", "20")
        try:
            limit = int(limit_raw)
        except ValueError:
            return _invalid_request(
                "limit must be an integer between 1 and 100", {}, param="limit"
            )

        if limit < 1 or limit > 100:
            return _invalid_request(
                "limit must be between 1 and 100", {}, param="limit"
            )

        order = request.query_params.get("order", "desc").lower()
        if order not in {"asc", "desc"}:
            return _invalid_request("order must be 'asc' or 'desc'", {}, param="order")

        after = request.query_params.get("after")
        before = request.query_params.get("before")

        try:
            items = await self._provider.get_input_items_async(
                response_id, limit=100, ascending=True
            )
        except ValueError:
            return _deleted_response(response_id, {})
        except KeyError:
            # Fall back to runtime_state for in-flight responses not yet persisted to provider
            try:
                items = await self._runtime_state.get_input_items(response_id)
            except ValueError:
                return _deleted_response(response_id, {})
            except KeyError:
                return _not_found(response_id, {})

        ordered_items = items if order == "asc" else list(reversed(items))
        scoped_items = _apply_item_cursors(ordered_items, after=after, before=before)

        page = scoped_items[:limit]
        has_more = len(scoped_items) > limit

        first_id = _extract_item_id(page[0]) if page else None
        last_id = _extract_item_id(page[-1]) if page else None

        return JSONResponse(
            {
                "object": "list",
                "data": page,
                "first_id": first_id,
                "last_id": last_id,
                "has_more": has_more,
            },
            status_code=200,
        )

    async def handle_shutdown(self) -> None:
        """Graceful shutdown handler.

        Signals all active responses to cancel and waits for in-flight
        background executions to complete within the configured grace period.

        :return: None
        :rtype: None
        """
        self._is_draining = True
        self._shutdown_requested.set()

        records = await self._runtime_state.list_records()
        for record in records:
            if record.response_context is not None:
                record.response_context.is_shutdown_requested = True

            record.cancel_signal.set()

            if record.mode_flags.background and record.status in {"queued", "in_progress"}:
                record.set_response_snapshot(
                    build_cancelled_response(record.response_id, record.agent_reference, record.model)
                )
                record.transition_to("cancelled")

        deadline = asyncio.get_running_loop().time() + float(
            self._runtime_options.shutdown_grace_period_seconds
        )
        while True:
            pending = [
                record
                for record in records
                if record.mode_flags.background
                and record.execution_task is not None
                and record.status in {"queued", "in_progress"}
            ]
            if not pending:
                break
            if asyncio.get_running_loop().time() >= deadline:
                break
            await asyncio.sleep(0.05)
