# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, TypeVar, Union

from typing_extensions import override

from azure.ai.evaluation._common.constants import (
    EvaluationMetrics,
    _InternalEvaluationMetrics,
    Tasks,
    _InternalAnnotationTasks,
)
from azure.ai.evaluation._common.rai_service import evaluate_with_rai_service, evaluate_with_rai_service_multimodal
from azure.ai.evaluation._common.utils import validate_azure_ai_project
from azure.ai.evaluation._exceptions import EvaluationException
from azure.ai.evaluation._common.utils import validate_conversation
from azure.ai.evaluation._constants import AggregationType
from azure.core.credentials import TokenCredential

from . import EvaluatorBase

T = TypeVar("T")


class RaiServiceEvaluatorBase(EvaluatorBase[T]):
    """Base class for all evaluators that require the use of the Azure AI RAI service for evaluation.
    This includes content safety evaluators, protected material evaluators, and others. These evaluators
    are all assumed to be of the "query and response or conversation" input variety.

    :param eval_metric: The evaluation metric to be used for evaluation. This is used by the API call logic
        to specify which evaluation to perform.
    :type eval_metric: ~azure.ai.evaluation._common.constants.EvaluationMetrics
    :param eval_last_turn: If True, only the last turn of the conversation will be evaluated, and no
        aggregation will be performed. If False, all turns will be evaluated and the numeric results will be,
        aggregated. Per-turn results are still be available in the output via the "evaluation_per_turn" key
        when this occurs. Default is False, resulting full conversation evaluation and aggregation.
    :type eval_last_turn: bool
    :param conversation_aggregation_type: The type of aggregation to perform on the per-turn results of a conversation
        to produce a single result.
        Default is ~azure.ai.evaluation.AggregationType.MEAN.
    :type conversation_aggregation_type: ~azure.ai.evaluation.AggregationType
    """

    @override
    def __init__(
        self,
        eval_metric: Union[EvaluationMetrics, _InternalEvaluationMetrics],
        azure_ai_project: dict,
        credential: TokenCredential,
        eval_last_turn: bool = False,
        conversation_aggregation_type: AggregationType = AggregationType.MEAN,
    ):
        super().__init__(eval_last_turn=eval_last_turn, conversation_aggregation_type=conversation_aggregation_type)
        self._eval_metric = eval_metric
        self._azure_ai_project = validate_azure_ai_project(azure_ai_project)
        self._credential = credential

    @override
    def __call__(  # pylint: disable=docstring-missing-param
        self,
        *args,
        **kwargs,
    ):
        """Evaluate either a query and response or a conversation. Must supply either a query AND response,
        or a conversation, but not both.

        :keyword query: The query to evaluate.
        :paramtype query: Optional[str]
        :keyword response: The response to evaluate.
        :paramtype response: Optional[str]
        :keyword conversation: The conversation to evaluate. Expected to contain a list of conversation turns under the
            key "messages", and potentially a global context under the key "context". Conversation turns are expected
            to be dictionaries with keys "content", "role", and possibly "context".
        :paramtype conversation: Optional[~azure.ai.evaluation.Conversation]
        :rtype: Union[Dict[str, T], Dict[str, Union[float, Dict[str, List[T]]]]]
        """
        return super().__call__(*args, **kwargs)

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict[str, T]:
        """Perform the evaluation using the Azure AI RAI service.
        The exact evaluation performed is determined by the evaluation metric supplied
        by the child class initializer.

        :param eval_input: The input to the evaluation function.
        :type eval_input: Dict
        :return: The evaluation result.
        :rtype: Dict
        """
        if "query" in eval_input and "response" in eval_input:
            return await self._evaluate_query_response(eval_input)

        conversation = eval_input.get("conversation", None)
        return await self._evaluate_conversation(conversation)

    async def _evaluate_conversation(self, conversation: Dict) -> Dict[str, T]:
        """
        Evaluates content according to this evaluator's metric.
        :keyword conversation: The conversation contains list of messages to be evaluated.
            Each message should have "role" and "content" keys.

        :param conversation: The conversation to evaluate.
        :type conversation: ~azure.ai.evaluation.Conversation
        :return: The evaluation score computation based on the Content Safety metric (self.metric).
        :rtype: Dict[str, Union[float, str]]
        """
        # validate inputs
        validate_conversation(conversation)
        messages = conversation["messages"]
        # Run score computation based on supplied metric.
        result = await evaluate_with_rai_service_multimodal(
            messages=messages,
            metric_name=self._eval_metric,
            project_scope=self._azure_ai_project,
            credential=self._credential,
        )
        return result

    async def _evaluate_query_response(self, eval_input: Dict) -> Dict[str, T]:
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
        input_data = {"query": query, "response": response}

        if "context" in self._singleton_inputs:
            context = eval_input.get("context", None)
            if context is None:
                raise EvaluationException(
                    message="Not implemented",
                    internal_message=(
                        "Attempted context-based evaluation without supplying context."
                        + " This should have failed earlier."
                    ),
                )
            input_data["context"] = context

        return await evaluate_with_rai_service(  # type: ignore
            metric_name=self._eval_metric,
            data=input_data,
            project_scope=self._azure_ai_project,
            credential=self._credential,
            annotation_task=self._get_task(),
            evaluator_name=self.__class__.__name__,
        )

    def _get_task(self):
        """Get the annotation task for the current evaluation metric.
        The annotation task is used by the RAI service script to determine a the message format
        of the API call, and how the output is processed, among other things.

        :return: The annotation task for the evaluator's self._eval_metric value.
        :rtype: ~azure.ai.evaluation._common.constants.Tasks

        """
        if self._eval_metric == EvaluationMetrics.GROUNDEDNESS:
            return Tasks.GROUNDEDNESS
        if self._eval_metric == EvaluationMetrics.XPIA:
            return Tasks.XPIA
        if self._eval_metric == _InternalEvaluationMetrics.ECI:
            return _InternalAnnotationTasks.ECI
        if self._eval_metric == EvaluationMetrics.PROTECTED_MATERIAL:
            return Tasks.PROTECTED_MATERIAL
        return Tasks.CONTENT_HARM
