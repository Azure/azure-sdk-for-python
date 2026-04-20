# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""End-to-end proxy tests for OpenAI-compatible upstream forwarding.

Architecture:

    Test client ──▶ Server A (proxy handler via openai SDK) ──▶ Server B (backend)

Server B is a ResponsesAgentServerHost with handlers that emit rich SSE
streams (multi-output, failed, text-only).  Server A is a proxy that uses
the ``openai`` Python SDK to call Server B via ``httpx.ASGITransport``.
Tests verify the full round-trip including streaming, non-streaming,
multi-output, failure propagation, and response-ID independence.
"""

from __future__ import annotations

import json
from typing import Any

import httpx
import openai
from starlette.testclient import TestClient

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
)

# ---------------------------------------------------------------------------
# SSE helpers (same pattern as test_sample_e2e.py)
# ---------------------------------------------------------------------------


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


def _post_stream(client: TestClient, payload: dict[str, Any]) -> list[dict[str, Any]]:
    payload["stream"] = True
    with client.stream("POST", "/responses", json=payload) as resp:
        assert resp.status_code == 200
        events = _collect_stream_events(resp)
    return events


def _base_payload(input_text: str = "hello", **overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": "test-model",
        "input": [
            {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": input_text}],
            }
        ],
    }
    payload.update(overrides)
    return payload


# ---------------------------------------------------------------------------
# Server B handlers (backend that emits rich SSE streams)
# ---------------------------------------------------------------------------


def _emit_text_only_handler(text: str):
    """Return a handler that emits a single text message."""

    def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: Any):
        async def _events():
            stream = ResponseEventStream(response_id=context.response_id, model=request.model)
            yield stream.emit_created()
            yield stream.emit_in_progress()

            msg = stream.add_output_item_message()
            yield msg.emit_added()
            tc = msg.add_text_content()
            yield tc.emit_added()
            yield tc.emit_delta(text)
            yield tc.emit_text_done(text)
            yield tc.emit_done()
            yield msg.emit_done()
            yield stream.emit_completed()

        return _events()

    return handler


def _emit_multi_output_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: Any):
    """Emit 3 output items: reasoning + function_call + text message."""

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=request.model)
        yield stream.emit_created()
        yield stream.emit_in_progress()

        # 1. Reasoning item
        reasoning = stream.add_output_item_reasoning_item()
        yield reasoning.emit_added()
        sp = reasoning.add_summary_part()
        yield sp.emit_added()
        yield sp.emit_text_delta("Thinking about")
        yield sp.emit_text_delta(" the answer...")
        yield sp.emit_text_done("Thinking about the answer...")
        yield sp.emit_done()
        yield reasoning.emit_done()

        # 2. Function call
        fc = stream.add_output_item_function_call("get_weather", "call_proxy_001")
        yield fc.emit_added()
        yield fc.emit_arguments_delta('{"city":')
        yield fc.emit_arguments_delta('"Seattle"}')
        yield fc.emit_arguments_done('{"city":"Seattle"}')
        yield fc.emit_done()

        # 3. Text message
        msg = stream.add_output_item_message()
        yield msg.emit_added()
        tc = msg.add_text_content()
        yield tc.emit_added()
        yield tc.emit_delta("The answer")
        yield tc.emit_delta(" is 42.")
        yield tc.emit_text_done("The answer is 42.")
        yield tc.emit_done()
        yield msg.emit_done()

        yield stream.emit_completed()

    return _events()


def _emit_failed_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: Any):
    """Emit created, in_progress, then failed."""

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=request.model)
        yield stream.emit_created()
        yield stream.emit_in_progress()
        yield stream.emit_failed(code="server_error", message="Backend processing error")

    return _events()


# ---------------------------------------------------------------------------
# Server A handler (proxy using openai SDK → Server B)
# ---------------------------------------------------------------------------


def _make_streaming_proxy_handler(upstream_client: openai.AsyncOpenAI):
    """Create a streaming proxy handler that forwards to upstream via openai SDK."""

    def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: Any):
        async def _events():
            stream = ResponseEventStream(response_id=context.response_id, model=request.model)
            yield stream.emit_created()
            yield stream.emit_in_progress()

            msg = stream.add_output_item_message()
            yield msg.emit_added()
            tc = msg.add_text_content()
            yield tc.emit_added()

            user_text = await context.get_input_text() or "hello"
            full_text: list[str] = []

            async with await upstream_client.responses.create(
                model=request.model or "gpt-4o-mini",
                input=user_text,
                stream=True,
            ) as upstream_stream:
                async for event in upstream_stream:
                    if event.type == "response.output_text.delta":
                        full_text.append(event.delta)
                        yield tc.emit_delta(event.delta)

            result_text = "".join(full_text)
            yield tc.emit_text_done(result_text)
            yield tc.emit_done()
            yield msg.emit_done()
            yield stream.emit_completed()

        return _events()

    return handler


def _make_non_streaming_proxy_handler(upstream_client: openai.AsyncOpenAI):
    """Create a non-streaming proxy handler that forwards to upstream via openai SDK."""

    def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: Any):
        async def _events():
            user_text = await context.get_input_text() or "hello"

            result = await upstream_client.responses.create(
                model=request.model or "gpt-4o-mini",
                input=user_text,
            )

            # Extract output text
            output_text = ""
            for item in result.output:
                if item.type == "message":
                    for part in item.content:
                        if part.type == "output_text":
                            output_text += part.text

            stream = ResponseEventStream(response_id=context.response_id, model=request.model)
            yield stream.emit_created()
            yield stream.emit_in_progress()

            for event in stream.output_item_message(output_text):
                yield event

            yield stream.emit_completed()

        return _events()

    return handler


def _make_upstream_integration_handler(upstream_client: openai.AsyncOpenAI):
    """Create an upstream integration handler (mirrors Sample 10).

    Owns the response lifecycle, translates upstream content events, and
    stamps its own response ID on all events.  Skips upstream lifecycle events
    (created, in_progress) and handles completed/failed from upstream.
    """

    def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: Any):
        async def _events():
            stream = ResponseEventStream(response_id=context.response_id, model=request.model)
            yield stream.emit_created()
            yield stream.emit_in_progress()

            user_text = await context.get_input_text() or "hello"
            upstream_failed = False

            # Track builders by output_index for multi-output
            reasoning_builder = None
            reasoning_sp = None
            fc_builder = None
            msg_builder = None
            text_builder = None

            async with await upstream_client.responses.create(
                model=request.model or "gpt-4o-mini",
                input=user_text,
                stream=True,
            ) as upstream_stream:
                async for event in upstream_stream:
                    event_type = event.type

                    # Skip upstream lifecycle events
                    if event_type in ("response.created", "response.in_progress"):
                        continue
                    if event_type == "response.completed":
                        break
                    if event_type == "response.failed":
                        upstream_failed = True
                        break

                    # Reasoning item events
                    if event_type == "response.output_item.added":
                        item = event.item
                        if item.type == "reasoning":
                            reasoning_builder = stream.add_output_item_reasoning_item()
                            yield reasoning_builder.emit_added()
                        elif item.type == "function_call":
                            fc_builder = stream.add_output_item_function_call(item.name, item.call_id)
                            yield fc_builder.emit_added()
                        elif item.type == "message":
                            msg_builder = stream.add_output_item_message()
                            yield msg_builder.emit_added()

                    elif event_type == "response.reasoning_summary_part.added":
                        if reasoning_builder is not None:
                            reasoning_sp = reasoning_builder.add_summary_part()
                            yield reasoning_sp.emit_added()

                    elif event_type == "response.reasoning_summary_text.delta":
                        if reasoning_sp is not None:
                            yield reasoning_sp.emit_text_delta(event.delta)

                    elif event_type == "response.reasoning_summary_text.done":
                        if reasoning_sp is not None:
                            yield reasoning_sp.emit_text_done(event.text)

                    elif event_type == "response.reasoning_summary_part.done":
                        if reasoning_sp is not None:
                            yield reasoning_sp.emit_done()

                    elif event_type == "response.output_item.done":
                        item = event.item
                        if item.type == "reasoning" and reasoning_builder is not None:
                            yield reasoning_builder.emit_done()
                        elif item.type == "function_call" and fc_builder is not None:
                            yield fc_builder.emit_done()
                        elif item.type == "message" and msg_builder is not None:
                            yield msg_builder.emit_done()

                    elif event_type == "response.function_call_arguments.delta":
                        if fc_builder is not None:
                            yield fc_builder.emit_arguments_delta(event.delta)

                    elif event_type == "response.function_call_arguments.done":
                        if fc_builder is not None:
                            yield fc_builder.emit_arguments_done(event.arguments)

                    elif event_type == "response.content_part.added":
                        if msg_builder is not None:
                            text_builder = msg_builder.add_text_content()
                            yield text_builder.emit_added()

                    elif event_type == "response.output_text.delta":
                        if text_builder is not None:
                            yield text_builder.emit_delta(event.delta)

                    elif event_type == "response.output_text.done":
                        if text_builder is not None:
                            yield text_builder.emit_text_done(event.text)

                    elif event_type == "response.content_part.done":
                        if text_builder is not None:
                            yield text_builder.emit_done()

            if upstream_failed:
                yield stream.emit_failed(code="server_error", message="Upstream request failed")
            else:
                yield stream.emit_completed()

        return _events()

    return handler


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------


def _create_server_b(handler) -> ResponsesAgentServerHost:
    """Create Server B with the given handler."""
    app = ResponsesAgentServerHost()
    app.response_handler(handler)
    return app


def _create_openai_client_for_app(app: ResponsesAgentServerHost) -> openai.AsyncOpenAI:
    """Create an openai.AsyncOpenAI client that routes to an in-process ASGI app."""
    transport = httpx.ASGITransport(app=app)
    http_client = httpx.AsyncClient(transport=transport, base_url="http://server-b")
    return openai.AsyncOpenAI(
        base_url="http://server-b/",
        api_key="unused",
        http_client=http_client,
    )


def _create_server_a(upstream_client: openai.AsyncOpenAI, handler_factory) -> ResponsesAgentServerHost:
    """Create Server A (proxy) with the given handler factory."""
    app = ResponsesAgentServerHost()
    app.response_handler(handler_factory(upstream_client))
    return app


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestStreamingProxy:
    """Streaming proxy: Server A forwards streaming events from Server B."""

    def test_streaming_proxy_full_roundtrip(self) -> None:
        """Server B streams 'Hello, World!' → proxy → client gets text."""
        server_b = _create_server_b(_emit_text_only_handler("Hello, World!"))
        upstream_client = _create_openai_client_for_app(server_b)
        server_a = _create_server_a(upstream_client, _make_streaming_proxy_handler)
        client = TestClient(server_a)

        events = _post_stream(client, _base_payload("Say hello"))

        event_types = [e["type"] for e in events]
        assert "response.created" in event_types
        assert "response.output_item.added" in event_types
        assert "response.completed" in event_types

        delta_events = [e for e in events if e["type"] == "response.output_text.delta"]
        full_text = "".join(e["data"]["delta"] for e in delta_events)
        assert full_text == "Hello, World!"

    def test_streaming_proxy_preserves_model(self) -> None:
        """Server A preserves the model from the request."""
        server_b = _create_server_b(_emit_text_only_handler("test"))
        upstream_client = _create_openai_client_for_app(server_b)
        server_a = _create_server_a(upstream_client, _make_streaming_proxy_handler)
        client = TestClient(server_a)

        events = _post_stream(client, _base_payload("test", model="my-custom-model"))

        completed = [e for e in events if e["type"] == "response.completed"]
        assert len(completed) == 1
        response_obj = completed[0]["data"]["response"]
        assert response_obj["model"] == "my-custom-model"


class TestNonStreamingProxy:
    """Non-streaming proxy: Server A calls Server B, returns JSON."""

    def test_non_streaming_proxy_full_roundtrip(self) -> None:
        """Non-streaming: completed JSON response with text."""
        server_b = _create_server_b(_emit_text_only_handler("Hello, World!"))
        upstream_client = _create_openai_client_for_app(server_b)
        server_a = _create_server_a(upstream_client, _make_non_streaming_proxy_handler)
        client = TestClient(server_a)

        resp = client.post("/responses", json=_base_payload("Say hello"))
        assert resp.status_code == 200
        body = resp.json()

        assert body["status"] == "completed"
        assert body["model"] == "test-model"
        output = body["output"]
        assert len(output) >= 1
        text_parts = [p for p in output[0]["content"] if p.get("type") == "output_text"]
        assert text_parts[0]["text"] == "Hello, World!"


class TestUpstreamIntegration:
    """Upstream integration: openai SDK → Server A → Server B (rich backend)."""

    def test_upstream_multi_output_all_roundtrip(self) -> None:
        """3 output items (reasoning + function_call + message) arrive at client."""
        server_b = _create_server_b(_emit_multi_output_handler)
        upstream_client = _create_openai_client_for_app(server_b)
        server_a = _create_server_a(upstream_client, _make_upstream_integration_handler)
        client = TestClient(server_a)

        resp = client.post("/responses", json=_base_payload("What's the weather?"))
        assert resp.status_code == 200
        body = resp.json()

        assert body["status"] == "completed"
        output = body["output"]
        assert len(output) == 3

        # Reasoning item
        assert output[0]["type"] == "reasoning"

        # Function call
        assert output[1]["type"] == "function_call"
        assert output[1]["name"] == "get_weather"
        assert output[1]["call_id"] == "call_proxy_001"
        assert json.loads(output[1]["arguments"]) == {"city": "Seattle"}

        # Text message
        assert output[2]["type"] == "message"
        text_parts = [p for p in output[2]["content"] if p.get("type") == "output_text"]
        assert text_parts[0]["text"] == "The answer is 42."

    def test_upstream_multi_output_streaming_all_roundtrip(self) -> None:
        """Streaming: all deltas from 3 output types arrive."""
        server_b = _create_server_b(_emit_multi_output_handler)
        upstream_client = _create_openai_client_for_app(server_b)
        server_a = _create_server_a(upstream_client, _make_upstream_integration_handler)
        client = TestClient(server_a)

        events = _post_stream(client, _base_payload("What's the weather?"))
        event_types = [e["type"] for e in events]

        # 3 output_item.added (reasoning, function_call, message)
        added_events = [e for e in events if e["type"] == "response.output_item.added"]
        assert len(added_events) == 3

        # 3 output_item.done
        done_events = [e for e in events if e["type"] == "response.output_item.done"]
        assert len(done_events) == 3

        # Reasoning summary deltas
        reasoning_deltas = [e for e in events if e["type"] == "response.reasoning_summary_text.delta"]
        assert len(reasoning_deltas) > 0

        # Function call argument deltas
        arg_deltas = [e for e in events if e["type"] == "response.function_call_arguments.delta"]
        assert len(arg_deltas) > 0

        # Text deltas
        text_deltas = [e for e in events if e["type"] == "response.output_text.delta"]
        full_text = "".join(e["data"]["delta"] for e in text_deltas)
        assert full_text == "The answer is 42."

        # Terminal
        assert "response.completed" in event_types

    def test_upstream_failed_propagates_failure(self) -> None:
        """Server B fails → client sees response.failed."""
        server_b = _create_server_b(_emit_failed_handler)
        upstream_client = _create_openai_client_for_app(server_b)
        server_a = _create_server_a(upstream_client, _make_upstream_integration_handler)
        client = TestClient(server_a)

        events = _post_stream(client, _base_payload("trigger failure"))
        event_types = [e["type"] for e in events]

        assert "response.failed" in event_types
        failed_event = next(e for e in events if e["type"] == "response.failed")
        response_obj = failed_event["data"]["response"]
        assert response_obj["status"] == "failed"

        # Should not have response.completed
        assert "response.completed" not in event_types

    def test_upstream_response_ids_are_independent(self) -> None:
        """Server A stamps its own response ID, not Server B's."""
        server_b = _create_server_b(_emit_multi_output_handler)
        upstream_client = _create_openai_client_for_app(server_b)
        server_a = _create_server_a(upstream_client, _make_upstream_integration_handler)
        client = TestClient(server_a)

        events = _post_stream(client, _base_payload("test"))

        # response.created carries Server A's response ID
        created_event = next(e for e in events if e["type"] == "response.created")
        server_a_id = created_event["data"]["response"]["id"]
        assert server_a_id
        assert server_a_id.startswith("caresp_")

        # response.completed should carry the same ID
        completed_event = next(e for e in events if e["type"] == "response.completed")
        completed_id = completed_event["data"]["response"]["id"]
        assert completed_id == server_a_id
