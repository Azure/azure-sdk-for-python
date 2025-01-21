# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict
from nltk.translate.gleu_score import sentence_gleu
from typing_extensions import overload, override

from azure.ai.evaluation._common.utils import nltk_tokenize

from azure.ai.evaluation._evaluators._common import EvaluatorBase


class GleuScoreEvaluator(EvaluatorBase):
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

    @override
    def __init__(self):
        super().__init__()

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict[str, float]:
        """Produce a glue score evaluation result.

        :param eval_input: The input to the evaluation function.
        :type eval_input: Dict
        :return: The evaluation result.
        :rtype: Dict
        """
        ground_truth = eval_input["ground_truth"]
        response = eval_input["response"]
        reference_tokens = nltk_tokenize(ground_truth)
        hypothesis_tokens = nltk_tokenize(response)

        score = sentence_gleu([reference_tokens], hypothesis_tokens)

        return {
            "gleu_score": score,
        }

    @overload  # type: ignore
    def __call__(self, *, ground_truth: str, response: str):
        """
        Evaluate the GLEU score between the response and the ground truth.

        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword ground_truth: The ground truth to be compared against.
        :paramtype ground_truth: str
        :return: The GLEU score.
        :rtype: Dict[str, float]
        """

    @override
    def __call__(  # pylint: disable=docstring-missing-param
        self,
        *args,
        **kwargs,
    ):
        """
        Evaluate the GLEU score between the response and the ground truth.

        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword ground_truth: The ground truth to be compared against.
        :paramtype ground_truth: str
        :return: The GLEU score.
        :rtype: Dict[str, float]
        """
        return super().__call__(*args, **kwargs)
