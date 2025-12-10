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
