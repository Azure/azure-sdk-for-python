# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Server-sent events helpers for Responses streaming."""

from __future__ import annotations

import itertools
import json
from contextvars import ContextVar
from datetime import date, datetime, time, timedelta
from typing import Any, Mapping

from ..models._generated import ResponseStreamEvent

_stream_counter_var: ContextVar[itertools.count] = ContextVar("_stream_counter_var")


def _json_default(o: Any) -> Any:
    """JSON encoder default for datetime and bytes.

    Handles datetime objects that leak through model ``as_dict()`` calls
    by serializing to ISO-8601 strings (or Unix timestamps for datetime).

    :param o: The object to encode.
    :type o: Any
    :returns: A JSON-serializable representation.
    :rtype: Any
    :raises TypeError: If the object type is not supported.
    """
    if isinstance(o, datetime):
        return int(o.timestamp())
    if isinstance(o, (date, time)):
        return o.isoformat()
    if isinstance(o, timedelta):
        return o.total_seconds()
    if isinstance(o, (bytes, bytearray)):
        import base64  # pylint: disable=import-outside-toplevel

        return base64.b64encode(o).decode("ascii")
    raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")


def new_stream_counter() -> None:
    """Initialize a fresh per-stream SSE sequence number counter for the current context.

    Call this once at the start of each streaming response so that concurrent
    streams are numbered independently, each starting from 0.

    :rtype: None
    """
    _stream_counter_var.set(itertools.count())


def _next_sequence_number() -> int:
    """Return the next SSE sequence number for the current stream context.

    Initializes a new per-stream counter if none has been set for the current
    context (e.g. direct calls from tests or outside a streaming request).

    :returns: A monotonically increasing integer, starting from 0 for each stream.
    :rtype: int
    """
    counter = _stream_counter_var.get(None)
    if counter is None:
        counter = itertools.count()
        _stream_counter_var.set(counter)
    return next(counter)


def _coerce_payload(event: Any) -> tuple[str, dict[str, Any]]:
    """Extract and normalize event type and payload from an event object.

    Supports dict-like, model-with-``as_dict()``, and plain-object event sources.

    :param event: The SSE event object to coerce.
    :type event: Any
    :returns: A tuple of ``(event_type, payload_dict)``.
    :rtype: tuple[str, dict[str, Any]]
    :raises ValueError: If the event does not include a non-empty ``type``.
    """
    event_type = getattr(event, "type", None)

    if isinstance(event, Mapping):
        payload = dict(event)
        if event_type is None:
            event_type = payload.get("type")
    elif hasattr(event, "as_dict"):
        payload = event.as_dict()  # type: ignore[assignment]
        if event_type is None:
            event_type = payload.get("type")
    else:
        payload = {key: value for key, value in vars(event).items() if not key.startswith("_")}

    if not event_type:
        raise ValueError("SSE event must include a non-empty 'type'")

    payload.pop("type", None)
    return str(event_type), payload


def _ensure_sequence_number(event: Any, payload: dict[str, Any]) -> None:
    """Ensure the payload has a valid ``sequence_number``, assigning one if missing.

    :param event: The original event object (used for attribute fallback).
    :type event: Any
    :param payload: The payload dict to mutate.
    :type payload: dict[str, Any]
    :rtype: None
    """
    explicit = payload.get("sequence_number")
    event_value = getattr(event, "sequence_number", None)
    candidate = explicit if explicit is not None else event_value

    if not isinstance(candidate, int) or candidate < 0:
        candidate = _next_sequence_number()

    payload["sequence_number"] = candidate


def _build_sse_frame(event_type: str, payload: dict[str, Any]) -> str:
    """Build a single SSE frame string from event type and payload.

    :param event_type: The SSE event type name.
    :type event_type: str
    :param payload: The payload dict to serialize as JSON.
    :type payload: dict[str, Any]
    :returns: A complete SSE frame string with trailing newlines.
    :rtype: str
    """
    # Sanitize event_type to prevent SSE response splitting via newline injection
    event_type = event_type.replace("\n", "").replace("\r", "")
    lines = [f"event: {event_type}"]
    lines.append(f"data: {json.dumps(payload, default=_json_default)}")
    lines.append("")
    lines.append("")
    return "\n".join(lines)


def encode_sse_event(event: ResponseStreamEvent) -> str:
    """Encode a response stream event into SSE wire format.

    :param event: Generated response stream event model.
    :type event: ~azure.ai.agentserver.responses.models._generated.ResponseStreamEvent
    :returns: Encoded SSE payload string.
    :rtype: str
    """
    if hasattr(event, "as_dict"):
        wire = event.as_dict()
        event_type = str(wire.get("type", ""))
        _ensure_sequence_number(event, wire)
        return _build_sse_frame(event_type, wire)
    # Fallback for non-model event objects (e.g. plain dataclass-like)
    event_type, payload = _coerce_payload(event)
    _ensure_sequence_number(event, payload)
    return _build_sse_frame(event_type, {"type": event_type, **payload})


def encode_sse_any_event(event: ResponseStreamEvent) -> str:
    """Encode a ``ResponseStreamEvent`` model instance to SSE format.

    Delegates to :func:`encode_sse_event`.

    :param event: The event to encode.
    :type event: ResponseStreamEvent
    :returns: Encoded SSE frame string.
    :rtype: str
    """
    return encode_sse_event(event)


def encode_keep_alive_comment(comment: str = "keep-alive") -> str:
    """Encode an SSE comment frame used for keep-alive traffic.

    :param comment: The comment text to include. Defaults to ``"keep-alive"``.
    :type comment: str
    :returns: An SSE comment frame string.
    :rtype: str
    """
    return f": {comment}\n\n"
