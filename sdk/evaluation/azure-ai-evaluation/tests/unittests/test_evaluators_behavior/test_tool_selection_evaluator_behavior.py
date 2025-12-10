# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Behavioral tests for Tool Selection Evaluator using AIProjectClient.
Tests various input scenarios: query, response, tool_definitions, and tool_calls.
"""

import pytest
from base_tool_parameters_behavior_test import BaseToolParametersBehaviorTest

@pytest.mark.unittest
class TestToolSelectionEvaluatorBehavior(BaseToolParametersBehaviorTest):
    """
    Behavioral tests for Tool Selection Evaluator.
    Tests different input formats and scenarios.
    """

    evaluator_name = "tool_selection"

    # Test Configs
    requires_valid_format = True
    requires_tool_definitions = True
    needs_arguments = False
