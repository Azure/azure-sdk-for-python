# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Behavioral tests for Tool Input Accuracy Evaluator.
"""

import pytest
from base_tool_calls_evaluator_behavior_test import BaseToolCallEvaluatorBehaviorTest


@pytest.mark.unittest
class TestToolInputAccuracyEvaluatorBehavior(BaseToolCallEvaluatorBehaviorTest):
    """
    Behavioral tests for Tool Input Accuracy Evaluator.
    Tests different input formats and scenarios.
    """

    evaluator_name = "tool_input_accuracy"

    MINIMAL_RESPONSE = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "name": "fetch_weather",
                        "arguments": {"location": "Seattle"},
                    }
                ],
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_call",
                        "name": "send_email",
                        "arguments": {
                            "recipient": "your_email@example.com",
                            "subject": "Weather Information for Seattle",
                            "body": "The current weather in Seattle is rainy with a temperature of 14\u00b0C.",
                        },
                    }
                ],
            },
        ]
   