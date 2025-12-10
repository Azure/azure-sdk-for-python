# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Behavioral tests for Groundedness Evaluator.
"""

import pytest
from base_evaluator_behavior_test import BaseEvaluatorBehaviorTest


@pytest.mark.unittest
class TestGroundednessEvaluatorBehavior(BaseEvaluatorBehaviorTest):
    """
    Behavioral tests for Groundedness Evaluator.
    Tests different input formats and scenarios.
    """

    evaluator_name = "groundedness"
    
    # Test Configs
    requires_query = False

    MINIMAL_RESPONSE = BaseEvaluatorBehaviorTest.weather_tool_call_and_assistant_response
