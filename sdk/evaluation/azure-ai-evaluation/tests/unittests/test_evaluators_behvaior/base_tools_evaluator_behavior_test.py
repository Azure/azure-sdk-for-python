# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Base class for behavioral tests of for tools evaluators.
Tests various input scenarios: query, response, and tool_definitions.
"""

from base_evaluator_behavior_test import BaseEvaluatorBehaviorTest


class BaseToolEvaluatorBehaviorTest(BaseEvaluatorBehaviorTest):
    """
    Base class for tool evaluator behavioral tests with tool_definitions.
    Extends BaseEvaluatorBehaviorTest with tool definition support.
    Subclasses should implement:
    - evaluator_name: str - name of the evaluator (e.g., "tool_output_utilization")
    - MINIMAL_RESPONSE: list - minimal valid response format for the evaluator
    """

    MINIMAL_RESPONSE = None

    # Tool definition test data
    VALID_TOOL_DEFINITIONS = [
        {
            "name": "fetch_weather",
            "description": "Fetches the weather information for the specified location.",
            "parameters": {
                "type": "object",
                "properties": {"location": {"type": "string"}},
            },
        },
        {
            "name": "send_email",
            "description": "Sends an email.",
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                },
            },
        },
    ]

    INVALID_TOOL_DEFINITIONS = [
        {
            "fetch_weather": {
                "description": "Fetches the weather information for the specified location.",
                "parameters": {
                    "type": "object",
                    "properties": {"location": {"type": "string"}},
                },
            }
        },
        {
            "send_email": {
                "description": "Sends an email.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "recipient": {"type": "string"},
                        "subject": {"type": "string"},
                        "body": {"type": "string"},
                    },
                },
            },
        },
    ]

    # ==================== OVERRIDE RESPONSE TESTS ====================
    
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

        if self.requires_valid_format:
            self.assert_not_applicable(result_data)
        else:
            self.assert_pass_or_fail(result_data)

    # ==================== TOOL DEFINITIONS TESTS ====================

    def test_tool_definitions_not_present(self, openai_client, model_deployment_name):
        """Tool definitions not present - should return not_applicable."""
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=self.VALID_QUERY,
            response=self.VALID_RESPONSE,
            tool_calls=self.VALID_TOOL_CALLS,
            tool_definitions=None,
        )
        result_data = self._extract_and_print_result(run, outputs, "Tool Definitions Not Present")

        self.assert_not_applicable(result_data)

    def test_tool_definitions_invalid_format(self, openai_client, model_deployment_name):
        """Tool definitions in invalid format - should return not_applicable."""
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=self.VALID_QUERY,
            response=self.VALID_RESPONSE,
            tool_calls=self.VALID_TOOL_CALLS,
            tool_definitions=self.INVALID_TOOL_DEFINITIONS,
        )
        result_data = self._extract_and_print_result(run, outputs, "Tool Definitions Invalid")

        if self.requires_valid_format:
            self.assert_not_applicable(result_data)
        else:
            self.assert_pass(result_data)