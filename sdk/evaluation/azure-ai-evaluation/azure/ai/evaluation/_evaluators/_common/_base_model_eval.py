# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import math
from typing import Any, Dict, List, Optional, TypeVar, Union

from azure.core.credentials import TokenCredential
from azure.ai.evaluation._constants import EVALUATION_PASS_FAIL_MAPPING
from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget
from . import EvaluatorBase
from ._decision_execution import DecisionExecutionPolicy
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

    :param result_key: The key to use for the result of the evaluation.
    :type result_key: str
    :param prompty_file: The prompt path, required only for a Prompty runner.
    :type prompty_file: Optional[str]
    :param model_config: The model configuration to use for evaluation.
    :type model_config: dict
    :keyword is_reasoning_model: This parameter is in preview. If True, updates the config parameters in prompty
        file based on reasoning models. Defaults to False.
    :type is_reasoning_model: bool
    :keyword decision_execution_policy: Optional transport-only limits and receipt callbacks for a decision runner.
        Rejected for Prompty evaluators; omitted policies preserve existing Prompty behavior.
    :paramtype decision_execution_policy: Optional[DecisionExecutionPolicy]
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
        decision_execution_policy: Optional[DecisionExecutionPolicy] = None,
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
        if is_decision_model_config(model_config):
            if not self._supports_decision_models:
                raise EvaluationException(
                    message=f"{subclass_name} does not support decision models.",
                    internal_message=f"{subclass_name} does not support decision models.",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.INVALID_VALUE,
                    target=ErrorTarget.EVALUATE,
                )
            self._model_runner: Union[DecisionModelRunner, PromptyModelRunner] = DecisionModelRunner(
                model_config,
                credential,
                binary=self._binary_decision,
                evaluator_name=subclass_name,
                execution_policy=decision_execution_policy,
            )
        else:
            if decision_execution_policy is not None:
                raise EvaluationException(
                    message="A decision_execution_policy is only supported by decision model evaluators.",
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
