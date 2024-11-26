# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import math
import os
import re

from promptflow._utils.async_utils import async_run_allowing_running_loop
from promptflow.core import AsyncPrompty

from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException

from ..._common.utils import construct_prompty_model_config, validate_model_config

try:
    from ..._user_agent import USER_AGENT
except ImportError:
    USER_AGENT = "None"


class _AsyncSimilarityEvaluator:
    # Constants must be defined within eval's directory to be save/loadable
    _PROMPTY_FILE = "similarity.prompty"
    _LLM_CALL_TIMEOUT = 600
    _DEFAULT_OPEN_API_VERSION = "2024-02-15-preview"

    def __init__(self, model_config: dict):
        prompty_model_config = construct_prompty_model_config(
            validate_model_config(model_config),
            self._DEFAULT_OPEN_API_VERSION,
            USER_AGENT,
        )

        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self._PROMPTY_FILE)
        self._flow = AsyncPrompty.load(source=prompty_path, model=prompty_model_config)

    async def __call__(self, *, query: str, response: str, ground_truth: str, **kwargs):
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
        # Validate input parameters
        query = str(query or "")
        response = str(response or "")
        ground_truth = str(ground_truth or "")

        if not (query.strip() and response.strip() and ground_truth.strip()):
            msg = "'query', 'response' and 'ground_truth' must be non-empty strings."
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                error_category=ErrorCategory.MISSING_FIELD,
                error_blame=ErrorBlame.USER_ERROR,
                error_target=ErrorTarget.SIMILARITY_EVALUATOR,
            )

        # Run the evaluation flow
        llm_output = await self._flow(
            query=query, response=response, ground_truth=ground_truth, timeout=self._LLM_CALL_TIMEOUT, **kwargs
        )

        score = math.nan
        if llm_output:
            match = re.search(r"\d", llm_output)
            if match:
                score = float(match.group())

        return {"similarity": float(score), "gpt_similarity": float(score)}


class SimilarityEvaluator:
    """
    Evaluates similarity score for a given query, response, and ground truth or a multi-turn conversation.

    The similarity measure evaluates the likeness between a ground truth sentence (or document) and the
    AI model's generated prediction. This calculation involves creating sentence-level embeddings for both
    the ground truth and the model's prediction, which are high-dimensional vector representations capturing
    the semantic meaning and context of the sentences.

    Use it when you want an objective evaluation of an AI model's performance, particularly in text generation
    tasks where you have access to ground truth responses. Similarity enables you to assess the generated
    text's semantic alignment with the desired content, helping to gauge the model's quality and accuracy.

    Similarity scores range from 1 to 5, with 1 being the least similar and 5 being the most similar.

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

    id = "azureml://registries/azureml/models/Similarity-Evaluator/versions/3"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    def __init__(self, model_config):
        self._async_evaluator = _AsyncSimilarityEvaluator(model_config)

    def __call__(self, *, query: str, response: str, ground_truth: str, **kwargs):
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
        return async_run_allowing_running_loop(
            self._async_evaluator, query=query, response=response, ground_truth=ground_truth, **kwargs
        )

    def _to_async(self):
        return self._async_evaluator
