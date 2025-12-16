# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import math
import os
import logging
import re
from typing import Dict, List, Union, TypeVar, Optional
from typing_extensions import overload, override
from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase
from azure.ai.evaluation._exceptions import (
    ErrorBlame,
    ErrorCategory,
    ErrorTarget,
    EvaluationException,
)
from ..._common.utils import check_score_is_valid
from azure.ai.evaluation._common._experimental import experimental

logger = logging.getLogger(__name__)

T_EvalValue = TypeVar("T_EvalValue")


@experimental
class ToolCallAccuracyEvaluator(PromptyEvaluatorBase[Union[str, float]]):
    """The Tool Call Accuracy evaluator assesses how accurately an AI uses tools by examining:
        - Relevance to the conversation.
        - Parameter correctness according to tool definitions.
        - Parameter value extraction from the conversation.

    The evaluator uses a scoring rubric of 1 to 5:
        - Score 1: The tool calls are irrelevant
        - Score 2: The tool calls are partially relevant, but not enough tools were called or the parameters were not correctly passed.
        - Score 3: The tool calls are relevant, but there were unnecessary, excessive tool calls made.
        - Score 4: The tool calls are relevant, but some tools returned errors and agent retried calling them again and succeeded.
        - Score 5: The tool calls are relevant, and all parameters were correctly passed.

    This evaluation focuses on measuring whether tool calls meaningfully contribute to addressing
    user needs while properly following tool definitions and using information present in the
    conversation history.

    :param model_config: Configuration for the Azure OpenAI model.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START tool_call_accuracy_evaluator]
            :end-before: [END tool_call_accuracy_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call a ToolCallAccuracyEvaluator.

    .. admonition:: Example using Azure AI Project URL:

        .. literalinclude:: ../samples/evaluation_samples_evaluate_fdp.py
            :start-after: [START tool_call_accuracy_evaluator]
            :end-before: [END tool_call_accuracy_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call ToolCallAccuracyEvaluator using Azure AI Project URL in the following format
                https://{resource_name}.services.ai.azure.com/api/projects/{project_name}

    .. note::

        The output field "details" has been renamed to "tool_call_accuracy_details" for clarity.

        To align with our support of a diverse set of models, an output key without the `gpt_` prefix has been added.
        To maintain backwards compatibility, the old key with the `gpt_` prefix is still be present in the output;
        however, it is recommended to use the new key moving forward as the old key will be deprecated in the future.

    """

    _PROMPTY_FILE = "tool_call_accuracy.prompty"
    _RESULT_KEY = "tool_call_accuracy"

    _MAX_TOOL_CALL_ACCURACY_SCORE = 5
    _MIN_TOOL_CALL_ACCURACY_SCORE = 1
    _DEFAULT_TOOL_CALL_ACCURACY_SCORE = 3

    _NO_TOOL_CALLS_MESSAGE = "No tool calls found in response or provided tool_calls."
    _NO_TOOL_DEFINITIONS_MESSAGE = "Tool definitions must be provided."
    _TOOL_DEFINITIONS_MISSING_MESSAGE = "Tool definitions for all tool calls must be provided."
    _INVALID_SCORE_MESSAGE = "Tool call accuracy score must be between 1 and 5."

    _LLM_SCORE_KEY = "tool_calls_success_level"

    id = "azureai://built-in/evaluators/tool_call_accuracy"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    @override
    def __init__(self, model_config, *, threshold=_DEFAULT_TOOL_CALL_ACCURACY_SCORE, credential=None, **kwargs):
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self._PROMPTY_FILE)
        self.threshold = threshold
        super().__init__(
            model_config=model_config,
            prompty_file=prompty_path,
            result_key=self._RESULT_KEY,
            credential=credential,
            threshold=threshold,
            **kwargs,
        )

    @overload
    def __call__(
        self,
        *,
        query: Union[str, List[dict]],
        tool_definitions: Union[dict, List[dict]],
        tool_calls: Union[dict, List[dict]] = None,
        response: Union[str, List[dict]] = None,
    ) -> Dict[str, Union[str, float]]:
        """
        Evaluate tool call accuracy. Accepts a query, tool definitions, and tool calls for evaluation.

        :keyword query: Query or Chat history up to the message that has the tool call being evaluated.
        :paramtype query: Union[str, List[dict]]
        :keyword tool_definitions: List of tool definitions whose calls are being evaluated.
        :paramtype tool_definitions: Union[dict, List[dict]]
        :keyword tool_calls: Optional List of tool calls to evaluate. If not provided response should be provided and should have
            tool call(s) in it.
        :paramtype tool_calls: Union[dict, List[dict]]
        :keyword response: Optional response to be evaluated alongside the tool calls.
            If provided all tool calls in response will be evaluated when tool_calls parameter is not provided.
            If provided and tool_calls parameter is provided, only the tool calls in tool_calls parameter will be evaluated.
                If response has extra tool calls they will not be evaluated, response will be used to extract any tool calls that are needed for evaluating a certain tool call.
            Recommended to provide it when there are tool calls that depend on output of a previous tool call.
        :paramtype response: Union[str, List[dict]]
        :return: The tool selection evaluation results.
        :rtype: Dict[str, Union[str, float]]
        """

    def _convert_kwargs_to_eval_input(self, **kwargs):
        """Convert an arbitrary input into a list of inputs for evaluators.
        It is assumed that evaluators generally make use of their inputs in one of two ways.
        Either they receive a collection of keyname inputs that are all single values
        (like a query and response), or they receive conversation that iss a list of dictionary
        values.

        The self._singleton_inputs list assigned during initialization is used to find and extract
        singleton keywords, and self._allow_conversation_input is used to determine if a conversation
        is a valid input.

        If both conversations and singletons are allowed, the function will raise an exception if both
        are inputted.

        This function must be overridden by child classes IF they need to both a conversation and
        other inputs to be passed in.

        :keyword kwargs: The inputs to convert.
        :type kwargs: Dict
        :return: A list of arbitrary values that are valid inputs for this evaluator's do_eval function.
        :rtype: List
        """
        # TODO add warning that only tool calls of type function are supported
        # Collect inputs
        tool_calls = kwargs.get("tool_calls")
        tool_definitions = kwargs.get("tool_definitions", [])  # Default to empty list
        query = kwargs.get("query")
        response = kwargs.get("response")
        # TODO : Support classes that represents tool calls, messages etc once client side definitions are available

        # Initially try to extract tool calls from the response whether or not tool_calls parameter is provided
        if response:
            try:
                parsed_tool_calls = self._parse_tools_from_response(response, ensure_arguments=True)
                if parsed_tool_calls:
                    tool_calls = parsed_tool_calls
            except EvaluationException as e:
                raise EvaluationException(
                    message=e.message,
                    category=e.category,
                    target=ErrorTarget.TOOL_CALL_ACCURACY_EVALUATOR,
                    blame=ErrorBlame.USER_ERROR,
                ) from e

        if not tool_calls:
            return {"error_message": self._NO_TOOL_CALLS_MESSAGE}

        if not isinstance(tool_calls, list):
            tool_calls = [tool_calls]
        
        # Validate that all tool calls have the "arguments" key
        for tool_call in tool_calls:
            if isinstance(tool_call, dict):
                if "arguments" not in tool_call:
                    raise EvaluationException(
                        message=f"Tool call missing 'arguments' field: {tool_call}",
                        category=ErrorCategory.MISSING_FIELD,
                        target=ErrorTarget.TOOL_CALL_ACCURACY_EVALUATOR,
                        blame=ErrorBlame.USER_ERROR,
                    )
        
        if not isinstance(tool_definitions, list):
            tool_definitions = [tool_definitions] if tool_definitions else []

        try:
            needed_tool_definitions = self._extract_needed_tool_definitions(
                tool_calls, tool_definitions, ErrorTarget.TOOL_CALL_ACCURACY_EVALUATOR
            )
        except EvaluationException:
            # Re-raise the exception from _extract_needed_tool_definitions as it already has specific error details
            raise

        # Check if no tool definitions were found at all (including built-in tools)
        if len(needed_tool_definitions) == 0:
            raise EvaluationException(
                message=self._NO_TOOL_DEFINITIONS_MESSAGE,
                category=ErrorCategory.INVALID_VALUE,
                target=ErrorTarget.TOOL_CALL_ACCURACY_EVALUATOR,
                blame=ErrorBlame.USER_ERROR,
            )

        return {
            "query": query,
            "tool_calls": tool_calls,
            "tool_definitions": needed_tool_definitions,
        }

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict[str, Union[float, str]]:  # type: ignore[override]
        """Do a tool call accuracy evaluation.
        :param eval_input: The input to the evaluator. Expected to contain
        whatever inputs are needed for the _flow method, including context
        and other fields depending on the child class.
        :type eval_input: Dict
        :return: The evaluation result.
        :rtype: Dict
        """
        # Single LLM call for all tool calls
        prompty_output_dict = await self._flow(timeout=self._LLM_CALL_TIMEOUT, **eval_input)
        llm_output = prompty_output_dict.get("llm_output", {})
        if isinstance(llm_output, dict):
            score = llm_output.get(self._LLM_SCORE_KEY, None)
            if not score or not check_score_is_valid(
                score,
                ToolCallAccuracyEvaluator._MIN_TOOL_CALL_ACCURACY_SCORE,
                ToolCallAccuracyEvaluator._MAX_TOOL_CALL_ACCURACY_SCORE,
            ):
                raise EvaluationException(
                    message=f"Invalid score value: {score}. Expected a number in range [{ToolCallAccuracyEvaluator._MIN_TOOL_CALL_ACCURACY_SCORE}, {ToolCallAccuracyEvaluator._MAX_TOOL_CALL_ACCURACY_SCORE}].",
                    internal_message="Invalid score value.",
                    category=ErrorCategory.FAILED_EXECUTION,
                    target=ErrorTarget.TOOL_CALL_ACCURACY_EVALUATOR,
                    blame=ErrorBlame.SYSTEM_ERROR,
                )

            # Format the output
            reason = llm_output.get("chain_of_thought", "")
            score = float(score)
            score_result = "pass" if score >= self.threshold else "fail"
            response_dict = {
                self._result_key: score,
                f"gpt_{self._result_key}": score,
                f"{self._result_key}_result": score_result,
                f"{self._result_key}_threshold": self._threshold,
                f"{self._result_key}_reason": reason,
                f"{self._result_key}_details": llm_output.get("details", {}),
                f"{self._result_key}_prompt_tokens": prompty_output_dict.get("input_token_count", 0),
                f"{self._result_key}_completion_tokens": prompty_output_dict.get("output_token_count", 0),
                f"{self._result_key}_total_tokens": prompty_output_dict.get("total_token_count", 0),
                f"{self._result_key}_finish_reason": prompty_output_dict.get("finish_reason", ""),
                f"{self._result_key}_model": prompty_output_dict.get("model_id", ""),
                f"{self._result_key}_sample_input": prompty_output_dict.get("sample_input", ""),
                f"{self._result_key}_sample_output": prompty_output_dict.get("sample_output", ""),
            }
            return response_dict

        else:
            raise EvaluationException(
                message="Tool call accuracy evaluator returned invalid output.",
                blame=ErrorBlame.SYSTEM_ERROR,
                category=ErrorCategory.FAILED_EXECUTION,
                target=ErrorTarget.TOOL_CALL_ACCURACY_EVALUATOR,
            )

    async def _real_call(self, **kwargs):
        """The asynchronous call where real end-to-end evaluation logic is performed.

        :keyword kwargs: The inputs to evaluate
        :type kwargs: Dict
        :return: The evaluation result
        :rtype: Union[DoEvalResult[T_EvalValue], AggregateResult[T_EvalValue]]
        """
        # Convert inputs into list of evaluable inputs.
        eval_input = self._convert_kwargs_to_eval_input(**kwargs)
        if isinstance(eval_input, dict) and eval_input.get("error_message"):
            # If there is an error message, return not applicable result
            return self._not_applicable_result(eval_input.get("error_message"), self.threshold)
        # Do the evaluation
        result = await self._do_eval(eval_input)
        # Return the result
        return result

    @override
    def __call__(  # pylint: disable=docstring-missing-param
        self,
        *args,
        **kwargs,
    ):
        """
        Evaluate tool call accuracy. Accepts a query, tool definitions, and tool calls for evaluation.

        :keyword query: Query or Chat history up to the message that has the tool call being evaluated.
        :paramtype query: Union[str, List[dict]]
        :keyword tool_definitions: List of tool definitions whose calls are being evaluated.
        :paramtype tool_definitions: Union[dict, List[dict]]
        :keyword tool_calls: Optional List of tool calls to evaluate. If not provided response should be provided and should have
            tool call(s) in it.
        :paramtype tool_calls: Union[dict, List[dict]]
        :keyword response: Optional response to be evaluated alongside the tool calls.
            If provided all tool calls in response will be evaluated when tool_calls parameter is not provided.
            If provided and tool_calls parameter is provided, only the tool calls in tool_calls parameter will be evaluated.
                If response has extra tool calls they will not be evaluated, response will be used to extract any tool calls that are needed for evaluating a certain tool call.
            Recommended to provide it when there are tool calls that depend on output of a previous tool call.
        :paramtype response: Union[str, List[dict]]
        :return: The tool selection evaluation results.
        :rtype: Dict[str, Union[str, float]]
        """
        return super().__call__(*args, **kwargs)
