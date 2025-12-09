# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Behavioral tests for Tool Selection Evaluator using AIProjectClient.
Tests various input scenarios: query, response, tool_definitions, and tool_calls.
"""

import pytest
from base_evaluator_behavior_test import BaseEvaluatorBehaviorTest


@pytest.mark.unittest
class TestToolSelectionEvaluatorBehavior(BaseEvaluatorBehaviorTest):
    """
    Behavioral tests for Tool Selection Evaluator.
    Tests different input formats and scenarios.
    """

    evaluator_name = "tool_selection"

    MINIMAL_RESPONSE = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "name": "fetch_weather",
                    }
                ],
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "name": "send_email",
                    }
                ],
            },
        ]
   
    def test_response_missing_parameters_without_tool_calls(self, openai_client, model_deployment_name):
        """Response is missing name parameter - should return not_applicable."""
        response = self.MINIMAL_RESPONSE.copy()
        # Remove 'name' from tool calls
        del response[0]["content"][0]["name"]
        del response[1]["content"][0]["name"]
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