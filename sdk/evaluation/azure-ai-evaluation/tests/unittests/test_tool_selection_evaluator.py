from unittest.mock import MagicMock

import pytest
from azure.ai.evaluation._evaluators._tool_selection import _ToolSelectionEvaluator
from azure.ai.evaluation._exceptions import ErrorCategory, EvaluationException


# Mock function for Tool Selection evaluator flow side effect
async def tool_selection_flow_side_effect(timeout, **kwargs):
    tool_calls = kwargs.get("tool_calls", [])
    tool_definitions = kwargs.get("tool_definitions", [])
    query = kwargs.get("query", "")

    # Simple scoring logic based on query and tool selection (binary: 0 or 1)
    score = 0  # Default fail score
    reason = "Tools selected are not relevant to the query"

    # Note: For ToolSelectionEvaluator, tool_calls is a list of strings (tool names)
    # Convert tool_calls to strings for consistent handling
    tool_names = [str(tc).lower() for tc in tool_calls]

    # Check for relevant tool usage patterns
    if "weather" in query.lower() and any("weather" in name for name in tool_names):
        score = 1
        reason = "Weather tool correctly selected for weather query"
    elif "search" in query.lower() and any("search" in name for name in tool_names):
        score = 1
        reason = "Search tool correctly selected for search query"
    elif "data" in query.lower() and any("data" in name for name in tool_names):
        score = 1
        reason = "Data tool correctly selected for data query"
    elif "financial" in query.lower() and any("financial" in name for name in tool_names):
        score = 1
        reason = "Financial tool correctly selected for financial query"
    elif len(tool_calls) == 0:
        score = 0
        reason = "No tools selected when tools were needed"
    elif "buy" in query.lower() and any("weather" in name for name in tool_names):
        score = 0
        reason = "Weather tool incorrectly selected for purchase query"

    # Handle invalid scenarios - check if any tool name contains "invalid"
    if any("invalid" in str(tc).lower() for tc in tool_calls):
        return {
            "llm_output": {
                "explanation": "Invalid tool call detected",
                "score": "invalid_score",
                "details": {},
            }
        }

    return {
        "llm_output": {
            "explanation": reason,
            "score": score,
            "details": {
                "tools_available": len(tool_definitions),
                "tools_selected": len(tool_calls),
            },
        }
    }


@pytest.mark.usefixtures("mock_model_config")
@pytest.mark.unittest
class TestToolSelectionEvaluator:
    def test_evaluate_tool_selection_pass_relevant_tools(self, mock_model_config):
        evaluator = _ToolSelectionEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=tool_selection_flow_side_effect)

        query = "What's the weather like today?"
        tool_calls = [
            {
                "type": "tool_call",
                "tool_call_id": "call_weather",
                "name": "get_weather",
                "arguments": {"location": "current"},
            }
        ]
        tool_definitions = [
            {
                "name": "get_weather",
                "type": "function",
                "description": "Get weather information",
                "parameters": {"type": "object", "properties": {"location": {"type": "string"}}},
            }
        ]

        result = evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = _ToolSelectionEvaluator._RESULT_KEY
        assert result is not None
        assert key in result
        assert result[key] == 1
        assert result[f"{key}_result"] == "pass"
        assert f"{key}_reason" in result

    def test_evaluate_tool_selection_fail_irrelevant_tools(self, mock_model_config):
        evaluator = _ToolSelectionEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=tool_selection_flow_side_effect)

        query = "I want to buy a jacket"
        tool_calls = [
            {
                "type": "tool_call",
                "tool_call_id": "call_weather",
                "name": "get_weather",
                "arguments": {"location": "current"},
            }
        ]
        tool_definitions = [
            {
                "name": "get_weather",
                "type": "function",
                "description": "Get weather information",
                "parameters": {"type": "object", "properties": {"location": {"type": "string"}}},
            },
            {
                "name": "buy_item",
                "type": "function",
                "description": "Purchase an item",
                "parameters": {"type": "object", "properties": {"item": {"type": "string"}}},
            },
        ]

        result = evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = _ToolSelectionEvaluator._RESULT_KEY
        assert result is not None
        assert key in result
        assert result[key] == 0
        assert result[f"{key}_result"] == "fail"
        assert f"{key}_reason" in result

    def test_evaluate_tool_selection_pass_search_query(self, mock_model_config):
        evaluator = _ToolSelectionEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=tool_selection_flow_side_effect)

        query = "Search for information about Python programming"
        tool_calls = [
            {
                "type": "tool_call",
                "tool_call_id": "call_search",
                "name": "web_search",
                "arguments": {"query": "Python programming"},
            }
        ]
        tool_definitions = [
            {
                "name": "web_search",
                "type": "function",
                "description": "Search the web for information",
                "parameters": {"type": "object", "properties": {"query": {"type": "string"}}},
            }
        ]

        result = evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = _ToolSelectionEvaluator._RESULT_KEY
        assert result is not None
        assert result[key] == 1
        assert result[f"{key}_result"] == "pass"

    def test_evaluate_tool_selection_pass_data_query(self, mock_model_config):
        evaluator = _ToolSelectionEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=tool_selection_flow_side_effect)

        query = "Analyze the data trends"
        tool_calls = [
            {
                "type": "tool_call",
                "tool_call_id": "call_data",
                "name": "analyze_data",
                "arguments": {"dataset": "trends"},
            }
        ]
        tool_definitions = [
            {
                "name": "analyze_data",
                "type": "function",
                "description": "Analyze data patterns",
                "parameters": {"type": "object", "properties": {"dataset": {"type": "string"}}},
            }
        ]

        result = evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = _ToolSelectionEvaluator._RESULT_KEY
        assert result is not None
        assert result[key] == 1
        assert result[f"{key}_result"] == "pass"

    def test_evaluate_tool_selection_pass_financial_query(self, mock_model_config):
        evaluator = _ToolSelectionEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=tool_selection_flow_side_effect)

        query = "Check my financial portfolio"
        tool_calls = [
            {
                "type": "tool_call",
                "tool_call_id": "call_financial",
                "name": "get_financial_data",
                "arguments": {"account": "portfolio"},
            }
        ]
        tool_definitions = [
            {
                "name": "get_financial_data",
                "type": "function",
                "description": "Get financial account information",
                "parameters": {"type": "object", "properties": {"account": {"type": "string"}}},
            }
        ]

        result = evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = _ToolSelectionEvaluator._RESULT_KEY
        assert result is not None
        assert result[key] == 1
        assert result[f"{key}_result"] == "pass"

    def test_evaluate_tool_selection_fail_no_tools_selected(self, mock_model_config):
        evaluator = _ToolSelectionEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=tool_selection_flow_side_effect)

        query = "What's the weather like today?"
        tool_calls = []
        tool_definitions = [
            {
                "name": "get_weather",
                "type": "function",
                "description": "Get weather information",
                "parameters": {"type": "object", "properties": {"location": {"type": "string"}}},
            }
        ]

        # Expect an exception to be raised
        with pytest.raises(EvaluationException) as exc_info:
            evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)

        assert "no tool calls found" in str(exc_info.value).lower()
        assert exc_info.value.category is ErrorCategory.NOT_APPLICABLE

    def test_evaluate_tool_selection_no_tool_definitions_throws_exception(self, mock_model_config):
        evaluator = _ToolSelectionEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=tool_selection_flow_side_effect)

        query = "What's the weather like today?"
        tool_calls = [
            {
                "type": "tool_call",
                "tool_call_id": "call_weather",
                "name": "get_weather",
                "arguments": {"location": "current"},
            }
        ]
        tool_definitions = []

        # Expect an exception to be raised
        with pytest.raises(EvaluationException) as exc_info:
            evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)
        
        # The error message should mention the specific tool that's missing
        assert "get_weather" in str(exc_info.value).lower() and "not found" in str(exc_info.value).lower()
        assert exc_info.value.category is ErrorCategory.NOT_APPLICABLE

    def test_evaluate_tool_selection_exception_invalid_score(self, mock_model_config):
        evaluator = _ToolSelectionEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=tool_selection_flow_side_effect)

        query = "Test invalid scenario"
        tool_calls = [
            {
                "type": "tool_call",
                "tool_call_id": "call_invalid",
                "name": "invalid_tool",
                "arguments": {},
            }
        ]
        tool_definitions = [
            {
                "name": "invalid_tool",
                "type": "function",
                "description": "Test tool",
                "parameters": {"type": "object"},
            }
        ]

        with pytest.raises(EvaluationException) as exc_info:
            evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)

        assert "Invalid score value" in str(exc_info.value)

    def test_evaluate_tool_selection_missing_query(self, mock_model_config):
        """Test that evaluator raises exception when query is None or missing."""
        evaluator = _ToolSelectionEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=tool_selection_flow_side_effect)

        tool_calls = [
            {
                "type": "tool_call",
                "tool_call_id": "call_weather",
                "name": "get_weather",
                "arguments": {"location": "current"},
            }
        ]
        tool_definitions = [
            {
                "name": "get_weather",
                "type": "function",
                "description": "Get weather information",
                "parameters": {"type": "object", "properties": {"location": {"type": "string"}}},
            }
        ]

        # Test with query=None
        with pytest.raises(EvaluationException) as exc_info:
            evaluator(query=None, tool_calls=tool_calls, tool_definitions=tool_definitions)

        assert "Query is a required input" in str(exc_info.value)

        # Test with query not provided at all
        with pytest.raises(EvaluationException) as exc_info:
            evaluator(tool_calls=tool_calls, tool_definitions=tool_definitions)

        assert "Query is a required input" in str(exc_info.value)
