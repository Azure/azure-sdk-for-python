# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from promptflow._utils.async_utils import async_run_allowing_running_loop
from azure.ai.evaluation._common.constants import EvaluationMetrics
from typing import List, Dict

try:
    from ._content_safety_multimodal_base import ContentSafetyMultimodalEvaluatorBase
except ImportError:
    from _content_safety_multimodal_base import ContentSafetyMultimodalEvaluatorBase

class HateUnfairnessMultimodalEvaluator:
    """
    Initialize a hate-unfairness multimodal evaluator for hate unfairness score.
    :param azure_ai_project: The scope of the Azure AI project.
        It contains subscription id, resource group, and project name.
    :type azure_ai_project: ~azure.ai.evaluation.AzureAIProject
    :param credential: The credential for connecting to Azure AI project.
    :type credential: ~azure.core.credentials.TokenCredential
    **Usage**
    .. code-block:: python
        azure_ai_project = {
            "subscription_id": "<subscription_id>",
            "resource_group_name": "<resource_group_name>",
            "project_name": "<project_name>",
        }
        eval_fn = HateUnfairnessEvaluator(azure_ai_project)
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
            "hate_unfairness": "High",
            "hate_unfairness_score": 6.5,
            "hate_unfairness_reason": "Some reason"
        }
    """
    
    def __init__(self, azure_ai_project: dict, credential=None) -> None:
        self._async_evaluator = _AsyncHateUnfairnessMultimodalEvaluator(azure_ai_project, credential)
    
    def __call__(self, *, messages, **kwargs):
        """
        Evaluates hate unfairness content.
        :keyword messages: The messages to be evaluated. Each message should have "role" and "content" keys.
        :paramtype messages: List[Dict]
        :return: The hate unfairness score.
        :rtype: dict
        """
        return async_run_allowing_running_loop(self._async_evaluator, messages=messages, **kwargs)
    
    def _to_async(self):
        return self._async_evaluator
    

class _AsyncHateUnfairnessMultimodalEvaluator(ContentSafetyMultimodalEvaluatorBase):
    def __init__(self, azure_ai_project: dict, credential=None):
        super().__init__(
            metric=EvaluationMetrics.HATE_FAIRNESS,
            azure_ai_project=azure_ai_project,
            credential=credential,
        )
    
    async def __call__(self, *, messages, **kwargs):
        return await super().__call__(messages=messages, **kwargs)