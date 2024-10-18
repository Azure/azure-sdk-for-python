# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from concurrent.futures import as_completed
from typing import Callable, Dict, List, Union

from promptflow.tracing import ThreadPoolExecutorWithContext as ThreadPoolExecutor

from azure.ai.evaluation._common._experimental import experimental

from ._hate_unfairness import HateUnfairnessEvaluator
from ._self_harm import SelfHarmEvaluator
from ._sexual import SexualEvaluator
from ._violence import ViolenceEvaluator


@experimental
class ContentSafetyEvaluator:
    """
    Initialize a content safety evaluator configured to evaluate content safetry metrics for QA scenario.

    :param credential: The credential for connecting to Azure AI project. Required
    :type credential: ~azure.core.credentials.TokenCredential
    :param azure_ai_project: The scope of the Azure AI project.
        It contains subscription id, resource group, and project name.
    :type azure_ai_project: ~azure.ai.evaluation.AzureAIProject
    :param parallel: If True, use parallel execution for evaluators. Else, use sequential execution.
        Default is True.

    **Usage**

    .. code-block:: python

        azure_ai_project = {
            "subscription_id": "<subscription_id>",
            "resource_group_name": "<resource_group_name>",
            "project_name": "<project_name>",
        }
        eval_fn = ContentSafetyEvaluator(azure_ai_project)
        result = eval_fn(
            query="What is the capital of France?",
            response="Paris.",
        )

    **Output format**

    .. code-block:: python

        {
            "violence": "Medium",
            "violence_score": 5.0,
            "violence_reason": "Some reason",
            "sexual": "Medium",
            "sexual_score": 5.0,
            "sexual_reason": "Some reason",
            "self_harm": "Medium",
            "self_harm_score": 5.0,
            "self_harm_reason": "Some reason",
            "hate_unfairness": "Medium",
            "hate_unfairness_score": 5.0,
            "hate_unfairness_reason": "Some reason"
        }
    """

    def __init__(self, credential, azure_ai_project, parallel: bool = True):
        self._parallel = parallel
        self._evaluators: List[Callable[..., Dict[str, Union[str, float]]]] = [
            ViolenceEvaluator(credential, azure_ai_project),
            SexualEvaluator(credential, azure_ai_project),
            SelfHarmEvaluator(credential, azure_ai_project),
            HateUnfairnessEvaluator(credential, azure_ai_project),
        ]

    def __call__(self, *, query: str, response: str, **kwargs):
        """
        Evaluates content-safety metrics for "question-answering" scenario.

        :keyword query: The query to be evaluated.
        :paramtype query: str
        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword parallel: Whether to evaluate in parallel.
        :paramtype parallel: bool
        :return: The scores for content-safety.
        :rtype: Dict[str, Union[str, float]]
        """
        results: Dict[str, Union[str, float]] = {}
        if self._parallel:
            with ThreadPoolExecutor() as executor:
                futures = {
                    executor.submit(evaluator, query=query, response=response, **kwargs): evaluator
                    for evaluator in self._evaluators
                }

                for future in as_completed(futures):
                    results.update(future.result())
        else:
            for evaluator in self._evaluators:
                result = evaluator(query=query, response=response, **kwargs)
                results.update(result)

        return results
