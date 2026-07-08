# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests for SSE streaming behavior."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream


def _noop_response_handler(request: Any, context: Any, cancellation_signal: Any):
    """Minimal handler used to wire the hosting surface in contract tests."""

    async def _events():
        if False:  # pragma: no cover - required to keep async-generator shape.
            yield None

    return _events()


def _build_client() -> TestClient:
    app = ResponsesAgentServerHost()
    app.response_handler(_noop_response_handler)
    return TestClient(app)


def _throwing_before_yield_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that raises before yielding any event.

    Used to test pre-creation error handling in SSE streaming mode.
    """

    async def _events():
        raise RuntimeError("Simulated pre-creation failure")
        if False:  # pragma: no cover - keep async generator shape.
            yield None

    return _events()


def _throwing_after_created_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that emits response.created then raises.

    Used to test post-creation error handling in SSE streaming mode.
    """

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
        yield stream.emit_created()
        raise RuntimeError("Simulated post-creation failure")

    return _events()


def _collect_stream_events(response: Any) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    current_type: str | None = None
    current_data: str | None = None

    for line in response.iter_lines():
        if not line:
            if current_type is not None:
                parsed_data: dict[str, Any] = {}
                if current_data:
                    parsed_data = json.loads(current_data)
                events.append({"type": current_type, "data": parsed_data})
            current_type = None
            current_data = None
            continue

        if line.startswith("event:"):
            current_type = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            current_data = line.split(":", 1)[1].strip()

    if current_type is not None:
        parsed_data = json.loads(current_data) if current_data else {}
        events.append({"type": current_type, "data": parsed_data})

    return events


def test_streaming__first_event_is_response_created() -> None:
    client = _build_client()

    with client.stream(
        "POST",
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": True,
            "store": True,
            "background": False,
        },
    ) as response:
        assert response.status_code == 200
        assert response.headers.get("content-type", "").startswith("text/event-stream")
        events = _collect_stream_events(response)

    assert events, "Expected at least one SSE event"
    assert events[0]["type"] == "response.created"
    # Contract (B8): response.created event status must be queued or in_progress
    created_status = events[0]["data"]["response"].get("status")
    assert created_status in {"queued", "in_progress"}, (
        f"response.created status must be queued or in_progress per B8, got: {created_status}"
    )


def test_streaming__sequence_number_is_monotonic_and_contiguous() -> None:
    client = _build_client()

    with client.stream(
        "POST",
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": True,
            "store": True,
            "background": False,
        },
    ) as response:
        assert response.status_code == 200
        events = _collect_stream_events(response)

    assert events, "Expected at least one SSE event"
    sequence_numbers = [event["data"].get("sequence_number") for event in events]
    assert all(isinstance(sequence_number, int) for sequence_number in sequence_numbers)
    assert sequence_numbers == sorted(sequence_numbers)
    assert sequence_numbers == list(range(len(sequence_numbers)))


def test_streaming__has_exactly_one_terminal_event() -> None:
    client = _build_client()

    with client.stream(
        "POST",
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": True,
            "store": True,
            "background": False,
        },
    ) as response:
        assert response.status_code == 200
        events = _collect_stream_events(response)

    event_types = [event["type"] for event in events]
    terminal_types = {"response.completed", "response.failed", "response.incomplete"}
    terminal_count = sum(1 for event_type in event_types if event_type in terminal_types)
    assert terminal_count == 1


def test_streaming__identity_fields_are_consistent_across_events() -> None:
    client = _build_client()

    with client.stream(
        "POST",
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": True,
            "store": True,
            "background": False,
        },
    ) as response:
        assert response.status_code == 200
        events = _collect_stream_events(response)

    assert events, "Expected at least one SSE event"
    # The first event is response.created — a lifecycle event whose data wraps the
    # Response snapshot under the "response" key per the ResponseCreatedEvent contract.
    first_response = events[0]["data"]["response"]
    response_id = first_response.get("response_id")
    assert response_id == first_response.get("id")
    assert isinstance(first_response.get("agent_reference"), dict)

    _LIFECYCLE_TYPES = {
        "response.queued",
        "response.created",
        "response.in_progress",
        "response.completed",
        "response.failed",
        "response.incomplete",
    }
    lifecycle_events = [e for e in events if e["type"] in _LIFECYCLE_TYPES]
    for event in lifecycle_events:
        response_payload = event["data"]["response"]
        assert response_payload.get("response_id") == response_id
        assert response_payload.get("id") == response_id
        assert response_payload.get("agent_reference") == first_response.get("agent_reference")


def test_streaming__forwards_emitted_event_before_late_handler_failure() -> None:
    def _fail_after_first_event_handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            yield {
                "type": "response.created",
                "response": {
                    "status": "in_progress",
                },
            }
            await asyncio.sleep(0)
            raise RuntimeError("late stream failure")

        return _events()

    app = ResponsesAgentServerHost()
    app.response_handler(_fail_after_first_event_handler)
    client = TestClient(app)

    with client.stream(
        "POST",
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": True,
            "store": True,
            "background": False,
        },
    ) as response:
        assert response.status_code == 200
        assert response.headers.get("content-type", "").startswith("text/event-stream")
        first_event_line = ""
        for line in response.iter_lines():
            if line.startswith("event:"):
                first_event_line = line
                break

    assert first_event_line == "event: response.created"


def test_streaming__sse_response_headers_per_contract() -> None:
    """SSE Response Headers: Content-Type with charset, Connection, Cache-Control, X-Accel-Buffering."""
    client = _build_client()

    with client.stream(
        "POST",
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": True,
            "store": True,
            "background": False,
        },
    ) as response:
        assert response.status_code == 200
        content_type = response.headers.get("content-type", "")
        assert content_type == "text/event-stream; charset=utf-8", (
            f"Expected Content-Type with charset per SSE headers contract, got: {content_type}"
        )
        assert response.headers.get("connection") == "keep-alive", "Missing Connection: keep-alive"
        assert response.headers.get("cache-control") == "no-cache", "Missing Cache-Control: no-cache"
        assert response.headers.get("x-accel-buffering") == "no", "Missing X-Accel-Buffering: no"
        list(response.iter_lines())


def test_streaming__wire_format_has_no_sse_id_field() -> None:
    """B27 — SSE wire format must not contain id: lines. Sequence number is in JSON payload."""
    client = _build_client()

    with client.stream(
        "POST",
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": True,
            "store": True,
            "background": False,
        },
    ) as response:
        assert response.status_code == 200
        raw_lines = list(response.iter_lines())

    id_lines = [line for line in raw_lines if line.startswith("id:")]
    assert id_lines == [], f"SSE stream must not contain id: lines per B27, found: {id_lines}"


def test_streaming__background_stream_may_include_response_queued_event() -> None:
    """B8 — response.queued is optional in background mode SSE streams."""
    client = _build_client()

    with client.stream(
        "POST",
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": True,
            "store": True,
            "background": True,
        },
    ) as response:
        assert response.status_code == 200
        events = _collect_stream_events(response)

    assert events, "Expected at least one SSE event"
    event_types = [e["type"] for e in events]
    # response.created must be first
    assert event_types[0] == "response.created"
    # If response.queued is present, it must be right after response.created
    if "response.queued" in event_types:
        queued_idx = event_types.index("response.queued")
        assert queued_idx == 1, "response.queued should be the second event if present"


# ══════════════════════════════════════════════════════════
# B4, B10, B13: Handler failure and in_progress event
# ══════════════════════════════════════════════════════════


def test_streaming__pre_creation_handler_failure_produces_terminal_event() -> None:
    """B4 — Handler raising before any yield in streaming mode → SSE stream terminates with a proper terminal event."""
    handler = _throwing_before_yield_handler
    app = ResponsesAgentServerHost()
    app.response_handler(handler)
    client = TestClient(app, raise_server_exceptions=False)

    with client.stream(
        "POST",
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": True,
            "store": True,
            "background": False,
        },
    ) as response:
        assert response.status_code == 200
        events = _collect_stream_events(response)

    event_types = [e["type"] for e in events]
    # B8: pre-creation error → standalone `error` SSE event only.
    # No response.created must precede it.
    assert "error" in event_types, (
        f"SSE stream must emit standalone 'error' event for pre-creation failure, got: {event_types}"
    )
    assert "response.created" not in event_types, (
        f"Pre-creation error must NOT emit response.created before 'error' event, got: {event_types}"
    )


def test_streaming__response_in_progress_event_is_in_stream() -> None:
    """B10 — response.in_progress must appear in the SSE stream between response.created and the terminal event."""
    client = _build_client()

    with client.stream(
        "POST",
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": True,
            "store": True,
            "background": False,
        },
    ) as response:
        assert response.status_code == 200
        events = _collect_stream_events(response)

    event_types = [e["type"] for e in events]
    assert "response.in_progress" in event_types, f"Expected response.in_progress in SSE stream, got: {event_types}"
    created_idx = event_types.index("response.created")
    in_progress_idx = event_types.index("response.in_progress")
    terminal_set = {"response.completed", "response.failed", "response.incomplete"}
    terminal_idx = next((i for i, t in enumerate(event_types) if t in terminal_set), None)
    assert terminal_idx is not None, f"No terminal event found in: {event_types}"
    assert created_idx < in_progress_idx < terminal_idx, (
        f"response.in_progress must appear after response.created and before terminal event. Order was: {event_types}"
    )


def test_streaming__post_creation_error_yields_response_failed_not_error_event() -> None:
    """B13 — Handler raising after response.created → terminal is response.failed, NOT a standalone error event."""
    handler = _throwing_after_created_handler
    app = ResponsesAgentServerHost()
    app.response_handler(handler)
    client = TestClient(app, raise_server_exceptions=False)

    with client.stream(
        "POST",
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": True,
            "store": True,
            "background": False,
        },
    ) as response:
        assert response.status_code == 200
        events = _collect_stream_events(response)

    event_types = [e["type"] for e in events]
    assert "response.failed" in event_types, (
        f"Expected response.failed terminal event after post-creation error, got: {event_types}"
    )
    # After response.created has been emitted, no standalone 'error' event should appear.
    # The failure must be surfaced as response.failed, not a raw error event.
    assert "error" not in event_types, (
        f"Standalone 'error' event must not appear after response.created. Events: {event_types}"
    )


# ══════════════════════════════════════════════════════════
# Task 4.1 — _process_handler_events pipeline contract tests
# ══════════════════════════════════════════════════════════


def test_stream_pre_creation_error_emits_error_event() -> None:
    """T1 — Handler raises before yielding; stream=True → SSE stream contains only a standalone error event.

    B8: The standalone ``error`` event must be the only event; ``response.created`` must NOT appear.
    """
    _app = ResponsesAgentServerHost()
    _app.response_handler(_throwing_before_yield_handler)
    client = TestClient(_app, raise_server_exceptions=False)

    with client.stream(
        "POST",
        "/responses",
        json={"model": "gpt-4o-mini", "input": "hello", "stream": True, "store": True, "background": False},
    ) as response:
        assert response.status_code == 200
        events = _collect_stream_events(response)

    event_types = [e["type"] for e in events]
    assert event_types == ["error"], f"Pre-creation error must produce exactly one 'error' event, got: {event_types}"
    assert "response.created" not in event_types


def test_stream_post_creation_error_emits_response_failed() -> None:
    """T2 — Handler raises after response.created; stream=True → SSE ends with response.failed.

    B13: After response.created, handler failures surface as ``response.failed``, not raw ``error``.
    """
    _app = ResponsesAgentServerHost()
    _app.response_handler(_throwing_after_created_handler)
    client = TestClient(_app, raise_server_exceptions=False)

    with client.stream(
        "POST",
        "/responses",
        json={"model": "gpt-4o-mini", "input": "hello", "stream": True, "store": True, "background": False},
    ) as response:
        assert response.status_code == 200
        events = _collect_stream_events(response)

    event_types = [e["type"] for e in events]
    assert "response.failed" in event_types, (
        f"Expected response.failed terminal after post-creation error, got: {event_types}"
    )
    assert "error" not in event_types, f"No standalone error event expected after response.created, got: {event_types}"
    # Exactly one terminal event
    terminal_types = {"response.completed", "response.failed", "response.incomplete"}
    assert sum(1 for t in event_types if t in terminal_types) == 1


def test_stream_empty_handler_emits_full_lifecycle() -> None:
    """T3 — Handler yields zero events; _process_handler_events synthesises full lifecycle.

    The SSE stream must contain response.created → response.in_progress → response.completed.
    """
    client = _build_client()

    with client.stream(
        "POST",
        "/responses",
        json={"model": "gpt-4o-mini", "input": "hello", "stream": True, "store": True, "background": False},
    ) as response:
        assert response.status_code == 200
        events = _collect_stream_events(response)

    event_types = [e["type"] for e in events]
    assert "response.created" in event_types, f"Missing response.created: {event_types}"
    assert "response.in_progress" in event_types, f"Missing response.in_progress: {event_types}"
    terminal_types = {"response.completed", "response.failed", "response.incomplete"}
    assert any(t in terminal_types for t in event_types), f"Missing terminal event in: {event_types}"
    # created must come before in_progress which must come before terminal
    created_idx = event_types.index("response.created")
    in_progress_idx = event_types.index("response.in_progress")
    terminal_idx = next(i for i, t in enumerate(event_types) if t in terminal_types)
    assert created_idx < in_progress_idx < terminal_idx, f"Lifecycle order violated: {event_types}"


def test_stream_sequence_numbers_monotonic() -> None:
    """T4 — SSE events from a streaming response have strictly monotonically
    increasing sequence numbers starting at 0."""
    client = _build_client()

    with client.stream(
        "POST",
        "/responses",
        json={"model": "gpt-4o-mini", "input": "hello", "stream": True, "store": True, "background": False},
    ) as response:
        assert response.status_code == 200
        events = _collect_stream_events(response)

    assert events, "Expected at least one SSE event"
    sequence_numbers = [e["data"].get("sequence_number") for e in events]
    assert all(isinstance(sn, int) for sn in sequence_numbers), (
        f"All events must carry an integer sequence_number, got: {sequence_numbers}"
    )
    assert sequence_numbers[0] == 0, f"First sequence_number must be 0, got {sequence_numbers[0]}"
    assert sequence_numbers == sorted(sequence_numbers), (
        f"Sequence numbers must be monotonically non-decreasing: {sequence_numbers}"
    )
    assert len(set(sequence_numbers)) == len(sequence_numbers), (
        f"Sequence numbers must be unique (strictly increasing): {sequence_numbers}"
    )
