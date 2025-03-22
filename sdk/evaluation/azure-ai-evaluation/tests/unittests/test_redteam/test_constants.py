"""
Unit tests for red_team_agent.utils.constants module.
"""

import pytest
from azure.ai.evaluation.red_team_agent.utils.constants import (
    BASELINE_IDENTIFIER, DATA_EXT, RESULTS_EXT,
    ATTACK_STRATEGY_COMPLEXITY_MAP, RISK_CATEGORY_EVALUATOR_MAP,
    INTERNAL_TASK_TIMEOUT, TASK_STATUS
)
from azure.ai.evaluation.red_team_agent.attack_strategy import AttackStrategy
from azure.ai.evaluation.red_team_agent.attack_objective_generator import RiskCategory
from azure.ai.evaluation import ViolenceEvaluator, HateUnfairnessEvaluator, SexualEvaluator, SelfHarmEvaluator


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


@pytest.mark.unittest
class TestAttackStrategyComplexityMap:
    """Test attack strategy complexity mapping."""
    
    def test_attack_strategy_complexity_map(self):
        """Verify attack strategy complexity map includes all expected strategies."""
        # Check baseline strategy
        assert str(AttackStrategy.Baseline.value) in ATTACK_STRATEGY_COMPLEXITY_MAP
        assert ATTACK_STRATEGY_COMPLEXITY_MAP[str(AttackStrategy.Baseline.value)] == "baseline"
        
        # Check easy strategies
        assert str(AttackStrategy.EASY.value) in ATTACK_STRATEGY_COMPLEXITY_MAP
        assert ATTACK_STRATEGY_COMPLEXITY_MAP[str(AttackStrategy.EASY.value)] == "easy"
        
        # Check moderate strategies
        assert str(AttackStrategy.MODERATE.value) in ATTACK_STRATEGY_COMPLEXITY_MAP
        assert ATTACK_STRATEGY_COMPLEXITY_MAP[str(AttackStrategy.MODERATE.value)] == "moderate"
        
        # Check difficult strategies
        assert str(AttackStrategy.DIFFICULT.value) in ATTACK_STRATEGY_COMPLEXITY_MAP
        assert ATTACK_STRATEGY_COMPLEXITY_MAP[str(AttackStrategy.DIFFICULT.value)] == "difficult"

        # Check specific strategy (Base64)
        assert str(AttackStrategy.Base64.value) in ATTACK_STRATEGY_COMPLEXITY_MAP
        assert ATTACK_STRATEGY_COMPLEXITY_MAP[str(AttackStrategy.Base64.value)] == "difficult"


@pytest.mark.unittest
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