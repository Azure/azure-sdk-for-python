# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from concurrent.futures import as_completed
from typing import Callable, Dict, List, Union

from promptflow.tracing import ThreadPoolExecutorWithContext as ThreadPoolExecutor

from .._coherence import CoherenceEvaluator
from .._f1_score import F1ScoreEvaluator
from .._fluency import FluencyEvaluator
from .._groundedness import GroundednessEvaluator
from .._relevance import RelevanceEvaluator
from .._similarity import SimilarityEvaluator


class QAEvaluator:
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
        self._parallel = kwargs.pop("_parallel", False)

        self._evaluators: List[Union[Callable[..., Dict[str, Union[str, float]]], Callable[..., Dict[str, float]]]] = [
            GroundednessEvaluator(model_config),
            RelevanceEvaluator(model_config),
            CoherenceEvaluator(model_config),
            FluencyEvaluator(model_config),
            SimilarityEvaluator(model_config),
            F1ScoreEvaluator(),
        ]

    def __call__(self, *, query: str, response: str, context: str, ground_truth: str, **kwargs):
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
        results: Dict[str, Union[str, float]] = {}
        if self._parallel:
            with ThreadPoolExecutor() as executor:
                futures = {
                    executor.submit(
                        evaluator, query=query, response=response, context=context, ground_truth=ground_truth, **kwargs
                    ): evaluator
                    for evaluator in self._evaluators
                }

                # Collect results as they complete
                for future in as_completed(futures):
                    results.update(future.result())
        else:
            for evaluator in self._evaluators:
                result = evaluator(query=query, response=response, context=context, ground_truth=ground_truth, **kwargs)
                results.update(result)

        return results
