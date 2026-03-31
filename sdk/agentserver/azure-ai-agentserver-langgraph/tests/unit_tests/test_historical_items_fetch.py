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


def _create_converter():
    """Helper to create a ResponseAPIDefaultConverter with mocked graph."""
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
        return ResponseAPIDefaultConverter(graph=mock_graph)


@pytest.mark.unit
class TestMergeMessagesWithoutDuplicates:
    """Tests for the merge logic in ResponseAPIDefaultConverter."""

    def test_merge_no_duplicates(self):
        """Test merging when there are no duplicates."""
        converter = _create_converter()

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
        converter = _create_converter()

        # Historical ends with the same message as current
        historical = [
            HumanMessage(content="First message"),
            HumanMessage(content="Duplicate message"),  # Last message matches current
        ]
        current = [
            HumanMessage(content="Duplicate message"),  # This matches last historical
        ]

        result = converter._merge_messages_without_duplicates(historical, current, "conv_123")

        # Last historical should be removed since it matches current
        assert len(result) == 2
        assert result[0].content == "First message"
        assert result[1].content == "Duplicate message"

    def test_merge_empty_historical(self):
        """Test merging when historical messages are empty."""
        converter = _create_converter()

        historical = []
        current = [
            HumanMessage(content="Current message"),
        ]

        result = converter._merge_messages_without_duplicates(historical, current, "conv_123")

        assert len(result) == 1
        assert result[0].content == "Current message"

    def test_merge_different_types_not_duplicates(self):
        """Test that messages with same content but different types are not considered duplicates."""
        converter = _create_converter()

        historical = [
            SystemMessage(content="Same content"),  # System message
        ]
        current = [
            HumanMessage(content="Same content"),  # Human message with same content
        ]

        result = converter._merge_messages_without_duplicates(historical, current, "conv_123")

        # Both should be kept because types are different
        assert len(result) == 2


@pytest.mark.unit
class TestFilterIncompleteToolCalls:
    """Tests for the _filter_incomplete_tool_calls method."""

    def test_filter_complete_tool_call_sequence(self):
        """Test that complete tool call sequences are preserved and reordered correctly."""
        converter = _create_converter()

        messages = [
            HumanMessage(content="What's the weather?"),
            AIMessage(content="", tool_calls=[{"id": "call_1", "name": "get_weather", "args": {}}]),
            ToolMessage(content="Sunny", tool_call_id="call_1"),
            AIMessage(content="The weather is sunny."),
        ]

        result = converter._filter_incomplete_tool_calls(messages)

        assert len(result) == 4
        assert isinstance(result[0], HumanMessage)
        assert isinstance(result[1], AIMessage)
        assert result[1].tool_calls is not None
        assert isinstance(result[2], ToolMessage)
        assert isinstance(result[3], AIMessage)

    def test_filter_incomplete_tool_call_removed(self):
        """Test that AIMessage with tool_calls without responses is removed."""
        converter = _create_converter()

        messages = [
            HumanMessage(content="What's the weather?"),
            AIMessage(content="", tool_calls=[{"id": "call_1", "name": "get_weather", "args": {}}]),
            # Missing ToolMessage for call_1
            AIMessage(content="Let me try again."),
        ]

        result = converter._filter_incomplete_tool_calls(messages)

        assert len(result) == 2
        assert isinstance(result[0], HumanMessage)
        assert isinstance(result[1], AIMessage)
        assert result[1].content == "Let me try again."

    def test_filter_reorders_tool_messages_after_ai_message(self):
        """Test that ToolMessages are placed immediately after their AIMessage."""
        converter = _create_converter()

        # Simulate out-of-order messages (tool response before tool call)
        messages = [
            HumanMessage(content="Query"),
            ToolMessage(content="Result", tool_call_id="call_1"),  # Out of order
            AIMessage(content="", tool_calls=[{"id": "call_1", "name": "search", "args": {}}]),
        ]

        result = converter._filter_incomplete_tool_calls(messages)

        assert len(result) == 3
        assert isinstance(result[0], HumanMessage)
        assert isinstance(result[1], AIMessage)
        assert result[1].tool_calls is not None
        assert isinstance(result[2], ToolMessage)
        assert result[2].tool_call_id == "call_1"

    def test_filter_multiple_tool_calls_in_one_message(self):
        """Test handling of multiple tool calls in a single AIMessage."""
        converter = _create_converter()

        messages = [
            AIMessage(content="", tool_calls=[
                {"id": "call_1", "name": "tool_a", "args": {}},
                {"id": "call_2", "name": "tool_b", "args": {}},
            ]),
            ToolMessage(content="Result A", tool_call_id="call_1"),
            ToolMessage(content="Result B", tool_call_id="call_2"),
        ]

        result = converter._filter_incomplete_tool_calls(messages)

        assert len(result) == 3
        assert isinstance(result[0], AIMessage)
        assert isinstance(result[1], ToolMessage)
        assert result[1].tool_call_id == "call_1"
        assert isinstance(result[2], ToolMessage)
        assert result[2].tool_call_id == "call_2"

    def test_filter_partial_tool_calls_removed(self):
        """Test that AIMessage with multiple tool_calls is removed if any response is missing."""
        converter = _create_converter()

        messages = [
            AIMessage(content="", tool_calls=[
                {"id": "call_1", "name": "tool_a", "args": {}},
                {"id": "call_2", "name": "tool_b", "args": {}},
            ]),
            ToolMessage(content="Result A", tool_call_id="call_1"),
            # Missing ToolMessage for call_2
        ]

        result = converter._filter_incomplete_tool_calls(messages)

        # The AIMessage should be removed because call_2 has no response
        assert len(result) == 0

    def test_filter_no_tool_calls_unchanged(self):
        """Test that messages without tool calls pass through unchanged."""
        converter = _create_converter()

        messages = [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there!"),
            HumanMessage(content="How are you?"),
            AIMessage(content="I'm doing well."),
        ]

        result = converter._filter_incomplete_tool_calls(messages)

        assert len(result) == 4
        assert result[0].content == "Hello"
        assert result[1].content == "Hi there!"
        assert result[2].content == "How are you?"
        assert result[3].content == "I'm doing well."

    def test_filter_empty_messages(self):
        """Test filtering an empty message list."""
        converter = _create_converter()

        result = converter._filter_incomplete_tool_calls([])

        assert result == []

    def test_filter_duplicate_tool_call_ids_in_history(self):
        """Test that duplicate AIMessages with same tool_call_id each get their ToolMessage."""
        converter = _create_converter()

        # Historical items may have duplicate tool calls (same call_id appearing twice)
        # This happens when conversation history is saved multiple times
        messages = [
            HumanMessage(content="Calculate 2+2"),
            AIMessage(
                content="",
                tool_calls=[{"id": "call_same", "name": "add", "args": {"a": 2, "b": 2}}],
            ),
            ToolMessage(content="4", tool_call_id="call_same"),
            AIMessage(content="The answer is 4"),
            HumanMessage(content="Calculate 3+3"),
            # Same tool_call_id appears again (duplicate from history)
            AIMessage(
                content="",
                tool_calls=[{"id": "call_same", "name": "add", "args": {"a": 3, "b": 3}}],
            ),
            ToolMessage(content="6", tool_call_id="call_same"),
            AIMessage(content="The answer is 6"),
        ]

        result = converter._filter_incomplete_tool_calls(messages)

        # Both AIMessages with tool_calls should have their ToolMessage following them
        assert len(result) == 8
        # First tool call sequence
        assert isinstance(result[1], AIMessage)
        assert result[1].tool_calls[0]["id"] == "call_same"
        assert isinstance(result[2], ToolMessage)
        assert result[2].tool_call_id == "call_same"
        # Second tool call sequence (same call_id, should still get ToolMessage)
        assert isinstance(result[5], AIMessage)
        assert result[5].tool_calls[0]["id"] == "call_same"
        assert isinstance(result[6], ToolMessage)
        assert result[6].tool_call_id == "call_same"


@pytest.mark.unit
class TestFetchHistoricalItems:
    """Tests for the _fetch_historical_items method using AsyncOpenAI."""

    @pytest.mark.asyncio
    async def test_fetch_returns_empty_when_no_endpoint(self):
        """Test that fetch returns empty list when no project endpoint is configured."""
        converter = _create_converter()

        with patch(
            "azure.ai.agentserver.langgraph.models.response_api_default_converter.get_project_endpoint",
            return_value=None,
        ):
            result = await converter._fetch_historical_items("conv_123")
            assert result == []

    @pytest.mark.asyncio
    async def test_fetch_returns_empty_on_import_error(self):
        """Test that fetch returns empty list when openai is not available."""
        converter = _create_converter()

        with patch(
            "azure.ai.agentserver.langgraph.models.response_api_default_converter.get_project_endpoint",
            return_value="https://test.endpoint.com",
        ):
            with patch.dict("sys.modules", {"openai": None}):
                # This should handle ImportError gracefully
                result = await converter._fetch_historical_items("conv_123")
                assert result == []

    @pytest.mark.asyncio
    async def test_fetch_converts_items_to_messages(self):
        """Test that fetched items are converted to LangGraph messages."""
        converter = _create_converter()

        # Create mock items
        mock_item = MagicMock()
        mock_item.model_dump = MagicMock(return_value={
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": "Hello"}],
        })

        async def mock_list(*args, **kwargs):
            yield mock_item

        mock_client = MagicMock()
        mock_client.conversations.items.list = mock_list

        with patch(
            "azure.ai.agentserver.langgraph.models.response_api_default_converter.get_project_endpoint",
            return_value="https://test.endpoint.com",
        ):
            with patch(
                "openai.AsyncOpenAI",
                return_value=mock_client,
            ):
                with patch(
                    "azure.identity.aio.DefaultAzureCredential",
                ) as mock_cred:
                    mock_cred_instance = MagicMock()
                    mock_cred.return_value = mock_cred_instance
                    mock_cred_instance.__aenter__ = AsyncMock(return_value=mock_cred_instance)
                    mock_cred_instance.__aexit__ = AsyncMock(return_value=None)

                    with patch(
                        "azure.identity.aio.get_bearer_token_provider",
                    ) as mock_token_provider:
                        mock_token_fn = MagicMock(return_value="test_token")
                        mock_token_provider.return_value = mock_token_fn

                        result = await converter._fetch_historical_items("conv_123")

                        assert len(result) == 1
                        assert isinstance(result[0], HumanMessage)
                        assert result[0].content == "Hello"


@pytest.mark.unit
class TestMergeAndFilterIntegration:
    """Tests for the integration of merge and filter operations in _get_input."""

    def test_filter_after_merge_catches_broken_sequences(self):
        """Test that filter runs after merge to catch sequences broken by deduplication."""
        converter = _create_converter()

        # Historical ends with AIMessage with tool_calls followed by ToolMessage
        # Current has the same ToolMessage (duplicate)
        historical = [
            HumanMessage(content="Calculate 2+2"),
            AIMessage(
                content="",
                tool_calls=[{"id": "call_123", "name": "add", "args": {"a": 2, "b": 2}}],
            ),
            ToolMessage(content="4", tool_call_id="call_123"),
        ]
        current = [
            ToolMessage(content="4", tool_call_id="call_123"),  # Same as last historical
        ]

        # After merge, the ToolMessage should be deduplicated
        merged = converter._merge_messages_without_duplicates(historical, current, "conv_123")
        # Historical would be [Human, AI], current is [ToolMessage(same)]
        # Dedup removes last 1 from historical: [Human, AI]
        # Then adds current: [Human, AI, ToolMessage]

        # But if dedup matched by content only (not tool_call_id), it might incorrectly match
        # In this case, let's verify the filter would catch any broken sequences
        filtered = converter._filter_incomplete_tool_calls(merged)

        # The result should have a complete sequence or remove the incomplete AIMessage
        for i, msg in enumerate(filtered):
            if isinstance(msg, AIMessage) and hasattr(msg, 'tool_calls') and msg.tool_calls:
                # Every AIMessage with tool_calls should be followed by its ToolMessages
                tool_call_ids = [
                    tc.get('id') if isinstance(tc, dict) else getattr(tc, 'id', None)
                    for tc in msg.tool_calls
                ]
                # Check that all tool_call_ids have corresponding ToolMessages in the result
                tool_responses = {
                    m.tool_call_id for m in filtered if isinstance(m, ToolMessage)
                }
                for tc_id in tool_call_ids:
                    assert tc_id in tool_responses, f"Tool call {tc_id} has no response"

    def test_filter_removes_orphaned_ai_message_after_dedup(self):
        """Test that an AIMessage with tool_calls is removed if its ToolMessage was deduplicated away."""
        converter = _create_converter()

        # Simulate a scenario where dedup incorrectly removes the ToolMessage
        # by testing the filter directly on a broken sequence
        broken_sequence = [
            HumanMessage(content="Calculate 2+2"),
            AIMessage(
                content="",
                tool_calls=[{"id": "call_orphan", "name": "add", "args": {"a": 2, "b": 2}}],
            ),
            # ToolMessage is missing!
        ]

        filtered = converter._filter_incomplete_tool_calls(broken_sequence)

        # The AIMessage with incomplete tool_calls should be removed
        assert len(filtered) == 1
        assert isinstance(filtered[0], HumanMessage)
        assert filtered[0].content == "Calculate 2+2"
