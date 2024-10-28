# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional

from typing_extensions import override

from azure.ai.evaluation._common._experimental import experimental
from azure.ai.evaluation._common.constants import EvaluationMetrics
from azure.ai.evaluation._evaluators._common import RaiServiceEvaluatorBase


@experimental
class ProtectedMaterialEvaluator(RaiServiceEvaluatorBase):
    """
    Initialize a protected material evaluator to detect whether protected material
    is present in the AI system's response. The evaluator outputs a Boolean label (`True` or `False`)
    indicating the presence of protected material, along with AI-generated reasoning.

    :param credential: The credential required for connecting to the Azure AI project.
    :type credential: ~azure.core.credentials.TokenCredential
    :param azure_ai_project: The scope of the Azure AI project, containing the subscription ID,
        resource group, and project name.
    :type azure_ai_project: ~azure.ai.evaluation.AzureAIProject

    :return: A dictionary with a label indicating the presence of protected material and the reasoning.
    :rtype: Dict[str, Union[bool, str]]

    **Usage Example**

    .. code-block:: python

        azure_ai_project = {
            "subscription_id": "<subscription_id>",
            "resource_group_name": "<resource_group_name>",
            "project_name": "<project_name>",
        }
        eval_fn = ProtectedMaterialEvaluator(azure_ai_project)
        result = eval_fn(query="What is the capital of France?", response="Paris.")

    **Output Format**

    .. code-block:: json

        {
            "protected_material_label": false,
            "protected_material_reason": "This query does not contain any protected material."
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
            eval_metric=EvaluationMetrics.PROTECTED_MATERIAL,
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
        Evaluate if protected material is present in your AI system's response.

        :keyword query: The query to be evaluated.
        :paramtype query: str
        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword conversation: The conversation to evaluate. Expected to contain a list of conversation turns under the
            key "messages". Conversation turns are expected
            to be dictionaries with keys "content" and "role".
        :paramtype conversation: Optional[~azure.ai.evaluation.Conversation]
        :return: The fluency score.
        :rtype: Union[Dict[str, Union[str, bool]], Dict[str, Union[str, bool, Dict[str, List[Union[str, bool]]]]]]
        """
        return super().__call__(query=query, response=response, conversation=conversation, **kwargs)
