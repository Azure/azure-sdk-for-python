# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests for GET /responses/{response_id} endpoint behavior."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost


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
    response_id = events[0]["data"]["response"].get("id")
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
    response_id = events[0]["data"]["response"].get("id")
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


def test_get_replay__rejects_bg_non_stream_response() -> None:
    """B2 — SSE replay requires stream=true at creation. background=true, stream=false → 400."""
    client = _build_client()

    create_response = client.post(
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hello",
            "stream": False,
            "store": True,
            "background": True,
        },
    )
    assert create_response.status_code == 200
    response_id = create_response.json()["id"]

    replay_response = client.get(f"/responses/{response_id}?stream=true")
    assert replay_response.status_code == 400
    payload = replay_response.json()
    assert payload["error"]["type"] == "invalid_request_error"


# ══════════════════════════════════════════════════════════
# B5: SSE replay rejection message text
# ══════════════════════════════════════════════════════════


def test_get_replay__rejection_message_hints_at_background_true() -> None:
    """B5 — SSE replay rejection error message contains 'background=true' hint.

    Clients should know how to fix their request.
    """
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

    replay_response = client.get(f"/responses/{response_id}?stream=true")
    assert replay_response.status_code == 400
    payload = replay_response.json()
    error_message = payload["error"].get("message", "")
    assert "background=true" in error_message, (
        f"Error message should hint at 'background=true' to guide the client, but got: {error_message!r}"
    )


# ════════════════════════════════════════════════════════
# N-6: GET ?stream=true SSE response headers
# ════════════════════════════════════════════════════════


def test_get_replay__sse_response_headers_are_correct() -> None:
    """SSE headers contract — GET ?stream=true replay must return required SSE response headers."""
    client = _build_client()

    response_id = _create_background_streaming_and_get_response_id(client)

    with client.stream("GET", f"/responses/{response_id}?stream=true") as replay_response:
        assert replay_response.status_code == 200
        headers = replay_response.headers

    content_type = headers.get("content-type", "")
    assert "text/event-stream" in content_type, (
        f"SSE replay Content-Type must be text/event-stream, got: {content_type!r}"
    )
    assert headers.get("cache-control") == "no-cache", (
        f"SSE replay Cache-Control must be no-cache, got: {headers.get('cache-control')!r}"
    )
    assert headers.get("connection", "").lower() == "keep-alive", (
        f"SSE replay Connection must be keep-alive, got: {headers.get('connection')!r}"
    )
    assert headers.get("x-accel-buffering") == "no", (
        f"SSE replay X-Accel-Buffering must be no, got: {headers.get('x-accel-buffering')!r}"
    )


# ══════════════════════════════════════════════════════════
# Task 4.2 — _finalize_bg_stream / _finalize_non_bg_stream
# ══════════════════════════════════════════════════════════


def test_c2_sync_stream_stored_get_returns_200() -> None:
    """T1 — store=True, bg=False, stream=True: POST then GET returns HTTP 200.

    _finalize_non_bg_stream must register a ResponseExecution so that the
    subsequent GET can find the stored non-background stream response.
    """
    client = _build_client()

    with client.stream(
        "POST",
        "/responses",
        json={"model": "gpt-4o-mini", "input": "hello", "stream": True, "store": True, "background": False},
    ) as create_response:
        assert create_response.status_code == 200
        events = _collect_replay_events(create_response)

    assert events, "Expected at least one SSE event"
    response_id = events[0]["data"]["response"].get("id")
    assert isinstance(response_id, str)

    get_response = client.get(f"/responses/{response_id}")
    assert get_response.status_code == 200, (
        f"_finalize_non_bg_stream must persist the record so GET returns 200, got {get_response.status_code}"
    )
    payload = get_response.json()
    assert payload.get("status") in {"completed", "failed", "incomplete", "cancelled"}, (
        f"Non-bg stored stream must be terminal after POST completes, got status={payload.get('status')!r}"
    )


def test_c4_bg_stream_get_sse_replay() -> None:
    """T2 — store=True, bg=True, stream=True: POST complete, then GET ?stream=true returns SSE replay.

    _finalize_bg_stream must complete the subject so that the subsequent
    replay GET can iterate the historical events to completion.
    """
    client = _build_client()

    with client.stream(
        "POST",
        "/responses",
        json={"model": "gpt-4o-mini", "input": "hello", "stream": True, "store": True, "background": True},
    ) as create_response:
        assert create_response.status_code == 200
        create_events = _collect_replay_events(create_response)

    assert create_events, "Expected at least one SSE event from POST"
    response_id = create_events[0]["data"]["response"].get("id")
    assert isinstance(response_id, str)

    with client.stream("GET", f"/responses/{response_id}?stream=true") as replay_response:
        assert replay_response.status_code == 200, (
            f"bg+stream GET ?stream=true must return 200, got {replay_response.status_code}"
        )
        assert replay_response.headers.get("content-type", "").startswith("text/event-stream")
        replay_events = _collect_replay_events(replay_response)

    assert replay_events, "Expected at least one event in SSE replay"
    replay_types = [e["type"] for e in replay_events]
    terminal_types = {"response.completed", "response.failed", "response.incomplete"}
    assert any(t in terminal_types for t in replay_types), (
        f"SSE replay must include a terminal event, got: {replay_types}"
    )
    # Replay must start from the beginning (response.created should be present)
    assert "response.created" in replay_types, f"SSE replay must include response.created, got: {replay_types}"


def test_c6_non_stored_stream_no_get() -> None:
    """T3 — store=False, bg=False, stream=True: GET returns HTTP 404.

    _finalize_non_bg_stream must NOT register the execution record when
    store=False, so a subsequent GET returns 404 (B16 / C6 contract).
    """
    client = _build_client()

    with client.stream(
        "POST",
        "/responses",
        json={"model": "gpt-4o-mini", "input": "hello", "stream": True, "store": False, "background": False},
    ) as create_response:
        assert create_response.status_code == 200
        create_events = _collect_replay_events(create_response)

    assert create_events, "Expected at least one SSE event from POST"
    response_id = create_events[0]["data"]["response"].get("id")
    assert isinstance(response_id, str)

    get_response = client.get(f"/responses/{response_id}")
    assert get_response.status_code == 404, (
        f"store=False stream response must not be retrievable via GET (C6), got {get_response.status_code}"
    )


def test_bg_stream_cancelled_subject_completed() -> None:
    """T4 — bg+stream response cancelled mid-stream: subject.complete() is called, no hang.

    _finalize_bg_stream must call subject.complete() even when the record's
    status is 'cancelled', so that live replay subscribers can exit cleanly.
    """
    from azure.ai.agentserver.responses._id_generator import IdGenerator
    from tests._helpers import poll_until

    gate_started: list[bool] = []

    def _blocking_bg_stream_handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            yield {"type": "response.created", "response": {"status": "in_progress", "output": []}}
            gate_started.append(True)
            # Block until cancelled
            while not cancellation_signal.is_set():
                import asyncio as _asyncio

                await _asyncio.sleep(0.01)

        return _events()

    import threading

    _app = ResponsesAgentServerHost()
    _app.response_handler(_blocking_bg_stream_handler)  # type: ignore[arg-type]  # yields raw dicts to test coercion
    app = _app

    response_id = IdGenerator.new_response_id()
    stream_events_received: list[str] = []
    stream_done = threading.Event()

    def _stream_thread() -> None:
        from starlette.testclient import TestClient as _TC

        _client = _TC(app)
        with _client.stream(
            "POST",
            "/responses",
            json={
                "response_id": response_id,
                "model": "gpt-4o-mini",
                "input": "hello",
                "stream": True,
                "store": True,
                "background": True,
            },
        ) as resp:
            for line in resp.iter_lines():
                stream_events_received.append(line)
        stream_done.set()

    t = threading.Thread(target=_stream_thread, daemon=True)
    t.start()

    # Wait for handler to start
    ok, _ = poll_until(
        lambda: bool(gate_started),
        timeout_s=5.0,
        interval_s=0.02,
        label="wait for bg stream handler to start",
    )
    assert ok, "Handler did not start within timeout"

    # Cancel the response
    from starlette.testclient import TestClient as _TC2

    _cancel_client = _TC2(app)
    cancel_resp = _cancel_client.post(f"/responses/{response_id}/cancel")
    assert cancel_resp.status_code == 200

    # The SSE stream should terminate (subject.complete() unblocks the iterator)
    assert stream_done.wait(timeout=5.0), (
        "_finalize_bg_stream must call subject.complete() so SSE stream terminates after cancel"
    )
    t.join(timeout=1.0)


# ---------------------------------------------------------------------------
# Missing protocol parity tests (ported from GetResponseProtocolTests)
# ---------------------------------------------------------------------------


def _cancellable_bg_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that blocks until cancelled — keeps bg response in_progress."""

    async def _events():
        yield {
            "type": "response.created",
            "response": {"status": "in_progress", "output": []},
        }
        while not cancellation_signal.is_set():
            await asyncio.sleep(0.01)

    return _events()


def test_get__in_progress_bg_response_returns_200() -> None:
    """GET on a background response that is still in_progress returns 200 with status in_progress."""
    app = ResponsesAgentServerHost()
    app.response_handler(_cancellable_bg_handler)  # type: ignore[arg-type]  # yields raw dicts to test coercion
    client = TestClient(app)

    create = client.post(
        "/responses",
        json={"model": "test", "input": "hello", "stream": False, "store": True, "background": True},
    )
    assert create.status_code == 200
    response_id = create.json()["id"]

    get = client.get(f"/responses/{response_id}")
    assert get.status_code == 200
    assert get.json()["status"] == "in_progress"

    # Clean up
    client.post(f"/responses/{response_id}/cancel")


def test_get__cancelled_bg_returns_200_with_cancelled_status() -> None:
    """GET on a cancelled background response returns 200 with status=cancelled and empty output."""
    app = ResponsesAgentServerHost()
    app.response_handler(_cancellable_bg_handler)  # type: ignore[arg-type]  # yields raw dicts to test coercion
    client = TestClient(app)

    create = client.post(
        "/responses",
        json={"model": "test", "input": "hello", "stream": False, "store": True, "background": True},
    )
    assert create.status_code == 200
    response_id = create.json()["id"]

    cancel = client.post(f"/responses/{response_id}/cancel")
    assert cancel.status_code == 200

    get = client.get(f"/responses/{response_id}")
    assert get.status_code == 200
    payload = get.json()
    assert payload["status"] == "cancelled"
    assert payload.get("output", []) == [], "Cancelled response must have 0 output items"


def test_get__sse_replay_starting_after_max_returns_no_events() -> None:
    """SSE replay with starting_after >= max sequence number returns an empty event stream."""
    client = _build_client()
    response_id = _create_background_streaming_and_get_response_id(client)

    # starting_after=9999 — way beyond any sequence in a simple handler
    with client.stream(
        "GET",
        f"/responses/{response_id}?stream=true&starting_after=9999",
    ) as replay:
        assert replay.status_code == 200
        events = _collect_replay_events(replay)

    assert events == [], "Replay with starting_after >= max seq must return 0 events"


def test_get__sse_replay_store_false_returns_404() -> None:
    """SSE replay on a store=false response returns 404."""
    client = _build_client()

    create = client.post(
        "/responses",
        json={"model": "test", "input": "hello", "stream": False, "store": False},
    )
    assert create.status_code == 200
    response_id = create.json()["id"]

    with client.stream("GET", f"/responses/{response_id}?stream=true") as replay:
        assert replay.status_code == 404


def test_get__stream_false_returns_json_snapshot() -> None:
    """Explicit ?stream=false returns a JSON snapshot, not SSE."""
    client = _build_client()
    response_id = _create_background_streaming_and_get_response_id(client)

    get = client.get(f"/responses/{response_id}?stream=false")
    assert get.status_code == 200
    assert get.headers.get("content-type", "").startswith("application/json")
    assert get.json()["id"] == response_id


def test_get__sse_replay_has_correct_sequence_numbers() -> None:
    """SSE replay produces monotonically increasing sequence numbers starting from 0."""
    client = _build_client()
    response_id = _create_background_streaming_and_get_response_id(client)

    with client.stream("GET", f"/responses/{response_id}?stream=true") as replay:
        assert replay.status_code == 200
        events = _collect_replay_events(replay)

    assert len(events) >= 2, "Expected at least 2 replayed SSE events"
    seq_nums = [e["data"].get("sequence_number") for e in events]
    assert seq_nums[0] == 0, "First sequence_number must be 0"
    for i in range(1, len(seq_nums)):
        assert seq_nums[i] > seq_nums[i - 1], (
            f"Sequence numbers not monotonically increasing at index {i}: {seq_nums[i - 1]} → {seq_nums[i]}"
        )


def test_get__accept_sse_without_stream_true_returns_json_snapshot() -> None:
    """Accept: text/event-stream WITHOUT ?stream=true returns JSON snapshot — Accept header is NOT a trigger for SSE.

    Ported from GetResponseProtocolTests.GET_WithAcceptSse_WithoutStreamTrue_Returns200_JsonSnapshot.
    """
    client = _build_client()
    response_id = _create_background_streaming_and_get_response_id(client)

    get = client.get(
        f"/responses/{response_id}",
        headers={"Accept": "text/event-stream"},
    )
    assert get.status_code == 200
    content_type = get.headers.get("content-type", "")
    assert content_type.startswith("application/json"), (
        f"Expected application/json when Accept: text/event-stream but no ?stream=true, got {content_type!r}"
    )
    assert get.json()["id"] == response_id


def test_get__store_false_returns_404() -> None:
    """GET on a store=false response returns 404.

    Ported from GetResponseProtocolTests.GET_StoreFalse_Returns404.
    """
    client = _build_client()

    create = client.post(
        "/responses",
        json={"model": "test", "input": "hello", "stream": False, "store": False},
    )
    assert create.status_code == 200
    response_id = create.json()["id"]

    get = client.get(f"/responses/{response_id}")
    assert get.status_code == 404
