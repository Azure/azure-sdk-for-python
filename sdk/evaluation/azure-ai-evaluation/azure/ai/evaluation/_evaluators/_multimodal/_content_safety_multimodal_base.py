# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from abc import ABC

from typing import Dict, List

from azure.ai.evaluation._common.constants import EvaluationMetrics
from azure.ai.evaluation._common.rai_service import evaluate_with_rai_service_multimodal


class ContentSafetyMultimodalEvaluatorBase(ABC):
    """
    Initialize a evaluator for a specified Evaluation Metric. Base class that is not
    meant to be instantiated by users.


    :param metric: The metric to be evaluated.
    :type metric: ~azure.ai.evaluation._evaluators._content_safety.flow.constants.EvaluationMetrics
    :param azure_ai_project: The scope of the Azure AI project.
        It contains subscription id, resource group, and project name.
    :type azure_ai_project: ~azure.ai.evaluation.AzureAIProject
    :param credential: The credential for connecting to Azure AI project.
    :type credential: ~azure.core.credentials.TokenCredential
    """

    def __init__(self, metric: EvaluationMetrics, azure_ai_project: dict, credential=None):
        self._metric = metric
        self._azure_ai_project = azure_ai_project
        self._credential = credential

    async def __call__(self, *, messages: List[Dict], **kwargs):
        """
        Evaluates content according to this evaluator's metric.

        :keyword messages: List of messages also known as conversation.
        :paramtype messages: List[Dict]
        :return: The evaluation score computation based on the Content Safety metric (self.metric).
        :rtype: Any
        """
        # Validate inputs
        
        # Run score computation based on supplied metric.
        result = await evaluate_with_rai_service_multimodal(
            messages=messages,
            metric_name=self._metric,
            project_scope=self._azure_ai_project,
            credential=self._credential,
        )
        return result
