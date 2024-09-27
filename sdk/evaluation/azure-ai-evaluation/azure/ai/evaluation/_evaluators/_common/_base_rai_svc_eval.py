# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, Optional
from typing_extensions import override

from abc import ABC

from typing import Dict
from azure.core.credentials import TokenCredential
from azure.ai.evaluation._common.constants import EvaluationMetrics
from azure.ai.evaluation._common.rai_service import evaluate_with_rai_service
from azure.ai.evaluation._model_configurations import AzureAIProject
from azure.ai.evaluation._exceptions import EvaluationException
from . import _BaseEval


class _BaseRaiServiceEval(_BaseEval):
    """Base class for all evaluators that require the use of the Azure AI RAI service for evaluation.
    This includes content safety evaluators, protected material evaluators, and others. These evaluators
    are all assumed to be of the "query and response or conversation" input variety.

    param eval_metric: The evaluation metric to be used for evaluation. This is used by the API call logic
    to specify which evaluation to perform.
    type eval_metric: ~azure.ai.evaluation._common.constants.EvaluationMetrics
    param azure_ai_project: The scope of the Azure AI project.
    type azure_ai_project: ~azure.ai.evaluation.AzureAIProject
    param credential: The credential for connecting to the Azure AI project.
    type credential: ~azure.core.credentials.TokenCredential
    param eval_last_turn: If True, only the last turn of the conversation will be evaluated, and no
        aggregation will be performed. If False, all turns will be evaluated and the numeric results will be,
        aggregated. Per-turn results are still be available in the output via the "evaluation_per_turn" key
        when this occurs. Default is False, resulting full conversation evaluation and aggregation.
    type eval_last_turn: bool
    """

    @override
    def __init__(
        self,
        eval_metric: EvaluationMetrics,
        azure_ai_project: AzureAIProject,
        credential: TokenCredential,
        eval_last_turn: bool = False,
    ):
        super().__init__(eval_last_turn=eval_last_turn)
        self._eval_metric = eval_metric
        self._azure_ai_project = azure_ai_project
        self._credential = credential

    @override
    def __call__(
        self,
        *,
        query: Optional[str] = None,
        response: Optional[str] = None,
        conversation: Optional[Dict] = None,
        **kwargs
    ):
        """Evaluate either a query and response or a conversation. Must supply either a query AND response, or a conversation,
        but not both.

        param query: The query to evaluate.
        type query: Optional[str]
        param response: The response to evaluate.
        type response: Optional[str]
        param conversation: The conversation to evaluate. Expected to contain a list of conversation turns under the
            key "messages", and potentially a global context under the key "context". Conversation turns are expected
            to be dictionaries with keys "content", "role", and possibly "context".
        type conversation: Optional[Dict]
        """
        return super().__call__(query=query, response=response, conversation=conversation, **kwargs)

    @override
    async def _do_eval(self, eval_input: Dict):
        query = eval_input.get("query", None)
        response = eval_input.get("response", None)
        if query is None or response is None:
            raise EvaluationException(
                message="Not implemented",
                internal_message=(
                    "Reached query/response evaluation without supplying query or response."
                    + " This should have failed earlier."
                ),
            )
        return await evaluate_with_rai_service(
            metric_name=self._eval_metric,
            query=query,
            response=response,
            project_scope=self._azure_ai_project,
            credential=self._credential,
        )
