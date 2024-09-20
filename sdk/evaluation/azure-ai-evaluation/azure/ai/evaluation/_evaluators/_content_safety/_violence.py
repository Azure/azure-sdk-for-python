# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from promptflow._utils.async_utils import async_run_allowing_running_loop
from azure.ai.evaluation._common.constants import EvaluationMetrics
from azure.ai.evaluation._model_configurations import AzureAIProject

try:
    from ._content_safety_base import ContentSafetyEvaluatorBase
except ImportError:
    from _content_safety_base import ContentSafetyEvaluatorBase


class _AsyncViolenceEvaluator(ContentSafetyEvaluatorBase):
    def __init__(self, azure_ai_project: dict, credential=None):
        super().__init__(
            metric=EvaluationMetrics.VIOLENCE,
            azure_ai_project=azure_ai_project,
            credential=credential,
        )

    async def __call__(self, *, query: str, response: str, **kwargs):
        return await super().__call__(query=query, response=response, **kwargs)


class ViolenceEvaluator:
    """
    Initialize a violence evaluator for violence score.

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
        eval_fn = ViolenceEvaluator(azure_ai_project)
        result = eval_fn(query="What is the capital of France?", response="Paris.")

    **Output format**

    .. code-block:: python

        {
            "violence": "High",
            "violence_score": 6.5,
            "violence_reason": "Some reason"
        }
    """

    def __init__(self, azure_ai_project: dict, credential=None):
        self._async_evaluator = _AsyncViolenceEvaluator(azure_ai_project, credential)

    def __call__(self, *, query: str, response: str, **kwargs):
        """
        Evaluates violence content.

        :keyword query: The query to be evaluated.
        :paramtype query: str
        :keyword response: The response to be evaluated.
        :paramtype response: str
        :return: The violence score.
        :rtype: dict
        """
        return async_run_allowing_running_loop(self._async_evaluator, query=query, response=response, **kwargs)

    def _to_async(self):
        return self._async_evaluator
