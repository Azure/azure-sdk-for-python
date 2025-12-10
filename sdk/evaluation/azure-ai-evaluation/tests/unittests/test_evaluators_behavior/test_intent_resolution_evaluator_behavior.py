# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Behavioral tests for Intent Resolution Evaluator.
"""

import pytest
from base_tools_evaluator_behavior_test import BaseToolsEvaluatorBehaviorTest


@pytest.mark.unittest
class TestIntentResolutionEvaluatorBehavior(BaseToolsEvaluatorBehaviorTest):
    """
    Behavioral tests for Intent Resolution Evaluator.
    Tests different input formats and scenarios.
    """

    evaluator_name = "intent_resolution"
