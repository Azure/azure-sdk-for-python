# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict

from nltk.translate.meteor_score import meteor_score
from typing_extensions import overload, override

from azure.ai.evaluation._common.utils import nltk_tokenize, ensure_nltk_data_downloaded
from azure.ai.evaluation._evaluators._common import EvaluatorBase


class MeteorScoreEvaluator(EvaluatorBase):
    """
    Calculates the METEOR score for a given response and ground truth.

    The METEOR (Metric for Evaluation of Translation with Explicit Ordering) score grader evaluates generated text by
    comparing it to reference texts, focusing on precision, recall, and content alignment. It addresses limitations of
    other metrics like BLEU by considering synonyms, stemming, and paraphrasing. METEOR score considers synonyms and
    word stems to more accurately capture meaning and language variations. In addition to machine translation and
    text summarization, paraphrase detection is an optimal use case for the METEOR score.

    Use the METEOR score when you want a more linguistically informed evaluation metric that captures not only
    n-gram overlap but also accounts for synonyms, stemming, and word order. This is particularly useful for evaluating
    tasks like machine translation, text summarization, and text generation.

    The METEOR score ranges from 0 to 1, with 1 indicating a perfect match.

    :param alpha: The METEOR score alpha parameter. Default is 0.9.
    :type alpha: float
    :param beta: The METEOR score beta parameter. Default is 3.0.
    :type beta: float
    :param gamma: The METEOR score gamma parameter. Default is 0.5.
    :type gamma: float

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START meteor_score_evaluator]
            :end-before: [END meteor_score_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call a MeteorScoreEvaluator with alpha of 0.8.
    """

    id = "azureml://registries/azureml/models/Meteor-Score-Evaluator/versions/3"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    @override
    def __init__(self, alpha: float = 0.9, beta: float = 3.0, gamma: float = 0.5):
        self._alpha = alpha
        self._beta = beta
        self._gamma = gamma
        ensure_nltk_data_downloaded()
        super().__init__()

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict[str, float]:
        """Produce a meteor score evaluation result.

        :param eval_input: The input to the evaluation function.
        :type eval_input: Dict
        :return: The evaluation result.
        :rtype: Dict
        """
        ground_truth = eval_input["ground_truth"]
        response = eval_input["response"]
        reference_tokens = nltk_tokenize(ground_truth)
        hypothesis_tokens = nltk_tokenize(response)
        score = meteor_score(
            [reference_tokens],
            hypothesis_tokens,
            alpha=self._alpha,
            beta=self._beta,
            gamma=self._gamma,
        )

        return {
            "meteor_score": score,
        }

    @overload  # type: ignore
    def __call__(self, *, ground_truth: str, response: str) -> Dict[str, float]:
        """
        Evaluate the METEOR score between the response and the ground truth.

        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword ground_truth: The ground truth to be compared against.
        :paramtype ground_truth: str
        :return: The METEOR score.
        :rtype: Dict[str, float]
        """

    @override
    def __call__(  # pylint: disable=docstring-missing-param
        self,
        *args,
        **kwargs,
    ):
        """
        Evaluate the METEOR score between the response and the ground truth.

        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword ground_truth: The ground truth to be compared against.
        :paramtype ground_truth: str
        :return: The METEOR score.
        :rtype: Dict[str, float]
        """
        return super().__call__(*args, **kwargs)
