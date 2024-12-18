# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu
from promptflow._utils.async_utils import async_run_allowing_running_loop

from azure.ai.evaluation._common.utils import nltk_tokenize


class _AsyncBleuScoreEvaluator:
    def __init__(self):
        pass

    async def __call__(self, *, response: str, ground_truth: str, **kwargs):
        reference_tokens = nltk_tokenize(ground_truth)
        hypothesis_tokens = nltk_tokenize(response)

        # NIST Smoothing
        smoothing_function = SmoothingFunction().method4
        score = sentence_bleu([reference_tokens], hypothesis_tokens, smoothing_function=smoothing_function)

        return {
            "bleu_score": score,
        }


class BleuScoreEvaluator:
    """
    Calculate the BLEU score for a given response and ground truth.

    BLEU (Bilingual Evaluation Understudy) score is commonly used in natural language processing (NLP) and machine
    translation. It is widely used in text summarization and text generation use cases.

    Use the BLEU score when you want to evaluate the similarity between the generated text and reference text,
    especially in tasks such as machine translation or text summarization, where n-gram overlap is a significant
    indicator of quality.

    The BLEU score ranges from 0 to 1, with higher scores indicating better quality.

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START bleu_score_evaluator]
            :end-before: [END bleu_score_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call an BleuScoreEvaluator.
    """

    id = "azureml://registries/azureml/models/Bleu-Score-Evaluator/versions/3"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    def __init__(self):
        self._async_evaluator = _AsyncBleuScoreEvaluator()

    def __call__(self, *, response: str, ground_truth: str, **kwargs):
        """
        Evaluate the BLEU score between the response and the ground truth.

        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword ground_truth: The ground truth to be compared against.
        :paramtype ground_truth: str
        :return: The BLEU score.
        :rtype: Dict[str, float]
        """
        return async_run_allowing_running_loop(
            self._async_evaluator, response=response, ground_truth=ground_truth, **kwargs
        )

    def _to_async(self):
        return self._async_evaluator
