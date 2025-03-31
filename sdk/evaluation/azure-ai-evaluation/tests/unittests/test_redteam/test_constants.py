"""
Unit tests for red_team.utils.constants module.
"""

import pytest
try:
    import pyrit
    has_pyrit = True
except ImportError:
    has_pyrit = False

if has_pyrit:
    from azure.ai.evaluation._red_team._utils.constants import (
        BASELINE_IDENTIFIER, DATA_EXT, RESULTS_EXT,
        ATTACK_STRATEGY_COMPLEXITY_MAP, RISK_CATEGORY_EVALUATOR_MAP,
        INTERNAL_TASK_TIMEOUT, TASK_STATUS
    )
    from azure.ai.evaluation._red_team._attack_strategy import AttackStrategy
    from azure.ai.evaluation._red_team._attack_objective_generator import RiskCategory
from azure.ai.evaluation import ViolenceEvaluator, HateUnfairnessEvaluator, SexualEvaluator, SelfHarmEvaluator


@pytest.mark.unittest
@pytest.mark.skipif(not has_pyrit, reason="redteam extra is not installed")
class TestBasicConstants:
    """Test basic constants are defined correctly."""

    def test_basic_constants(self):
        """Verify basic constants are defined correctly."""
        assert BASELINE_IDENTIFIER == "baseline"
        assert DATA_EXT == ".jsonl"
        assert RESULTS_EXT == ".json"
        assert INTERNAL_TASK_TIMEOUT == 120


@pytest.mark.unittest
@pytest.mark.skipif(not has_pyrit, reason="redteam extra is not installed")
class TestTaskStatusConstants:
    """Test task status constants are defined correctly."""
    
    def test_task_status_constants(self):
        """Verify task status constants are defined correctly."""
        assert TASK_STATUS["PENDING"] == "pending"
        assert TASK_STATUS["RUNNING"] == "running"
        assert TASK_STATUS["COMPLETED"] == "completed"
        assert TASK_STATUS["FAILED"] == "failed"
        assert TASK_STATUS["TIMEOUT"] == "timeout"


@pytest.mark.unittest
@pytest.mark.skipif(not has_pyrit, reason="redteam extra is not installed")
class TestRiskCategoryEvaluatorMap:
    """Test risk category evaluator mapping."""
    
    def test_risk_category_evaluator_map(self):
        """Verify risk category evaluator map includes all risk categories."""
        assert RiskCategory.Violence in RISK_CATEGORY_EVALUATOR_MAP
        assert RISK_CATEGORY_EVALUATOR_MAP[RiskCategory.Violence] == ViolenceEvaluator
        
        assert RiskCategory.HateUnfairness in RISK_CATEGORY_EVALUATOR_MAP
        assert RISK_CATEGORY_EVALUATOR_MAP[RiskCategory.HateUnfairness] == HateUnfairnessEvaluator
        
        assert RiskCategory.Sexual in RISK_CATEGORY_EVALUATOR_MAP
        assert RISK_CATEGORY_EVALUATOR_MAP[RiskCategory.Sexual] == SexualEvaluator
        
        assert RiskCategory.SelfHarm in RISK_CATEGORY_EVALUATOR_MAP
        assert RISK_CATEGORY_EVALUATOR_MAP[RiskCategory.SelfHarm] == SelfHarmEvaluator