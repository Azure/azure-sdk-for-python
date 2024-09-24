# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from typing import Optional

from promptflow._utils.async_utils import async_run_allowing_running_loop

from azure.ai.evaluation._common.constants import EvaluationMetrics
from azure.ai.evaluation._common.rai_service import evaluate_with_rai_service
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException

logger = logging.getLogger(__name__)


class IndirectAttackEvaluator:
    """A Cross-Domain Prompt Injection Attack (XPIA) jailbreak evaluator.

    Detect whether cross domain injected attacks are present in your AI system's response.

    :param azure_ai_project: The scope of the Azure AI project. It contains subscription id, resource group, and project
        name.
    :type azure_ai_project: ~azure.ai.evaluation.AzureAIProject
    :param eval_last_turn: Set to True to evaluate only the most recent exchange in the dialogue,
        focusing on the latest user inquiry and the assistant's corresponding response. Defaults to False
    :type eval_last_turn: bool
    :param credential: The credential for connecting to Azure AI project.
    :type credential: ~azure.core.credentials.TokenCredential
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

    def __init__(self, azure_ai_project: dict, eval_last_turn: bool = False, credential=None):
        self._evaluator = _IndirectAttackEvaluator(azure_ai_project, credential)
        self._eval_last_turn = eval_last_turn

    def __call__(
        self,
        *,
        query: Optional[str],
        response: Optional[str],
        **kwargs,
    ):
        """
        Evaluates content according to the presence of attacks injected into the conversation context to
        interrupt normal expected functionality by eliciting manipulated content, intrusion and attempting
        to gather information outside the scope of your AI system.
        :keyword query: The query to be evaluated. Mutually exclusive with 'conversation'.
        :paramtype query: Optional[str]
        :keyword response: The response to be evaluated. Mutually exclusive with 'conversation'.
        :paramtype response: Optional[str]
        :return: The evaluation scores and reasoning.
        :rtype: dict
        """

        return self._evaluator(query=query, response=response, **kwargs)


class _AsyncIndirectAttackEvaluator:
    def __init__(self, azure_ai_project: dict, credential=None):
        self._azure_ai_project = azure_ai_project
        self._credential = credential

    async def __call__(self, *, query: str, response: str, **kwargs):
        """
        Evaluates content according to this evaluator's metric.
        :keyword query: The query to be evaluated.
        :paramtype query: str
        :keyword response: The response to be evaluated.
        :paramtype response: str
        :return: The evaluation score computation based on the metric (self.metric).
        :rtype: Any
        """
        # Validate inputs
        # Raises value error if failed, so execution alone signifies success.
        if not (query and query.strip() and query != "None") or not (
            response and response.strip() and response != "None"
        ):
            msg = "Both 'query' and 'response' must be non-empty strings."
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                error_category=ErrorCategory.MISSING_FIELD,
                error_blame=ErrorBlame.USER_ERROR,
                error_target=ErrorTarget.INDIRECT_ATTACK_EVALUATOR,
            )

        # Run score computation based on supplied metric.
        result = await evaluate_with_rai_service(
            metric_name=EvaluationMetrics.XPIA,
            query=query,
            response=response,
            project_scope=self._azure_ai_project,
            credential=self._credential,
        )
        return result


class _IndirectAttackEvaluator:
    def __init__(self, azure_ai_project: dict, credential=None):
        self._async_evaluator = _AsyncIndirectAttackEvaluator(azure_ai_project, credential)

    def __call__(self, *, query: str, response: str, **kwargs):
        """
        Evaluates XPIA content.
        :keyword query: The query to be evaluated.
        :paramtype query: str
        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword context: The context to be evaluated.
        :paramtype context: str
        :return: The XPIA score.
        :rtype: dict
        """
        return async_run_allowing_running_loop(self._async_evaluator, query=query, response=response, **kwargs)

    def _to_async(self):
        return self._async_evaluator
