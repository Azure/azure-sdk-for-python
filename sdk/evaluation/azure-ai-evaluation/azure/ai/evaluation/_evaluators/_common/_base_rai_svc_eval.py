# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict, List, TypeVar, Union, Optional

from typing_extensions import override

from azure.ai.evaluation._common.constants import (
    EvaluationMetrics,
    _InternalEvaluationMetrics,
    Tasks,
    _InternalAnnotationTasks,
)
from azure.ai.evaluation._common.rai_service import (
    evaluate_with_rai_service_sync,
    evaluate_with_rai_service_sync_multimodal,
)
from azure.ai.evaluation._common.utils import validate_azure_ai_project, is_onedp_project
from azure.ai.evaluation._exceptions import EvaluationException
from azure.ai.evaluation._common.utils import validate_conversation
from azure.ai.evaluation._constants import _AggregationType
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
    :param conversation_aggregation_type: The type of aggregation to perform on the per-turn results of a conversation        to produce a single result.
        Default is ~azure.ai.evaluation._AggregationType.MEAN.
    :type conversation_aggregation_type: ~azure.ai.evaluation._AggregationType
    :param threshold: The threshold for the evaluation. Default is 3.
    :type threshold: Optional[int]
    :param _higher_is_better: If True, higher scores are better. Default is True.
    :type _higher_is_better: Optional[bool]
    :param evaluate_query: If True, the query will be included in the evaluation data when evaluating
        query-response pairs. If False, only the response will be evaluated. Default is False.
        Can be passed as a keyword argument.
    :type evaluate_query: bool
    :keyword _use_legacy_endpoint: Whether to use the legacy evaluation endpoint instead of the sync_evals endpoint.
        Defaults to False. Can be passed as a keyword argument.
    :paramtype _use_legacy_endpoint: bool
    """

    @override
    def __init__(
        self,
        eval_metric: Union[EvaluationMetrics, _InternalEvaluationMetrics],
        azure_ai_project: Union[dict, str],
        credential: TokenCredential,
        eval_last_turn: bool = False,
        conversation_aggregation_type: _AggregationType = _AggregationType.MEAN,
        threshold: int = 3,
        _higher_is_better: Optional[bool] = False,
        **kwargs,
    ):
        super().__init__(
            eval_last_turn=eval_last_turn,
            conversation_aggregation_type=conversation_aggregation_type,
            threshold=threshold,
            _higher_is_better=_higher_is_better,
        )
        self._eval_metric = eval_metric
        self._azure_ai_project = validate_azure_ai_project(azure_ai_project)
        self._credential = credential
        self._threshold = threshold

        # Handle evaluate_query parameter from kwargs
        self._evaluate_query = kwargs.get("evaluate_query", False)
        self._higher_is_better = _higher_is_better
        # Handle _use_legacy_endpoint parameter from kwargs
        self._use_legacy_endpoint = kwargs.get("_use_legacy_endpoint", False)

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
        if "response" in eval_input:
            return await self._evaluate_query_response(eval_input)

        conversation = eval_input.get("conversation", None)
        return await self._evaluate_conversation(conversation)

    async def _evaluate_conversation(self, conversation: Dict) -> Dict[str, T]:
        """Evaluates content according to this evaluator's metric.
        Evaluates each turn separately to maintain per-turn granularity.
        """
        validate_conversation(conversation)
        messages = conversation["messages"]

        # Convert enum to string value
        metric_value = self._eval_metric.value if hasattr(self._eval_metric, "value") else self._eval_metric

        # Extract conversation turns (user-assistant pairs)
        turns = self._extract_turns(messages)

        # Evaluate each turn separately
        per_turn_results = []
        for turn in turns:
            turn_result = await evaluate_with_rai_service_sync_multimodal(
                messages=turn,  # Single turn
                metric_name=metric_value,
                project_scope=self._azure_ai_project,
                credential=self._credential,
                use_legacy_endpoint=self._use_legacy_endpoint,
            )
            parsed = self._parse_eval_result(turn_result)
            per_turn_results.append(parsed)

        result = self._aggregate_results(per_turn_results)
        return result

    def _extract_turns(self, messages: List[Dict]) -> List[List[Dict]]:
        """Split conversation into user-assistant turn pairs.

        : param messages: List of conversation messages
        :type messages: List[Dict]
        :return: List of turns, where each turn is a list of messages
        :rtype: List[List[Dict]]
        """
        turns = []
        current_turn = []

        for msg in messages:
            current_turn.append(msg)
            # End turn when we see an assistant message
            if msg.get("role") == "assistant":
                turns.append(current_turn)
                current_turn = []

        # Handle case where conversation ends without assistant response
        if current_turn:
            turns.append(current_turn)

        return turns

    async def _evaluate_query_response(self, eval_input: Dict) -> Dict[str, T]:
        query = eval_input.get("query", None)
        response = eval_input.get("response", None)
        if response is None:
            raise EvaluationException(
                message="Not implemented",
                internal_message=(
                    "Reached query/response evaluation without supplying response."
                    + " This should have failed earlier."
                ),
            )
        input_data = {"response": str(response)}

        if query is not None and self._evaluate_query:
            input_data["query"] = str(query)

        if "context" in self._get_all_singleton_inputs():
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

        eval_result = await evaluate_with_rai_service_sync(  # type: ignore
            metric_name=self._eval_metric,
            data=input_data,
            project_scope=self._azure_ai_project,
            credential=self._credential,
            annotation_task=self._get_task(),
            evaluator_name=self.__class__.__name__,
            use_legacy_endpoint=self._use_legacy_endpoint,
        )

        # Parse the EvalRunOutputItem format to the expected dict format
        return self._parse_eval_result(eval_result)

    def _parse_eval_result(self, eval_result) -> Dict[str, T]:
        """Parse the EvalRunOutputItem format into the expected dict format.

        : param eval_result: The result from evaluate_with_rai_service_sync (EvalRunOutputItem).
        :return: The parsed result in the expected format.
        : rtype: Dict[str, T]
        """
        # Handle EvalRunOutputItem structure
        if hasattr(eval_result, "results") or (isinstance(eval_result, dict) and "results" in eval_result):
            results = eval_result.results if hasattr(eval_result, "results") else eval_result.get("results", [])

            # Find the result matching our metric
            for result_item in results:
                result_dict = result_item if isinstance(result_item, dict) else result_item.__dict__

                # Get metric name
                metric_name = result_dict.get("metric")
                if not metric_name:
                    continue

                # Check if this result matches our evaluator's metric
                if metric_name == self._eval_metric or metric_name == self._eval_metric.value:
                    # Extract common fields
                    score = result_dict.get("score", 0)
                    reason = result_dict.get("reason", "")
                    properties = result_dict.get("properties", {})

                    # Special handling for evaluators that use _label format
                    if self._eval_metric in [
                        EvaluationMetrics.CODE_VULNERABILITY,
                        EvaluationMetrics.PROTECTED_MATERIAL,
                        EvaluationMetrics.UNGROUNDED_ATTRIBUTES,
                        EvaluationMetrics.XPIA,
                        _InternalEvaluationMetrics.ECI,
                    ]:
                        # Extract label from scoreProperties
                        score_properties = properties.get("scoreProperties", {})
                        label_str = score_properties.get("label", "false")

                        # Convert string to boolean
                        label = label_str.lower() == "true" if isinstance(label_str, str) else bool(label_str)

                        parsed_result = {
                            f"{self._eval_metric.value}_label": label,
                            f"{self._eval_metric.value}_reason": reason,
                        }

                        # For protected_material, also extract breakdown if available
                        if self._eval_metric == EvaluationMetrics.PROTECTED_MATERIAL:
                            for component in ["fictional_characters", "logos_and_brands", "artwork"]:
                                component_value = score_properties.get(component)
                                if component_value is not None:
                                    # Convert string to boolean if needed
                                    component_label = (
                                        component_value.lower() == "true"
                                        if isinstance(component_value, str)
                                        else bool(component_value)
                                    )
                                    parsed_result[f"{component}_label"] = component_label
                                    # Reason might be in a separate field or computed
                                    component_reason = score_properties.get(f"{component}_reasoning", "")
                                    if component_reason:
                                        parsed_result[f"{component}_reason"] = component_reason

                        # Extract details from scoreProperties
                        if score_properties:
                            parsed_result[f"{self._eval_metric. value}_details"] = _prepare_details(score_properties)

                        # Extract token counts from metrics
                        metrics = properties.get("metrics", {})
                        prompt_tokens = metrics.get("promptTokens", "")
                        completion_tokens = metrics.get("completionTokens", "")

                        # Calculate total tokens
                        try:
                            total_tokens = (
                                str(int(prompt_tokens) + int(completion_tokens))
                                if prompt_tokens and completion_tokens
                                else ""
                            )
                        except (ValueError, TypeError):
                            total_tokens = ""

                        # Add token metadata (matching old format)
                        parsed_result[f"{self._eval_metric. value}_total_tokens"] = total_tokens
                        parsed_result[f"{self._eval_metric.value}_prompt_tokens"] = prompt_tokens
                        parsed_result[f"{self._eval_metric.value}_completion_tokens"] = completion_tokens

                        # Add empty placeholders for fields that sync_evals doesn't provide
                        parsed_result[f"{self._eval_metric.value}_finish_reason"] = ""
                        parsed_result[f"{self._eval_metric.value}_sample_input"] = ""
                        parsed_result[f"{self._eval_metric.value}_sample_output"] = ""
                        parsed_result[f"{self._eval_metric.value}_model"] = ""

                        return parsed_result

                    # Standard handling for harm severity evaluators
                    # Convert score to severity label if needed
                    severity_label = result_dict.get("label")
                    if severity_label is None:
                        # Calculate severity from score
                        from azure.ai.evaluation._common.utils import get_harm_severity_level

                        severity_label = get_harm_severity_level(score)

                    # Extract token counts
                    metrics = properties.get("metrics", {})
                    prompt_tokens = metrics.get("promptTokens", "")
                    completion_tokens = metrics.get("completionTokens", "")

                    try:
                        total_tokens = (
                            str(int(prompt_tokens) + int(completion_tokens))
                            if prompt_tokens and completion_tokens
                            else ""
                        )
                    except (ValueError, TypeError):
                        total_tokens = ""

                    # Return in the expected format matching parse_response output
                    return {
                        self._eval_metric.value: severity_label,
                        f"{self._eval_metric.value}_score": score,
                        f"{self._eval_metric.value}_reason": reason,
                        f"{self._eval_metric.value}_total_tokens": total_tokens,
                        f"{self._eval_metric.value}_prompt_tokens": prompt_tokens,
                        f"{self._eval_metric.value}_completion_tokens": completion_tokens,
                        f"{self._eval_metric.value}_finish_reason": "",
                        f"{self._eval_metric.value}_sample_input": "",
                        f"{self._eval_metric.value}_sample_output": "",
                        f"{self._eval_metric.value}_model": "",
                    }

            # If no matching result found, fall through

        # If we can't parse as EvalRunOutputItem or no matching result found,
        # check if it's already in the correct format (might be legacy response)
        if isinstance(eval_result, dict):
            # Check if it already has the expected keys
            expected_key = (
                f"{self._eval_metric.value}_label"
                if self._eval_metric
                in [
                    EvaluationMetrics.CODE_VULNERABILITY,
                    EvaluationMetrics.PROTECTED_MATERIAL,
                    EvaluationMetrics.UNGROUNDED_ATTRIBUTES,
                    EvaluationMetrics.XPIA,
                    _InternalEvaluationMetrics.ECI,
                ]
                else self._eval_metric.value
            )

            if expected_key in eval_result:
                return eval_result

        # Return empty dict if we can't parse
        return {}

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
        if self._eval_metric == EvaluationMetrics.CODE_VULNERABILITY:
            return Tasks.CODE_VULNERABILITY
        if self._eval_metric == EvaluationMetrics.UNGROUNDED_ATTRIBUTES:
            return Tasks.UNGROUNDED_ATTRIBUTES
        return Tasks.CONTENT_HARM


def _coerce_string_boolean(value: Any) -> Any:
    """Convert common string boolean values to their bool equivalents."""

    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
    return value


def _prepare_details(details: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize detail keys and coerce string booleans recursively.

    Excludes internal/metadata fields that shouldn't be exposed in details.
    """
    # Fields to exclude from details
    EXCLUDED_FIELDS = {
        "label",  # Exposed as top-level _label field, not in details
        "refusalDetectionTokensIncluded",  # Internal metadata
        "version",
        "totalTokenCount",
        "inputTokenCount",
        "outputTokenCount",
        "finish_reason",
        "sample_input",
        "sample_output",
        "model",
    }

    normalized: Dict[str, Any] = {}
    for key, value in details.items():
        # Skip excluded fields
        if key in EXCLUDED_FIELDS:
            continue

        normalized_key = key.replace("-", "_") if isinstance(key, str) else key
        normalized[normalized_key] = _prepare_detail_value(value)
    return normalized


def _prepare_detail_value(value: Any) -> Any:
    if isinstance(value, dict):
        return _prepare_details(value)
    if isinstance(value, list):
        return [_prepare_detail_value(item) for item in value]
    return _coerce_string_boolean(value)
