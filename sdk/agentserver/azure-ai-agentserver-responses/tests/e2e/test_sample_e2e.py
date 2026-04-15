# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""End-to-end tests for Samples 1-16."""

from __future__ import annotations

import asyncio
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
    TextResponse,
)
from azure.ai.agentserver.responses.models import FunctionCallOutputItemParam, ItemMessage
from azure.ai.agentserver.responses.models._generated import StructuredOutputsOutputItem

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


def _sample1_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Echo handler: returns the user's input text using TextResponse."""

    async def _create_text():
        return await context.get_input_text()

    return TextResponse(
        context,
        request,
        text=_create_text,
    )


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


async def _sample2_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Streaming handler: emits text in token-by-token deltas using TextResponse with configure."""
    user_text = await context.get_input_text()
    tokens = user_text.split() if user_text else ["Hello", "World"]

    async def _stream():
        for token in tokens:
            yield token + " "

    return TextResponse(
        context,
        request,
        configure=lambda response: setattr(response, "temperature", 0.7),
        text=_stream(),
    )


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


async def _sample3_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Convenience handler: emits a greeting using output_item_message()."""
    stream = ResponseEventStream(response_id=context.response_id, request=request)

    stream.response.temperature = 0.7
    stream.response.max_output_tokens = 1024

    yield stream.emit_created()
    yield stream.emit_in_progress()

    user_text = await context.get_input_text()
    for event in stream.output_item_message(f"Hello, {user_text}! Welcome."):
        yield event

    yield stream.emit_completed()


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


async def _sample4_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Function-calling handler: uses convenience generators for both turns."""
    items = await context.get_input_items()
    has_fn_output = any(isinstance(item, FunctionCallOutputItemParam) for item in items)

    stream = ResponseEventStream(response_id=context.response_id, request=request)
    yield stream.emit_created()
    yield stream.emit_in_progress()

    if has_fn_output:
        # Second turn: extract function output and echo it as text
        fn_output_text = ""
        for item in items:
            if isinstance(item, FunctionCallOutputItemParam):
                fn_output_text = item.output or ""
                break
        for event in stream.output_item_message(f"The weather is: {fn_output_text}"):
            yield event
    else:
        # First turn: emit a function call for get_weather
        args = json.dumps({"location": await context.get_input_text()})
        for event in stream.output_item_function_call("get_weather", "call_001", args):
            yield event

    yield stream.emit_completed()


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


async def _sample5_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Study tutor handler using TextResponse: welcome on first turn,
    references previous_response_id on second turn."""
    has_previous = request.previous_response_id is not None and str(request.previous_response_id).strip() != ""
    user_text = await context.get_input_text()
    if has_previous:
        text = f"Building on our previous discussion ({request.previous_response_id}): {user_text}"
    else:
        text = f"Welcome! I'm your study tutor. You asked: {user_text}"

    return TextResponse(context, request, text=lambda: text)


def test_sample5_first_turn_welcome() -> None:
    """First turn (no history) returns welcome message."""
    client = _make_app(_sample5_handler)
    resp = _post_json(client, _base_payload("Hi there"))

    body = resp.json()
    assert body["status"] == "completed"
    text_parts = [p for p in body["output"][0]["content"] if p.get("type") == "output_text"]
    assert "Welcome" in text_parts[0]["text"]
    assert "study tutor" in text_parts[0]["text"]
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
    assert "Building on our previous discussion" in text
    assert first_id in text


# ---------------------------------------------------------------------------
# Sample 6: Multi Output — Reasoning + Message
# ---------------------------------------------------------------------------


async def _sample6_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Math solver handler: emits a reasoning item then a message item using convenience generators."""
    stream = ResponseEventStream(response_id=context.response_id, request=request)
    question = await context.get_input_text() or "What is 6 times 7?"

    yield stream.emit_created()
    yield stream.emit_in_progress()

    # Output item 0: reasoning
    thought = f'The user asked: "{question}". I need to compute the result.'
    for event in stream.output_item_reasoning_item(thought):
        yield event

    # Output item 1: message
    for event in stream.output_item_message(f"After reasoning: {question}"):
        yield event

    yield stream.emit_completed()


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


def _sample7_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Handler that reports which model is used, via TextResponse."""
    return TextResponse(
        context,
        request,
        text=lambda: f"[model={request.model}]",
    )


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


def _sample8_response_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Responses handler for the mixin test, via TextResponse."""

    async def _create_text():
        return f"[Response] Echo: {await context.get_input_text()}"

    return TextResponse(
        context,
        request,
        text=_create_text,
    )


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
        return JSONResponse(
            {
                "invocation_id": invocation_id,
                "status": "completed",
                "output": f"[Invocation] Echo: {data.get('message', '')}",
            }
        )

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

    def _handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):

        async def _create_text():
            return f"Self-hosted: {await context.get_input_text()}"

        return TextResponse(
            context,
            request,
            text=_create_text,
        )

    responses_app.create_handler(_handler)

    parent_app = Starlette(
        routes=[
            Mount("/api", app=responses_app),
        ]
    )

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
# Sample 10: Streaming Upstream — Raw events, no ResponseEventStream
# ---------------------------------------------------------------------------


def _sample10_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Streaming upstream handler: yields raw event dicts."""

    async def _mock_upstream_events(prompt: str):
        """Simulate upstream SSE stream events (lifecycle + content)."""
        # Upstream lifecycle — handler will skip these
        yield {"type": "response.created"}
        yield {"type": "response.in_progress"}
        # Upstream content — handler will yield these directly
        yield {
            "type": "response.output_item.added",
            "output_index": 0,
            "item": {"id": "item_up_001", "type": "message", "role": "assistant", "content": []},
        }
        yield {
            "type": "response.content_part.added",
            "output_index": 0,
            "content_index": 0,
            "part": {"type": "output_text", "text": ""},
        }
        tokens = ["Upstream says: ", "Hello", ", ", prompt, "!"]
        for token in tokens:
            yield {"type": "response.output_text.delta", "output_index": 0, "content_index": 0, "delta": token}
        full = "".join(tokens)
        yield {"type": "response.output_text.done", "output_index": 0, "content_index": 0, "text": full}
        yield {
            "type": "response.content_part.done",
            "output_index": 0,
            "content_index": 0,
            "part": {"type": "output_text", "text": full},
        }
        yield {
            "type": "response.output_item.done",
            "output_index": 0,
            "item": {
                "id": "item_up_001",
                "type": "message",
                "role": "assistant",
                "content": [{"type": "output_text", "text": full}],
            },
        }
        yield {"type": "response.completed"}

    async def _events():
        # Build response snapshot by hand — no ResponseEventStream.
        snapshot: dict[str, Any] = {
            "id": context.response_id,
            "object": "response",
            "status": "in_progress",
            "model": request.model or "",
            "output": [],
        }

        # Lifecycle events nest the snapshot under "response"
        # — matching the SSE wire format.
        yield {"type": "response.created", "response": snapshot}
        yield {"type": "response.in_progress", "response": snapshot}

        user_text = await context.get_input_text() or "world"
        output_items: list[dict[str, Any]] = []
        upstream_failed = False

        async for event in _mock_upstream_events(user_text):
            event_type = event["type"]
            if event_type in ("response.created", "response.in_progress"):
                continue
            if event_type == "response.completed":
                break
            if event_type == "response.failed":
                upstream_failed = True
                break

            # Clear upstream response_id on output items.
            if event_type == "response.output_item.added":
                event.get("item", {}).pop("response_id", None)  # type: ignore[union-attr]
            elif event_type == "response.output_item.done":
                item: dict[str, Any] = event.get("item", {})  # type: ignore[assignment]
                item.pop("response_id", None)
                output_items.append(item)

            yield event

        if upstream_failed:
            snapshot["status"] = "failed"
            snapshot["error"] = {"code": "server_error", "message": "Upstream request failed"}
            yield {"type": "response.failed", "response": snapshot}
        else:
            snapshot["status"] = "completed"
            snapshot["output"] = output_items
            yield {"type": "response.completed", "response": snapshot}

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
# Sample 11: Non-Streaming Upstream — Output item builders
# ---------------------------------------------------------------------------


def _sample11_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Non-streaming upstream handler: iterates upstream output items via builders."""

    def _mock_upstream_call(prompt: str) -> list[dict[str, Any]]:
        """Simulate upstream non-streaming response returning output items."""
        return [
            {
                "type": "message",
                "content": [{"type": "output_text", "text": f"Upstream non-streaming reply to: {prompt}"}],
            }
        ]

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, request=request)
        yield stream.emit_created()
        yield stream.emit_in_progress()

        user_text = await context.get_input_text() or "world"
        upstream_items = _mock_upstream_call(user_text)

        for item in upstream_items:
            if item["type"] == "message":
                text = "".join(part["text"] for part in item["content"] if part.get("type") == "output_text")
                for event in stream.output_item_message(text):
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


# ---------------------------------------------------------------------------
# Item Reference Multi-Turn Tests
#
# Validates that item_reference inputs are resolved by the server to their
# concrete Item types before reaching the handler.
# ---------------------------------------------------------------------------


async def _item_ref_echo_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    """Handler that echoes resolved input items as JSON in the response text.

    For each input item, emits its type and (for messages) its text content.
    This lets tests verify that item_references were resolved to concrete items.
    """
    items = await context.get_input_items()
    summaries = []
    for item in items:
        if isinstance(item, ItemMessage):
            texts = []
            for part in getattr(item, "content", None) or []:
                t = getattr(part, "text", None)
                if t:
                    texts.append(t)
            summaries.append({"type": "message", "text": " ".join(texts)})
        else:
            summaries.append({"type": getattr(item, "type", "unknown")})

    return TextResponse(context, request, text=lambda: json.dumps(summaries))


def test_item_reference_turn2_resolves_to_message() -> None:
    """Turn 2 sends an item_reference to Turn 1's output; handler receives a resolved Item."""
    client = _make_app(_item_ref_echo_handler)

    # Turn 1: normal message input
    t1_resp = _post_json(client, _base_payload("Hello from turn 1"))
    assert t1_resp.status_code == 200
    t1_body = t1_resp.json()
    assert t1_body["status"] == "completed"
    # Get the output item ID from turn 1's message output
    t1_output_id = t1_body["output"][0]["id"]
    t1_response_id = t1_body["id"]

    # Turn 2: send an item_reference pointing to the turn-1 output item
    t2_payload = _base_payload(
        [
            {"type": "item_reference", "id": t1_output_id},
            {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "And hello from turn 2"}]},
        ]
    )
    t2_payload["previous_response_id"] = t1_response_id
    t2_resp = _post_json(client, t2_payload)

    assert t2_resp.status_code == 200
    t2_body = t2_resp.json()
    assert t2_body["status"] == "completed"
    # Parse handler's serialised summary from the response text
    text_parts = [p for p in t2_body["output"][0]["content"] if p.get("type") == "output_text"]
    items_json = json.loads(text_parts[0]["text"])

    # First item should be the resolved message from turn 1
    assert items_json[0]["type"] == "message"
    # Second item is the inline message from turn 2
    assert items_json[1]["type"] == "message"
    assert "turn 2" in items_json[1]["text"]


def test_item_reference_get_input_text_includes_resolved() -> None:
    """get_input_text() includes text from resolved item_references."""
    client = _make_app(_item_ref_echo_handler)

    # Turn 1 (unused — establishes context in a different client)
    _post_json(client, _base_payload("Alpha"))

    # Turn 2: handler uses get_input_text which should include resolved text
    async def _text_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
        text = await context.get_input_text()
        return TextResponse(context, request, text=lambda: f"GOT: {text}")

    client2 = _make_app(_text_handler)
    # First create context for turn 1 in client2 too
    t1b = _post_json(client2, _base_payload("Alpha"))
    t1b_body = t1b.json()
    t1b_output_id = t1b_body["output"][0]["id"]
    t1b_response_id = t1b_body["id"]

    t2_payload = _base_payload(
        [
            {"type": "item_reference", "id": t1b_output_id},
            {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "Beta"}]},
        ]
    )
    t2_payload["previous_response_id"] = t1b_response_id
    t2_resp = _post_json(client2, t2_payload)

    t2_body = t2_resp.json()
    text_parts = [p for p in t2_body["output"][0]["content"] if p.get("type") == "output_text"]
    result_text = text_parts[0]["text"]
    assert "GOT:" in result_text
    assert "Beta" in result_text


def test_item_reference_nonexistent_dropped_silently() -> None:
    """An item_reference pointing to a non-existent ID is silently dropped."""
    client = _make_app(_item_ref_echo_handler)

    payload = _base_payload(
        [
            {"type": "item_reference", "id": "item_nonexistent_999"},
            {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "Only me"}]},
        ]
    )
    resp = _post_json(client, payload)

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "completed"
    text_parts = [p for p in body["output"][0]["content"] if p.get("type") == "output_text"]
    items_json = json.loads(text_parts[0]["text"])

    # Only the inline message should remain — the unresolvable reference is dropped
    assert len(items_json) == 1
    assert items_json[0]["type"] == "message"
    assert "Only me" in items_json[0]["text"]


def test_item_reference_three_turn_chain() -> None:
    """Three-turn conversation: each turn references previous output via item_reference."""
    client = _make_app(_item_ref_echo_handler)

    # Turn 1
    t1 = _post_json(client, _base_payload("Turn 1"))
    t1_body = t1.json()
    t1_id = t1_body["id"]
    t1_output_id = t1_body["output"][0]["id"]

    # Turn 2: reference turn-1 output
    t2_payload = _base_payload(
        [
            {"type": "item_reference", "id": t1_output_id},
            {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "Turn 2"}]},
        ]
    )
    t2_payload["previous_response_id"] = t1_id
    t2 = _post_json(client, t2_payload)
    t2_body = t2.json()
    t2_id = t2_body["id"]
    t2_output_id = t2_body["output"][0]["id"]

    # Turn 3: reference turn-2 output
    t3_payload = _base_payload(
        [
            {"type": "item_reference", "id": t2_output_id},
            {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "Turn 3"}]},
        ]
    )
    t3_payload["previous_response_id"] = t2_id
    t3 = _post_json(client, t3_payload)
    t3_body = t3.json()
    assert t3_body["status"] == "completed"

    text_parts = [p for p in t3_body["output"][0]["content"] if p.get("type") == "output_text"]
    items_json = json.loads(text_parts[0]["text"])

    # Should have 2 items: resolved reference from turn 2 + inline turn-3 message
    assert len(items_json) == 2
    assert items_json[0]["type"] == "message"
    assert items_json[1]["type"] == "message"
    assert "Turn 3" in items_json[1]["text"]


def test_item_reference_resolve_references_false() -> None:
    """When resolve_references=False, item_references are passed through as-is."""

    async def _unresolved_handler(
        request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event
    ):
        items = await context.get_input_items(resolve_references=False)
        summaries = []
        for item in items:
            item_type = getattr(item, "type", "unknown")
            summaries.append({"type": item_type})
        return TextResponse(context, request, text=lambda: json.dumps(summaries))

    client = _make_app(_unresolved_handler)

    # Turn 1
    t1 = _post_json(client, _base_payload("Hello"))
    t1_body = t1.json()
    t1_output_id = t1_body["output"][0]["id"]
    t1_id = t1_body["id"]

    # Turn 2 with resolve_references=False in handler
    t2_payload = _base_payload(
        [
            {"type": "item_reference", "id": t1_output_id},
            {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "test"}]},
        ]
    )
    t2_payload["previous_response_id"] = t1_id
    t2 = _post_json(client, t2_payload)
    t2_body = t2.json()

    text_parts = [p for p in t2_body["output"][0]["content"] if p.get("type") == "output_text"]
    items_json = json.loads(text_parts[0]["text"])

    # First item should remain as item_reference (not resolved)
    assert items_json[0]["type"] == "item_reference"
    # Second is the inline message
    assert items_json[1]["type"] == "message"


def test_item_reference_input_items_endpoint() -> None:
    """The GET /responses/{id}/input_items endpoint returns resolved items."""
    client = _make_app(_item_ref_echo_handler)

    # Turn 1
    t1 = _post_json(client, _base_payload("Stored text"))
    t1_body = t1.json()
    t1_output_id = t1_body["output"][0]["id"]
    t1_id = t1_body["id"]

    # Turn 2 with item_reference
    t2_payload = _base_payload(
        [
            {"type": "item_reference", "id": t1_output_id},
            {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "New input"}]},
        ]
    )
    t2_payload["previous_response_id"] = t1_id
    t2 = _post_json(client, t2_payload)
    t2_body = t2.json()
    t2_id = t2_body["id"]

    # GET input_items for turn 2
    input_items_resp = client.get(f"/responses/{t2_id}/input_items")
    assert input_items_resp.status_code == 200
    input_items_body = input_items_resp.json()

    # Should contain resolved items (not raw item_references)
    items = input_items_body.get("data", [])
    assert len(items) >= 1
    # None of the items should be type "item_reference" — they should all be resolved
    for item in items:
        assert item.get("type") != "item_reference", f"Expected resolved item, got item_reference: {item}"


# ===========================================================================
# Sample 12 — Image Generation
# ===========================================================================


TINY_IMAGE_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGP4z8BQDwAEgAF/pooBPQAAAABJRU5ErkJggg=="


async def _image_gen_convenience_handler(
    request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event
):
    stream = ResponseEventStream(response_id=context.response_id, request=request)
    yield stream.emit_created()
    yield stream.emit_in_progress()
    async for event in stream.aoutput_item_image_gen_call(TINY_IMAGE_B64):
        yield event
    yield stream.emit_completed()


def _image_gen_streaming_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    stream = ResponseEventStream(response_id=context.response_id, request=request)
    yield stream.emit_created()
    yield stream.emit_in_progress()
    ig = stream.add_output_item_image_gen_call()
    yield ig.emit_added()
    yield ig.emit_in_progress()
    yield ig.emit_generating()
    for i in range(2):
        yield ig.emit_partial_image(f"partial_{i}")
    yield ig.emit_completed()
    yield ig.emit_done(TINY_IMAGE_B64)
    yield stream.emit_completed()


def test_sample12_image_gen_convenience_emits_lifecycle() -> None:
    """Image gen convenience emits the full lifecycle with result in done."""
    events = _post_stream(_make_app(_image_gen_convenience_handler), _base_payload())
    types = [e["type"] for e in events]
    assert "response.output_item.added" in types
    assert "response.image_generation_call.in_progress" in types
    assert "response.image_generation_call.generating" in types
    assert "response.image_generation_call.completed" in types
    assert "response.output_item.done" in types
    assert "response.completed" in types
    # The done event should carry the result
    done_events = [e for e in events if e["type"] == "response.output_item.done"]
    assert done_events
    assert done_events[0]["data"]["item"]["result"] == TINY_IMAGE_B64


def test_sample12_image_gen_streaming_partials() -> None:
    """Image gen streaming handler emits partial_image events."""
    events = _post_stream(_make_app(_image_gen_streaming_handler), _base_payload())
    partial_events = [e for e in events if e["type"] == "response.image_generation_call.partial_image"]
    assert len(partial_events) == 2
    assert partial_events[0]["data"]["partial_image_b64"] == "partial_0"
    assert partial_events[1]["data"]["partial_image_b64"] == "partial_1"


def test_sample12_image_gen_non_streaming_returns_result() -> None:
    """Non-streaming mode returns the image result in the output."""
    resp = _post_json(_make_app(_image_gen_convenience_handler), _base_payload())
    body = resp.json()
    assert resp.status_code == 200
    assert body["output"][0]["type"] == "image_generation_call"
    assert body["output"][0]["result"] == TINY_IMAGE_B64


# ===========================================================================
# Sample 13 — Image Input
# ===========================================================================


async def _image_url_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    from azure.ai.agentserver.responses._data_url import is_data_url
    from azure.ai.agentserver.responses.models import MessageContentInputImageContent

    items = await context.get_input_items()
    images = []
    for item in items:
        if not isinstance(item, ItemMessage):
            continue
        for content in item.content or []:
            if isinstance(content, MessageContentInputImageContent):
                images.append(content)
    urls = [img.image_url for img in images if img.image_url and not is_data_url(img.image_url)]
    return TextResponse(context, request, text=f"URLs: {', '.join(urls)}")


async def _image_base64_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    from azure.ai.agentserver.responses._data_url import get_media_type, is_data_url, try_decode_bytes
    from azure.ai.agentserver.responses.models import MessageContentInputImageContent

    items = await context.get_input_items()
    images = []
    for item in items:
        if not isinstance(item, ItemMessage):
            continue
        for content in item.content or []:
            if isinstance(content, MessageContentInputImageContent):
                images.append(content)
    results = []
    for img in images:
        if img.image_url and is_data_url(img.image_url):
            raw = try_decode_bytes(img.image_url)
            media = get_media_type(img.image_url)
            results.append(f"{media} ({len(raw)} bytes)")
    return TextResponse(context, request, text=f"Decoded: {'; '.join(results)}")


async def _image_file_id_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    from azure.ai.agentserver.responses.models import MessageContentInputImageContent

    items = await context.get_input_items()
    images = []
    for item in items:
        if not isinstance(item, ItemMessage):
            continue
        for content in item.content or []:
            if isinstance(content, MessageContentInputImageContent):
                images.append(content)
    file_ids = [img.file_id for img in images if img.file_id]
    return TextResponse(context, request, text=f"File IDs: {', '.join(file_ids)}")


def _image_input_payload(content_list):
    return _base_payload(
        [{"role": "user", "content": content_list}],
    )


def test_sample13_image_input_url_handler() -> None:
    """URL image input handler echoes back the URL."""
    payload = _image_input_payload(
        [{"type": "input_image", "image_url": "https://example.com/photo.png", "detail": "auto"}]
    )
    resp = _post_json(_make_app(_image_url_handler), payload)
    body = resp.json()
    text = body["output"][0]["content"][0]["text"]
    assert "https://example.com/photo.png" in text


def test_sample13_image_input_base64_handler() -> None:
    """Base64 image input handler decodes and reports media type + size."""
    import base64

    raw_bytes = b"fake-image-data"
    data_url = f"data:image/png;base64,{base64.b64encode(raw_bytes).decode()}"
    payload = _image_input_payload([{"type": "input_image", "image_url": data_url, "detail": "auto"}])
    resp = _post_json(_make_app(_image_base64_handler), payload)
    body = resp.json()
    text = body["output"][0]["content"][0]["text"]
    assert "image/png" in text
    assert f"{len(raw_bytes)} bytes" in text


def test_sample13_image_input_file_id_handler() -> None:
    """File ID image input handler echoes back the file_id."""
    payload = _image_input_payload([{"type": "input_image", "file_id": "/images/photo.png", "detail": "auto"}])
    resp = _post_json(_make_app(_image_file_id_handler), payload)
    body = resp.json()
    text = body["output"][0]["content"][0]["text"]
    assert "/images/photo.png" in text


# ===========================================================================
# Sample 14 — File Inputs
# ===========================================================================


async def _file_base64_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    from azure.ai.agentserver.responses._data_url import get_media_type, is_data_url, try_decode_bytes
    from azure.ai.agentserver.responses.models import ItemMessage, MessageContentInputFileContent

    items = await context.get_input_items()
    files = []
    for item in items:
        if not isinstance(item, ItemMessage):
            continue
        for content in item.content or []:
            if isinstance(content, MessageContentInputFileContent):
                files.append(content)
    results = []
    for f in files:
        if f.file_data and is_data_url(f.file_data):
            raw = try_decode_bytes(f.file_data)
            media = get_media_type(f.file_data)
            results.append(f"{media} ({len(raw)} bytes)")
    return TextResponse(context, request, text=f"Decoded: {'; '.join(results)}")


async def _file_url_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    from azure.ai.agentserver.responses.models import ItemMessage, MessageContentInputFileContent

    items = await context.get_input_items()
    files = []
    for item in items:
        if not isinstance(item, ItemMessage):
            continue
        for content in item.content or []:
            if isinstance(content, MessageContentInputFileContent):
                files.append(content)
    urls = [f.file_url for f in files if f.file_url]
    return TextResponse(context, request, text=f"URLs: {', '.join(urls)}")


async def _file_id_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    from azure.ai.agentserver.responses.models import ItemMessage, MessageContentInputFileContent

    items = await context.get_input_items()
    files = []
    for item in items:
        if not isinstance(item, ItemMessage):
            continue
        for content in item.content or []:
            if isinstance(content, MessageContentInputFileContent):
                files.append(content)
    file_ids = [f.file_id for f in files if f.file_id]
    return TextResponse(context, request, text=f"File IDs: {', '.join(file_ids)}")


def _file_input_payload(content_list):
    return _base_payload(
        [{"role": "user", "content": content_list}],
    )


def test_sample14_file_input_base64_handler() -> None:
    """Base64 file input handler decodes and reports media type + size."""
    import base64

    raw_bytes = b"%PDF-1.4 fake pdf content"
    data_url = f"data:application/pdf;base64,{base64.b64encode(raw_bytes).decode()}"
    payload = _file_input_payload([{"type": "input_file", "file_data": data_url}])
    resp = _post_json(_make_app(_file_base64_handler), payload)
    body = resp.json()
    text = body["output"][0]["content"][0]["text"]
    assert "application/pdf" in text
    assert f"{len(raw_bytes)} bytes" in text


def test_sample14_file_input_url_handler() -> None:
    """File URL handler echoes back the URL."""
    payload = _file_input_payload([{"type": "input_file", "file_url": "https://example.com/report.pdf"}])
    resp = _post_json(_make_app(_file_url_handler), payload)
    body = resp.json()
    text = body["output"][0]["content"][0]["text"]
    assert "https://example.com/report.pdf" in text


def test_sample14_file_input_file_id_handler() -> None:
    """File ID handler echoes back the file_id."""
    payload = _file_input_payload([{"type": "input_file", "file_id": "/reports/summary.pdf"}])
    resp = _post_json(_make_app(_file_id_handler), payload)
    body = resp.json()
    text = body["output"][0]["content"][0]["text"]
    assert "/reports/summary.pdf" in text


# ===========================================================================
# Sample 15 — Annotations
# ===========================================================================


async def _annotations_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
    from azure.ai.agentserver.responses.models import FileCitationBody, FilePath, UrlCitationBody

    stream = ResponseEventStream(response_id=context.response_id, request=request)
    yield stream.emit_created()
    yield stream.emit_in_progress()
    annotations = [
        FilePath(file_id="/reports/summary.pdf", index=0),
        FileCitationBody(file_id="/sources/paper.pdf", index=1, filename="paper.pdf"),
        UrlCitationBody(url="https://example.com/guide", start_index=0, end_index=10, title="Guide"),
    ]
    async for event in stream.aoutput_item_message("Here are your sources.", annotations=annotations):
        yield event
    yield stream.emit_completed()


def test_sample15_annotations_emitted() -> None:
    """Streaming mode emits annotation.added events for each annotation."""
    events = _post_stream(_make_app(_annotations_handler), _base_payload())
    ann_events = [e for e in events if e["type"] == "response.output_text.annotation.added"]
    assert len(ann_events) == 3
    # Check annotation types
    assert ann_events[0]["data"]["annotation"]["type"] == "file_path"
    assert ann_events[1]["data"]["annotation"]["type"] == "file_citation"
    assert ann_events[2]["data"]["annotation"]["type"] == "url_citation"
    # Check annotation indices are sequential
    assert ann_events[0]["data"]["annotation_index"] == 0
    assert ann_events[1]["data"]["annotation_index"] == 1
    assert ann_events[2]["data"]["annotation_index"] == 2


def test_sample15_non_streaming_annotations_in_output() -> None:
    """Non-streaming mode returns the text message with annotations tracked."""
    resp = _post_json(_make_app(_annotations_handler), _base_payload())
    body = resp.json()
    assert resp.status_code == 200
    assert body["output"][0]["type"] == "message"
    text_content = body["output"][0]["content"][0]
    assert text_content["text"] == "Here are your sources."


# ===========================================================================
# Sample 16 — Structured Outputs
# ===========================================================================


async def _structured_convenience_handler(
    request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event
):
    stream = ResponseEventStream(response_id=context.response_id, request=request)
    yield stream.emit_created()
    yield stream.emit_in_progress()
    async for event in stream.aoutput_item_structured_outputs({"sentiment": "positive", "confidence": 0.95}):
        yield event
    yield stream.emit_completed()


def _structured_full_control_handler(
    request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event
):
    stream = ResponseEventStream(response_id=context.response_id, request=request)
    yield stream.emit_created()
    yield stream.emit_in_progress()
    builder = stream.add_output_item_structured_outputs()
    item = StructuredOutputsOutputItem(id=builder.item_id, output={"status": "ok"})
    yield builder.emit_added(item)
    yield builder.emit_done(item)
    yield stream.emit_completed()


def test_sample16_structured_outputs_convenience() -> None:
    """Convenience method emits structured_outputs item with correct data."""
    events = _post_stream(_make_app(_structured_convenience_handler), _base_payload())
    types = [e["type"] for e in events]
    assert "response.output_item.added" in types
    assert "response.output_item.done" in types
    done_events = [e for e in events if e["type"] == "response.output_item.done"]
    item = done_events[0]["data"]["item"]
    assert item["type"] == "structured_outputs"
    assert item["output"]["sentiment"] == "positive"
    assert item["output"]["confidence"] == 0.95


def test_sample16_structured_outputs_non_streaming() -> None:
    """Non-streaming mode returns the structured output in response body."""
    resp = _post_json(_make_app(_structured_convenience_handler), _base_payload())
    body = resp.json()
    assert resp.status_code == 200
    assert body["output"][0]["type"] == "structured_outputs"
    assert body["output"][0]["output"]["sentiment"] == "positive"


def test_sample16_structured_outputs_full_control() -> None:
    """Full-control builder emits correct structured_outputs lifecycle."""
    events = _post_stream(_make_app(_structured_full_control_handler), _base_payload())
    done_events = [e for e in events if e["type"] == "response.output_item.done"]
    assert done_events
    item = done_events[0]["data"]["item"]
    assert item["type"] == "structured_outputs"
    assert item["output"]["status"] == "ok"
