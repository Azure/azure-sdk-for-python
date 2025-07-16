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
    """Test conversation processing with edge cases that previously caused NaN results
    
    This test class validates that conversation processing handles edge cases gracefully,
    especially the context handling logic that was restored to fix GroundednessProEvaluator
    regression. The tests ensure that:
    
    1. Mismatched user/assistant message patterns don't cause exceptions
    2. Context is properly structured as expected by service evaluators
    3. Edge cases return empty results instead of NaN
    4. Perfect conversations continue to work correctly
    """

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
        assert result[0]["conversation"]["messages"][0]["role"] == "user"
        assert result[0]["conversation"]["messages"][1]["role"] == "assistant"
        assert result[0]["conversation"]["messages"][0]["content"] == "write a song"
        assert result[0]["conversation"]["messages"][1]["content"] == "I'm sorry, but I can't assist with that request."

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

    def test_context_handling_with_edge_cases(self):
        """Test that context is properly handled in edge cases (matches GroundednessProEvaluator expectations)"""
        
        class MockContextEvaluator(EvaluatorBase):
            """Mock evaluator that requires context for testing"""
            
            def __init__(self):
                super().__init__()
            
            async def _do_eval(self, eval_input):
                return {"mock_score": 1.0}
            
            def __call__(self, *, query=None, response=None, context=None, **kwargs):
                return super().__call__(query=query, response=response, context=context, **kwargs)
        
        evaluator = MockContextEvaluator()
        converter = evaluator._derive_conversation_converter()
        
        # Test with global context and multiple assistant messages
        conversation_with_context = {
            "context": "Global context",
            "messages": [
                {"role": "user", "content": "write a song"},
                {"role": "assistant", "content": "I'm sorry, but I can't assist with that request."},
                {"role": "assistant", "content": "No problem at all!"},
            ]
        }
        
        result = converter(conversation_with_context)
        assert len(result) == 1
        assert "context" in result[0]
        
        # Verify context structure matches GroundednessProEvaluator expectations
        # Should be a string representation of a dictionary with global_context
        context_str = result[0]["context"]
        assert "global_context" in context_str
        assert "Global context" in context_str
        
        # Verify the context is properly formatted as expected by service evaluators
        assert context_str == "{'global_context': 'Global context'}"

    def test_context_with_message_level_context(self):
        """Test context handling with message-level context in addition to global context"""
        
        class MockContextEvaluator(EvaluatorBase):
            """Mock evaluator that requires context for testing"""
            
            def __init__(self):
                super().__init__()
            
            async def _do_eval(self, eval_input):
                return {"mock_score": 1.0}
            
            def __call__(self, *, query=None, response=None, context=None, **kwargs):
                return super().__call__(query=query, response=response, context=context, **kwargs)
        
        evaluator = MockContextEvaluator()
        converter = evaluator._derive_conversation_converter()
        
        # Test with global context and message-level context
        conversation_with_detailed_context = {
            "context": "Global context",
            "messages": [
                {"role": "user", "content": "Customer wants to know the capital of France", "context": "Customer wants to know the capital of France"},
                {"role": "assistant", "content": "Paris", "context": "Paris is the capital of France"},
            ]
        }
        
        result = converter(conversation_with_detailed_context)
        assert len(result) == 1
        assert "context" in result[0]
        
        # Verify context structure includes all three context types
        context_str = result[0]["context"]
        assert "global_context" in context_str
        assert "query_context" in context_str  
        assert "response_context" in context_str
        assert "Global context" in context_str
        assert "Customer wants to know the capital of France" in context_str
        assert "Paris is the capital of France" in context_str
        
        # Verify the exact format expected by GroundednessProEvaluator
        expected_context = "{'global_context': 'Global context', 'query_context': 'Customer wants to know the capital of France', 'response_context': 'Paris is the capital of France'}"
        assert context_str == expected_context

    def test_context_handling_without_context_input(self):
        """Test that evaluators without context input don't include context in result"""
        
        class MockNoContextEvaluator(EvaluatorBase):
            """Mock evaluator that doesn't require context"""
            
            def __init__(self):
                super().__init__()
            
            async def _do_eval(self, eval_input):
                return {"mock_score": 1.0}
            
            def __call__(self, *, query=None, response=None, **kwargs):
                return super().__call__(query=query, response=response, **kwargs)
        
        evaluator = MockNoContextEvaluator()
        converter = evaluator._derive_conversation_converter()
        
        conversation_with_context = {
            "context": "Global context",
            "messages": [
                {"role": "user", "content": "write a song"},
                {"role": "assistant", "content": "I'm sorry, but I can't assist with that request."},
            ]
        }
        
        result = converter(conversation_with_context)
        assert len(result) == 1
        # Should not include context since this evaluator doesn't require it
        assert "context" not in result[0]
        assert "query" in result[0]
        assert "response" in result[0]

    def test_context_handling_with_mismatched_conversations(self):
        """Test context handling specifically with edge cases that previously caused NaN (multiple assistants + context)"""
        
        class MockContextEvaluator(EvaluatorBase):
            """Mock evaluator that requires context for testing"""
            
            def __init__(self):
                super().__init__()
            
            async def _do_eval(self, eval_input):
                return {"mock_score": 1.0}
            
            def __call__(self, *, query=None, response=None, context=None, **kwargs):
                return super().__call__(query=query, response=response, context=context, **kwargs)
        
        evaluator = MockContextEvaluator()
        converter = evaluator._derive_conversation_converter()
        
        # Test the specific pattern that caused GroundednessProEvaluator regression:
        # Multiple consecutive assistant messages WITH context
        conversation_multiple_assistants_with_context = {
            "context": "Global context",
            "messages": [
                {"role": "user", "content": ""},
                {"role": "assistant", "content": "Paris", "context": "Paris is the capital of France"},
                {"role": "assistant", "content": "No problem at all!"},
                {"role": "assistant", "content": "Thank you!"},
            ]
        }
        
        result = converter(conversation_multiple_assistants_with_context)
        
        # Should return one result (first user-assistant pair) 
        assert len(result) == 1
        assert "context" in result[0]
        assert "query" in result[0]
        assert "response" in result[0]
        
        # Verify context includes both global and response context from first assistant message
        context_str = result[0]["context"]
        assert "global_context" in context_str
        assert "response_context" in context_str
        assert "Global context" in context_str
        assert "Paris is the capital of France" in context_str
        
        # Verify it's the first assistant message that was used
        assert result[0]["response"] == "Paris"
        
        # Verify exact format matches what GroundednessProEvaluator expects
        expected_context = "{'global_context': 'Global context', 'response_context': 'Paris is the capital of France'}"
        assert context_str == expected_context