"""Starlette hosting integration for the Responses server package."""

from __future__ import annotations

import asyncio
import re
import sys
from copy import deepcopy
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, AsyncIterator
from uuid import uuid4

from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from ._event_stream import ResponseEventStream
from ._observability import build_platform_server_header
from ._options import ResponsesServerOptions
from ._sse import encode_sse_payload
from ._state_machine import LifecycleStateMachineError, normalize_lifecycle_events
from ._validation import parse_and_validate_create_response, to_api_error_response
from .models.errors import RequestValidationError

if TYPE_CHECKING:
    from starlette.applications import Starlette

    from ._handlers import ResponseHandler


_SDK_NAME = "azure-ai-agentserver-responses"
_SDK_VERSION = "0.0.0"
_RESPONSE_ID_PATTERN = re.compile(r"^resp_[A-Za-z0-9_-]{8,}$")
_DEFAULT_AGENT_REFERENCE_NAME = "server-default-agent"


@dataclass(slots=True)
class _ExecutionRecord:
    response_id: str
    agent_reference: dict[str, Any]
    stream: bool
    store: bool
    background: bool
    replay_enabled: bool
    visible_via_get: bool
    status: str
    model: str | None
    events: list[dict[str, Any]] = field(default_factory=list)
    cancel_signal: asyncio.Event = field(default_factory=asyncio.Event)
    background_started_at: float | None = None
    completion_delay_seconds: float = 0.25

    def to_snapshot(self) -> dict[str, Any]:
        return {
            "id": self.response_id,
            "response_id": self.response_id,
            "agent_reference": deepcopy(self.agent_reference),
            "object": "response",
            "status": self.status,
            "model": self.model,
        }


class _RuntimeState:
    def __init__(self) -> None:
        self._records: dict[str, _ExecutionRecord] = {}
        self._lock = asyncio.Lock()

    async def add(self, record: _ExecutionRecord) -> None:
        async with self._lock:
            self._records[record.response_id] = record

    async def get(self, response_id: str) -> _ExecutionRecord | None:
        async with self._lock:
            return self._records.get(response_id)


def _runtime_marker() -> str:
    return f"python/{sys.version_info.major}.{sys.version_info.minor}"


def _platform_header(options: ResponsesServerOptions) -> str:
    return build_platform_server_header(
        sdk_name=_SDK_NAME,
        version=_SDK_VERSION,
        runtime=_runtime_marker(),
        extra=options.additional_server_identity,
    )


def _json_payload(value: Any) -> Any:
    if hasattr(value, "as_dict"):
        return value.as_dict()  # type: ignore[no-any-return]
    return value


def _error_response(error: Exception, headers: dict[str, str]) -> JSONResponse:
    envelope = to_api_error_response(error)
    payload = _json_payload(envelope)
    error_type = payload.get("error", {}).get("type") if isinstance(payload, dict) else None

    status_code = 500
    if error_type == "invalid_request_error":
        status_code = 400
    elif error_type == "not_found_error":
        status_code = 404

    return JSONResponse(payload, status_code=status_code, headers=headers)


def _not_found(response_id: str, headers: dict[str, str]) -> JSONResponse:
    payload = {
        "error": {
            "type": "not_found_error",
            "code": "not_found",
            "message": f"response '{response_id}' was not found",
            "param": "response_id",
        }
    }
    return JSONResponse(payload, status_code=404, headers=headers)


def _invalid_request(message: str, headers: dict[str, str], *, param: str | None = None) -> JSONResponse:
    payload = {
        "error": {
            "type": "invalid_request_error",
            "code": "invalid_request",
            "message": message,
            "param": param,
        }
    }
    return JSONResponse(payload, status_code=400, headers=headers)


def _validate_response_id(response_id: str) -> None:
    if not _RESPONSE_ID_PATTERN.fullmatch(response_id):
        raise RequestValidationError(
            "response_id must start with 'resp_' and contain only alphanumeric, underscore, or dash characters",
            code="invalid_request",
            param="response_id",
        )


def _normalize_agent_reference(value: Any) -> dict[str, Any]:
    if value is None:
        return {
            "type": "agent_reference",
            "name": _DEFAULT_AGENT_REFERENCE_NAME,
        }

    if hasattr(value, "as_dict"):
        candidate = value.as_dict()
    elif isinstance(value, dict):
        candidate = dict(value)
    else:
        raise RequestValidationError(
            "agent_reference must be an object",
            code="invalid_request",
            param="agent_reference",
        )

    candidate.setdefault("type", "agent_reference")
    name = candidate.get("name")
    reference_type = candidate.get("type")

    if reference_type != "agent_reference":
        raise RequestValidationError(
            "agent_reference.type must be 'agent_reference'",
            code="invalid_request",
            param="agent_reference.type",
        )

    if not isinstance(name, str) or not name.strip():
        raise RequestValidationError(
            "agent_reference.name must be a non-empty string",
            code="invalid_request",
            param="agent_reference.name",
        )

    candidate["name"] = name.strip()
    return candidate


def _prevalidate_identity_payload(payload: Any) -> None:
    if not isinstance(payload, dict):
        return

    raw_response_id = payload.get("response_id")
    if raw_response_id is not None:
        if not isinstance(raw_response_id, str) or not raw_response_id.strip():
            raise RequestValidationError(
                "response_id must be a non-empty string",
                code="invalid_request",
                param="response_id",
            )
        _validate_response_id(raw_response_id.strip())

    raw_agent_reference = payload.get("agent_reference")
    if raw_agent_reference is None:
        return

    if not isinstance(raw_agent_reference, dict):
        raise RequestValidationError(
            "agent_reference must be an object",
            code="invalid_request",
            param="agent_reference",
        )

    if raw_agent_reference.get("type") != "agent_reference":
        raise RequestValidationError(
            "agent_reference.type must be 'agent_reference'",
            code="invalid_request",
            param="agent_reference.type",
        )

    raw_name = raw_agent_reference.get("name")
    if not isinstance(raw_name, str) or not raw_name.strip():
        raise RequestValidationError(
            "agent_reference.name must be a non-empty string",
            code="invalid_request",
            param="agent_reference.name",
        )


def _resolve_identity_fields(parsed: Any) -> tuple[str, dict[str, Any]]:
    parsed_mapping = parsed.as_dict() if hasattr(parsed, "as_dict") else {}
    explicit_response_id = parsed_mapping.get("response_id") or getattr(parsed, "response_id", None)
    if isinstance(explicit_response_id, str) and explicit_response_id.strip():
        response_id = explicit_response_id.strip()
    else:
        response_id = f"resp_{uuid4().hex[:24]}"

    _validate_response_id(response_id)
    agent_reference = _normalize_agent_reference(
        parsed_mapping.get("agent_reference") if isinstance(parsed_mapping, dict) else getattr(parsed, "agent_reference", None)
    )
    return response_id, agent_reference


def _build_events(
    response_id: str,
    *,
    include_progress: bool,
    agent_reference: dict[str, Any],
    model: str | None,
) -> list[dict[str, Any]]:
    stream = ResponseEventStream(
        response_id=response_id,
        agent_reference=agent_reference,
        model=model,
    )
    events = [stream.emit_created(status="queued")]
    if include_progress:
        events.append(stream.emit_in_progress())
    events.append(stream.emit_completed())
    return events


async def _encode_sse(events: list[dict[str, Any]]) -> AsyncIterator[str]:
    for event in events:
        yield encode_sse_payload(event["type"], event["payload"])


async def _complete_background(record: _ExecutionRecord) -> None:
    record.status = "in_progress"
    try:
        await asyncio.wait_for(record.cancel_signal.wait(), timeout=record.completion_delay_seconds)
    except TimeoutError:
        if record.status not in {"cancelled", "failed", "incomplete"}:
            record.status = "completed"


def _refresh_background_status(record: _ExecutionRecord) -> None:
    if not record.background or record.status in {"completed", "failed", "incomplete", "cancelled"}:
        return

    if record.cancel_signal.is_set():
        record.status = "cancelled"
        return

    if record.status == "queued":
        record.status = "in_progress"

    if record.background_started_at is None:
        return

    now = asyncio.get_running_loop().time()
    if now - record.background_started_at >= record.completion_delay_seconds:
        record.status = "completed"


def map_responses_server(
    app: "Starlette",
    handler: "ResponseHandler",
    *,
    prefix: str = "",
    options: ResponsesServerOptions | None = None,
) -> None:
    """Register Responses API routes on a Starlette application.

    :param app: Starlette application instance to configure.
    :param handler: User-provided response handler implementation.
    :param prefix: Optional route prefix.
    :param options: Optional server runtime options.
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

    try:
        normalize_lifecycle_events(
            response_id="resp_validation",
            events=[
                {"type": "response.created", "payload": {"status": "queued"}},
                {"type": "response.completed", "payload": {"status": "completed"}},
            ],
        )
    except LifecycleStateMachineError as exc:
        raise RuntimeError(f"Invalid lifecycle event state machine configuration: {exc}") from exc

    async def _create(request: Request) -> Response:
        try:
            payload = await request.json()
            _prevalidate_identity_payload(payload)
            parsed = parse_and_validate_create_response(payload, options=runtime_options)
        except Exception as exc:
            return _error_response(exc, response_headers)

        try:
            response_id, agent_reference = _resolve_identity_fields(parsed)
        except Exception as exc:
            return _error_response(exc, response_headers)

        stream = bool(getattr(parsed, "stream", False))
        store = True if getattr(parsed, "store", None) is None else bool(parsed.store)
        background = bool(getattr(parsed, "background", False))
        model = getattr(parsed, "model", None)

        if stream and not background:
            if store:
                streaming_record = _ExecutionRecord(
                    response_id=response_id,
                    agent_reference=deepcopy(agent_reference),
                    stream=True,
                    store=True,
                    background=False,
                    replay_enabled=False,
                    visible_via_get=False,
                    status="completed",
                    model=model,
                )
                await runtime_state.add(streaming_record)

            events = _build_events(
                response_id,
                include_progress=True,
                agent_reference=agent_reference,
                model=model,
            )
            return StreamingResponse(_encode_sse(events), media_type="text/event-stream", headers=response_headers)

        status = "queued" if background else "completed"
        record = _ExecutionRecord(
            response_id=response_id,
            agent_reference=deepcopy(agent_reference),
            stream=stream,
            store=store,
            background=background,
            replay_enabled=stream and background,
            visible_via_get=store and not (stream and not background),
            status=status,
            model=model,
            events=_build_events(
                response_id,
                include_progress=True,
                agent_reference=agent_reference,
                model=model,
            )
            if stream and background
            else [],
            background_started_at=asyncio.get_running_loop().time() if background and store else None,
        )

        if store:
            await runtime_state.add(record)

        return JSONResponse(record.to_snapshot(), status_code=200, headers=response_headers)

    async def _get(request: Request) -> Response:
        response_id = request.path_params["response_id"]
        record = await runtime_state.get(response_id)
        if record is None:
            return _not_found(response_id, response_headers)

        _refresh_background_status(record)

        stream_replay = request.query_params.get("stream", "false").lower() == "true"
        if stream_replay:
            if not record.replay_enabled:
                return _invalid_request("stream replay is not available for this response", response_headers, param="stream")

            cursor_raw = request.query_params.get("starting_after")
            starting_after = -1
            if cursor_raw is not None:
                try:
                    starting_after = int(cursor_raw)
                except ValueError:
                    return _invalid_request("starting_after must be an integer", response_headers, param="starting_after")

            replay_events = [event for event in record.events if event["payload"]["sequence_number"] > starting_after]
            return StreamingResponse(_encode_sse(replay_events), media_type="text/event-stream", headers=response_headers)

        if not record.visible_via_get:
            return _not_found(response_id, response_headers)

        return JSONResponse(record.to_snapshot(), status_code=200, headers=response_headers)

    async def _cancel(request: Request) -> Response:
        response_id = request.path_params["response_id"]
        record = await runtime_state.get(response_id)
        if record is None:
            return _not_found(response_id, response_headers)

        _refresh_background_status(record)

        if not record.background:
            return _invalid_request("only background responses can be cancelled", response_headers, param="response_id")

        if record.status == "cancelled":
            return JSONResponse(record.to_snapshot(), status_code=200, headers=response_headers)

        if record.status in {"completed", "failed", "incomplete"}:
            return _invalid_request("response is already in terminal state", response_headers, param="response_id")

        record.status = "cancelled"
        record.cancel_signal.set()
        return JSONResponse(record.to_snapshot(), status_code=200, headers=response_headers)

    app.add_route(f"{normalized_prefix}/responses", _create, methods=["POST"])
    app.add_route(f"{normalized_prefix}/responses/{{response_id}}", _get, methods=["GET"])
    app.add_route(f"{normalized_prefix}/responses/{{response_id}}/cancel", _cancel, methods=["POST"])
