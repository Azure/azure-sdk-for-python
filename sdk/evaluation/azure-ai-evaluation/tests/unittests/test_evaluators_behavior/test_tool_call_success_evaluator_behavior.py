# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Behavioral tests for Tool Call Success Evaluator.
"""

import pytest
from base_tools_evaluator_behavior_test import BaseToolsEvaluatorBehaviorTest


@pytest.mark.unittest
class TestToolCallSuccessEvaluatorBehavior(BaseToolsEvaluatorBehaviorTest):
    """
    Behavioral tests for Tool Call Success Evaluator.
    Tests different input formats and scenarios.
    """

    evaluator_name = "tool_call_success"

    # Test Configs
    requires_query = False

    MINIMAL_RESPONSE = BaseToolsEvaluatorBehaviorTest.tool_results_without_arguments
