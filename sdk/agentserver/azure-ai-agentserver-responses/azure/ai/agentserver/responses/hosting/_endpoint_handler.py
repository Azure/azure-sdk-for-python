# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""HTTP endpoint handler for the Responses server.

This module owns all Starlette I/O: ``Request`` parsing, route-level
validation, header propagation, and ``Response`` construction.  Business
logic lives in :class:`_ResponseOrchestrator`.
"""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
from contextlib import asynccontextmanager
from copy import deepcopy
from typing import Any, AsyncIterator

from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from .._handlers import RuntimeResponseContext
from .._options import ResponsesServerOptions
from ..models import ResponseModeFlags
from ..streaming._helpers import _encode_sse
from ..streaming._state_machine import LifecycleStateMachineError, normalize_lifecycle_events
from ._background import _refresh_background_status, _try_execute_background_runner
from ._execution_context import _ExecutionContext
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
    _extract_input_items,
    _extract_item_id,
    _extract_previous_response_id,
    _prevalidate_identity_payload,
    _resolve_identity_fields,
)
from ._runtime_state import _RuntimeState
from ._validation import parse_and_validate_create_response
from ..streaming._helpers import EVENT_TYPE


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
        sdk_name: str,
    ) -> None:
        """Initialise the endpoint handler.

        :param orchestrator: Event-pipeline orchestrator.
        :type orchestrator: _ResponseOrchestrator
        :param runtime_state: In-memory execution record store.
        :type runtime_state: _RuntimeState
        :param runtime_options: Server runtime options.
        :type runtime_options: ResponsesServerOptions
        :param response_headers: Base response headers for every response.
        :type response_headers: dict[str, str]
        :param sse_headers: Additional SSE-specific headers (merged with response_headers).
        :type sse_headers: dict[str, str]
        :param sdk_name: SDK package name string for observability tags.
        :type sdk_name: str
        """
        self._orchestrator = orchestrator
        self._runtime_state = runtime_state
        self._runtime_options = runtime_options
        self._response_headers = response_headers
        self._sse_headers = sse_headers
        self._sdk_name = sdk_name
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
            return _service_unavailable("Server is shutting down.", self._response_headers)

        span = start_create_span(
            "create_response",
            build_create_span_tags(
                response_id=None,
                model=None,
                agent_reference=None,
                service_name=self._sdk_name,
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
            return _error_response(exc, self._response_headers)

        try:
            response_id, agent_reference = _resolve_identity_fields(parsed)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            captured_error = exc
            span.end(captured_error)
            return _error_response(exc, self._response_headers)

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
        context.is_shutdown_requested = self._shutdown_requested.is_set()
        cancellation_signal = asyncio.Event()
        if context.is_shutdown_requested:
            cancellation_signal.set()

        span.set_tags(
            build_create_span_tags(
                response_id=response_id,
                model=model,
                agent_reference=agent_reference,
                service_name=self._sdk_name,
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
            captured_error=captured_error,
        )

        if stream:
            return StreamingResponse(
                self._orchestrator.run_stream(ctx),
                media_type="text/event-stream",
                headers=self._sse_headers,
            )

        if not background:
            try:
                snapshot = await self._orchestrator.run_sync(ctx)
                return JSONResponse(snapshot, status_code=200, headers=self._response_headers)
            except _HandlerError as exc:
                return _error_response(exc.original, self._response_headers)

        snapshot = await self._orchestrator.run_background(ctx)
        return JSONResponse(snapshot, status_code=200, headers=self._response_headers)

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
                return _deleted_response(response_id, self._response_headers)
            return _not_found(response_id, self._response_headers)

        await _try_execute_background_runner(record)
        _refresh_background_status(record)

        stream_replay = request.query_params.get("stream", "false").lower() == "true"
        if stream_replay:
            if not record.replay_enabled:
                return _invalid_mode(
                    "stream replay is not available for this response; to enable SSE replay, " \
                    + "create the response with background=true",
                    self._response_headers,
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
                        self._response_headers,
                        param="starting_after",
                    )

            replay_events = [
                event for event in record.events
                if event["payload"]["sequence_number"] > starting_after
            ]
            return StreamingResponse(
                _encode_sse(replay_events), media_type="text/event-stream", headers=self._sse_headers
            )

        if not record.visible_via_get:
            return _not_found(response_id, self._response_headers)

        return JSONResponse(record.to_snapshot(), status_code=200, headers=self._response_headers)

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
            return _not_found(response_id, self._response_headers)

        _refresh_background_status(record)

        if record.background and record.status in {"queued", "in_progress"}:
            return _invalid_request(
                "Cannot delete an in-flight response.",
                self._response_headers,
                param="response_id",
            )

        deleted = await self._runtime_state.delete(response_id)
        if not deleted:
            return _not_found(response_id, self._response_headers)

        return JSONResponse(
            {"id": response_id, "object": "response.deleted", "deleted": True},
            status_code=200,
            headers=self._response_headers,
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
            return _not_found(response_id, self._response_headers)

        _refresh_background_status(record)

        if not record.background:
            return _invalid_request(
                "Cannot cancel a synchronous response.",
                self._response_headers,
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
            return JSONResponse(record.to_snapshot(), status_code=200, headers=self._response_headers)

        if record.status == "completed":
            return _invalid_request(
                "Cannot cancel a completed response.",
                self._response_headers,
                param="response_id",
            )

        if record.status == "failed":
            return _invalid_request(
                "Cannot cancel a failed response.",
                self._response_headers,
                param="response_id",
            )

        if record.status == "incomplete":
            return _invalid_request(
                "Cannot cancel an incomplete response.",
                self._response_headers,
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
        return JSONResponse(record.to_snapshot(), status_code=200, headers=self._response_headers)

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
                "limit must be an integer between 1 and 100", self._response_headers, param="limit"
            )

        if limit < 1 or limit > 100:
            return _invalid_request(
                "limit must be between 1 and 100", self._response_headers, param="limit"
            )

        order = request.query_params.get("order", "desc").lower()
        if order not in {"asc", "desc"}:
            return _invalid_request("order must be 'asc' or 'desc'", self._response_headers, param="order")

        after = request.query_params.get("after")
        before = request.query_params.get("before")

        try:
            items = await self._runtime_state.get_input_items(response_id)
        except ValueError:
            return _deleted_response(response_id, self._response_headers)
        except KeyError:
            return _not_found(response_id, self._response_headers)

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
            headers=self._response_headers,
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

        deadline = asyncio.get_running_loop().time() + float(
            self._runtime_options.shutdown_grace_period_seconds
        )
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

    # ------------------------------------------------------------------
    # Lifespan integration
    # ------------------------------------------------------------------

    def lifespan_context(self, original_lifespan: Any) -> Any:
        """Wrap a Starlette lifespan context manager with shutdown handling.

        :param original_lifespan: The existing app lifespan context manager.
        :type original_lifespan: Any
        :return: A new async context manager that calls :meth:`handle_shutdown` on exit.
        :rtype: Any
        """
        handler = self

        @asynccontextmanager
        async def _lifespan_with_shutdown(app_instance: Any) -> AsyncIterator[None]:
            async with original_lifespan(app_instance):
                try:
                    yield
                finally:
                    await handler.handle_shutdown()

        return _lifespan_with_shutdown
