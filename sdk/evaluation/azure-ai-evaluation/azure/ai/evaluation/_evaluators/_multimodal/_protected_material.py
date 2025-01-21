# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from promptflow._utils.async_utils import async_run_allowing_running_loop
from azure.ai.evaluation._common.constants import EvaluationMetrics
from azure.ai.evaluation._common.utils import validate_conversation
from azure.ai.evaluation._common.rai_service import evaluate_with_rai_service_multimodal
from azure.ai.evaluation._common._experimental import experimental


@experimental
class ProtectedMaterialMultimodalEvaluator:
    """
    Initialize a protected materials evaluator to detect whether protected material
    is present in multimodal messages. The evaluator outputs a Boolean label (`True` or `False`)
    indicating the presence of protected material, along with AI-generated reasoning.

    :param credential: The credential for connecting to the Azure AI project. This is required.
    :type credential: ~azure.core.credentials.TokenCredential
    :param azure_ai_project: The scope of the Azure AI project, containing the subscription ID,
        resource group, and project name.
    :type azure_ai_project: ~azure.ai.evaluation.AzureAIProject

    :return: A dictionary containing the evaluation result label and reasoning.

    **Usage Example**

    .. code-block:: python

        azure_ai_project = {
            "subscription_id": "<subscription_id>",
            "resource_group_name": "<resource_group_name>",
            "project_name": "<project_name>",
        }
        eval_fn = ProtectedMaterialMultimodalEvaluator(azure_ai_project)
        result = eval_fn(conversation=
            {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "What's in this image?"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": "<image url or base64 encoded image>"
                                }
                            }
                        ]
                    },
                    {
                        "role": "assistant",
                        "content": "This picture shows an astronaut standing in the desert."
                    }
                ]
            }
        )

    **Output Format**

    .. code-block:: json

        {
            "protected_material_label": "False",
            "protected_material_reason": "This query does not contain any protected material."
        }

    """

    id = "protected_material_multimodal"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    def __init__(
        self,
        credential,
        azure_ai_project,
    ):
        self._async_evaluator = _AsyncProtectedMaterialMultimodalEvaluator(credential, azure_ai_project)

    def __call__(self, *, conversation, **kwargs):
        """
        Evaluates protected materials content.

        :keyword conversation: The conversation contains list of messages to be evaluated.
            Each message should have "role" and "content" keys. It supports single turn only.
        :paramtype conversation: ~azure.ai.evaluation.Conversation
        :return: A dictionary containing a boolean label and reasoning.
        :rtype: Dict[str, str]
        """
        return async_run_allowing_running_loop(self._async_evaluator, conversation=conversation, **kwargs)

    def _to_async(self):
        return self._async_evaluator


class _AsyncProtectedMaterialMultimodalEvaluator:
    def __init__(self, credential, azure_ai_project):
        self._credential = credential
        self._azure_ai_project = azure_ai_project

    async def __call__(self, *, conversation, **kwargs):
        """
        Evaluates content according to this evaluator's metric.

        :keyword conversation: The conversation contains list of messages to be evaluated.
            Each message should have "role" and "content" keys. It supports single turn only.
        :paramtype conversation: ~azure.ai.evaluation.Conversation
        :return: The evaluation score computation based on the Content Safety metric (self.metric).
        :rtype: Any
        """
        # Validate inputs
        validate_conversation(conversation)
        messages = conversation["messages"]
        # Run score computation based on supplied metric.
        result = await evaluate_with_rai_service_multimodal(
            messages=messages,
            metric_name=EvaluationMetrics.PROTECTED_MATERIAL,
            credential=self._credential,
            project_scope=self._azure_ai_project,
        )
        return result
