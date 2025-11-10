# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import math
import re
import os
from itertools import chain
from typing import Dict, Optional, TypeVar, Union, List

if os.getenv("AI_EVALS_USE_PF_PROMPTY", "false").lower() == "true":
    from promptflow.core._flow import AsyncPrompty
else:
    from azure.ai.evaluation._legacy.prompty import AsyncPrompty
from typing_extensions import override

from azure.core.credentials import TokenCredential
from azure.ai.evaluation._common.constants import PROMPT_BASED_REASON_EVALUATORS
from azure.ai.evaluation._constants import EVALUATION_PASS_FAIL_MAPPING
from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget
from ..._common.utils import construct_prompty_model_config, validate_model_config, parse_quality_evaluator_reason_score
from . import EvaluatorBase

try:
    from ..._user_agent import UserAgentSingleton
except ImportError:

    class UserAgentSingleton:
        @property
        def value(self) -> str:
            return "None"


T = TypeVar("T")


class PromptyEvaluatorBase(EvaluatorBase[T]):
    """Base class for all evaluators that make use of context as an input. It's also assumed that such evaluators
    make use of a prompty file, and return their results as a dictionary, with a single key-value pair
    linking the result name to a float value (unless multi-turn evaluation occurs, in which case the
    per-turn results are stored in a list under the key "evaluation_per_turn").

    :param result_key: The key to use for the result of the evaluation. Single turn evaluations will return
        a dictionary in the format {result_key: float}.
    :type result_key: str
    :param prompty_file: The path to the prompty file to use for evaluation.
    :type prompty_file: str
    :param model_config: The model configuration to use for evaluation.
    :type model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration]
    :param ignore_queries: If True, queries will be ignored in conversation evaluations. Default is False.
        Useful since some evaluators of this format are response-only.
    :type ignore_queries: bool
    :keyword is_reasoning_model: This parameter is in preview. If True, updates the config parameters in prompty file based on reasoning models. Defaults to False.
    :type is_reasoning_model: bool
    """

    _LLM_CALL_TIMEOUT = 600
    _DEFAULT_OPEN_API_VERSION = "2024-02-15-preview"

    def __init__(
        self,
        *,
        result_key: str,
        prompty_file: str,
        model_config: dict,
        eval_last_turn: bool = False,
        threshold: int = 3,
        credential: Optional[TokenCredential] = None,
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
        user_agent = f"{UserAgentSingleton().value} (type=evaluator subtype={subclass_name})"
        prompty_model_config = construct_prompty_model_config(
            validate_model_config(model_config),
            self._DEFAULT_OPEN_API_VERSION,
            user_agent,
        )

        self._flow = AsyncPrompty.load(
            source=self._prompty_file,
            model=prompty_model_config,
            token_credential=credential,
            is_reasoning_model=self._is_reasoning_model,
        )

    # __call__ not overridden here because child classes have such varied signatures that there's no point
    # defining a default here.
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

    @override
    async def _do_eval_wflow(self, eval_input: Dict, flow) -> Dict[str, Union[float, str]]:  # type: ignore[override]
        """Do a relevance evaluation.

        :param eval_input: The input to the evaluator. Expected to contain
        whatever inputs are needed for the _flow method, including context
        and other fields depending on the child class.
        :type eval_input: Dict
        :return: The evaluation result.
        :rtype: Dict
        """
        if "query" not in eval_input and "response" not in eval_input:
            raise EvaluationException(
                message="Only text conversation inputs are supported.",
                internal_message="Only text conversation inputs are supported.",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.INVALID_VALUE,
                target=ErrorTarget.CONVERSATION,
            )
        # Call the prompty flow to get the evaluation result.
        prompty_output_dict = await flow(timeout=self._LLM_CALL_TIMEOUT, **eval_input)

        score = math.nan
        if prompty_output_dict:
            llm_output = prompty_output_dict.get("llm_output", "")
            input_token_count = prompty_output_dict.get("input_token_count", 0)
            output_token_count = prompty_output_dict.get("output_token_count", 0)
            total_token_count = prompty_output_dict.get("total_token_count", 0)
            finish_reason = prompty_output_dict.get("finish_reason", "")
            model_id = prompty_output_dict.get("model_id", "")
            sample_input = prompty_output_dict.get("sample_input", "")
            sample_output = prompty_output_dict.get("sample_output", "")
            # Parse out score and reason from evaluators known to possess them.
            if self._result_key in PROMPT_BASED_REASON_EVALUATORS:
                score, reason = parse_quality_evaluator_reason_score(llm_output)
                binary_result = self._get_binary_result(score)
                return {
                    self._result_key: float(score),
                    f"gpt_{self._result_key}": float(score),
                    f"{self._result_key}_reason": reason,
                    f"{self._result_key}_result": binary_result,
                    f"{self._result_key}_threshold": self._threshold,
                    f"{self._result_key}_prompt_tokens": input_token_count,
                    f"{self._result_key}_completion_tokens": output_token_count,
                    f"{self._result_key}_total_tokens": total_token_count,
                    f"{self._result_key}_finish_reason": finish_reason,
                    f"{self._result_key}_model": model_id,
                    f"{self._result_key}_sample_input": sample_input,
                    f"{self._result_key}_sample_output": sample_output,
                }
            match = re.search(r"\d", llm_output)
            if match:
                score = float(match.group())
                binary_result = self._get_binary_result(score)
            return {
                self._result_key: float(score),
                f"gpt_{self._result_key}": float(score),
                f"{self._result_key}_result": binary_result,
                f"{self._result_key}_threshold": self._threshold,
                f"{self._result_key}_prompt_tokens": input_token_count,
                f"{self._result_key}_completion_tokens": output_token_count,
                f"{self._result_key}_total_tokens": total_token_count,
                f"{self._result_key}_finish_reason": finish_reason,
                f"{self._result_key}_model": model_id,
                f"{self._result_key}_sample_input": sample_input,
                f"{self._result_key}_sample_output": sample_output,
            }

        binary_result = self._get_binary_result(score)
        return {
            self._result_key: float(score),
            f"gpt_{self._result_key}": float(score),
            f"{self._result_key}_result": binary_result,
            f"{self._result_key}_threshold": self._threshold,
        }

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict[str, Union[float, str]]:  # type: ignore[override]
        """Do a relevance evaluation with default flow.

        :param eval_input: The input to the evaluator. Expected to contain
        whatever inputs are needed for the _flow method, including context
        and other fields depending on the child class.
        :type eval_input: Dict
        :return: The evaluation result.
        :rtype: Dict
        """

        return await self._do_eval_wflow(eval_input, self._flow)

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

        # OpenAPI tool is a collection of functions, so we need to expand it
        tool_definitions_expanded = list(
            chain.from_iterable(
                tool.get("functions", []) if tool.get("type") == "openapi" else [tool]
                for tool in needed_tool_definitions
            )
        )

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
                            tool.get("name") == tool_name and tool.get("type", "function") == "function"
                            for tool in tool_definitions_expanded
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

    def _not_applicable_result(
        self, error_message: str, threshold: Union[int, float]
    ) -> Dict[str, Union[str, float, Dict]]:
        """Return a result indicating that the evaluation is not applicable.

        :param error_message: The error message explaining why evaluation is not applicable.
        :type error_message: str
        :param threshold: The threshold value for the evaluator.
        :type threshold: Union[int, float]
        :return: A dictionary containing the result of the evaluation.
        :rtype: Dict[str, Union[str, float, Dict]]
        """
        # If no tool calls were made or tool call type is not supported, return not applicable result
        return {
            self._result_key: self._NOT_APPLICABLE_RESULT,
            f"{self._result_key}_result": "pass",
            f"{self._result_key}_threshold": threshold,
            f"{self._result_key}_reason": error_message,
            f"{self._result_key}_details": {},
        }
