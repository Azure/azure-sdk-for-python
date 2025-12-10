# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Base class for behavioral tests of evaluators.
Tests various input scenarios: query, and response.
"""

from typing import Any, Dict, List
from base_evaluator_runner import BaseEvaluatorRunner


class BaseEvaluatorBehaviorTest(BaseEvaluatorRunner):
    """
    Base class for evaluator behavioral tests with query and response inputs.
    Subclasses should implement:
    - evaluator_name: str - name of the evaluator (e.g., "relevance")
    Subclasses may override:
    - requires_valid_format: bool - whether valid format is required for response
    - requires_query: bool - whether query is required
    - tools_evaluator: bool - whether evaluator uses tool calls
    - MINIMAL_RESPONSE: list - minimal valid response format for the evaluator
    """

    # Subclasses may override
    # Test Configs
    requires_valid_format: bool = False
    requires_query: bool = True
    tools_evaluator: bool = False

    MINIMAL_RESPONSE: List[Dict[str, Any]] = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "I have successfully sent you an email with the weather information for Seattle. The current weather is rainy with a temperature of 14\u00b0C.",
                    }
                ],
            },
        ]

    weather_tool_call_and_assistant_response: List[Dict[str, Any]] = [
            {
                "tool_call_id": "call_1",
                "role": "tool",
                "content": [{"type": "tool_result", "tool_result": {"weather": "Rainy, 14\u00b0C"}}],
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "I have successfully sent you an email with the weather information for Seattle. The current weather is rainy with a temperature of 14\u00b0C.",
                    }
                ],
            },
        ]

    email_tool_call_and_assistant_response: List[Dict[str, Any]] = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_2",
                        "name": "send_email",
                        "arguments": {
                            "recipient": "your_email@example.com",
                            "subject": "Weather Information for Seattle",
                            "body": "The current weather in Seattle is rainy with a temperature of 14\u00b0C.",
                        },
                    }
                ],
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "I have successfully sent you an email with the weather information for Seattle. The current weather is rainy with a temperature of 14\u00b0C.",
                    }
                ],
            },
        ]
    
    tool_results_without_arguments: List[Dict[str, Any]] = [
            {
                "tool_call_id": "call_1",
                "role": "tool",
                "content": [{"type": "tool_result", "tool_result": {"weather": "Rainy, 14\u00b0C"}}],
            },
            {
                "tool_call_id": "call_2",
                "role": "tool",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_result": {"message": "Email successfully sent to your_email@example.com."},
                    }
                ],
            },
        ]

    tool_results_with_arguments: List[Dict[str, Any]] = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "name": "fetch_weather",
                        "arguments": {"location": "Seattle"},
                    }
                ],
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "name": "send_email",
                        "arguments": {
                            "recipient": "your_email@example.com",
                            "subject": "Weather Information for Seattle",
                            "body": "The current weather in Seattle is rainy with a temperature of 14\u00b0C.",
                        },
                    }
                ],
            },
        ]

    # Tool-related test data (can be overridden by subclasses)
    VALID_TOOL_CALLS: List[Dict[str, Any]] = None
    INVALID_TOOL_CALLS: List[Dict[str, Any]] = None
    VALID_TOOL_DEFINITIONS: List[Dict[str, Any]] = None
    INVALID_TOOL_DEFINITIONS: List[Dict[str, Any]] = None

    # Common test data for query and response
    STRING_QUERY: str = "Can you send me an email to your_email@example.com with weather information for Seattle?"
    
    STRING_RESPONSE: str = "I have successfully sent you an email with the weather information for Seattle. The current weather is rainy with a temperature of 14\u00b0C."
    
    VALID_QUERY: List[Dict[str, Any]] = [
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": "Can you send me an email to your_email@example.com with weather information for Seattle?",
            }
        },
    ]

    VALID_RESPONSE: List[Dict[str, Any]] = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_1",
                        "name": "fetch_weather",
                        "arguments": {"location": "Seattle"},
                    }
                ],
            },
            {
                "tool_call_id": "call_1",
                "role": "tool",
                "content": [{"type": "tool_result", "tool_result": {"weather": "Rainy, 14\u00b0C"}}],
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "tool_call_id": "call_2",
                        "name": "send_email",
                        "arguments": {
                            "recipient": "your_email@example.com",
                            "subject": "Weather Information for Seattle",
                            "body": "The current weather in Seattle is rainy with a temperature of 14\u00b0C.",
                        },
                    }
                ],
            },
            {
                "tool_call_id": "call_2",
                "role": "tool",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_result": {"message": "Email successfully sent to your_email@example.com."},
                    }
                ],
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "I have successfully sent you an email with the weather information for Seattle. The current weather is rainy with a temperature of 14\u00b0C.",
                    }
                ],
            },
        ]

    INVALID_QUERY: List[Dict[str, Any]] = [
        {
            "user": "Can you send me an email to your_email@example.com with weather information for Seattle?",
        },
    ]

    INVALID_RESPONSE: List[Dict[str, Any]] = [
            {
                "tool_call": [
                    {
                        "name": "fetch_weather",
                        "arguments": {"location": "Seattle"},
                    }
                ],
            },
            {
                "tool_result": {"weather": "Rainy, 14\u00b0C"},
            },
            {
                "tool_call": [
                    {
                        "name": "send_email",
                        "arguments": {
                            "recipient": "your_email@example.com",
                            "subject": "Weather Information for Seattle",
                            "body": "The current weather in Seattle is rainy with a temperature of 14\u00b0C.",
                        },
                    }
                ],
            },
            {
                "tool_result": {"message": "Email successfully sent to your_email@example.com."},
            },
            {
                "assistant": "I have successfully sent you an email with the weather information for Seattle. The current weather is rainy with a temperature of 14\u00b0C.",
            },
        ]
    
    # ==================== All Valid ====================

    def test_all_valid_inputs(self, openai_client, model_deployment_name):
        """All inputs valid and in correct format."""
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=self.VALID_QUERY,
            response=self.VALID_RESPONSE,
            tool_calls=self.VALID_TOOL_CALLS,
            tool_definitions=self.VALID_TOOL_DEFINITIONS,
        )
        result_data = self._extract_and_print_result(run, outputs, "All Valid")

        self.assert_pass(result_data)

    # ==================== QUERY TESTS ====================

    def test_query_not_present(self, openai_client, model_deployment_name):
        """Query not present - evaluator raises exception."""
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=None,
            response=self.VALID_RESPONSE,
            tool_calls=self.VALID_TOOL_CALLS,
            tool_definitions=self.VALID_TOOL_DEFINITIONS,
        )
        result_data = self._extract_and_print_result(run, outputs, "Query Not Present")

        if self.requires_query:
            self.assert_error(result_data)
        else:
            self.assert_pass(result_data)

    def test_query_as_string(self, openai_client, model_deployment_name):
        """Query as string - should pass."""
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=self.STRING_QUERY,
            response=self.VALID_RESPONSE,
            tool_calls=self.VALID_TOOL_CALLS,
            tool_definitions=self.VALID_TOOL_DEFINITIONS,
        )
        result_data = self._extract_and_print_result(run, outputs, "Query String")

        self.assert_pass(result_data)

    def test_query_invalid_format(self, openai_client, model_deployment_name):
        """Query in invalid format - should pass."""
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=self.INVALID_QUERY,
            response=self.VALID_RESPONSE,
            tool_calls=self.VALID_TOOL_CALLS,
            tool_definitions=self.VALID_TOOL_DEFINITIONS,
        )
        result_data = self._extract_and_print_result(run, outputs, "Query Invalid")

        self.assert_pass(result_data)

    # ==================== RESPONSE TESTS ====================

    def test_response_not_present(self, openai_client, model_deployment_name):
        """Response not present - should return not applicable."""
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=self.VALID_QUERY,
            response=None,
            tool_calls=None,
            tool_definitions=self.VALID_TOOL_DEFINITIONS,
        )
        result_data = self._extract_and_print_result(run, outputs, "Response and Tool Calls Not Present")

        self.assert_error(result_data)

    def test_response_as_string(self, openai_client, model_deployment_name):
        """Response as string - should pass."""
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=self.VALID_QUERY,
            response=self.STRING_RESPONSE,
            tool_calls=None,
            tool_definitions=self.VALID_TOOL_DEFINITIONS,
        )
        result_data = self._extract_and_print_result(run, outputs, "Response String without Tool Calls")

        if self.requires_valid_format:  # If Tool Calls Evaluator
            self.assert_not_applicable(result_data)
        elif self.tools_evaluator:
            self.assert_pass_or_fail(result_data)
        else:
            self.assert_pass(result_data)

    def test_response_invalid_format(self, openai_client, model_deployment_name):
        """Response in invalid format - should return not_applicable."""
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=self.VALID_QUERY,
            response=self.INVALID_RESPONSE,
            tool_calls=None,
            tool_definitions=self.VALID_TOOL_DEFINITIONS,
        )
        result_data = self._extract_and_print_result(run, outputs, "Response Invalid without Tool Calls")

        if self.requires_valid_format:
            self.assert_error(result_data)
        else:
            self.assert_pass(result_data)
    
    def test_response_minimal_format(self, openai_client, model_deployment_name):
        """Response in minimal format - should pass."""
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=self.VALID_QUERY,
            response=self.MINIMAL_RESPONSE,
            tool_calls=None,
            tool_definitions=self.VALID_TOOL_DEFINITIONS,
        )
        result_data = self._extract_and_print_result(run, outputs, "Response Minimal without Tool Calls")

        self.assert_pass(result_data)
