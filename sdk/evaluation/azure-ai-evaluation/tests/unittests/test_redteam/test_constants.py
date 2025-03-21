"""
Unit tests for red_team_agent.utils.constants module.
"""

import pytest
from azure.ai.evaluation.red_team_agent.utils.constants import (
    BASELINE_IDENTIFIER, DATA_EXT, RESULTS_EXT,
    ATTACK_STRATEGY_COMPLEXITY_MAP, RISK_CATEGORY_EVALUATOR_MAP,
    INTERNAL_TASK_TIMEOUT, TASK_STATUS, DUCK_DB
)
from azure.ai.evaluation.red_team_agent.attack_strategy import AttackStrategy
from azure.ai.evaluation.red_team_agent.attack_objective_generator import RiskCategory
from azure.ai.evaluation._evaluators import ViolenceEvaluator, HateUnfairnessEvaluator, SexualEvaluator, SelfHarmEvaluator


def test_basic_constants():
    """Verify basic constants are defined correctly."""
    assert BASELINE_IDENTIFIER == "Baseline"
    assert DATA_EXT == ".jsonl"
    assert RESULTS_EXT == ".jsonl"
    assert DUCK_DB == "duckdb"
    assert INTERNAL_TASK_TIMEOUT == 120


def test_task_status_constants():
    """Verify task status constants are defined correctly."""
    assert TASK_STATUS["PENDING"] == "PENDING"
    assert TASK_STATUS["RUNNING"] == "RUNNING"
    assert TASK_STATUS["COMPLETED"] == "COMPLETED"
    assert TASK_STATUS["FAILED"] == "FAILED"
    assert TASK_STATUS["TIMEOUT"] == "TIMEOUT"


def test_attack_strategy_complexity_map():
    """Verify attack strategy complexity map includes all expected strategies."""
    # Check baseline strategy
    assert str(AttackStrategy.Baseline.value) in ATTACK_STRATEGY_COMPLEXITY_MAP
    assert ATTACK_STRATEGY_COMPLEXITY_MAP[str(AttackStrategy.Baseline.value)] == "baseline"
    
    # Check easy strategies
    assert str(AttackStrategy.Base64.value) in ATTACK_STRATEGY_COMPLEXITY_MAP
    assert ATTACK_STRATEGY_COMPLEXITY_MAP[str(AttackStrategy.Base64.value)] == "easy"
    assert str(AttackStrategy.EASY.value) in ATTACK_STRATEGY_COMPLEXITY_MAP
    assert ATTACK_STRATEGY_COMPLEXITY_MAP[str(AttackStrategy.EASY.value)] == "easy"
    
    # Check moderate strategies
    assert str(AttackStrategy.MODERATE.value) in ATTACK_STRATEGY_COMPLEXITY_MAP
    assert ATTACK_STRATEGY_COMPLEXITY_MAP[str(AttackStrategy.MODERATE.value)] == "moderate"
    
    # Check difficult strategies
    assert str(AttackStrategy.DIFFICULT.value) in ATTACK_STRATEGY_COMPLEXITY_MAP
    assert ATTACK_STRATEGY_COMPLEXITY_MAP[str(AttackStrategy.DIFFICULT.value)] == "difficult"


def test_risk_category_evaluator_map():
    """Verify risk category evaluator map includes all risk categories."""
    assert RiskCategory.Violence in RISK_CATEGORY_EVALUATOR_MAP
    assert RISK_CATEGORY_EVALUATOR_MAP[RiskCategory.Violence] == ViolenceEvaluator
    
    assert RiskCategory.HateUnfairness in RISK_CATEGORY_EVALUATOR_MAP
    assert RISK_CATEGORY_EVALUATOR_MAP[RiskCategory.HateUnfairness] == HateUnfairnessEvaluator
    
    assert RiskCategory.Sexual in RISK_CATEGORY_EVALUATOR_MAP
    assert RISK_CATEGORY_EVALUATOR_MAP[RiskCategory.Sexual] == SexualEvaluator
    
    assert RiskCategory.SelfHarm in RISK_CATEGORY_EVALUATOR_MAP
    assert RISK_CATEGORY_EVALUATOR_MAP[RiskCategory.SelfHarm] == SelfHarmEvaluator