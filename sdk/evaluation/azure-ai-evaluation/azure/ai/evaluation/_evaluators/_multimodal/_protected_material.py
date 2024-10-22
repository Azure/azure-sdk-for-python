# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from promptflow._utils.async_utils import async_run_allowing_running_loop

from azure.ai.evaluation._common.constants import EvaluationMetrics
from azure.ai.evaluation._common.rai_service import evaluate_with_rai_service_multimodal


class ProtectedMaterialMultimodalEvaluator:
    """
    Initialize a protected materials evaluator to detect whether protected material
    is present in multimodal messages. Outputs True or False with AI-generated reasoning.

    :param credential: The credential for connecting to Azure AI project. Required
    :type credential: ~azure.core.credentials.TokenCredential
    :param azure_ai_project: The scope of the Azure AI project.
        It contains subscription id, resource group, and project name.
    :type azure_ai_project: ~azure.ai.evaluation.AzureAIProject
    :return: Whether or not protected material was found in the response, with AI-generated reasoning.
    :rtype: Dict[str, str]

    **Usage**
    .. code-block:: python
        azure_ai_project = {
            "subscription_id": "<subscription_id>",
            "resource_group_name": "<resource_group_name>",
            "project_name": "<project_name>",
        }
        eval_fn = ProtectedMaterialMultimodalEvaluator(azure_ai_project)
        result = eval_fn(
            messages= [
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
                    "content": "This picture shows an astronaut standing in desert."
                }
            ]
        )
    
    **Output format**
    .. code-block:: python
        {
            "protected_material_label": "False",
            "protected_material_reason": "This query does not contain any protected material."
        }
    """
    
    def __init__(self, azure_ai_project: dict, credential=None):
        self._async_evaluator = _AsyncProtectedMaterialMultimodalEvaluator(azure_ai_project, credential)

    def __call__(self, *, messages, **kwargs):
        """
        Evaluates protected materials content.

        :keyword messages: The messages to be evaluated. Each message should have "role" and "content" keys.
        :paramtype messages: List[Dict]
        :return: A dictionary containing a boolean label and reasoning.
        :rtype: dict
        """
        return async_run_allowing_running_loop(self._async_evaluator, messages=messages, **kwargs)

    def _to_async(self):
        return self._async_evaluator

class _AsyncProtectedMaterialMultimodalEvaluator:
    def __init__(self, azure_ai_project: dict, credential: None):
        self._azure_ai_project = azure_ai_project
        self._credential = credential

    async def __call__(self, *, messages, **kwargs):
        """
        Evaluates content according to this evaluator's metric.
        :keyword messages: The messages to be evaluated. Each message should have "role" and "content" keys.
        :paramtype messages: List[Dict]
        :return: The evaluation score computation based on the Content Safety metric (self.metric).
        :rtype: Any
        """
        # Validate inputs
        
        # Run score computation based on supplied metric.
        result = await evaluate_with_rai_service_multimodal(
            messages=messages,
            metric_name=EvaluationMetrics.PROTECTED_MATERIAL,
            project_scope=self._azure_ai_project,
            credential=self._credential,
        )
        return result