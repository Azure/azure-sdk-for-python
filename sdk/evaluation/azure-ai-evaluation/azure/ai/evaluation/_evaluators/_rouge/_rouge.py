# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from enum import Enum

from promptflow._utils.async_utils import async_run_allowing_running_loop

from azure.ai.evaluation._vendor.rouge_score import rouge_scorer


class RougeType(Enum):
    """
    Enumeration of ROUGE (Recall-Oriented Understudy for Gisting Evaluation) types.
    """

    ROUGE_1 = "rouge1"
    """Overlap of unigrams (single words) between generated and reference text."""

    ROUGE_2 = "rouge2"
    """Overlap of bigrams (two consecutive words) between generated and reference text."""

    ROUGE_3 = "rouge3"
    """Overlap of trigrams (three consecutive words) between generated and reference text."""

    ROUGE_4 = "rouge4"
    """Overlap of four-grams (four consecutive words) between generated and reference text."""

    ROUGE_5 = "rouge5"
    """Overlap of five-grams (five consecutive words) between generated and reference text."""

    ROUGE_L = "rougeL"
    """Overlap of L-grams (L consecutive words) between generated and reference text."""


class _AsyncRougeScoreEvaluator:
    def __init__(self, rouge_type: RougeType):
        self._rouge_type = rouge_type

    async def __call__(self, *, ground_truth: str, response: str, **kwargs):
        scorer = rouge_scorer.RougeScorer(rouge_types=[self._rouge_type.value])
        metrics = scorer.score(ground_truth, response)[self._rouge_type.value]
        return {
            "rouge_precision": metrics.precision,
            "rouge_recall": metrics.recall,
            "rouge_f1_score": metrics.fmeasure,
        }


class RougeScoreEvaluator:
    """
    Calculates the ROUGE score for a given response and ground truth.

    The ROUGE score (Recall-Oriented Understudy for Gisting Evaluation) evaluates the similarity between the
    generated text and reference text based on n-gram overlap, including ROUGE-N (unigram, bigram, etc.), and
    ROUGE-L (longest common subsequence). It calculates precision, recall, and F1 scores to capture how well
    the generated text matches the reference text. Rouge type options are "rouge1" (Unigram overlap), "rouge2"
    (Bigram overlap), "rouge3" (Trigram overlap), "rouge4" (4-gram overlap), "rouge5" (5-gram overlap), "rougeL"
    (L-graph overlap)

    Use the ROUGE score when you need a robust evaluation metric for text summarization, machine translation, and
    other natural language processing tasks, especially when focusing on recall and the ability to capture relevant
    information from the reference text.

    ROUGE scores range from 0 to 1, with higher scores indicating better quality.

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START rouge_score_evaluator]
            :end-before: [END rouge_score_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call a RougeScoreEvaluator with a four-gram rouge type.
    """

    id = "azureml://registries/azureml/models/Rouge-Score-Evaluator/versions/3"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    def __init__(self, rouge_type: RougeType):
        self._async_evaluator = _AsyncRougeScoreEvaluator(rouge_type)

    def __call__(self, *, ground_truth: str, response: str, **kwargs):
        """
        Evaluate the ROUGE score between the response and the ground truth.

        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword ground_truth: The ground truth to be compared against.
        :paramtype ground_truth: str
        :return: The ROUGE score.
        :rtype: Dict[str, float]
        """
        return async_run_allowing_running_loop(
            self._async_evaluator, ground_truth=ground_truth, response=response, **kwargs
        )

    def _to_async(self):
        return self._async_evaluator
