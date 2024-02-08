# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, Union

QA = "qa"
CHAT = "chat"

SUPPORTED_TASK_TYPE = [QA, CHAT]

SUPPORTED_TO_METRICS_TASK_TYPE_MAPPING = {
    QA: "qa",
    CHAT: "chat",
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
    HATE_FAIRNESS = "hate_fairness"
    VIOLENCE = "violence"
    SELF_HARM = "self_harm"


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
        EvaluationMetrics.BERTSCORE,
        EvaluationMetrics.BERTSCORE,
        EvaluationMetrics.HATE_FAIRNESS,
        EvaluationMetrics.VIOLENCE,
        EvaluationMetrics.SELF_HARM
    ]


class ChatMetrics:
    DEFAULT_LIST = [
        EvaluationMetrics.GPT_GROUNDEDNESS,
        EvaluationMetrics.GPT_RELEVANCE,
        EvaluationMetrics.GPT_RETRIEVAL_SCORE
    ]
    SUPPORTED_LIST = [
        EvaluationMetrics.GPT_GROUNDEDNESS,
        EvaluationMetrics.GPT_RELEVANCE,
        EvaluationMetrics.GPT_RETRIEVAL_SCORE,
        EvaluationMetrics.HATE_FAIRNESS,
        EvaluationMetrics.VIOLENCE,
        EvaluationMetrics.SELF_HARM
    ]


TASK_TYPE_TO_METRICS_MAPPING: Dict[str, Union[QaMetrics, ChatMetrics]] = {
    "qa": QaMetrics(),
    "rag-evaluation": ChatMetrics()
}

SUPPORTED_TASK_TYPE_TO_METRICS_MAPPING = {
    QA: QaMetrics,
    CHAT: ChatMetrics
}
