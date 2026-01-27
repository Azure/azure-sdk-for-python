# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from unittest.mock import MagicMock

import pytest
from azure.ai.evaluation._evaluators._task_completion import _TaskCompletionEvaluator
from azure.ai.evaluation._exceptions import EvaluationException


# Mock flow side effect that mimics the output of the prompty (the _flow call)
async def flow_side_effect(timeout, **kwargs):
    query = kwargs.get("query", "")
    response = kwargs.get("response", "")

    # Simple logic to determine success based on keywords in query and response
    if "complete" in str(response).lower() or "done" in str(response).lower():
        success = 1
        explanation = "Task was completed successfully with all requirements met."
        details = {
            "task_requirements": "The requirements for the task.",
            "delivered_outcome": "The final deliverable of the task.",
            "completion_gaps": "complete",
        }
    elif "partial" in str(response).lower():
        success = 0
        explanation = "Task was only partially completed, missing key requirements."
        details = {
            "task_requirements": "The requirements for the task.",
            "delivered_outcome": "The final deliverable of the task.",
            "completion_gaps": "incomplete",
        }
    elif "invalid" in str(response).lower():
        # Return invalid output to test error handling
        success = "invalid_value"
        explanation = "This is an invalid response."
        details = {}
    else:
        success = 0
        explanation = "Task was not completed."
        details = {
            "task_requirements": "The requirements for the task.",
            "delivered_outcome": "none",
            "completion_gaps": "failed",
        }

    return {
        "llm_output": {
            "success": success,
            "explanation": explanation,
            "details": details,
        },
    }


@pytest.mark.usefixtures("mock_model_config")
@pytest.mark.unittest
class TestTaskCompletionEvaluator:
    def test_task_completed_successfully(self, mock_model_config):
        """Test when task is completed successfully"""
        evaluator = _TaskCompletionEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        query = "Plan a 3-day itinerary for Paris with cultural landmarks and local cuisine."
        response = "I have completed a comprehensive 3-day Paris itinerary with cultural landmarks and local cuisine recommendations."

        result = evaluator(query=query, response=response)

        key = _TaskCompletionEvaluator._RESULT_KEY
        assert result is not None
        assert key in result
        assert result[key] == 1
        assert result[f"{key}_result"] == "pass"
        assert f"{key}_reason" in result
        assert "completed successfully" in result[f"{key}_reason"]
        assert f"{key}_details" in result
        assert isinstance(result[f"{key}_details"], dict)

    def test_task_not_completed(self, mock_model_config):
        """Test when task is not completed"""
        evaluator = _TaskCompletionEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        query = "Write a detailed analysis of market trends."
        response = "I cannot provide this analysis at the moment."

        result = evaluator(query=query, response=response)

        key = _TaskCompletionEvaluator._RESULT_KEY
        assert result is not None
        assert key in result
        assert result[key] == 0
        assert result[f"{key}_result"] == "fail"
        assert f"{key}_reason" in result
        assert f"{key}_details" in result

    def test_task_partially_completed(self, mock_model_config):
        """Test when task is only partially completed"""
        evaluator = _TaskCompletionEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        query = "Create a budget plan with income, expenses, and savings goals."
        response = "I have provided a partial budget plan with income and expenses only."

        result = evaluator(query=query, response=response)

        key = _TaskCompletionEvaluator._RESULT_KEY
        assert result is not None
        assert key in result
        assert result[key] == 0
        assert result[f"{key}_result"] == "fail"
        assert "partial" in result[f"{key}_reason"].lower()
        assert f"{key}_details" in result

    def test_with_tool_definitions(self, mock_model_config):
        """Test evaluation with tool definitions provided"""
        evaluator = _TaskCompletionEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        query = [{"role": "user", "content": "Find hotels in Paris and book the cheapest one"}]
        response = [
            {"role": "assistant", "content": "Task is complete. I found hotels and booked the cheapest option."}
        ]
        tool_definitions = [
            {
                "name": "search_hotels",
                "description": "Search for hotels in a location",
                "parameters": {
                    "type": "object",
                    "properties": {"location": {"type": "string", "description": "City name"}},
                },
            },
            {
                "name": "book_hotel",
                "description": "Book a hotel",
                "parameters": {
                    "type": "object",
                    "properties": {"hotel_id": {"type": "string", "description": "Hotel identifier"}},
                },
            },
        ]

        result = evaluator(query=query, response=response, tool_definitions=tool_definitions)

        key = _TaskCompletionEvaluator._RESULT_KEY
        assert result is not None
        assert key in result
        assert result[key] == 1
        assert result[f"{key}_result"] == "pass"

    def test_with_conversation_history(self, mock_model_config):
        """Test evaluation with conversation history as list of messages"""
        evaluator = _TaskCompletionEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        query = [
            {"role": "system", "content": "You are a helpful travel assistant."},
            {"role": "user", "content": "I need to book a flight to Tokyo."},
            {"role": "assistant", "content": "I can help you with that. What dates?"},
            {"role": "user", "content": "December 15-22, 2025"},
        ]
        response = [
            {"role": "assistant", "content": "Done! I have booked your flight to Tokyo for December 15-22, 2025."}
        ]

        result = evaluator(query=query, response=response)

        key = _TaskCompletionEvaluator._RESULT_KEY
        assert result is not None
        assert key in result
        assert result[key] == 1
        assert result[f"{key}_result"] == "pass"

    def test_missing_query_and_response(self, mock_model_config):
        """Test that missing both query and response raises an exception"""
        evaluator = _TaskCompletionEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        with pytest.raises(EvaluationException) as exc_info:
            evaluator()

        assert "Query is a required input" in str(exc_info.value)

    def test_string_success_value_true(self, mock_model_config):
        """Test handling of string 'TRUE' as success value"""
        evaluator = _TaskCompletionEvaluator(model_config=mock_model_config)

        async def string_true_flow(timeout, **kwargs):
            return {
                "llm_output": {
                    "success": "TRUE",
                    "explanation": "Task completed",
                    "details": {},
                }
            }

        evaluator._flow = MagicMock(side_effect=string_true_flow)

        query = "Complete this task"
        response = "Task is complete"
        result = evaluator(query=query, response=response)

        key = _TaskCompletionEvaluator._RESULT_KEY
        assert result[key] == 1
        assert result[f"{key}_result"] == "pass"

    def test_string_success_value_false(self, mock_model_config):
        """Test handling of string 'FALSE' as success value"""
        evaluator = _TaskCompletionEvaluator(model_config=mock_model_config)

        async def string_false_flow(timeout, **kwargs):
            return {
                "llm_output": {
                    "success": "FALSE",
                    "explanation": "Task not completed",
                    "details": {},
                }
            }

        evaluator._flow = MagicMock(side_effect=string_false_flow)

        query = "Complete this task"
        response = "Could not complete"
        result = evaluator(query=query, response=response)

        key = _TaskCompletionEvaluator._RESULT_KEY
        assert result[key] == 0
        assert result[f"{key}_result"] == "fail"

    def test_invalid_llm_output_format(self, mock_model_config):
        """Test handling when LLM output is not a dictionary"""
        evaluator = _TaskCompletionEvaluator(model_config=mock_model_config)

        async def invalid_output_flow(timeout, **kwargs):
            return {"llm_output": "This is a string, not a dictionary"}

        evaluator._flow = MagicMock(side_effect=invalid_output_flow)

        query = "Complete this task"
        response = "Done"
        result = evaluator(query=query, response=response)

        key = _TaskCompletionEvaluator._RESULT_KEY
        assert result[key] == 0

    def test_default_success_value(self, mock_model_config):
        """Test that default success value is 0 when not provided"""
        evaluator = _TaskCompletionEvaluator(model_config=mock_model_config)

        async def no_success_flow(timeout, **kwargs):
            return {
                "llm_output": {
                    "explanation": "No success field provided",
                    "details": {},
                }
            }

        evaluator._flow = MagicMock(side_effect=no_success_flow)

        query = "Complete this task"
        response = "Task response"
        result = evaluator(query=query, response=response)

        key = _TaskCompletionEvaluator._RESULT_KEY
        assert result[key] == 0
        assert result[f"{key}_result"] == "fail"

    def test_complex_response_with_tool_calls(self, mock_model_config):
        """Test evaluation with response containing tool calls"""
        evaluator = _TaskCompletionEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        query = "Search for restaurants and make a reservation"
        response = [
            {
                "role": "assistant",
                "content": [{"type": "text", "text": "Let me search for restaurants."}],
                "tool_calls": [
                    {
                        "type": "function",
                        "id": "call_1",
                        "function": {
                            "name": "search_restaurants",
                            "arguments": '{"location": "downtown", "cuisine": "Italian"}',
                        },
                    }
                ],
            },
            {
                "role": "tool",
                "tool_call_id": "call_1",
                "content": [
                    {"type": "tool_result", "tool_result": {"result": "Found 5 Italian restaurants downtown."}}
                ],
            },
            {"role": "assistant", "content": "Task complete! I found restaurants and made a reservation."},
        ]
        tool_definitions = [
            {
                "name": "search_restaurants",
                "type": "function",
                "description": "Search for restaurants",
                "parameters": {"type": "object", "properties": {}},
            }
        ]

        result = evaluator(query=query, response=response, tool_definitions=tool_definitions)

        key = _TaskCompletionEvaluator._RESULT_KEY
        assert result is not None
        assert key in result
        assert result[key] == 1
        assert result[f"{key}_result"] == "pass"

    def test_numeric_success_values(self, mock_model_config):
        """Test that numeric 0 and 1 values work correctly"""
        evaluator = _TaskCompletionEvaluator(model_config=mock_model_config)

        async def numeric_success_flow(timeout, **kwargs):
            # Return 1 for success
            return {
                "llm_output": {
                    "success": 1,
                    "explanation": "Task completed",
                    "details": {},
                }
            }

        evaluator._flow = MagicMock(side_effect=numeric_success_flow)

        query = "Complete this task"
        response = "Done"
        result = evaluator(query=query, response=response)

        key = _TaskCompletionEvaluator._RESULT_KEY
        assert result[key] == 1
        assert result[f"{key}_result"] == "pass"

    def test_empty_details(self, mock_model_config):
        """Test handling of empty details field"""
        evaluator = _TaskCompletionEvaluator(model_config=mock_model_config)

        async def empty_details_flow(timeout, **kwargs):
            return {
                "llm_output": {
                    "success": 1,
                    "explanation": "Task completed",
                    # No details field
                }
            }

        evaluator._flow = MagicMock(side_effect=empty_details_flow)

        query = "Test"
        response = "Complete"
        result = evaluator(query=query, response=response)

        key = _TaskCompletionEvaluator._RESULT_KEY
        assert f"{key}_details" in result
        assert result[f"{key}_details"] == ""

    def test_empty_explanation(self, mock_model_config):
        """Test handling of missing explanation field"""
        evaluator = _TaskCompletionEvaluator(model_config=mock_model_config)

        async def no_explanation_flow(timeout, **kwargs):
            return {
                "llm_output": {
                    "success": 1,
                    "details": {},
                    # No explanation field
                }
            }

        evaluator._flow = MagicMock(side_effect=no_explanation_flow)

        query = "Test"
        response = "Complete"
        result = evaluator(query=query, response=response)

        key = _TaskCompletionEvaluator._RESULT_KEY
        assert f"{key}_reason" in result
        assert result[f"{key}_reason"] == ""
