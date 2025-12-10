# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Base class for behavioral tests of tool calls evaluators.
Tests various input scenarios: query, response, tool_definitions, and tool_calls.
"""

from base_tools_evaluator_behavior_test import BaseToolEvaluatorBehaviorTest


class BaseToolCallEvaluatorBehaviorTest(BaseToolEvaluatorBehaviorTest):
    """
    Base class for tool call evaluator behavioral tests with tool_calls.
    Extends BaseToolEvaluatorBehaviorTest with tool call support.
    Subclasses should implement:
    - evaluator_name: str - name of the evaluator (e.g., "tool_selection")
    - MINIMAL_RESPONSE: list - minimal valid response format for the evaluator
    - needs_arguments: bool - whether tool calls need arguments to be valid
    """
    
    # TODO: Remove if not needed
    needs_arguments = False
    
    MINIMAL_RESPONSE = None

    # Tool call test data
    VALID_TOOL_CALLS = [
        {
            "type": "tool_call",
            "tool_call_id": "call_1",
            "name": "fetch_weather",
            "arguments": {"location": "Seattle"},
        },
        {
            "type": "tool_call",
            "tool_call_id": "call_2",
            "name": "send_email",
            "arguments": {
                "recipient": "your_email@example.com",
                "subject": "Weather Information for Seattle",
                "body": "The current weather in Seattle is rainy with a temperature of 14\u00b0C.",
            },
        },
    ]

    INVALID_TOOL_CALLS = [
        {
            "name": "fetch_weather",
            "arguments": {"location": "Seattle"},
        },
        {
            "name": "send_email",
            "arguments": {
                "recipient": "your_email@example.com",
                "subject": "Weather Information for Seattle",
                "body": "The current weather in Seattle is rainy with a temperature of 14\u00b0C.",
            },
        },
    ]

    # ==================== OVERRIDE RESPONSE TESTS ====================
    
    def test_response_not_present(self, openai_client, model_deployment_name):
        """Response not present but tool_calls provided - should pass."""
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=self.VALID_QUERY,
            response=None,
            tool_calls=self.VALID_TOOL_CALLS,
            tool_definitions=self.VALID_TOOL_DEFINITIONS,
        )
        result_data = self._extract_and_print_result(run, outputs, "Response Not Present but Tool Calls Provided")

        self.assert_pass(result_data)
    
    def test_response_as_string(self, openai_client, model_deployment_name):
        """Response as string - should pass with explicit tool_calls."""
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=self.VALID_QUERY,
            response=self.STRING_RESPONSE,
            tool_calls=self.VALID_TOOL_CALLS,
            tool_definitions=self.VALID_TOOL_DEFINITIONS,
        )
        result_data = self._extract_and_print_result(run, outputs, "Response String With Tool Calls")

        self.assert_pass(result_data)

    def test_response_invalid_format(self, openai_client, model_deployment_name):
        """Response in invalid format - should pass with explicit tool_calls."""
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=self.VALID_QUERY,
            response=self.INVALID_RESPONSE,
            tool_calls=self.VALID_TOOL_CALLS,
            tool_definitions=self.VALID_TOOL_DEFINITIONS,
        )
        result_data = self._extract_and_print_result(run, outputs, "Response Invalid With Tool Calls")

        self.assert_pass(result_data)

    # ==================== RESPONSE AND TOOL CALLS TESTS ====================

    def test_response_and_tool_calls_not_present(self, openai_client, model_deployment_name):
        """Response and tool_calls not present - should return not applicable."""
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=self.VALID_QUERY,
            response=None,
            tool_calls=None,
            tool_definitions=self.VALID_TOOL_DEFINITIONS,
        )
        result_data = self._extract_and_print_result(run, outputs, "Response And Tool Calls Not Present")

        self.assert_not_applicable(result_data)

    def test_response_as_string_without_tool_calls(self, openai_client, model_deployment_name):
        """Response as string - should return not applicable."""
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=self.VALID_QUERY,
            response=self.STRING_RESPONSE,
            tool_calls=None,
            tool_definitions=self.VALID_TOOL_DEFINITIONS,
        )
        result_data = self._extract_and_print_result(run, outputs, "Response String Without Tool Calls")

        self.assert_not_applicable(result_data)

    def test_response_invalid_format_without_tool_calls(self, openai_client, model_deployment_name):
        """Response in invalid format - should return not_applicable."""
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=self.VALID_QUERY,
            response=self.INVALID_RESPONSE,
            tool_calls=None,
            tool_definitions=self.VALID_TOOL_DEFINITIONS,
        )
        result_data = self._extract_and_print_result(run, outputs, "Response Invalid Without Tool Calls")

        if self.requires_valid_format:
            self.assert_not_applicable(result_data)
        else:
            self.assert_pass(result_data)
    
    def test_response_minimal_format_without_tool_calls(self, openai_client, model_deployment_name):
        """Response in minimal format - should pass."""
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=self.VALID_QUERY,
            response=self.MINIMAL_RESPONSE,
            tool_calls=None,
            tool_definitions=self.VALID_TOOL_DEFINITIONS,
        )
        result_data = self._extract_and_print_result(run, outputs, "Response Minimal Without Tool Calls")

        self.assert_pass(result_data)

    # ==================== TOOL CALLS TESTS ====================

    def test_tool_calls_not_present(self, openai_client, model_deployment_name):
        """Tool calls not present with valid response - should pass."""
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=self.VALID_QUERY,
            response=self.VALID_RESPONSE,
            tool_calls=None,
            tool_definitions=self.VALID_TOOL_DEFINITIONS,
        )
        result_data = self._extract_and_print_result(run, outputs, "Tool Calls Not Present")

        self.assert_pass(result_data)

    def test_tool_calls_invalid_format(self, openai_client, model_deployment_name):
        """Tool calls in invalid format with valid response - should pass."""
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=self.VALID_QUERY,
            response=self.VALID_RESPONSE,
            tool_calls=self.INVALID_TOOL_CALLS,
            tool_definitions=self.VALID_TOOL_DEFINITIONS,
        )
        result_data = self._extract_and_print_result(run, outputs, "Tool Calls Invalid With Valid Response")

        self.assert_pass(result_data)

    def test_tool_calls_invalid_format_without_valid_response(self, openai_client, model_deployment_name):
        """Tool calls in invalid format without valid response - should return not_applicable."""
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=self.VALID_QUERY,
            response=None,
            tool_calls=self.INVALID_TOOL_CALLS,
            tool_definitions=self.VALID_TOOL_DEFINITIONS,
        )
        result_data = self._extract_and_print_result(run, outputs, "Tool Calls Invalid Without Valid Response")

        if self.requires_valid_format:
            self.assert_not_applicable(result_data)
        else:
            self.assert_pass(result_data)
            
    # =================== PARAMETERS TESTS ====================
    
    def remove_parameter_from_response(self, parameter_name):
        """Helper to remove a parameter from all tool calls in the response."""
        response = self.VALID_RESPONSE.copy()
        # Remove parameter from tool calls
        for message in response:
            for content in message.get("content", []):
                if parameter_name in content:
                    del content[parameter_name]
        
        return response

    def test_response_missing_name_parameters_without_tool_calls(self, openai_client, model_deployment_name):
        """Response is missing name parameter - should return not_applicable."""
        response = self.remove_parameter_from_response("name")
        
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=self.VALID_QUERY,
            response=response,
            tool_calls=None,
            tool_definitions=self.VALID_TOOL_DEFINITIONS,
        )
        result_data = self._extract_and_print_result(run, outputs, "Response Missing name Parameter Without Tool Calls")

        self.assert_not_applicable(result_data)

    def test_response_missing_arguments_parameters_without_tool_calls(self, openai_client, model_deployment_name):
        """Response is missing arguments parameter - should return not_applicable."""
        response = self.remove_parameter_from_response("arguments")
        
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=self.VALID_QUERY,
            response=response,
            tool_calls=None,
            tool_definitions=self.VALID_TOOL_DEFINITIONS,
        )
        result_data = self._extract_and_print_result(run, outputs, "Response Missing name Parameter Without Tool Calls")

        if self.needs_arguments:
            self.assert_not_applicable(result_data)
        else:
            self.assert_pass(result_data)
