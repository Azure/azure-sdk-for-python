# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Behavioral tests for Fluency Evaluator.
"""

import pytest
from base_evaluator_behavior_test import BaseEvaluatorBehaviorTest


@pytest.mark.unittest
class TestFluencyEvaluatorBehavior(BaseEvaluatorBehaviorTest):
    """
    Behavioral tests for Fluency Evaluator.
    Tests different input formats and scenarios.
    """

    evaluator_name = "fluency"

    # Test Configs
    requires_query = False
