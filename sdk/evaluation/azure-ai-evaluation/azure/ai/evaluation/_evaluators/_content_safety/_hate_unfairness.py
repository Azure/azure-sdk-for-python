# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, List, Union

from typing_extensions import overload, override

from azure.ai.evaluation._common._experimental import experimental
from azure.ai.evaluation._common.constants import EvaluationMetrics
from azure.ai.evaluation._evaluators._common import RaiServiceEvaluatorBase
from azure.ai.evaluation._model_configurations import Conversation


@experimental
class HateUnfairnessEvaluator(RaiServiceEvaluatorBase[Union[str, float]]):
    """
    Initialize a hate-unfairness evaluator for hate unfairness score.

    :param credential: The credential for connecting to Azure AI project. Required
    :type credential: ~azure.core.credentials.TokenCredential
    :param azure_ai_project: The scope of the Azure AI project.
        It contains subscription id, resource group, and project name.
    :type azure_ai_project: ~azure.ai.evaluation.AzureAIProject

    **Usage**

    .. code-block:: python

        azure_ai_project = {
            "subscription_id": "<subscription_id>",
            "resource_group_name": "<resource_group_name>",
            "project_name": "<project_name>",
        }
        eval_fn = HateUnfairnessEvaluator(azure_ai_project)
        result = eval_fn(query="What is the capital of France?", response="Paris.")

    **Output format**

    .. code-block:: python

        {
            "hate_unfairness": "High",
            "hate_unfairness_score": 6.5,
            "hate_unfairness_reason": "Some reason"
        }
    """

    @override
    def __init__(
        self,
        credential,
        azure_ai_project,
    ):
        super().__init__(
            eval_metric=EvaluationMetrics.HATE_FAIRNESS,
            azure_ai_project=azure_ai_project,
            credential=credential,
        )

    @overload
    def __call__(
        self,
        *,
        query: str,
        response: str,
    ) -> Dict[str, Union[str, float]]:
        """Evaluate the given query/response pair for hateful content

        :keyword query: The query to be evaluated.
        :paramtype query: str
        :keyword response: The response to be evaluated.
        :paramtype response: str
        :return: The hate score
        :rtype: Dict[str, Union[str, float]]
        """

    @overload
    def __call__(
        self,
        *,
        conversation: Conversation,
    ) -> Dict[str, Union[float, Dict[str, List[Union[str, float]]]]]:
        """Evaluate a conversation for hateful content

        :keyword conversation: The conversation to evaluate. Expected to contain a list of conversation turns under the
            key "messages", and potentially a global context under the key "context". Conversation turns are expected
            to be dictionaries with keys "content", "role", and possibly "context".
        :paramtype conversation: Optional[~azure.ai.evaluation.Conversation]
        :return: The hate score
        :rtype: Dict[str, Union[float, Dict[str, List[Union[str, float]]]]]
        """

    @override
    def __call__(  # pylint: disable=docstring-missing-param
        self,
        *args,
        **kwargs,
    ):
        """
        Evaluate whether hateful content is present in your AI system's response.

        :keyword query: The query to be evaluated.
        :paramtype query: Optional[str]
        :keyword response: The response to be evaluated.
        :paramtype response: Optional[str]
        :keyword conversation: The conversation to evaluate. Expected to contain a list of conversation turns under the
            key "messages". Conversation turns are expected
            to be dictionaries with keys "content" and "role".
        :paramtype conversation: Optional[~azure.ai.evaluation.Conversation]
        :return: The fluency score.
        :rtype: Union[Dict[str, Union[str, float]], Dict[str, Union[float, Dict[str, List[Union[str, float]]]]]]
        """
        return super().__call__(*args, **kwargs)
