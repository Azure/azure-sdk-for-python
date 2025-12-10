# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Behavioral tests for Tool Output Utilization Evaluator.
"""

import pytest
from base_tools_evaluator_behavior_test import BaseToolEvaluatorBehaviorTest
from base_evaluator_behavior_test import BaseEvaluatorBehaviorTest


@pytest.mark.unittest
class TestToolOutputUtilizationEvaluatorBehavior(BaseToolEvaluatorBehaviorTest):
    """
    Behavioral tests for Tool Output Utilization Evaluator.
    Tests different input formats and scenarios.
    """

    evaluator_name = "tool_output_utilization"
    
    # Test Configs
    requires_valid_format = False

    MINIMAL_RESPONSE = BaseEvaluatorBehaviorTest.VALID_RESPONSE
