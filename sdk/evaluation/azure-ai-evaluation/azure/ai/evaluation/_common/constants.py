# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from enum import Enum

from azure.core import CaseInsensitiveEnumMeta

PROMPT_BASED_REASON_EVALUATORS = ["coherence", "relevance", "retrieval", "groundedness", "fluency", "intent_resolution",
                                  "tool_call_accurate", "response_completeness", "task_adherence"]


class CommonConstants:
    """Define common constants."""

    DEFAULT_HTTP_TIMEOUT = 60


class RAIService:
    """Define constants related to RAI service"""

    TIMEOUT = 1800
    SLEEP_TIME = 2
    HARM_SEVERITY_THRESHOLD = 4


class HarmSeverityLevel(Enum):
    """Harm severity levels."""

    VeryLow = "Very low"
    Low = "Low"
    Medium = "Medium"
    High = "High"


class Tasks:
    """Defines types of annotation tasks supported by RAI Service."""

    CONTENT_HARM = "content harm"
    PROTECTED_MATERIAL = "protected material"
    XPIA = "xpia"
    GROUNDEDNESS = "groundedness"
    CODE_VULNERABILITY = "code vulnerability"
    UNGROUNDED_ATTRIBUTES = "inference sensitive attributes"


class _InternalAnnotationTasks:
    """Defines types of annotation tasks that are supported for internal use. Such tasks are
    experimental and subject to potential change or migration to the main Evaluation Metrics
    enum over time."""

    ECI = "eci"


class EvaluationMetrics(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Evaluation metrics to aid the RAI service in determining what
    metrics to request, and how to present them back to the user."""

    HATE_FAIRNESS = "hate_fairness"
    HATE_UNFAIRNESS = "hate_unfairness"
    VIOLENCE = "violence"
    SELF_HARM = "self_harm"
    SEXUAL = "sexual"
    PROTECTED_MATERIAL = "protected_material"
    XPIA = "xpia"
    GROUNDEDNESS = "generic_groundedness"
    CODE_VULNERABILITY = "code_vulnerability"
    UNGROUNDED_ATTRIBUTES = "ungrounded_attributes"


class _InternalEvaluationMetrics(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Evaluation metrics that are not publicly supported.
    These metrics are experimental and subject to potential change or migration to the main
    enum over time.
    """

    ECI = "eci"
