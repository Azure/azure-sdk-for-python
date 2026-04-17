# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Protocol conformance tests for auto-stamping ``response_id`` on output items (US2).

Validates that every output item emitted by the SDK has ``response_id`` matching
the parent response ID, and that handler-set values take precedence.

Python port of ResponseIdAutoStampProtocolTests.
"""

from __future__ import annotations

import json as _json
from typing import Any

from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream
from tests._helpers import poll_until

# ════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════


def _collect_sse_events(response: Any) -> list[dict[str, Any]]:
    """Parse SSE lines from a streaming response."""
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


def _handler_with_output(request: Any, context: Any, cancellation_signal: Any):
    """Handler that emits a single message output item using the builder."""

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
        yield stream.emit_created()
        msg = stream.add_output_item_message()
        yield msg.emit_added()
        text = msg.add_text_content()
        yield text.emit_added()
        yield text.emit_delta("Hello")
        yield text.emit_text_done()
        yield text.emit_done()
        yield msg.emit_done()
        yield stream.emit_completed()

    return _events()


def _handler_with_custom_response_id(custom_id: str):
    """Handler that creates output items and overrides response_id on them."""

    def handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
            yield stream.emit_created()

            # Use the builder to create the item, then modify response_id on the emitted event
            msg = stream.add_output_item_message()
            added_event = msg.emit_added()
            # Override response_id on the item to test handler-set precedence
            added_event["item"]["response_id"] = custom_id
            yield added_event

            done_event = msg.emit_done()
            done_event["item"]["response_id"] = custom_id
            yield done_event

            yield stream.emit_completed()

        return _events()

    return handler


def _handler_with_multiple_outputs(request: Any, context: Any, cancellation_signal: Any):
    """Handler that emits two message output items."""

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
        yield stream.emit_created()

        msg1 = stream.add_output_item_message()
        yield msg1.emit_added()
        text1 = msg1.add_text_content()
        yield text1.emit_added()
        yield text1.emit_delta("Hello")
        yield text1.emit_text_done()
        yield text1.emit_done()
        yield msg1.emit_done()

        msg2 = stream.add_output_item_message()
        yield msg2.emit_added()
        text2 = msg2.add_text_content()
        yield text2.emit_added()
        yield text2.emit_delta("World")
        yield text2.emit_text_done()
        yield text2.emit_done()
        yield msg2.emit_done()

        yield stream.emit_completed()

    return _events()


def _direct_yield_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that directly yields events without using builders.

    Does NOT set response_id on output items. Layer 2 (event consumption loop)
    must auto-stamp it.
    """

    async def _events():
        # Use builder for response.created (well-formed)
        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
        yield stream.emit_created()

        # Directly yield output_item events without response_id using wire format
        item_id = f"caitem_{context.response_id[7:25]}directyield00000000000000000001"
        yield {
            "type": "response.output_item.added",
            "item": {
                "id": item_id,
                "type": "message",
                "role": "assistant",
                "status": "in_progress",
                "content": [],
                # response_id intentionally NOT set — Layer 2 should stamp it
            },
            "output_index": 0,
        }
        yield {
            "type": "response.output_item.done",
            "item": {
                "id": item_id,
                "type": "message",
                "role": "assistant",
                "status": "completed",
                "content": [],
                # response_id intentionally NOT set
            },
            "output_index": 0,
        }

        yield stream.emit_completed()

    return _events()


def _build_client(handler: Any) -> TestClient:
    app = ResponsesAgentServerHost()
    app.response_handler(handler)
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
# T012: Streaming output items have response_id from response.created
# ════════════════════════════════════════════════════════════


def test_streaming_output_items_have_response_id_matching_response_created() -> None:
    """T012 — response_id on output items must match the response ID."""
    client = _build_client(_handler_with_output)

    with client.stream("POST", "/responses", json={"model": "test", "stream": True}) as resp:
        assert resp.status_code == 200
        events = _collect_sse_events(resp)

    # Extract response ID from response.created
    created_event = next(e for e in events if e["type"] == "response.created")
    response_id = created_event["data"]["response"]["id"]

    # All output_item.added and output_item.done events must have matching response_id
    item_events = [e for e in events if e["type"] in ("response.output_item.added", "response.output_item.done")]
    assert item_events, "Expected at least one output item event"

    for evt in item_events:
        item = evt["data"]["item"]
        assert item.get("response_id") == response_id, (
            f"Expected response_id={response_id}, got {item.get('response_id')} on event {evt['type']}"
        )


# ════════════════════════════════════════════════════════════
# T013: Handler-set response_id is preserved
# ════════════════════════════════════════════════════════════


def test_handler_set_response_id_is_preserved() -> None:
    """T013 — handler-set response_id takes precedence over auto-stamping."""
    custom_id = "custom-response-id-override"
    client = _build_client(_handler_with_custom_response_id(custom_id))

    with client.stream("POST", "/responses", json={"model": "test", "stream": True}) as resp:
        assert resp.status_code == 200
        events = _collect_sse_events(resp)

    item_added = next(e for e in events if e["type"] == "response.output_item.added")
    item = item_added["data"]["item"]
    assert item.get("response_id") == custom_id


# ════════════════════════════════════════════════════════════
# T014: Multiple output items all get same response_id
# ════════════════════════════════════════════════════════════


def test_multiple_output_items_all_have_same_response_id() -> None:
    """T014 — all output items share the same response_id."""
    client = _build_client(_handler_with_multiple_outputs)

    with client.stream("POST", "/responses", json={"model": "test", "stream": True}) as resp:
        assert resp.status_code == 200
        events = _collect_sse_events(resp)

    created_event = next(e for e in events if e["type"] == "response.created")
    response_id = created_event["data"]["response"]["id"]

    item_events = [e for e in events if e["type"] in ("response.output_item.added", "response.output_item.done")]
    assert len(item_events) >= 4, f"Expected at least 4 item events (2 added + 2 done), got {len(item_events)}"

    for evt in item_events:
        item = evt["data"]["item"]
        assert item.get("response_id") == response_id


# ════════════════════════════════════════════════════════════
# T015: GET JSON snapshot has response_id on output items
# ════════════════════════════════════════════════════════════


def test_get_json_snapshot_has_response_id_on_output_items() -> None:
    """T015 — GET JSON snapshot includes response_id on output items."""
    client = _build_client(_handler_with_output)

    # Create a stored response (bg=True for GETable state)
    r = client.post(
        "/responses",
        json={"model": "test", "stream": False, "store": True, "background": True},
    )
    assert r.status_code == 200
    response_id = r.json()["id"]
    _wait_for_terminal(client, response_id)

    get_resp = client.get(f"/responses/{response_id}")
    assert get_resp.status_code == 200
    doc = get_resp.json()
    output = doc["output"]
    assert len(output) > 0, "Expected at least one output item"

    for item in output:
        assert item.get("response_id") == response_id, (
            f"Expected response_id={response_id} on GET output item, got {item.get('response_id')}"
        )


# ════════════════════════════════════════════════════════════
# T016: Direct-yield handler gets response_id auto-stamped (Layer 2)
# ════════════════════════════════════════════════════════════


def test_direct_yield_handler_gets_response_id_auto_stamped() -> None:
    """T016 — Layer 2 auto-stamps response_id on items from direct-yield handlers."""
    client = _build_client(_direct_yield_handler)

    with client.stream("POST", "/responses", json={"model": "test", "stream": True}) as resp:
        assert resp.status_code == 200
        events = _collect_sse_events(resp)

    created_event = next(e for e in events if e["type"] == "response.created")
    response_id = created_event["data"]["response"]["id"]

    item_added = next(e for e in events if e["type"] == "response.output_item.added")
    item = item_added["data"]["item"]
    assert item.get("response_id") == response_id, (
        f"Expected auto-stamped response_id={response_id}, got {item.get('response_id')}"
    )
