# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Literal


class EvaluationMetrics:
    """Metrics for model evaluation."""

    GROUNDEDNESS = "groundedness"
    RELEVANCE = "relevance"
    COHERENCE = "coherence"
    FLUENCY = "fluency"
    SIMILARITY = "similarity"
    F1_SCORE = "f1_score"
    RETRIEVAL_SCORE = "retrieval_score"
    HATE_FAIRNESS = "hate_fairness"
    HATE_UNFAIRNESS = "hate_unfairness"
    VIOLENCE = "violence"
    SELF_HARM = "self_harm"
    SEXUAL = "sexual"
    PROTECTED_MATERIAL = "protected_material"
    XPIA = "xpia"


class _InternalEvaluationMetrics:
    """Evaluation metrics that are not publicly supported.
    These metrics are experimental and subject to potential change or migration to the main
    enum over time.
    """

    ECI = "eci"


class Prefixes:
    """Column prefixes for inputs and outputs."""

    INPUTS = "inputs."
    OUTPUTS = "outputs."
    TSG_OUTPUTS = "__outputs."


class DefaultOpenEncoding:
    """Enum that captures SDK's default values for the encoding param of open(...)"""

    READ = "utf-8-sig"
    """SDK Default Encoding when reading a file"""
    WRITE = "utf-8"
    """SDK Default Encoding when writing a file"""


class EvaluationRunProperties:
    """Defines properties used to identify an evaluation run by UI"""

    RUN_TYPE = "runType"
    EVALUATION_RUN = "_azureml.evaluation_run"


DEFAULT_EVALUATION_RESULTS_FILE_NAME = "evaluation_results.json"

CONTENT_SAFETY_DEFECT_RATE_THRESHOLD_DEFAULT = 4

PF_BATCH_TIMEOUT_SEC_DEFAULT = 3600
PF_BATCH_TIMEOUT_SEC = "PF_BATCH_TIMEOUT_SEC"
PF_DISABLE_TRACING = "PF_DISABLE_TRACING"

OTEL_EXPORTER_OTLP_TRACES_TIMEOUT = "OTEL_EXPORTER_OTLP_TRACES_TIMEOUT"
OTEL_EXPORTER_OTLP_TRACES_TIMEOUT_DEFAULT = 60

AZURE_OPENAI_TYPE: Literal["azure_openai"] = "azure_openai"

OPENAI_TYPE: Literal["openai"] = "openai"
