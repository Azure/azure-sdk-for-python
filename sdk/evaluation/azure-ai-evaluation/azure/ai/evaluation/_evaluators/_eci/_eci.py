# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional
from typing_extensions import override
from azure.ai.evaluation._common.constants import _InternalEvaluationMetrics
from azure.ai.evaluation._evaluators._common import RaiServiceEvaluatorBase


class ECIEvaluator(RaiServiceEvaluatorBase):
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
    :type credential: Optional[~azure.core.credentials.TokenCredential]
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

    @override
    def __init__(
        self,
        azure_ai_project: dict,
        credential: Optional[dict] = None,
        eval_last_turn: bool = False,
    ):
        super().__init__(
            eval_metric=_InternalEvaluationMetrics.ECI,
            azure_ai_project=azure_ai_project,
            credential=credential,
            eval_last_turn=eval_last_turn,
        )
