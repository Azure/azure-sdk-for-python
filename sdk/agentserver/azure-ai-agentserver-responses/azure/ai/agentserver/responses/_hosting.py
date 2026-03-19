"""Starlette hosting integration for the Responses server package."""

from __future__ import annotations

import asyncio
import sys
from copy import deepcopy
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, AsyncIterator

from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from ._handlers import RuntimeResponseContext
from ._event_stream import ResponseEventStream
from ._id_generator import IdGenerator
from ._observability import build_create_span_tags, build_platform_server_header, start_create_span
from ._options import ResponsesServerOptions
from ._sse import encode_sse_payload
from ._state_machine import LifecycleStateMachineError, normalize_lifecycle_events
from ._validation import (
    build_api_error_response,
    build_invalid_mode_error_response,
    build_not_found_error_response,
    parse_and_validate_create_response,
    to_api_error_response,
)
from .models import ResponseModeFlags
from .models import _generated as generated_models
from .models.errors import RequestValidationError

if TYPE_CHECKING:
    from starlette.applications import Starlette

    from ._handlers import ResponseHandler


_SDK_NAME = "azure-ai-agentserver-responses"
_SDK_VERSION = "0.0.0"
_DEFAULT_AGENT_REFERENCE_NAME = "server-default-agent"
EVENT_TYPE = generated_models.ResponseStreamEventType
_RESPONSE_SNAPSHOT_EVENT_TYPES = {
    EVENT_TYPE.RESPONSE_CREATED.value,
    EVENT_TYPE.RESPONSE_QUEUED.value,
    EVENT_TYPE.RESPONSE_IN_PROGRESS.value,
    EVENT_TYPE.RESPONSE_COMPLETED.value,
    EVENT_TYPE.RESPONSE_FAILED.value,
    EVENT_TYPE.RESPONSE_INCOMPLETE.value,
}


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
    response_payload: dict[str, Any] | None = None
    events: list[dict[str, Any]] = field(default_factory=list)
    cancel_signal: asyncio.Event = field(default_factory=asyncio.Event)
    background_runner: Any | None = None
    background_execution_started: bool = False
    input_items: list[dict[str, Any]] = field(default_factory=list)
    previous_response_id: str | None = None

    def to_snapshot(self) -> dict[str, Any]:
        def _normalize_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
            normalized = generated_models.Response(payload).as_dict()
            if isinstance(normalized, dict):
                return normalized
            return payload

        if isinstance(self.response_payload, dict):
            payload = deepcopy(self.response_payload)
            payload.setdefault("id", self.response_id)
            payload.setdefault("response_id", self.response_id)
            payload.setdefault("agent_reference", deepcopy(self.agent_reference))
            payload.setdefault("object", "response")
            payload["status"] = self.status
            if self.model is not None:
                payload.setdefault("model", self.model)
            return _normalize_snapshot(payload)

        payload = {
            "id": self.response_id,
            "response_id": self.response_id,
            "agent_reference": deepcopy(self.agent_reference),
            "object": "response",
            "status": self.status,
            "model": self.model,
        }
        return _normalize_snapshot(payload)


class _RuntimeState:
    def __init__(self) -> None:
        self._records: dict[str, _ExecutionRecord] = {}
        self._deleted_response_ids: set[str] = set()
        self._lock = asyncio.Lock()

    async def add(self, record: _ExecutionRecord) -> None:
        async with self._lock:
            self._records[record.response_id] = record
            self._deleted_response_ids.discard(record.response_id)

    async def get(self, response_id: str) -> _ExecutionRecord | None:
        async with self._lock:
            return self._records.get(response_id)

    async def is_deleted(self, response_id: str) -> bool:
        async with self._lock:
            return response_id in self._deleted_response_ids

    async def delete(self, response_id: str) -> bool:
        async with self._lock:
            record = self._records.pop(response_id, None)
            if record is None:
                return False
            self._deleted_response_ids.add(response_id)
            return True

    async def get_input_items(self, response_id: str) -> list[dict[str, Any]]:
        async with self._lock:
            record = self._records.get(response_id)
            if record is None:
                if response_id in self._deleted_response_ids:
                    raise ValueError(f"response '{response_id}' has been deleted")
                raise KeyError(f"response '{response_id}' not found")

            if not record.visible_via_get:
                raise KeyError(f"response '{response_id}' not found")

            history: list[dict[str, Any]] = []
            cursor = record.previous_response_id
            visited: set[str] = set()

            while isinstance(cursor, str) and cursor and cursor not in visited:
                visited.add(cursor)
                previous = self._records.get(cursor)
                if previous is None:
                    break
                history = [*deepcopy(previous.input_items), *history]
                cursor = previous.previous_response_id

            return [*history, *deepcopy(record.input_items)]


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


def _extract_input_items(raw_payload: Any) -> list[dict[str, Any]]:
    if not isinstance(raw_payload, dict):
        return []

    value = raw_payload.get("input")
    if not isinstance(value, list):
        return []

    extracted: list[dict[str, Any]] = []
    for item in value:
        if isinstance(item, dict):
            extracted.append(deepcopy(item))
    return extracted


def _extract_previous_response_id(raw_payload: Any) -> str | None:
    if not isinstance(raw_payload, dict):
        return None
    value = raw_payload.get("previous_response_id")
    return value if isinstance(value, str) and value else None


def _extract_item_id(item: dict[str, Any]) -> str | None:
    value = item.get("id")
    return str(value) if value is not None else None


def _apply_item_cursors(items: list[dict[str, Any]], *, after: str | None, before: str | None) -> list[dict[str, Any]]:
    scoped = items

    if after is not None:
        after_index = next((index for index, item in enumerate(scoped) if _extract_item_id(item) == after), None)
        if after_index is not None:
            scoped = scoped[after_index + 1 :]

    if before is not None:
        before_index = next((index for index, item in enumerate(scoped) if _extract_item_id(item) == before), None)
        if before_index is not None:
            scoped = scoped[:before_index]

    return scoped


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
    payload = _json_payload(
        build_api_error_response(
            message=f"Response with id '{response_id}' not found.",
            code="invalid_request",
            param="response_id",
            error_type="invalid_request_error",
        )
    )
    return JSONResponse(payload, status_code=404, headers=headers)


def _invalid_request(message: str, headers: dict[str, str], *, param: str | None = None) -> JSONResponse:
    payload = _json_payload(
        build_api_error_response(
            message=message,
            code="invalid_request",
            param=param,
            error_type="invalid_request_error",
        )
    )
    return JSONResponse(payload, status_code=400, headers=headers)


def _invalid_mode(message: str, headers: dict[str, str], *, param: str | None = None) -> JSONResponse:
    payload = _json_payload(build_invalid_mode_error_response(message, param=param))
    return JSONResponse(payload, status_code=400, headers=headers)


def _deleted_response(response_id: str, headers: dict[str, str]) -> JSONResponse:
    return _invalid_request(
        f"Response with id '{response_id}' has been deleted.",
        headers,
        param="response_id",
    )


def _validate_response_id(response_id: str) -> None:
    is_valid_id, _ = IdGenerator.is_valid(response_id)
    if not is_valid_id:
        raise RequestValidationError(
            "response_id must be in format caresp_<18-char partition key><32-char alphanumeric entropy>",
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
        response_id = IdGenerator.new_response_id()

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


def _coerce_handler_event(handler_event: Any) -> dict[str, Any]:
    if isinstance(handler_event, dict):
        event_data = deepcopy(handler_event)
    elif hasattr(handler_event, "as_dict"):
        event_data = handler_event.as_dict()
    else:
        raise TypeError("handler events must be dictionaries or generated event models")

    event_type = event_data.get("type")
    if not isinstance(event_type, str) or not event_type:
        raise ValueError("handler event must include a non-empty 'type'")

    payload = event_data.get("payload")
    if isinstance(payload, dict):
        normalized_payload = deepcopy(payload)
    else:
        normalized_payload = {key: deepcopy(value) for key, value in event_data.items() if key != "type"}

    return {"type": event_type, "payload": normalized_payload}


def _apply_stream_event_defaults(
    event: dict[str, Any],
    *,
    response_id: str,
    agent_reference: dict[str, Any],
    model: str | None,
    sequence_number: int | None,
) -> dict[str, Any]:
    normalized = deepcopy(event)
    payload = normalized.get("payload")
    if not isinstance(payload, dict):
        payload = {}
        normalized["payload"] = payload

    payload.setdefault("id", response_id)
    payload.setdefault("response_id", response_id)
    payload.setdefault("object", "response")
    payload.setdefault("agent_reference", deepcopy(agent_reference))
    if model is not None:
        payload.setdefault("model", model)

    if sequence_number is not None:
        payload["sequence_number"] = sequence_number
    else:
        payload.pop("sequence_number", None)
    return normalized


def _extract_response_snapshot_from_events(
    events: list[dict[str, Any]],
    *,
    response_id: str,
    agent_reference: dict[str, Any],
    model: str | None,
    remove_sequence_number: bool = False,
) -> dict[str, Any]:
    for event in reversed(events):
        event_type = event.get("type")
        payload = event.get("payload")
        if event_type in _RESPONSE_SNAPSHOT_EVENT_TYPES and isinstance(payload, dict):
            snapshot = deepcopy(payload)
            snapshot.setdefault("id", response_id)
            snapshot.setdefault("response_id", response_id)
            snapshot.setdefault("agent_reference", deepcopy(agent_reference))
            snapshot.setdefault("object", "response")
            snapshot.setdefault("output", [])
            if model is not None:
                snapshot.setdefault("model", model)
            if remove_sequence_number:
                snapshot.pop("sequence_number", None)
            return snapshot

    fallback_events = _build_events(
        response_id,
        include_progress=True,
        agent_reference=agent_reference,
        model=model,
    )
    fallback_payload = deepcopy(fallback_events[-1]["payload"])
    fallback_payload.setdefault("output", [])
    if remove_sequence_number:
        fallback_payload.pop("sequence_number", None)
    return fallback_payload


async def _run_background_non_stream(
    *,
    create_async: Any,
    parsed: Any,
    context: RuntimeResponseContext,
    cancellation_signal: asyncio.Event,
    record: _ExecutionRecord,
    response_id: str,
    agent_reference: dict[str, Any],
    model: str | None,
) -> None:
    record.status = "in_progress"
    handler_events: list[dict[str, Any]] = []

    try:
        async for handler_event in create_async(parsed, context, cancellation_signal):
            if cancellation_signal.is_set():
                record.status = "cancelled"
                return

            coerced = _coerce_handler_event(handler_event)
            normalized = _apply_stream_event_defaults(
                coerced,
                response_id=response_id,
                agent_reference=agent_reference,
                model=model,
                sequence_number=None,
            )
            handler_events.append(normalized)
    except Exception:
        if record.status != "cancelled":
            record.status = "failed"
            record.response_payload = {
                "id": response_id,
                "response_id": response_id,
                "agent_reference": deepcopy(agent_reference),
                "object": "response",
                "status": "failed",
                "model": model,
                "output": [],
            }
        return

    if cancellation_signal.is_set():
        record.status = "cancelled"
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
        remove_sequence_number=True,
    )

    resolved_status = response_payload.get("status")
    record.response_payload = response_payload
    if record.status != "cancelled":
        record.status = resolved_status if isinstance(resolved_status, str) else "completed"


async def _try_execute_background_runner(record: _ExecutionRecord) -> None:
    if not record.background or record.status in {"completed", "failed", "incomplete", "cancelled"}:
        return

    if record.background_runner is None or record.background_execution_started:
        return

    if record.cancel_signal.is_set():
        record.status = "cancelled"
        return

    runner = record.background_runner
    record.background_execution_started = True
    try:
        await runner()
    finally:
        record.background_runner = None


def _refresh_background_status(record: _ExecutionRecord) -> None:
    if not record.background or record.status in {"completed", "failed", "incomplete", "cancelled"}:
        return

    if record.background_runner is not None or record.background_execution_started:
        if record.cancel_signal.is_set():
            record.status = "cancelled"
            return

        if record.status == "queued":
            record.status = "in_progress"
        return

    if record.cancel_signal.is_set():
        record.status = "cancelled"
        return

    if record.status == "queued":
        record.status = "in_progress"


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
                {"type": EVENT_TYPE.RESPONSE_CREATED.value, "payload": {"status": "queued"}},
                {"type": EVENT_TYPE.RESPONSE_COMPLETED.value, "payload": {"status": "completed"}},
            ],
        )
    except LifecycleStateMachineError as exc:
        raise RuntimeError(f"Invalid lifecycle event state machine configuration: {exc}") from exc

    async def _create(request: Request) -> Response:
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
        except Exception as exc:
            captured_error = exc
            span.end(captured_error)
            return _error_response(exc, response_headers)

        try:
            response_id, agent_reference = _resolve_identity_fields(parsed)
        except Exception as exc:
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
        cancellation_signal = asyncio.Event()

        span.set_tags(
            build_create_span_tags(
                response_id=response_id,
                model=model,
                agent_reference=agent_reference,
                service_name=_SDK_NAME,
            )
        )

        if stream:
            handler_events: list[dict[str, Any]] = []
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

                return StreamingResponse(_fallback_stream(), media_type="text/event-stream", headers=response_headers)
            except Exception as exc:
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

            async def _live_stream() -> AsyncIterator[str]:
                nonlocal captured_error

                try:
                    yield encode_sse_payload(first_normalized["type"], first_normalized["payload"])
                    async for handler_event in handler_iterator:
                        coerced = _coerce_handler_event(handler_event)
                        normalized = _apply_stream_event_defaults(
                            coerced,
                            response_id=response_id,
                            agent_reference=agent_reference,
                            model=model,
                            sequence_number=len(handler_events),
                        )
                        handler_events.append(normalized)
                        yield encode_sse_payload(normalized["type"], normalized["payload"])
                except Exception as exc:
                    captured_error = exc
                    return
                finally:
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

            return StreamingResponse(_live_stream(), media_type="text/event-stream", headers=response_headers)

        if not stream and not background:
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
            except Exception as exc:
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
            )

            if store:
                await runtime_state.add(record)

            span.end(captured_error)
            return JSONResponse(record.to_snapshot(), status_code=200, headers=response_headers)

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

    async def _get(request: Request) -> Response:
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
                return _invalid_mode("stream replay is not available for this response", response_headers, param="stream")

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

    async def _delete(request: Request) -> Response:
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

    async def _cancel(request: Request) -> Response:
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

    app.add_route(f"{normalized_prefix}/responses", _create, methods=["POST"])
    app.add_route(f"{normalized_prefix}/responses/{{response_id}}", _get, methods=["GET"])
    app.add_route(f"{normalized_prefix}/responses/{{response_id}}", _delete, methods=["DELETE"])
    app.add_route(f"{normalized_prefix}/responses/{{response_id}}/cancel", _cancel, methods=["POST"])
    app.add_route(f"{normalized_prefix}/responses/{{response_id}}/input_items", _get_input_items, methods=["GET"])
