# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from typing import Dict

from typing_extensions import overload, override

from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase


class SimilarityEvaluator(PromptyEvaluatorBase):
    """
    Evaluates similarity score for a given query, response, and ground truth.

    The similarity measure evaluates the likeness between a ground truth
    sentence (or document) and the AI model's generated prediction. This
    involves creating sentence-level embeddings for both the ground truth and
    the model's prediction. These are high-dimensional vectors capturing the
    semantic meaning and context of the sentences.

    Use it when you need an objective evaluation of an AI model's performance,
    especially for text generation with ground truth responses. Similarity
    assesses semantic alignment with the desired content and helps gauge model
    quality and accuracy.

    Similarity scores range from 1 to 5 (1 = least similar, 5 = most similar).

    :param model_config: Configuration for the Azure OpenAI model.
    :type model_config:
        Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]
    :param threshold: The threshold for the similarity evaluator. Default is 3.
    :type threshold: int
    :keyword is_reasoning_model: (Preview) config for chat completions is
        updated to use reasoning models
    :type is_reasoning_model: bool

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START similarity_evaluator]
            :end-before: [END similarity_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call a SimilarityEvaluator with a
                four-gram rouge type.

    .. admonition:: Example using Azure AI Project URL:

        .. literalinclude:: ../samples/evaluation_samples_evaluate_fdp.py
            :start-after: [START similarity_evaluator]
            :end-before: [END similarity_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call SimilarityEvaluator using Azure AI
                Project URL in the following format
                https://{resource_name}.services.ai.azure.com/api/projects/{project_name}

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_threshold.py
            :start-after: [START threshold_similarity_evaluator]
            :end-before: [END threshold_similarity_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize with a threshold and call a
                SimilarityEvaluator.

    .. note::

    To align with our support of diverse models, an output key without the
    `gpt_` prefix has been added. To maintain backwards compatibility, the
    old key with the `gpt_` prefix is still present in the output; however,
    it is recommended to use the new key moving forward as the old key will
    be deprecated in the future.
    """

    # Constants must be defined within eval's directory to be save/loadable

    _PROMPTY_FILE = "similarity.prompty"
    _RESULT_KEY = "similarity"

    id = "azureai://built-in/evaluators/similarity"
    """Evaluator identifier for cloud evaluation."""

    @override
    def __init__(self, model_config, *, threshold=3, **kwargs):
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self._PROMPTY_FILE)
        self._threshold = threshold
        self._higher_is_better = True
        super().__init__(
            model_config=model_config,
            prompty_file=prompty_path,
            result_key=self._RESULT_KEY,
            threshold=threshold,
            _higher_is_better=self._higher_is_better,
            **kwargs,
        )

    # Ignoring a mypy error about having only 1 overload function.
    # We want to use the overload style for all evals, even single-inputs.
    # This makes refactoring to multi-input styles easier, keeps stylistic
    # consistency across evals, and avoids parsing issues with non-overloaded
    # syntax.
    @overload  # type: ignore
    def __call__(
        self, *, query: str, response: str, ground_truth: str
    ) -> Dict[str, float]:
        """
        Evaluate similarity.

        :keyword query: The query to be evaluated.
        :paramtype query: str
        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword ground_truth: The ground truth to be evaluated.
        :paramtype ground_truth: str
        :return: The similarity score.
        :rtype: Dict[str, float]
        """

    @override
    def __call__(  # pylint: disable=docstring-missing-param
        self,
        *args,
        **kwargs,
    ):
        """
        Evaluate similarity.

        :keyword query: The query to be evaluated.
        :paramtype query: str
        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword ground_truth: The ground truth to be evaluated.
        :paramtype ground_truth: str
        :return: The similarity score.
        :rtype: Dict[str, float]
        """
        return super().__call__(*args, **kwargs)
