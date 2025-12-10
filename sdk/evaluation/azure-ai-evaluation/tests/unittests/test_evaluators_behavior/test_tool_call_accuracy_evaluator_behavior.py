# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Behavioral tests for Tool Call Accuracy Evaluator using AIProjectClient.
Tests various input scenarios: query, response, tool_definitions, and tool_calls.
"""

import pytest
from base_tool_calls_evaluator_behavior_test import BaseToolCallEvaluatorBehaviorTest


@pytest.mark.unittest
class TestToolCallAccuracyEvaluatorBehavior(BaseToolCallEvaluatorBehaviorTest):
    """
    Behavioral tests for Tool Call Accuracy Evaluator.
    Tests different input formats and scenarios.
    """

    evaluator_name = "tool_call_accuracy"
    
    MINIMAL_RESPONSE = BaseToolCallEvaluatorBehaviorTest.weather_tool_call_and_assistant_response