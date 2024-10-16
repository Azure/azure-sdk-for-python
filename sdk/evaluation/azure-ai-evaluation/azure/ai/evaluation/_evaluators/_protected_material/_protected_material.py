# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing_extensions import override

from azure.ai.evaluation._common.constants import EvaluationMetrics
from azure.ai.evaluation._evaluators._common import RaiServiceEvaluatorBase


class ProtectedMaterialEvaluator(RaiServiceEvaluatorBase):
    """
    Initialize a protected material evaluator to detect whether protected material
    is present in your AI system's response. Outputs True or False with AI-generated reasoning.

    :param credential: The credential for connecting to Azure AI project. Required
    :type credential: ~azure.core.credentials.TokenCredential
    :param azure_ai_project: The scope of the Azure AI project.
        It contains subscription id, resource group, and project name.
    :type azure_ai_project: ~azure.ai.evaluation.AzureAIProject
    :return: Whether or not protected material was found in the response, with AI-generated reasoning.
    :rtype: Dict[str, str]

    .. admonition:: Example:

    .. literalinclude:: ../samples/evaluation_samples_evaluate.py
        :start-after: [START protected_material_evaluator]
        :end-before: [END protected_material_evaluator]
        :language: python
        :dedent: 8
        :caption: Initialize and call a ProtectedMaterialEvaluator.
    """

    @override
    def __init__(
        self,
        credential,
        azure_ai_project: dict,
        eval_last_turn: bool = False,
    ):
        super().__init__(
            eval_metric=EvaluationMetrics.PROTECTED_MATERIAL,
            azure_ai_project=azure_ai_project,
            credential=credential,
            eval_last_turn=eval_last_turn,
        )
