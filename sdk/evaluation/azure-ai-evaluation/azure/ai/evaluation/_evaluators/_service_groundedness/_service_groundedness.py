# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing_extensions import override

from azure.ai.evaluation._common.constants import EvaluationMetrics
from azure.ai.evaluation._evaluators._common import RaiServiceEvaluatorBase


class GroundednessProEvaluator(RaiServiceEvaluatorBase):
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
        eval_fn = GroundednessProEvaluator(azure_ai_project)
        result = eval_fn(response="Paris", context="Paris.")

    **Output format**

    .. code-block:: python

        {
            "groundedness": 5,
            "reason": "The response is grounded"
        }
    """

    @override
    def __init__(
        self,
        credential,
        azure_ai_project: dict,
    ):
        super().__init__(
            eval_metric=EvaluationMetrics.GROUNDEDNESS,
            azure_ai_project=azure_ai_project,
            credential=credential,
        )
