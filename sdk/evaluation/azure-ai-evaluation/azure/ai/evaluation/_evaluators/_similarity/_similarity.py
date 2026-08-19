# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from typing import Any, Dict

from typing_extensions import overload, override

from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase
from azure.ai.evaluation._evaluators._common._validators import (
    MessagesOrQueryResponseInputValidator,
    ValidatorInterface,
)
from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget


class SimilarityEvaluator(PromptyEvaluatorBase):
    """
    Evaluates similarity score for a given query, response, and ground truth.

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
    :param threshold: The threshold for the similarity evaluator. Default is 3.
    :type threshold: int
    :param credential: The credential for authenticating to Azure AI service.
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword is_reasoning_model: If True, the evaluator will use reasoning model configuration (o1/o3 models).
        This will adjust parameters like max_completion_tokens and remove unsupported parameters. Default is False.
    :paramtype is_reasoning_model: bool

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START similarity_evaluator]
            :end-before: [END similarity_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call a SimilarityEvaluator with a four-gram rouge type.

    .. admonition:: Example using Azure AI Project URL:

        .. literalinclude:: ../samples/evaluation_samples_evaluate_fdp.py
            :start-after: [START similarity_evaluator]
            :end-before: [END similarity_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call SimilarityEvaluator using Azure AI Project URL in the following format
                https://{resource_name}.services.ai.azure.com/api/projects/{project_name}

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_threshold.py
            :start-after: [START threshold_similarity_evaluator]
            :end-before: [END threshold_similarity_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize with a threshold and call a SimilarityEvaluator.

    .. note::

        To align with our support of a diverse set of models, an output key without the `gpt_` prefix has been added.
        To maintain backwards compatibility, the old key with the `gpt_` prefix is still be present in the output;
        however, it is recommended to use the new key moving forward as the old key will be deprecated in the future.
    """

    # Constants must be defined within eval's directory to be save/loadable

    _PROMPTY_FILE = "similarity.prompty"
    _RESULT_KEY = "similarity"

    _validator: ValidatorInterface

    id = "azureai://built-in/evaluators/similarity"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    @override
    def __init__(self, model_config, *, threshold=3, credential=None, **kwargs):
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self._PROMPTY_FILE)
        self._threshold = threshold
        self._higher_is_better = True
        # Initialize input validator — accepts messages OR query/response(/ground_truth).
        self._validator = MessagesOrQueryResponseInputValidator(error_target=ErrorTarget.SIMILARITY_EVALUATOR)
        super().__init__(
            model_config=model_config,
            prompty_file=prompty_path,
            result_key=self._RESULT_KEY,
            threshold=threshold,
            credential=credential,
            _higher_is_better=self._higher_is_better,
            **kwargs,
        )

    # Ignoring a mypy error about having only 1 overload function.
    # We want to use the overload style for all evals, even single-inputs. This is both to make
    # refactoring to multi-input styles easier, stylistic consistency consistency across evals,
    # and due to the fact that non-overloaded syntax now causes various parsing issues that
    # we don't want to deal with.
    @overload  # type: ignore
    def __call__(self, *, query: str, response: str, ground_truth: str) -> Dict[str, float]:
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

    @override
    def _convert_kwargs_to_eval_input(self, **kwargs):
        """Convert keyword arguments to evaluation input, with validation.

        Normalize a bare ``messages=[...]`` kwarg (plus any scalar adjuncts the SDK
        batch engine may forward alongside it) into a ``conversation={...}`` dict so
        the base ``_derive_conversation_converter`` can extract per-turn q/r for the
        judge. This mirrors the shape ACA/RAISvc produce when a customer's
        ``data_mapping`` targets ``messages`` plus top-level ``context`` /
        ``ground_truth`` / ``tool_definitions`` fields.
        """
        conversation = kwargs.get("conversation")
        messages = kwargs.get("messages")
        if conversation is None and messages is not None:
            conv: Dict[str, Any] = {"messages": messages}
            context = kwargs.pop("context", None)
            if context is not None:
                conv["context"] = context
            tool_definitions = kwargs.pop("tool_definitions", None)
            if tool_definitions is not None:
                conv["tool_definitions"] = tool_definitions
            # Top-level ground_truth: stamp onto assistant turns lacking their own,
            # so the base converter picks it up as per-response ground_truth.
            ground_truth = kwargs.pop("ground_truth", None)
            if ground_truth is not None and isinstance(messages, list):
                for m in messages:
                    if isinstance(m, dict) and m.get("role") == "assistant" and "ground_truth" not in m:
                        m["ground_truth"] = ground_truth
            kwargs["conversation"] = conv
            kwargs.pop("messages", None)
            return super()._convert_kwargs_to_eval_input(**kwargs)

        if conversation is not None:
            return super()._convert_kwargs_to_eval_input(**kwargs)

        query = kwargs.get("query")
        response = kwargs.get("response")
        ground_truth = kwargs.get("ground_truth")

        # Validate required fields are not None
        if query is None:
            raise EvaluationException(
                message="Either 'conversation' or individual inputs must be provided. 'query' is missing.",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.MISSING_FIELD,
                target=ErrorTarget.SIMILARITY_EVALUATOR,
            )

        if response is None:
            raise EvaluationException(
                message="Either 'conversation' or individual inputs must be provided. 'response' is missing.",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.MISSING_FIELD,
                target=ErrorTarget.SIMILARITY_EVALUATOR,
            )

        if ground_truth is None:
            raise EvaluationException(
                message="Either 'conversation' or individual inputs must be provided. 'ground_truth' is missing.",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.MISSING_FIELD,
                target=ErrorTarget.SIMILARITY_EVALUATOR,
            )

        return super()._convert_kwargs_to_eval_input(**kwargs)
