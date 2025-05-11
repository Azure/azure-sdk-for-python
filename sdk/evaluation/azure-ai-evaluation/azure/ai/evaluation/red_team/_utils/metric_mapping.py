"""
Mapping utilities for metrics and risk categories in Red Team Agent.
"""
from .._attack_objective_generator import RiskCategory
from azure.ai.evaluation._constants import EvaluationMetrics, _InternalEvaluationMetrics

# Mapping of risk categories to their corresponding evaluation metrics
RISK_CATEGORY_METRIC_MAP = {
    RiskCategory.Violence: EvaluationMetrics.VIOLENCE,
    RiskCategory.HateUnfairness: EvaluationMetrics.HATE_UNFAIRNESS,
    RiskCategory.Sexual: EvaluationMetrics.SEXUAL,
    RiskCategory.SelfHarm: EvaluationMetrics.SELF_HARM,
    RiskCategory.ProtectedMaterial: EvaluationMetrics.PROTECTED_MATERIAL,
    RiskCategory.ECI: _InternalEvaluationMetrics.ECI,
    RiskCategory.CodeVulnerability: EvaluationMetrics.CODE_VULNERABILITY,
}

def get_metric_from_risk_category(risk_category: RiskCategory) -> str:
    """Get the appropriate evaluation metric for a given risk category.
    
    :param risk_category: The risk category to map to an evaluation metric
    :type risk_category: RiskCategory
    :return: The corresponding evaluation metric
    :rtype: str
    """
    return RISK_CATEGORY_METRIC_MAP.get(risk_category, EvaluationMetrics.HATE_UNFAIRNESS)
