import pytest
from langchain_core import messages as langgraph_messages

from azure.ai.agentserver.core import models
from azure.ai.agentserver.core.models import projects as project_models
from azure.ai.agentserver.langgraph.models.response_api_request_converter import ResponseAPIMessageRequestConverter


@pytest.mark.unit
def test_convert_implicit_user_message():
    """Test conversion of ImplicitUserMessage to HumanMessage."""

    input_data = "input text string"
    implicit_user_message = {"content": input_data}
    create_response = models.CreateResponse(
        input=[implicit_user_message],
    )

    converter = ResponseAPIMessageRequestConverter(create_response)
    res = converter.convert()

    assert "messages" in res
    assert len(res["messages"]) == 1
    assert isinstance(res["messages"][0], langgraph_messages.HumanMessage)
    assert res["messages"][0].content == input_data


@pytest.mark.unit
def test_convert_implicit_user_message_with_contents():
    """Test conversion of ImplicitUserMessage with list of contents to HumanMessage."""

    input_data = [
        {"text": "text content", "type": "input_text"},
    ]
    create_response = models.CreateResponse(input=[{"content": input_data}])

    converter = ResponseAPIMessageRequestConverter(create_response)
    res = converter.convert()

    assert "messages" in res
    assert len(res["messages"]) == 1
    assert isinstance(res["messages"][0], langgraph_messages.HumanMessage)
    assert isinstance(res["messages"][0].content, list)
    assert len(res["messages"][0].content) == len(input_data)

    for item_content, content in zip(input_data, res["messages"][0].content, strict=False):
        assert isinstance(content, dict)
        assert content["type"] == "text"
        assert content["text"] == item_content.get("text")


@pytest.mark.unit
def test_convert_item_param_message():
    """Test conversion of ItemParam of type MESSAGE to corresponding message."""

    input_data = [
        {"role": "user", "content": "user message"},
        {"role": "assistant", "content": "assistant message"},
        {"role": "system", "content": "system message"},
    ]
    create_response = models.CreateResponse(
        input=input_data,
    )
    converter = ResponseAPIMessageRequestConverter(create_response)
    res = converter.convert()

    assert "messages" in res
    assert len(res["messages"]) == len(input_data)

    for item, message in zip(input_data, res["messages"], strict=False):
        if item["role"] == project_models.ResponsesMessageRole.USER:
            assert isinstance(message, langgraph_messages.HumanMessage)
        elif item["role"] == project_models.ResponsesMessageRole.ASSISTANT:
            assert isinstance(message, langgraph_messages.AIMessage)
        elif item["role"] == project_models.ResponsesMessageRole.SYSTEM:
            assert isinstance(message, langgraph_messages.SystemMessage)
        else:
            pytest.fail(f"Unexpected role: {item['role']}")

        assert isinstance(message.content, str)
        assert message.content == item["content"]


@pytest.mark.unit
def test_convert_item_param_function_call_and_function_call_output():
    """Test conversion of ItemParam of type FUNCTION_CALL and FUNCTION_CALL_OUTPUT to corresponding message."""

    input_data = [
        {
            "type": "function_call",
            "call_id": "call_001",
            "name": "get_ticket_status",
            "arguments": '{"ticket_number": "845732"}',
            "status": "completed",
        },
        {
            "type": "function_call_output",
            "call_id": "call_001",
            "output": ('{"ticket_number": "845732", "status": "in_progress", "last_updated": "2024-07-15T09:42:00Z"}'),
            "status": "completed",
        },
    ]
    create_response = models.CreateResponse(
        input=input_data,
    )
    converter = ResponseAPIMessageRequestConverter(create_response)
    res = converter.convert()
    assert "messages" in res
    assert len(res["messages"]) == len(input_data)
    assert isinstance(res["messages"][0], langgraph_messages.AIMessage)
    assert res["messages"][0].tool_calls is not None
    assert len(res["messages"][0].tool_calls) == 1
    tool_call_detail = res["messages"][0].tool_calls[0]
    assert tool_call_detail["id"] == "call_001"
    assert tool_call_detail["name"] == "get_ticket_status"
    assert tool_call_detail["args"] == {"ticket_number": "845732"}
    assert isinstance(res["messages"][1], langgraph_messages.ToolMessage)
    assert res["messages"][1].tool_call_id == "call_001"
    assert res["messages"][1].content == (
        '{"ticket_number": "845732", "status": "in_progress", "last_updated": "2024-07-15T09:42:00Z"}'
    )
