# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Protocol conformance tests for auto-stamping ``agent_reference`` on output items (US3).

Validates that ``agent_reference`` from the create request propagates to the
response object and all output items, with handler-set values taking precedence.

Python port of AgentReferenceAutoStampProtocolTests.
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


def _handler_with_handler_set_agent_ref(request: Any, context: Any, cancellation_signal: Any):
    """Handler that sets a custom agent_reference on the output item directly."""

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
        yield stream.emit_created()

        # Use the builder then override agent_reference on the emitted event
        msg = stream.add_output_item_message()
        added_event = msg.emit_added()
        added_event["item"]["agent_reference"] = {
            "type": "agent_reference",
            "name": "handler-agent",
            "version": "9.0",
        }
        yield added_event

        done_event = msg.emit_done()
        done_event["item"]["agent_reference"] = {
            "type": "agent_reference",
            "name": "handler-agent",
            "version": "9.0",
        }
        yield done_event

        yield stream.emit_completed()

    return _events()


def _direct_yield_handler(request: Any, context: Any, cancellation_signal: Any):
    """Handler that directly yields events without using builder.

    Does NOT set agent_reference on output items. Layer 2 must stamp it.
    """

    async def _events():
        # Use builder for response.created
        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
        yield stream.emit_created()

        item_id = f"caitem_{context.response_id[7:25]}directyield00000000000000000001"
        yield {
            "type": "response.output_item.added",
            "item": {
                "id": item_id,
                "type": "message",
                "role": "assistant",
                "status": "in_progress",
                "content": [],
                # agent_reference intentionally NOT set
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
            },
            "output_index": 0,
        }

        yield stream.emit_completed()

    return _events()


def _build_client(handler: Any) -> TestClient:
    app = ResponsesAgentServerHost()
    app.response_handler(handler)
    return TestClient(app)


# ════════════════════════════════════════════════════════════
# T024: agent_reference on CreateResponse appears on response
# ════════════════════════════════════════════════════════════


def test_agent_reference_appears_on_response() -> None:
    """T024 — agent_reference from request propagates to response.created."""
    client = _build_client(_handler_with_output)

    with client.stream(
        "POST",
        "/responses",
        json={
            "model": "test",
            "stream": True,
            "agent_reference": {"type": "agent_reference", "name": "my-agent", "version": "1.0"},
        },
    ) as resp:
        assert resp.status_code == 200
        events = _collect_sse_events(resp)

    created_event = next(e for e in events if e["type"] == "response.created")
    response_obj = created_event["data"]["response"]
    agent_ref = response_obj["agent_reference"]
    assert agent_ref["name"] == "my-agent"
    assert agent_ref["version"] == "1.0"


# ════════════════════════════════════════════════════════════
# T025: agent_reference propagates to output items
# ════════════════════════════════════════════════════════════


def test_agent_reference_propagates_to_output_items() -> None:
    """T025 — agent_reference from request propagates to all output items."""
    client = _build_client(_handler_with_output)

    with client.stream(
        "POST",
        "/responses",
        json={
            "model": "test",
            "stream": True,
            "agent_reference": {"type": "agent_reference", "name": "my-agent", "version": "1.0"},
        },
    ) as resp:
        assert resp.status_code == 200
        events = _collect_sse_events(resp)

    item_events = [e for e in events if e["type"] in ("response.output_item.added", "response.output_item.done")]
    assert item_events, "Expected at least one output item event"

    for evt in item_events:
        item = evt["data"]["item"]
        agent_ref = item.get("agent_reference")
        assert agent_ref is not None, f"agent_reference missing on {evt['type']}"
        assert agent_ref["name"] == "my-agent"
        assert agent_ref["version"] == "1.0"


# ════════════════════════════════════════════════════════════
# T026: Handler-set agent_reference takes precedence
# ════════════════════════════════════════════════════════════


def test_handler_set_agent_reference_is_preserved() -> None:
    """T026 — handler-set agent_reference takes precedence over request agent_reference."""
    client = _build_client(_handler_with_handler_set_agent_ref)

    with client.stream(
        "POST",
        "/responses",
        json={
            "model": "test",
            "stream": True,
            "agent_reference": {"type": "agent_reference", "name": "request-agent", "version": "1.0"},
        },
    ) as resp:
        assert resp.status_code == 200
        events = _collect_sse_events(resp)

    item_added = next(e for e in events if e["type"] == "response.output_item.added")
    item = item_added["data"]["item"]
    agent_ref = item.get("agent_reference")
    assert agent_ref is not None
    assert agent_ref["name"] == "handler-agent", f"Expected handler-agent to take precedence, got {agent_ref['name']}"


# ════════════════════════════════════════════════════════════
# T027: No agent_reference on request → no agent_reference on items
# ════════════════════════════════════════════════════════════


def test_no_agent_reference_on_request_no_agent_reference_on_items() -> None:
    """T027 — without agent_reference on request, output items should not have one."""
    client = _build_client(_handler_with_output)

    with client.stream(
        "POST",
        "/responses",
        json={"model": "test", "stream": True},
    ) as resp:
        assert resp.status_code == 200
        events = _collect_sse_events(resp)

    item_events = [e for e in events if e["type"] in ("response.output_item.added", "response.output_item.done")]
    assert item_events, "Expected at least one output item event"

    for evt in item_events:
        item = evt["data"]["item"]
        agent_ref = item.get("agent_reference")
        # agent_reference should be absent or null when request has none
        assert agent_ref is None or agent_ref == {}, (
            f"Output item should not have agent_reference when request has none, got: {agent_ref}"
        )


# ════════════════════════════════════════════════════════════
# T028: Direct-yield handler gets agent_reference auto-stamped (Layer 2)
# ════════════════════════════════════════════════════════════


def test_direct_yield_handler_gets_agent_reference_auto_stamped() -> None:
    """T028 — Layer 2 auto-stamps agent_reference on items from direct-yield handlers."""
    client = _build_client(_direct_yield_handler)

    with client.stream(
        "POST",
        "/responses",
        json={
            "model": "test",
            "stream": True,
            "agent_reference": {"type": "agent_reference", "name": "direct-agent", "version": "2.0"},
        },
    ) as resp:
        assert resp.status_code == 200
        events = _collect_sse_events(resp)

    item_added = next(e for e in events if e["type"] == "response.output_item.added")
    item = item_added["data"]["item"]
    agent_ref = item.get("agent_reference")
    assert agent_ref is not None, "agent_reference should be auto-stamped by Layer 2"
    assert agent_ref["name"] == "direct-agent"
