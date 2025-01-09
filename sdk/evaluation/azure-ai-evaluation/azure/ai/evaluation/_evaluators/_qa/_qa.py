# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Union

from typing_extensions import overload, override

from azure.ai.evaluation._evaluators._common import MultiEvaluatorBase

from .._coherence import CoherenceEvaluator
from .._f1_score import F1ScoreEvaluator
from .._fluency import FluencyEvaluator
from .._groundedness import GroundednessEvaluator
from .._relevance import RelevanceEvaluator
from .._similarity import SimilarityEvaluator


class QAEvaluator(MultiEvaluatorBase[Union[str, float]]):
    """
    Initialize a question-answer evaluator configured for a specific Azure OpenAI model.

    :param model_config: Configuration for the Azure OpenAI model.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]
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

    .. note::

        To align with our support of a diverse set of models, keys without the `gpt_` prefix has been added.
        To maintain backwards compatibility, the old keys with the `gpt_` prefix are still be present in the output;
        however, it is recommended to use the new keys moving forward as the old keys will be deprecated in the future.
    """

    id = "qa"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    def __init__(self, model_config, **kwargs):
        evaluators = [
            GroundednessEvaluator(model_config),
            RelevanceEvaluator(model_config),
            CoherenceEvaluator(model_config),
            FluencyEvaluator(model_config),
            SimilarityEvaluator(model_config),
            F1ScoreEvaluator(),
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
