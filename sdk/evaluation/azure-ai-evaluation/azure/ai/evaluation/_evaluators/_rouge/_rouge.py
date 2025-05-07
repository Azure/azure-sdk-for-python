# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from enum import Enum

from typing import Dict
from typing_extensions import overload, override

from azure.ai.evaluation._vendor.rouge_score import rouge_scorer
from azure.ai.evaluation._evaluators._common import EvaluatorBase
from azure.ai.evaluation._constants import EVALUATION_PASS_FAIL_MAPPING
import math


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
    :param rouge_type: The type of ROUGE score to calculate. Default is "rouge1".
    :type rouge_type: str
    :param precision_threshold: The threshold value to determine if the precision evaluation passes or fails. Default is 0.5.
    :type precision_threshold: float
    :param recall_threshold: The threshold value to determine if the recall evaluation passes or fails. Default is 0.5.
    :type recall_threshold: float
    :param f1_score_threshold: The threshold value to determine if the F1 score evaluation passes or fails. Default is 0.5.
    :type f1_score_threshold: float

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START rouge_score_evaluator]
            :end-before: [END rouge_score_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call a RougeScoreEvaluator with a four-gram rouge type.

    .. admonition:: Example with threshold:

        .. literalinclude:: ../samples/evaluation_samples_threshold.py
            :start-after: [START threshold_rouge_score_evaluator]
            :end-before: [END threshold_rouge_score_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize with a specified threshold and call a RougeScoreEvaluator with a four-gram rouge type.
    """

    id = "azureml://registries/azureml/models/Rouge-Score-Evaluator/versions/3"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    @override
    def __init__(
        self, 
        rouge_type: RougeType,
        *,
        precision_threshold: float = 0.5,
        recall_threshold: float = 0.5,
        f1_score_threshold: float = 0.5
    ):
        self._rouge_type = rouge_type
        self._higher_is_better = True
        super().__init__()
        
        # Type checking for threshold parameters
        for name, value in [
            ("precision_threshold", precision_threshold),
            ("recall_threshold", recall_threshold),
            ("f1_score_threshold", f1_score_threshold),
        ]:
            if not isinstance(value, float):
                raise TypeError(f"{name} must be a float, got {type(value)}")
                
        self._threshold = {
            "precision": precision_threshold,
            "recall": recall_threshold,
            "f1_score": f1_score_threshold,
        }

    def _get_binary_result(
            self,
            rouge_precision: float,
            rouge_recall: float,
            rouge_f1_score: float,
    ) -> Dict[str, bool]:
        """
        Get binary result based on the threshold.

        :param rouge_precision: The precision score.
        :type rouge_precision: float
        :param rouge_recall: The recall score.
        :type rouge_recall: float
        :param rouge_f1_score: The F1 score.
        :type rouge_f1_score: float
        :return: A dictionary with binary results for precision, recall, and F1 score.

        """
        # Initialize results with False for NaN values
        results = {
            "rouge_precision_result": False,
            "rouge_recall_result": False,
            "rouge_f1_score_result": False,
        }

        # Check if values are valid (not NaN) before comparison
        precision_valid = not math.isnan(rouge_precision)
        recall_valid = not math.isnan(rouge_recall)
        f1_valid = not math.isnan(rouge_f1_score)
        
        if self._higher_is_better:
            if precision_valid:
                results["rouge_precision_result"] = (rouge_precision >= self._threshold["precision"])
            if recall_valid:
                results["rouge_recall_result"] = (rouge_recall >= self._threshold["recall"])
            if f1_valid:
                results["rouge_f1_score_result"] = (rouge_f1_score >= self._threshold["f1_score"])
        else:
            if precision_valid:
                results["rouge_precision_result"] = (rouge_precision <= self._threshold["precision"])
            if recall_valid:
                results["rouge_recall_result"] = (rouge_recall <= self._threshold["recall"])
            if f1_valid:
                results["rouge_f1_score_result"] = (rouge_f1_score <= self._threshold["f1_score"])
        
        return results

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
        binary_results = {
            "rouge_precision_result": False,
            "rouge_recall_result": False,
            "rouge_f1_score_result": False,
        }
        # Convert metrics to floats, using nan for None or non-convertible values
        rouge_precision = float(metrics.precision) if metrics.precision is not None else float('nan')
        rouge_recall = float(metrics.recall) if metrics.recall is not None else float('nan')
        rouge_f1_score = float(metrics.fmeasure) if metrics.fmeasure is not None else float('nan')
        binary_results = self._get_binary_result(
            rouge_precision=rouge_precision,
            rouge_recall=rouge_recall,
            rouge_f1_score=rouge_f1_score,
        )
        return {
            "rouge_precision": rouge_precision,
            "rouge_recall": rouge_recall,
            "rouge_f1_score": rouge_f1_score,
            "rouge_precision_result": EVALUATION_PASS_FAIL_MAPPING[binary_results["rouge_precision_result"]],
            "rouge_recall_result": EVALUATION_PASS_FAIL_MAPPING[binary_results["rouge_recall_result"]],
            "rouge_f1_score_result": EVALUATION_PASS_FAIL_MAPPING[binary_results["rouge_f1_score_result"]],
            "rouge_precision_threshold": self._threshold["precision"],
            "rouge_recall_threshold": self._threshold["recall"],
            "rouge_f1_score_threshold": self._threshold["f1_score"],
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
