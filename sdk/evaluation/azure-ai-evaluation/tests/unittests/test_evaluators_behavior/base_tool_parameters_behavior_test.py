# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Base class for behavioral tests of tool calls evaluators.
Tests Parameters in tool calls: type, name, arguments.
"""

from base_tools_evaluator_behavior_test import BaseToolsEvaluatorBehaviorTest


class BaseToolParametersBehaviorTest(BaseToolsEvaluatorBehaviorTest):
    """
    Base class for tool parameters behavioral tests in tool_calls.
    Extends BaseToolsEvaluatorBehaviorTest with tool call support.
    Subclasses should implement:
    - evaluator_name: str - name of the evaluator (e.g., "tool_selection")
    Subclasses may override:
    - requires_arguments: bool - whether tool calls need arguments to be valid
    - requires_tool_definitions: bool - whether tool definitions are required
    - requires_query: bool - whether query is required
    - MINIMAL_RESPONSE: list - minimal valid response format for the evaluator
    """
    
    # Test Configs
    requires_arguments: bool = True
    
    def remove_parameter_from_response(self, parameter_name: str) -> list[dict]:
        """Helper to remove a parameter from all tool calls in the response."""
        response = self.VALID_RESPONSE.copy()
        # Remove parameter from tool calls
        for message in response:
            for content in message.get("content", []):
                if parameter_name in content:
                    del content[parameter_name]
        
        return response

    def test_response_missing_parameters_without_tool_calls(self, openai_client, model_deployment_name, parameter: str, requires_parameter: bool):
        """
        Response is missing a specific parameter - should return not_applicable or pass depending on requires_parameter flag.
        :parameter: The parameter to remove from the response.
        :requires_parameter: Whether the evaluator requires this parameter to be present.
        """
        response = self.remove_parameter_from_response(parameter)
        
        run, outputs = self._run_evaluation(
            self.evaluator_name,
            openai_client, model_deployment_name,
            query=self.VALID_QUERY,
            response=response,
            tool_calls=None,
            tool_definitions=self.VALID_TOOL_DEFINITIONS,
        )
        result_data = self._extract_and_print_result(run, outputs, f"Response Missing {parameter} Parameter Without Tool Calls")

        if requires_parameter:
            self.assert_error(result_data)
        else:
            self.assert_pass(result_data)

    # =================== PARAMETERS TESTS ====================
    
    def test_response_missing_type_parameters_without_tool_calls(self, openai_client, model_deployment_name):
        """Response is missing name parameter - should return not_applicable."""
        self.test_response_missing_parameters_without_tool_calls(
            openai_client, model_deployment_name,
            parameter="type",
            requires_parameter=True
        )

    def test_response_missing_name_parameters_without_tool_calls(self, openai_client, model_deployment_name):
        """Response is missing name parameter - should return not_applicable."""
        self.test_response_missing_parameters_without_tool_calls(
            openai_client, model_deployment_name,
            parameter="name",
            requires_parameter=True
        )

    def test_response_missing_arguments_parameters_without_tool_calls(self, openai_client, model_deployment_name):
        """Response is missing arguments parameter - should return not_applicable."""
        self.test_response_missing_parameters_without_tool_calls(
            openai_client, model_deployment_name,
            parameter="arguments",
            requires_parameter=self.requires_arguments
        )
