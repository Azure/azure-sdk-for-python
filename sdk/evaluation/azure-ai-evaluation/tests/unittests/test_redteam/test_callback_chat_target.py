"""
Unit tests for callback_chat_target module.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

try:
    import pyrit
    has_pyrit = True
except ImportError:
    has_pyrit = False

if has_pyrit:   
    from pyrit.common import initialize_pyrit, IN_MEMORY

    from azure.ai.evaluation.red_team._callback_chat_target import _CallbackChatTarget

    initialize_pyrit(memory_db_type=IN_MEMORY)

@pytest.fixture(scope="function")
def mock_callback():
    """Mock callback for tests."""
    return AsyncMock(
        return_value={
            "messages": [
                {"role": "user", "content": "test prompt"},
                {"role": "assistant", "content": "test response"}
            ],
            "stream": False,
            "session_state": None,
            "context": {}
        }
    )


@pytest.fixture(scope="function")
def chat_target(mock_callback):
    """Create a _CallbackChatTarget instance for tests."""
    return _CallbackChatTarget(callback=mock_callback)


@pytest.fixture(scope="function")
def mock_request():
    """Create a mocked request object that mimics PromptRequestResponse from pyrit."""
    request_piece = MagicMock()
    request_piece.conversation_id = "test-id"
    request_piece.converted_value = "test prompt"
    request_piece.converted_value_data_type = "text"
    request_piece.to_chat_message.return_value = MagicMock(
        role="user", content="test prompt"
    )
    
    request = MagicMock()
    request.request_pieces = [request_piece]
    request.response_pieces = []
    
    # Mock the constructor pattern used by _CallbackChatTarget
    response_piece = MagicMock()
    request.from_response = MagicMock(return_value=request)
    return request


@pytest.mark.unittest
@pytest.mark.skipif(not has_pyrit, reason="redteam extra is not installed")
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
@pytest.mark.skipif(not has_pyrit, reason="redteam extra is not installed")
class TestCallbackChatTargetPrompts:
    """Test _CallbackChatTarget prompt handling."""
    
    @pytest.mark.asyncio
    async def test_send_prompt_async(self, chat_target, mock_request, mock_callback):
        """Test send_prompt_async method."""
        with patch.object(chat_target, "_memory") as mock_memory, \
            patch("azure.ai.evaluation.red_team._callback_chat_target.construct_response_from_request") as mock_construct:
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
            assert call_args["context"] is None
            
            # Check memory usage
            mock_memory.get_chat_messages_with_conversation_id.assert_called_once_with(
                conversation_id="test-id"
            )

    def test_validate_request_multiple_pieces(self, chat_target):
        """Test _validate_request with multiple request pieces."""
        mock_req = MagicMock()
        mock_req.request_pieces = [MagicMock(), MagicMock()]  # Two pieces
        
        with pytest.raises(ValueError) as excinfo:
            chat_target._validate_request(prompt_request=mock_req)
        
        assert "only supports a single prompt request piece" in str(excinfo.value)

    def test_validate_request_non_text_type(self, chat_target):
        """Test _validate_request with non-text data type."""
        mock_req = MagicMock()
        mock_piece = MagicMock()
        mock_piece.converted_value_data_type = "image"  # Not text
        mock_req.request_pieces = [mock_piece]
        
        with pytest.raises(ValueError) as excinfo:
            chat_target._validate_request(prompt_request=mock_req)
        
        assert "only supports text prompt input" in str(excinfo.value)


@pytest.mark.unittest
@pytest.mark.skipif(not has_pyrit, reason="redteam extra is not installed")
class TestCallbackChatTargetFeatures:
    """Test _CallbackChatTarget feature support."""

    def test_is_json_response_supported(self, chat_target):
        """Test is_json_response_supported method."""
        assert chat_target.is_json_response_supported() is False