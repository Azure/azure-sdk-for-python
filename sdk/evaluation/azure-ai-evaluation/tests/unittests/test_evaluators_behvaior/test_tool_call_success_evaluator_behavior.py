# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Behavioral tests for Tool Call Success Evaluator.
"""

import pytest
from base_tools_evaluator_behavior_test import BaseToolEvaluatorBehaviorTest


@pytest.mark.unittest
class TestToolCallSuccessEvaluatorBehavior(BaseToolEvaluatorBehaviorTest):
    """
    Behavioral tests for Tool Call Success Evaluator.
    Tests different input formats and scenarios.
    """

    evaluator_name = "tool_call_success"

    # Test Configs
    requires_valid_format = False
    requires_query = False

    MINIMAL_RESPONSE = [
            {
                "tool_call_id": "call_1",
                "role": "tool",
                "content": [{"type": "tool_result", "tool_result": {"weather": "Rainy, 14\u00b0C"}}],
            },
            {
                "tool_call_id": "call_2",
                "role": "tool",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_result": {"message": "Email successfully sent to your_email@example.com."},
                    }
                ],
            },
        ]
