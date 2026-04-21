# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Protocol conformance tests for detecting direct output manipulation (FR-008a).

Validates that when a handler directly adds/removes items from
ResponseObject.Output without emitting corresponding output_item events,
the SDK detects the inconsistency and fails with a server error.

Python port of OutputManipulationDetectionTests.
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


def _output_manipulation_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that directly manipulates Output without emitting output_item events.

    This violates FR-008a — the SDK should detect this and fail.
    """

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
        yield stream.emit_created()

        # Directly manipulate the response output list without using builder events
        # This is an FR-008a violation
        stream.response.output.append(
            {
                "id": "fake-item-id",
                "type": "message",
                "role": "assistant",
                "status": "completed",
                "content": [],
            }
        )

        yield stream.emit_completed()

    return _events()


def _build_client(handler: Any) -> TestClient:
    app = ResponsesAgentServerHost()
    app.response_handler(handler)
    return TestClient(app)


# ════════════════════════════════════════════════════════════
# T027: Direct Output manipulation → bad handler error (non-streaming)
# ════════════════════════════════════════════════════════════


def test_direct_output_add_without_builder_events_returns_bad_handler_error() -> None:
    """FR-008a — direct output manipulation detected → response fails with server_error.

    The handler directly adds an item to response.output without emitting
    output_item.added. The SDK should detect the inconsistency and fail.
    """
    client = _build_client(_output_manipulation_handler)

    response = client.post("/responses", json={"model": "test"})

    # Output manipulation detected → response lifecycle completes as failed
    assert response.status_code == 200
    doc = response.json()
    assert doc["status"] == "failed"
    error = doc["error"]
    assert error["code"] == "server_error"
    assert error["message"] == "An internal server error occurred."


# ════════════════════════════════════════════════════════════
# Streaming variant — direct output manipulation → response.failed emitted
# ════════════════════════════════════════════════════════════


def test_streaming_direct_output_add_emits_failed_event() -> None:
    """FR-008a — direct output manipulation in streaming mode emits response.failed."""
    client = _build_client(_output_manipulation_handler)

    with client.stream("POST", "/responses", json={"model": "test", "stream": True}) as resp:
        assert resp.status_code == 200
        events = _collect_sse_events(resp)

    # Should have response.created (handler emitted it) then response.failed
    event_types = [e["type"] for e in events]
    assert "response.created" in event_types
    assert "response.failed" in event_types
    assert "response.completed" not in event_types
