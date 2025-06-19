"""
Mapping utilities for metrics and risk categories in Red Team Agent.
"""

from .._attack_objective_generator import _InternalRiskCategory, RiskCategory
from azure.ai.evaluation._constants import EvaluationMetrics, _InternalEvaluationMetrics
from azure.ai.evaluation._common.constants import Tasks, _InternalAnnotationTasks

# Mapping of risk categories to their corresponding evaluation metrics
RISK_CATEGORY_METRIC_MAP = {
    RiskCategory.Violence: EvaluationMetrics.VIOLENCE,
    RiskCategory.HateUnfairness: EvaluationMetrics.HATE_FAIRNESS,
    RiskCategory.Sexual: EvaluationMetrics.SEXUAL,
    RiskCategory.SelfHarm: EvaluationMetrics.SELF_HARM,
    RiskCategory.ProtectedMaterial: EvaluationMetrics.PROTECTED_MATERIAL,
    _InternalRiskCategory.ECI: _InternalEvaluationMetrics.ECI,
    RiskCategory.CodeVulnerability: EvaluationMetrics.CODE_VULNERABILITY,
}

RISK_CATEGORY_ANNOTATION_TASK_MAP = {
    RiskCategory.Violence: Tasks.CONTENT_HARM,
    RiskCategory.HateUnfairness: Tasks.CONTENT_HARM,
    RiskCategory.Sexual: Tasks.CONTENT_HARM,
    RiskCategory.SelfHarm: Tasks.CONTENT_HARM,
    RiskCategory.ProtectedMaterial: Tasks.PROTECTED_MATERIAL,
    _InternalRiskCategory.ECI: _InternalAnnotationTasks.ECI,
    RiskCategory.CodeVulnerability: Tasks.CODE_VULNERABILITY,
}


def get_metric_from_risk_category(risk_category: RiskCategory) -> str:
    """Get the appropriate evaluation metric for a given risk category.

    :param risk_category: The risk category to map to an evaluation metric
    :type risk_category: RiskCategory
    :return: The corresponding evaluation metric
    :rtype: str
    """
    return RISK_CATEGORY_METRIC_MAP.get(risk_category, EvaluationMetrics.HATE_FAIRNESS)


def get_annotation_task_from_risk_category(risk_category: RiskCategory) -> str:
    """
    Get the appropriate annotation task for a given risk category.
    :param risk_category: The risk category to map to an annotation task
    :type risk_category: RiskCategory
    :return: The corresponding annotation task
    :rtype: str
    """
    return RISK_CATEGORY_ANNOTATION_TASK_MAP.get(risk_category, Tasks.CONTENT_HARM)
