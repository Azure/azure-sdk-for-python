# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Phase E Part D stream builder parity tests."""

from __future__ import annotations

from azure.ai.agentserver.responses._id_generator import IdGenerator
from azure.ai.agentserver.responses.models._generated import (
    OutputItemMessage,
    ResponseObject,
    ResponseStreamEvent,
)
from azure.ai.agentserver.responses.streaming import (
    OutputItemFunctionCallBuilder,
    OutputItemFunctionCallOutputBuilder,
    OutputItemMessageBuilder,
    ResponseEventStream,
    TextContentBuilder,
)


def test_text_content_builder__emits_added_delta_done_events() -> None:
    stream = ResponseEventStream(response_id="resp_builder_1")
    stream.emit_created()
    message = stream.add_output_item_message()
    message.emit_added()
    text = message.add_text_content()

    added = text.emit_added()
    delta = text.emit_delta("hello")
    text_done = text.emit_text_done()
    done = text.emit_done()

    assert isinstance(text, TextContentBuilder)
    # Every emitted event must be a ResponseStreamEvent subtype, not a plain dict
    for event in (added, delta, text_done, done):
        assert isinstance(event, ResponseStreamEvent), f"Expected ResponseStreamEvent, got {type(event)}"
    assert added["type"] == "response.content_part.added"
    assert delta["type"] == "response.output_text.delta"
    assert text_done["type"] == "response.output_text.done"
    assert text_done["text"] == "hello"
    assert done["type"] == "response.content_part.done"


def test_text_content_builder__emit_done_merges_all_delta_fragments() -> None:
    stream = ResponseEventStream(response_id="resp_builder_1b")
    stream.emit_created()
    message = stream.add_output_item_message()
    message.emit_added()
    text = message.add_text_content()

    text.emit_added()
    text.emit_delta("hello")
    text.emit_delta(" ")
    text.emit_delta("world")
    done = text.emit_text_done()

    assert done["type"] == "response.output_text.done"
    assert done["text"] == "hello world"
    assert text.final_text == "hello world"


def test_output_item_message_builder__emits_added_content_done_and_done() -> None:
    stream = ResponseEventStream(response_id="resp_builder_2")
    stream.emit_created()
    message = stream.add_output_item_message()
    text = message.add_text_content()

    added = message.emit_added()
    text.emit_added()
    text.emit_delta("alpha")
    text.emit_text_done()
    content_done = text.emit_done()
    done = message.emit_done()

    assert isinstance(message, OutputItemMessageBuilder)
    for event in (added, content_done, done):
        assert isinstance(event, ResponseStreamEvent), f"Expected ResponseStreamEvent, got {type(event)}"
    assert added["type"] == "response.output_item.added"
    assert content_done["type"] == "response.content_part.done"
    assert done["type"] == "response.output_item.done"
    assert done["item"]["type"] == "message"
    assert done["item"]["content"][0]["text"] == "alpha"


def test_output_item_function_call_builder__emits_arguments_and_done_events() -> None:
    stream = ResponseEventStream(response_id="resp_builder_3")
    stream.emit_created()
    function_call = stream.add_output_item_function_call("get_weather", "call_1")

    added = function_call.emit_added()
    delta = function_call.emit_arguments_delta('{"loc')
    args_done = function_call.emit_arguments_done('{"location": "Seattle"}')
    done = function_call.emit_done()

    assert isinstance(function_call, OutputItemFunctionCallBuilder)
    for event in (added, delta, args_done, done):
        assert isinstance(event, ResponseStreamEvent), f"Expected ResponseStreamEvent, got {type(event)}"
    assert added["type"] == "response.output_item.added"
    assert delta["type"] == "response.function_call_arguments.delta"
    assert args_done["type"] == "response.function_call_arguments.done"
    assert done["type"] == "response.output_item.done"
    assert done["item"]["name"] == "get_weather"
    assert done["item"]["call_id"] == "call_1"
    assert done["item"]["arguments"] == '{"location": "Seattle"}'


def test_output_item_function_call_output_builder__emits_added_and_done_events() -> None:
    stream = ResponseEventStream(response_id="resp_builder_3b")
    stream.emit_created()
    function_output = stream.add_output_item_function_call_output("call_1")

    added = function_output.emit_added("partial")
    done = function_output.emit_done("result")

    assert isinstance(function_output, OutputItemFunctionCallOutputBuilder)
    for event in (added, done):
        assert isinstance(event, ResponseStreamEvent), f"Expected ResponseStreamEvent, got {type(event)}"
    assert added["type"] == "response.output_item.added"
    assert added["item"]["type"] == "function_call_output"
    assert added["item"]["call_id"] == "call_1"
    assert done["type"] == "response.output_item.done"
    assert done["item"]["output"] == "result"


def test_output_item_events__item_has_response_id_and_agent_reference() -> None:
    """B20/B21 — output items carry response_id and agent_reference stamped by _with_output_item_defaults."""
    stream = ResponseEventStream(
        response_id="resp_builder_3c",
        agent_reference={"type": "agent_reference", "name": "agent-a"},
    )
    stream.emit_created()
    function_call = stream.add_output_item_function_call("get_weather", "call_2")

    added = function_call.emit_added()
    done = function_call.emit_done()

    assert added["item"]["response_id"] == "resp_builder_3c"
    assert added["item"]["agent_reference"]["name"] == "agent-a"
    assert done["item"]["response_id"] == "resp_builder_3c"
    assert done["item"]["agent_reference"]["name"] == "agent-a"


def test_stream_builders__share_global_sequence_number() -> None:
    stream = ResponseEventStream(response_id="resp_builder_4")
    stream.emit_created()
    stream.emit_in_progress()
    message = stream.add_output_item_message()
    event = message.emit_added()

    assert event["sequence_number"] == 2


def test_message_builder__output_index_increments_across_factories() -> None:
    stream = ResponseEventStream(response_id="resp_builder_5")
    stream.emit_created()
    message = stream.add_output_item_message()
    function_call = stream.add_output_item_function_call("fn", "call_1")
    function_output = stream.add_output_item_function_call_output("call_2")

    assert message.output_index == 0
    assert function_call.output_index == 1
    assert function_output.output_index == 2


def test_message_builder__emit_done_requires_completed_content() -> None:
    stream = ResponseEventStream(response_id="resp_builder_6")
    stream.emit_created()
    message = stream.add_output_item_message()
    message.emit_added()

    import pytest

    with pytest.raises(ValueError):
        message.emit_done()


def test_builder_events__include_required_payload_fields_per_event_type() -> None:
    stream = ResponseEventStream(response_id="resp_builder_7")
    stream.emit_created()

    code_interpreter = stream.add_output_item_code_interpreter_call()
    code_delta = code_interpreter.emit_code_delta("print('hi')")
    code_done = code_interpreter.emit_code_done("print('hi')")

    image_gen = stream.add_output_item_image_gen_call()
    partial_image = image_gen.emit_partial_image("ZmFrZS1pbWFnZQ==")

    custom_tool = stream.add_output_item_custom_tool_call("call_7", "custom")
    input_done = custom_tool.emit_input_done('{"ok": true}')

    function_call = stream.add_output_item_function_call("tool_fn", "call_fn_7")
    args_done = function_call.emit_arguments_done('{"city": "Seattle"}')

    mcp_call = stream.add_output_item_mcp_call("srv", "tool")
    mcp_args_done = mcp_call.emit_arguments_done('{"arg": 1}')

    message = stream.add_output_item_message()
    message.emit_added()
    refusal = message.add_refusal_content()
    refusal.emit_added()
    refusal.emit_refusal_done("cannot comply")
    refusal_part_done = refusal.emit_done()

    reasoning = stream.add_output_item_reasoning_item()
    reasoning.emit_added()
    summary = reasoning.add_summary_part()
    summary_added = summary.emit_added()
    summary.emit_text_done("short reason")
    summary_done = summary.emit_done()
    reasoning_item_done = reasoning.emit_done()

    assert code_delta["type"] == "response.code_interpreter_call_code.delta"
    assert code_delta["item_id"] == code_interpreter.item_id
    assert code_delta["delta"] == "print('hi')"

    assert code_done["type"] == "response.code_interpreter_call_code.done"
    assert code_done["item_id"] == code_interpreter.item_id
    assert code_done["code"] == "print('hi')"

    assert partial_image["type"] == "response.image_generation_call.partial_image"
    assert partial_image["item_id"] == image_gen.item_id
    assert partial_image["partial_image_index"] == 0
    assert partial_image["partial_image_b64"] == "ZmFrZS1pbWFnZQ=="

    assert input_done["type"] == "response.custom_tool_call_input.done"
    assert input_done["item_id"] == custom_tool.item_id
    assert input_done["input"] == '{"ok": true}'

    assert args_done["type"] == "response.function_call_arguments.done"
    assert args_done["item_id"] == function_call.item_id
    assert args_done["name"] == "tool_fn"
    assert args_done["arguments"] == '{"city": "Seattle"}'

    assert mcp_args_done["type"] == "response.mcp_call_arguments.done"
    assert mcp_args_done["item_id"] == mcp_call.item_id
    assert mcp_args_done["arguments"] == '{"arg": 1}'

    assert refusal_part_done["type"] == "response.content_part.done"
    assert refusal_part_done["part"]["type"] == "refusal"
    assert refusal_part_done["part"]["refusal"] == "cannot comply"

    assert summary_added["type"] == "response.reasoning_summary_part.added"
    assert summary_added["part"]["type"] == "summary_text"
    assert summary_added["part"]["text"] == ""

    assert summary_done["type"] == "response.reasoning_summary_part.done"
    assert summary_done["part"]["type"] == "summary_text"
    assert summary_done["part"]["text"] == "short reason"

    assert reasoning_item_done["type"] == "response.output_item.done"
    assert reasoning_item_done["item"]["summary"][0]["type"] == "summary_text"
    assert reasoning_item_done["item"]["summary"][0]["text"] == "short reason"


def test_stream_item_id_generation__uses_expected_shape_and_response_partition_key() -> None:
    response_id = IdGenerator.new_response_id()
    stream = ResponseEventStream(response_id=response_id)

    generated_item_ids = [
        stream.add_output_item_message().item_id,
        stream.add_output_item_function_call("fn", "call_a").item_id,
        stream.add_output_item_function_call_output("call_b").item_id,
        stream.add_output_item_reasoning_item().item_id,
        stream.add_output_item_file_search_call().item_id,
        stream.add_output_item_web_search_call().item_id,
        stream.add_output_item_code_interpreter_call().item_id,
        stream.add_output_item_image_gen_call().item_id,
        stream.add_output_item_mcp_call("srv", "tool").item_id,
        stream.add_output_item_mcp_list_tools("srv").item_id,
        stream.add_output_item_custom_tool_call("call_c", "custom").item_id,
    ]

    response_partition_key = IdGenerator.extract_partition_key(response_id)
    for item_id in generated_item_ids:
        assert IdGenerator.extract_partition_key(item_id) == response_partition_key
        body = item_id.split("_", maxsplit=1)[1]
        assert len(body) == 50


def test_response_event_stream__exposes_mutable_response_snapshot_for_lifecycle_events() -> None:
    stream = ResponseEventStream(response_id="resp_builder_snapshot", model="gpt-4o-mini")
    stream.response.temperature = 1
    stream.response.metadata = {"source": "unit-test"}

    created = stream.emit_created()

    assert created["type"] == "response.created"
    assert created["response"]["id"] == "resp_builder_snapshot"
    assert created["response"]["model"] == "gpt-4o-mini"
    assert created["response"]["temperature"] == 1
    assert created["response"]["metadata"] == {"source": "unit-test"}


def test_response_event_stream__tracks_completed_output_items_into_response_output() -> None:
    stream = ResponseEventStream(response_id="resp_builder_output")
    stream.emit_created()

    message = stream.add_output_item_message()
    message.emit_added()
    text = message.add_text_content()
    text.emit_added()
    text.emit_delta("hello")
    text.emit_text_done()
    text.emit_done()
    done = message.emit_done()

    assert done["type"] == "response.output_item.done"
    # response.output items must be properly typed model instances
    assert isinstance(stream.response, ResponseObject)
    assert len(stream.response.output) == 1
    output_item_obj = stream.response.output[0]
    assert isinstance(output_item_obj, OutputItemMessage), (
        f"Expected OutputItemMessage on response.output, got {type(output_item_obj)}"
    )
    output_item = output_item_obj.as_dict()
    assert output_item["id"] == message.item_id
    assert output_item["type"] == "message"
    assert output_item["content"][0]["text"] == "hello"
