# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Callable, Dict
from unittest.mock import MagicMock

import pytest
from azure.ai.evaluation._evaluators._tool_input_accuracy import _ToolInputAccuracyEvaluator
from azure.ai.evaluation._exceptions import EvaluationException

from .base_evaluator_tests import BaseEvaluatorInputTests


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
class TestToolInputAccuracyEvaluator(BaseEvaluatorInputTests):
    """Unit tests for Tool Input Accuracy Evaluator."""

    # ========================================================================
    # CONFIGURATION
    # ========================================================================

    def get_evaluator_class(self):
        return _ToolInputAccuracyEvaluator

    def get_flow_side_effect(self) -> Callable:
        return flow_side_effect

    @property
    def PARAMETER_CONFIG(self) -> Dict[str, Dict[str, Any]]:
        """Configuration for Tool Input Accuracy Evaluator parameters."""
        
        # Shared test data
        base_response = [
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
        
        base_tool_definitions = [
            {
                "name": "get_weather",
                "type": "function",
                "description": "Get weather information",
                "parameters": {
                    "type": "object",
                    "properties": {"location": {"type": "string"}},
                    "required": ["location"],
                },
            }
        ]

        return {
            "query": {
                "test_data": {
                    "valid": "What is the weather in Paris?",
                    "empty": "",
                    "string": "What is the weather in Paris?",
                    "json_single": [{"role": "user", "content": "What is the weather in Paris?"}],
                    "json_object": [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "I want to know about the weather."},
                        {"role": "assistant", "content": "Sure, which city?"},
                        {"role": "user", "content": "Paris"},
                    ],
                    "unexpected": {"text": "What is the weather?", "metadata": {"timestamp": "2024-01-01"}},
                    "success": {
                        "query": "What is the weather in Paris? all_correct",
                        "response": [
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
                        ],
                        "tool_definitions": [
                            {
                                "name": "get_weather",
                                "type": "function",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "location": {"type": "string"},
                                        "units": {"type": "string"},
                                    },
                                    "required": ["location"],
                                },
                            }
                        ],
                    },
                    "not_present": {
                        "query": "What's the weather like? ungrounded",
                        "response": [
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
                        ],
                        "tool_definitions": [
                            {
                                "name": "get_weather",
                                "type": "function",
                                "parameters": {
                                    "type": "object",
                                    "properties": {"location": {"type": "string"}, "units": {"type": "string"}},
                                    "required": ["location"],
                                },
                            }
                        ],
                    },
                    "not_as_expected": {
                        "query": "Set temperature to twenty wrong_type",
                        "response": [
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
                        ],
                        "tool_definitions": [
                            {
                                "name": "set_temperature",
                                "type": "function",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "room": {"type": "string"},
                                        "temperature": {"type": "number"},
                                    },
                                    "required": ["room", "temperature"],
                                },
                            }
                        ],
                    },
                },
                "expected_results": {
                    "not_passed": "pass",
                    "string": "pass",
                    "json_object": "pass",
                    "unexpected": "pass",
                    "extracted_success": "pass",
                    "not_present": "fail",
                    "not_as_expected": "fail",
                },
            },
            "response": {
                "test_data": {
                    "valid": base_response,
                    "empty": [],
                    "string": "The weather is sunny.",
                    "json_single": [{"role": "assistant", "content": "I can help you with that."}],
                    "json_object": base_response,
                    "unexpected": [{"text": "Some response", "data": {"value": 123}}],
                    "success": {
                        "query": "all_correct",
                        "response": base_response,
                        "tool_definitions": base_tool_definitions,
                    },
                    "not_present": {
                        "query": "What is the weather?",
                        "response": [{"role": "assistant", "content": "I can help you with that."}],
                        "tool_definitions": base_tool_definitions,
                    },
                    "not_as_expected": {
                        "query": "mixed_errors",
                        "response": [
                            {
                                "role": "assistant",
                                "content": [
                                    {
                                        "type": "tool_call",
                                        "tool_call_id": "call_123",
                                        "name": "complex_function",
                                        "arguments": {
                                            "param1": "correct",
                                            "param2": "wrong_type",
                                            "extra_param": "unexpected",
                                        },
                                    }
                                ],
                            }
                        ],
                        "tool_definitions": [
                            {
                                "name": "complex_function",
                                "type": "function",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "param1": {"type": "string"},
                                        "param2": {"type": "number"},
                                        "required_param": {"type": "string"},
                                    },
                                    "required": ["param1", "required_param"],
                                },
                            }
                        ],
                    },
                },
                "expected_results": {
                    "not_passed": "not applicable",
                    "string": "not applicable",
                    "json_object": "pass",
                    "unexpected": "not applicable",
                    "extracted_success": "pass",
                    "not_present": "not applicable",
                    "not_as_expected": "fail",
                },
                "result_assertions": lambda result, key: assert_parameter_accuracy(result, key, 100.0),
            },
            "tool_definitions": {
                "test_data": {
                    "valid": base_tool_definitions,
                    "empty": [],
                    "string": "get_weather",
                    "json_object": base_tool_definitions,
                    "unexpected": [{"function_name": "get_weather", "params": ["location"]}],
                    "success": {
                        "query": "all_correct",
                        "response": base_response,
                        "tool_definitions": base_tool_definitions,
                    },
                    "not_present": {
                        "query": "What is the weather?",
                        "response": base_response,
                        "tool_definitions": [
                            {
                                "name": "get_time",
                                "type": "function",
                                "parameters": {"type": "object", "properties": {"timezone": {"type": "string"}}},
                            }
                        ],
                    },
                    "not_as_expected": {
                        "query": "wrong_type",
                        "response": [
                            {
                                "role": "assistant",
                                "content": [
                                    {
                                        "type": "tool_call",
                                        "tool_call_id": "call_123",
                                        "name": "get_weather",
                                        "arguments": {"location": "Paris", "temperature": "twenty"},
                                    }
                                ],
                            }
                        ],
                        "tool_definitions": [
                            {
                                "name": "get_weather",
                                "type": "function",
                                "parameters": {
                                    "type": "object",
                                    "properties": {"location": {"type": "string"}, "temperature": {"type": "number"}},
                                    "required": ["location"],
                                },
                            }
                        ],
                    },
                },
                "expected_results": {
                    "not_passed": "not applicable",
                    "string": "exception",
                    "json_object": "pass",
                    "unexpected": "not applicable",
                    "extracted_success": "pass",
                    "not_present": "not applicable",
                    "not_as_expected": "fail",
                },
                "exception_type": AttributeError,
            },
        }

    # ========================================================================
    # QUERY INPUT SCENARIO TESTS
    # ========================================================================

    def test_query_not_passed_empty_or_null(self, mock_model_config):
        """Test query input: Not Passed, Empty, or Null."""
        self.run_test_not_passed_empty_or_null(mock_model_config, "query", "pass")

    def test_query_string_or_json_single_string(self, mock_model_config):
        """Test query input: String or JSON with single item string."""
        self.run_test_string_or_json_single_string(mock_model_config, "query", "pass")

    def test_query_json_object(self, mock_model_config):
        """Test query input: JSON Object (proper conversation format)."""
        self.run_test_json_object(mock_model_config, "query", "pass")

    def test_query_json_object_unexpected_format(self, mock_model_config):
        """Test query input: JSON Object not in expected format."""
        self.run_test_json_object_unexpected_format(mock_model_config, "query", "pass")

    def test_query_extracted_parameter_successfully(self, mock_model_config):
        """Test query input: Extracted parameter successfully."""
        def custom_assertions(result, key):
            assert result[key] == 1
            assert result[f"{key}_result"] == "pass"
            assert result[f"{key}_details"]["parameter_extraction_accuracy"] == 100.0
        
        self.run_test_extracted_parameter_successfully(mock_model_config, "query", custom_assertions)

    def test_query_parameter_not_present(self, mock_model_config):
        """Test query input: Parameter not present (ungrounded parameter)."""
        evaluator = self.create_evaluator(mock_model_config)
        key = self.get_result_key()
        
        test_data = self.PARAMETER_CONFIG["query"]["test_data"]["not_present"]
        result = evaluator(**test_data)
        
        assert result[key] == 0
        assert result[f"{key}_result"] == "fail"
        assert "not grounded" in result[f"{key}_reason"].lower()
        assert result[f"{key}_details"]["parameter_extraction_accuracy"] == 50.0

    def test_query_parameter_not_as_expected(self, mock_model_config):
        """Test query input: Parameter not as expected."""
        evaluator = self.create_evaluator(mock_model_config)
        key = self.get_result_key()
        
        test_data = self.PARAMETER_CONFIG["query"]["test_data"]["not_as_expected"]
        result = evaluator(**test_data)
        
        assert result[key] == 0
        assert result[f"{key}_result"] == "fail"
        assert "number" in result[f"{key}_reason"].lower() and "string" in result[f"{key}_reason"].lower()
        assert result[f"{key}_details"]["parameter_extraction_accuracy"] == 50.0

    # ========================================================================
    # RESPONSE INPUT SCENARIO TESTS
    # ========================================================================

    def test_response_not_passed_empty_or_null(self, mock_model_config):
        """Test response input: Not Passed, Empty, or Null."""
        self.run_test_not_passed_empty_or_null(
            mock_model_config, 
            "response", 
            "not applicable",
            "Response parameter is required"
        )

    def test_response_string_or_json_single_string(self, mock_model_config):
        """Test response input: String or JSON with single item string."""
        self.run_test_string_or_json_single_string(
            mock_model_config, 
            "response", 
            "not applicable",
            expected_message=_ToolInputAccuracyEvaluator._NO_TOOL_CALLS_MESSAGE
        )

    def test_response_json_object(self, mock_model_config):
        """Test response input: JSON Object (proper tool call format)."""
        evaluator = self.create_evaluator(mock_model_config)
        key = self.get_result_key()
        
        test_data = self.PARAMETER_CONFIG["response"]["test_data"]["success"]
        result = evaluator(**test_data)
        
        assert result[key] == 1
        assert result[f"{key}_result"] == "pass"
        assert result[f"{key}_details"]["parameter_extraction_accuracy"] == 100.0

    def test_response_json_object_unexpected_format(self, mock_model_config):
        """Test response input: JSON Object not in expected format."""
        self.run_test_json_object_unexpected_format(mock_model_config, "response", "not applicable")

    def test_response_extracted_parameter_successfully(self, mock_model_config):
        """Test response input: Extracted parameter successfully."""
        def custom_assertions(result, key):
            assert result[key] == 1
            assert result[f"{key}_result"] == "pass"
            assert result[f"{key}_details"]["parameter_extraction_accuracy"] == 100.0
        
        self.run_test_extracted_parameter_successfully(mock_model_config, "response", custom_assertions)

    def test_response_parameter_not_present(self, mock_model_config):
        """Test response input: Parameter not present."""
        self.run_test_parameter_not_present(
            mock_model_config, 
            "response", 
            "not applicable",
            _ToolInputAccuracyEvaluator._NO_TOOL_CALLS_MESSAGE
        )

    def test_response_parameter_not_as_expected(self, mock_model_config):
        """Test response input: Parameter not as expected."""
        evaluator = self.create_evaluator(mock_model_config)
        key = self.get_result_key()
        
        test_data = self.PARAMETER_CONFIG["response"]["test_data"]["not_as_expected"]
        result = evaluator(**test_data)
        
        assert result[key] == 0
        assert result[f"{key}_result"] == "fail"
        assert len(result[f"{key}_details"]["incorrect_parameters"]) >= 2
        assert result[f"{key}_details"]["parameter_extraction_accuracy"] == 25.0

    # ========================================================================
    # TOOL DEFINITIONS INPUT SCENARIO TESTS
    # ========================================================================

    def test_tool_definitions_not_passed_empty_or_null(self, mock_model_config):
        """Test tool_definitions input: Not Passed, Empty, or Null."""
        self.run_test_not_passed_empty_or_null(
            mock_model_config, 
            "tool_definitions", 
            "not applicable",
            _ToolInputAccuracyEvaluator._NO_TOOL_DEFINITIONS_MESSAGE
        )

    def test_tool_definitions_string_or_json_single_string(self, mock_model_config):
        """Test tool_definitions input: String or JSON with single item string."""
        self.run_test_string_or_json_single_string(
            mock_model_config, 
            "tool_definitions", 
            "exception",
            exception_type=AttributeError
        )

    def test_tool_definitions_json_object(self, mock_model_config):
        """Test tool_definitions input: JSON Object (proper definition format)."""
        self.run_test_json_object(mock_model_config, "tool_definitions", "pass")

    def test_tool_definitions_json_object_unexpected_format(self, mock_model_config):
        """Test tool_definitions input: JSON Object not in expected format."""
        self.run_test_json_object_unexpected_format(mock_model_config, "tool_definitions", "not applicable")

    def test_tool_definitions_extracted_parameter_successfully(self, mock_model_config):
        """Test tool_definitions input: Extracted parameter successfully."""
        def custom_assertions(result, key):
            assert result[key] == 1
            assert result[f"{key}_result"] == "pass"
            assert result[f"{key}_details"]["parameter_extraction_accuracy"] == 100.0
        
        self.run_test_extracted_parameter_successfully(mock_model_config, "tool_definitions", custom_assertions)

    def test_tool_definitions_parameter_not_present(self, mock_model_config):
        """Test tool_definitions input: Parameter not present."""
        self.run_test_parameter_not_present(
            mock_model_config, 
            "tool_definitions", 
            "not applicable",
            _ToolInputAccuracyEvaluator._TOOL_DEFINITIONS_MISSING_MESSAGE
        )

    def test_tool_definitions_parameter_not_as_expected(self, mock_model_config):
        """Test tool_definitions input: Parameter not as expected."""
        self.run_test_parameter_not_as_expected(mock_model_config, "tool_definitions")


# Helper function for assertions
def assert_parameter_accuracy(result, key, expected_accuracy):
    """Assert parameter extraction accuracy."""
    assert f"{key}_details" in result
    if "parameter_extraction_accuracy" in result[f"{key}_details"]:
        assert result[f"{key}_details"]["parameter_extraction_accuracy"] == expected_accuracy