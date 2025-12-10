# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Behavioral tests for Relevance Evaluator.
"""

import pytest
from base_evaluator_behavior_test import BaseEvaluatorBehaviorTest


@pytest.mark.unittest
class TestRelevanceEvaluatorBehavior(BaseEvaluatorBehaviorTest):
    """
    Behavioral tests for Relevance Evaluator.
    Tests different input formats and scenarios.
    """

    evaluator_name = "relevance"
