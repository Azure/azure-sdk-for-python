"""Tests for conversation persistence functionality in FoundryCBAgent."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class MockAgentRunContext:
    """Mock AgentRunContext for testing."""

    def __init__(self, conversation_id=None, store=False, input_items=None):
        self._conversation_id = conversation_id
        self._request = {
            "store": store,
            "input": input_items or [],
        }

    @property
    def conversation_id(self):
        return self._conversation_id

    @property
    def request(self):
        return self._request


class AsyncIteratorMock:
    """Helper class to create an async iterator from a list."""

    def __init__(self, items):
        self.items = items
        self.index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index >= len(self.items):
            raise StopAsyncIteration
        item = self.items[self.index]
        self.index += 1
        return item


def create_mock_agent():
    """Create a mock FoundryCBAgent without calling __init__."""
    from azure.ai.agentserver.core.server.base import FoundryCBAgent

    # Create instance without calling __init__
    agent = object.__new__(FoundryCBAgent)
    agent._project_endpoint = None
    agent.credentials = None
    agent.tracer = None
    agent._port = 8088
    return agent


@pytest.mark.unit
class TestShouldStore:
    """Tests for _should_store method."""

    def test_should_store_returns_true_when_all_conditions_met(self):
        """Test that _should_store returns True when store=True, conversation_id exists, and endpoint exists."""
        agent = create_mock_agent()
        agent._project_endpoint = "https://test.endpoint.com"

        context = MockAgentRunContext(
            conversation_id="conv_123",
            store=True,
        )

        result = agent._should_store(context)
        assert result  # Truthy value when all conditions met

    def test_should_store_returns_false_when_store_is_false(self):
        """Test that _should_store returns False when store=False."""
        agent = create_mock_agent()
        agent._project_endpoint = "https://test.endpoint.com"

        context = MockAgentRunContext(
            conversation_id="conv_123",
            store=False,
        )

        result = agent._should_store(context)
        assert not result  # Falsy value when store=False

    def test_should_store_returns_false_when_no_conversation_id(self):
        """Test that _should_store returns False when conversation_id is None."""
        agent = create_mock_agent()
        agent._project_endpoint = "https://test.endpoint.com"

        context = MockAgentRunContext(
            conversation_id=None,
            store=True,
        )

        result = agent._should_store(context)
        assert not result  # Falsy value when conversation_id is None

    def test_should_store_returns_false_when_no_endpoint(self):
        """Test that _should_store returns False when project_endpoint is None."""
        agent = create_mock_agent()
        agent._project_endpoint = None

        context = MockAgentRunContext(
            conversation_id="conv_123",
            store=True,
        )

        result = agent._should_store(context)
        assert not result  # Falsy value when endpoint is None


@pytest.mark.unit
class TestItemsAreEqual:
    """Tests for _items_are_equal method."""

    def test_items_equal_with_same_string_content(self):
        """Test items are equal when type, role, and string content match."""
        agent = create_mock_agent()

        item1 = {"type": "message", "role": "user", "content": "Hello"}
        item2 = {"type": "message", "role": "user", "content": "Hello"}

        assert agent._items_are_equal(item1, item2) is True

    def test_items_not_equal_with_different_content(self):
        """Test items are not equal when content differs."""
        agent = create_mock_agent()

        item1 = {"type": "message", "role": "user", "content": "Hello"}
        item2 = {"type": "message", "role": "user", "content": "Goodbye"}

        assert agent._items_are_equal(item1, item2) is False

    def test_items_not_equal_with_different_type(self):
        """Test items are not equal when type differs."""
        agent = create_mock_agent()

        item1 = {"type": "message", "role": "user", "content": "Hello"}
        item2 = {"type": "function_call", "role": "user", "content": "Hello"}

        assert agent._items_are_equal(item1, item2) is False

    def test_items_not_equal_with_different_role(self):
        """Test items are not equal when role differs."""
        agent = create_mock_agent()

        item1 = {"type": "message", "role": "user", "content": "Hello"}
        item2 = {"type": "message", "role": "assistant", "content": "Hello"}

        assert agent._items_are_equal(item1, item2) is False

    def test_items_equal_with_structured_content(self):
        """Test items are equal when structured content text matches."""
        agent = create_mock_agent()

        item1 = {
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": "Hello"}],
        }
        item2 = {
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": "Hello"}],
        }

        assert agent._items_are_equal(item1, item2) is True

    def test_items_not_equal_with_different_structured_content(self):
        """Test items are not equal when structured content text differs."""
        agent = create_mock_agent()

        item1 = {
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": "Hello"}],
        }
        item2 = {
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": "Goodbye"}],
        }

        assert agent._items_are_equal(item1, item2) is False


@pytest.mark.unit
class TestSaveInputToConversation:
    """Tests for _save_input_to_conversation method."""

    @pytest.mark.asyncio
    async def test_save_input_skips_when_no_input_items(self):
        """Test that save is skipped when there are no input items."""
        agent = create_mock_agent()
        agent._project_endpoint = "https://test.endpoint.com"
        agent._create_openai_client = AsyncMock()

        context = MockAgentRunContext(
            conversation_id="conv_123",
            store=True,
            input_items=[],
        )

        await agent._save_input_to_conversation(context)

        # OpenAI client should not be created if no items
        agent._create_openai_client.assert_not_called()

    @pytest.mark.asyncio
    async def test_save_input_converts_string_to_message(self):
        """Test that string input is converted to message format."""
        agent = create_mock_agent()
        agent._project_endpoint = "https://test.endpoint.com"

        mock_client = AsyncMock()
        mock_client.conversations.items.list = MagicMock(return_value=AsyncIteratorMock([]))
        mock_client.conversations.items.create = AsyncMock()
        agent._create_openai_client = AsyncMock(return_value=mock_client)

        context = MockAgentRunContext(
            conversation_id="conv_123",
            store=True,
            input_items=["Hello, world!"],
        )

        await agent._save_input_to_conversation(context)

        mock_client.conversations.items.create.assert_called_once()
        call_args = mock_client.conversations.items.create.call_args
        assert call_args.kwargs["conversation_id"] == "conv_123"
        assert call_args.kwargs["items"][0]["type"] == "message"
        assert call_args.kwargs["items"][0]["role"] == "user"
        assert call_args.kwargs["items"][0]["content"] == "Hello, world!"

    @pytest.mark.asyncio
    async def test_save_input_skips_duplicates(self):
        """Test that save is skipped when input matches last historical items."""
        agent = create_mock_agent()
        agent._project_endpoint = "https://test.endpoint.com"

        # Create mock historical item
        mock_historical_item = MagicMock()
        mock_historical_item.model_dump = MagicMock(return_value={
            "type": "message",
            "role": "user",
            "content": "Hello, world!",
        })

        mock_client = AsyncMock()
        mock_client.conversations.items.list = MagicMock(
            return_value=AsyncIteratorMock([mock_historical_item])
        )
        mock_client.conversations.items.create = AsyncMock()
        agent._create_openai_client = AsyncMock(return_value=mock_client)

        context = MockAgentRunContext(
            conversation_id="conv_123",
            store=True,
            input_items=["Hello, world!"],
        )

        await agent._save_input_to_conversation(context)

        # Create should not be called because input is duplicate
        mock_client.conversations.items.create.assert_not_called()
