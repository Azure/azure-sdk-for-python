# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging

from typing import Optional
from typing_extensions import override
from azure.ai.evaluation._common.constants import EvaluationMetrics
from azure.ai.evaluation._evaluators._common import RaiServiceEvaluatorBase


logger = logging.getLogger(__name__)


class IndirectAttackEvaluator(RaiServiceEvaluatorBase):
    """A Cross-Domain Prompt Injection Attack (XPIA) jailbreak evaluator.

    Detect whether cross domain injected attacks are present in your AI system's response.

    :param azure_ai_project: The scope of the Azure AI project. It contains subscription id, resource group, and project
        name.
    :type azure_ai_project: ~azure.ai.evaluation.AzureAIProject
    :param eval_last_turn: Set to True to evaluate only the most recent exchange in the dialogue,
        focusing on the latest user inquiry and the assistant's corresponding response. Defaults to False
    :type eval_last_turn: bool
    :param credential: The credential for connecting to Azure AI project.
    :type credential: Optional[~azure.core.credentials.TokenCredential]
    :return: A function that evaluates and generates metrics for XPIA chat scenario. Metrics include the overall
        evaluation label and reason for the Q/A Pair, as well as sub-labels for manipulated content, intrusion, and
        information.
    :rtype: Callable
        **Usage**

        .. code-block:: python

            eval_fn = IndirectAttackEvaluator(model_config)
            result = eval_fn(query="What is the capital of France?", response="Paris.")

        **Output format for question-answer pair**

        .. code-block:: python

            {
                'xpia_label': False,
                'xpia_reason': 'The conversation does not contain any manipulated content, intrusion or
                              information gathering.'
                'xpia_information_gathering': False,
                'xpia_intrusion': False
                'xpia_manipulated_content': False
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
            eval_metric=EvaluationMetrics.XPIA,
            azure_ai_project=azure_ai_project,
            credential=credential,
            eval_last_turn=eval_last_turn,
        )
