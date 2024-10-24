# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from concurrent.futures import as_completed
from typing import Callable, Dict, List

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

    **Usage**

    .. code-block:: python

        eval_fn = QAEvaluator(model_config)
        result = qa_eval(
            query="Tokyo is the capital of which country?",
            response="Japan",
            context="Tokyo is the capital of Japan.",
            ground_truth="Japan"
        )

    **Output format**

    .. code-block:: python

        {
            "groundedness": 3.5,
            "relevance": 4.0,
            "coherence": 1.5,
            "fluency": 4.0,
            "similarity": 3.0,
            "gpt_groundedness": 3.5,
            "gpt_relevance": 4.0,
            "gpt_coherence": 1.5,
            "gpt_fluency": 4.0,
            "gpt_similarity": 3.0,
            "f1_score": 0.42
        }
    """

    def __init__(self, model_config, parallel: bool = True):
        self._parallel = parallel

        self._evaluators: List[Callable[..., Dict[str, float]]] = [
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
        :keyword parallel: Whether to evaluate in parallel. Defaults to True.
        :paramtype parallel: bool
        :return: The scores for QA scenario.
        :rtype: Dict[str, float]
        """
        results: Dict[str, float] = {}
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
