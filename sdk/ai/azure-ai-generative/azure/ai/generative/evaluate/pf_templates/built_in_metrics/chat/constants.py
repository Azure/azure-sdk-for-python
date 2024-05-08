from azureml.metrics import constants
from enum import Enum


class RAIService:
    """Define constants related to RAI service"""
    TIMEOUT = 120
    SLEEPTIME = 2
    HARM_SEVERITY_THRESHOLD = 4


class Metric:
    """Defines all metrics supported by RAI service"""
    # Content harm
    SelfHarm = "self_harm"
    Violence = "violence"
    Sexual = "sexual"
    HateUnfairness = "hate_unfairness"


class Tasks:
    """Defines types of annotation tasks supported by RAI Service."""
    CONTENT_HARM = "content harm"


class HarmSeverityLevel(Enum):
    VeryLow = "Very low"
    Low = "Low"
    Medium = "Medium"
    High = "High"


# Content harm metric set
CONTENT_HARM_METRICS = {
    Metric.SelfHarm,
    Metric.Violence,
    Metric.Sexual,
    Metric.HateUnfairness
}


RAG_EVALUATION_SET = constants.Metric.RAG_EVALUATION_SET
NON_RAG_EVALUATION_SET = {constants.Metric.GPTCoherence,
                          constants.Metric.GPTFluency}
QUALITY_METRIC_SET = RAG_EVALUATION_SET | NON_RAG_EVALUATION_SET
