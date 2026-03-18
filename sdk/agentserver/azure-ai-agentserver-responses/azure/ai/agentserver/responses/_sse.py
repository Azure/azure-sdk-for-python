"""Server-sent events helpers for Responses streaming."""

from __future__ import annotations

import itertools
import json
from typing import Any, Mapping

from .models._generated import ResponseStreamEvent


_sequence_counter = itertools.count()


def _next_sequence_number() -> int:
    return next(_sequence_counter)


def _coerce_payload(event: Any) -> tuple[str, dict[str, Any]]:
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
    explicit = payload.get("sequence_number")
    event_value = getattr(event, "sequence_number", None)
    candidate = explicit if explicit is not None else event_value

    if not isinstance(candidate, int) or candidate < 0:
        candidate = _next_sequence_number()

    payload["sequence_number"] = candidate


def _build_sse_frame(event_type: str, payload: dict[str, Any]) -> str:
    lines = [f"event: {event_type}"]

    # Emit multiline text as data lines for readability, then emit canonical
    # JSON payload for deterministic parsers.
    text_value = payload.get("text")
    if isinstance(text_value, str) and "\n" in text_value:
        lines.extend(f"data: {line}" for line in text_value.splitlines())

    lines.append(f"data: {json.dumps(payload)}")
    lines.append("")
    lines.append("")
    return "\n".join(lines)


def encode_sse_event(event: ResponseStreamEvent) -> str:
    """Encode a response stream event into SSE wire format.

    :param event: Generated response stream event model.
    :returns: Encoded SSE payload string.
    """
    event_type, payload = _coerce_payload(event)
    _ensure_sequence_number(event, payload)
    return _build_sse_frame(event_type, payload)


def encode_sse_payload(event_type: str, payload: Mapping[str, Any]) -> str:
    """Encode an event type + payload pair into SSE wire format."""
    event = {"type": event_type, **dict(payload)}
    normalized_type, normalized_payload = _coerce_payload(event)
    _ensure_sequence_number(event, normalized_payload)
    return _build_sse_frame(normalized_type, normalized_payload)


def encode_keep_alive_comment(comment: str = "keep-alive") -> str:
    """Encode an SSE comment frame used for keep-alive traffic."""
    return f": {comment}\n\n"
