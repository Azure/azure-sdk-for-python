"""
Unit tests for red_team.utils.constants module.
"""

import pytest
from azure.ai.evaluation.red_team._utils.constants import (
    BASELINE_IDENTIFIER,
    DATA_EXT,
    RESULTS_EXT,
    ATTACK_STRATEGY_COMPLEXITY_MAP,
    INTERNAL_TASK_TIMEOUT,
    TASK_STATUS,
)
from azure.ai.evaluation.red_team._attack_strategy import AttackStrategy
from azure.ai.evaluation.red_team._attack_objective_generator import RiskCategory
from azure.ai.evaluation import (
    ViolenceEvaluator,
    HateUnfairnessEvaluator,
    SexualEvaluator,
    SelfHarmEvaluator,
)


@pytest.mark.unittest
class TestBasicConstants:
    """Test basic constants are defined correctly."""

    def test_basic_constants(self):
        """Verify basic constants are defined correctly."""
        assert BASELINE_IDENTIFIER == "baseline"
        assert DATA_EXT == ".jsonl"
        assert RESULTS_EXT == ".json"
        assert INTERNAL_TASK_TIMEOUT == 120


@pytest.mark.unittest
class TestTaskStatusConstants:
    """Test task status constants are defined correctly."""

    def test_task_status_constants(self):
        """Verify task status constants are defined correctly."""
        assert TASK_STATUS["PENDING"] == "pending"
        assert TASK_STATUS["RUNNING"] == "running"
        assert TASK_STATUS["COMPLETED"] == "completed"
        assert TASK_STATUS["FAILED"] == "failed"
        assert TASK_STATUS["TIMEOUT"] == "timeout"
