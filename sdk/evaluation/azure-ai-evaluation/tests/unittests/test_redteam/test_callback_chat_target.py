"""
Unit tests for callback_chat_target module.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
import os

from openai import RateLimitError as OpenAIRateLimitError
from pyrit.exceptions import EmptyResponseException, RateLimitException
from pyrit.memory import CentralMemory, SQLiteMemory

from azure.ai.evaluation.red_team._callback_chat_target import _CallbackChatTarget

# Initialize PyRIT with in-memory database
CentralMemory.set_memory_instance(SQLiteMemory(db_path=":memory:"))


@pytest.fixture(scope="function")
def mock_callback():
    """Mock callback for tests."""
    return AsyncMock(
        return_value={
            "messages": [{"role": "user", "content": "test prompt"}, {"role": "assistant", "content": "test response"}],
            "stream": False,
            "session_state": None,
            "context": {},
        }
    )


@pytest.fixture(scope="function")
def chat_target(mock_callback):
    """Create a _CallbackChatTarget instance for tests."""
    return _CallbackChatTarget(callback=mock_callback)


@pytest.fixture(scope="function")
def mock_request():
    """Create a mocked request object that mimics Message from pyrit."""
    request_piece = MagicMock()
    request_piece.conversation_id = "test-id"
    request_piece.converted_value = "test prompt"
    request_piece.converted_value_data_type = "text"
    request_piece.to_chat_message.return_value = MagicMock(role="user", content="test prompt")
    request_piece.labels.get.return_value = None

    request = MagicMock()
    request.message_pieces = [request_piece]
    request.get_piece = MagicMock(side_effect=lambda i: request.message_pieces[i])

    # Mock the constructor pattern used by _CallbackChatTarget
    response_piece = MagicMock()
    request.from_response = MagicMock(return_value=request)
    return request


@pytest.mark.unittest
class TestCallbackChatTargetInitialization:
    """Test the initialization of _CallbackChatTarget."""

    def test_init(self, mock_callback):
        """Test the initialization of _CallbackChatTarget."""
        target = _CallbackChatTarget(callback=mock_callback)

        assert target._callback == mock_callback
        assert target._stream is False

        # Test with stream=True
        target_with_stream = _CallbackChatTarget(callback=mock_callback, stream=True)
        assert target_with_stream._stream is True


@pytest.mark.unittest
class TestCallbackChatTargetPrompts:
    """Test _CallbackChatTarget prompt handling."""

    @pytest.mark.asyncio
    async def test_send_prompt_async(self, chat_target, mock_request, mock_callback):
        """Test send_prompt_async method."""
        with patch.object(chat_target, "_memory") as mock_memory, patch(
            "azure.ai.evaluation.red_team._callback_chat_target.construct_response_from_request"
        ) as mock_construct:
            # Setup memory mock
            mock_memory.get_chat_messages_with_conversation_id.return_value = []

            # Setup construct_response mock
            mock_construct.return_value = mock_request

            # Call the method
            response = await chat_target.send_prompt_async(prompt_request=mock_request)

            # Check that callback was called with correct parameters
            mock_callback.assert_called_once()
            call_args = mock_callback.call_args[1]
            assert call_args["stream"] is False
            assert call_args["session_state"] is None
            assert call_args["context"] == {}

            # Check memory usage
            mock_memory.get_chat_messages_with_conversation_id.assert_called_once_with(conversation_id="test-id")

    @pytest.mark.asyncio
    async def test_send_prompt_async_with_context_from_labels(self, chat_target, mock_callback):
        """Test send_prompt_async method with context from request labels."""
        # Create a request with context in labels
        request_piece = MagicMock()
        request_piece.conversation_id = "test-id"
        request_piece.converted_value = "test prompt"
        request_piece.converted_value_data_type = "text"
        request_piece.to_chat_message.return_value = MagicMock(role="user", content="test prompt")
        request_piece.labels = {"context": {"contexts": ["test context data"]}}

        mock_request = MagicMock()
        mock_request.message_pieces = [request_piece]
        mock_request.get_piece = MagicMock(side_effect=lambda i: mock_request.message_pieces[i])

        with patch.object(chat_target, "_memory") as mock_memory, patch(
            "azure.ai.evaluation.red_team._callback_chat_target.construct_response_from_request"
        ) as mock_construct:
            # Setup memory mock
            mock_memory.get_chat_messages_with_conversation_id.return_value = []

            # Setup construct_response mock
            mock_construct.return_value = mock_request

            # Call the method
            response = await chat_target.send_prompt_async(prompt_request=mock_request)

            # Check that callback was called with correct parameters including context from labels
            mock_callback.assert_called_once()
            call_args = mock_callback.call_args[1]
            assert call_args["stream"] is False
            assert call_args["session_state"] is None
            assert call_args["context"] == {"contexts": ["test context data"]}

            # Check memory usage
            mock_memory.get_chat_messages_with_conversation_id.assert_called_once_with(conversation_id="test-id")

    def test_validate_request_multiple_pieces(self, chat_target):
        """Test _validate_request with multiple request pieces."""
        mock_req = MagicMock()
        mock_req.message_pieces = [MagicMock(), MagicMock()]  # Two pieces

        with pytest.raises(ValueError) as excinfo:
            chat_target._validate_request(prompt_request=mock_req)

        assert "only supports a single prompt request piece" in str(excinfo.value)

    def test_validate_request_non_text_type(self, chat_target):
        """Test _validate_request with non-text data type."""
        mock_req = MagicMock()
        mock_piece = MagicMock()
        mock_piece.converted_value_data_type = "image"  # Not text
        mock_req.message_pieces = [mock_piece]
        mock_req.get_piece = MagicMock(side_effect=lambda i: mock_req.message_pieces[i])

        with pytest.raises(ValueError) as excinfo:
            chat_target._validate_request(prompt_request=mock_req)

        assert "only supports text prompt input" in str(excinfo.value)


@pytest.mark.unittest
class TestCallbackChatTargetFeatures:
    """Test _CallbackChatTarget feature support."""

    def test_is_json_response_supported(self, chat_target):
        """Test is_json_response_supported method."""
        assert chat_target.is_json_response_supported() is False


@pytest.mark.unittest
class TestCallbackChatTargetRetry:
    """Test _CallbackChatTarget retry behavior."""

    def test_init_retry_enabled_default(self, mock_callback):
        """Test that retry_enabled defaults to True."""
        target = _CallbackChatTarget(callback=mock_callback)
        assert target._retry_enabled is True

    def test_init_retry_enabled_false(self, mock_callback):
        """Test that retry_enabled can be set to False."""
        target = _CallbackChatTarget(callback=mock_callback, retry_enabled=False)
        assert target._retry_enabled is False

    @pytest.mark.asyncio
    async def test_rate_limit_exception_translated_from_openai_error(self, mock_callback):
        """Test that OpenAI RateLimitError is translated to RateLimitException."""
        # Create a mock response that looks like an OpenAI rate limit error
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {}

        mock_callback.side_effect = OpenAIRateLimitError(
            "Rate limit exceeded",
            response=mock_response,
            body={"error": {"message": "Rate limit exceeded"}}
        )

        target = _CallbackChatTarget(callback=mock_callback, retry_enabled=False)

        # Create mock request
        request_piece = MagicMock()
        request_piece.conversation_id = "test-id"
        request_piece.converted_value = "test prompt"
        request_piece.converted_value_data_type = "text"
        request_piece.labels = {}

        mock_request = MagicMock()
        mock_request.message_pieces = [request_piece]
        mock_request.get_piece = MagicMock(side_effect=lambda i: mock_request.message_pieces[i])

        with patch.object(target, "_memory") as mock_memory:
            mock_memory.get_conversation.return_value = []

            with pytest.raises(RateLimitException) as exc_info:
                await target.send_prompt_async(message=mock_request)

            assert exc_info.value.status_code == 429
            assert "Rate limit exceeded" in exc_info.value.message

    @pytest.mark.asyncio
    async def test_rate_limit_in_error_message_translated(self, mock_callback):
        """Test that errors with 'rate limit' in message are translated."""
        mock_callback.side_effect = Exception("Request failed: rate limit exceeded for model")

        target = _CallbackChatTarget(callback=mock_callback, retry_enabled=False)

        # Create mock request
        request_piece = MagicMock()
        request_piece.conversation_id = "test-id"
        request_piece.converted_value = "test prompt"
        request_piece.converted_value_data_type = "text"
        request_piece.labels = {}

        mock_request = MagicMock()
        mock_request.message_pieces = [request_piece]
        mock_request.get_piece = MagicMock(side_effect=lambda i: mock_request.message_pieces[i])

        with patch.object(target, "_memory") as mock_memory:
            mock_memory.get_conversation.return_value = []

            with pytest.raises(RateLimitException) as exc_info:
                await target.send_prompt_async(message=mock_request)

            assert exc_info.value.status_code == 429

    @pytest.mark.asyncio
    async def test_429_in_error_message_translated(self, mock_callback):
        """Test that errors with '429' in message are translated."""
        mock_callback.side_effect = Exception("HTTP 429: Too many requests")

        target = _CallbackChatTarget(callback=mock_callback, retry_enabled=False)

        # Create mock request
        request_piece = MagicMock()
        request_piece.conversation_id = "test-id"
        request_piece.converted_value = "test prompt"
        request_piece.converted_value_data_type = "text"
        request_piece.labels = {}

        mock_request = MagicMock()
        mock_request.message_pieces = [request_piece]
        mock_request.get_piece = MagicMock(side_effect=lambda i: mock_request.message_pieces[i])

        with patch.object(target, "_memory") as mock_memory:
            mock_memory.get_conversation.return_value = []

            with pytest.raises(RateLimitException) as exc_info:
                await target.send_prompt_async(message=mock_request)

            assert exc_info.value.status_code == 429

    @pytest.mark.asyncio
    async def test_empty_response_raises_exception(self, mock_callback):
        """Test that empty callback response raises EmptyResponseException."""
        mock_callback.return_value = {
            "messages": [{"role": "assistant", "content": ""}],
            "stream": False,
            "session_state": None,
            "context": {},
        }

        target = _CallbackChatTarget(callback=mock_callback, retry_enabled=False)

        # Create mock request
        request_piece = MagicMock()
        request_piece.conversation_id = "test-id"
        request_piece.converted_value = "test prompt"
        request_piece.converted_value_data_type = "text"
        request_piece.labels = {}

        mock_request = MagicMock()
        mock_request.message_pieces = [request_piece]
        mock_request.get_piece = MagicMock(side_effect=lambda i: mock_request.message_pieces[i])

        with patch.object(target, "_memory") as mock_memory:
            mock_memory.get_conversation.return_value = []

            with pytest.raises(EmptyResponseException) as exc_info:
                await target.send_prompt_async(message=mock_request)

            assert "empty response" in exc_info.value.message.lower()

    @pytest.mark.asyncio
    async def test_whitespace_only_response_raises_exception(self, mock_callback):
        """Test that whitespace-only callback response raises EmptyResponseException."""
        mock_callback.return_value = {
            "messages": [{"role": "assistant", "content": "   \n\t  "}],
            "stream": False,
            "session_state": None,
            "context": {},
        }

        target = _CallbackChatTarget(callback=mock_callback, retry_enabled=False)

        # Create mock request
        request_piece = MagicMock()
        request_piece.conversation_id = "test-id"
        request_piece.converted_value = "test prompt"
        request_piece.converted_value_data_type = "text"
        request_piece.labels = {}

        mock_request = MagicMock()
        mock_request.message_pieces = [request_piece]
        mock_request.get_piece = MagicMock(side_effect=lambda i: mock_request.message_pieces[i])

        with patch.object(target, "_memory") as mock_memory:
            mock_memory.get_conversation.return_value = []

            with pytest.raises(EmptyResponseException):
                await target.send_prompt_async(message=mock_request)

    @pytest.mark.asyncio
    async def test_non_rate_limit_error_not_translated(self, mock_callback):
        """Test that non-rate-limit errors are not translated."""
        mock_callback.side_effect = ValueError("Some other error")

        target = _CallbackChatTarget(callback=mock_callback, retry_enabled=False)

        # Create mock request
        request_piece = MagicMock()
        request_piece.conversation_id = "test-id"
        request_piece.converted_value = "test prompt"
        request_piece.converted_value_data_type = "text"
        request_piece.labels = {}

        mock_request = MagicMock()
        mock_request.message_pieces = [request_piece]
        mock_request.get_piece = MagicMock(side_effect=lambda i: mock_request.message_pieces[i])

        with patch.object(target, "_memory") as mock_memory:
            mock_memory.get_conversation.return_value = []

            with pytest.raises(ValueError) as exc_info:
                await target.send_prompt_async(message=mock_request)

            assert "Some other error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_retry_enabled_uses_retry_wrapper(self, mock_callback):
        """Test that retry_enabled=True uses the retry wrapper method."""
        mock_callback.return_value = {
            "messages": [{"role": "assistant", "content": "test response"}],
            "stream": False,
            "session_state": None,
            "context": {},
        }

        target = _CallbackChatTarget(callback=mock_callback, retry_enabled=True)

        # Create mock request
        request_piece = MagicMock()
        request_piece.conversation_id = "test-id"
        request_piece.converted_value = "test prompt"
        request_piece.converted_value_data_type = "text"
        request_piece.labels = {}

        mock_request = MagicMock()
        mock_request.message_pieces = [request_piece]
        mock_request.get_piece = MagicMock(side_effect=lambda i: mock_request.message_pieces[i])

        with patch.object(target, "_memory") as mock_memory, patch(
            "azure.ai.evaluation.red_team._callback_chat_target.construct_response_from_request"
        ) as mock_construct:
            mock_memory.get_conversation.return_value = []
            mock_construct.return_value = mock_request

            # Spy on _send_prompt_with_retry
            with patch.object(target, "_send_prompt_with_retry", wraps=target._send_prompt_with_retry) as mock_retry:
                await target.send_prompt_async(message=mock_request)
                mock_retry.assert_called_once()

    @pytest.mark.asyncio
    async def test_retry_disabled_bypasses_retry_wrapper(self, mock_callback):
        """Test that retry_enabled=False bypasses the retry wrapper method."""
        mock_callback.return_value = {
            "messages": [{"role": "assistant", "content": "test response"}],
            "stream": False,
            "session_state": None,
            "context": {},
        }

        target = _CallbackChatTarget(callback=mock_callback, retry_enabled=False)

        # Create mock request
        request_piece = MagicMock()
        request_piece.conversation_id = "test-id"
        request_piece.converted_value = "test prompt"
        request_piece.converted_value_data_type = "text"
        request_piece.labels = {}

        mock_request = MagicMock()
        mock_request.message_pieces = [request_piece]
        mock_request.get_piece = MagicMock(side_effect=lambda i: mock_request.message_pieces[i])

        with patch.object(target, "_memory") as mock_memory, patch(
            "azure.ai.evaluation.red_team._callback_chat_target.construct_response_from_request"
        ) as mock_construct:
            mock_memory.get_conversation.return_value = []
            mock_construct.return_value = mock_request

            # Spy on both methods
            with patch.object(target, "_send_prompt_with_retry", wraps=target._send_prompt_with_retry) as mock_retry, \
                 patch.object(target, "_send_prompt_impl", wraps=target._send_prompt_impl) as mock_impl:
                await target.send_prompt_async(message=mock_request)
                mock_retry.assert_not_called()
                mock_impl.assert_called_once()

    @pytest.mark.asyncio
    async def test_retry_on_rate_limit_exception(self):
        """Test that RateLimitException triggers retry when retry_enabled=True."""
        call_count = 0

        async def failing_then_succeeding_callback(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RateLimitException(status_code=429, message="Rate limit hit")
            return {
                "messages": [{"role": "assistant", "content": "success after retry"}],
                "stream": False,
                "session_state": None,
                "context": {},
            }

        # Set retry config to minimize test time
        os.environ["RETRY_MAX_NUM_ATTEMPTS"] = "5"
        os.environ["RETRY_WAIT_MIN_SECONDS"] = "0"
        os.environ["RETRY_WAIT_MAX_SECONDS"] = "1"

        try:
            target = _CallbackChatTarget(callback=failing_then_succeeding_callback, retry_enabled=True)

            # Create mock request
            request_piece = MagicMock()
            request_piece.conversation_id = "test-id"
            request_piece.converted_value = "test prompt"
            request_piece.converted_value_data_type = "text"
            request_piece.labels = {}

            mock_request = MagicMock()
            mock_request.message_pieces = [request_piece]
            mock_request.get_piece = MagicMock(side_effect=lambda i: mock_request.message_pieces[i])

            with patch.object(target, "_memory") as mock_memory, patch(
                "azure.ai.evaluation.red_team._callback_chat_target.construct_response_from_request"
            ) as mock_construct:
                mock_memory.get_conversation.return_value = []
                mock_construct.return_value = mock_request

                result = await target.send_prompt_async(message=mock_request)

                # Should have retried and succeeded
                assert call_count == 3
                assert result is not None
        finally:
            # Clean up env vars
            os.environ.pop("RETRY_MAX_NUM_ATTEMPTS", None)
            os.environ.pop("RETRY_WAIT_MIN_SECONDS", None)
            os.environ.pop("RETRY_WAIT_MAX_SECONDS", None)
