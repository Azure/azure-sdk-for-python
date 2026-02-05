"""Tests for historical items fetching and merging functionality."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from azure.ai.agentserver.langgraph.models.response_api_request_converter import convert_item_resource_to_message


@pytest.mark.unit
class TestConvertItemResourceToMessage:
    """Tests for convert_item_resource_to_message function."""

    def test_convert_user_message_with_input_text(self):
        """Test conversion of user message with input_text content."""
        item = {
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": "Hello, how are you?"}],
        }
        result = convert_item_resource_to_message(item)

        assert isinstance(result, HumanMessage)
        assert result.content == "Hello, how are you?"

    def test_convert_assistant_message_with_output_text(self):
        """Test conversion of assistant message with output_text content."""
        item = {
            "type": "message",
            "role": "assistant",
            "content": [{"type": "output_text", "text": "I'm doing well, thank you!"}],
        }
        result = convert_item_resource_to_message(item)

        assert isinstance(result, AIMessage)
        assert result.content == "I'm doing well, thank you!"

    def test_convert_system_message(self):
        """Test conversion of system message."""
        item = {
            "type": "message",
            "role": "system",
            "content": [{"type": "input_text", "text": "You are a helpful assistant."}],
        }
        result = convert_item_resource_to_message(item)

        assert isinstance(result, SystemMessage)
        assert result.content == "You are a helpful assistant."

    def test_convert_message_with_string_content(self):
        """Test conversion of message with direct string content."""
        item = {
            "type": "message",
            "role": "user",
            "content": "Direct string content",
        }
        result = convert_item_resource_to_message(item)

        assert isinstance(result, HumanMessage)
        assert result.content == "Direct string content"

    def test_convert_function_call(self):
        """Test conversion of function call item."""
        item = {
            "type": "function_call",
            "call_id": "call_123",
            "name": "get_weather",
            "arguments": '{"location": "Seattle"}',
        }
        result = convert_item_resource_to_message(item)

        assert isinstance(result, AIMessage)
        assert len(result.tool_calls) == 1
        assert result.tool_calls[0]["id"] == "call_123"
        assert result.tool_calls[0]["name"] == "get_weather"
        assert result.tool_calls[0]["args"] == {"location": "Seattle"}

    def test_convert_function_call_output(self):
        """Test conversion of function call output item."""
        item = {
            "type": "function_call_output",
            "call_id": "call_123",
            "output": "Sunny, 72°F",
        }
        result = convert_item_resource_to_message(item)

        assert isinstance(result, ToolMessage)
        assert result.tool_call_id == "call_123"
        assert result.content == "Sunny, 72°F"

    def test_convert_unsupported_type_returns_none(self):
        """Test that unsupported item types return None."""
        item = {
            "type": "unknown_type",
            "content": "some content",
        }
        result = convert_item_resource_to_message(item)

        assert result is None

    def test_convert_message_with_empty_content_list(self):
        """Test conversion of message with empty content list."""
        item = {
            "type": "message",
            "role": "user",
            "content": [],
        }
        result = convert_item_resource_to_message(item)

        assert isinstance(result, HumanMessage)
        assert result.content == ""


@pytest.mark.unit
class TestMergeMessagesWithoutDuplicates:
    """Tests for the merge logic in ResponseAPIDefaultConverter."""

    def test_merge_no_duplicates(self):
        """Test merging when there are no duplicates."""
        from azure.ai.agentserver.langgraph.models.response_api_default_converter import (
            ResponseAPIDefaultConverter,
        )

        # Create a minimal mock graph with valid schema
        mock_graph = MagicMock()
        mock_graph.builder.state_schema.__annotations__ = {"messages": list}
        mock_graph.checkpointer = None

        with patch(
            "azure.ai.agentserver.langgraph.models.utils.is_state_schema_valid",
            return_value=True,
        ):
            converter = ResponseAPIDefaultConverter(graph=mock_graph)

        historical = [
            HumanMessage(content="Historical message 1"),
            AIMessage(content="Historical response 1"),
        ]
        current = [
            HumanMessage(content="Current message"),
        ]

        result = converter._merge_messages_without_duplicates(historical, current, "conv_123")

        assert len(result) == 3
        assert result[0].content == "Historical message 1"
        assert result[1].content == "Historical response 1"
        assert result[2].content == "Current message"

    def test_merge_with_duplicates(self):
        """Test merging filters out duplicate messages."""
        from azure.ai.agentserver.langgraph.models.response_api_default_converter import (
            ResponseAPIDefaultConverter,
        )

        mock_graph = MagicMock()
        mock_graph.builder.state_schema.__annotations__ = {"messages": list}
        mock_graph.checkpointer = None

        with patch(
            "azure.ai.agentserver.langgraph.models.utils.is_state_schema_valid",
            return_value=True,
        ):
            converter = ResponseAPIDefaultConverter(graph=mock_graph)

        historical = [
            HumanMessage(content="Duplicate message"),
            HumanMessage(content="Unique historical message"),
        ]
        current = [
            HumanMessage(content="Duplicate message"),  # This is a duplicate
        ]

        result = converter._merge_messages_without_duplicates(historical, current, "conv_123")

        assert len(result) == 2
        assert result[0].content == "Unique historical message"
        assert result[1].content == "Duplicate message"

    def test_merge_empty_historical(self):
        """Test merging when historical messages are empty."""
        from azure.ai.agentserver.langgraph.models.response_api_default_converter import (
            ResponseAPIDefaultConverter,
        )

        mock_graph = MagicMock()
        mock_graph.builder.state_schema.__annotations__ = {"messages": list}
        mock_graph.checkpointer = None

        with patch(
            "azure.ai.agentserver.langgraph.models.utils.is_state_schema_valid",
            return_value=True,
        ):
            converter = ResponseAPIDefaultConverter(graph=mock_graph)

        historical = []
        current = [
            HumanMessage(content="Current message"),
        ]

        result = converter._merge_messages_without_duplicates(historical, current, "conv_123")

        assert len(result) == 1
        assert result[0].content == "Current message"

    def test_merge_different_types_not_duplicates(self):
        """Test that messages with same content but different types are not considered duplicates."""
        from azure.ai.agentserver.langgraph.models.response_api_default_converter import (
            ResponseAPIDefaultConverter,
        )

        mock_graph = MagicMock()
        mock_graph.builder.state_schema.__annotations__ = {"messages": list}
        mock_graph.checkpointer = None

        with patch(
            "azure.ai.agentserver.langgraph.models.utils.is_state_schema_valid",
            return_value=True,
        ):
            converter = ResponseAPIDefaultConverter(graph=mock_graph)

        historical = [
            SystemMessage(content="Same content"),  # System message
        ]
        current = [
            HumanMessage(content="Same content"),  # Human message with same content
        ]

        result = converter._merge_messages_without_duplicates(historical, current, "conv_123")

        # Both should be kept because types are different
        assert len(result) == 2
