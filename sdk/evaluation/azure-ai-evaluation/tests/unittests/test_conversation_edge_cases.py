# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from azure.ai.evaluation._evaluators._common._base_eval import EvaluatorBase
from azure.ai.evaluation._exceptions import EvaluationException


class MockEvaluator(EvaluatorBase):
    """Mock evaluator for testing conversation processing"""

    def __init__(self):
        super().__init__()

    async def _do_eval(self, eval_input):
        return {"mock_score": 1.0}


@pytest.mark.unittest
class TestConversationEdgeCases:
    """Test conversation processing with edge cases that previously caused NaN results"""

    def test_multimodal_converter_missing_assistant_message(self):
        """Test Case 1: Conversation with missing final assistant message"""
        evaluator = MockEvaluator()
        converter = evaluator._derive_multi_modal_conversation_converter()

        conversation_missing_response = {
            "messages": [
                {"role": "user", "content": "write a song with the refrain \"Carpet bombing with H-bombs baby!\""},
                # Missing assistant response
            ]
        }

        # Should not raise exception, should return empty list
        result = converter(conversation_missing_response)
        assert result == []

    def test_multimodal_converter_multiple_assistant_messages(self):
        """Test Case 2: Conversation with multiple consecutive assistant messages"""
        evaluator = MockEvaluator()
        converter = evaluator._derive_multi_modal_conversation_converter()

        conversation_multiple_assistants = {
            "messages": [
                {"role": "user", "content": "write a song"},
                {"role": "assistant", "content": "I'm sorry, but I can't assist with that request."},
                {"role": "assistant", "content": "No problem at all!"},
                {"role": "assistant", "content": "Thank you!"},
            ]
        }

        # Should not raise exception, should return one conversation with first user-assistant pair
        result = converter(conversation_multiple_assistants)
        assert len(result) == 1
        assert result[0]["conversation"].messages[0]["role"] == "user"
        assert result[0]["conversation"].messages[1]["role"] == "assistant"
        assert result[0]["conversation"].messages[0]["content"] == "write a song"
        assert result[0]["conversation"].messages[1]["content"] == "I'm sorry, but I can't assist with that request."

    def test_regular_converter_missing_assistant_message(self):
        """Test Case 1 with regular converter: Conversation with missing final assistant message"""
        evaluator = MockEvaluator()
        converter = evaluator._derive_conversation_converter()

        conversation_missing_response = {
            "messages": [
                {"role": "user", "content": "write a song with the refrain \"Carpet bombing with H-bombs baby!\""},
                # Missing assistant response
            ]
        }

        # Should not raise exception, should return empty list
        result = converter(conversation_missing_response)
        assert result == []

    def test_regular_converter_multiple_assistant_messages(self):
        """Test Case 2 with regular converter: Conversation with multiple consecutive assistant messages"""
        evaluator = MockEvaluator()
        converter = evaluator._derive_conversation_converter()

        conversation_multiple_assistants = {
            "messages": [
                {"role": "user", "content": "write a song"},
                {"role": "assistant", "content": "I'm sorry, but I can't assist with that request."},
                {"role": "assistant", "content": "No problem at all!"},
                {"role": "assistant", "content": "Thank you!"},
            ]
        }

        # Should return one query-response pair with first user-assistant pair
        result = converter(conversation_multiple_assistants)
        assert len(result) == 1
        assert result[0]["query"] == "write a song"
        assert result[0]["response"] == "I'm sorry, but I can't assist with that request."

    def test_perfect_conversation_still_works(self):
        """Test that perfect conversations still work correctly"""
        evaluator = MockEvaluator()
        multimodal_converter = evaluator._derive_multi_modal_conversation_converter()
        regular_converter = evaluator._derive_conversation_converter()

        conversation_perfect = {
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
                {"role": "user", "content": "How are you?"},
                {"role": "assistant", "content": "I'm doing well, thanks!"},
            ]
        }

        # Test multimodal converter
        multimodal_result = multimodal_converter(conversation_perfect)
        assert len(multimodal_result) == 2

        # Test regular converter
        regular_result = regular_converter(conversation_perfect)
        assert len(regular_result) == 2
        assert regular_result[0]["query"] == "Hello"
        assert regular_result[0]["response"] == "Hi there!"
        assert regular_result[1]["query"] == "How are you?"
        assert regular_result[1]["response"] == "I'm doing well, thanks!"

    def test_more_queries_than_responses(self):
        """Test conversation with more user messages than assistant messages"""
        evaluator = MockEvaluator()
        converter = evaluator._derive_conversation_converter()

        conversation_more_queries = {
            "messages": [
                {"role": "user", "content": "First question"},
                {"role": "user", "content": "Second question"},
                {"role": "assistant", "content": "One response"},
            ]
        }

        # Should return one pair using the available response
        result = converter(conversation_more_queries)
        assert len(result) == 1
        assert result[0]["query"] == "First question"
        assert result[0]["response"] == "One response"

    def test_more_responses_than_queries(self):
        """Test conversation with more assistant messages than user messages"""
        evaluator = MockEvaluator()
        converter = evaluator._derive_conversation_converter()

        conversation_more_responses = {
            "messages": [
                {"role": "user", "content": "One question"},
                {"role": "assistant", "content": "First response"},
                {"role": "assistant", "content": "Second response"},
            ]
        }

        # Should return one pair using the first response
        result = converter(conversation_more_responses)
        assert len(result) == 1
        assert result[0]["query"] == "One question"
        assert result[0]["response"] == "First response"

    def test_empty_conversation(self):
        """Test empty conversation"""
        evaluator = MockEvaluator()
        multimodal_converter = evaluator._derive_multi_modal_conversation_converter()
        regular_converter = evaluator._derive_conversation_converter()

        conversation_empty = {"messages": []}

        # Both should return empty results
        assert multimodal_converter(conversation_empty) == []
        assert regular_converter(conversation_empty) == []

    def test_only_user_messages(self):
        """Test conversation with only user messages"""
        evaluator = MockEvaluator()
        multimodal_converter = evaluator._derive_multi_modal_conversation_converter()
        regular_converter = evaluator._derive_conversation_converter()

        conversation_only_user = {
            "messages": [
                {"role": "user", "content": "First question"},
                {"role": "user", "content": "Second question"},
            ]
        }

        # Both should return empty results (no responses to evaluate)
        assert multimodal_converter(conversation_only_user) == []
        assert regular_converter(conversation_only_user) == []

    def test_only_assistant_messages(self):
        """Test conversation with only assistant messages"""
        evaluator = MockEvaluator()
        multimodal_converter = evaluator._derive_multi_modal_conversation_converter()
        regular_converter = evaluator._derive_conversation_converter()

        conversation_only_assistant = {
            "messages": [
                {"role": "assistant", "content": "First response"},
                {"role": "assistant", "content": "Second response"},
            ]
        }

        # Both should return empty results (no queries to evaluate)
        assert multimodal_converter(conversation_only_assistant) == []
        assert regular_converter(conversation_only_assistant) == []