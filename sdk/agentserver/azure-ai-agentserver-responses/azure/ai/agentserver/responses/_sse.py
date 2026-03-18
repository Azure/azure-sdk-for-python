"""Server-sent events helpers for Responses streaming."""

from __future__ import annotations

from .models._generated import ResponseStreamEvent


def encode_sse_event(event: ResponseStreamEvent) -> str:
    """Encode a response stream event into SSE wire format.

    :param event: Generated response stream event model.
    :returns: Encoded SSE payload string.
    """
    raise NotImplementedError("SSE encoding will be implemented in Phase 2.")
