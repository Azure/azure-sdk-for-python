from unittest.mock import MagicMock

import pytest
from azure.ai.evaluation import ToolCallAccuracyEvaluator
from azure.ai.evaluation._exceptions import EvaluationException


# This mock should return a dictionary that mimics the output of the prompty (the _flow call),
# which is then processed by the _do_eval method.
async def flow_side_effect(timeout, **kwargs):
    tool_calls = kwargs.get("tool_calls", [])
    
    good_calls = sum(1 for tc in tool_calls if "good" in tc.get("tool_call_id", ""))
    bad_calls = sum(1 for tc in tool_calls if "bad" in tc.get("tool_call_id", ""))
    invalid_calls = sum(1 for tc in tool_calls if "invalid" in tc.get("tool_call_id", ""))
    total_calls = len(tool_calls)

    if invalid_calls > 0:
        # Return a non-numeric score to trigger an exception in the evaluator's check_score_is_valid
        return {
            "chain_of_thought": "The tool calls were very correct that I returned a huge number!",
            "tool_calls_success_level": 25,
            "additional_details": {},
            ToolCallAccuracyEvaluator._EXCESS_TOOL_CALLS_KEY: {},
            ToolCallAccuracyEvaluator._MISSING_TOOL_CALLS_KEY: {}
        }

    score = 1  # Default score for "all bad"
    if total_calls > 0:
        if good_calls == total_calls:
            score = 5  # All good
        elif good_calls > 0:
            score = 3  # Mixed good and bad
    
    return {
        "chain_of_thought": f"Evaluated {total_calls} tool calls with {good_calls} correct calls.",
        "tool_calls_success_level": score,
        "additional_details": {
            "tool_calls_made_by_agent": total_calls,
            "correct_tool_calls_made_by_agent": good_calls
        },
        ToolCallAccuracyEvaluator._EXCESS_TOOL_CALLS_KEY: {"total": 0},
        ToolCallAccuracyEvaluator._MISSING_TOOL_CALLS_KEY: {"total": 0}
    }


@pytest.mark.usefixtures("mock_model_config")
@pytest.mark.unittest
class TestToolCallAccuracyEvaluator:
    def test_evaluate_tools_valid1(self, mock_model_config):
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        # Test evaluation with one good and one bad tool call
        query="Where is the Eiffel Tower?"
        tool_calls=[
            {
                "type": "tool_call",
                "tool_call_id": "call_good",
                "name": "fetch_weather",
                "arguments": {"location": "Paris"},
            },
            {
                "type": "tool_call",
                "tool_call_id": "call_bad",
                "name": "buy_jacket",
                "arguments": {"type": "raincoat"},
            },
        ]
        tool_definitions=[
            {
                "name": "fetch_weather",
                "type": "function",
                "description": "Fetches the weather information for the specified location.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "The location to fetch weather for."}
                    },
                },
            },
            {
                "name": "buy_jacket",
                "type": "function",
                "description": "Buy a jacket of the given type.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "description": "The type of jacket to buy."}
                    },
                },
            },
        ]
        result = evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = ToolCallAccuracyEvaluator._RESULT_KEY
        assert result is not None
        assert (key in result and f"{key}_result" in result and f"{key}_threshold" in result)
        assert result[key] == 3.0  # Mixed good/bad gets score 3
        assert result[f"{key}_result"] == "pass"
        assert result[f"{key}_threshold"] == ToolCallAccuracyEvaluator._DEFAULT_TOOL_CALL_ACCURACY_SCORE
        assert f"{key}_reason" in result
        assert result[f"{key}_reason"] == "Evaluated 2 tool calls with 1 correct calls."
        assert "per_tool_call_details" in result
        assert ToolCallAccuracyEvaluator._EXCESS_TOOL_CALLS_KEY in result
        assert ToolCallAccuracyEvaluator._MISSING_TOOL_CALLS_KEY in result
        assert result["applicable"] is True

    def test_evaluate_tools_valid2(self, mock_model_config):
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        # Test evaluation with two bad tool calls
        query="Where is the Eiffel Tower?"
        tool_calls=[
            {
                "type": "tool_call",
                "tool_call_id": "call_bad",
                "name": "fetch_weather",
                "arguments": {"location": "Tokyo"},
            },
            {
                "type": "tool_call",
                "tool_call_id": "call_bad",
                "name": "buy_jacket",
                "arguments": {"type": "raincoat"},
            },
        ]
        tool_definitions=[
            {
                "name": "fetch_weather",
                "type": "function",
                "description": "Fetches the weather information for the specified location.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "The location to fetch weather for."}
                    },
                },
            },
            {
                "name": "buy_jacket",
                "type": "function",
                "description": "Buy a jacket of the given type.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "description": "The type of jacket to buy."}
                    },
                },
            },
        ]
        result = evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = ToolCallAccuracyEvaluator._RESULT_KEY
        assert result is not None
        assert (key in result and f"{key}_result" in result and f"{key}_threshold" in result)
        assert result[key] == 1.0  # All bad gets score 1
        assert result[f"{key}_result"] == "fail"
        assert result[f"{key}_threshold"] == ToolCallAccuracyEvaluator._DEFAULT_TOOL_CALL_ACCURACY_SCORE
        assert f"{key}_reason" in result
        assert result[f"{key}_reason"] == "Evaluated 2 tool calls with 0 correct calls."
        assert "per_tool_call_details" in result
        assert ToolCallAccuracyEvaluator._EXCESS_TOOL_CALLS_KEY in result
        assert ToolCallAccuracyEvaluator._MISSING_TOOL_CALLS_KEY in result
        assert result["applicable"] is True

    def test_evaluate_tools_valid3(self, mock_model_config):
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        # Test evaluation with two good tool calls
        query="Where is the Eiffel Tower?"
        tool_calls=[
            {
                "type": "tool_call",
                "tool_call_id": "call_good",
                "name": "fetch_weather",
                "arguments": {"location": "Paris"},
            },
            {
                "type": "tool_call",
                "tool_call_id": "call_good",
                "name": "buy_jacket",
                "arguments": {"type": "jacket"},
            },
        ]
        tool_definitions=[
            {
                "name": "fetch_weather",
                "type": "function",
                "description": "Fetches the weather information for the specified location.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "The location to fetch weather for."}
                    },
                },
            },
            {
                "name": "buy_jacket",
                "type": "function",
                "description": "Buy a jacket of the given type.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "description": "The type of jacket to buy."}
                    },
                },
            },
        ]
        result = evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = ToolCallAccuracyEvaluator._RESULT_KEY
        assert result is not None
        assert (key in result and f"{key}_result" in result and f"{key}_threshold" in result)
        assert result[key] == 5.0  # All good gets score 5
        assert result[f"{key}_result"] == "pass"
        assert result[f"{key}_threshold"] == ToolCallAccuracyEvaluator._DEFAULT_TOOL_CALL_ACCURACY_SCORE
        assert f"{key}_reason" in result
        assert result[f"{key}_reason"] == "Evaluated 2 tool calls with 2 correct calls."
        assert "per_tool_call_details" in result
        assert ToolCallAccuracyEvaluator._EXCESS_TOOL_CALLS_KEY in result
        assert ToolCallAccuracyEvaluator._MISSING_TOOL_CALLS_KEY in result
        assert result["applicable"] is True

    def test_evaluate_tools_one_eval_fails(self, mock_model_config):
        with pytest.raises(EvaluationException) as exc_info:
            evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
            evaluator._flow = MagicMock(side_effect=flow_side_effect)

            # Test evaluation with an invalid tool call ID to trigger failure
            query="Where is the Eiffel Tower?"
            tool_calls=[
                {
                    "type": "tool_call",
                    "tool_call_id": "call_invalid",
                    "name": "fetch_weather",
                    "arguments": {"location": "Tokyo"},
                },
            ]
            tool_definitions=[
                {
                    "name": "fetch_weather",
                    "type": "function",
                    "description": "Fetches the weather information for the specified location.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string", "description": "The location to fetch weather for."}
                        },
                    },
                },
            ]
            evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)
        
        assert "Invalid score value" in str(exc_info.value)

    def test_evaluate_tools_some_not_applicable(self, mock_model_config):
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        # Test with one function tool and one non-function tool
        query="Where is the Eiffel Tower?"
        tool_calls=[
            {
                "type": "tool_call",
                "tool_call_id": "call_good",
                "name": "fetch_weather",
                "arguments": {"location": "Tokyo"},
            },
            {
                "type": "tool_call",
                "tool_call_id": "call_bad",
                "name": "buy_jacket",
                "arguments": {"type": "raincoat"},
            },
        ]
        tool_definitions=[
            {
                "name": "fetch_weather",
                "type": "function",
                "description": "Fetches the weather information for the specified location.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "The location to fetch weather for."}
                    },
                },
            },
            {
                "name": "buy_jacket",
                "type": "another_built_in", # This tool will be filtered out
                "description": "Buy a jacket of the given type.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "description": "The type of jacket to buy."}
                    },
                },
            },
        ]
        result = evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = ToolCallAccuracyEvaluator._RESULT_KEY
        assert result is not None
        assert result[key] == ToolCallAccuracyEvaluator._NOT_APPLICABLE_RESULT
        assert result[f"{key}_result"] == "pass"
        assert result[f"{key}_threshold"] == ToolCallAccuracyEvaluator._DEFAULT_TOOL_CALL_ACCURACY_SCORE
        assert result[f"{key}_reason"] == ToolCallAccuracyEvaluator._TOOL_DEFINITIONS_MISSING_MESSAGE
        assert result["per_tool_call_details"] == {}
        assert result[ToolCallAccuracyEvaluator._EXCESS_TOOL_CALLS_KEY] == {}
        assert result[ToolCallAccuracyEvaluator._MISSING_TOOL_CALLS_KEY] == {}
        assert result["applicable"] is False

    def test_evaluate_tools_all_not_applicable(self, mock_model_config):
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)
        
        # Test with only non-function tools
        query="Where is the Eiffel Tower?"
        tool_calls=[
            {
                "type": "tool_call",
                "tool_call_id": "call_good",
                "name": "fetch_weather",
                "arguments": {"location": "Tokyo"},
            },
        ]
        tool_definitions=[
            {
                "name": "fetch_weather",
                "type": "some_built_in", # Not a 'function' type
                "description": "Fetches the weather information for the specified location.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "The location to fetch weather for."}
                    },
                },
            },
        ]
        result = evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = ToolCallAccuracyEvaluator._RESULT_KEY
        assert result is not None
        assert result[key] == ToolCallAccuracyEvaluator._NOT_APPLICABLE_RESULT
        assert result[f"{key}_result"] == "pass"
        assert result[f"{key}_threshold"] == ToolCallAccuracyEvaluator._DEFAULT_TOOL_CALL_ACCURACY_SCORE
        assert result[f"{key}_reason"] == ToolCallAccuracyEvaluator._TOOL_DEFINITIONS_MISSING_MESSAGE
        assert result["per_tool_call_details"] == {}
        assert result[ToolCallAccuracyEvaluator._EXCESS_TOOL_CALLS_KEY] == {}
        assert result[ToolCallAccuracyEvaluator._MISSING_TOOL_CALLS_KEY] == {}
        assert result["applicable"] is False

    def test_evaluate_tools_no_tools(self, mock_model_config):
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        # Test with no tool calls provided
        query="Where is the Eiffel Tower?"
        tool_calls=[]
        tool_definitions=[
            {
                "name": "fetch_weather",
                "type": "function",
                "description": "Fetches the weather information for the specified location.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "The location to fetch weather for."}
                    },
                },
            },
        ]
        result = evaluator(query=query, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = ToolCallAccuracyEvaluator._RESULT_KEY
        assert result is not None
        assert result[key] == ToolCallAccuracyEvaluator._NOT_APPLICABLE_RESULT
        assert result[f"{key}_result"] == "pass"
        assert result[f"{key}_threshold"] == ToolCallAccuracyEvaluator._DEFAULT_TOOL_CALL_ACCURACY_SCORE
        assert result[f"{key}_reason"] == ToolCallAccuracyEvaluator._NO_TOOL_CALLS_MESSAGE
        assert result["per_tool_call_details"] == {}
        assert result[ToolCallAccuracyEvaluator._EXCESS_TOOL_CALLS_KEY] == {}
        assert result[ToolCallAccuracyEvaluator._MISSING_TOOL_CALLS_KEY] == {}
        assert result["applicable"] is False