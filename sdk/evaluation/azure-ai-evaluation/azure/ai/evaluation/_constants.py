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
    ARTWORK = "artwork"
    FICTIONAL_CHARACTERS = "fictional_characters"
    LOGOS_AND_BRANDS = "logos_and_brands"
    XPIA = "xpia"
    CODE_VULNERABILITY = "code_vulnerability"
    UNGROUNDED_ATTRIBUTES = "ungrounded_attributes"
    SENSITIVE_DATA_LEAKAGE = "sensitive_data_leakage"
    TASK_ADHERENCE = "task_adherence"
    PROHIBITED_ACTIONS = "prohibited_actions"


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
    NAME_MAP = "_azureml.evaluation_name_map"
    NAME_MAP_LENGTH = "_azureml.evaluation_name_map_length"


@experimental
class _AggregationType(enum.Enum):
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


class TokenScope(str, enum.Enum):
    """Defines the scope of the token used to access Azure resources."""

    DEFAULT_AZURE_MANAGEMENT = "https://management.azure.com/.default"
    COGNITIVE_SERVICES_MANAGEMENT = "https://ai.azure.com/.default"
    AZURE_ML = "https://ml.azure.com/.default"


class _EvaluatorMetricMapping:
    """
    Static mapping of evaluator names to their metric names, based on assets.json.
    The 'builtin.' prefix is removed from the evaluator name keys.
    If an evaluator maps to multiple metrics, all metric names are included in the list, and the first one is considered the primary metric.
    """

    EVALUATOR_NAME_METRICS_MAPPINGS = {
        "bleu_score": ["bleu"],
        "coherence": ["coherence"],
        "document_retrieval": [
            "xdcg@3",
            "ndcg@3",
            "fidelity",
            "top1_relevance",
            "top3_max_relevance",
            "holes",
            "holes_ratio",
            "total_retrieved_documents",
            "total_ground_truth_documents",
        ],
        "f1_score": ["f1_score"],
        "fluency": ["fluency"],
        "gleu_score": ["gleu"],
        "meteor_score": ["meteor"],
        "relevance": ["relevance"],
        "response_completeness": ["response_completeness"],
        "rouge_score": ["rouge_f1_score", "rouge_precision", "rouge_recall"],
        "groundedness_pro": ["groundedness_pro"],
        "similarity": ["similarity"],
        "intent_resolution": ["intent_resolution"],
        "retrieval": ["retrieval"],
        "task_adherence": ["task_adherence"],
        "tool_call_accuracy": ["tool_call_accuracy"],
        "groundedness": ["groundedness"],
        "code_vulnerability": ["code_vulnerability"],
        "eci": ["eci"],
        "protected_material": ["protected_material"],
        "ungrounded_attributes": ["ungrounded_attributes"],
        "indirect_attack": ["xpia", "xpia_manipulated_content", "xpia_intrusion", "xpia_information_gathering"],
        "label_grader": ["label_model"],
        "string_check_grader": ["string_check"],
        "text_similarity_grader": ["similarity"],
        "score_model_grader": ["score_model"],
        "sexual": ["sexual"],
        "self_harm": ["self_harm"],
        "violence": ["violence"],
        "hate_unfairness": ["hate_unfairness"],
        "tool_input_accuracy": ["tool_input_accuracy"],
        "task_completion": ["task_completion"],
        "tool_success": ["tool_success"],
        "tool_call_success": ["tool_call_success"],
        "tool_selection": ["tool_selection"],
        "tool_output_utilization": ["tool_output_utilization"],
        "task_navigation_efficiency": ["task_navigation_efficiency"],
        "text_similarity": ["similarity"],
        "string_check": ["string_check"],
        "sensitive_data_leakage": ["prohibited_actions"],
        "score_model": ["score_model"],
        "label_model": ["label_model"],
        "prohibited_actions": ["prohibited_actions"],
    }

    EVAL_CLASS_NAME_MAP = {
        "BleuScoreEvaluator": "bleu_score",
        "CodeVulnerabilityEvaluator": "code_vulnerability",
        "CoherenceEvaluator": "coherence",
        "ContentSafetyEvaluator": "content_safety",
        "DocumentRetrievalEvaluator": "document_retrieval",
        "ECIEvaluator": "eci",
        "F1ScoreEvaluator": "f1_score",
        "FluencyEvaluator": "fluency",
        "GleuScoreEvaluator": "gleu_score",
        "GroundednessEvaluator": "groundedness",
        "GroundednessProEvaluator": "groundedness_pro",
        "HateUnfairnessEvaluator": "hate_unfairness",
        "IndirectAttackEvaluator": "indirect_attack",
        "IntentResolutionEvaluator": "intent_resolution",
        "MeteorScoreEvaluator": "meteor_score",
        "ProtectedMaterialEvaluator": "protected_material",
        "QAEvaluator": "qa",
        "RelevanceEvaluator": "relevance",
        "ResponseCompletenessEvaluator": "response_completeness",
        "RetrievalEvaluator": "retrieval",
        "RougeScoreEvaluator": "rouge_score",
        "SelfHarmEvaluator": "self_harm",
        "SexualEvaluator": "sexual",
        "SimilarityEvaluator": "similarity",
        "TaskAdherenceEvaluator": "task_adherence",
        "TaskCompletionEvaluator": "task_completion",
        "ToolCallAccuracyEvaluator": "tool_call_accuracy",
        "UngroundedAttributesEvaluator": "ungrounded_attributes",
        "ViolenceEvaluator": "violence",
    }


DEFAULT_EVALUATION_RESULTS_FILE_NAME = "evaluation_results.json"

CONTENT_SAFETY_DEFECT_RATE_THRESHOLD_DEFAULT = 4

PF_BATCH_TIMEOUT_SEC_DEFAULT = 3600
PF_BATCH_TIMEOUT_SEC = "PF_BATCH_TIMEOUT_SEC"
PF_DISABLE_TRACING = "PF_DISABLE_TRACING"

OTEL_EXPORTER_OTLP_TRACES_TIMEOUT = "OTEL_EXPORTER_OTLP_TRACES_TIMEOUT"
OTEL_EXPORTER_OTLP_TRACES_TIMEOUT_DEFAULT = 60

AZURE_OPENAI_TYPE: Literal["azure_openai"] = "azure_openai"

OPENAI_TYPE: Literal["openai"] = "openai"

EVALUATION_PASS_FAIL_MAPPING = {
    True: "pass",
    False: "fail",
}

DEFAULT_MAX_COMPLETION_TOKENS_REASONING_MODELS = 60000
BINARY_AGGREGATE_SUFFIX = "binary_aggregate"

AOAI_COLUMN_NAME = "aoai"
DEFAULT_OAI_EVAL_RUN_NAME = "AI_SDK_EVAL_RUN"
DEFAULT_AOAI_API_VERSION = "2025-04-01-preview"  # Unfortunately relying on preview version for now.

# OpenTelemetry event names
EVALUATION_EVENT_NAME = "gen_ai.evaluation.result"
