# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict
from nltk.translate.gleu_score import sentence_gleu
from typing_extensions import overload, override

from azure.ai.evaluation._common.utils import nltk_tokenize

from azure.ai.evaluation._evaluators._common import EvaluatorBase
from azure.ai.evaluation._constants import EVALUATION_PASS_FAIL_MAPPING


class GleuScoreEvaluator(EvaluatorBase):
    """
    Calculates the GLEU (Google-BLEU) score between a response and the ground truth.

    The GLEU (Google-BLEU) score evaluator measures the similarity between generated and reference texts by
    evaluating n-gram overlap, considering both precision and recall. This balanced evaluation, designed for
    sentence-level assessment, makes it ideal for detailed analysis of translation quality. GLEU is well-suited for
    use cases such as machine translation, text summarization, and text generation.

    GLEU scores range from 0 to 1, where a value of 1 represents perfect overlap between the response and
    the ground truth and a value of 0 indicates no overlap.

    :param threshold: The threshold for the GLEU evaluator. Default is 0.5.
    :type threshold: float

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START gleu_score_evaluator]
            :end-before: [END gleu_score_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call a GleuScoreEvaluator.
    
    .. admonition:: Example with Threshold:

        .. literalinclude:: ../samples/evaluation_samples_threshold.py
            :start-after: [START threshold_gleu_score_evaluator]
            :end-before: [END threshold_gleu_score_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize with threshold and call a GleuScoreEvaluator.

    .. admonition:: Example using Azure AI Project URL:
                
        .. literalinclude:: ../samples/evaluation_samples_evaluate_fdp.py
            :start-after: [START gleu_score_evaluator]
            :end-before: [END gleu_score_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call GleuScoreEvaluator using Azure AI Project URL in the following format 
                https://{resource_name}.services.ai.azure.com/api/projects/{project_name}
    """

    id = "azureml://registries/azureml/models/Gleu-Score-Evaluator/versions/3"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    @override
    def __init__(self, *, threshold=0.5):
        self._threshold = threshold
        self._higher_is_better = True
        super().__init__(threshold=threshold, _higher_is_better=self._higher_is_better)

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
        binary_result = False
        if self._higher_is_better:
            if score >= self._threshold:
                binary_result = True
        else:
            if score <= self._threshold:
                binary_result = True
        return {
            "gleu_score": score,
            "gleu_result": EVALUATION_PASS_FAIL_MAPPING[binary_result],
            "gleu_threshold": self._threshold,
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
