"""Unit tests for CSV conversation input handling."""
import pytest

from azure.ai.evaluation._evaluators._common._base_eval import EvaluatorBase
from azure.ai.evaluation._exceptions import EvaluationException


class MockEvaluator(EvaluatorBase):
    """Mock evaluator for testing conversation parsing."""
    
    def __init__(self):
        super().__init__(eval_last_turn=False)
    
    async def _do_eval(self, eval_input):
        """Mock evaluation."""
        return {"score": 1.0}


@pytest.mark.unittest
class TestCSVConversationParsing:
    """Tests for handling conversation input from CSV files."""
    
    def test_conversation_string_is_parsed_as_json(self):
        """Test that conversation strings from CSV are properly parsed to dict."""
        evaluator = MockEvaluator()
        
        # Simulate conversation as a JSON string (as loaded from CSV)
        conversation_str = '{"messages": [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi"}]}'
        
        # This should parse the string and process it without error
        result = evaluator._convert_kwargs_to_eval_input(conversation=conversation_str)
        
        # Verify it returns a result (not raising an error)
        assert result is not None
        assert isinstance(result, list)
    
    def test_conversation_dict_still_works(self):
        """Test that conversation as dict (normal case) still works."""
        evaluator = MockEvaluator()
        
        # Normal conversation as dict
        conversation_dict = {
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi"}
            ]
        }
        
        # This should process without error
        result = evaluator._convert_kwargs_to_eval_input(conversation=conversation_dict)
        
        # Verify it returns a result
        assert result is not None
        assert isinstance(result, list)
    
    def test_invalid_json_string_raises_error(self):
        """Test that invalid JSON string raises appropriate error."""
        evaluator = MockEvaluator()
        
        # Invalid JSON string
        invalid_json = '{"messages": invalid json}'
        
        # Should raise EvaluationException with helpful message
        with pytest.raises(EvaluationException) as exc_info:
            evaluator._convert_kwargs_to_eval_input(conversation=invalid_json)
        
        # Verify error message mentions JSON and CSV
        error_msg = str(exc_info.value)
        assert "JSON" in error_msg
        assert "CSV" in error_msg
    
    def test_is_multi_modal_conversation_with_string_returns_false(self):
        """Test that _is_multi_modal_conversation properly handles string input."""
        evaluator = MockEvaluator()
        
        # String that contains "messages" substring (the bug scenario)
        conversation_str = '{"messages": [{"role": "user", "content": "Hello"}]}'
        
        # Should return False because it's a string, not a dict
        result = evaluator._is_multi_modal_conversation(conversation_str)
        
        assert result is False
    
    def test_is_multi_modal_conversation_with_dict_checks_properly(self):
        """Test that _is_multi_modal_conversation works with dict input."""
        evaluator = MockEvaluator()
        
        # Regular conversation dict (non-multimodal)
        conversation_dict = {
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi"}
            ]
        }
        
        # Should return False for non-multimodal conversation
        result = evaluator._is_multi_modal_conversation(conversation_dict)
        
        assert result is False
    
    def test_is_multi_modal_conversation_with_image_returns_true(self):
        """Test that _is_multi_modal_conversation detects multimodal content."""
        evaluator = MockEvaluator()
        
        # Multimodal conversation with image
        conversation_dict = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What's in this image?"},
                        {"type": "image_url", "image_url": {"url": "http://example.com/image.jpg"}}
                    ]
                }
            ]
        }
        
        # Should return True for multimodal conversation
        result = evaluator._is_multi_modal_conversation(conversation_dict)
        
        assert result is True
