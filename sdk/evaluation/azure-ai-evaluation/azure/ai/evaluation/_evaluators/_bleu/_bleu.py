# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict
from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu
from typing_extensions import overload, override

from azure.ai.evaluation._common.utils import nltk_tokenize

from azure.ai.evaluation._evaluators._common import EvaluatorBase
from azure.ai.evaluation._constants import EVALUATION_PASS_FAIL_MAPPING


class BleuScoreEvaluator(EvaluatorBase):
    """
    Calculate the BLEU score for a given response and ground truth.

    BLEU (Bilingual Evaluation Understudy) score is commonly used in natural language processing (NLP) and machine
    translation. It is widely used in text summarization and text generation use cases.

    Use the BLEU score when you want to evaluate the similarity between the generated text and reference text,
    especially in tasks such as machine translation or text summarization, where n-gram overlap is a significant
    indicator of quality.

    The BLEU score ranges from 0 to 1, with higher scores indicating better quality.
    :param threshold: The threshold for the evaluation. Default is 0.5.
    :type threshold: float

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START bleu_score_evaluator]
            :end-before: [END bleu_score_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call an BleuScoreEvaluator using azure.ai.evaluation.AzureAIProject
        
    .. admonition:: Example using Azure AI Project URL:
                
        .. literalinclude:: ../samples/evaluation_samples_evaluate_fdp.py
            :start-after: [START bleu_score_evaluator]
            :end-before: [END bleu_score_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call an BleuScoreEvaluator using Azure AI Project URL in following format 
                https://{resource_name}.services.ai.azure.com/api/projects/{project_name}

    .. admonition:: Example with Threshold:
        .. literalinclude:: ../samples/evaluation_samples_threshold.py
            :start-after: [START threshold_bleu_score_evaluator]
            :end-before: [END threshold_bleu_score_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize with threshold and call an BleuScoreEvaluator.
    """

    id = "azureml://registries/azureml/models/Bleu-Score-Evaluator/versions/3"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    def __init__(self, *, threshold=0.5):
        self._threshold = threshold
        self._higher_is_better = True
        super().__init__(threshold=threshold, _higher_is_better=self._higher_is_better)

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict[str, float]:
        """Produce a bleu score evaluation result.

        :param eval_input: The input to the evaluation function.
        :type eval_input: Dict
        :return: The evaluation result.
        :rtype: Dict
        """
        ground_truth = eval_input["ground_truth"]
        response = eval_input["response"]
        reference_tokens = nltk_tokenize(ground_truth)
        hypothesis_tokens = nltk_tokenize(response)

        # NIST Smoothing
        smoothing_function = SmoothingFunction().method4
        score = sentence_bleu([reference_tokens], hypothesis_tokens, smoothing_function=smoothing_function)
        binary_result = False
        if self._higher_is_better:
            binary_result = score >= self._threshold
        else:
            binary_result = score <= self._threshold

        return {
            "bleu_score": score,
            "bleu_result": EVALUATION_PASS_FAIL_MAPPING[binary_result],
            "bleu_threshold": self._threshold,
        }

    @overload  # type: ignore
    def __call__(self, *, response: str, ground_truth: str):
        """
        Evaluate the BLEU score between the response and the ground truth.

        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword ground_truth: The ground truth to be compared against.
        :paramtype ground_truth: str
        :return: The BLEU score.
        :rtype: Dict[str, float]
        """

    @override
    def __call__(  # pylint: disable=docstring-missing-param
        self,
        *args,
        **kwargs,
    ):
        """
        Evaluate the BLEU score between the response and the ground truth.

        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword ground_truth: The ground truth to be compared against.
        :paramtype ground_truth: str
        :return: The BLEU score.
        :rtype: Dict[str, float]
        """
        return super().__call__(*args, **kwargs)
