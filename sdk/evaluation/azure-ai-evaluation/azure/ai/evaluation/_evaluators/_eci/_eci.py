# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from promptflow._utils.async_utils import async_run_allowing_running_loop
from azure.ai.evaluation._common.constants import _InternalEvaluationMetrics
from azure.ai.evaluation._common.rai_service import evaluate_with_rai_service
from azure.ai.evaluation._model_configurations import AzureAIProject


class _AsyncECIEvaluator:
    def __init__(self, azure_ai_project: dict, credential=None):
        self._azure_ai_project = azure_ai_project
        self._credential = credential

    async def __call__(self, *, query: str, response: str, **kwargs):
        # Validate inputs
        # Raises value error if failed, so execution alone signifies success.
        if not (query and query.strip() and query != "None") or not (
            response and response.strip() and response != "None"
        ):
            raise ValueError("Both 'query' and 'response' must be non-empty strings.")

        # Run score computation based on supplied metric.
        result = await evaluate_with_rai_service(
            metric_name=_InternalEvaluationMetrics.ECI,
            query=query,
            response=response,
            project_scope=self._azure_ai_project,
            credential=self._credential,
        )
        return result


class ECIEvaluator:
    """
    Initialize an ECI evaluator to evaluate ECI based on the following guidelines:
    Detects whether ECI is present without a disclaimer in the AI system’s response.
    After the response is annotated by GPT using the binary annotation prompt
    (which checks for disclaimer or authoritative sources),
    we now want to check, if there was a disclaimer, the language should be exactly
    "AI-generated content may be incorrect. If you are seeking ECI-related information, please go to Bing Search."
    Outputs True or False with AI-generated reasoning.

    :param azure_ai_project: The scope of the Azure AI project.
        It contains subscription id, resource group, and project name.
    :type azure_ai_project: ~azure.ai.evaluation.AzureAIProject
    :param credential: The credential for connecting to Azure AI project.
    :type credential: ~azure.core.credentials.TokenCredential
    :return: Whether or not ECI was found in the response without a disclaimer, with AI-generated reasoning
    :rtype: Dict[str, str]

    **Usage**

    .. code-block:: python

        azure_ai_project = {
            "subscription_id": "<subscription_id>",
            "resource_group_name": "<resource_group_name>",
            "project_name": "<project_name>",
        }
        eval_fn = ECIEvaluator(azure_ai_project)
        result = eval_fn(query="What is the capital of France?", response="Paris.")

    **Output format**

    .. code-block:: python

        {
            "eci_label": "False",
            "eci_reason": "Some reason."
        }
    """

    def __init__(self, azure_ai_project: dict, credential=None) -> None:
        self._async_evaluator = _AsyncECIEvaluator(azure_ai_project, credential)

    def __call__(self, *, query: str, response: str, **kwargs):
        """
        Evaluates ECI content.

        :keyword query: The query to be evaluated.
        :paramtype query: str
        :keyword response: The response to be evaluated.
        :paramtype response: str
        :return: The ECI result.
        :rtype: dict
        """
        return async_run_allowing_running_loop(self._async_evaluator, query=query, response=response, **kwargs)

    def _to_async(self):
        return self._async_evaluator
