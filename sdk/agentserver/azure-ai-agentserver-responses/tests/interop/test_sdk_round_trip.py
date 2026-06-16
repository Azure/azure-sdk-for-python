# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""OpenAI Python SDK round-trip tests.

These tests verify end-to-end compatibility between the **openai** Python SDK
and our Responses API server.  Each test:

1. Creates a ``ResponsesAgentServerHost`` with a specific handler
2. Uses ``starlette.testclient.TestClient`` (an ``httpx.Client`` subclass)
   as the ``http_client`` for ``openai.OpenAI``
3. Calls ``client.responses.create()`` through the SDK
4. Asserts the SDK-parsed ``Response`` object matches expectations

This is the Python equivalent of the SDK round-trip test suite.

When a test fails, FIX THE SERVICE — do not change the test.
"""

from __future__ import annotations

from typing import Any

import pytest
from starlette.testclient import TestClient

openai = pytest.importorskip("openai", reason="openai SDK required for round-trip tests")

from openai.types.responses import (  # noqa: E402
    ResponseCodeInterpreterToolCall,
    ResponseFileSearchToolCall,
    ResponseFunctionToolCall,
    ResponseOutputMessage,
    ResponseOutputText,
    ResponseReasoningItem,
)
from openai.types.responses.response_output_item import (  # noqa: E402
    ImageGenerationCall,
    McpCall,
    McpListTools,
)

from azure.ai.agentserver.responses import (  # noqa: E402
    ResponseEventStream,
    ResponsesAgentServerHost,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_captured: dict[str, Any] = {}


def _make_sdk_client(handler) -> openai.OpenAI:
    """Build an OpenAI SDK client backed by our ASGI test server.

    ``TestClient`` (an ``httpx.Client`` subclass) is passed as
    ``http_client`` so all traffic goes through the ASGI app — no real
    network calls are made.
    """
    app = ResponsesAgentServerHost()
    app.response_handler(handler)
    tc = TestClient(app)
    return openai.OpenAI(
        api_key="test-key",
        base_url="http://testserver",
        http_client=tc,
    )


def _capturing(handler):
    """Wrap *handler* so the parsed ``CreateResponse`` is captured."""
    _captured.clear()

    def wrapper(request, context, cancellation_signal):
        _captured["request"] = request
        _captured["context"] = context
        return handler(request, context, cancellation_signal)

    return wrapper


# ---------------------------------------------------------------------------
# Handler factories
# ---------------------------------------------------------------------------
# Each factory returns a handler that emits specific output item(s).
# Handlers follow the (request, context, cancellation_signal) -> AsyncIterator
# signature required by ResponsesAgentServerHost.


def _text_message_handler(text: str = "Hello, world!"):
    def handler(request, context, cancellation_signal):
        async def events():
            s = ResponseEventStream(response_id=context.response_id, model=request.model)
            yield s.emit_created()
            for ev in s.output_item_message(text):
                yield ev
            yield s.emit_completed()

        return events()

    return handler


def _function_call_handler(
    name: str = "get_weather",
    call_id: str = "call_abc123",
    arguments: str = '{"location":"Seattle"}',
):
    def handler(request, context, cancellation_signal):
        async def events():
            s = ResponseEventStream(response_id=context.response_id, model=request.model)
            yield s.emit_created()
            for ev in s.output_item_function_call(name, call_id, arguments):
                yield ev
            yield s.emit_completed()

        return events()

    return handler


def _function_call_output_handler(
    call_id: str = "call_abc123",
    output: str = "72°F and sunny",
):
    def handler(request, context, cancellation_signal):
        async def events():
            s = ResponseEventStream(response_id=context.response_id, model=request.model)
            yield s.emit_created()
            for ev in s.output_item_function_call_output(call_id, output):
                yield ev
            yield s.emit_completed()

        return events()

    return handler


def _reasoning_handler(summary: str = "Let me think step by step..."):
    def handler(request, context, cancellation_signal):
        async def events():
            s = ResponseEventStream(response_id=context.response_id, model=request.model)
            yield s.emit_created()
            for ev in s.output_item_reasoning_item(summary):
                yield ev
            yield s.emit_completed()

        return events()

    return handler


def _file_search_handler():
    def handler(request, context, cancellation_signal):
        async def events():
            s = ResponseEventStream(response_id=context.response_id, model=request.model)
            yield s.emit_created()
            b = s.add_output_item_file_search_call()
            yield b.emit_added()
            yield b.emit_in_progress()
            yield b.emit_searching()
            yield b.emit_completed()
            yield b.emit_done()
            yield s.emit_completed()

        return events()

    return handler


def _web_search_handler():
    """Emit a web_search_call with a valid ``action`` payload.

    The OpenAI SDK requires ``action`` to be a discriminated union member
    (``ActionSearch``, etc.) so we use the low-level builder and override
    the item to include a valid search action.
    """

    def handler(request, context, cancellation_signal):
        async def events():
            s = ResponseEventStream(response_id=context.response_id, model=request.model)
            yield s.emit_created()
            b = s.add_output_item_web_search_call()
            # Override the added item to include a valid action.
            added = b.emit_added()
            item = added.get("item", {})
            item["action"] = {"type": "search", "query": "test query"}
            yield added
            yield b.emit_searching()
            yield b.emit_completed()
            done = b.emit_done()
            done_item = done.get("item", {})
            done_item["action"] = {"type": "search", "query": "test query"}
            yield done
            yield s.emit_completed()

        return events()

    return handler


def _code_interpreter_handler(code: str = "print('hello')"):
    def handler(request, context, cancellation_signal):
        async def events():
            s = ResponseEventStream(response_id=context.response_id, model=request.model)
            yield s.emit_created()
            b = s.add_output_item_code_interpreter_call()
            yield b.emit_added()
            for ev in b.code(code):
                yield ev
            yield b.emit_completed()
            yield b.emit_done()
            yield s.emit_completed()

        return events()

    return handler


def _image_gen_handler():
    def handler(request, context, cancellation_signal):
        async def events():
            s = ResponseEventStream(response_id=context.response_id, model=request.model)
            yield s.emit_created()
            b = s.add_output_item_image_gen_call()
            yield b.emit_added()
            yield b.emit_generating()
            yield b.emit_completed()
            yield b.emit_done("")
            yield s.emit_completed()

        return events()

    return handler


def _mcp_call_handler(
    server_label: str = "my-server",
    name: str = "search_docs",
):
    def handler(request, context, cancellation_signal):
        async def events():
            s = ResponseEventStream(response_id=context.response_id, model=request.model)
            yield s.emit_created()
            b = s.add_output_item_mcp_call(server_label, name)
            yield b.emit_added()
            for ev in b.arguments('{"query": "test"}'):
                yield ev
            yield b.emit_completed()
            yield b.emit_done()
            yield s.emit_completed()

        return events()

    return handler


def _mcp_list_tools_handler(server_label: str = "my-server"):
    def handler(request, context, cancellation_signal):
        async def events():
            s = ResponseEventStream(response_id=context.response_id, model=request.model)
            yield s.emit_created()
            b = s.add_output_item_mcp_list_tools(server_label)
            yield b.emit_added()
            yield b.emit_completed()
            yield b.emit_done()
            yield s.emit_completed()

        return events()

    return handler


def _multiple_items_handler():
    """Emit a message, a function call, and a reasoning item."""

    def handler(request, context, cancellation_signal):
        async def events():
            s = ResponseEventStream(response_id=context.response_id, model=request.model)
            yield s.emit_created()
            for ev in s.output_item_message("Here is the result."):
                yield ev
            for ev in s.output_item_function_call("lookup", "call_multi", '{"id": 42}'):
                yield ev
            for ev in s.output_item_reasoning_item("Analyzing the data..."):
                yield ev
            yield s.emit_completed()

        return events()

    return handler


# ---------------------------------------------------------------------------
# Non-streaming round-trip tests — text message
# ---------------------------------------------------------------------------


class TestEmitTextMessage:
    """SDK parses a single text message response."""

    def test_basic_text(self):
        client = _make_sdk_client(_text_message_handler("Hello, world!"))
        resp = client.responses.create(model="test-model", input="hi")

        assert resp.status == "completed"
        assert resp.model == "test-model"
        assert resp.object == "response"
        assert len(resp.output) == 1

        msg = resp.output[0]
        assert isinstance(msg, ResponseOutputMessage)
        assert msg.type == "message"
        assert msg.role == "assistant"
        assert len(msg.content) == 1

        text = msg.content[0]
        assert isinstance(text, ResponseOutputText)
        assert text.type == "output_text"
        assert text.text == "Hello, world!"

    def test_empty_text(self):
        client = _make_sdk_client(_text_message_handler(""))
        resp = client.responses.create(model="test", input="hi")
        msg = resp.output[0]
        assert isinstance(msg, ResponseOutputMessage)
        assert msg.content[0].text == ""

    def test_long_text(self):
        long = "x" * 10_000
        client = _make_sdk_client(_text_message_handler(long))
        resp = client.responses.create(model="test", input="hi")
        assert resp.output[0].content[0].text == long

    def test_unicode_text(self):
        text = "Hello 🌍! café. 日本語テスト"
        client = _make_sdk_client(_text_message_handler(text))
        resp = client.responses.create(model="test", input="hi")
        assert resp.output[0].content[0].text == text


# ---------------------------------------------------------------------------
# Non-streaming round-trip tests — function call
# ---------------------------------------------------------------------------


class TestEmitFunctionCall:
    """SDK parses a function tool call response."""

    def test_basic_function_call(self):
        client = _make_sdk_client(_function_call_handler("get_weather", "call_123", '{"city":"NYC"}'))
        resp = client.responses.create(model="test", input="weather?")

        assert resp.status == "completed"
        assert len(resp.output) == 1

        fc = resp.output[0]
        assert isinstance(fc, ResponseFunctionToolCall)
        assert fc.type == "function_call"
        assert fc.name == "get_weather"
        assert fc.call_id == "call_123"
        assert fc.arguments == '{"city":"NYC"}'

    def test_empty_arguments(self):
        client = _make_sdk_client(_function_call_handler("ping", "call_empty", ""))
        resp = client.responses.create(model="test", input="ping")
        fc = resp.output[0]
        assert isinstance(fc, ResponseFunctionToolCall)
        assert fc.arguments == ""


# ---------------------------------------------------------------------------
# Non-streaming round-trip tests — function call output
# ---------------------------------------------------------------------------


class TestEmitFunctionCallOutput:
    """SDK parses a function_call_output item."""

    def test_basic_output(self):
        client = _make_sdk_client(_function_call_output_handler("call_abc", "72°F"))
        resp = client.responses.create(model="test", input="hi")

        assert resp.status == "completed"
        assert len(resp.output) == 1

        item = resp.output[0]
        # OpenAI SDK may deserialize as ResponseOutputMessage fallback;
        # check attributes directly for wire-level compliance.
        assert item.type == "function_call_output"
        assert item.call_id == "call_abc"
        assert item.output == "72°F"


# ---------------------------------------------------------------------------
# Non-streaming round-trip tests — reasoning
# ---------------------------------------------------------------------------


class TestEmitReasoning:
    """SDK parses a reasoning item response."""

    def test_basic_reasoning(self):
        client = _make_sdk_client(_reasoning_handler("Step 1: Analyze the problem."))
        resp = client.responses.create(model="test", input="think")

        assert resp.status == "completed"
        assert len(resp.output) == 1

        item = resp.output[0]
        assert isinstance(item, ResponseReasoningItem)
        assert item.type == "reasoning"
        assert len(item.summary) == 1
        assert item.summary[0].text == "Step 1: Analyze the problem."


# ---------------------------------------------------------------------------
# Non-streaming round-trip tests — file search call
# ---------------------------------------------------------------------------


class TestEmitFileSearchCall:
    """SDK parses a file_search_call item."""

    def test_basic_file_search(self):
        client = _make_sdk_client(_file_search_handler())
        resp = client.responses.create(model="test", input="search files")

        assert resp.status == "completed"
        assert len(resp.output) == 1

        item = resp.output[0]
        assert isinstance(item, ResponseFileSearchToolCall)
        assert item.type == "file_search_call"
        assert item.status == "completed"


# ---------------------------------------------------------------------------
# Non-streaming round-trip tests — web search call
# ---------------------------------------------------------------------------


class TestEmitWebSearchCall:
    """SDK parses a web_search_call item.

    The web search builder needs a valid ``action`` dict
    (e.g. ``{"type": "search", "query": "..."}``).
    """

    def test_basic_web_search(self):
        client = _make_sdk_client(_web_search_handler())
        resp = client.responses.create(model="test", input="search web")

        assert resp.status == "completed"
        assert len(resp.output) == 1

        item = resp.output[0]
        assert item.type == "web_search_call"
        assert item.status == "completed"


# ---------------------------------------------------------------------------
# Non-streaming round-trip tests — code interpreter call
# ---------------------------------------------------------------------------


class TestEmitCodeInterpreterCall:
    """SDK parses a code_interpreter_call item."""

    def test_basic_code_interpreter(self):
        client = _make_sdk_client(_code_interpreter_handler("print('hi')"))
        resp = client.responses.create(model="test", input="run code")

        assert resp.status == "completed"
        assert len(resp.output) == 1

        item = resp.output[0]
        assert isinstance(item, ResponseCodeInterpreterToolCall)
        assert item.type == "code_interpreter_call"
        assert item.code == "print('hi')"
        assert item.status == "completed"


# ---------------------------------------------------------------------------
# Non-streaming round-trip tests — image generation call
# ---------------------------------------------------------------------------


class TestEmitImageGenCall:
    """SDK parses an image_generation_call item."""

    def test_basic_image_gen(self):
        client = _make_sdk_client(_image_gen_handler())
        resp = client.responses.create(model="test", input="draw cat")

        assert resp.status == "completed"
        assert len(resp.output) == 1

        item = resp.output[0]
        assert isinstance(item, ImageGenerationCall)
        assert item.type == "image_generation_call"
        assert item.status == "completed"


# ---------------------------------------------------------------------------
# Non-streaming round-trip tests — MCP call
# ---------------------------------------------------------------------------


class TestEmitMcpCall:
    """SDK parses an mcp_call item."""

    def test_basic_mcp_call(self):
        client = _make_sdk_client(_mcp_call_handler("tool-server", "do_stuff"))
        resp = client.responses.create(model="test", input="mcp")

        assert resp.status == "completed"
        assert len(resp.output) == 1

        item = resp.output[0]
        assert isinstance(item, McpCall)
        assert item.type == "mcp_call"
        assert item.name == "do_stuff"
        assert item.server_label == "tool-server"


# ---------------------------------------------------------------------------
# Non-streaming round-trip tests — MCP list tools
# ---------------------------------------------------------------------------


class TestEmitMcpListTools:
    """SDK parses an mcp_list_tools item."""

    def test_basic_list_tools(self):
        client = _make_sdk_client(_mcp_list_tools_handler("tool-server"))
        resp = client.responses.create(model="test", input="list")

        assert resp.status == "completed"
        assert len(resp.output) == 1

        item = resp.output[0]
        assert isinstance(item, McpListTools)
        assert item.type == "mcp_list_tools"
        assert item.server_label == "tool-server"


# ---------------------------------------------------------------------------
# Non-streaming round-trip tests — multiple items
# ---------------------------------------------------------------------------


class TestEmitMultipleItems:
    """SDK parses a response with multiple output item types."""

    def test_message_function_call_reasoning(self):
        client = _make_sdk_client(_multiple_items_handler())
        resp = client.responses.create(model="test", input="multi")

        assert resp.status == "completed"
        assert len(resp.output) == 3

        # 1. text message
        msg = resp.output[0]
        assert isinstance(msg, ResponseOutputMessage)
        assert msg.content[0].text == "Here is the result."

        # 2. function call
        fc = resp.output[1]
        assert isinstance(fc, ResponseFunctionToolCall)
        assert fc.name == "lookup"
        assert fc.call_id == "call_multi"

        # 3. reasoning
        reason = resp.output[2]
        assert isinstance(reason, ResponseReasoningItem)
        assert len(reason.summary) == 1


# ---------------------------------------------------------------------------
# Response properties tests
# ---------------------------------------------------------------------------


class TestResponseProperties:
    """Verify standard Response properties are populated."""

    def test_response_id_present(self):
        client = _make_sdk_client(_text_message_handler())
        resp = client.responses.create(model="test", input="hi")
        assert resp.id is not None
        assert len(resp.id) > 0

    def test_model_preserved(self):
        client = _make_sdk_client(_text_message_handler())
        resp = client.responses.create(model="my-custom-model", input="hi")
        assert resp.model == "my-custom-model"

    def test_object_type(self):
        client = _make_sdk_client(_text_message_handler())
        resp = client.responses.create(model="test", input="hi")
        assert resp.object == "response"

    def test_created_at_present(self):
        client = _make_sdk_client(_text_message_handler())
        resp = client.responses.create(model="test", input="hi")
        assert resp.created_at is not None

    def test_completed_status(self):
        client = _make_sdk_client(_text_message_handler())
        resp = client.responses.create(model="test", input="hi")
        assert resp.status == "completed"


# ---------------------------------------------------------------------------
# Input round-trip tests
# ---------------------------------------------------------------------------


class TestInputRoundTrip:
    """Verify that SDK-built requests are correctly parsed by the server."""

    def test_string_input(self):
        handler = _text_message_handler()
        client = _make_sdk_client(_capturing(handler))
        client.responses.create(model="test", input="Hello, server!")

        req = _captured["request"]
        assert req is not None

    def test_message_input(self):
        handler = _text_message_handler()
        client = _make_sdk_client(_capturing(handler))
        client.responses.create(
            model="test",
            input=[{"role": "user", "content": "What is 2+2?"}],
        )
        req = _captured["request"]
        assert req is not None

    def test_multi_turn_input(self):
        handler = _text_message_handler()
        client = _make_sdk_client(_capturing(handler))
        client.responses.create(
            model="test",
            input=[
                {"role": "user", "content": "Hi"},
                {"role": "assistant", "content": "Hello!"},
                {"role": "user", "content": "How are you?"},
            ],
        )
        req = _captured["request"]
        assert req is not None

    def test_model_in_request(self):
        handler = _text_message_handler()
        client = _make_sdk_client(_capturing(handler))
        client.responses.create(model="gpt-4o", input="hi")
        assert _captured["request"].model == "gpt-4o"

    def test_instructions_in_request(self):
        handler = _text_message_handler()
        client = _make_sdk_client(_capturing(handler))
        client.responses.create(model="test", input="hi", instructions="Be helpful")
        assert _captured["request"].instructions == "Be helpful"

    def test_temperature_in_request(self):
        handler = _text_message_handler()
        client = _make_sdk_client(_capturing(handler))
        client.responses.create(model="test", input="hi", temperature=0.7)
        assert _captured["request"].temperature == pytest.approx(0.7)

    def test_tools_in_request(self):
        handler = _text_message_handler()
        client = _make_sdk_client(_capturing(handler))
        client.responses.create(
            model="test",
            input="hi",
            tools=[
                {
                    "type": "function",
                    "name": "get_weather",
                    "parameters": {
                        "type": "object",
                        "properties": {"city": {"type": "string"}},
                    },
                }
            ],
        )
        req = _captured["request"]
        assert req.tools is not None
        assert len(req.tools) >= 1

    def test_max_output_tokens_in_request(self):
        handler = _text_message_handler()
        client = _make_sdk_client(_capturing(handler))
        client.responses.create(
            model="test",
            input="hi",
            max_output_tokens=1024,
        )
        assert _captured["request"].max_output_tokens == 1024


# ---------------------------------------------------------------------------
# Streaming round-trip tests
# ---------------------------------------------------------------------------


class TestStreamingRoundTrip:
    """Verify SDK streaming integration.

    Streaming through OpenAI SDK + TestClient exercises the full SSE
    pipeline: server emits events → TestClient → httpx → OpenAI SDK parser.
    """

    def test_stream_text_message(self):
        """Stream yields events and the final response has the expected text."""
        handler = _text_message_handler("Streamed text")
        app = ResponsesAgentServerHost()
        app.response_handler(handler)
        tc = TestClient(app)
        client = openai.OpenAI(
            api_key="test-key",
            base_url="http://testserver",
            http_client=tc,
        )

        events_seen: list[str] = []
        with client.responses.create(
            model="test",
            input="hi",
            stream=True,
        ) as stream:
            for event in stream:
                events_seen.append(event.type)

        # Expect lifecycle events including created, output_item, and completed.
        assert "response.created" in events_seen
        assert "response.completed" in events_seen
        assert any("output_text" in t for t in events_seen)

    def test_stream_function_call(self):
        """Stream a function call and verify argument events."""
        handler = _function_call_handler("my_func", "call_s1", '{"x": 1}')
        app = ResponsesAgentServerHost()
        app.response_handler(handler)
        tc = TestClient(app)
        client = openai.OpenAI(
            api_key="test-key",
            base_url="http://testserver",
            http_client=tc,
        )

        events_seen: list[str] = []
        with client.responses.create(
            model="test",
            input="do it",
            stream=True,
        ) as stream:
            for event in stream:
                events_seen.append(event.type)

        assert "response.created" in events_seen
        assert "response.completed" in events_seen
        assert any("function_call_arguments" in t for t in events_seen)

    def test_stream_multiple_items(self):
        """Stream a mix of output items."""
        handler = _multiple_items_handler()
        app = ResponsesAgentServerHost()
        app.response_handler(handler)
        tc = TestClient(app)
        client = openai.OpenAI(
            api_key="test-key",
            base_url="http://testserver",
            http_client=tc,
        )

        events_seen: list[str] = []
        with client.responses.create(
            model="test",
            input="all",
            stream=True,
        ) as stream:
            for event in stream:
                events_seen.append(event.type)

        # Should see events for message, function call, and reasoning.
        assert "response.output_item.added" in events_seen
        assert "response.completed" in events_seen
        # Multiple output_item.added events (one per item)
        added_count = events_seen.count("response.output_item.added")
        assert added_count == 3, f"expected 3 output_item.added, got {added_count}"
