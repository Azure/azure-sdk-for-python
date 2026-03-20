# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests for GET /responses/{response_id} endpoint behavior."""

from __future__ import annotations

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


def _collect_replay_events(response: Any) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    current_type: str | None = None
    current_data: str | None = None

    for line in response.iter_lines():
        if not line:
            if current_type is not None:
                payload = json.loads(current_data) if current_data else {}
                events.append({"type": current_type, "data": payload})
            current_type = None
            current_data = None
            continue

        if line.startswith("event:"):
            current_type = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            current_data = line.split(":", 1)[1].strip()

    if current_type is not None:
        payload = json.loads(current_data) if current_data else {}
        events.append({"type": current_type, "data": payload})

    return events


def _create_streaming_and_get_response_id(client: TestClient) -> str:
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
    ) as create_response:
        assert create_response.status_code == 200
        assert create_response.headers.get("content-type", "").startswith("text/event-stream")
        events = _collect_replay_events(create_response)

    assert events, "Expected streaming create to emit at least one event"
    response_id = events[0]["data"].get("id")
    assert isinstance(response_id, str)
    return response_id


def _create_background_streaming_and_get_response_id(client: TestClient) -> str:
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
    ) as create_response:
        assert create_response.status_code == 200
        assert create_response.headers.get("content-type", "").startswith("text/event-stream")
        events = _collect_replay_events(create_response)

    assert events, "Expected background streaming create to emit at least one event"
    response_id = events[0]["data"].get("id")
    assert isinstance(response_id, str)
    return response_id


def test_get__returns_latest_snapshot_for_existing_response() -> None:
    client = _build_client()

    create_response = client.post(
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": False,
            "store": True,
            "background": False,
        },
    )
    assert create_response.status_code == 200
    response_id = create_response.json()["id"]

    get_response = client.get(f"/responses/{response_id}")
    assert get_response.status_code == 200
    payload = get_response.json()
    assert payload.get("id") == response_id
    assert payload.get("response_id") == response_id
    assert payload.get("object") == "response"
    assert isinstance(payload.get("agent_reference"), dict)
    assert payload["agent_reference"].get("type") == "agent_reference"
    assert payload.get("status") in {"queued", "in_progress", "completed", "failed", "incomplete", "cancelled"}
    assert payload.get("model") == "gpt-4o-mini"
    assert "sequence_number" not in payload


def test_get__returns_404_for_unknown_response_id() -> None:
    client = _build_client()

    get_response = client.get("/responses/resp_does_not_exist")
    assert get_response.status_code == 404
    payload = get_response.json()
    assert isinstance(payload.get("error"), dict)


def test_get__returns_snapshot_for_stored_non_background_stream_response_after_completion() -> None:
    client = _build_client()

    response_id = _create_streaming_and_get_response_id(client)

    get_response = client.get(f"/responses/{response_id}")
    assert get_response.status_code == 200
    payload = get_response.json()
    assert payload.get("id") == response_id
    assert payload.get("status") in {"completed", "failed", "incomplete", "cancelled"}


def test_get_replay__rejects_request_when_replay_preconditions_are_not_met() -> None:
    client = _build_client()

    response_id = _create_streaming_and_get_response_id(client)

    replay_response = client.get(f"/responses/{response_id}?stream=true")
    assert replay_response.status_code == 400
    payload = replay_response.json()
    assert isinstance(payload.get("error"), dict)
    assert payload["error"].get("type") == "invalid_request_error"
    assert payload["error"].get("param") == "stream"


def test_get_replay__rejects_invalid_starting_after_cursor_type() -> None:
    client = _build_client()

    response_id = _create_background_streaming_and_get_response_id(client)

    replay_response = client.get(f"/responses/{response_id}?stream=true&starting_after=not-an-int")
    assert replay_response.status_code == 400
    payload = replay_response.json()
    assert payload["error"].get("type") == "invalid_request_error"
    assert payload["error"].get("param") == "starting_after"


def test_get_replay__starting_after_returns_events_after_cursor() -> None:
    client = _build_client()

    response_id = _create_background_streaming_and_get_response_id(client)

    with client.stream("GET", f"/responses/{response_id}?stream=true&starting_after=0") as replay_response:
        assert replay_response.status_code == 200
        assert replay_response.headers.get("content-type", "").startswith("text/event-stream")
        replay_events = _collect_replay_events(replay_response)

    assert replay_events, "Expected replay stream to include events after cursor"
    sequence_numbers = [event["data"].get("sequence_number") for event in replay_events]
    assert all(isinstance(sequence_number, int) for sequence_number in sequence_numbers)
    assert min(sequence_numbers) > 0
    terminal_events = {
        "response.completed",
        "response.failed",
        "response.incomplete",
    }
    assert any(event["type"] in terminal_events for event in replay_events)
