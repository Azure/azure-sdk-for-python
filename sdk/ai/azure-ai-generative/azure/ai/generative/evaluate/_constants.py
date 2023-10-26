# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml.metrics import constants

QA = "qa"
CHAT = "chat"

SUPPORTED_TASK_TYPE = [QA, CHAT]

SUPPORTED_TO_METRICS_TASK_TYPE_MAPPING = {
    QA: constants.QUESTION_ANSWERING,
    CHAT: constants.RAG_EVALUATION,
}

TYPE_TO_KWARGS_MAPPING = {
    constants.QUESTION_ANSWERING: ["questions", "contexts", "y_pred", "y_test"],
    constants.RAG_EVALUATION: ["y_pred"]
}


class EvaluationMetrics:
    """
    Evaluation metrics supported by evaluation in azure-ai-generative sdk
    """

    GPT_GROUNDEDNESS = "gpt_groundedness"
    GPT_RELEVANCE = "gpt_relevance"
    GPT_COHERENCE = "gpt_coherence"
    GPT_FLUENCY = "gpt_fluency"
    GPT_SIMILARITY = "gpt_similarity"
    F1_SCORE = "f1_score"
    EXACT_MATCH = "exact_match"
    ADA_SIMILARITY = "ada_similarity"
    BERTSCORE = "bertscore"
    GPT_RETRIEVAL_SCORE = "gpt_retrieval_score"
    # These are temporary until names are fixed in metrics package
    RETRIEVAL_SCORE = "retrieval_score"
    GROUNDING_SCORE = "grounding_score"
    GENERATION_SCORE = "generation_score"


class QaMetrics:
    DEFAULT_LIST = [
        EvaluationMetrics.GPT_GROUNDEDNESS,
        EvaluationMetrics.GPT_RELEVANCE,
        EvaluationMetrics.GPT_COHERENCE
    ]
    SUPPORTED_LIST = [
        EvaluationMetrics.GPT_GROUNDEDNESS,
        EvaluationMetrics.GPT_RELEVANCE,
        EvaluationMetrics.GPT_COHERENCE,
        EvaluationMetrics.GPT_FLUENCY,
        EvaluationMetrics.GPT_SIMILARITY,
        EvaluationMetrics.F1_SCORE,
        EvaluationMetrics.EXACT_MATCH,
        EvaluationMetrics.ADA_SIMILARITY,
        EvaluationMetrics.BERTSCORE
    ]


class ChatMetrics:
    DEFAULT_LIST = [
        EvaluationMetrics.GROUNDING_SCORE,
        EvaluationMetrics.RETRIEVAL_SCORE,
        EvaluationMetrics.GENERATION_SCORE
    ]
    SUPPORTED_LIST = [
        EvaluationMetrics.GROUNDING_SCORE,
        EvaluationMetrics.RETRIEVAL_SCORE,
        EvaluationMetrics.GENERATION_SCORE
    ]


TASK_TYPE_TO_METRICS_MAPPING = {
    constants.QUESTION_ANSWERING: QaMetrics,
    constants.RAG_EVALUATION: ChatMetrics
}
