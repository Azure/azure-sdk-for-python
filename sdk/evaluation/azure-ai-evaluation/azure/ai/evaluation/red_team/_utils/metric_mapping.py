"""
Mapping utilities for metrics and risk categories in Red Team Agent.
"""

from typing import Union
from .._attack_objective_generator import _InternalRiskCategory, RiskCategory
from azure.ai.evaluation._constants import EvaluationMetrics, _InternalEvaluationMetrics
from azure.ai.evaluation._common.constants import Tasks, _InternalAnnotationTasks

# Mapping of risk categories to their corresponding evaluation metrics
# Note: For HateUnfairness, the mapping defaults to HATE_FAIRNESS, but the Sync API
# (used for all projects) requires HATE_UNFAIRNESS instead.
# This is handled dynamically in _evaluation_processor.py.
RISK_CATEGORY_METRIC_MAP = {
    RiskCategory.Violence: EvaluationMetrics.VIOLENCE,
    RiskCategory.HateUnfairness: EvaluationMetrics.HATE_FAIRNESS,
    RiskCategory.Sexual: EvaluationMetrics.SEXUAL,
    RiskCategory.SelfHarm: EvaluationMetrics.SELF_HARM,
    RiskCategory.ProtectedMaterial: EvaluationMetrics.PROTECTED_MATERIAL,
    RiskCategory.UngroundedAttributes: EvaluationMetrics.UNGROUNDED_ATTRIBUTES,
    _InternalRiskCategory.ECI: _InternalEvaluationMetrics.ECI,
    RiskCategory.CodeVulnerability: EvaluationMetrics.CODE_VULNERABILITY,
    RiskCategory.SensitiveDataLeakage: EvaluationMetrics.SENSITIVE_DATA_LEAKAGE,
    RiskCategory.TaskAdherence: EvaluationMetrics.TASK_ADHERENCE,
    RiskCategory.ProhibitedActions: EvaluationMetrics.PROHIBITED_ACTIONS,
}

RISK_CATEGORY_ANNOTATION_TASK_MAP = {
    RiskCategory.Violence: Tasks.CONTENT_HARM,
    RiskCategory.HateUnfairness: Tasks.CONTENT_HARM,
    RiskCategory.Sexual: Tasks.CONTENT_HARM,
    RiskCategory.SelfHarm: Tasks.CONTENT_HARM,
    RiskCategory.ProtectedMaterial: Tasks.PROTECTED_MATERIAL,
    RiskCategory.UngroundedAttributes: Tasks.UNGROUNDED_ATTRIBUTES,
    _InternalRiskCategory.ECI: _InternalAnnotationTasks.ECI,
    RiskCategory.CodeVulnerability: Tasks.CODE_VULNERABILITY,
    RiskCategory.SensitiveDataLeakage: Tasks.SENSITIVE_DATA_LEAKAGE,
    RiskCategory.TaskAdherence: Tasks.TASK_ADHERENCE,
    RiskCategory.ProhibitedActions: Tasks.PROHIBITED_ACTIONS,
}


def get_metric_from_risk_category(risk_category: Union[RiskCategory]) -> str:
    """Get the appropriate evaluation metric for a given risk category.

    :param risk_category: The risk category to map to an evaluation metric
    :type risk_category: Union[RiskCategory]
    :return: The corresponding evaluation metric
    :rtype: str
    """
    return RISK_CATEGORY_METRIC_MAP.get(risk_category, EvaluationMetrics.HATE_FAIRNESS)


def get_annotation_task_from_risk_category(risk_category: Union[RiskCategory]) -> str:
    """
    Get the appropriate annotation task for a given risk category.
    :param risk_category: The risk category to map to an annotation task
    :type risk_category: Union[RiskCategory]
    :return: The corresponding annotation task
    :rtype: str
    """
    return RISK_CATEGORY_ANNOTATION_TASK_MAP.get(risk_category, Tasks.CONTENT_HARM)


def get_attack_objective_from_risk_category(risk_category: Union[RiskCategory]) -> str:
    """Get the attack objective string for a given risk category.

    :param risk_category: The risk category to map to an attack objective
    :type risk_category: Union[RiskCategory]
    :return: The corresponding attack objective string
    :rtype: str
    """
    if risk_category == RiskCategory.UngroundedAttributes:
        return "isa"
    else:
        return risk_category.value
