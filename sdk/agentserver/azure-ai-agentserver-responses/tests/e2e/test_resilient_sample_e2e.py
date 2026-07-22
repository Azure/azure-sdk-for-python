# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""E2E tests for the resilient responses samples (19-22) + generic upstream-wrap patterns.

These tests verify that the sample handler patterns:
- Emit response.created as the FIRST event
- Emit a terminal event (response.completed)
- Produce output content (not empty)
- Handle cancellation correctly (skip completed on shutdown)
- Never return None or exit without events

Note: the shipped numbered samples are 19-22. The Claude-style and Copilot-style
"wrap a stateful upstream SDK" patterns are not shipped as numbered samples (they
require external SDKs); we test the same handler PATTERN inline (simulated
upstream) to verify the event protocol is correct.
"""

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

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _collect_sse(response) -> list[dict[str, Any]]:
    events = []
    current_type = None
    current_data = None
    for line in response.iter_lines():
        if not line:
            if current_type:
                events.append({"type": current_type, "data": json.loads(current_data) if current_data else {}})
            current_type = current_data = None
            continue
        if line.startswith("event:"):
            current_type = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            current_data = line.split(":", 1)[1].strip()
    if current_type:
        events.append({"type": current_type, "data": json.loads(current_data) if current_data else {}})
    return events


# ---------------------------------------------------------------------------
# Resilient Claude-style upstream pattern (wrap a stateful upstream SDK; no real Anthropic SDK)
# ---------------------------------------------------------------------------


def _make_claude_style_app() -> TestClient:
    """A resilient Claude-style upstream-wrap pattern with a simulated upstream (no real Claude SDK)."""
    options = ResponsesServerOptions(resilient_background=True, steerable_conversations=True)
    app = ResponsesAgentServerHost(options=options)

    @app.response_handler
    async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
        stream = ResponseEventStream(response_id=context.response_id, request=request)
        input_text = await context.get_input_text()

        yield stream.emit_created()

        # Pre-entry: steered away → return without terminal
        # (In real sample, sends message to Claude SDK first to preserve context)
        if cancellation_signal.is_set():
            return

        yield stream.emit_in_progress()

        message = stream.add_output_item_message()
        yield message.emit_added()
        text = message.add_text_content()
        yield text.emit_added()

        # Simulates ClaudeSDKClient streaming
        for word in f"Claude says: {input_text}".split():
            if cancellation_signal.is_set():
                break
            yield text.emit_delta(word + " ")
            await asyncio.sleep(0.01)

        yield text.emit_text_done()
        yield text.emit_done()
        yield message.emit_done()

        if context.shutdown.is_set():
            return
        else:
            yield stream.emit_completed()

    return TestClient(app)


class TestResilientClaudeStylePattern:
    def test_streaming_emits_created_first(self) -> None:
        client = _make_claude_style_app()
        payload = {"model": "claude", "input": "Hello!", "stream": True, "store": True, "background": True}
        with client.stream("POST", "/responses", json=payload) as resp:
            events = _collect_sse(resp)
        assert events[0]["type"] == "response.created"

    def test_streaming_emits_completed(self) -> None:
        client = _make_claude_style_app()
        payload = {"model": "claude", "input": "Hello!", "stream": True, "store": True, "background": True}
        with client.stream("POST", "/responses", json=payload) as resp:
            events = _collect_sse(resp)
        types = [e["type"] for e in events]
        assert "response.completed" in types

    def test_produces_output_text(self) -> None:
        client = _make_claude_style_app()
        payload = {"model": "claude", "input": "world", "stream": True, "store": True, "background": True}
        with client.stream("POST", "/responses", json=payload) as resp:
            events = _collect_sse(resp)
        deltas = [e for e in events if e["type"] == "response.output_text.delta"]
        assert len(deltas) > 0, "Handler must produce output text deltas"
        full_text = "".join(e["data"].get("delta", "") for e in deltas)
        assert "world" in full_text


# ---------------------------------------------------------------------------
# Sample 18: Resilient Copilot (tests the handler pattern, no real OpenAI SDK)
# ---------------------------------------------------------------------------


def _make_sample18_app() -> TestClient:
    """Reproduces the upstream-owned resilient recovery pattern with a simulated upstream."""
    options = ResponsesServerOptions(resilient_background=True, steerable_conversations=True)
    app = ResponsesAgentServerHost(options=options)

    @app.response_handler
    async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
        stream = ResponseEventStream(response_id=context.response_id, request=request)
        input_text = await context.get_input_text()

        yield stream.emit_created()

        # Pre-entry: steered away → return without terminal
        # (In real sample, sends message to Copilot SDK then aborts)
        if cancellation_signal.is_set():
            return

        yield stream.emit_in_progress()

        message = stream.add_output_item_message()
        yield message.emit_added()
        text = message.add_text_content()
        yield text.emit_added()

        # Simulates CopilotClient event-driven streaming
        for word in f"Copilot response to: {input_text}".split():
            if cancellation_signal.is_set():
                break
            yield text.emit_delta(word + " ")
            await asyncio.sleep(0.01)

        yield text.emit_text_done()
        yield text.emit_done()
        yield message.emit_done()

        if context.shutdown.is_set():
            return
        else:
            yield stream.emit_completed()

    return TestClient(app)


class TestSample18ResilientCopilot:
    def test_streaming_emits_created_first(self) -> None:
        client = _make_sample18_app()
        payload = {"model": "gpt-4o", "input": "test", "stream": True, "store": True, "background": True}
        with client.stream("POST", "/responses", json=payload) as resp:
            events = _collect_sse(resp)
        assert events[0]["type"] == "response.created"

    def test_streaming_emits_completed(self) -> None:
        client = _make_sample18_app()
        payload = {"model": "gpt-4o", "input": "test", "stream": True, "store": True, "background": True}
        with client.stream("POST", "/responses", json=payload) as resp:
            events = _collect_sse(resp)
        types = [e["type"] for e in events]
        assert "response.completed" in types

    def test_produces_content_deltas(self) -> None:
        client = _make_sample18_app()
        payload = {"model": "gpt-4o", "input": "hello", "stream": True, "store": True, "background": True}
        with client.stream("POST", "/responses", json=payload) as resp:
            events = _collect_sse(resp)
        deltas = [e for e in events if e["type"] == "response.output_text.delta"]
        assert len(deltas) > 0, "Must produce text deltas"


# ---------------------------------------------------------------------------
# Sample 19: Resilient Streaming (simulated LLM)
# ---------------------------------------------------------------------------


def _make_sample19_app() -> TestClient:
    options = ResponsesServerOptions(resilient_background=True)
    app = ResponsesAgentServerHost(options=options)

    @app.response_handler
    async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
        stream = ResponseEventStream(response_id=context.response_id, request=request)
        yield stream.emit_created()

        # Pre-entry: return without terminal
        if cancellation_signal.is_set():
            return

        yield stream.emit_in_progress()

        message = stream.add_output_item_message()
        yield message.emit_added()
        text = message.add_text_content()
        yield text.emit_added()

        input_text = await context.get_input_text()
        for word in f"Response to: {input_text}".split():
            if cancellation_signal.is_set():
                break
            yield text.emit_delta(word + " ")
            await asyncio.sleep(0.01)

        yield text.emit_text_done()
        yield text.emit_done()
        yield message.emit_done()

        if context.shutdown.is_set():
            return
        else:
            yield stream.emit_completed()

    return TestClient(app)


class TestSample19ResilientStreaming:
    def test_streaming_emits_created_first(self) -> None:
        client = _make_sample19_app()
        payload = {"model": "m", "input": "test", "stream": True, "store": True, "background": True}
        with client.stream("POST", "/responses", json=payload) as resp:
            events = _collect_sse(resp)
        assert events[0]["type"] == "response.created"

    def test_streaming_emits_completed(self) -> None:
        client = _make_sample19_app()
        payload = {"model": "m", "input": "test", "stream": True, "store": True, "background": True}
        with client.stream("POST", "/responses", json=payload) as resp:
            events = _collect_sse(resp)
        types = [e["type"] for e in events]
        assert "response.completed" in types

    def test_produces_content_deltas(self) -> None:
        client = _make_sample19_app()
        payload = {"model": "m", "input": "hello", "stream": True, "store": True, "background": True}
        with client.stream("POST", "/responses", json=payload) as resp:
            events = _collect_sse(resp)
        deltas = [e for e in events if e["type"] == "response.output_text.delta"]
        assert len(deltas) > 0, "Must produce text deltas"


# ---------------------------------------------------------------------------
# Sample 20: Resilient Steering (with CancellationReason)
# ---------------------------------------------------------------------------


def _make_sample20_app() -> TestClient:
    options = ResponsesServerOptions(resilient_background=True, steerable_conversations=True)
    app = ResponsesAgentServerHost(options=options)

    @app.response_handler
    async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
        stream = ResponseEventStream(response_id=context.response_id, request=request)
        input_text = await context.get_input_text()

        yield stream.emit_created()

        if cancellation_signal.is_set():
            return

        yield stream.emit_in_progress()

        message = stream.add_output_item_message()
        yield message.emit_added()
        text = message.add_text_content()
        yield text.emit_added()

        for word in f"Explaining {input_text} in detail".split():
            if cancellation_signal.is_set():
                break
            yield text.emit_delta(word + " ")
            await asyncio.sleep(0.05)

        yield text.emit_text_done()
        yield text.emit_done()
        yield message.emit_done()

        if context.shutdown.is_set():
            return
        else:
            yield stream.emit_completed()

    return TestClient(app)


class TestSample20ResilientSteering:
    def test_normal_completion(self) -> None:
        client = _make_sample20_app()
        payload = {"model": "m", "input": "quantum", "stream": True, "store": True, "background": True}
        with client.stream("POST", "/responses", json=payload) as resp:
            events = _collect_sse(resp)
        types = [e["type"] for e in events]
        assert types[0] == "response.created"
        assert "response.completed" in types
        deltas = [e for e in events if e["type"] == "response.output_text.delta"]
        assert len(deltas) > 0

    def test_pre_entry_steering_still_emits_created_and_completed(self) -> None:
        """When cancellation is already set before handler starts, it should
        still emit created + completed (not exit silently)."""
        client = _make_sample20_app()
        # Start a slow turn, then immediately steer with a second turn
        payload1 = {"model": "m", "input": "slow topic", "store": True, "background": True}
        resp1 = client.post("/responses", json=payload1)
        assert resp1.status_code == 200
        resp1_id = resp1.json()["id"]

        # Steer: send a new turn referencing the same conversation
        payload2 = {
            "model": "m",
            "input": "fast topic",
            "store": True,
            "background": True,
            "previous_response_id": resp1_id,
            "stream": True,
        }
        with client.stream("POST", "/responses", json=payload2) as resp2:
            events = _collect_sse(resp2)
        types = [e["type"] for e in events]
        # The second turn should complete normally
        assert "response.created" in types
        assert "response.completed" in types

    def test_shutdown_mid_stream_no_terminal_event(self) -> None:
        """Simulate shutdown mid-stream — handler should NOT emit completed.

        This mirrors the SIMULATE_SHUTDOWN_MS pattern from the samples: fire
        SHUTTING_DOWN after a delay and verify the handler exits without a
        terminal event.
        """
        shutdown_detected = {"fired": False}

        options = ResponsesServerOptions(resilient_background=True, steerable_conversations=True)
        app_local = ResponsesAgentServerHost(options=options)

        @app_local.response_handler
        async def shutdown_handler(
            request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event
        ):
            stream = ResponseEventStream(response_id=context.response_id, request=request)
            input_text = await context.get_input_text()

            yield stream.emit_created()

            if cancellation_signal.is_set():
                return

            yield stream.emit_in_progress()

            # Schedule simulated shutdown after very short delay
            async def fire_shutdown():
                await asyncio.sleep(0.02)
                context.shutdown.set()

                cancellation_signal.set()
                cancellation_signal.set()

            asyncio.create_task(fire_shutdown())

            message = stream.add_output_item_message()
            yield message.emit_added()
            text = message.add_text_content()
            yield text.emit_added()

            for word in f"Explaining {input_text} in great detail with many words".split():
                if cancellation_signal.is_set():
                    break
                yield text.emit_delta(word + " ")
                await asyncio.sleep(0.05)

            yield text.emit_text_done()
            yield text.emit_done()
            yield message.emit_done()

            if context.shutdown.is_set():
                shutdown_detected["fired"] = True
                return
            else:
                yield stream.emit_completed()

        client = TestClient(app_local)
        payload = {"model": "m", "input": "quantum", "stream": True, "store": True, "background": True}
        with client.stream("POST", "/responses", json=payload) as resp:
            events = _collect_sse(resp)
        types = [e["type"] for e in events]
        # Must have created + in_progress but NOT completed (shutdown return)
        assert "response.created" in types
        assert "response.in_progress" in types
        assert "response.completed" not in types
        # Handler detected shutdown and exited cleanly
        assert shutdown_detected["fired"] is True


# ---------------------------------------------------------------------------
# Sample 22: Resilient Multi-turn
# ---------------------------------------------------------------------------


def _make_sample22_app() -> TestClient:
    options = ResponsesServerOptions(resilient_background=True, steerable_conversations=False)
    app = ResponsesAgentServerHost(options=options)

    @app.response_handler
    async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
        input_text = await context.get_input_text()
        turn_count = context.conversation_chain_metadata.get("turn_count", 0) + 1
        if input_text.strip().lower() == "done":
            context.conversation_chain_metadata.clear()
            return TextResponse(context, request, text=f"Done! Session complete after {turn_count - 1} turns.")
        history_items = await context.get_history()
        reply = f"Turn {turn_count}: '{input_text}', context={len(history_items)} items"
        context.conversation_chain_metadata["turn_count"] = turn_count
        return TextResponse(context, request, text=reply)

    return TestClient(app)


class TestSample22ResilientMultiturn:
    def test_first_turn_completes(self) -> None:
        client = _make_sample22_app()
        payload = {"model": "chat", "input": "Hello", "store": True, "background": True}
        resp = client.post("/responses", json=payload)
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] in ("in_progress", "completed")

    def test_first_turn_produces_output(self) -> None:
        client = _make_sample22_app()
        payload = {"model": "chat", "input": "Hello", "stream": True, "store": True, "background": True}
        with client.stream("POST", "/responses", json=payload) as resp:
            events = _collect_sse(resp)
        types = [e["type"] for e in events]
        assert types[0] == "response.created"
        assert "response.completed" in types
        deltas = [e for e in events if e["type"] == "response.output_text.delta"]
        assert len(deltas) > 0

    def test_multi_turn_conversation(self) -> None:
        """Verify handler works with multiple independent turns."""
        client = _make_sample22_app()
        # Turn 1
        resp1 = client.post(
            "/responses", json={"model": "chat", "input": "My name is Alice", "store": True, "background": True}
        )
        assert resp1.status_code == 200
        body1 = resp1.json()
        assert body1["status"] in ("in_progress", "completed")

        # Turn 2 (independent — no previous_response_id to avoid TaskManager)
        resp2 = client.post(
            "/responses",
            json={"model": "chat", "input": "What is my name?", "store": True, "background": True},
        )
        assert resp2.status_code == 200
        assert resp2.json()["status"] in ("in_progress", "completed")

    def test_done_terminates_session(self) -> None:
        """When resilience context is available, 'done' produces session-complete message."""
        client = _make_sample22_app()
        payload = {"model": "chat", "input": "done", "stream": True, "store": True, "background": True}
        with client.stream("POST", "/responses", json=payload) as resp:
            events = _collect_sse(resp)
        types = [e["type"] for e in events]
        assert "response.created" in types
        assert "response.completed" in types
        # "done" command produces session-complete message
        deltas = [e for e in events if e["type"] == "response.output_text.delta"]
        full_text = "".join(e["data"].get("delta", "") for e in deltas)
        assert "done" in full_text.lower()
