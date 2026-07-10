# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Protocol conformance tests for ``conversation`` × ``store`` interaction.

``conversation`` + ``store=false`` is accepted — reads history, doesn't write it.
The response is ephemeral (GET returns 404).

Python port of ConversationStoreProtocolTests.
"""

from __future__ import annotations

import json as _json
from typing import Any

from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream

# ════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════


def _collect_sse_events(response: Any) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    current_type: str | None = None
    current_data: str | None = None
    for line in response.iter_lines():
        if not line:
            if current_type is not None:
                payload = _json.loads(current_data) if current_data else {}
                events.append({"type": current_type, "data": payload})
            current_type = None
            current_data = None
            continue
        if line.startswith("event:"):
            current_type = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            current_data = line.split(":", 1)[1].strip()
    if current_type is not None:
        payload = _json.loads(current_data) if current_data else {}
        events.append({"type": current_type, "data": payload})
    return events


def _simple_text_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that emits created + completed."""

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
        yield stream.emit_created()
        yield stream.emit_completed()

    return _events()


def _noop_handler(request: Any, context: Any, cancellation_signal: Any):
    async def _events():
        if False:
            yield None

    return _events()


def _build_client(handler: Any = None) -> TestClient:
    app = ResponsesAgentServerHost()
    app.response_handler(handler or _noop_handler)
    return TestClient(app)


# ════════════════════════════════════════════════════════════
# conversation (string ID) + store=false → 200 SSE, GET → 404
# ════════════════════════════════════════════════════════════


def test_store_false_with_conversation_string_id_returns_200_ephemeral() -> None:
    """conversation + store=false is accepted and response is ephemeral (GET → 404)."""
    client = _build_client(_simple_text_handler)

    with client.stream(
        "POST",
        "/responses",
        json={
            "model": "test",
            "store": False,
            "stream": True,
            "conversation": "conv_abc123",
        },
    ) as resp:
        assert resp.status_code == 200
        content_type = resp.headers.get("content-type", "")
        assert "text/event-stream" in content_type
        events = _collect_sse_events(resp)

    # Verify stream completed
    terminal = [e for e in events if e["type"] == "response.completed"]
    assert terminal, "Expected response.completed event"

    # Extract response ID and verify ephemeral (GET → 404)
    response_id = events[0]["data"]["response"]["id"]
    get_resp = client.get(f"/responses/{response_id}")
    assert get_resp.status_code == 404


# ════════════════════════════════════════════════════════════
# conversation (object) + store=false → 200 SSE, GET → 404
# ════════════════════════════════════════════════════════════


def test_store_false_with_conversation_object_returns_200_ephemeral() -> None:
    """conversation object + store=false is accepted and response is ephemeral (GET → 404)."""
    client = _build_client(_simple_text_handler)

    with client.stream(
        "POST",
        "/responses",
        json={
            "model": "test",
            "store": False,
            "stream": True,
            "conversation": {"id": "conv_xyz789"},
        },
    ) as resp:
        assert resp.status_code == 200
        content_type = resp.headers.get("content-type", "")
        assert "text/event-stream" in content_type
        events = _collect_sse_events(resp)

    terminal = [e for e in events if e["type"] == "response.completed"]
    assert terminal, "Expected response.completed event"

    response_id = events[0]["data"]["response"]["id"]
    get_resp = client.get(f"/responses/{response_id}")
    assert get_resp.status_code == 404


# ════════════════════════════════════════════════════════════
# store=true + conversation is allowed (not rejected)
# ════════════════════════════════════════════════════════════


def test_store_true_with_conversation_is_allowed() -> None:
    """store=true + conversation combination should not be rejected."""
    client = _build_client()

    response = client.post(
        "/responses",
        json={
            "model": "test",
            "store": True,
            "conversation": "conv_abc123",
        },
    )
    # Should not be 400 — this combination is valid
    assert response.status_code != 400


# ════════════════════════════════════════════════════════════
# store=false without conversation is allowed
# ════════════════════════════════════════════════════════════


def test_store_false_without_conversation_is_allowed() -> None:
    """store=false without conversation should be accepted."""
    client = _build_client()

    response = client.post(
        "/responses",
        json={
            "model": "test",
            "store": False,
        },
    )
    assert response.status_code == 200


# ════════════════════════════════════════════════════════════
# Conversation round-trip tests
# (ported from ConversationStoreProtocolTests.cs)
# ════════════════════════════════════════════════════════════


def test_default_with_conversation_string_round_trips_in_response() -> None:
    """Conversation string round-trips in the default (sync) JSON response."""
    client = _build_client()

    response = client.post(
        "/responses",
        json={"model": "test", "conversation": "conv_abc123"},
    )
    assert response.status_code == 200
    payload = response.json()
    conv = payload.get("conversation")
    assert conv is not None, "conversation must be present in response"
    conv_id = conv.get("id") if isinstance(conv, dict) else conv
    assert conv_id == "conv_abc123", f"Expected conversation.id='conv_abc123', got {conv_id!r}"


def test_default_with_conversation_object_round_trips_in_response() -> None:
    """Conversation object round-trips in the default (sync) JSON response."""
    client = _build_client()

    response = client.post(
        "/responses",
        json={"model": "test", "conversation": {"id": "conv_xyz789"}},
    )
    assert response.status_code == 200
    payload = response.json()
    conv = payload.get("conversation")
    assert conv is not None, "conversation must be present in response"
    conv_id = conv.get("id") if isinstance(conv, dict) else conv
    assert conv_id == "conv_xyz789", f"Expected conversation.id='conv_xyz789', got {conv_id!r}"


def test_streaming_with_conversation_string_round_trips_in_created_event() -> None:
    """Conversation string is stamped on the response.created SSE event."""
    client = _build_client(_simple_text_handler)

    with client.stream(
        "POST",
        "/responses",
        json={"model": "test", "stream": True, "conversation": "conv_abc123"},
    ) as resp:
        assert resp.status_code == 200
        events = _collect_sse_events(resp)

    created = [e for e in events if e["type"] == "response.created"]
    assert created, "Expected response.created event"
    conv = created[0]["data"]["response"].get("conversation")
    assert conv is not None, "conversation must be stamped on response.created"
    conv_id = conv.get("id") if isinstance(conv, dict) else conv
    assert conv_id == "conv_abc123"


def test_streaming_with_conversation_object_round_trips_in_created_event() -> None:
    """Conversation object is stamped on the response.created SSE event."""
    client = _build_client(_simple_text_handler)

    with client.stream(
        "POST",
        "/responses",
        json={"model": "test", "stream": True, "conversation": {"id": "conv_xyz789"}},
    ) as resp:
        assert resp.status_code == 200
        events = _collect_sse_events(resp)

    created = [e for e in events if e["type"] == "response.created"]
    assert created, "Expected response.created event"
    conv = created[0]["data"]["response"].get("conversation")
    assert conv is not None, "conversation must be stamped on response.created"
    conv_id = conv.get("id") if isinstance(conv, dict) else conv
    assert conv_id == "conv_xyz789"


def test_streaming_conversation_stamped_on_completed_event() -> None:
    """Conversation ID is stamped on the response.completed SSE event."""
    client = _build_client(_simple_text_handler)

    with client.stream(
        "POST",
        "/responses",
        json={"model": "test", "stream": True, "conversation": "conv_roundtrip"},
    ) as resp:
        assert resp.status_code == 200
        events = _collect_sse_events(resp)

    completed = [e for e in events if e["type"] == "response.completed"]
    assert completed, "Expected response.completed event"
    conv = completed[0]["data"]["response"].get("conversation")
    assert conv is not None, "conversation must be stamped on response.completed"
    conv_id = conv.get("id") if isinstance(conv, dict) else conv
    assert conv_id == "conv_roundtrip"


def _lifecycle_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that emits created → in_progress → completed lifecycle events."""

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
        yield stream.emit_created()
        yield stream.emit_in_progress()
        yield stream.emit_completed()

    return _events()


def test_streaming_conversation_stamped_on_all_lifecycle_events() -> None:
    """Conversation ID is stamped on all lifecycle events (created, in_progress, completed)."""
    client = _build_client(_lifecycle_handler)

    with client.stream(
        "POST",
        "/responses",
        json={"model": "test", "stream": True, "conversation": "conv_all_events"},
    ) as resp:
        assert resp.status_code == 200
        events = _collect_sse_events(resp)

    lifecycle_types = {"response.created", "response.in_progress", "response.completed"}
    lifecycle_events = [e for e in events if e["type"] in lifecycle_types]
    assert len(lifecycle_events) >= 3, (
        f"Expected at least 3 lifecycle events, got {[e['type'] for e in lifecycle_events]}"
    )

    for evt in lifecycle_events:
        conv = evt["data"]["response"].get("conversation")
        assert conv is not None, f"conversation must be stamped on {evt['type']}"
        conv_id = conv.get("id") if isinstance(conv, dict) else conv
        assert conv_id == "conv_all_events", (
            f"Expected conversation.id='conv_all_events' on {evt['type']}, got {conv_id!r}"
        )


def test_background_with_conversation_string_round_trips_in_response() -> None:
    """Background mode: conversation string round-trips in the 200 POST response."""
    client = _build_client()

    response = client.post(
        "/responses",
        json={
            "model": "test",
            "background": True,
            "store": True,
            "conversation": "conv_bg_123",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    conv = payload.get("conversation")
    assert conv is not None, "conversation must be present in background response"
    conv_id = conv.get("id") if isinstance(conv, dict) else conv
    assert conv_id == "conv_bg_123", f"Expected conversation.id='conv_bg_123', got {conv_id!r}"


def test_default_without_conversation_response_has_null_conversation() -> None:
    """When no conversation is provided, the conversation property is absent or null."""
    client = _build_client()

    response = client.post(
        "/responses",
        json={"model": "test"},
    )
    assert response.status_code == 200
    payload = response.json()
    conv = payload.get("conversation")
    # conversation should be absent or null
    assert conv is None, f"Expected null/absent conversation when not provided, got {conv!r}"
