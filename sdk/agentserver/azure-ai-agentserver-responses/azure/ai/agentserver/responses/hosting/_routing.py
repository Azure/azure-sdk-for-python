# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Starlette hosting integration for the Responses server package."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import sys
from contextlib import asynccontextmanager
from copy import deepcopy
from typing import TYPE_CHECKING, Any, AsyncIterator

from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from .._handlers import RuntimeResponseContext
from ._observability import build_create_span_tags, build_platform_server_header, start_create_span
from .._options import ResponsesServerOptions
from ..streaming._sse import encode_keep_alive_comment, encode_sse_payload
from ..streaming._state_machine import LifecycleStateMachineError, normalize_lifecycle_events
from ._validation import parse_and_validate_create_response
from ..models import ResponseModeFlags
from ._background import _refresh_background_status, _run_background_non_stream, _try_execute_background_runner
from ..streaming._helpers import (
    EVENT_TYPE,
    _RESPONSE_SNAPSHOT_EVENT_TYPES,
    _apply_stream_event_defaults,
    _build_events,
    _coerce_handler_event,
    _encode_sse,
    _extract_response_snapshot_from_events,
)
from ._http_errors import (
    _deleted_response,
    _error_response,
    _invalid_mode,
    _invalid_request,
    _not_found,
    _service_unavailable,
)
from ._request_parsing import (
    _apply_item_cursors,
    _extract_input_items,
    _extract_item_id,
    _extract_previous_response_id,
    _prevalidate_identity_payload,
    _resolve_identity_fields,
)
from ._runtime_state import _ExecutionRecord, _RuntimeState
from .._version import VERSION

if TYPE_CHECKING:
    from starlette.applications import Starlette

    from .._handlers import ResponseHandler


_SDK_NAME = "azure-ai-agentserver-responses"
_SDK_VERSION = VERSION


def _runtime_marker() -> str:
    """Build the Python runtime version marker string.

    :return: A string like ``"python/3.12"``.
    :rtype: str
    """
    return f"python/{sys.version_info.major}.{sys.version_info.minor}"


def _platform_header(options: ResponsesServerOptions) -> str:
    """Build the ``x-platform-server`` header value from runtime options.

    :param options: Server runtime options.
    :type options: ResponsesServerOptions
    :return: Formatted platform server identity header string.
    :rtype: str
    """
    return build_platform_server_header(
        sdk_name=_SDK_NAME,
        version=_SDK_VERSION,
        runtime=_runtime_marker(),
        extra=options.additional_server_identity,
    )


def map_responses_server(  # pylint: disable=too-many-statements
    app: "Starlette",
    handler: "ResponseHandler",
    *,
    prefix: str = "",
    options: ResponsesServerOptions | None = None,
) -> None:
    """Register Responses API routes on a Starlette application.

    :param app: Starlette application instance to configure.
    :type app: Starlette
    :param handler: User-provided response handler implementation.
    :type handler: ResponseHandler
    :keyword prefix: Optional route prefix.
    :keyword type prefix: str
    :keyword options: Optional server runtime options.
    :keyword type options: ResponsesServerOptions | None
    """
    if app is None:
        raise ValueError("app is required")

    if handler is None:
        raise ValueError(
            "No ResponseHandler implementation is registered. Provide a handler before calling map_responses_server()."
        )

    create_async = getattr(handler, "create_async", None)
    if not callable(create_async):
        raise TypeError("handler must define create_async(request, context, cancellation_signal)")

    normalized_prefix = prefix.strip()
    if normalized_prefix and not normalized_prefix.startswith("/"):
        normalized_prefix = f"/{normalized_prefix}"
    normalized_prefix = normalized_prefix.rstrip("/")

    runtime_options = options or ResponsesServerOptions()
    runtime_state = _RuntimeState()
    response_headers = {"x-platform-server": _platform_header(runtime_options)}
    shutdown_requested = asyncio.Event()
    runtime_is_draining = False

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

    async def _create_stream(  # pylint: disable=too-many-statements
        *,
        parsed: Any,
        context: RuntimeResponseContext,
        cancellation_signal: asyncio.Event,
        response_id: str,
        agent_reference: Any,
        model: str | None,
        store: bool,
        background: bool,
        input_items: list[Any],
        previous_response_id: str | None,
        span: Any,
        captured_error: Exception | None,
    ) -> Response:
        """Handle a streaming create-response request.

        Invokes the handler's async generator and returns an SSE
        ``StreamingResponse``, optionally storing the execution record.

        :keyword parsed: Parsed ``CreateResponse`` model instance.
        :keyword type parsed: Any
        :keyword context: Runtime response context for this request.
        :keyword type context: RuntimeResponseContext
        :keyword cancellation_signal: Event signalling cancellation.
        :keyword type cancellation_signal: asyncio.Event
        :keyword response_id: The assigned response ID.
        :keyword type response_id: str
        :keyword agent_reference: Normalized agent reference dictionary.
        :keyword type agent_reference: Any
        :keyword model: Model name, or ``None``.
        :keyword type model: str | None
        :keyword store: Whether to persist the execution record.
        :keyword type store: bool
        :keyword background: Whether this is a background request.
        :keyword type background: bool
        :keyword input_items: Extracted input items from the request.
        :keyword type input_items: list[Any]
        :keyword previous_response_id: Previous response ID for chaining, or ``None``.
        :keyword type previous_response_id: str | None
        :keyword span: Active observability span.
        :keyword type span: Any
        :keyword captured_error: Pre-captured error, or ``None``.
        :keyword type captured_error: Exception | None
        :return: An SSE ``StreamingResponse`` or error ``JSONResponse``.
        :rtype: Response
        """
        handler_events: list[dict[str, Any]] = []
        bg_record: _ExecutionRecord | None = None

        def _normalize_and_append(handler_event: Any) -> dict[str, Any]:
            coerced = _coerce_handler_event(handler_event)
            normalized = _apply_stream_event_defaults(
                coerced,
                response_id=response_id,
                agent_reference=agent_reference,
                model=model,
                sequence_number=len(handler_events),
            )
            handler_events.append(normalized)
            if bg_record is not None and bg_record.status != "cancelled":
                bg_record.events.append(deepcopy(normalized))
                event_type = normalized.get("type")
                payload = normalized.get("payload", {})
                if event_type in _RESPONSE_SNAPSHOT_EVENT_TYPES:
                    # response.* lifecycle event: replace the entire snapshot (S-013)
                    bg_record.response_payload = _extract_response_snapshot_from_events(
                        handler_events,
                        response_id=response_id,
                        agent_reference=agent_reference,
                        model=model,
                    )
                    resolved = bg_record.response_payload.get("status")
                    if isinstance(resolved, str):
                        bg_record.status = resolved
                elif event_type == EVENT_TYPE.RESPONSE_OUTPUT_ITEM_ADDED.value:
                    # Accumulate output items between response.* events (S-014)
                    item = payload.get("item")
                    if isinstance(item, dict) and isinstance(bg_record.response_payload, dict):
                        output = bg_record.response_payload.setdefault("output", [])
                        output.append(deepcopy(item))
                elif event_type == EVENT_TYPE.RESPONSE_OUTPUT_ITEM_DONE.value:
                    # Update tracked output item at its index
                    item = payload.get("item")
                    output_index = payload.get("output_index")
                    if (
                        isinstance(item, dict)
                        and isinstance(output_index, int)
                        and isinstance(bg_record.response_payload, dict)
                    ):
                        output = bg_record.response_payload.get("output", [])
                        if 0 <= output_index < len(output):
                            output[output_index] = deepcopy(item)
            return normalized

        async def _finalize_stream() -> None:
            if bg_record is not None:
                # Background+stream: record was created at response.created
                # time.  Update terminal state unless cancel endpoint already
                # set the final state.
                if bg_record.status != "cancelled":
                    events = handler_events if handler_events else _build_events(
                        response_id,
                        include_progress=True,
                        agent_reference=agent_reference,
                        model=model,
                    )
                    if captured_error is not None:
                        bg_record.status = "failed"
                        bg_record.response_payload = {
                            "id": response_id,
                            "response_id": response_id,
                            "agent_reference": deepcopy(agent_reference),
                            "object": "response",
                            "status": "failed",
                            "model": model,
                            "output": [],
                        }
                    else:
                        response_payload = _extract_response_snapshot_from_events(
                            events,
                            response_id=response_id,
                            agent_reference=agent_reference,
                            model=model,
                        )
                        resolved_status = response_payload.get("status")
                        status = resolved_status if isinstance(resolved_status, str) else "in_progress"
                        bg_record.response_payload = response_payload
                        bg_record.status = status
                    bg_record.events = deepcopy(handler_events) if handler_events else []
                span.end(captured_error)
                return

            events = handler_events if handler_events else _build_events(
                response_id,
                include_progress=True,
                agent_reference=agent_reference,
                model=model,
            )
            response_payload = _extract_response_snapshot_from_events(
                events,
                response_id=response_id,
                agent_reference=agent_reference,
                model=model,
            )
            resolved_status = response_payload.get("status")
            status = (
                resolved_status
                if isinstance(resolved_status, str)
                else ("in_progress" if background else "completed")
            )
            if store:
                stream_record = _ExecutionRecord(
                    response_id=response_id,
                    agent_reference=deepcopy(agent_reference),
                    stream=True,
                    store=True,
                    background=background,
                    replay_enabled=background,
                    visible_via_get=True,
                    status=status,
                    model=model,
                    response_payload=response_payload,
                    events=deepcopy(events) if background else [],
                    input_items=deepcopy(input_items),
                    previous_response_id=previous_response_id,
                )
                await runtime_state.add(stream_record)
            span.end(captured_error)

        try:
            handler_iterator = create_async(parsed, context, cancellation_signal)
            first_handler_event = await handler_iterator.__anext__()
        except StopAsyncIteration:
            events = _build_events(
                response_id,
                include_progress=True,
                agent_reference=agent_reference,
                model=model,
            )

            async def _fallback_stream() -> AsyncIterator[str]:
                try:
                    for event in events:
                        yield encode_sse_payload(event["type"], event["payload"])
                finally:
                    await _finalize_stream()

            return StreamingResponse(_fallback_stream(), media_type="text/event-stream", headers=response_headers)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            captured_error = exc
            span.end(captured_error)
            return _error_response(exc, response_headers)

        first_normalized = _apply_stream_event_defaults(
            _coerce_handler_event(first_handler_event),
            response_id=response_id,
            agent_reference=agent_reference,
            model=model,
            sequence_number=0,
        )
        handler_events.append(first_normalized)

        if background and store:
            initial_payload = _extract_response_snapshot_from_events(
                handler_events,
                response_id=response_id,
                agent_reference=agent_reference,
                model=model,
            )
            initial_status = initial_payload.get("status")
            if not isinstance(initial_status, str):
                initial_status = "in_progress"
            bg_record = _ExecutionRecord(
                response_id=response_id,
                agent_reference=deepcopy(agent_reference),
                stream=True,
                store=True,
                background=True,
                replay_enabled=True,
                visible_via_get=True,
                status=initial_status,
                model=model,
                response_payload=initial_payload,
                events=[deepcopy(first_normalized)],
                input_items=deepcopy(input_items),
                previous_response_id=previous_response_id,
                cancel_signal=cancellation_signal,
            )
            await runtime_state.add(bg_record)

        async def _live_stream() -> AsyncIterator[str]:  # pylint: disable=too-many-statements
            nonlocal captured_error

            if not runtime_options.sse_keep_alive_enabled:
                # Fast path: no keep-alive, iterate handler directly.
                try:
                    yield encode_sse_payload(first_normalized["type"], first_normalized["payload"])
                    async for handler_event in handler_iterator:
                        normalized = _normalize_and_append(handler_event)
                        yield encode_sse_payload(normalized["type"], normalized["payload"])
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    captured_error = exc
                    return
                finally:
                    await _finalize_stream()
                return

            # Keep-alive path: merge handler events with periodic keep-alive comments
            # via a shared queue so comments are sent even while the handler is idle.
            _SENTINEL = object()
            merge_queue: asyncio.Queue[str | object] = asyncio.Queue()
            handler_error: list[Exception] = []

            async def _handler_producer() -> None:
                try:
                    async for handler_event in handler_iterator:
                        normalized = _normalize_and_append(handler_event)
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
                _keep_alive_producer(runtime_options.sse_keep_alive_interval_seconds)  # type: ignore[arg-type]
            )

            try:
                yield encode_sse_payload(first_normalized["type"], first_normalized["payload"])
                while True:
                    item = await merge_queue.get()
                    if item is _SENTINEL:
                        break
                    yield item  # type: ignore[misc]
                if handler_error:
                    captured_error = handler_error[0]
            except Exception as exc:  # pylint: disable=broad-exception-caught
                captured_error = exc
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

                await _finalize_stream()

        return StreamingResponse(_live_stream(), media_type="text/event-stream", headers=response_headers)

    async def _create_sync(
        *,
        parsed: Any,
        context: RuntimeResponseContext,
        cancellation_signal: asyncio.Event,
        response_id: str,
        agent_reference: Any,
        model: str | None,
        store: bool,
        input_items: list[Any],
        previous_response_id: str | None,
        span: Any,
        captured_error: Exception | None,
    ) -> Response:
        """Handle a synchronous (non-stream, non-background) create-response request.

        Collects all handler events, builds the response snapshot, and returns
        a ``JSONResponse``.

        :keyword parsed: Parsed ``CreateResponse`` model instance.
        :keyword type parsed: Any
        :keyword context: Runtime response context for this request.
        :keyword type context: RuntimeResponseContext
        :keyword cancellation_signal: Event signalling cancellation.
        :keyword type cancellation_signal: asyncio.Event
        :keyword response_id: The assigned response ID.
        :keyword type response_id: str
        :keyword agent_reference: Normalized agent reference dictionary.
        :keyword type agent_reference: Any
        :keyword model: Model name, or ``None``.
        :keyword type model: str | None
        :keyword store: Whether to persist the execution record.
        :keyword type store: bool
        :keyword input_items: Extracted input items from the request.
        :keyword type input_items: list[Any]
        :keyword previous_response_id: Previous response ID for chaining, or ``None``.
        :keyword type previous_response_id: str | None
        :keyword span: Active observability span.
        :keyword type span: Any
        :keyword captured_error: Pre-captured error, or ``None``.
        :keyword type captured_error: Exception | None
        :return: A ``JSONResponse`` containing the response snapshot.
        :rtype: Response
        """
        handler_events: list[dict[str, Any]] = []
        try:
            async for handler_event in create_async(parsed, context, cancellation_signal):
                coerced = _coerce_handler_event(handler_event)
                normalized = _apply_stream_event_defaults(
                    coerced,
                    response_id=response_id,
                    agent_reference=agent_reference,
                    model=model,
                    sequence_number=None,
                )
                handler_events.append(normalized)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            captured_error = exc
            span.end(captured_error)
            return _error_response(exc, response_headers)

        events = handler_events if handler_events else _build_events(
            response_id,
            include_progress=True,
            agent_reference=agent_reference,
            model=model,
        )
        response_payload = _extract_response_snapshot_from_events(
            events,
            response_id=response_id,
            agent_reference=agent_reference,
            model=model,
            remove_sequence_number=True,
        )
        resolved_status = response_payload.get("status")
        status = resolved_status if isinstance(resolved_status, str) else "completed"

        record = _ExecutionRecord(
            response_id=response_id,
            agent_reference=deepcopy(agent_reference),
            stream=False,
            store=store,
            background=False,
            replay_enabled=False,
            visible_via_get=store,
            status=status,
            model=model,
            response_payload=response_payload,
            input_items=deepcopy(input_items),
            previous_response_id=previous_response_id,
            response_context=context,
        )

        if store:
            await runtime_state.add(record)

        span.end(captured_error)
        return JSONResponse(record.to_snapshot(), status_code=200, headers=response_headers)

    async def _create_background(
        *,
        parsed: Any,
        context: RuntimeResponseContext,
        cancellation_signal: asyncio.Event,
        response_id: str,
        agent_reference: Any,
        model: str | None,
        store: bool,
        input_items: list[Any],
        previous_response_id: str | None,
        span: Any,
        captured_error: Exception | None,
    ) -> Response:
        """Handle a background (non-stream) create-response request.

        Creates a queued execution record with an attached background runner,
        and returns the initial snapshot immediately.

        :keyword parsed: Parsed ``CreateResponse`` model instance.
        :keyword type parsed: Any
        :keyword context: Runtime response context for this request.
        :keyword type context: RuntimeResponseContext
        :keyword cancellation_signal: Event signalling cancellation.
        :keyword type cancellation_signal: asyncio.Event
        :keyword response_id: The assigned response ID.
        :keyword type response_id: str
        :keyword agent_reference: Normalized agent reference dictionary.
        :keyword type agent_reference: Any
        :keyword model: Model name, or ``None``.
        :keyword type model: str | None
        :keyword store: Whether to persist the execution record.
        :keyword type store: bool
        :keyword input_items: Extracted input items from the request.
        :keyword type input_items: list[Any]
        :keyword previous_response_id: Previous response ID for chaining, or ``None``.
        :keyword type previous_response_id: str | None
        :keyword span: Active observability span.
        :keyword type span: Any
        :keyword captured_error: Pre-captured error, or ``None``.
        :keyword type captured_error: Exception | None
        :return: A ``JSONResponse`` containing the queued response snapshot.
        :rtype: Response
        """
        record = _ExecutionRecord(
            response_id=response_id,
            agent_reference=deepcopy(agent_reference),
            stream=False,
            store=store,
            background=True,
            replay_enabled=False,
            visible_via_get=store,
            status="queued",
            model=model,
            input_items=deepcopy(input_items),
            previous_response_id=previous_response_id,
            response_context=context,
        )

        async def _background_runner() -> None:
            await _run_background_non_stream(
                create_async=create_async,
                parsed=parsed,
                context=context,
                cancellation_signal=cancellation_signal,
                record=record,
                response_id=response_id,
                agent_reference=agent_reference,
                model=model,
            )

        record.background_runner = _background_runner

        if store:
            await runtime_state.add(record)

        span.end(captured_error)
        return JSONResponse(record.to_snapshot(), status_code=200, headers=response_headers)

    async def _create(request: Request) -> Response:
        """Route handler for ``POST /responses``.

        Parses and validates the create request, then dispatches to the
        appropriate stream, sync, or background handler.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: The HTTP response for the create operation.
        :rtype: Response
        """
        nonlocal runtime_is_draining

        if runtime_is_draining:
            return _service_unavailable("Server is shutting down.", response_headers)

        span = start_create_span(
            "create_response",
            build_create_span_tags(
                response_id=None,
                model=None,
                agent_reference=None,
                service_name=_SDK_NAME,
            ),
            hook=runtime_options.create_span_hook,
        )
        captured_error: Exception | None = None

        try:
            payload = await request.json()
            _prevalidate_identity_payload(payload)
            parsed = parse_and_validate_create_response(payload, options=runtime_options)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            captured_error = exc
            span.end(captured_error)
            return _error_response(exc, response_headers)

        try:
            response_id, agent_reference = _resolve_identity_fields(parsed)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            captured_error = exc
            span.end(captured_error)
            return _error_response(exc, response_headers)

        stream = bool(getattr(parsed, "stream", False))
        store = True if getattr(parsed, "store", None) is None else bool(parsed.store)
        background = bool(getattr(parsed, "background", False))
        model = getattr(parsed, "model", None)
        input_items = _extract_input_items(payload)
        previous_response_id = _extract_previous_response_id(payload)
        mode_flags = ResponseModeFlags(stream=stream, store=store, background=background)
        context = RuntimeResponseContext(
            response_id=response_id,
            mode_flags=mode_flags,
            raw_body=payload,
        )
        context.is_shutdown_requested = shutdown_requested.is_set()
        cancellation_signal = asyncio.Event()
        if context.is_shutdown_requested:
            cancellation_signal.set()

        span.set_tags(
            build_create_span_tags(
                response_id=response_id,
                model=model,
                agent_reference=agent_reference,
                service_name=_SDK_NAME,
            )
        )

        if stream:
            return await _create_stream(
                parsed=parsed,
                context=context,
                cancellation_signal=cancellation_signal,
                response_id=response_id,
                agent_reference=agent_reference,
                model=model,
                store=store,
                background=background,
                input_items=input_items,
                previous_response_id=previous_response_id,
                span=span,
                captured_error=captured_error,
            )

        if not background:
            return await _create_sync(
                parsed=parsed,
                context=context,
                cancellation_signal=cancellation_signal,
                response_id=response_id,
                agent_reference=agent_reference,
                model=model,
                store=store,
                input_items=input_items,
                previous_response_id=previous_response_id,
                span=span,
                captured_error=captured_error,
            )

        return await _create_background(
            parsed=parsed,
            context=context,
            cancellation_signal=cancellation_signal,
            response_id=response_id,
            agent_reference=agent_reference,
            model=model,
            store=store,
            input_items=input_items,
            previous_response_id=previous_response_id,
            span=span,
            captured_error=captured_error,
        )

    async def _get(request: Request) -> Response:  # pylint: disable=too-many-return-statements
        """Route handler for ``GET /responses/{response_id}``.

        Returns the response snapshot or replays SSE events if ``stream=true``
        is specified in the query parameters.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: A ``JSONResponse`` with the snapshot or an SSE ``StreamingResponse``.
        :rtype: Response
        """
        response_id = request.path_params["response_id"]
        record = await runtime_state.get(response_id)
        if record is None:
            if await runtime_state.is_deleted(response_id):
                return _deleted_response(response_id, response_headers)
            return _not_found(response_id, response_headers)

        await _try_execute_background_runner(record)
        _refresh_background_status(record)

        stream_replay = request.query_params.get("stream", "false").lower() == "true"
        if stream_replay:
            if not record.replay_enabled:
                return _invalid_mode(
                    "stream replay is not available for this response",
                    response_headers,
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
                        response_headers,
                        param="starting_after",
                    )

            replay_events = [
                event for event in record.events
                if event["payload"]["sequence_number"] > starting_after
            ]
            return StreamingResponse(
                _encode_sse(replay_events), media_type="text/event-stream", headers=response_headers
            )

        if not record.visible_via_get:
            return _not_found(response_id, response_headers)

        return JSONResponse(record.to_snapshot(), status_code=200, headers=response_headers)

    async def _delete(request: Request) -> Response:
        """Route handler for ``DELETE /responses/{response_id}``.

        Deletes the response record if it exists and is not in-flight.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: A ``JSONResponse`` confirming deletion or an error response.
        :rtype: Response
        """
        response_id = request.path_params["response_id"]
        record = await runtime_state.get(response_id)
        if record is None:
            return _not_found(response_id, response_headers)

        _refresh_background_status(record)

        if record.background and record.status in {"queued", "in_progress"}:
            return _invalid_request(
                "Cannot delete an in-flight response.",
                response_headers,
                param="response_id",
            )

        deleted = await runtime_state.delete(response_id)
        if not deleted:
            return _not_found(response_id, response_headers)

        payload = {
            "id": response_id,
            "object": "response.deleted",
            "deleted": True,
        }
        return JSONResponse(payload, status_code=200, headers=response_headers)

    async def _cancel(request: Request) -> Response:  # pylint: disable=too-many-return-statements
        """Route handler for ``POST /responses/{response_id}/cancel``.

        Cancels a background response by setting the cancellation signal and
        updating the record status.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: A ``JSONResponse`` with the cancelled snapshot or an error response.
        :rtype: Response
        """
        response_id = request.path_params["response_id"]
        record = await runtime_state.get(response_id)
        if record is None:
            return _not_found(response_id, response_headers)

        _refresh_background_status(record)

        if not record.background:
            return _invalid_request(
                "Cannot cancel a synchronous response.",
                response_headers,
                param="response_id",
            )

        if record.status == "cancelled":
            if not isinstance(record.response_payload, dict):
                record.response_payload = {
                    "id": record.response_id,
                    "response_id": record.response_id,
                    "agent_reference": deepcopy(record.agent_reference),
                    "object": "response",
                    "status": "cancelled",
                    "model": record.model,
                    "output": [],
                }
            else:
                record.response_payload["status"] = "cancelled"
                record.response_payload["output"] = []
            return JSONResponse(record.to_snapshot(), status_code=200, headers=response_headers)

        if record.status == "completed":
            return _invalid_request(
                "Cannot cancel a completed response.",
                response_headers,
                param="response_id",
            )

        if record.status == "failed":
            return _invalid_request(
                "Cannot cancel a failed response.",
                response_headers,
                param="response_id",
            )

        if record.status == "incomplete":
            return _invalid_request(
                "Cannot cancel an incomplete response.",
                response_headers,
                param="response_id",
            )

        record.status = "cancelled"
        record.cancel_signal.set()
        record.response_payload = {
            "id": record.response_id,
            "response_id": record.response_id,
            "agent_reference": deepcopy(record.agent_reference),
            "object": "response",
            "status": "cancelled",
            "model": record.model,
            "output": [],
        }
        return JSONResponse(record.to_snapshot(), status_code=200, headers=response_headers)

    async def _get_input_items(request: Request) -> Response:
        """Route handler for ``GET /responses/{response_id}/input_items``.

        Returns a paginated list of input items for the given response,
        including items from the ancestor chain.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: A ``JSONResponse`` with the paginated input items list.
        :rtype: Response
        """
        response_id = request.path_params["response_id"]

        limit_raw = request.query_params.get("limit", "20")
        try:
            limit = int(limit_raw)
        except ValueError:
            return _invalid_request("limit must be an integer between 1 and 100", response_headers, param="limit")

        if limit < 1 or limit > 100:
            return _invalid_request("limit must be between 1 and 100", response_headers, param="limit")

        order = request.query_params.get("order", "desc").lower()
        if order not in {"asc", "desc"}:
            return _invalid_request("order must be 'asc' or 'desc'", response_headers, param="order")

        after = request.query_params.get("after")
        before = request.query_params.get("before")

        try:
            items = await runtime_state.get_input_items(response_id)
        except ValueError:
            return _deleted_response(response_id, response_headers)
        except KeyError:
            return _not_found(response_id, response_headers)

        ordered_items = items if order == "asc" else list(reversed(items))
        scoped_items = _apply_item_cursors(ordered_items, after=after, before=before)

        page = scoped_items[:limit]
        has_more = len(scoped_items) > limit

        first_id = _extract_item_id(page[0]) if page else None
        last_id = _extract_item_id(page[-1]) if page else None

        payload = {
            "object": "list",
            "data": page,
            "first_id": first_id,
            "last_id": last_id,
            "has_more": has_more,
        }
        return JSONResponse(payload, status_code=200, headers=response_headers)

    async def _on_shutdown() -> None:
        """Graceful shutdown handler.

        Signals all active responses to cancel, waits for in-flight background
        executions to complete within the configured grace period.

        :return: None
        :rtype: None
        """
        nonlocal runtime_is_draining

        runtime_is_draining = True
        shutdown_requested.set()

        records = await runtime_state.list_records()
        for record in records:
            if record.response_context is not None:
                record.response_context.is_shutdown_requested = True

            record.cancel_signal.set()

            if record.background and record.status in {"queued", "in_progress"}:
                record.status = "cancelled"
                record.response_payload = {
                    "id": record.response_id,
                    "response_id": record.response_id,
                    "agent_reference": deepcopy(record.agent_reference),
                    "object": "response",
                    "status": "cancelled",
                    "model": record.model,
                    "output": [],
                }

        deadline = asyncio.get_running_loop().time() + float(runtime_options.shutdown_grace_period_seconds)
        while True:
            pending = [
                record
                for record in records
                if record.background
                and record.background_execution_started
                and record.status in {"queued", "in_progress"}
            ]
            if not pending:
                break

            if asyncio.get_running_loop().time() >= deadline:
                break

            await asyncio.sleep(0.05)

    app.add_route(f"{normalized_prefix}/responses", _create, methods=["POST"])
    app.add_route(f"{normalized_prefix}/responses/{{response_id}}", _get, methods=["GET"])
    app.add_route(f"{normalized_prefix}/responses/{{response_id}}", _delete, methods=["DELETE"])
    app.add_route(f"{normalized_prefix}/responses/{{response_id}}/cancel", _cancel, methods=["POST"])
    app.add_route(f"{normalized_prefix}/responses/{{response_id}}/input_items", _get_input_items, methods=["GET"])

    _original_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def _lifespan_with_shutdown(app_instance: Any) -> AsyncIterator[None]:
        async with _original_lifespan(app_instance):
            try:
                yield
            finally:
                await _on_shutdown()

    app.router.lifespan_context = _lifespan_with_shutdown
