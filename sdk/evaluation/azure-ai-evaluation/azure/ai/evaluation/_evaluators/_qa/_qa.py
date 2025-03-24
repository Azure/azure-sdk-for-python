# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional, Union

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
    :param threshold: Optional dictionary of thresholds for different evaluation metrics.
        Keys can be "groundedness", "relevance", "coherence", "fluency", "similarity",
        and "f1_score". Default values are 3 for integer metrics and 0.5 for float
        metrics. If None or an empty dictionary is provided, default values will be
        used for all metrics. If a partial dictionary is provided, default values
        will be used for any missing keys.
    :type threshold: Optional[dict]
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

    id = "qa"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    def __init__(self, model_config, threshold: Optional[dict] = {}, **kwargs):
        default_threshold = {
            "groundedness": 3,
            "relevance": 3,
            "coherence": 3,
            "fluency": 3,
            "similarity": 3,
            "f1_score": 0.5,
        }
        if threshold is None:
            threshold = {}
        for key in default_threshold.keys():
            if key not in threshold:
                threshold[key] = default_threshold[key]
            if not isinstance(threshold[key], (int, float)):
                raise TypeError(
                    f"Threshold for {key} must be an int or float, got {type(threshold[key])}"
                )
        evaluators = [
            GroundednessEvaluator(model_config, threshold=threshold["groundedness"]),
            RelevanceEvaluator(model_config, threshold=threshold["relevance"]),
            CoherenceEvaluator(model_config, threshold=threshold["coherence"]),
            FluencyEvaluator(model_config, threshold=threshold["fluency"]),
            SimilarityEvaluator(model_config, threshold=threshold["similarity"]),
            F1ScoreEvaluator(threshold=threshold["f1_score"]),
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
