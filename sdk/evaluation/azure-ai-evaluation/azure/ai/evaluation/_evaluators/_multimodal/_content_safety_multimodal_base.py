# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC
from typing import Union
from azure.ai.evaluation._common.rai_service import evaluate_with_rai_service_multimodal
from azure.ai.evaluation._common.constants import EvaluationMetrics, _InternalEvaluationMetrics
from azure.ai.evaluation._common.utils import validate_conversation
from azure.core.credentials import TokenCredential


class ContentSafetyMultimodalEvaluatorBase(ABC):
    """
    Initialize a evaluator for a specified Evaluation Metric. Base class that is not
    meant to be instantiated by users.

    :param metric: The metric to be evaluated.
    :type metric: ~azure.ai.evaluation._evaluators._content_safety.flow.constants.EvaluationMetrics
    :param credential: The credential for connecting to Azure AI project. Required
    :type credential: ~azure.core.credentials.TokenCredential
    :param azure_ai_project: The scope of the Azure AI project.
        It contains subscription id, resource group, and project name.
    :type azure_ai_project: ~azure.ai.evaluation.AzureAIProject
    """

    def __init__(
        self,
        metric: Union[EvaluationMetrics, _InternalEvaluationMetrics],
        credential: TokenCredential,
        azure_ai_project,
    ):
        self._metric = metric
        self._azure_ai_project = azure_ai_project
        self._credential = credential

    async def __call__(self, *, conversation, **kwargs):
        """
        Evaluates content according to this evaluator's metric.
        :keyword conversation: The conversation contains list of messages to be evaluated.
            Each message should have "role" and "content" keys.
        :paramtype conversation: ~azure.ai.evaluation.Conversation
        :return: The evaluation score computation based on the Content Safety metric (self.metric).
        :rtype: Dict[str, Union[float, str]]
        """
        # validate inputs
        validate_conversation(conversation)
        messages = conversation["messages"]
        # Run score computation based on supplied metric.
        result = await evaluate_with_rai_service_multimodal(
            messages=messages,
            metric_name=self._metric,
            project_scope=self._azure_ai_project,
            credential=self._credential,
        )
        return result
