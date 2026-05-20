# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Protocol conformance tests for ``x-agent-response-id`` header (B38).

When the header is present with a non-empty value, the SDK MUST use that value
as the response ID instead of generating one.

Python port of ResponseIdHeaderTests.
"""

from __future__ import annotations

import json as _json
from typing import Any

from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses._id_generator import IdGenerator
from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream
from tests._helpers import poll_until

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


_last_context: Any = None


def _tracking_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that records its context for inspection."""
    global _last_context
    _last_context = context

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


def _wait_for_terminal(client: TestClient, response_id: str) -> None:
    ok, diag = poll_until(
        lambda: (
            client.get(f"/responses/{response_id}").json().get("status")
            in ("completed", "failed", "incomplete", "cancelled")
        ),
        timeout_s=5.0,
        label="wait_for_terminal",
    )
    assert ok, diag


# ════════════════════════════════════════════════════════════
# Default mode: x-agent-response-id
# ════════════════════════════════════════════════════════════


def test_default_with_header_uses_header_value() -> None:
    """B38 — default mode: x-agent-response-id header overrides response ID."""
    custom_id = IdGenerator.new_response_id()
    client = _build_client()

    response = client.post(
        "/responses",
        json={"model": "test"},
        headers={"x-agent-response-id": custom_id},
    )
    assert response.status_code == 200
    assert response.json()["id"] == custom_id


def test_default_without_header_generates_caresp_id() -> None:
    """B38 — without header, generates caresp_ prefixed ID."""
    client = _build_client()

    response = client.post("/responses", json={"model": "test"})
    assert response.status_code == 200
    assert response.json()["id"].startswith("caresp_")


def test_default_with_empty_header_generates_caresp_id() -> None:
    """B38 — empty header is ignored, generates caresp_ prefixed ID."""
    client = _build_client()

    response = client.post(
        "/responses",
        json={"model": "test"},
        headers={"x-agent-response-id": ""},
    )
    assert response.status_code == 200
    assert response.json()["id"].startswith("caresp_")


# ════════════════════════════════════════════════════════════
# Streaming mode: x-agent-response-id
# ════════════════════════════════════════════════════════════


def test_streaming_with_header_uses_header_value() -> None:
    """B38 — streaming mode: x-agent-response-id header overrides response ID."""
    custom_id = IdGenerator.new_response_id()
    client = _build_client(_tracking_handler)

    with client.stream(
        "POST",
        "/responses",
        json={"model": "test", "stream": True},
        headers={"x-agent-response-id": custom_id},
    ) as resp:
        events = _collect_sse_events(resp)

    created_event = next(e for e in events if e["type"] == "response.created")
    response_id = created_event["data"]["response"]["id"]
    assert response_id == custom_id


# ════════════════════════════════════════════════════════════
# Background mode: x-agent-response-id
# ════════════════════════════════════════════════════════════


def test_background_with_header_uses_header_value() -> None:
    """B38 — background mode: x-agent-response-id header overrides response ID."""
    custom_id = IdGenerator.new_response_id()
    client = _build_client()

    response = client.post(
        "/responses",
        json={"model": "test", "background": True},
        headers={"x-agent-response-id": custom_id},
    )
    assert response.status_code == 200
    assert response.json()["id"] == custom_id


# ════════════════════════════════════════════════════════════
# Handler receives the correct ResponseId on context
# ════════════════════════════════════════════════════════════


def test_handler_context_has_correct_response_id() -> None:
    """B38 — handler context receives the header-specified response ID."""
    global _last_context
    _last_context = None

    custom_id = IdGenerator.new_response_id()
    client = _build_client(_tracking_handler)

    client.post(
        "/responses",
        json={"model": "test"},
        headers={"x-agent-response-id": custom_id},
    )

    assert _last_context is not None
    assert _last_context.response_id == custom_id
