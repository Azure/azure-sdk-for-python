# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from concurrent.futures import as_completed
from typing import Callable, Dict, List, Optional, Union

from promptflow.tracing import ThreadPoolExecutorWithContext as ThreadPoolExecutor
from typing_extensions import override

from azure.ai.evaluation._common._experimental import experimental
from azure.ai.evaluation._evaluators._common import EvaluatorBase

from ._hate_unfairness import HateUnfairnessEvaluator
from ._self_harm import SelfHarmEvaluator
from ._sexual import SexualEvaluator
from ._violence import ViolenceEvaluator


@experimental
class ContentSafetyEvaluator(EvaluatorBase):
    """
    Initialize a content safety evaluator configured to evaluate content safetry metrics for QA scenario.

    :param credential: The credential for connecting to Azure AI project. Required
    :type credential: ~azure.core.credentials.TokenCredential
    :param azure_ai_project: The scope of the Azure AI project.
        It contains subscription id, resource group, and project name.
    :type azure_ai_project: ~azure.ai.evaluation.AzureAIProject
    :param eval_last_turn: Whether to evaluate the last turn of a conversation. Default is False.
    :type eval_last_turn: bool
    :param kwargs: Additional arguments to pass to the evaluator.
    :type kwargs: Any
    :return: A function that evaluates content-safety metrics for "question-answering" scenario.
    :rtype: Callable

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

    # TODO address 3579092 to re-enabled parallel evals.
    def __init__(self, credential, azure_ai_project, eval_last_turn: bool = False, **kwargs):
        super().__init__(eval_last_turn=eval_last_turn)
        self._parallel = kwargs.pop("parallel", False)
        self._evaluators: List[Callable[..., Dict[str, Union[str, float]]]] = [
            ViolenceEvaluator(credential, azure_ai_project),
            SexualEvaluator(credential, azure_ai_project),
            SelfHarmEvaluator(credential, azure_ai_project),
            HateUnfairnessEvaluator(credential, azure_ai_project),
        ]

    @override
    def __call__(
        self,
        *,
        query: Optional[str] = None,
        response: Optional[str] = None,
        conversation=None,
        **kwargs,
    ):
        """Evaluate a collection of content safety metrics for the given query/response pair or conversation.
        This inputs must supply either a query AND response, or a conversation, but not both.

        :keyword query: The query to evaluate.
        :paramtype query: Optional[str]
        :keyword response: The response to evaluate.
        :paramtype response: Optional[str]
        :keyword conversation: The conversation to evaluate. Expected to contain a list of conversation turns under the
            key "messages", and potentially a global context under the key "context". Conversation turns are expected
            to be dictionaries with keys "content", "role", and possibly "context".
        :paramtype conversation: Optional[~azure.ai.evaluation.Conversation]
        :return: The evaluation result.
        :rtype: Union[Dict[str, Union[str, float]], Dict[str, Union[str, float, Dict[str, List[Union[str, float]]]]]]
        """
        return super().__call__(query=query, response=response, conversation=conversation, **kwargs)

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict[str, Union[str, float]]:
        """Perform the evaluation using the Azure AI RAI service.
        The exact evaluation performed is determined by the evaluation metric supplied
        by the child class initializer.

        :param eval_input: The input to the evaluation function.
        :type eval_input: Dict
        :return: The evaluation result.
        :rtype: Dict
        """
        query = eval_input.get("query", None)
        response = eval_input.get("response", None)
        conversation = eval_input.get("conversation", None)
        results: Dict[str, Union[str, float]] = {}
        # TODO fix this to not explode on empty optional inputs (PF SKD error)
        if self._parallel:
            with ThreadPoolExecutor() as executor:
                # pylint: disable=no-value-for-parameter
                futures = {
                    executor.submit(query=query, response=response, conversation=conversation): evaluator
                    for evaluator in self._evaluators
                }

                for future in as_completed(futures):
                    results.update(future.result())
        else:
            for evaluator in self._evaluators:
                result = evaluator(query=query, response=response, conversation=conversation)
                results.update(result)

        return results
