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
    
    # Test Configs
    requires_valid_format = False

    MINIMAL_RESPONSE = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "I have successfully sent you an email with the weather information for Seattle. The current weather is rainy with a temperature of 14\u00b0C.",
                    }
                ],
            },
        ]
