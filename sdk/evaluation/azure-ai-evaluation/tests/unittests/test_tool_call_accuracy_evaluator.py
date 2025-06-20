from unittest.mock import MagicMock

import pytest
from azure.ai.evaluation import ToolCallAccuracyEvaluator
from azure.ai.evaluation._exceptions import EvaluationException


# Use tool_call_id convenience to specify whether eval result is good, bad, or invalid
async def flow_side_effect(timeout, **kwargs):
    if "good" in kwargs.get("tool_call").get("tool_call_id"):
        return """<S0>Let's think step by step. You're totally right!</S0> <S1>Tool is the best ever.</S1> <S2>1</S2>"""
    elif "bad" in kwargs.get("tool_call").get("tool_call_id"):
        return """<S0>Let's think step by step. You're wrong!</S0> <S1>Tool is not good.</S1> <S2>0</S2>"""
    else:
        return """<S0>Let's think </S0>Or not.</S0> <S1>Tool is...who knows.</S1> <S2>hello</S2>"""


@pytest.mark.usefixtures("mock_model_config")
@pytest.mark.unittest
class TestToolCallAccuracyEvaluator:
    def test_evaluate_tools_valid1(self, mock_model_config):
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        # Test evaluation with valid input, one good tool call and one bad
        query="Where is the Eiffel Tower?"
        response="The Eiffel Tower is in Paris."
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
        result = evaluator(query=query, response=response, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = ToolCallAccuracyEvaluator._AGGREGATE_RESULT_KEY
        assert result is not None
        assert (key in result and f"{key}_result" in result and f"{key}_threshold" in result)
        assert result[key] == 0.5
        assert result[f"{key}_result"] == "fail"
        assert result[f"{key}_threshold"] == ToolCallAccuracyEvaluator._DEFAULT_TOOL_CALL_ACCURACY_SCORE
        assert "per_tool_call_details" in result
        assert len(result["per_tool_call_details"]) == 2
        for tool_call in result["per_tool_call_details"]:
            assert "tool_call_accurate" in tool_call
            assert "tool_call_accurate_reason" in tool_call
            assert "tool_call_id" in tool_call
            if tool_call["tool_call_id"] == "call_good":
                assert tool_call["tool_call_accurate"] is True
                assert len(tool_call["tool_call_accurate_reason"]) > 0
            elif tool_call["tool_call_id"] == "call_bad":
                assert tool_call["tool_call_accurate"] is False
                assert len(tool_call["tool_call_accurate_reason"]) > 0
            else:
                pytest.fail()


    def test_evaluate_tools_valid2(self, mock_model_config):
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        # Test evaluation with valid input, one good tool call and one bad
        query="Where is the Eiffel Tower?"
        response="The Eiffel Tower is in Paris."
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
        result = evaluator(query=query, response=response, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = ToolCallAccuracyEvaluator._AGGREGATE_RESULT_KEY
        assert result is not None
        assert (key in result and f"{key}_result" in result and f"{key}_threshold" in result)
        assert result[key] == 0.0
        assert result[f"{key}_result"] == "fail"
        assert result[f"{key}_threshold"] == ToolCallAccuracyEvaluator._DEFAULT_TOOL_CALL_ACCURACY_SCORE
        assert "per_tool_call_details" in result
        assert len(result["per_tool_call_details"]) == 2
        for tool_call in result["per_tool_call_details"]:
            assert "tool_call_accurate" in tool_call
            assert "tool_call_accurate_reason" in tool_call
            assert "tool_call_id" in tool_call
            if tool_call["tool_call_id"] == "call_good":
                assert tool_call["tool_call_accurate"] is False
                assert len(tool_call["tool_call_accurate_reason"]) > 0
            elif tool_call["tool_call_id"] == "call_bad":
                assert tool_call["tool_call_accurate"] is False
                assert len(tool_call["tool_call_accurate_reason"]) > 0
            else:
                pytest.fail()


    def test_evaluate_tools_valid3(self, mock_model_config):
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        # Test evaluation with valid input, one good tool call and one bad
        query="Where is the Eiffel Tower?"
        response="The Eiffel Tower is in Paris."
        tool_calls=[
            {
                "type": "tool_call",
                "tool_call_id": "call_good",
                "name": "fetch_weather",
                "arguments": {"location": "Tokyo"},
            },
            {
                "type": "tool_call",
                "tool_call_id": "call_good",
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
        result = evaluator(query=query, response=response, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = ToolCallAccuracyEvaluator._AGGREGATE_RESULT_KEY
        assert result is not None
        assert (key in result and f"{key}_result" in result and f"{key}_threshold" in result)
        assert result[key] == 1.0
        assert result[f"{key}_result"] == "pass"
        assert result[f"{key}_threshold"] == ToolCallAccuracyEvaluator._DEFAULT_TOOL_CALL_ACCURACY_SCORE
        assert "per_tool_call_details" in result
        assert len(result["per_tool_call_details"]) == 2
        for tool_call in result["per_tool_call_details"]:
            assert "tool_call_accurate" in tool_call
            assert "tool_call_accurate_reason" in tool_call
            assert "tool_call_id" in tool_call
            if tool_call["tool_call_id"] == "call_good":
                assert tool_call["tool_call_accurate"] is True
                assert len(tool_call["tool_call_accurate_reason"]) > 0
            elif tool_call["tool_call_id"] == "call_bad":
                assert tool_call["tool_call_accurate"] is True
                assert len(tool_call["tool_call_accurate_reason"]) > 0
            else:
                pytest.fail()

    def test_evaluate_tools_one_eval_fails(self, mock_model_config):
        with pytest.raises(EvaluationException) as exc_info:

            evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
            evaluator._flow = MagicMock(side_effect=flow_side_effect)

            # Test evaluation with valid input, one good tool call and one bad
            query="Where is the Eiffel Tower?"
            response="The Eiffel Tower is in Paris."
            tool_calls=[
                {
                    "type": "tool_call",
                    "tool_call_id": "call_good",
                    "name": "fetch_weather",
                    "arguments": {"location": "Tokyo"},
                },
                {
                    "type": "tool_call",
                    "tool_call_id": "call_invalid",
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
            result = evaluator(query=query, response=response, tool_calls=tool_calls, tool_definitions=tool_definitions)
        # if one tool call evaluation fails, we'll fail the whole thing
        assert "Tool call accuracy evaluator" in str(exc_info.value)

    def test_evaluate_tools_some_not_applicable(self, mock_model_config):
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        # Test evaluation with valid input, one good tool call and one bad
        query="Where is the Eiffel Tower?"
        response="The Eiffel Tower is in Paris."
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
                "type": "another_built_in",
                "description": "Buy a jacket of the given type.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "description": "The type of jacket to buy."}
                    },
                },
            },
        ]
        result = evaluator(query=query, response=response, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = ToolCallAccuracyEvaluator._AGGREGATE_RESULT_KEY
        assert result is not None
        assert (key in result and f"{key}_result" in result and f"{key}_threshold" in result)
        assert result[key] == 1.0
        assert result[f"{key}_result"] == "pass"
        assert result[f"{key}_threshold"] == ToolCallAccuracyEvaluator._DEFAULT_TOOL_CALL_ACCURACY_SCORE
        assert "per_tool_call_details" in result
        assert len(result["per_tool_call_details"]) == 2
        for tool_call in result["per_tool_call_details"]:
            assert "tool_call_accurate" in tool_call
            assert "tool_call_accurate_reason" in tool_call
            assert "tool_call_id" in tool_call
            if tool_call["tool_call_id"] == "call_good":
                assert tool_call["tool_call_accurate"] is True
                assert len(tool_call["tool_call_accurate_reason"]) > 0
            elif tool_call["tool_call_id"] == "call_bad":
                assert tool_call["tool_call_accurate"] == "not applicable"
                assert tool_call["tool_call_accurate_reason"] == "Tool call not supported for evaluation"
            else:
                pytest.fail()

    def test_evaluate_tools_all_not_applicable(self, mock_model_config):
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        # Test evaluation with valid input, one good tool call and one bad
        query="Where is the Eiffel Tower?"
        response="The Eiffel Tower is in Paris."
        tool_calls=[
            {
                "type": "tool_call",
                "tool_call_id": "call_good",
                "name": "fetch_weather",
                "arguments": {"location": "Tokyo"},
            },
            {
                "type": "tool_call",
                "tool_call_id": "call_good",
                "name": "buy_jacket",
                "arguments": {"type": "raincoat"},
            },
        ]
        tool_definitions=[
            {
                "name": "fetch_weather",
                "type": "some_built_in",
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
                "type": "another_built_in",
                "description": "Buy a jacket of the given type.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "description": "The type of jacket to buy."}
                    },
                },
            },
        ]
        result = evaluator(query=query, response=response, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = ToolCallAccuracyEvaluator._AGGREGATE_RESULT_KEY
        assert result is not None
        assert (key in result and f"{key}_result" in result and f"{key}_threshold" in result)
        assert result[key] == "not applicable"
        assert result[f"{key}_result"] == "not applicable"
        assert result[f"{key}_threshold"] == ToolCallAccuracyEvaluator._DEFAULT_TOOL_CALL_ACCURACY_SCORE
        assert "per_tool_call_details" in result
        assert len(result["per_tool_call_details"]) == 0
        assert result[f"{key}_reason"] == "Tool call accuracy evaluation is not yet supported for the invoked tools."

    def test_evaluate_tools_no_tools(self, mock_model_config):
        evaluator = ToolCallAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        # Test evaluation with valid input, one good tool call and one bad
        query="Where is the Eiffel Tower?"
        response="The Eiffel Tower is in Paris."
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
            {
                "name": "buy_jacket",
                "type": "another_built_in",
                "description": "Buy a jacket of the given type.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "description": "The type of jacket to buy."}
                    },
                },
            },
        ]
        result = evaluator(query=query, response=response, tool_calls=tool_calls, tool_definitions=tool_definitions)

        key = ToolCallAccuracyEvaluator._AGGREGATE_RESULT_KEY
        assert result is not None
        assert (key in result and f"{key}_result" in result and f"{key}_threshold" in result)
        assert result[key] == "not applicable"
        assert result[f"{key}_result"] == "not applicable"
        assert result[f"{key}_threshold"] == ToolCallAccuracyEvaluator._DEFAULT_TOOL_CALL_ACCURACY_SCORE
        assert "per_tool_call_details" in result
        assert len(result["per_tool_call_details"]) == 0
        assert result[f"{key}_reason"] == "No tool calls were made."

