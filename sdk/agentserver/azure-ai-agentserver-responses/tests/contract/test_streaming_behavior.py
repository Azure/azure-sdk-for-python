"""Contract tests for SSE streaming behavior."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from starlette.applications import Starlette
from starlette.testclient import TestClient

from azure.ai.agentserver.responses.hosting import map_responses_server


class _NoopResponseHandler:
    """Minimal handler used to wire the hosting surface in contract tests."""

    def create_async(self, request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            if False:  # pragma: no cover - required to keep async-generator shape.
                yield None

        return _events()


def _build_client() -> TestClient:
    app = Starlette()
    map_responses_server(app, _NoopResponseHandler())
    return TestClient(app)


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
    first_payload = events[0]["data"]
    response_id = first_payload.get("response_id")
    assert response_id == first_payload.get("id")
    assert isinstance(first_payload.get("agent_reference"), dict)

    for event in events:
        payload = event["data"]
        assert payload.get("response_id") == response_id
        assert payload.get("id") == response_id
        assert payload.get("agent_reference") == first_payload.get("agent_reference")


def test_streaming__forwards_emitted_event_before_late_handler_failure() -> None:
    class _FailAfterFirstEventHandler:
        def create_async(self, request: Any, context: Any, cancellation_signal: Any):
            async def _events():
                yield {
                    "type": "response.created",
                    "payload": {
                        "status": "in_progress",
                    },
                }
                await asyncio.sleep(0)
                raise RuntimeError("late stream failure")

            return _events()

    app = Starlette()
    map_responses_server(app, _FailAfterFirstEventHandler())
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
