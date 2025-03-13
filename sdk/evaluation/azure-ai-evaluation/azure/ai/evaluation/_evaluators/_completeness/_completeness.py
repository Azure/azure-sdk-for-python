# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from typing import Dict, Union

from typing_extensions import overload, override

from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase


class CompletenessEvaluator(PromptyEvaluatorBase):
    """
    Evaluates the extent to which a given response contains all necessary and relevant information with respect to the provided ground truth.

    The completeness measure assesses how thoroughly an AI model's generated response aligns with the key information, claims, and statements established in the ground truth. This evaluation considers the presence, accuracy, and relevance of the content provided. 
    The assessment spans multiple levels, ranging from fully incomplete to fully complete, ensuring a comprehensive evaluation of the response's content quality.

    Use this metric when you need to evaluate an AI model's ability to deliver comprehensive and accurate information, particularly in text generation tasks where conveying all essential details is crucial for clarity, context, and correctness.

    Completeness scores range from 1 to 5:

    1: Fully incomplete — Contains none of the necessary information.
    2: Barely complete — Contains only a small portion of the required information.
    3: Moderately complete — Covers about half of the required content.
    4: Mostly complete — Includes most of the necessary details with minimal omissions.
    5: Fully complete — Contains all key information without any omissions.

    :param model_config: Configuration for the Azure OpenAI model.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START rouge_score_evaluator]
            :end-before: [END rouge_score_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call a RougeScoreEvaluator with a four-gram rouge type.

    .. note::

        To align with our support of a diverse set of models, an output key without the `gpt_` prefix has been added.
        To maintain backwards compatibility, the old key with the `gpt_` prefix is still be present in the output;
        however, it is recommended to use the new key moving forward as the old key will be deprecated in the future.
    """

    # Constants must be defined within eval's directory to be save/loadable

    _PROMPTY_FILE = "completeness.prompty"
    _RESULT_KEY = "completeness"

    id = "completeness"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    @override
    def __init__(self, model_config):
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self._PROMPTY_FILE)
        super().__init__(model_config=model_config, prompty_file=prompty_path, result_key=self._RESULT_KEY)

    # Ignoring a mypy error about having only 1 overload function.
    # We want to use the overload style for all evals, even single-inputs. This is both to make
    # refactoring to multi-input styles easier, stylistic consistency consistency across evals,
    # and due to the fact that non-overloaded syntax now causes various parsing issues that
    # we don't want to deal with.
    @overload  # type: ignore
    def __call__(self, *, response: str, ground_truth: str, threshold: float = 3) -> Dict[str, Union[str, bool, float]]:
        """
        Evaluate completeness.

        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword ground_truth: The ground truth to be evaluated.
        :paramtype ground_truth: str
        :keyword threshold: Threshold to calculate if response is complete
        :paramtype threshold: float 
        :return: The completeness score.
        :rtype: Dict[str, Union[str, bool, float]]
        """

    @override
    def __call__(  # pylint: disable=docstring-missing-param
        self,
        *args,
        **kwargs,
    ):
        """
        Evaluate Completeness.

        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword ground_truth: The ground truth to be evaluated.
        :paramtype ground_truth: str
        :return: The completeness score.
        :rtype: Dict[str, Union[str, bool, float]]
        """
        completeness_result = super().__call__(*args, **kwargs)
        if not isinstance(completeness_result, dict) or not "response_completeness" in completeness_result:
            raise Exception("Completeness Result is invalid") # this might not be needed
        threshold = kwargs.get("threshold", 3.0)
        response_complete_score = completeness_result.get("score")
        explanation = completeness_result.get("explanation")

        is_response_complete = response_complete_score >= threshold

        return {
            "is_response_complete": is_response_complete,
            "response_complete_score": response_complete_score,
            "explanation": explanation
        }
