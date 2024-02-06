from azureml.metrics import constants

class RAIService:
    """Define constants related to RAI service"""
    API_BASE = "https://int.api.azureml-test.ms/raisvc/v1.0/subscriptions"
    TIMEOUT = 1800
    SLEEPTIME = 2

class Metric:
    """Defines all metrics supported by RAI service"""
    # Content harm
    SelfHarm = "self_harm"
    Violence = "violence"
    Sexual = "sexual"
    HateFairness = "hate_fairness"

class Tasks:
    """Defines types of annotation tasks supported by RAI Service."""
    CONTENT_HARM = "content harm"

# Content harm metric set
CONTENT_HARM_METRICS = {
    Metric.SelfHarm,
    Metric.Violence,
    Metric.Sexual,
    Metric.HateFairness
}

RAG_EVALUATION_SET = constants.Metric.RAG_EVALUATION_SET
NON_RAG_EAVLUATION_SET = {constants.Metric.GPTCoherence, constants.Metric.GPTFluency}
QUALITY_METRIC_SET = RAG_EVALUATION_SET | NON_RAG_EAVLUATION_SET
