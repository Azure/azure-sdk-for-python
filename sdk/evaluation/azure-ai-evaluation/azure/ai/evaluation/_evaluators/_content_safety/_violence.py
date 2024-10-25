# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional

from typing_extensions import override

from azure.ai.evaluation._common._experimental import experimental
from azure.ai.evaluation._common.constants import EvaluationMetrics
from azure.ai.evaluation._evaluators._common import RaiServiceEvaluatorBase


@experimental
class ViolenceEvaluator(RaiServiceEvaluatorBase):
    """
    Initialize a violence evaluator for violence score.

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
        credential = DefaultAzureCredential()
        eval_fn = ViolenceEvaluator(azure_ai_project, credential)
        result = eval_fn(query="What is the capital of France?", response="Paris.")

    **Output format**

    .. code-block:: python

        {
            "violence": "High",
            "violence_score": 6.5,
            "violence_reason": "Some reason"
        }

    **Usage with conversation**

    .. code-block:: python

        azure_ai_project = {
            "subscription_id": "<subscription_id>",
            "resource_group_name": "<resource_group_name>",
            "project_name": "<project_name>",
        }
        credential = DefaultAzureCredential()
        eval_fn = ViolenceEvaluator(azure_ai_project, credential)
        conversation = {
            "messages": [
                {"content": "Hello", "role": "user"},
                {"content": "Hi", "role": "assistant"},
                {"content": "What is the capital of Hawaii?", "role": "user"},
                {"content": "Honolulu", "role": "assistant"}
            ]
        }
        result = eval_fn(conversation=conversation)

    **Output format with conversation input**

    .. code-block:: python

        {
            "violence_score": 4.5,
            "evaluation_per_turn": {
                "violence": ["High", "Low"],
                "violence_score": [6.5, 2.5],
                "violence_reason": ["Some reason", "Some other reason"]
            }
        }
    """

    @override
    def __init__(
        self,
        credential,
        azure_ai_project,
        eval_last_turn: bool = False,
    ):
        super().__init__(
            eval_metric=EvaluationMetrics.VIOLENCE,
            azure_ai_project=azure_ai_project,
            credential=credential,
            eval_last_turn=eval_last_turn,
        )

    @override
    def __call__(
        self,
        *,
        query: Optional[str] = None,
        response: Optional[str] = None,
        conversation=None,
        **kwargs,
    ):
        """
        Evaluate whether violent content is present in your AI system's response.

        :keyword query: The query to be evaluated.
        :paramtype query: str
        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword conversation: The conversation to evaluate. Expected to contain a list of conversation turns under the
            key "messages". Conversation turns are expected
            to be dictionaries with keys "content" and "role".
        :paramtype conversation: Optional[~azure.ai.evaluation.Conversation]
        :return: The violence score. If a multi-turn conversation is provided, the top-level score will be the average
            of all turns, and per-turn evaluation results can be found under the "evaluation_per_turn" key.
        :rtype: Union[Dict[str, Union[str, float]], Dict[str, Union[str, float, Dict[str, List[Union[str, float]]]]]]
        """
        return super().__call__(query=query, response=response, conversation=conversation, **kwargs)
