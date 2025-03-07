# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from enum import Enum

from typing import Dict
from typing_extensions import overload, override

from azure.ai.evaluation._vendor.rouge_score import rouge_scorer
from azure.ai.evaluation._evaluators._common import EvaluatorBase


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


class RougeScoreEvaluator(EvaluatorBase):
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

    @override
    def __init__(self, rouge_type: RougeType):
        self._rouge_type = rouge_type
        super().__init__()

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict[str, float]:
        """Produce a rouge score evaluation result.

        :param eval_input: The input to the evaluation function.
        :type eval_input: Dict
        :return: The evaluation result.
        :rtype: Dict
        """
        ground_truth = eval_input["ground_truth"]
        response = eval_input["response"]
        scorer = rouge_scorer.RougeScorer(rouge_types=[self._rouge_type.value])
        metrics = scorer.score(ground_truth, response)[self._rouge_type.value]
        return {
            "rouge_precision": metrics.precision,
            "rouge_recall": metrics.recall,
            "rouge_f1_score": metrics.fmeasure,
        }

    @overload  # type: ignore
    def __call__(self, *, ground_truth: str, response: str) -> Dict[str, float]:
        """
        Evaluate the ROUGE score between the response and the ground truth.

        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword ground_truth: The ground truth to be compared against.
        :paramtype ground_truth: str
        :return: The ROUGE score.
        :rtype: Dict[str, float]
        """

    @override
    def __call__(  # pylint: disable=docstring-missing-param
        self,
        *args,
        **kwargs,
    ):
        """
        Evaluate route score.
        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword ground_truth: The ground truth to be compared against.
        :paramtype ground_truth: str
        :return: The ROUGE score.
        :rtype: Dict[str, float]
        """
        return super().__call__(*args, **kwargs)
