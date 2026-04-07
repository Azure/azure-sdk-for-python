# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""End-to-end tests matching .NET SampleEndToEndTests (Samples 1-11)."""

from __future__ import annotations

import json
from typing import Any

import pytest

from starlette.testclient import TestClient

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
    ResponsesServerOptions,
    get_input_expanded,
    get_input_text,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_app(handler, **kwargs) -> TestClient:
    app = ResponsesAgentServerHost(**kwargs)
    app.create_handler(handler)
    return TestClient(app)


def _collect_stream_events(response: Any) -> list[dict[str, Any]]:
    """Parse SSE lines from a streaming response into structured events."""
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


def _post_json(client: TestClient, payload: dict[str, Any]) -> Any:
    return client.post("/responses", json=payload)


def _post_stream(client: TestClient, payload: dict[str, Any]) -> list[dict[str, Any]]:
    payload["stream"] = True
    with client.stream("POST", "/responses", json=payload) as resp:
        assert resp.status_code == 200
        events = _collect_stream_events(resp)
    return events


def _base_payload(input_value: Any = "hello", **overrides) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": "test-model",
        "input": input_value,
        "stream": False,
    }
    payload.update(overrides)
    return payload


# ---------------------------------------------------------------------------
# Sample 1: Getting Started — Echo handler
# ---------------------------------------------------------------------------


def _sample1_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: Any):
    """Echo handler: returns the user's input text."""

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=request.model)
        yield stream.emit_created()

        msg = stream.add_output_item_message()
        yield msg.emit_added()

        text_content = msg.add_text_content()
        yield text_content.emit_added()

        user_text = get_input_text(request)
        yield text_content.emit_delta(user_text)
        yield text_content.emit_done()
        yield msg.emit_content_done(text_content)
        yield msg.emit_done()

        yield stream.emit_completed()

    return _events()


def test_sample1_echo_handler_echoes_input_text() -> None:
    """Non-streaming echo returns correct text."""
    client = _make_app(_sample1_handler)
    resp = _post_json(client, _base_payload("Say something"))

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "completed"
    output = body["output"]
    assert len(output) == 1
    assert output[0]["type"] == "message"
    text_parts = [p for p in output[0]["content"] if p.get("type") == "output_text"]
    assert len(text_parts) == 1
    assert text_parts[0]["text"] == "Say something"


def test_sample1_echo_handler_structured_input() -> None:
    """Structured message input still echoes text."""
    client = _make_app(_sample1_handler)
    structured_input = [
        {
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": "structured hello"}],
        }
    ]
    resp = _post_json(client, _base_payload(structured_input))

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "completed"
    output = body["output"]
    assert len(output) == 1
    text_parts = [p for p in output[0]["content"] if p.get("type") == "output_text"]
    assert text_parts[0]["text"] == "structured hello"


# ---------------------------------------------------------------------------
# Sample 2: Streaming Text Deltas
# ---------------------------------------------------------------------------


def _sample2_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: Any):
    """Streaming handler: emits text in token-by-token deltas."""

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=request.model)
        yield stream.emit_created()

        msg = stream.add_output_item_message()
        yield msg.emit_added()

        text_content = msg.add_text_content()
        yield text_content.emit_added()

        user_text = get_input_text(request)
        tokens = user_text.split() if user_text else ["Hello", "World"]
        for token in tokens:
            yield text_content.emit_delta(token + " ")
        yield text_content.emit_done()
        yield msg.emit_content_done(text_content)
        yield msg.emit_done()

        yield stream.emit_completed()

    return _events()


def test_sample2_streaming_handler_streams_token_deltas() -> None:
    """Streaming response emits delta events."""
    client = _make_app(_sample2_handler)
    events = _post_stream(client, _base_payload("one two three"))

    delta_events = [e for e in events if e["type"] == "response.output_text.delta"]
    assert len(delta_events) == 3
    joined = "".join(e["data"]["delta"] for e in delta_events)
    assert joined.strip() == "one two three"


def test_sample2_streaming_handler_non_streaming_returns_full_text() -> None:
    """Non-streaming fallback returns full text."""
    client = _make_app(_sample2_handler)
    resp = _post_json(client, _base_payload("alpha beta"))

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "completed"
    text_parts = [p for p in body["output"][0]["content"] if p.get("type") == "output_text"]
    assert text_parts[0]["text"].strip() == "alpha beta"


# ---------------------------------------------------------------------------
# Sample 3: Full Control — All lifecycle events
# ---------------------------------------------------------------------------


def _sample3_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: Any):
    """Full lifecycle handler: emits all standard lifecycle event types."""

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=request.model)
        yield stream.emit_created()

        msg = stream.add_output_item_message()
        yield msg.emit_added()

        text_content = msg.add_text_content()
        yield text_content.emit_added()

        user_text = get_input_text(request)
        greeting = f"Hello, {user_text}! Welcome."
        yield text_content.emit_delta(greeting)
        yield text_content.emit_done()
        yield msg.emit_content_done(text_content)
        yield msg.emit_done()

        yield stream.emit_completed()

    return _events()


def test_sample3_full_lifecycle_events() -> None:
    """Streaming response contains all lifecycle event types."""
    client = _make_app(_sample3_handler)
    events = _post_stream(client, _base_payload("World"))

    event_types = [e["type"] for e in events]
    expected_types = [
        "response.created",
        "response.output_item.added",
        "response.content_part.added",
        "response.output_text.delta",
        "response.output_text.done",
        "response.content_part.done",
        "response.output_item.done",
        "response.completed",
    ]
    for expected in expected_types:
        assert expected in event_types, f"Missing event type: {expected}"


def test_sample3_greeting_includes_input() -> None:
    """Greeting text includes user input."""
    client = _make_app(_sample3_handler)
    resp = _post_json(client, _base_payload("Alice"))

    body = resp.json()
    text_parts = [p for p in body["output"][0]["content"] if p.get("type") == "output_text"]
    assert "Alice" in text_parts[0]["text"]
    assert "Hello" in text_parts[0]["text"]


# ---------------------------------------------------------------------------
# Sample 4: Function Calling
# ---------------------------------------------------------------------------


def _sample4_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: Any):
    """Function-calling handler: emits get_weather function call on first turn,
    and a text response on second turn when function_call_output is present."""

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=request.model)
        yield stream.emit_created()

        items = get_input_expanded(request)
        has_fn_output = any(
            (item.get("type") if isinstance(item, dict) else getattr(item, "type", None))
            == "function_call_output"
            for item in items
        )

        if has_fn_output:
            # Second turn: extract function output and echo it as text
            fn_output_text = ""
            for item in items:
                item_type = item.get("type") if isinstance(item, dict) else getattr(item, "type", None)
                if item_type == "function_call_output":
                    fn_output_text = (
                        item.get("output") if isinstance(item, dict) else getattr(item, "output", "")
                    )
                    break

            msg = stream.add_output_item_message()
            yield msg.emit_added()
            text_content = msg.add_text_content()
            yield text_content.emit_added()
            yield text_content.emit_delta(f"The weather is: {fn_output_text}")
            yield text_content.emit_done()
            yield msg.emit_content_done(text_content)
            yield msg.emit_done()
        else:
            # First turn: emit a function call for get_weather
            fc = stream.add_output_item_function_call(name="get_weather", call_id="call_001")
            yield fc.emit_added()
            args = json.dumps({"location": get_input_text(request)})
            yield fc.emit_arguments_delta(args)
            yield fc.emit_arguments_done(args)
            yield fc.emit_done()

        yield stream.emit_completed()

    return _events()


def test_sample4_turn1_emits_function_call() -> None:
    """First turn emits function_call with get_weather."""
    client = _make_app(_sample4_handler)
    events = _post_stream(client, _base_payload("Seattle"))

    added_events = [e for e in events if e["type"] == "response.output_item.added"]
    assert len(added_events) == 1
    item = added_events[0]["data"]["item"]
    assert item["type"] == "function_call"
    assert item["name"] == "get_weather"
    assert item["call_id"] == "call_001"


def test_sample4_turn2_returns_weather_text() -> None:
    """Second turn with function_call_output returns weather text."""
    client = _make_app(_sample4_handler)
    input_items = [
        {
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": "Seattle"}],
        },
        {
            "type": "function_call_output",
            "call_id": "call_001",
            "output": "72°F and sunny",
        },
    ]
    resp = _post_json(client, _base_payload(input_items))

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "completed"
    msg_outputs = [o for o in body["output"] if o.get("type") == "message"]
    assert len(msg_outputs) == 1
    text_parts = [p for p in msg_outputs[0]["content"] if p.get("type") == "output_text"]
    assert "72°F and sunny" in text_parts[0]["text"]


# ---------------------------------------------------------------------------
# Sample 5: Conversation History
# ---------------------------------------------------------------------------


def _sample5_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: Any):
    """Conversation history handler: welcome on first turn,
    references previous_response_id on second turn."""

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=request.model)
        yield stream.emit_created()

        msg = stream.add_output_item_message()
        yield msg.emit_added()

        text_content = msg.add_text_content()
        yield text_content.emit_added()

        has_previous = (
            request.previous_response_id is not None
            and str(request.previous_response_id).strip() != ""
        )
        if has_previous:
            reply = f"Following up on {request.previous_response_id}: {get_input_text(request)}"
        else:
            reply = f"Welcome! You said: {get_input_text(request)}"

        yield text_content.emit_delta(reply)
        yield text_content.emit_done()
        yield msg.emit_content_done(text_content)
        yield msg.emit_done()

        yield stream.emit_completed()

    return _events()


def test_sample5_first_turn_welcome() -> None:
    """First turn (no history) returns welcome message."""
    client = _make_app(_sample5_handler)
    resp = _post_json(client, _base_payload("Hi there"))

    body = resp.json()
    assert body["status"] == "completed"
    text_parts = [p for p in body["output"][0]["content"] if p.get("type") == "output_text"]
    assert "Welcome" in text_parts[0]["text"]
    assert "Hi there" in text_parts[0]["text"]


def test_sample5_second_turn_references_history() -> None:
    """Second turn references previous response."""
    client = _make_app(_sample5_handler)

    # First turn
    first_resp = _post_json(client, _base_payload("Hello"))
    first_body = first_resp.json()
    first_id = first_body["id"]

    # Second turn with previous_response_id
    second_payload = _base_payload("Follow up question")
    second_payload["previous_response_id"] = first_id
    second_resp = _post_json(client, second_payload)

    second_body = second_resp.json()
    assert second_body["status"] == "completed"
    text_parts = [p for p in second_body["output"][0]["content"] if p.get("type") == "output_text"]
    text = text_parts[0]["text"]
    assert "Following up on" in text
    assert first_id in text


# ---------------------------------------------------------------------------
# Sample 6: Multi Output — Reasoning + Message
# ---------------------------------------------------------------------------


def _sample6_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: Any):
    """Multi-output handler: emits a reasoning item then a message item."""

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=request.model)
        yield stream.emit_created()

        # Output item 1: reasoning
        reasoning = stream.add_output_item_reasoning_item()
        yield reasoning.emit_added()
        summary = reasoning.add_summary_part()
        yield summary.emit_added()
        yield summary.emit_text_delta("Let me think about this...")
        yield summary.emit_text_done("Let me think about this...")
        reasoning.emit_summary_part_done(summary)
        yield reasoning.emit_done()

        # Output item 2: message
        msg = stream.add_output_item_message()
        yield msg.emit_added()
        text_content = msg.add_text_content()
        yield text_content.emit_added()
        user_text = get_input_text(request)
        yield text_content.emit_delta(f"After reasoning: {user_text}")
        yield text_content.emit_done()
        yield msg.emit_content_done(text_content)
        yield msg.emit_done()

        yield stream.emit_completed()

    return _events()


def test_sample6_streaming_emits_reasoning_and_message() -> None:
    """Streaming response has 2 output_item.added events."""
    client = _make_app(_sample6_handler)
    events = _post_stream(client, _base_payload("complex question"))

    added_events = [e for e in events if e["type"] == "response.output_item.added"]
    assert len(added_events) == 2
    assert added_events[0]["data"]["item"]["type"] == "reasoning"
    assert added_events[1]["data"]["item"]["type"] == "message"


def test_sample6_non_streaming_both_output_items() -> None:
    """Non-streaming returns 2 output items."""
    client = _make_app(_sample6_handler)
    resp = _post_json(client, _base_payload("deep thought"))

    body = resp.json()
    assert body["status"] == "completed"
    output = body["output"]
    assert len(output) == 2
    assert output[0]["type"] == "reasoning"
    assert output[1]["type"] == "message"
    text_parts = [p for p in output[1]["content"] if p.get("type") == "output_text"]
    assert "deep thought" in text_parts[0]["text"]


# ---------------------------------------------------------------------------
# Sample 7: Customization — Default model via options
# ---------------------------------------------------------------------------


def _sample7_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: Any):
    """Handler that reports which model is used."""

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=request.model)
        yield stream.emit_created()

        msg = stream.add_output_item_message()
        yield msg.emit_added()

        text_content = msg.add_text_content()
        yield text_content.emit_added()

        yield text_content.emit_delta(f"[model={request.model}]")
        yield text_content.emit_done()
        yield msg.emit_content_done(text_content)
        yield msg.emit_done()

        yield stream.emit_completed()

    return _events()


def test_sample7_custom_options_applied() -> None:
    """Default model is applied when request omits model."""
    opts = ResponsesServerOptions(
        default_model="gpt-4o",
        sse_keep_alive_interval_seconds=5,
        shutdown_grace_period_seconds=15,
    )
    client = _make_app(_sample7_handler, options=opts)

    # POST without model — server should fill in "gpt-4o" from options
    payload: dict[str, Any] = {"input": "hello", "stream": False}
    resp = _post_json(client, payload)

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "completed"
    text_parts = [p for p in body["output"][0]["content"] if p.get("type") == "output_text"]
    assert "gpt-4o" in text_parts[0]["text"]


def test_sample7_explicit_model_overrides_default() -> None:
    """Explicit model in request overrides default_model."""
    opts = ResponsesServerOptions(default_model="gpt-4o")
    client = _make_app(_sample7_handler, options=opts)

    resp = _post_json(client, _base_payload("hello", model="custom-model"))

    body = resp.json()
    text_parts = [p for p in body["output"][0]["content"] if p.get("type") == "output_text"]
    assert "custom-model" in text_parts[0]["text"]


# ---------------------------------------------------------------------------
# Sample 8: Mixin Composition — Both protocols on one server
# ---------------------------------------------------------------------------


def _sample8_response_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: Any):
    """Responses handler for the mixin test."""

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=request.model)
        yield stream.emit_created()

        msg = stream.add_output_item_message()
        yield msg.emit_added()

        text_content = msg.add_text_content()
        yield text_content.emit_added()

        user_text = get_input_text(request)
        yield text_content.emit_delta(f"[Response] Echo: {user_text}")
        yield text_content.emit_done()
        yield msg.emit_content_done(text_content)
        yield msg.emit_done()

        yield stream.emit_completed()

    return _events()


def test_sample8_mixin_composition_both_protocols() -> None:
    """Both /responses and /invocations endpoints work."""
    invocations = pytest.importorskip(
        "azure.ai.agentserver.invocations",
        reason="azure-ai-agentserver-invocations not installed",
    )
    InvocationAgentServerHost = invocations.InvocationAgentServerHost

    from starlette.requests import Request
    from starlette.responses import JSONResponse, Response

    class MyHost(InvocationAgentServerHost, ResponsesAgentServerHost):
        pass

    host = MyHost()

    @host.invoke_handler
    async def handle_invoke(request: Request) -> Response:
        data = await request.json()
        invocation_id = request.state.invocation_id
        return JSONResponse({
            "invocation_id": invocation_id,
            "status": "completed",
            "output": f"[Invocation] Echo: {data.get('message', '')}",
        })

    host.create_handler(_sample8_response_handler)

    client = TestClient(host)

    # Test invocations endpoint
    inv_resp = client.post("/invocations", json={"message": "Hello invocations"})
    assert inv_resp.status_code == 200
    inv_body = inv_resp.json()
    assert inv_body["status"] == "completed"
    assert "Hello invocations" in inv_body["output"]

    # Test responses endpoint
    resp = client.post(
        "/responses",
        json={"model": "test-model", "input": "Hello responses", "stream": False},
    )
    assert resp.status_code == 200
    resp_body = resp.json()
    assert resp_body["status"] == "completed"
    text_parts = [p for p in resp_body["output"][0]["content"] if p.get("type") == "output_text"]
    assert "Hello responses" in text_parts[0]["text"]


# ---------------------------------------------------------------------------
# Sample 9: Self-Hosting — Mount under /api prefix
# ---------------------------------------------------------------------------


def test_sample9_self_hosted_responses_under_prefix() -> None:
    """Responses endpoints work under /api prefix."""
    from starlette.applications import Starlette
    from starlette.routing import Mount

    responses_app = ResponsesAgentServerHost()

    def _handler(request: CreateResponse, context: ResponseContext, cancellation_signal: Any):
        async def _events():
            stream = ResponseEventStream(response_id=context.response_id, model=request.model)
            yield stream.emit_created()

            msg = stream.add_output_item_message()
            yield msg.emit_added()

            text_content = msg.add_text_content()
            yield text_content.emit_added()

            yield text_content.emit_delta(f"Self-hosted: {get_input_text(request)}")
            yield text_content.emit_done()
            yield msg.emit_content_done(text_content)
            yield msg.emit_done()

            yield stream.emit_completed()

        return _events()

    responses_app.create_handler(_handler)

    parent_app = Starlette(routes=[
        Mount("/api", app=responses_app),
    ])

    client = TestClient(parent_app)
    resp = client.post(
        "/api/responses",
        json={"model": "test-model", "input": "mounted test", "stream": False},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "completed"
    text_parts = [p for p in body["output"][0]["content"] if p.get("type") == "output_text"]
    assert "mounted test" in text_parts[0]["text"]


# ---------------------------------------------------------------------------
# Sample 10: Streaming Upstream — Forward from async generator
# ---------------------------------------------------------------------------


def _sample10_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: Any):
    """Streaming upstream handler: streams tokens from a mock upstream."""

    async def _mock_upstream(prompt: str):
        tokens = ["Upstream says: ", "Hello", ", ", prompt, "!"]
        for token in tokens:
            yield token

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=request.model)
        yield stream.emit_created()

        user_text = get_input_text(request) or "world"
        upstream_tokens = _mock_upstream(user_text)

        async for event in stream.aoutput_item_message(upstream_tokens):
            yield event

        yield stream.emit_completed()

    return _events()


def test_sample10_streaming_upstream_emits_deltas() -> None:
    """Streaming upstream produces delta events."""
    client = _make_app(_sample10_handler)
    events = _post_stream(client, _base_payload("Alice"))

    event_types = [e["type"] for e in events]
    # Verify full lifecycle
    assert "response.created" in event_types
    assert "response.output_item.added" in event_types
    assert "response.output_text.done" in event_types
    assert "response.output_item.done" in event_types
    assert "response.completed" in event_types

    delta_events = [e for e in events if e["type"] == "response.output_text.delta"]
    assert len(delta_events) == 5
    joined = "".join(e["data"]["delta"] for e in delta_events)
    assert "Alice" in joined
    assert "Upstream says" in joined


def test_sample10_streaming_upstream_non_streaming_returns_full_text() -> None:
    """Non-streaming fallback reassembles all deltas."""
    client = _make_app(_sample10_handler)
    resp = _post_json(client, _base_payload("Bob"))

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "completed"
    text_parts = [p for p in body["output"][0]["content"] if p.get("type") == "output_text"]
    assert "Bob" in text_parts[0]["text"]
    assert "Upstream says" in text_parts[0]["text"]


# ---------------------------------------------------------------------------
# Sample 11: Non-Streaming Upstream — Forward complete response
# ---------------------------------------------------------------------------


def _sample11_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: Any):
    """Non-streaming upstream handler: calls mock upstream, emits result."""

    def _mock_upstream_call(prompt: str) -> str:
        return f"Upstream non-streaming reply to: {prompt}"

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=request.model)
        yield stream.emit_created()

        user_text = get_input_text(request) or "world"
        upstream_reply = _mock_upstream_call(user_text)

        for event in stream.output_item_message(upstream_reply):
            yield event

        yield stream.emit_completed()

    return _events()


def test_sample11_non_streaming_upstream_returns_output() -> None:
    """Non-streaming upstream returns completed response."""
    client = _make_app(_sample11_handler)
    resp = _post_json(client, _base_payload("Charlie"))

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "completed"
    output = body["output"]
    assert len(output) == 1
    assert output[0]["type"] == "message"
    text_parts = [p for p in output[0]["content"] if p.get("type") == "output_text"]
    assert "Upstream non-streaming reply to: Charlie" in text_parts[0]["text"]


def test_sample11_non_streaming_upstream_streaming_events() -> None:
    """Streaming mode still emits proper lifecycle events."""
    client = _make_app(_sample11_handler)
    events = _post_stream(client, _base_payload("Dana"))

    event_types = [e["type"] for e in events]
    assert "response.created" in event_types
    assert "response.output_item.added" in event_types
    assert "response.output_text.delta" in event_types
    assert "response.completed" in event_types

    delta_events = [e for e in events if e["type"] == "response.output_text.delta"]
    joined = "".join(e["data"]["delta"] for e in delta_events)
    assert "Dana" in joined
