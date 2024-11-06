# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from nltk.translate.meteor_score import meteor_score
from promptflow._utils.async_utils import async_run_allowing_running_loop

from azure.ai.evaluation._common.utils import nltk_tokenize, ensure_nltk_data_downloaded


class _AsyncMeteorScoreEvaluator:
    def __init__(self, alpha: float = 0.9, beta: float = 3.0, gamma: float = 0.5):
        self._alpha = alpha
        self._beta = beta
        self._gamma = gamma

        ensure_nltk_data_downloaded()

    async def __call__(self, *, ground_truth: str, response: str, **kwargs):
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


class MeteorScoreEvaluator:
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

    def __init__(self, alpha: float = 0.9, beta: float = 3.0, gamma: float = 0.5):
        self._async_evaluator = _AsyncMeteorScoreEvaluator(alpha=alpha, beta=beta, gamma=gamma)

    def __call__(self, *, ground_truth: str, response: str, **kwargs):
        """
        Evaluate the METEOR score between the response and the ground truth.

        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword ground_truth: The ground truth to be compared against.
        :paramtype ground_truth: str
        :return: The METEOR score.
        :rtype: Dict[str, float]
        """
        return async_run_allowing_running_loop(
            self._async_evaluator, ground_truth=ground_truth, response=response, **kwargs
        )

    def _to_async(self):
        return self._async_evaluator
