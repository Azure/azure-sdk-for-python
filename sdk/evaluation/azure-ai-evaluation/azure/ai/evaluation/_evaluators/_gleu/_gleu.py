# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from nltk.translate.gleu_score import sentence_gleu
from promptflow._utils.async_utils import async_run_allowing_running_loop

from azure.ai.evaluation._common.utils import nltk_tokenize


class _AsyncGleuScoreEvaluator:
    def __init__(self):
        pass

    async def __call__(self, *, ground_truth: str, response: str, **kwargs):
        reference_tokens = nltk_tokenize(ground_truth)
        hypothesis_tokens = nltk_tokenize(response)

        score = sentence_gleu([reference_tokens], hypothesis_tokens)

        return {
            "gleu_score": score,
        }


class GleuScoreEvaluator:
    """
    Calculates the GLEU (Google-BLEU) score between a response and the ground truth.

    The GLEU (Google-BLEU) score evaluator measures the similarity between generated and reference texts by
    evaluating n-gram overlap, considering both precision and recall. This balanced evaluation, designed for
    sentence-level assessment, makes it ideal for detailed analysis of translation quality. GLEU is well-suited for
    use cases such as machine translation, text summarization, and text generation.

    GLEU scores range from 0 to 1, where a value of 1 represents perfect overlap between the response and
    the ground truth and a value of 0 indicates no overlap.

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START gleu_score_evaluator]
            :end-before: [END gleu_score_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call a GleuScoreEvaluator.
    """

    id = "azureml://registries/azureml/models/Gleu-Score-Evaluator/versions/3"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    def __init__(self):
        self._async_evaluator = _AsyncGleuScoreEvaluator()

    def __call__(self, *, ground_truth: str, response: str, **kwargs):
        """
        Evaluate the GLEU score between the response and the ground truth.

        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword ground_truth: The ground truth to be compared against.
        :paramtype ground_truth: str
        :return: The GLEU score.
        :rtype: Dict[str, float]
        """
        return async_run_allowing_running_loop(
            self._async_evaluator, ground_truth=ground_truth, response=response, **kwargs
        )

    def _to_async(self):
        return self._async_evaluator
