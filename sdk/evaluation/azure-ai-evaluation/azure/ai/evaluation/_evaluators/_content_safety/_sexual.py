# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing_extensions import override
from azure.ai.evaluation._common.constants import EvaluationMetrics
from azure.ai.evaluation._model_configurations import AzureAIProject
from azure.ai.evaluation._evaluators._common._base_rai_svc_eval import BaseRaiServiceEval


class SexualEvaluator(BaseRaiServiceEval):
    """
    Initialize a sexual evaluator for sexual score.

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
        eval_fn = SexualEvaluator(azure_ai_project)
        result = eval_fn(query="What is the capital of France?", response="Paris.")

    **Output format**

    .. code-block:: python

        {
            "sexual": "High",
            "sexual_score": 6.5,
            "sexual_reason": "Some reason"
        }
    """

    @override
    def __init__(self, azure_ai_project: AzureAIProject, credential=None, eval_last_turn: bool = False):
        return super().__init__(eval_metric=EvaluationMetrics.SEXUAL, azure_ai_project=azure_ai_project, credential=credential, eval_last_turn=eval_last_turn)
