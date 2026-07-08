# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests for SSE keep-alive comment frames during streaming."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses._options import ResponsesServerOptions


def _make_slow_handler(delay_seconds: float = 0.5, event_count: int = 2):
    """Factory for a handler that yields events with a configurable delay between them."""

    def _handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            for i in range(event_count):
                if i > 0:
                    await asyncio.sleep(delay_seconds)
                yield {
                    "type": "response.created" if i == 0 else "response.completed",
                    "response": {
                        "status": "in_progress" if i == 0 else "completed",
                    },
                }

        return _events()

    return _handler


def _noop_handler(request: Any, context: Any, cancellation_signal: Any):
    """Minimal handler producing an empty stream."""

    async def _events():
        if False:  # pragma: no cover
            yield None

    return _events()


def _build_client(
    handler: Any | None = None,
    *,
    keep_alive_seconds: int | None = None,
) -> TestClient:
    options = ResponsesServerOptions(sse_keep_alive_interval_seconds=keep_alive_seconds)
    app = ResponsesAgentServerHost(options=options)
    app.response_handler(handler or _noop_handler)
    return TestClient(app)


def _parse_raw_lines(response: Any) -> list[str]:
    """Collect all raw lines (including SSE comments) from a streaming response."""
    return list(response.iter_lines())


def _collect_events_and_comments(response: Any) -> tuple[list[dict[str, Any]], list[str]]:
    """Parse SSE stream into (events, comments).

    Events are objects with ``type`` and ``data`` keys.
    Comments are raw lines starting with ``:``.
    """
    events: list[dict[str, Any]] = []
    comments: list[str] = []
    current_type: str | None = None
    current_data: str | None = None

    for line in response.iter_lines():
        if not line:
            if current_type is not None:
                parsed: dict[str, Any] = {}
                if current_data:
                    parsed = json.loads(current_data)
                events.append({"type": current_type, "data": parsed})
            current_type = None
            current_data = None
            continue

        if line.startswith(":"):
            comments.append(line)
        elif line.startswith("event:"):
            current_type = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            current_data = line.split(":", 1)[1].strip()

    if current_type is not None:
        parsed = json.loads(current_data) if current_data else {}
        events.append({"type": current_type, "data": parsed})

    return events, comments


def _stream_post(client: TestClient, **extra_json: Any) -> Any:
    """Issue a streaming POST /responses and return the streaming context manager."""
    payload = {
        "model": "gpt-4o-mini",
        "input": "hello",
        "stream": True,
        "store": True,
        "background": False,
        **extra_json,
    }
    return client.stream("POST", "/responses", json=payload)


# -- Tests: keep-alive disabled (default) -----------------------------------


def test_keep_alive__disabled_by_default_no_comment_frames() -> None:
    """When keep-alive is not configured, no SSE comment frames should appear."""
    handler = _make_slow_handler(delay_seconds=0.3, event_count=2)
    client = _build_client(handler)

    with _stream_post(client) as response:
        assert response.status_code == 200
        events, comments = _collect_events_and_comments(response)

    assert len(events) >= 1
    assert len(comments) == 0, f"Expected no keep-alive comments, got: {comments}"


# -- Tests: keep-alive enabled -----------------------------------------------


def test_keep_alive__enabled_interleaves_comment_frames_during_slow_handler() -> None:
    """When keep-alive is enabled with a short interval, SSE comment frames
    should appear between handler events when the handler is slow."""
    # Handler delays 1.5s between events; keep-alive fires every 0.2s
    handler = _make_slow_handler(delay_seconds=1.5, event_count=2)
    client = _build_client(handler, keep_alive_seconds=1)

    with _stream_post(client) as response:
        assert response.status_code == 200
        events, comments = _collect_events_and_comments(response)

    # At least one keep-alive comment should have been sent during the 1.5s gap
    assert len(comments) >= 1, (
        f"Expected at least one keep-alive comment, got {len(comments)}. Events: {[e['type'] for e in events]}"
    )
    # All comments should be the standard keep-alive format
    for comment in comments:
        assert comment == ": keep-alive"


def test_keep_alive__comment_format_is_sse_compliant() -> None:
    """Keep-alive frames must be valid SSE comments (colon-prefixed)."""
    handler = _make_slow_handler(delay_seconds=1.5, event_count=2)
    client = _build_client(handler, keep_alive_seconds=1)

    with _stream_post(client) as response:
        assert response.status_code == 200
        raw_lines = _parse_raw_lines(response)

    keep_alive_lines = [line for line in raw_lines if line.startswith(": keep-alive")]
    assert len(keep_alive_lines) >= 1
    for line in keep_alive_lines:
        # SSE comments start with colon; must not contain "event:" or "data:"
        assert line.startswith(":")
        assert "event:" not in line
        assert "data:" not in line


def test_keep_alive__does_not_disrupt_event_stream_integrity() -> None:
    """Even with keep-alive enabled, all handler events should be present
    with correct types, ordering, and monotonic sequence numbers."""
    handler = _make_slow_handler(delay_seconds=1.5, event_count=2)
    client = _build_client(handler, keep_alive_seconds=1)

    with _stream_post(client) as response:
        assert response.status_code == 200
        events, comments = _collect_events_and_comments(response)

    event_types = [e["type"] for e in events]
    assert "response.created" in event_types
    # Sequence numbers should still be monotonically increasing
    seq_nums = [e["data"].get("sequence_number") for e in events if "sequence_number" in e["data"]]
    assert seq_nums == sorted(seq_nums)


def test_keep_alive__no_comments_after_stream_ends() -> None:
    """After the handler finishes, no trailing keep-alive comments should appear."""
    handler = _make_slow_handler(delay_seconds=0.0, event_count=2)
    client = _build_client(handler, keep_alive_seconds=1)

    with _stream_post(client) as response:
        assert response.status_code == 200
        events, comments = _collect_events_and_comments(response)

    # Handler is fast (0s delay), so no keep-alive should be needed
    # (the stream finishes before the 1s interval fires)
    assert len(events) >= 1
    # No comments expected since the handler is faster than the keep-alive interval
    assert len(comments) == 0


def test_keep_alive__fallback_stream_does_not_include_keep_alive() -> None:
    """When the handler yields no events (empty generator → fallback stream),
    keep-alive should not appear since the fallback stream is immediate."""
    client = _build_client(_noop_handler, keep_alive_seconds=1)

    with _stream_post(client) as response:
        assert response.status_code == 200
        events, comments = _collect_events_and_comments(response)

    assert len(events) >= 1  # fallback auto-generates lifecycle events
    assert len(comments) == 0
