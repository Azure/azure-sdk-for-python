# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing_extensions import override

from azure.ai.evaluation._common.constants import EvaluationMetrics
from azure.ai.evaluation._evaluators._common import RaiServiceEvaluatorBase


class ViolenceEvaluator(RaiServiceEvaluatorBase):
    """
    Initialize a violence evaluator for violence score.

    :param credential: The credential for connecting to Azure AI project. Required
    :type credential: ~azure.core.credentials.TokenCredential
    :param azure_ai_project: The scope of the Azure AI project.
        It contains subscription id, resource group, and project name.
    :type azure_ai_project: ~azure.ai.evaluation.AzureAIProject

    .. admonition:: Example:

    .. literalinclude:: ../samples/evaluation_samples_evaluate.py
        :start-after: [START violence_evaluator]
        :end-before: [END violence_evaluator]
        :language: python
        :dedent: 8
        :caption: Initialize and call a ViolenceEvaluator.
    """

    @override
    def __init__(
        self,
        credential,
        azure_ai_project: dict,
        eval_last_turn: bool = False,
    ):
        super().__init__(
            eval_metric=EvaluationMetrics.VIOLENCE,
            azure_ai_project=azure_ai_project,
            credential=credential,
            eval_last_turn=eval_last_turn,
        )
