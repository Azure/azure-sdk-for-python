# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from unittest.mock import MagicMock

import pytest
from azure.ai.evaluation._evaluators._tool_input_accuracy import _ToolInputAccuracyEvaluator
from azure.ai.evaluation._exceptions import ErrorCategory, EvaluationException


# This mock should return a dictionary that mimics the output of the prompty (the _flow call),
# which is then processed by the _do_eval method.
# The flow returns a dict with "llm_output" key containing the actual evaluation result.
async def flow_side_effect(timeout, **kwargs):
    query = kwargs.get("query", "")
    tool_calls = kwargs.get("tool_calls", [])
    tool_definitions = kwargs.get("tool_definitions", {})

    # Mock different scenarios based on query content
    if "all_correct" in str(query).lower():
        # All parameters are correct
        total_params = 2
        correct_params = 2
        llm_output = {
            "chain_of_thought": "All parameters are properly grounded, have correct types, and follow the required format.",
            "details": {
                "total_parameters_passed": total_params,
                "correct_parameters_passed": correct_params,
                "incorrect_parameters": [],
            },
            "result": 1,  # PASS
        }
    elif "missing_required" in str(query).lower():
        # Missing required parameters
        total_params = 1
        correct_params = 1
        llm_output = {
            "chain_of_thought": "Missing required parameter 'location' for weather function.",
            "details": {
                "total_parameters_passed": total_params,
                "correct_parameters_passed": correct_params,
                "incorrect_parameters": ["Missing required parameter: location"],
            },
            "result": 0,  # FAIL
        }
    elif "wrong_type" in str(query).lower():
        # Wrong parameter type
        total_params = 2
        correct_params = 1
        llm_output = {
            "chain_of_thought": "Parameter 'temperature' should be number but received string.",
            "details": {
                "total_parameters_passed": total_params,
                "correct_parameters_passed": correct_params,
                "incorrect_parameters": ["Parameter 'temperature' has wrong type: expected number, got string"],
            },
            "result": 0,  # FAIL
        }
    elif "ungrounded" in str(query).lower():
        # Ungrounded parameters
        total_params = 2
        correct_params = 1
        llm_output = {
            "chain_of_thought": "Parameter 'location' value 'Mars' is not grounded in conversation history.",
            "details": {
                "total_parameters_passed": total_params,
                "correct_parameters_passed": correct_params,
                "incorrect_parameters": ["Parameter 'location' value not grounded in conversation history"],
            },
            "result": 0,  # FAIL
        }
    elif "unexpected_param" in str(query).lower():
        # Unexpected parameters
        total_params = 3
        correct_params = 2
        llm_output = {
            "chain_of_thought": "Unexpected parameter 'extra_param' not defined in tool definition.",
            "details": {
                "total_parameters_passed": total_params,
                "correct_parameters_passed": correct_params,
                "incorrect_parameters": ["Unexpected parameter: extra_param"],
            },
            "result": 0,  # FAIL
        }
    elif "mixed_errors" in str(query).lower():
        # Multiple errors
        total_params = 4
        correct_params = 1
        llm_output = {
            "chain_of_thought": "Multiple parameter errors found.",
            "details": {
                "total_parameters_passed": total_params,
                "correct_parameters_passed": correct_params,
                "incorrect_parameters": [
                    "Missing required parameter: location",
                    "Parameter 'temperature' has wrong type",
                    "Unexpected parameter: extra_param",
                ],
            },
            "result": 0,  # FAIL
        }
    elif "invalid_result" in str(query).lower():
        # Return invalid result to trigger exception
        llm_output = {
            "chain_of_thought": "This should trigger an exception.",
            "details": {"total_parameters_passed": 1, "correct_parameters_passed": 1, "incorrect_parameters": []},
            "result": 5,  # Invalid result
        }
    else:
        # Default case - all correct
        total_params = 1
        correct_params = 1
        llm_output = {
            "chain_of_thought": "Default evaluation - parameters are correct.",
            "details": {
                "total_parameters_passed": total_params,
                "correct_parameters_passed": correct_params,
                "incorrect_parameters": [],
            },
            "result": 1,  # PASS
        }

    # Return in the format expected by _do_eval: wrapped in llm_output key
    return {"llm_output": llm_output}


@pytest.mark.usefixtures("mock_model_config")
@pytest.mark.unittest
class TestToolInputAccuracyEvaluator:

    def test_evaluator_init(self, mock_model_config):
        """Test that the evaluator initializes correctly."""
        evaluator = _ToolInputAccuracyEvaluator(model_config=mock_model_config)
        assert evaluator is not None
        assert evaluator._RESULT_KEY == "tool_input_accuracy"

    def test_evaluate_all_correct_parameters(self, mock_model_config):
        """Test evaluation when all parameters are correct."""
        evaluator = _ToolInputAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        query = "What is the weather in Paris? all_correct"
        response = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_123",
                        "name": "get_weather",
                        "arguments": {"location": "Paris", "units": "celsius"},
                    }
                ],
            }
        ]
        tool_definitions = [
            {
                "name": "get_weather",
                "type": "function",
                "description": "Get weather information for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "The location to get weather for"},
                        "units": {
                            "type": "string",
                            "description": "Temperature units",
                            "enum": ["celsius", "fahrenheit"],
                        },
                    },
                    "required": ["location"],
                },
            }
        ]

        result = evaluator(query=query, response=response, tool_definitions=tool_definitions)

        key = _ToolInputAccuracyEvaluator._RESULT_KEY
        assert result is not None
        assert key in result
        assert f"{key}_result" in result
        assert f"{key}_reason" in result
        assert result[key] == 1
        assert result[f"{key}_result"] == "pass"
        assert f"{key}_details" in result
        assert result[f"{key}_details"]["parameter_extraction_accuracy"] == 100.0

    def test_evaluate_missing_required_parameters(self, mock_model_config):
        """Test evaluation when required parameters are missing."""
        evaluator = _ToolInputAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        query = "Get weather missing_required"
        response = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_123",
                        "name": "get_weather",
                        "arguments": {"units": "celsius"},
                    }
                ],
            }
        ]
        tool_definitions = [
            {
                "name": "get_weather",
                "type": "function",
                "description": "Get weather information for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "The location to get weather for"},
                        "units": {"type": "string", "description": "Temperature units"},
                    },
                    "required": ["location"],
                },
            }
        ]

        result = evaluator(query=query, response=response, tool_definitions=tool_definitions)

        key = _ToolInputAccuracyEvaluator._RESULT_KEY
        assert result is not None
        assert result[key] == 0
        assert result[f"{key}_result"] == "fail"
        assert "missing required parameter" in result[f"{key}_reason"].lower()
        assert f"{key}_details" in result
        assert result[f"{key}_details"]["parameter_extraction_accuracy"] == 100.0  # 1/1 correct param

    def test_evaluate_wrong_parameter_type(self, mock_model_config):
        """Test evaluation when parameters have wrong types."""
        evaluator = _ToolInputAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        query = "Set temperature wrong_type"
        response = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_123",
                        "name": "set_temperature",
                        "arguments": {"room": "bedroom", "temperature": "twenty"},
                    }
                ],
            }
        ]
        tool_definitions = [
            {
                "name": "set_temperature",
                "type": "function",
                "description": "Set room temperature",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "room": {"type": "string", "description": "The room name"},
                        "temperature": {"type": "number", "description": "Temperature in degrees"},
                    },
                    "required": ["room", "temperature"],
                },
            }
        ]

        result = evaluator(query=query, response=response, tool_definitions=tool_definitions)

        key = _ToolInputAccuracyEvaluator._RESULT_KEY
        assert result is not None
        assert result[key] == 0
        assert result[f"{key}_result"] == "fail"
        assert "number" in result[f"{key}_reason"].lower() and "string" in result[f"{key}_reason"].lower()
        assert f"{key}_details" in result
        assert result[f"{key}_details"]["parameter_extraction_accuracy"] == 50.0  # 1/2 correct params

    def test_evaluate_ungrounded_parameters(self, mock_model_config):
        """Test evaluation when parameters are not grounded in conversation."""
        evaluator = _ToolInputAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        query = "What's the weather like? ungrounded"
        response = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_123",
                        "name": "get_weather",
                        "arguments": {"location": "Mars", "units": "celsius"},
                    }
                ],
            }
        ]
        tool_definitions = [
            {
                "name": "get_weather",
                "type": "function",
                "description": "Get weather information for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "The location to get weather for"},
                        "units": {"type": "string", "description": "Temperature units"},
                    },
                    "required": ["location"],
                },
            }
        ]

        result = evaluator(query=query, response=response, tool_definitions=tool_definitions)

        key = _ToolInputAccuracyEvaluator._RESULT_KEY
        assert result is not None
        assert result[key] == 0
        assert result[f"{key}_result"] == "fail"
        assert "not grounded" in result[f"{key}_reason"].lower()
        assert f"{key}_details" in result
        assert result[f"{key}_details"]["parameter_extraction_accuracy"] == 50.0  # 1/2 correct params

    def test_evaluate_unexpected_parameters(self, mock_model_config):
        """Test evaluation when unexpected parameters are provided."""
        evaluator = _ToolInputAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        query = "Get weather info unexpected_param"
        response = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_123",
                        "name": "get_weather",
                        "arguments": {"location": "Paris", "units": "celsius", "extra_param": "unexpected"},
                    }
                ],
            }
        ]
        tool_definitions = [
            {
                "name": "get_weather",
                "type": "function",
                "description": "Get weather information for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "The location to get weather for"},
                        "units": {"type": "string", "description": "Temperature units"},
                    },
                    "required": ["location"],
                },
            }
        ]

        result = evaluator(query=query, response=response, tool_definitions=tool_definitions)

        key = _ToolInputAccuracyEvaluator._RESULT_KEY
        assert result is not None
        assert result[key] == 0
        assert result[f"{key}_result"] == "fail"
        assert "unexpected parameter" in result[f"{key}_reason"].lower()
        assert f"{key}_details" in result
        assert result[f"{key}_details"]["parameter_extraction_accuracy"] == 66.67  # 2/3 correct params

    def test_evaluate_mixed_errors(self, mock_model_config):
        """Test evaluation with multiple types of errors."""
        evaluator = _ToolInputAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        query = "Complex query with mixed_errors"
        response = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_123",
                        "name": "complex_function",
                        "arguments": {"param1": "correct", "param2": "wrong_type", "extra_param": "unexpected"},
                    }
                ],
            }
        ]
        tool_definitions = [
            {
                "name": "complex_function",
                "type": "function",
                "description": "A complex function with multiple parameters",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "param1": {"type": "string", "description": "First parameter"},
                        "param2": {"type": "number", "description": "Second parameter"},
                        "required_param": {"type": "string", "description": "Required parameter"},
                    },
                    "required": ["param1", "required_param"],
                },
            }
        ]

        result = evaluator(query=query, response=response, tool_definitions=tool_definitions)

        key = _ToolInputAccuracyEvaluator._RESULT_KEY
        assert result is not None
        assert result[key] == 0
        assert result[f"{key}_result"] == "fail"
        assert (
            "multiple" in result[f"{key}_reason"].lower() or len(result[f"{key}_details"]["incorrect_parameters"]) >= 2
        )
        assert f"{key}_details" in result
        assert result[f"{key}_details"]["parameter_extraction_accuracy"] == 25.0  # 1/4 correct params

    def test_evaluate_no_tool_calls(self, mock_model_config):
        """Test evaluation when no tool calls are present."""
        evaluator = _ToolInputAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        query = "Simple question without tool calls"
        response = [{"role": "assistant", "content": "I can help you with that."}]
        tool_definitions = [{"name": "get_weather", "type": "function", "description": "Get weather information"}]

        # Expect an exception to be raised
        with pytest.raises(EvaluationException) as exc_info:
            evaluator(query=query, response=response, tool_definitions=tool_definitions)

        assert "no tool calls found" in str(exc_info.value).lower()
        assert exc_info.value.category is ErrorCategory.NOT_APPLICABLE

    def test_evaluate_no_tool_definitions_throws_exception(self, mock_model_config):
        """Test evaluation when no tool definitions are provided."""
        evaluator = _ToolInputAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        query = "Get weather"
        response = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_123",
                        "name": "get_weather",
                        "arguments": {"location": "Paris"},
                    }
                ],
            }
        ]
        tool_definitions = []

        # Expect an exception to be raised
        with pytest.raises(EvaluationException) as exc_info:
            evaluator(query=query, response=response, tool_definitions=tool_definitions)

        # The error message should mention the specific tool that's missing
        assert "get_weather" in str(exc_info.value).lower() and "not found" in str(exc_info.value).lower()
        assert exc_info.value.category is ErrorCategory.NOT_APPLICABLE

    def test_evaluate_missing_tool_definitions_throws_exception(self, mock_model_config):
        """Test evaluation when tool definitions are missing for some tool calls."""
        evaluator = _ToolInputAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        query = "Get weather"
        response = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_123",
                        "name": "get_weather",
                        "arguments": {"location": "Paris"},
                    }
                ],
            }
        ]
        tool_definitions = [{"name": "different_function", "type": "function", "description": "A different function"}]

        # Expect an exception to be raised
        with pytest.raises(EvaluationException) as exc_info:
            evaluator(query=query, response=response, tool_definitions=tool_definitions)

        # The error should mention the specific tool that's missing
        assert "get_weather" in str(exc_info.value).lower() and "not found" in str(exc_info.value).lower()
        assert exc_info.value.category is ErrorCategory.NOT_APPLICABLE

    def test_evaluate_invalid_result_value(self, mock_model_config):
        """Test that invalid result values raise an exception."""
        evaluator = _ToolInputAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        query = "Test invalid_result"
        response = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_123",
                        "name": "test_function",
                        "arguments": {"param": "value"},
                    }
                ],
            }
        ]
        tool_definitions = [
            {
                "name": "test_function",
                "type": "function",
                "description": "Test function",
                "parameters": {
                    "type": "object",
                    "properties": {"param": {"type": "string", "description": "Test parameter"}},
                },
            }
        ]

        with pytest.raises(EvaluationException) as exc_info:
            evaluator(query=query, response=response, tool_definitions=tool_definitions)

        assert "Invalid result value" in str(exc_info.value)

    def test_evaluate_no_response(self, mock_model_config):
        """Test evaluation when no response is provided."""
        evaluator = _ToolInputAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        query = "Get weather"
        tool_definitions = [{"name": "get_weather", "type": "function", "description": "Get weather information"}]

        # Expect an exception to be raised
        with pytest.raises(EvaluationException) as exc_info:
            evaluator(query=query, response=None, tool_definitions=tool_definitions)

        # The error message should mention the specific tool that's missing
        assert "response is required" in str(exc_info.value).lower()
        assert exc_info.value.category is ErrorCategory.MISSING_FIELD

    def test_parameter_extraction_accuracy_calculation(self, mock_model_config):
        """Test the parameter extraction accuracy calculation."""
        evaluator = _ToolInputAccuracyEvaluator(model_config=mock_model_config)

        # Test with some correct parameters
        details = {
            "total_parameters_passed": 5,
            "correct_parameters_passed": 3,
            "incorrect_parameters": ["param1", "param2"],
        }
        accuracy = evaluator._calculate_parameter_extraction_accuracy(details)
        assert accuracy == 60.0

        # Test with all correct parameters
        details = {"total_parameters_passed": 4, "correct_parameters_passed": 4, "incorrect_parameters": []}
        accuracy = evaluator._calculate_parameter_extraction_accuracy(details)
        assert accuracy == 100.0

        # Test with no parameters
        details = {"total_parameters_passed": 0, "correct_parameters_passed": 0, "incorrect_parameters": []}
        accuracy = evaluator._calculate_parameter_extraction_accuracy(details)
        assert accuracy == 100.0

        # Test with all incorrect parameters
        details = {
            "total_parameters_passed": 3,
            "correct_parameters_passed": 0,
            "incorrect_parameters": ["param1", "param2", "param3"],
        }
        accuracy = evaluator._calculate_parameter_extraction_accuracy(details)
        assert accuracy == 0.0

    def test_evaluate_with_conversation_history(self, mock_model_config):
        """Test evaluation with conversation history format."""
        evaluator = _ToolInputAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        query = [
            {"role": "user", "content": "What's the weather in Paris?"},
            {"role": "assistant", "content": "I'll check the weather for you."},
        ]
        response = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_123",
                        "name": "get_weather",
                        "arguments": {"location": "Paris"},
                    }
                ],
            }
        ]
        tool_definitions = [
            {
                "name": "get_weather",
                "type": "function",
                "description": "Get weather information for a location",
                "parameters": {
                    "type": "object",
                    "properties": {"location": {"type": "string", "description": "The location to get weather for"}},
                    "required": ["location"],
                },
            }
        ]

        result = evaluator(query=query, response=response, tool_definitions=tool_definitions)

        key = _ToolInputAccuracyEvaluator._RESULT_KEY
        assert result is not None
        assert key in result
        assert f"{key}_result" in result

    def test_evaluate_with_single_tool_definition(self, mock_model_config):
        """Test evaluation with a single tool definition (not in list format)."""
        evaluator = _ToolInputAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        query = "Get weather all_correct"
        response = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_123",
                        "name": "get_weather",
                        "arguments": {"location": "Paris"},
                    }
                ],
            }
        ]
        # Single tool definition (not in list)
        tool_definitions = {
            "name": "get_weather",
            "type": "function",
            "description": "Get weather information for a location",
            "parameters": {
                "type": "object",
                "properties": {"location": {"type": "string", "description": "The location to get weather for"}},
                "required": ["location"],
            },
        }

        result = evaluator(query=query, response=response, tool_definitions=tool_definitions)

        key = _ToolInputAccuracyEvaluator._RESULT_KEY
        assert result is not None
        assert result[key] == 1
        assert result[f"{key}_result"] == "pass"

    def test_evaluate_missing_query(self, mock_model_config):
        """Test that evaluator raises exception when query is None or missing."""
        evaluator = _ToolInputAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        response = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_123",
                        "name": "get_weather",
                        "arguments": {"location": "Paris"},
                    }
                ],
            }
        ]
        tool_definitions = [
            {
                "name": "get_weather",
                "type": "function",
                "description": "Get weather information for a location",
                "parameters": {
                    "type": "object",
                    "properties": {"location": {"type": "string", "description": "The location to get weather for"}},
                    "required": ["location"],
                },
            }
        ]

        # Test with query=None
        with pytest.raises(EvaluationException) as exc_info:
            evaluator(query=None, response=response, tool_definitions=tool_definitions)

        assert "Query is a required input" in str(exc_info.value)

        # Test with query not provided at all
        with pytest.raises(EvaluationException) as exc_info:
            evaluator(response=response, tool_definitions=tool_definitions)

        assert "Query is a required input" in str(exc_info.value)

    def test_evaluate_missing_arguments_field(self, mock_model_config):
        """Test that an exception is raised when response contains tool calls without arguments field."""
        evaluator = _ToolInputAccuracyEvaluator(model_config=mock_model_config)
        evaluator._flow = MagicMock(side_effect=flow_side_effect)

        query = "What's the weather in Paris?"
        # Response with tool call missing the 'arguments' field
        response = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_123",
                        "name": "get_weather",
                        # Missing 'arguments' field here
                    }
                ],
            }
        ]
        tool_definitions = [
            {
                "name": "get_weather",
                "type": "function",
                "description": "Get weather information for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location to get weather for.",
                        }
                    },
                },
            },
        ]

        with pytest.raises(EvaluationException) as exc_info:
            evaluator(query=query, response=response, tool_definitions=tool_definitions)

        assert "Tool call missing 'arguments' field" in str(exc_info.value)
        assert exc_info.value.category is ErrorCategory.MISSING_FIELD
