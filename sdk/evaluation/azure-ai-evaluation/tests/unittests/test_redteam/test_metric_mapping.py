"""
Unit tests for red_team._utils.metric_mapping module.
"""

import pytest
from azure.ai.evaluation.red_team._utils.metric_mapping import (
    RISK_CATEGORY_METRIC_MAP,
    RISK_CATEGORY_ANNOTATION_TASK_MAP,
    get_metric_from_risk_category,
    get_annotation_task_from_risk_category,
    get_attack_objective_from_risk_category,
)
from azure.ai.evaluation.red_team._attack_objective_generator import (
    RiskCategory,
    _InternalRiskCategory,
)
from azure.ai.evaluation._constants import EvaluationMetrics, _InternalEvaluationMetrics
from azure.ai.evaluation._common.constants import Tasks, _InternalAnnotationTasks


@pytest.mark.unittest
class TestRiskCategoryMetricMap:
    """Test RISK_CATEGORY_METRIC_MAP contains all expected entries."""

    @pytest.mark.parametrize(
        "risk_category, expected_metric",
        [
            (RiskCategory.Violence, EvaluationMetrics.VIOLENCE),
            (RiskCategory.HateUnfairness, EvaluationMetrics.HATE_UNFAIRNESS),
            (RiskCategory.Sexual, EvaluationMetrics.SEXUAL),
            (RiskCategory.SelfHarm, EvaluationMetrics.SELF_HARM),
            (RiskCategory.ProtectedMaterial, EvaluationMetrics.PROTECTED_MATERIAL),
            (RiskCategory.UngroundedAttributes, EvaluationMetrics.UNGROUNDED_ATTRIBUTES),
            (_InternalRiskCategory.ECI, _InternalEvaluationMetrics.ECI),
            (RiskCategory.CodeVulnerability, EvaluationMetrics.CODE_VULNERABILITY),
            (RiskCategory.SensitiveDataLeakage, EvaluationMetrics.SENSITIVE_DATA_LEAKAGE),
            (RiskCategory.TaskAdherence, EvaluationMetrics.TASK_ADHERENCE),
            (RiskCategory.ProhibitedActions, EvaluationMetrics.PROHIBITED_ACTIONS),
        ],
    )
    def test_metric_map_entry(self, risk_category, expected_metric):
        """Verify each risk category maps to the correct evaluation metric."""
        assert RISK_CATEGORY_METRIC_MAP[risk_category] == expected_metric

    def test_metric_map_size(self):
        """Verify the metric map contains exactly 11 entries."""
        assert len(RISK_CATEGORY_METRIC_MAP) == 11


@pytest.mark.unittest
class TestRiskCategoryAnnotationTaskMap:
    """Test RISK_CATEGORY_ANNOTATION_TASK_MAP contains all expected entries."""

    @pytest.mark.parametrize(
        "risk_category, expected_task",
        [
            (RiskCategory.Violence, Tasks.CONTENT_HARM),
            (RiskCategory.HateUnfairness, Tasks.CONTENT_HARM),
            (RiskCategory.Sexual, Tasks.CONTENT_HARM),
            (RiskCategory.SelfHarm, Tasks.CONTENT_HARM),
            (RiskCategory.ProtectedMaterial, Tasks.PROTECTED_MATERIAL),
            (RiskCategory.UngroundedAttributes, Tasks.UNGROUNDED_ATTRIBUTES),
            (_InternalRiskCategory.ECI, _InternalAnnotationTasks.ECI),
            (RiskCategory.CodeVulnerability, Tasks.CODE_VULNERABILITY),
            (RiskCategory.SensitiveDataLeakage, Tasks.SENSITIVE_DATA_LEAKAGE),
            (RiskCategory.TaskAdherence, Tasks.TASK_ADHERENCE),
            (RiskCategory.ProhibitedActions, Tasks.PROHIBITED_ACTIONS),
        ],
    )
    def test_annotation_task_map_entry(self, risk_category, expected_task):
        """Verify each risk category maps to the correct annotation task."""
        assert RISK_CATEGORY_ANNOTATION_TASK_MAP[risk_category] == expected_task

    def test_annotation_task_map_size(self):
        """Verify the annotation task map contains exactly 11 entries."""
        assert len(RISK_CATEGORY_ANNOTATION_TASK_MAP) == 11

    def test_content_harm_categories(self):
        """Verify Violence, HateUnfairness, Sexual, SelfHarm all map to CONTENT_HARM."""
        content_harm_categories = [
            RiskCategory.Violence,
            RiskCategory.HateUnfairness,
            RiskCategory.Sexual,
            RiskCategory.SelfHarm,
        ]
        for category in content_harm_categories:
            assert RISK_CATEGORY_ANNOTATION_TASK_MAP[category] == Tasks.CONTENT_HARM


@pytest.mark.unittest
class TestGetMetricFromRiskCategory:
    """Test get_metric_from_risk_category function."""

    @pytest.mark.parametrize(
        "risk_category, expected_metric",
        [
            (RiskCategory.Violence, EvaluationMetrics.VIOLENCE),
            (RiskCategory.HateUnfairness, EvaluationMetrics.HATE_UNFAIRNESS),
            (RiskCategory.Sexual, EvaluationMetrics.SEXUAL),
            (RiskCategory.SelfHarm, EvaluationMetrics.SELF_HARM),
            (RiskCategory.ProtectedMaterial, EvaluationMetrics.PROTECTED_MATERIAL),
            (RiskCategory.UngroundedAttributes, EvaluationMetrics.UNGROUNDED_ATTRIBUTES),
            (_InternalRiskCategory.ECI, _InternalEvaluationMetrics.ECI),
            (RiskCategory.CodeVulnerability, EvaluationMetrics.CODE_VULNERABILITY),
            (RiskCategory.SensitiveDataLeakage, EvaluationMetrics.SENSITIVE_DATA_LEAKAGE),
            (RiskCategory.TaskAdherence, EvaluationMetrics.TASK_ADHERENCE),
            (RiskCategory.ProhibitedActions, EvaluationMetrics.PROHIBITED_ACTIONS),
        ],
    )
    def test_known_risk_category(self, risk_category, expected_metric):
        """Verify known risk categories return their mapped metric."""
        assert get_metric_from_risk_category(risk_category) == expected_metric

    def test_unknown_risk_category_returns_default(self):
        """Verify unknown risk category falls back to HATE_UNFAIRNESS."""
        result = get_metric_from_risk_category("nonexistent_category")
        assert result == EvaluationMetrics.HATE_UNFAIRNESS


@pytest.mark.unittest
class TestGetAnnotationTaskFromRiskCategory:
    """Test get_annotation_task_from_risk_category function."""

    @pytest.mark.parametrize(
        "risk_category, expected_task",
        [
            (RiskCategory.Violence, Tasks.CONTENT_HARM),
            (RiskCategory.HateUnfairness, Tasks.CONTENT_HARM),
            (RiskCategory.Sexual, Tasks.CONTENT_HARM),
            (RiskCategory.SelfHarm, Tasks.CONTENT_HARM),
            (RiskCategory.ProtectedMaterial, Tasks.PROTECTED_MATERIAL),
            (RiskCategory.UngroundedAttributes, Tasks.UNGROUNDED_ATTRIBUTES),
            (_InternalRiskCategory.ECI, _InternalAnnotationTasks.ECI),
            (RiskCategory.CodeVulnerability, Tasks.CODE_VULNERABILITY),
            (RiskCategory.SensitiveDataLeakage, Tasks.SENSITIVE_DATA_LEAKAGE),
            (RiskCategory.TaskAdherence, Tasks.TASK_ADHERENCE),
            (RiskCategory.ProhibitedActions, Tasks.PROHIBITED_ACTIONS),
        ],
    )
    def test_known_risk_category(self, risk_category, expected_task):
        """Verify known risk categories return their mapped annotation task."""
        assert get_annotation_task_from_risk_category(risk_category) == expected_task

    def test_unknown_risk_category_returns_default(self):
        """Verify unknown risk category falls back to CONTENT_HARM."""
        result = get_annotation_task_from_risk_category("nonexistent_category")
        assert result == Tasks.CONTENT_HARM


@pytest.mark.unittest
class TestGetAttackObjectiveFromRiskCategory:
    """Test get_attack_objective_from_risk_category function."""

    def test_ungrounded_attributes_returns_isa(self):
        """Verify UngroundedAttributes returns 'isa' instead of its enum value."""
        result = get_attack_objective_from_risk_category(RiskCategory.UngroundedAttributes)
        assert result == "isa"

    @pytest.mark.parametrize(
        "risk_category",
        [
            RiskCategory.Violence,
            RiskCategory.HateUnfairness,
            RiskCategory.Sexual,
            RiskCategory.SelfHarm,
            RiskCategory.ProtectedMaterial,
            RiskCategory.CodeVulnerability,
            RiskCategory.SensitiveDataLeakage,
            RiskCategory.TaskAdherence,
            RiskCategory.ProhibitedActions,
        ],
    )
    def test_non_ungrounded_returns_enum_value(self, risk_category):
        """Verify non-UngroundedAttributes categories return their enum value."""
        result = get_attack_objective_from_risk_category(risk_category)
        assert result == risk_category.value

    def test_internal_eci_returns_enum_value(self):
        """Verify _InternalRiskCategory.ECI returns its enum value."""
        result = get_attack_objective_from_risk_category(_InternalRiskCategory.ECI)
        assert result == _InternalRiskCategory.ECI.value
        assert result == "eci"

    def test_ungrounded_attributes_value_differs_from_isa(self):
        """Confirm the special case is needed: the enum value is not 'isa'."""
        assert RiskCategory.UngroundedAttributes.value != "isa"
        assert RiskCategory.UngroundedAttributes.value == "ungrounded_attributes"
