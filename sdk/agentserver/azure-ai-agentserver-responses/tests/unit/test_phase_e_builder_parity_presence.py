"""Parity presence tests for builder classes implemented in .NET."""

from __future__ import annotations

from azure.ai.agentserver.responses import (
    OutputItemCodeInterpreterCallBuilder,
    OutputItemCustomToolCallBuilder,
    OutputItemFileSearchCallBuilder,
    OutputItemFunctionCallBuilder,
    OutputItemImageGenCallBuilder,
    OutputItemMcpCallBuilder,
    OutputItemMcpListToolsBuilder,
    OutputItemReasoningItemBuilder,
    OutputItemWebSearchCallBuilder,
    ReasoningSummaryPartBuilder,
    RefusalContentBuilder,
    ResponseEventStream,
)


def test_builder_parity__all_dotnet_builder_types_are_available() -> None:
    stream = ResponseEventStream(response_id="resp_parity_1")
    stream.emit_created()

    message = stream.add_output_item_message()
    refusal = message.add_refusal_content()
    reasoning = stream.add_output_item_reasoning_item()
    summary = reasoning.add_summary_part()
    file_search = stream.add_output_item_file_search_call()
    web_search = stream.add_output_item_web_search_call()
    code_interpreter = stream.add_output_item_code_interpreter_call()
    image_gen = stream.add_output_item_image_gen_call()
    function_call = stream.add_output_item_function_call("fn", "call_1")
    mcp_call = stream.add_output_item_mcp_call("srv", "tool")
    mcp_list_tools = stream.add_output_item_mcp_list_tools("srv")
    custom_tool = stream.add_output_item_custom_tool_call("call_2", "custom")

    assert isinstance(refusal, RefusalContentBuilder)
    assert isinstance(reasoning, OutputItemReasoningItemBuilder)
    assert isinstance(summary, ReasoningSummaryPartBuilder)
    assert isinstance(file_search, OutputItemFileSearchCallBuilder)
    assert isinstance(web_search, OutputItemWebSearchCallBuilder)
    assert isinstance(code_interpreter, OutputItemCodeInterpreterCallBuilder)
    assert isinstance(image_gen, OutputItemImageGenCallBuilder)
    assert isinstance(function_call, OutputItemFunctionCallBuilder)
    assert isinstance(mcp_call, OutputItemMcpCallBuilder)
    assert isinstance(mcp_list_tools, OutputItemMcpListToolsBuilder)
    assert isinstance(custom_tool, OutputItemCustomToolCallBuilder)


def test_builder_parity__tool_builders_emit_expected_event_types() -> None:
    stream = ResponseEventStream(response_id="resp_parity_2")
    stream.emit_created()

    assert (
        stream.add_output_item_file_search_call().emit_in_progress()["type"]
        == "response.file_search_call.in_progress"
    )
    assert stream.add_output_item_web_search_call().emit_searching()["type"] == "response.web_search_call.searching"
    assert (
        stream.add_output_item_code_interpreter_call().emit_interpreting()["type"]
        == "response.code_interpreter_call.interpreting"
    )
    assert (
        stream.add_output_item_image_gen_call().emit_generating()["type"]
        == "response.image_generation_call.generating"
    )
    assert stream.add_output_item_mcp_call("srv", "tool").emit_failed()["type"] == "response.mcp_call.failed"
    assert (
        stream.add_output_item_mcp_list_tools("srv").emit_completed()["type"] == "response.mcp_list_tools.completed"
    )
    assert (
        stream.add_output_item_custom_tool_call("call_2", "custom").emit_input_delta("x")["type"]
        == "response.custom_tool_call_input.delta"
    )
