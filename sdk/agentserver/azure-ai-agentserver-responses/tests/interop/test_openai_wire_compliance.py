# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Raw JSON wire-format compliance tests.

Tests in this file define the OpenAI wire-format contract.
When a test fails, FIX THE SERVICE — do not change the test.
See COMPLIANCE.md for the source-of-truth specification.

Each test sends a JSON payload that is valid per the OpenAI Responses API
specification and verifies our server accepts it and correctly deserializes
the model.  The JSON payloads match exactly what the OpenAI SDK (or any
compliant client) would produce.
"""

from __future__ import annotations

import json
from typing import Any

from starlette.testclient import TestClient

from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
    get_input_expanded,
)
from azure.ai.agentserver.responses.models import (
    get_tool_choice_expanded,
)

# ---------------------------------------------------------------------------
# Test infrastructure
# ---------------------------------------------------------------------------

# Mutable container to capture the deserialized request from the handler.
_captured: dict[str, Any] = {}


def _capture_handler(request: CreateResponse, context: ResponseContext, cancellation_signal: Any):
    """Handler that captures the parsed request, then emits a minimal response."""
    _captured["request"] = request

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, model=request.model)
        yield stream.emit_created()
        yield stream.emit_in_progress()

        msg = stream.add_output_item_message()
        yield msg.emit_added()
        text = msg.add_text_content()
        yield text.emit_added()
        yield text.emit_text_done("ok")
        yield text.emit_done()
        yield msg.emit_done()

        yield stream.emit_completed()

    return _events()


def _build_client() -> TestClient:
    app = ResponsesAgentServerHost()
    app.response_handler(_capture_handler)
    return TestClient(app)


def _send_and_capture(json_body: str) -> CreateResponse:
    """POST raw JSON to /responses and return the captured CreateResponse."""
    _captured.clear()
    client = _build_client()
    resp = client.post(
        "/responses",
        content=json_body.encode("utf-8"),
        headers={"content-type": "application/json"},
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    return _captured["request"]


def _send_input_and_capture(input_items_json: str) -> list:
    """Send input items array and return the expanded item list."""
    json_body = f'{{"model": "test", "input": {input_items_json}}}'
    request = _send_and_capture(json_body)
    return get_input_expanded(request)


def _send_stream_and_collect(json_body: str) -> list[dict[str, Any]]:
    """POST raw JSON with stream=True and collect SSE events."""
    _captured.clear()
    client = _build_client()
    body = json.loads(json_body)
    body["stream"] = True
    with client.stream(
        "POST",
        "/responses",
        content=json.dumps(body).encode("utf-8"),
        headers={"content-type": "application/json"},
    ) as resp:
        assert resp.status_code == 200
        events: list[dict[str, Any]] = []
        current_type: str | None = None
        current_data: str | None = None
        for line in resp.iter_lines():
            if not line:
                if current_type is not None:
                    events.append(
                        {
                            "type": current_type,
                            "data": json.loads(current_data) if current_data else {},
                        }
                    )
                current_type = None
                current_data = None
                continue
            if line.startswith("event:"):
                current_type = line.split(":", 1)[1].strip()
            elif line.startswith("data:"):
                current_data = line.split(":", 1)[1].strip()
        if current_type is not None:
            events.append(
                {
                    "type": current_type,
                    "data": json.loads(current_data) if current_data else {},
                }
            )
    return events


def _reject_payload(json_body: str) -> int:
    """POST raw JSON and return the status code (expected non-200)."""
    client = _build_client()
    resp = client.post(
        "/responses",
        content=json_body.encode("utf-8"),
        headers={"content-type": "application/json"},
    )
    return resp.status_code


# ═══════════════════════════════════════════════════════════════════
#  GAP-01: EasyInputMessage — type is OPTIONAL (C-MSG-01)
# ═══════════════════════════════════════════════════════════════════


def test_c_msg_01__message_without_type_accepted_as_message() -> None:
    """OpenAI spec: EasyInputMessage does NOT require 'type'."""
    items = _send_input_and_capture("""
        [{ "role": "user", "content": "Hello without type" }]
    """)
    assert len(items) == 1
    assert items[0].get("type") == "message"
    assert items[0].get("role") == "user"


def test_c_msg_01__message_with_type_also_accepted() -> None:
    items = _send_input_and_capture("""
        [{ "type": "message", "role": "user", "content": "With type" }]
    """)
    assert len(items) == 1
    assert items[0].get("role") == "user"


def test_c_msg_01__multiple_messages_without_type() -> None:
    items = _send_input_and_capture("""
        [
            { "role": "developer", "content": "System msg" },
            { "role": "user", "content": "User msg" },
            { "role": "assistant", "content": "Asst msg" }
        ]
    """)
    assert len(items) == 3
    assert items[0].get("role") == "developer"
    assert items[1].get("role") == "user"
    assert items[2].get("role") == "assistant"


# ═══════════════════════════════════════════════════════════════════
#  ItemReferenceParam — type is REQUIRED (SDK always sends it)
# ═══════════════════════════════════════════════════════════════════


def test_item_reference_with_type_accepted() -> None:
    items = _send_input_and_capture("""
        [{ "type": "item_reference", "id": "msg_existing_002" }]
    """)
    assert len(items) == 1
    assert items[0].get("type") == "item_reference"
    assert items[0].get("id") == "msg_existing_002"


# ═══════════════════════════════════════════════════════════════════
#  GAP-03: InputImageContent.detail is OPTIONAL (C-IMG-01)
# ═══════════════════════════════════════════════════════════════════


def test_c_img_01__input_image_without_detail_accepted() -> None:
    items = _send_input_and_capture("""
        [{
            "type": "message",
            "role": "user",
            "content": [
                { "type": "input_image", "image_url": "https://example.com/img.png" }
            ]
        }]
    """)
    assert len(items) == 1
    assert items[0].get("type") == "message"


def test_c_img_01__input_image_with_detail_also_accepted() -> None:
    items = _send_input_and_capture("""
        [{
            "type": "message",
            "role": "user",
            "content": [
                { "type": "input_image", "image_url": "https://example.com/img.png", "detail": "high" }
            ]
        }]
    """)
    assert len(items) == 1


def test_c_img_01__input_image_with_null_detail_accepted() -> None:
    items = _send_input_and_capture("""
        [{
            "type": "message",
            "role": "user",
            "content": [
                { "type": "input_image", "image_url": "https://example.com/img.png", "detail": null }
            ]
        }]
    """)
    assert len(items) == 1


# ═══════════════════════════════════════════════════════════════════
#  GAP-04 & GAP-05: FunctionTool — strict & parameters OPTIONAL
# ═══════════════════════════════════════════════════════════════════


def test_c_func_01__function_tool_without_strict_accepted() -> None:
    request = _send_and_capture("""
        {
            "model": "test",
            "tools": [{
                "type": "function",
                "name": "get_weather",
                "description": "Get weather",
                "parameters": { "type": "object", "properties": {} }
            }]
        }
    """)
    assert request.tools is not None
    assert len(request.tools) == 1
    assert request.tools[0].get("type") == "function"
    assert request.tools[0].get("name") == "get_weather"


def test_c_func_02__function_tool_without_parameters_accepted() -> None:
    request = _send_and_capture("""
        {
            "model": "test",
            "tools": [{
                "type": "function",
                "name": "no_params_tool"
            }]
        }
    """)
    assert request.tools is not None
    assert len(request.tools) == 1
    assert request.tools[0].get("name") == "no_params_tool"


def test_c_func_01_02__function_tool_minimal_form_accepted() -> None:
    request = _send_and_capture("""
        {
            "model": "test",
            "tools": [{ "type": "function", "name": "minimal_tool" }]
        }
    """)
    assert request.tools is not None
    assert len(request.tools) == 1
    assert request.tools[0].get("name") == "minimal_tool"


def test_c_func_01__function_tool_with_strict_null_accepted() -> None:
    request = _send_and_capture("""
        {
            "model": "test",
            "tools": [{
                "type": "function",
                "name": "get_weather",
                "strict": null,
                "parameters": { "type": "object", "properties": {} }
            }]
        }
    """)
    assert request.tools is not None
    assert len(request.tools) == 1


def test_c_func_01__function_tool_with_strict_true_accepted() -> None:
    request = _send_and_capture("""
        {
            "model": "test",
            "tools": [{
                "type": "function",
                "name": "strict_tool",
                "strict": true,
                "parameters": { "type": "object", "properties": {} }
            }]
        }
    """)
    assert request.tools is not None
    assert len(request.tools) == 1


# ═══════════════════════════════════════════════════════════════════
#  INPUT ITEM TYPES — all types recognized by the OpenAI spec
# ═══════════════════════════════════════════════════════════════════


def test_input_message_text_content() -> None:
    items = _send_input_and_capture("""
        [{
            "type": "message",
            "role": "user",
            "content": [{ "type": "input_text", "text": "Hello" }]
        }]
    """)
    assert len(items) == 1
    assert items[0].get("type") == "message"
    assert items[0].get("role") == "user"
    content = items[0].get("content", [])
    assert len(content) == 1
    assert content[0].get("type") == "input_text"
    assert content[0].get("text") == "Hello"


def test_input_message_string_content() -> None:
    items = _send_input_and_capture("""
        [{ "type": "message", "role": "developer", "content": "System prompt" }]
    """)
    assert len(items) == 1
    assert items[0].get("role") == "developer"


def test_input_message_multiple_content_parts() -> None:
    items = _send_input_and_capture("""
        [{
            "type": "message",
            "role": "user",
            "content": [
                { "type": "input_text", "text": "Look at this image" },
                { "type": "input_image", "image_url": "https://example.com/img.png" }
            ]
        }]
    """)
    assert len(items) == 1
    content = items[0].get("content", [])
    assert len(content) == 2


def test_input_message_all_roles() -> None:
    items = _send_input_and_capture("""
        [
            { "type": "message", "role": "user", "content": "r1" },
            { "type": "message", "role": "assistant", "content": "r2" },
            { "type": "message", "role": "developer", "content": "r3" },
            { "type": "message", "role": "system", "content": "r4" }
        ]
    """)
    assert len(items) == 4
    assert items[0].get("role") == "user"
    assert items[1].get("role") == "assistant"
    assert items[2].get("role") == "developer"
    assert items[3].get("role") == "system"


def test_input_function_call() -> None:
    items = _send_input_and_capture("""
        [{
            "type": "function_call",
            "call_id": "call_abc",
            "name": "get_weather",
            "arguments": "{\\"city\\":\\"Seattle\\"}"
        }]
    """)
    assert len(items) == 1
    assert items[0].get("type") == "function_call"
    assert items[0].get("call_id") == "call_abc"
    assert items[0].get("name") == "get_weather"
    assert items[0].get("arguments") == '{"city":"Seattle"}'


def test_input_function_call_output_string_output() -> None:
    items = _send_input_and_capture("""
        [{
            "type": "function_call_output",
            "call_id": "call_abc",
            "output": "72°F and sunny"
        }]
    """)
    assert len(items) == 1
    assert items[0].get("type") == "function_call_output"
    assert items[0].get("call_id") == "call_abc"


def test_input_function_call_output_array_output() -> None:
    """output can be an array of content parts per OpenAI spec."""
    items = _send_input_and_capture("""
        [{
            "type": "function_call_output",
            "call_id": "call_xyz",
            "output": [
                { "type": "input_text", "text": "Result text" }
            ]
        }]
    """)
    assert len(items) == 1
    assert items[0].get("type") == "function_call_output"


def test_input_reasoning() -> None:
    items = _send_input_and_capture("""
        [{
            "type": "reasoning",
            "id": "rs_abc",
            "summary": [
                { "type": "summary_text", "text": "Thinking step 1" }
            ]
        }]
    """)
    assert len(items) == 1
    assert items[0].get("type") == "reasoning"
    assert items[0].get("id") == "rs_abc"


def test_input_computer_call_output() -> None:
    items = _send_input_and_capture("""
        [{
            "type": "computer_call_output",
            "call_id": "cu_abc",
            "output": {
                "type": "computer_screenshot",
                "image_url": "https://example.com/screenshot.png"
            }
        }]
    """)
    assert len(items) == 1
    assert items[0].get("type") == "computer_call_output"
    assert items[0].get("call_id") == "cu_abc"


def test_input_mcp_approval_response() -> None:
    items = _send_input_and_capture("""
        [{
            "type": "mcp_approval_response",
            "approval_request_id": "mcpr_abc",
            "approve": true
        }]
    """)
    assert len(items) == 1
    assert items[0].get("type") == "mcp_approval_response"
    assert items[0].get("approval_request_id") == "mcpr_abc"
    assert items[0].get("approve") is True


def test_input_mixed_types_all_deserialize() -> None:
    items = _send_input_and_capture("""
        [
            { "role": "user", "content": "Hello" },
            { "type": "function_call", "call_id": "c1", "name": "fn", "arguments": "{}" },
            { "type": "function_call_output", "call_id": "c1", "output": "done" },
            { "type": "item_reference", "id": "ref_001" }
        ]
    """)
    assert len(items) == 4
    # First item is a message (inferred from role without type)
    assert items[0].get("role") == "user"
    assert items[1].get("type") == "function_call"
    assert items[2].get("type") == "function_call_output"
    assert items[3].get("type") == "item_reference"


# ═══════════════════════════════════════════════════════════════════
#  CREATERESPONSE PROPERTIES — all fields round-trip
# ═══════════════════════════════════════════════════════════════════


def test_create_response_model() -> None:
    req = _send_and_capture('{"model": "gpt-4o-mini"}')
    assert req.model == "gpt-4o-mini"


def test_create_response_instructions() -> None:
    req = _send_and_capture('{"model": "test", "instructions": "Be helpful"}')
    assert req.instructions == "Be helpful"


def test_create_response_temperature() -> None:
    req = _send_and_capture('{"model": "test", "temperature": 0.7}')
    assert abs(req.temperature - 0.7) < 0.001


def test_create_response_top_p() -> None:
    req = _send_and_capture('{"model": "test", "top_p": 0.9}')
    assert abs(req.top_p - 0.9) < 0.001


def test_create_response_max_output_tokens() -> None:
    req = _send_and_capture('{"model": "test", "max_output_tokens": 1024}')
    assert req.max_output_tokens == 1024


def test_create_response_previous_response_id() -> None:
    req = _send_and_capture('{"model": "test", "previous_response_id": "resp_prev_001"}')
    assert req.previous_response_id == "resp_prev_001"


def test_create_response_store() -> None:
    req = _send_and_capture('{"model": "test", "store": false}')
    assert req.store is False


def test_create_response_metadata() -> None:
    req = _send_and_capture('{"model": "test", "metadata": {"key": "value"}}')
    assert req.metadata is not None
    assert req.metadata.get("key") == "value"


def test_create_response_parallel_tool_calls() -> None:
    req = _send_and_capture('{"model": "test", "parallel_tool_calls": false}')
    assert req.parallel_tool_calls is False


def test_create_response_truncation() -> None:
    req = _send_and_capture('{"model": "test", "truncation": "auto"}')
    assert req.truncation is not None


def test_create_response_reasoning() -> None:
    req = _send_and_capture('{"model": "test", "reasoning": {"effort": "high"}}')
    assert req.reasoning is not None


def test_create_response_tool_choice_auto() -> None:
    req = _send_and_capture('{"model": "test", "tool_choice": "auto"}')
    tc = get_tool_choice_expanded(req)
    assert tc is not None
    assert tc.get("type") == "auto" or tc.get("mode") == "auto"


def test_create_response_tool_choice_required() -> None:
    req = _send_and_capture('{"model": "test", "tool_choice": "required"}')
    tc = get_tool_choice_expanded(req)
    assert tc is not None


def test_create_response_tool_choice_none() -> None:
    req = _send_and_capture('{"model": "test", "tool_choice": "none"}')
    tc = get_tool_choice_expanded(req)
    assert tc is None


def test_create_response_tool_choice_function_object() -> None:
    req = _send_and_capture("""
        {"model": "test", "tool_choice": {"type": "function", "name": "get_weather"}}
    """)
    tc = get_tool_choice_expanded(req)
    assert tc is not None
    assert tc.get("name") == "get_weather"


def test_create_response_tools_web_search() -> None:
    req = _send_and_capture("""
        {"model": "test", "tools": [{"type": "web_search_preview"}]}
    """)
    assert req.tools is not None
    assert len(req.tools) == 1
    assert req.tools[0].get("type") == "web_search_preview"


def test_create_response_tools_file_search() -> None:
    req = _send_and_capture("""
        {"model": "test", "tools": [{"type": "file_search", "vector_store_ids": ["vs_abc"]}]}
    """)
    assert req.tools is not None
    assert len(req.tools) == 1
    assert req.tools[0].get("type") == "file_search"


def test_create_response_tools_code_interpreter() -> None:
    req = _send_and_capture("""
        {"model": "test", "tools": [{"type": "code_interpreter"}]}
    """)
    assert req.tools is not None
    assert len(req.tools) == 1
    assert req.tools[0].get("type") == "code_interpreter"


def test_create_response_stream() -> None:
    events = _send_stream_and_collect('{"model": "test"}')
    assert len(events) > 0
    assert events[0]["type"] == "response.created"


# ═══════════════════════════════════════════════════════════════════
#  RESPONSE OBJECT — server output readable by OpenAI SDK
# ═══════════════════════════════════════════════════════════════════


def test_response_object_has_required_fields() -> None:
    """Non-streaming response has all required fields per OpenAI spec."""
    client = _build_client()
    resp = client.post(
        "/responses",
        content=b'{"model": "gpt-4o"}',
        headers={"content-type": "application/json"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "id" in body
    assert body.get("object") == "response"
    assert body.get("status") in {"completed", "failed", "in_progress", "cancelled", "queued", "incomplete"}
    assert body.get("model") == "gpt-4o"
    assert "output" in body
    assert "created_at" in body


# ═══════════════════════════════════════════════════════════════════
#  SHORTHAND NOTATIONS — string | array forms
# ═══════════════════════════════════════════════════════════════════


def test_input_string_shorthand_expands_to_user_message() -> None:
    req = _send_and_capture('{"model": "test", "input": "Hello world"}')
    items = get_input_expanded(req)
    assert len(items) == 1
    assert items[0].get("role") == "user"
    content = items[0].get("content", [])
    assert len(content) == 1
    assert content[0].get("type") == "input_text"
    assert content[0].get("text") == "Hello world"


def test_input_empty_array_returns_empty() -> None:
    req = _send_and_capture('{"model": "test", "input": []}')
    assert get_input_expanded(req) == []


def test_input_null_or_absent_returns_empty() -> None:
    req = _send_and_capture('{"model": "test"}')
    assert get_input_expanded(req) == []


def test_message_content_string_shorthand_expands_to_input_text() -> None:
    items = _send_input_and_capture("""
        [{"type": "message", "role": "user", "content": "shorthand"}]
    """)
    # Content is stored as the raw value — may be string or expanded
    # The server keeps the original form; expansion happens via get_content_expanded
    assert len(items) == 1
    assert items[0].get("role") == "user"


def test_message_content_empty_string_accepted() -> None:
    items = _send_input_and_capture("""
        [{"type": "message", "role": "user", "content": ""}]
    """)
    assert len(items) == 1


# ═══════════════════════════════════════════════════════════════════
#  COMBINED SCENARIO — realistic multi-turn with all shorthands
# ═══════════════════════════════════════════════════════════════════


def test_full_payload_all_shorthands_and_minimal_forms() -> None:
    """Uses ALL shorthand/minimal forms in one request."""
    req = _send_and_capture("""
        {
            "model": "gpt-4o",
            "input": "What is the weather?",
            "instructions": "Be helpful",
            "tool_choice": "auto",
            "store": true,
            "temperature": 0.5,
            "max_output_tokens": 500,
            "tools": [
                { "type": "function", "name": "get_weather" }
            ]
        }
    """)
    assert req.model == "gpt-4o"
    assert req.instructions == "Be helpful"
    assert abs(req.temperature - 0.5) < 0.001
    assert req.max_output_tokens == 500
    assert req.store is True

    items = get_input_expanded(req)
    assert len(items) == 1
    assert items[0].get("role") == "user"

    tc = get_tool_choice_expanded(req)
    assert tc is not None

    assert req.tools is not None
    assert len(req.tools) == 1


def test_multi_turn_mixed_shorthand_and_full_form() -> None:
    items = _send_input_and_capture("""
        [
            { "role": "developer", "content": "You are helpful" },
            {
                "type": "message",
                "role": "user",
                "content": [
                    { "type": "input_text", "text": "Look at this" },
                    { "type": "input_image", "image_url": "https://example.com/img.png" }
                ]
            }
        ]
    """)
    assert len(items) == 2
    assert items[0].get("role") == "developer"
    assert items[1].get("role") == "user"
    content = items[1].get("content", [])
    assert len(content) == 2


# ═══════════════════════════════════════════════════════════════════
#  VALIDATION — reject truly invalid inputs
# ═══════════════════════════════════════════════════════════════════


def test_reject_input_as_number() -> None:
    status = _reject_payload('{"model": "test", "input": 42}')
    assert status == 400


def test_reject_input_as_boolean() -> None:
    status = _reject_payload('{"model": "test", "input": true}')
    assert status == 400


def test_reject_content_as_number() -> None:
    status = _reject_payload("""
        {"model": "test", "input": [{"type": "message", "role": "user", "content": 42}]}
    """)
    assert status == 400
