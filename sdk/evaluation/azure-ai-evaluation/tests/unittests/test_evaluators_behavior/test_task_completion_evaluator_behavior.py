# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Behavioral tests for Task Completion Evaluator.
"""

import pytest
from base_tools_evaluator_behavior_test import BaseToolsEvaluatorBehaviorTest


@pytest.mark.unittest
class TestTaskCompletionEvaluatorBehavior(BaseToolsEvaluatorBehaviorTest):
    """
    Behavioral tests for Task Completion Evaluator.
    Tests different input formats and scenarios.
    """

    evaluator_name = "task_completion"

    MINIMAL_RESPONSE = BaseToolsEvaluatorBehaviorTest.email_tool_call_and_assistant_response
