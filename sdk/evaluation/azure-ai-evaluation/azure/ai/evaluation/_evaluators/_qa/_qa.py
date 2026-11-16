# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Union

from typing_extensions import overload, override

from azure.ai.evaluation._evaluators._common import MultiEvaluatorBase
from azure.ai.evaluation._evaluators._common._model_runners import is_decision_model_config
from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget

from .._coherence import CoherenceEvaluator
from .._f1_score import F1ScoreEvaluator
from .._fluency import FluencyEvaluator
from .._groundedness import GroundednessEvaluator
from .._relevance import RelevanceEvaluator
from .._similarity import SimilarityEvaluator

_DECISION_MEMBER_OPTIONS = (
    "credential",
    "timeout",
    "timeout_seconds",
    "max_retries",
    "cancellation_requested",
    "max_request_bytes",
    "max_state_question_bytes",
    "max_response_bytes",
)


class QAEvaluator(MultiEvaluatorBase[Union[str, float]]):
    """
    Initialize a question-answer evaluator configured for a specific Azure OpenAI model.

    :param model_config: Configuration for the Azure OpenAI model, or a decision model configuration with
        ``type="decision"``, ``azure_endpoint`` and ``azure_deployment``. With a decision model, ``credential`` and
        the decision execution controls are passed to the model-based evaluators, which run on separate threads, so
        the credential must be synchronous.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]
    :param groundedness_threshold: The threshold for groundedness evaluation. Default is 3.
    :type groundedness_threshold: int
    :param relevance_threshold: The threshold for relevance evaluation. Default is 3.
    :type relevance_threshold: int
    :param coherence_threshold: The threshold for coherence evaluation. Default is 3.
    :type coherence_threshold: int
    :param fluency_threshold: The threshold for fluency evaluation. Default is 3.
    :type fluency_threshold: int
    :param similarity_threshold: The threshold for similarity evaluation. Default is 3.
    :type similarity_threshold: int
    :param f1_score_threshold: The threshold for F1 score evaluation. Default is 0.5.
    :type f1_score_threshold: float
    :return: A callable class that evaluates and generates metrics for "question-answering" scenario.
    :param kwargs: Additional arguments to pass to the evaluator.
    :type kwargs: Any

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START qa_evaluator]
            :end-before: [END qa_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call a QAEvaluator.

    .. admonition:: Example using Azure AI Project URL:

        .. literalinclude:: ../samples/evaluation_samples_evaluate_fdp.py
            :start-after: [START qa_evaluator]
            :end-before: [END qa_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call QAEvaluator using Azure AI Project URL in the following format
                https://{resource_name}.services.ai.azure.com/api/projects/{project_name}

    .. admonition:: Example with Threshold:

        .. literalinclude:: ../samples/evaluation_samples_threshold.py
            :start-after: [START threshold_qa_evaluator]
            :end-before: [END threshold_qa_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize with threshold and call a QAEvaluator.

    .. note::

        To align with our support of a diverse set of models, keys without the `gpt_` prefix has been added.
        To maintain backwards compatibility, the old keys with the `gpt_` prefix are still be present in the output;
        however, it is recommended to use the new keys moving forward as the old keys will be deprecated in the future.
    """

    id = "azureai://built-in/evaluators/qa"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    def __init__(
        self,
        model_config,
        *,
        groundedness_threshold: int = 3,
        relevance_threshold: int = 3,
        coherence_threshold: int = 3,
        fluency_threshold: int = 3,
        similarity_threshold: int = 3,
        f1_score_threshold: float = 0.5,
        **kwargs,
    ):
        # Type checking
        for name, value in [
            ("groundedness_threshold", groundedness_threshold),
            ("relevance_threshold", relevance_threshold),
            ("coherence_threshold", coherence_threshold),
            ("fluency_threshold", fluency_threshold),
            ("similarity_threshold", similarity_threshold),
            ("f1_score_threshold", f1_score_threshold),
        ]:
            if not isinstance(value, (int, float)):
                raise EvaluationException(
                    message=f"{name} must be an int or float, got {type(value)}",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.INVALID_VALUE,
                    target=ErrorTarget.QA_EVALUATOR,
                )

        # Extract is_reasoning_model from kwargs to pass to LLM-based evaluators
        member_kwargs = {"is_reasoning_model": kwargs.get("is_reasoning_model", False)}
        if is_decision_model_config(model_config):
            # Decision members need the caller's credential and execution controls; chat members are unchanged.
            member_kwargs.update({name: kwargs[name] for name in _DECISION_MEMBER_OPTIONS if name in kwargs})

        evaluators = [
            GroundednessEvaluator(model_config, threshold=groundedness_threshold, **member_kwargs),
            RelevanceEvaluator(model_config, threshold=relevance_threshold, **member_kwargs),
            CoherenceEvaluator(model_config, threshold=coherence_threshold, **member_kwargs),
            FluencyEvaluator(model_config, threshold=fluency_threshold, **member_kwargs),
            SimilarityEvaluator(model_config, threshold=similarity_threshold, **member_kwargs),
            F1ScoreEvaluator(threshold=f1_score_threshold),
        ]
        super().__init__(evaluators=evaluators, **kwargs)

    @overload  # type: ignore
    def __call__(self, *, query: str, response: str, context: str, ground_truth: str):
        """
        Evaluates question-answering scenario.

        :keyword query: The query to be evaluated.
        :paramtype query: str
        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword context: The context to be evaluated.
        :paramtype context: str
        :keyword ground_truth: The ground truth to be evaluated.
        :paramtype ground_truth: str
        :return: The scores for QA scenario.
        :rtype: Dict[str, Union[str, float]]
        """

    @override
    def __call__(  # pylint: disable=docstring-missing-param
        self,
        *args,
        **kwargs,
    ):
        """
        Evaluates question-answering scenario.

        :keyword query: The query to be evaluated.
        :paramtype query: str
        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword context: The context to be evaluated.
        :paramtype context: str
        :keyword ground_truth: The ground truth to be evaluated.
        :paramtype ground_truth: str
        :return: The scores for QA scenario.
        :rtype: Dict[str, Union[str, float]]
        """

        return super().__call__(*args, **kwargs)
