# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import math
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

from azure.core.credentials import TokenCredential
from azure.ai.evaluation._constants import EVALUATION_PASS_FAIL_MAPPING
from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget
from . import EvaluatorBase
from ._model_runners import (
    DecisionModelRunner,
    PromptyModelRunner,
    is_decision_model_config,
)

T = TypeVar("T")


def not_applicable_result(result_key: str, reason: str, threshold: float) -> Dict[str, Any]:
    return {
        result_key: None,
        f"{result_key}_score": None,
        f"{result_key}_passed": None,
        f"{result_key}_result": "not_applicable",
        f"{result_key}_reason": f"Not applicable: {reason}",
        f"{result_key}_status": "skipped",
        f"{result_key}_threshold": threshold,
        f"{result_key}_properties": None,
    }


class ModelEvaluatorBase(EvaluatorBase[T]):
    """Base class for evaluators whose judgement comes from a model.

    The base selects one model runner at construction from ``model_config`` and holds the helpers shared by
    model-backed evaluators. A configuration tagged ``type="decision"`` selects a decision model runner, which
    only evaluators that set ``_supports_decision_models`` accept; any other configuration selects the Prompty
    runner and exposes its flow as ``_flow``. Interpreting a model's answer remains the evaluator's job.

    Decision requires an explicit API key or a credential with a callable ``get_token``. For Entra authentication,
    pass and reuse a synchronous ``azure.identity.DefaultAzureCredential`` as ``credential=`` for synchronous
    and batch calls, closing it after all evaluations complete. Async credentials require the same caller-managed
    event loop for all uses. The SDK never closes caller credentials. Prompty authentication is unchanged.

    :param result_key: The key to use for the result of the evaluation.
    :type result_key: str
    :param prompty_file: The prompt path, required only for a Prompty runner.
    :type prompty_file: Optional[str]
    :param model_config: The model configuration to use for evaluation.
    :type model_config: dict
    :keyword is_reasoning_model: This parameter is in preview. If True, updates the config parameters in prompty
        file based on reasoning models. Defaults to False.
    :type is_reasoning_model: bool
    :keyword timeout: Optional overall Decision time limit, including authentication and retries. Defaults to
        120 seconds for Decision; an explicit value retains the existing evaluator timeout cap.
        The remaining budget also limits native transport connect/read timeouts. Awaiting is cancelled at the
        deadline and the native async transport stops response body reads. Synchronous credential calls cannot be
        forcibly interrupted and may delay synchronous return.
    :paramtype timeout: Optional[float]
    :keyword timeout_seconds: Optional Decision connect/read timeout.
    :paramtype timeout_seconds: Optional[float]
    :keyword max_retries: Optional Decision retry limit, defaults to 3.
    :paramtype max_retries: Optional[int]
    :keyword cancellation_requested: Optional Decision cancellation callback, polled during authentication,
        requests and retry waits. Cancelling stops awaiting synchronous credential calls, not their worker threads.
    :paramtype cancellation_requested: Optional[Callable[[], bool]]
    :keyword max_request_bytes: Optional limit on the compact UTF-8 serialized Decision request.
    :paramtype max_request_bytes: Optional[int]
    :keyword max_state_question_bytes: Optional limit on the largest individual state/question pair.
    :paramtype max_state_question_bytes: Optional[int]
    :keyword max_response_bytes: Optional response acceptance limit before JSON parsing, not a streaming bound.
    :paramtype max_response_bytes: Optional[int]
    """

    _LLM_CALL_TIMEOUT = 600
    _DEFAULT_OPEN_API_VERSION = "2024-02-15-preview"

    _supports_decision_models = False
    """Whether this evaluator can be configured with a decision model."""
    _binary_decision = False
    """Whether decision answers become a binary score, which permits ``probability_threshold``."""

    def __init__(
        self,
        *,
        result_key: str,
        prompty_file: Optional[str] = None,
        model_config: dict,
        eval_last_turn: bool = False,
        threshold: int = 3,
        credential: Optional[TokenCredential] = None,
        timeout: Optional[float] = None,
        timeout_seconds: Optional[float] = None,
        max_retries: Optional[int] = None,
        cancellation_requested: Optional[Callable[[], bool]] = None,
        max_request_bytes: Optional[int] = None,
        max_state_question_bytes: Optional[int] = None,
        max_response_bytes: Optional[int] = None,
        _higher_is_better: bool = False,
        **kwargs,
    ) -> None:
        self._result_key = result_key
        self._is_reasoning_model = kwargs.get("is_reasoning_model", False)
        self._prompty_file = prompty_file
        self._threshold = threshold
        self._higher_is_better = _higher_is_better
        super().__init__(eval_last_turn=eval_last_turn, threshold=threshold, _higher_is_better=_higher_is_better)

        subclass_name = self.__class__.__name__
        execution_options: Dict[str, Any] = {
            "timeout_seconds": timeout_seconds,
            "max_retries": max_retries,
            "cancellation_requested": cancellation_requested,
            "max_request_bytes": max_request_bytes,
            "max_state_question_bytes": max_state_question_bytes,
            "max_response_bytes": max_response_bytes,
        }
        if is_decision_model_config(model_config):
            if not self._supports_decision_models:
                raise EvaluationException(
                    message=f"{subclass_name} does not support decision models.",
                    internal_message=f"{subclass_name} does not support decision models.",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.INVALID_VALUE,
                    target=ErrorTarget.EVALUATE,
                )
            if timeout is not None:
                if (
                    isinstance(timeout, bool)
                    or not isinstance(timeout, (int, float))
                    or not math.isfinite(timeout)
                    or timeout <= 0
                ):
                    raise EvaluationException(
                        message="'timeout' must be a positive finite number.",
                        blame=ErrorBlame.USER_ERROR,
                        category=ErrorCategory.INVALID_VALUE,
                        target=ErrorTarget.EVALUATE,
                    )
                self._LLM_CALL_TIMEOUT = min(self._LLM_CALL_TIMEOUT, timeout)
            else:
                self._LLM_CALL_TIMEOUT = min(self._LLM_CALL_TIMEOUT, 120)
            self._model_runner: Union[DecisionModelRunner, PromptyModelRunner] = DecisionModelRunner(
                model_config,
                credential,
                binary=self._binary_decision,
                evaluator_name=subclass_name,
                **{name: value for name, value in execution_options.items() if value is not None},
            )
        else:
            if timeout is not None or any(value is not None for value in execution_options.values()):
                raise EvaluationException(
                    message="Decision execution controls are only supported by decision model evaluators.",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.INVALID_VALUE,
                    target=ErrorTarget.EVALUATE,
                )
            if not prompty_file:
                raise EvaluationException(
                    message="A prompty_file is required for a chat model evaluator.",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.MISSING_FIELD,
                    target=ErrorTarget.EVALUATE,
                )
            self._model_runner = PromptyModelRunner(
                model_config=model_config,
                prompty_file=prompty_file,
                credential=credential,
                is_reasoning_model=self._is_reasoning_model,
                evaluator_name=subclass_name,
                api_version=self._DEFAULT_OPEN_API_VERSION,
            )

    @property
    def _prompty_model_runner(self) -> PromptyModelRunner:
        runner = self._model_runner
        if not isinstance(runner, PromptyModelRunner):
            raise RuntimeError("This evaluator is not configured with a Prompty model.")
        return runner

    @property
    def _flow(self) -> Any:
        runner = self._model_runner
        if not isinstance(runner, PromptyModelRunner):
            raise AttributeError("A decision model evaluator does not have a Prompty flow.")
        return runner.flow

    @_flow.setter
    def _flow(self, flow: Any) -> None:
        self._prompty_model_runner.flow = flow

    @property
    def _uses_decision_model(self) -> bool:
        return isinstance(self._model_runner, DecisionModelRunner)

    @property
    def _decision_model_runner(self) -> DecisionModelRunner:
        runner = self._model_runner
        if not isinstance(runner, DecisionModelRunner):
            raise RuntimeError("This evaluator is not configured with a decision model.")
        return runner

    def _aggregate_results(self, per_turn_results: List[Dict[str, T]]) -> Dict[str, Any]:
        """Aggregate scores normally, but sum independently known Decision usage across turns.

        A single shared model is promoted for attribution. Mixed or missing model identities remain per-turn
        rather than attributing all usage to the last model. Prompty aggregation is unchanged.
        """
        aggregated: Dict[str, Any] = super()._aggregate_results(per_turn_results)
        if not self._uses_decision_model:
            return aggregated
        metrics = {metric for turn in per_turn_results for metric in turn}
        for metric in metrics:
            if metric.endswith(("_prompt_tokens", "_completion_tokens", "_total_tokens")):
                values = (turn.get(metric) for turn in per_turn_results)
                known = [
                    value for value in values if isinstance(value, int) and not isinstance(value, bool) and value >= 0
                ]
                if known:
                    aggregated[metric] = sum(known)
                else:
                    aggregated.pop(metric, None)
            elif metric.endswith("_model"):
                models = [turn.get(metric) for turn in per_turn_results]
                if (
                    models
                    and isinstance(models[0], str)
                    and models[0].strip()
                    and all(model == models[0] for model in models)
                ):
                    aggregated[metric] = models[0]
                else:
                    aggregated.pop(metric, None)
        return aggregated

    def _on_evaluation_error(self, error: EvaluationException, per_turn_results: List[Dict[str, T]]) -> None:
        """Preserve known Decision turn usage without changing the failure or Prompty behavior.

        Only the request-owning result's usage is accumulated. A failed turn's execution summary cannot
        describe all these turns, so it is omitted and the wider usage scope is explicit.
        """
        if not self._uses_decision_model or not per_turn_results:
            return
        fields = ("prompt_tokens", "completion_tokens", "total_tokens")
        contributions = []
        for result in per_turn_results:
            usage = self._known_turn_usage(result, fields, prefix=f"{self._result_key}_")
            if usage:
                contributions.append((usage, result.get(f"{self._result_key}_model")))
        if not contributions:
            return
        properties = dict(error.properties) if isinstance(error.properties, dict) else {}
        failing_usage = self._known_turn_usage(properties, fields)
        if failing_usage:
            contributions.append((failing_usage, properties.get("model")))
        for field in fields:
            known = [usage[field] for usage, _ in contributions if field in usage]
            if known:
                properties[field] = sum(known)
            else:
                properties.pop(field, None)
        models = [model for _, model in contributions]
        common_model = models[0] if isinstance(models[0], str) and models[0].strip() else None
        if common_model is not None and all(model == common_model for model in models):
            properties["model"] = common_model
        else:
            properties.pop("model", None)
        native = properties.get("decision_model")
        native = dict(native) if isinstance(native, dict) else {}
        native.pop("execution", None)
        if "model" in properties:
            native["model"] = properties["model"]
        else:
            native.pop("model", None)
        native["usage_available"] = True
        native["result_usage_scope"] = "reported_turns_only"
        properties["decision_model"] = native
        error.properties = properties

    @staticmethod
    def _known_turn_usage(values: Dict[str, Any], fields: tuple, *, prefix: str = "") -> Dict[str, int]:
        """Keep each known count independently; missing totals are not inferred from partial counts."""
        return {
            field: values[prefix + field]
            for field in fields
            if isinstance(values.get(prefix + field), int)
            and not isinstance(values[prefix + field], bool)
            and values[prefix + field] >= 0
        }

    def _get_binary_result(self, score: float) -> str:
        """Get the binary result based on the score.

        :param score: The score to evaluate.
        :type score: float
        :return: The binary result.
        :rtype: str
        """
        if math.isnan(score):
            return "unknown"
        if self._higher_is_better:
            if score >= self._threshold:
                return EVALUATION_PASS_FAIL_MAPPING[True]
            else:
                return EVALUATION_PASS_FAIL_MAPPING[False]
        else:
            if score <= self._threshold:
                return EVALUATION_PASS_FAIL_MAPPING[True]
            else:
                return EVALUATION_PASS_FAIL_MAPPING[False]

    @staticmethod
    def _get_token_metadata(prompty_output: Dict) -> Dict:
        """Extract token usage and model metadata from the prompty output dict.

        :param prompty_output: The raw output dictionary from the prompty flow.
        :type prompty_output: Dict
        :return: A dictionary with token counts, finish reason, model, and sample I/O.
        :rtype: Dict
        """
        return {
            "prompt_tokens": prompty_output.get("input_token_count", 0),
            "completion_tokens": prompty_output.get("output_token_count", 0),
            "total_tokens": prompty_output.get("total_token_count", 0),
            "finish_reason": prompty_output.get("finish_reason", ""),
            "model": prompty_output.get("model_id", ""),
            "sample_input": prompty_output.get("sample_input", ""),
            "sample_output": prompty_output.get("sample_output", ""),
        }

    @staticmethod
    def _get_built_in_tool_definition(tool_name: str):
        """Get the definition for the built-in tool."""
        try:
            from ..._converters._models import _BUILT_IN_DESCRIPTIONS, _BUILT_IN_PARAMS

            if tool_name in _BUILT_IN_DESCRIPTIONS:
                return {
                    "type": tool_name,
                    "description": _BUILT_IN_DESCRIPTIONS[tool_name],
                    "name": tool_name,
                    "parameters": _BUILT_IN_PARAMS.get(tool_name, {}),
                }
        except ImportError:
            pass
        return None

    def _get_needed_built_in_tool_definitions(self, tool_calls: List[Dict]) -> List[Dict]:
        """Extract tool definitions needed for the given built-in tool calls."""
        needed_definitions = []
        for tool_call in tool_calls:
            if isinstance(tool_call, dict):
                tool_type = tool_call.get("type")

                # Only support converter format: {type: "tool_call", name: "bing_custom_search", arguments: {...}}
                if tool_type == "tool_call":
                    tool_name = tool_call.get("name")
                    if tool_name:
                        definition = self._get_built_in_tool_definition(tool_name)
                        if definition and definition not in needed_definitions:
                            needed_definitions.append(definition)

        return needed_definitions

    def _extract_tool_names_from_calls(self, tool_calls: List[Dict]) -> List[str]:
        """Extract just the tool names from tool calls, removing parameters."""
        tool_names = []
        for tool_call in tool_calls:
            if isinstance(tool_call, dict):
                tool_type = tool_call.get("type")
                if tool_type == "tool_call":
                    tool_name = tool_call.get("name")
                    if tool_name:
                        tool_names.append(tool_name)
                elif tool_call.get("function", {}).get("name"):
                    # Handle function call format
                    tool_names.append(tool_call["function"]["name"])
                elif tool_call.get("name"):
                    # Handle direct name format
                    tool_names.append(tool_call["name"])
        return tool_names

    def _extract_needed_tool_definitions(
        self, tool_calls: List[Dict], tool_definitions: List[Dict], error_target: ErrorTarget
    ) -> List[Dict]:
        """Extract the tool definitions that are needed for the provided tool calls.

        :param tool_calls: The tool calls that need definitions
        :type tool_calls: List[Dict]
        :param tool_definitions: User-provided tool definitions
        :type tool_definitions: List[Dict]
        :param error_target: The evaluator-specific error target for exceptions
        :type error_target: ErrorTarget
        :return: List of needed tool definitions
        :rtype: List[Dict]
        :raises EvaluationException: If validation fails
        """
        needed_tool_definitions = []

        # Add all user-provided tool definitions
        needed_tool_definitions.extend(tool_definitions)

        # Add the needed built-in tool definitions (if they are called)
        built_in_definitions = self._get_needed_built_in_tool_definitions(tool_calls)
        needed_tool_definitions.extend(built_in_definitions)

        # An OpenAPI tool is a collection of functions. When an OpenAPI tool
        # definition exposes its nested functions, expand it into those functions
        # so tool calls referencing a nested function name can be matched. If an
        # OpenAPI tool definition has no nested functions, keep the OpenAPI tool
        # definition as is for backward compatibility.
        tool_definitions_expanded = []
        for tool in needed_tool_definitions:
            openapi_functions = tool.get("functions") if tool.get("type") == "openapi" else None
            if openapi_functions:
                tool_definitions_expanded.extend(openapi_functions)
            else:
                tool_definitions_expanded.append(tool)

        # Validate that all tool calls have corresponding definitions
        for tool_call in tool_calls:
            if isinstance(tool_call, dict):
                tool_type = tool_call.get("type")

                if tool_type == "tool_call":
                    tool_name = tool_call.get("name")
                    if tool_name and self._get_built_in_tool_definition(tool_name):
                        # This is a built-in tool from converter, already handled above
                        continue
                    elif tool_name:
                        # This is a regular function tool from converter
                        tool_definition_exists = any(
                            tool.get("name") == tool_name for tool in tool_definitions_expanded
                        )
                        if not tool_definition_exists:
                            raise EvaluationException(
                                message=f"Tool definition for {tool_name} not found",
                                blame=ErrorBlame.USER_ERROR,
                                category=ErrorCategory.INVALID_VALUE,
                                target=error_target,
                            )
                    else:
                        raise EvaluationException(
                            message=f"Tool call missing name: {tool_call}",
                            blame=ErrorBlame.USER_ERROR,
                            category=ErrorCategory.INVALID_VALUE,
                            target=error_target,
                        )
                else:
                    # Unsupported tool format - only converter format is supported
                    raise EvaluationException(
                        message=f"Unsupported tool call format. Only converter format is supported: {tool_call}",
                        blame=ErrorBlame.USER_ERROR,
                        category=ErrorCategory.INVALID_VALUE,
                        target=error_target,
                    )
            else:
                # Tool call is not a dictionary
                raise EvaluationException(
                    message=f"Tool call is not a dictionary: {tool_call}",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.INVALID_VALUE,
                    target=error_target,
                )

        return needed_tool_definitions

    def _return_not_applicable_result(
        self, error_message: str, threshold: Union[int, float]
    ) -> Dict[str, Union[str, float, Dict, None]]:
        """Return a result indicating that the tool call is not applicable for evaluation.

        :param error_message: The error message indicating why the evaluation is not applicable.
        :type error_message: str
        :param threshold: The threshold value for the evaluation.
        :type threshold: Union[int, float]
        :return: A dictionary containing the result of the evaluation.
        :rtype: Dict[str, Union[str, float, None]]
        """
        return not_applicable_result(self._result_key, error_message, threshold)
