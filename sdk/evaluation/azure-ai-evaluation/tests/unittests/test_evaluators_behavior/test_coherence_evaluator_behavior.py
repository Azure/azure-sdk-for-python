# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Behavioral tests for Coherence Evaluator.
"""

import pytest
from base_evaluator_behavior_test import BaseEvaluatorBehaviorTest


@pytest.mark.unittest
class TestCoherenceEvaluatorBehavior(BaseEvaluatorBehaviorTest):
    """
    Behavioral tests for Coherence Evaluator.
    Tests different input formats and scenarios.
    """

    evaluator_name = "coherence"
