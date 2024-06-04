from enum import Enum


class RAIService:
    """Define constants related to RAI service"""
    TIMEOUT = 1800
    SLEEPTIME = 2
    HARM_SEVERITY_THRESHOLD = 4


class Metric:
    """Defines all metrics supported by RAI service"""
    Metrics = "metrics"

    # Content harm
    SelfHarm = "self_harm"
    Violence = "violence"
    Sexual = "sexual"
    HateFairness = "hate_unfairness"

    QUALITY_METRICS = {
        "gpt_groundedness",
        "gpt_similarity",
        "gpt_fluency",
        "gpt_coherence",
        "gpt_relevance",
        "f1_score"
        }

    # Content harm metric set
    CONTENT_HARM_METRICS = {
        SelfHarm,
        Violence,
        Sexual,
        HateFairness
    }


class HarmSeverityLevel(Enum):
    VeryLow = "Very low"
    Low = "Low"
    Medium = "Medium"
    High = "High"


class Tasks:
    """Defines types of annotation tasks supported by RAI Service."""
    CONTENT_HARM = "content harm"
