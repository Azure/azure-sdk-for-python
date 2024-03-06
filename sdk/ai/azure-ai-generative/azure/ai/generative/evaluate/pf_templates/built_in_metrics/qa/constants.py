import sys
from enum import Enum
#import numpy as np

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
    HateFairness = "hate_fairness"

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
    Safe = 0
    Low = 1
    Medium = 2
    High = 3

class Tasks:
    """Defines types of annotation tasks supported by RAI Service."""
    CONTENT_HARM = "content harm"