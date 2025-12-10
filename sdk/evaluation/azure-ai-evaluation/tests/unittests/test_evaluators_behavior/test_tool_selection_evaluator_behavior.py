# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Behavioral tests for Tool Selection Evaluator using AIProjectClient.
Tests various input scenarios: query, response, tool_definitions, and tool_calls.
"""

import pytest
from base_tool_calls_evaluator_behavior_test import BaseToolCallEvaluatorBehaviorTest


@pytest.mark.unittest
class TestToolSelectionEvaluatorBehavior(BaseToolCallEvaluatorBehaviorTest):
    """
    Behavioral tests for Tool Selection Evaluator.
    Tests different input formats and scenarios.
    """

    evaluator_name = "tool_selection"
