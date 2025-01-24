# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import enum
from typing import Literal
from azure.ai.evaluation._common._experimental import experimental


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
    EVALUATION_SDK = "_azureml.evaluation_sdk_name"


@experimental
class AggregationType(enum.Enum):
    """Defines how numeric evaluation results should be aggregated
    to produce a single value. Used by individual evaluators to combine per-turn results for
    a conversation-based input. In general, wherever this enum is used, it is also possible
    to directly assign the underlying aggregation function for more complex use cases.
    The 'custom' value is generally not an acceptable input, and should only be used as an output
    to indicate that a custom aggregation function has been injected."""

    MEAN = "mean"
    MAX = "max"
    MIN = "min"
    SUM = "sum"
    CUSTOM = "custom"


DEFAULT_EVALUATION_RESULTS_FILE_NAME = "evaluation_results.json"

CONTENT_SAFETY_DEFECT_RATE_THRESHOLD_DEFAULT = 4

PF_BATCH_TIMEOUT_SEC_DEFAULT = 3600
PF_BATCH_TIMEOUT_SEC = "PF_BATCH_TIMEOUT_SEC"
PF_DISABLE_TRACING = "PF_DISABLE_TRACING"

OTEL_EXPORTER_OTLP_TRACES_TIMEOUT = "OTEL_EXPORTER_OTLP_TRACES_TIMEOUT"
OTEL_EXPORTER_OTLP_TRACES_TIMEOUT_DEFAULT = 60

AZURE_OPENAI_TYPE: Literal["azure_openai"] = "azure_openai"

OPENAI_TYPE: Literal["openai"] = "openai"
